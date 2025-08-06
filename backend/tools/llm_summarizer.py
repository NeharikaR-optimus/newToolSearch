import json
import logging
from typing import Dict, List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT
from .search_agent import SearchAgent
from .extractor import extract_tool_info

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
        ("system", """You are an expert at extracting developer tool names from tech articles and news. 
        Extract a JSON list of unique tool names mentioned in the following text that would be useful for developers, including:
        - Programming languages and frameworks (React, Vue, Python, Rust, etc.)
        - Development tools and IDEs (VS Code, IntelliJ, etc.)
        - DevOps and deployment tools (Docker, Kubernetes, AWS services, etc.)
        - Database technologies (PostgreSQL, MongoDB, Redis, etc.)
        - API development and testing tools (Postman, Insomnia, etc.)
        - Mobile development frameworks (Flutter, React Native, etc.)
        - Web frameworks and libraries (Next.js, Express, FastAPI, etc.)
        - AI and ML tools for developers (GitHub Copilot, ChatGPT, TensorFlow, etc.)
        - Productivity and collaboration tools for developers (Slack, Discord, Notion, etc.)
        - Security and monitoring tools (SonarQube, Datadog, etc.)
        
        Extract ALL types of developer-relevant tools mentioned, not just AI tools.
        Focus on actual tool names, framework names, and platform names.
        Ignore generic terms like "software", "application", "platform" without specific names.
        Only return the JSON list, no explanation."""),
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
        ("system", """You are an expert analyst of developer tools and technologies. 
        Summarize the following tool/technology with a focus on its relevance for developers, programmers, and technical teams.
        
        Return a JSON with:
        - 'summary': 1-2 sentence summary highlighting key benefits for developers
        - 'bullets': 3-4 key features or use cases focused on development/technical applications
        
        Handle different tool types appropriately:
        - For programming languages/frameworks: focus on syntax, ecosystem, performance, use cases
        - For development tools: focus on features, integrations, workflow improvements
        - For DevOps tools: focus on deployment, scaling, monitoring capabilities
        - For databases: focus on performance, scalability, use cases
        - For AI/ML tools: focus on developer integration, APIs, technical capabilities
        - For productivity tools: focus on developer collaboration, project management features
        
        Always emphasize technical and developer-relevant aspects."""),
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
        ("system", """You are an expert analyst of developer tools and AI technologies. 
        Summarize the following AI tool with a focus on its relevance for developers, programmers, and technical teams.
        
        Return a JSON with:
        - 'summary': 1-2 sentence summary highlighting developer benefits
        - 'bullets': 3-4 key features focused on development use cases
        
        Focus on aspects like: coding assistance, development workflow, API capabilities, integration options, 
        technical features, productivity benefits for developers."""),
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
