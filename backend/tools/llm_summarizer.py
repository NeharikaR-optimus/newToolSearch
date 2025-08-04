
# LLM-based tool name extraction from article text
def get_llm_tool_names_from_text(article_text: str) -> list:
    """
    Uses LLM to extract a list of AI tool names from the given article text.
    Returns a list of tool names.
    """
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT
# Constant for repeated '/openai/' string
OPENAI_PATH = '/openai/'

def get_llm_tool_names_from_text(article_text: str) -> list:
    """
    Uses LLM to extract a list of AI tool names from the given article text.
    Returns a list of tool names.
    """
    llm = AzureChatOpenAI(
        openai_api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT.split(OPENAI_PATH)[0] + '/',
        deployment_name="gpt-4o-mini",
        api_version="2025-01-01-preview",
        temperature=0.2,
        max_tokens=512,
    )
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are an expert at extracting product names from articles. Extract a JSON list of unique AI tool names mentioned in the following text. Only return the list, no explanation."),
        ("user", "{article_text}")
    ])
    prompt = prompt_template.format(article_text=article_text[:12000])  # Truncate if too long
    response = llm.invoke(prompt)
    content = response.content.strip()
    if content.startswith('```'):
        content = content.lstrip('`').strip()
        if content.lower().startswith('json'):
            content = content[4:].strip()
        if content.endswith('```'):
            content = content[:-3].strip()
    try:
        tool_names = json.loads(content)
        if isinstance(tool_names, list):
            return [str(t) for t in tool_names if isinstance(t, str)]
        return []
    except Exception:
        return []
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT
from typing import Dict, List
import logging
import json

def make_llm_summarize_node():
    llm = AzureChatOpenAI(
        openai_api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT.split(OPENAI_PATH)[0] + '/',
        deployment_name="gpt-4o-mini",
        api_version="2025-01-01-preview",
        temperature=0.7,
        max_tokens=512,
    )
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are an expert product analyst. Summarize the following tool as a JSON with 'summary' and 'bullets'."),
        ("user", "{tool_data}")
    ])
    def llm_summarize_node(state: Dict) -> Dict:
        summaries = []
        for tool in state["extracted_tools"]:
            prompt = prompt_template.format(tool_data=str(tool))
            logging.info(f"Prompt for tool {tool.get('website', '')}: {prompt}")
            try:
                response = llm.invoke(prompt)
                logging.info(f"LLM response for tool {tool.get('website', '')}: {response.content}")
                # Remove triple backticks and optional 'json' marker
                content = response.content.strip()
                if content.startswith('```'):
                    content = content.lstrip('`').strip()
                    if content.lower().startswith('json'):
                        content = content[4:].strip()
                    if content.endswith('```'):
                        content = content[:-3].strip()
                parsed = json.loads(content)
                summaries.append({
                    "summary": parsed.get("summary", ""),
                    "bullets": parsed.get("bullets", []),
                    "category": tool.get("category", ""),
                    "website": tool.get("website", "")
                })
            except Exception:
                logging.error(f"LLM summarization failed for tool {tool.get('website', '')}")
                summaries.append({
                    "summary": "LLM summarization failed.",
                    "bullets": [],
                    "category": tool.get("category", ""),
                    "website": tool.get("website", "")
                })
        state["summaries"] = summaries
        return state
    return llm_summarize_node


# New function: summarize top tools by searching and LLM summarization
from .search_agent import SearchAgent
from .extractor import extract_tool_info
def summarize_top_tools(tool_names, search_agent=None, llm=None):
    """
    For each tool name, fetch details (single search call), then summarize with LLM (single call per tool).
    Returns a list of summaries.
    """
    if search_agent is None:
        search_agent = SearchAgent()
    if llm is None:
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
    summaries = []
    for tool_name in tool_names:
        search_results = search_agent.search_tool(tool_name)
        if not search_results:
            continue
        tool_info = extract_tool_info(search_results[0])
        prompt = prompt_template.format(tool_data=str(tool_info))
        try:
            response = llm.invoke(prompt)
            content = response.content.strip()
            if content.startswith('```'):
                content = content.lstrip('`').strip()
                if content.lower().startswith('json'):
                    content = content[4:].strip()
                if content.endswith('```'):
                    content = content[:-3].strip()
            parsed = json.loads(content)
            summaries.append({
                "name": tool_name,
                "summary": parsed.get("summary", ""),
                "bullets": parsed.get("bullets", []),
                "category": tool_info.get("category", ""),
                "website": tool_info.get("website", "")
            })
        except Exception:
            summaries.append({
                "name": tool_name,
                "summary": "LLM summarization failed.",
                "bullets": [],
                "category": tool_info.get("category", ""),
                "website": tool_info.get("website", "")
            })
    return summaries
