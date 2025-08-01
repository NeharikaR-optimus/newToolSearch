
from typing import List, Dict
import requests
import sys
import os
import time
last_fetch_file = "last_fetch.json"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from config import LANGSEARCH_API_KEY, LANGSEARCH_SEARCH_ENDPOINT
from datetime import datetime

class SearchAgent:
    def search_tool(self, tool_name: str):
        headers = {
            "Authorization": f"Bearer {LANGSEARCH_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "query": tool_name,
            "freshness": "oneMonth",
            "summary": True,
            "count": 1
        }
        response = requests.post(LANGSEARCH_SEARCH_ENDPOINT, headers=headers, json=body)
        if response.status_code != 200:
            print("LangSearch error:", response.text)
            return []
        data = response.json()
        return data.get("data", {}).get("webPages", {}).get("value", [])
    def search_new_ai_tools(self) -> List[Dict]:
        """
        Uses LangSearch Web Search API to find new AI tools announced in the last 7 days.
        Returns a list of raw search results (dicts with 'url', 'name', 'snippet', etc.).
        """
        import json
        from datetime import datetime
        now = datetime.now()
        today = now.strftime("%B %Y")
        query = f"new AI tool released {today} OR AI product launch {today} OR AI app launch {today}"
        headers = {
            "Authorization": f"Bearer {LANGSEARCH_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "query": query,
            "freshness": "oneWeek",
            "summary": True,
            "count": 10
        }
        response = requests.post(LANGSEARCH_SEARCH_ENDPOINT, headers=headers, json=body)
        if response.status_code == 429:
            print("LangSearch rate limit hit, returning empty list.")
            return []
        if response.status_code != 200:
            print("LangSearch error:", response.text)
            response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("webPages", {}).get("value", [])

    def llm_summarize_tool(self, name, snippets):
        """
        Summarize the tool using LLM. Replace this with your actual LLM call.
        """
        joined = " ".join(snippets)
        return f"{name}: {joined[:300]}..." if joined else f"No summary available for {name}."
    def force_fetch_and_store(self, results_path: str = "weekly_ai_tools.json"):
        """
        Force a new fetch and store the results to the given file.
        """
        results = self.search_new_ai_tools(force_fetch=True)
        import json
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump({"results": results}, f, ensure_ascii=False, indent=2)
        print(f"Forced fetch complete. Results written to {results_path}")


