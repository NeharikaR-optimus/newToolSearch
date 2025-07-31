

from typing import List, Dict
from langgraph.graph import StateGraph, START, END

from backend.tools.search_agent import SearchAgent
from backend.tools.extractor import extract_tool_info

from backend.tools.llm_tool import summarize_tool_with_llm

def make_search_node(search_agent):
    def search_node(state: Dict) -> Dict:
        state["search_results"] = search_agent.search_new_ai_tools()
        return state
    return search_node

def make_extract_node():
    def extract_node(state: Dict) -> Dict:
        state["extracted_tools"] = [extract_tool_info(r) for r in state["search_results"]]
        return state
    return extract_node

def make_llm_summarize_node():
    def llm_summarize_node(state: Dict) -> Dict:
        summaries = [summarize_tool_with_llm(tool) for tool in state["extracted_tools"]]
        state["summaries"] = summaries
        return state
    return llm_summarize_node
class Workflow:
    def __init__(self, search_agent):
        self.search_agent = search_agent

        graph = StateGraph(dict)
        graph.add_node("search", make_search_node(self.search_agent))
        graph.add_node("extract", make_extract_node())
        graph.add_node("llm_summarize", make_llm_summarize_node())

        graph.add_edge(START, "search")
        graph.add_edge("search", "extract")
        graph.add_edge("extract", "llm_summarize")
        graph.add_edge("llm_summarize", END)

        self.app = graph.compile()

    def run(self) -> List[Dict]:
        initial_state = {}
        result = self.app.invoke(initial_state)
        return result.get("summaries", [])
