from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT
import logging
import json

def summarize_tool_with_llm(tool: dict) -> dict:
    llm = AzureChatOpenAI(
        openai_api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT.split('/openai/')[0] + '/',
        deployment_name="gpt-4o-mini",
        api_version="2025-01-01-preview",
        temperature=0.7,
        max_tokens=512,
    )
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are an expert product analyst. Summarize the following tool as a JSON with 'summary' and 'bullets'."),
        ("user", "{tool_data}")
    ])
    prompt = prompt_template.format(tool_data=str(tool))
    logging.info(f"Prompt for tool {tool.get('website', '')}: {prompt}")
    try:
        response = llm.invoke(prompt)
        logging.info(f"LLM response for tool {tool.get('website', '')}: {response.content}")
        content = response.content.strip()
        if content.startswith('```'):
            content = content.lstrip('`').strip()
            if content.lower().startswith('json'):
                content = content[4:].strip()
            if content.endswith('```'):
                content = content[:-3].strip()
        parsed = json.loads(content)
        return {
            "summary": parsed.get("summary", ""),
            "bullets": parsed.get("bullets", []),
            "category": tool.get("category", ""),
            "website": tool.get("website", "")
        }
    except Exception as e:
        try:
            logging.error(f"LLM raw response for tool {tool.get('website', '')}: {response.content}")
        except Exception:
            logging.error(f"No LLM response object for tool {tool.get('website', '')}")
        logging.error(f"LLM summarization failed for tool {tool.get('website', '')}: {e}")
        return {
            "summary": "LLM summarization failed.",
            "bullets": [],
            "category": tool.get("category", ""),
            "website": tool.get("website", "")
        }
