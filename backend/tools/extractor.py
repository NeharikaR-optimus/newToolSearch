from typing import Dict
import requests
from bs4 import BeautifulSoup

def extract_tool_info(result: Dict) -> Dict:
    name = result.get("name")
    website = result.get("url")
    snippet = result.get("snippet", "")
    summary = result.get("summary", "")
    functionality = summary or snippet
    audience = "General AI users"
    features = [snippet[:100]] if snippet else []
    pricing = "Unknown"
    category = "AI Tool"
    # Try to crawl the website for more info
    try:
        resp = requests.get(website, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                functionality = meta_desc["content"]
            if not name:
                title = soup.find("title")
                if title:
                    name = title.text.strip()
            text = soup.get_text(" ", strip=True).lower()
            for word in ["free", "trial", "pricing", "$", "price", "subscription"]:
                if word in text:
                    pricing = "See website for details"
                    break
    except Exception:
        pass
    return {
        "name": name,
        "website": website,
        "functionality": functionality,
        "audience": audience,
        "features": features,
        "pricing": pricing,
        "category": category
    }
