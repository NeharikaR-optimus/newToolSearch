
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
        Uses LangSearch Web Search API to find AI tools relevant for developers.
        Returns a list of raw search results (dicts with 'url', 'name', 'snippet', etc.).
        """
        import json
        # Focus on developer-relevant AI tools and recent releases
        queries = [
            "new AI developer tools 2024 2025 programming coding",
            "AI code generation tools GitHub Copilot alternatives",
            "AI development tools machine learning MLOps",
            "developer AI tools API libraries frameworks",
            "coding assistant AI tools IDE extensions"
        ]
        
        all_results = []
        
        for query in queries:
            headers = {
                "Authorization": f"Bearer {LANGSEARCH_API_KEY}",
                "Content-Type": "application/json"
            }
            body = {
                "query": query,
                "freshness": "oneMonth",  # Look for recent tools
                "summary": True,
                "count": 5  # Fewer results per query to avoid rate limits
            }
            print(f"Searching with query: {query}")
            
            try:
                response = requests.post(LANGSEARCH_SEARCH_ENDPOINT, headers=headers, json=body)
                print(f"LangSearch response status: {response.status_code}")
                
                if response.status_code == 429:
                    print("LangSearch rate limit hit, skipping this query.")
                    continue
                    
                if response.status_code != 200:
                    print(f"LangSearch error for query '{query}': {response.text}")
                    continue
                    
                data = response.json()
                results = data.get("data", {}).get("webPages", {}).get("value", [])
                print(f"Query '{query}' returned {len(results)} results")
                all_results.extend(results)
                
                # Add delay between requests to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error with query '{query}': {e}")
                continue
        
        print(f"Total search results collected: {len(all_results)}")
        # Remove duplicates based on URL
        unique_results = []
        seen_urls = set()
        for result in all_results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        print(f"Unique results after deduplication: {len(unique_results)}")
        return unique_results[:15]  # Return top 15 unique results

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
        results = self.search_new_ai_tools()
        import json
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump({"results": results}, f, ensure_ascii=False, indent=2)
        print(f"Forced fetch complete. Results written to {results_path}")


