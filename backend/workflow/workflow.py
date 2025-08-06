
from typing import List, Dict
from collections import Counter
from langgraph.graph import StateGraph, START, END
from tools.article_url_extractor import extract_tool_names_llm
from tools.llm_summarizer import summarize_top_tools
from tools.search_agent import SearchAgent


def make_search_articles_node(top_n_articles: int = 12):
    def search_articles_node(state: Dict) -> Dict:
        search_agent = SearchAgent()
        results = search_agent.search_new_ai_tools()  # Now searches all trending tech tools
        # Get top N article URLs - increased from 4 to 12 for more diversity
        urls = [r.get('url') for r in results if r.get('url')][:top_n_articles]
        state["article_urls"] = urls
        state["search_results"] = results  # Store all results for context
        return state
    return search_articles_node

def make_extract_tools_llm_node(top_n: int = 8):
    def extract_tools_llm_node(state: Dict) -> Dict:
        tool_names = extract_tool_names_llm(state["article_urls"])
        # Increased diversity in final selection
        ranked = Counter(tool_names).most_common(top_n)
        state["top_tools"] = [name for name, _ in ranked]
        return state
    return extract_tools_llm_node

def make_llm_summarize_top_tools_node():
    def llm_summarize_top_tools_node(state: Dict) -> Dict:
        summaries = summarize_top_tools(state["top_tools"])
        state["summaries"] = summaries
        return state
    return llm_summarize_top_tools_node
class Workflow:
    def __init__(self, top_n_articles: int = 12, top_n_tools: int = 8):
        self.top_n_articles = top_n_articles
        self.top_n_tools = top_n_tools

        graph = StateGraph(dict)
        graph.add_node("search_articles", make_search_articles_node(self.top_n_articles))
        graph.add_node("extract_tools_llm", make_extract_tools_llm_node(self.top_n_tools))
        graph.add_node("llm_summarize_top_tools", make_llm_summarize_top_tools_node())

        graph.add_edge(START, "search_articles")
        graph.add_edge("search_articles", "extract_tools_llm")
        graph.add_edge("extract_tools_llm", "llm_summarize_top_tools")
        graph.add_edge("llm_summarize_top_tools", END)

        self.app = graph.compile()

    def run(self) -> List[Dict]:
        initial_state = {}
        result = self.app.invoke(initial_state)
        return result.get("summaries", [])
