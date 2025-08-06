from typing import List
import json
import requests
from bs4 import BeautifulSoup
from .llm_summarizer import get_llm_tool_names_from_text
import re
from collections import Counter

def extract_tool_names_llm(urls: List[str], timeout: int = 8) -> list:
    """
    Fetches all article texts, concatenates them, and uses a single LLM call to extract AI tool names.
    Returns a list of tool names.
    """
    article_texts = []
    for url in urls:
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(" ", strip=True)
            article_texts.append(text)
        except Exception:
            continue
    combined_text = '\n'.join(article_texts)
    if not combined_text.strip():
        return []
    return get_llm_tool_names_from_text(combined_text)
def extract_article_urls(json_path: str) -> List[str]:
    """
    Extracts all article URLs from the 'website' field in the weekly_ai_tools.json file.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    results = data.get('results', [])
    urls = [item.get('website') for item in results if item.get('website')]
    return urls


def extract_tool_names_from_articles(urls: List[str], timeout: int = 8) -> Counter:
    """
    Crawls each article URL and extracts probable AI tool names from the entire article text.
    Returns a Counter of tool name frequencies.
    """
    tool_name_counter = Counter()
    tool_pattern = re.compile(r"([A-Z][a-zA-Z0-9\-]+(?: [A-Z][a-zA-Z0-9\-]+)*)")
    blacklist = {"AI", "Tools", "App", "Agent", "Labs", "Software", "Platform", "Applications", "Assistant", "Product", "Framework", "Games", "Books", "Examples", "Recents", "Facebook", "Home", "Contact", "About", "Login", "Register", "Read", "Learn", "Explore", "More", "News", "Guide", "Review", "Top", "Best", "List", "Features", "Pricing", "Website", "Summary", "Category"}
    for url in urls:
        print(f"\nProcessing URL: {url}")
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code != 200:
                print(f"  Failed to fetch (status {resp.status_code})")
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            probable_tools = set()
            all_text = soup.get_text(" ", strip=True)
            for m in tool_pattern.findall(all_text):
                if m not in blacklist and len(m) > 2 and not m.islower():
                    print(f"  Found tool (anywhere): {m}")
                    probable_tools.add(m)
            filtered = [t for t in probable_tools if t not in blacklist and len(t) > 2 and not t.islower()]
            print(f"  Tools extracted from this URL: {filtered}")
            tool_name_counter.update(filtered)
        except Exception as e:
            print(f"  Exception: {e}")
            continue
    print(f"\nFinal tool name counts: {tool_name_counter}")
    return tool_name_counter
