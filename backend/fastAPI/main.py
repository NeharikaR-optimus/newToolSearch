
from fastapi import FastAPI, Request
from pydantic import BaseModel
from workflow.workflow import Workflow
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import json
import os

app = FastAPI()

# Instantiate workflow with path to weekly_ai_tools.json
JSON_PATH = os.path.join(os.path.dirname(__file__), "weekly_ai_tools.json")
workflow = Workflow(top_n_tools=8)  # Increased from 5 to 8 for more developer tools

RESULTS_PATH = os.path.join(os.path.dirname(__file__), "weekly_ai_tools.json")

def run_and_store_weekly_results():
    """Run workflow and store results with timestamp"""
    try:
        print("Starting workflow execution...")
        results = workflow.run()
        print(f"Workflow returned {len(results)} results")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "results": results,
            "last_updated": timestamp,
            "total_tools": len(results)
        }
        with open(RESULTS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[{timestamp}] Workflow completed. Found {len(results)} tools.")
        
        # If no results found, create a diagnostic message
        if len(results) == 0:
            print("No results found - this may indicate search API issues or overly restrictive queries")
            
    except Exception as e:
        print(f"Error in workflow: {e}")
        import traceback
        traceback.print_exc()
        # Create empty results file if workflow fails
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(RESULTS_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "results": [], 
                "last_updated": timestamp, 
                "total_tools": 0,
                "error": str(e),
                "message": "Workflow failed - check search API configuration"
            }, f)


# APScheduler setup (run every 7 days automatically)
scheduler = BackgroundScheduler()
scheduler.add_job(run_and_store_weekly_results, "interval", days=7)
scheduler.start()

# Run once at startup to ensure results exist
run_and_store_weekly_results()

class ChatRequest(BaseModel):
    message: str
    history: list

@app.post("/chatbot")
async def chatbot_endpoint(chat: ChatRequest):
    user_message = chat.message
    results = workflow.run()
    if results:
        reply = results[0]["summary"]
    else:
        reply = "Sorry, I couldn't find any new AI tools this week."
    return {"reply": reply}

@app.get("/")
def read_root():
    return {"message": "AI Tools Discovery API is running."}

@app.get("/weekly-ai-tools")
def get_weekly_ai_tools():
    """
    Return the most recent weekly discovered AI tools and their summaries.
    """
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Return the data as-is (includes metadata like last_updated)
        return data
    else:
        return {
            "results": [], 
            "last_updated": "Never", 
            "total_tools": 0,
            "message": "No tools data available. Try triggering a manual search."
        }

@app.post("/trigger-workflow")
def trigger_workflow_manually():
    """
    Manually trigger the workflow to search for new AI tools.
    """
    try:
        print("Manual workflow trigger initiated...")
        run_and_store_weekly_results()
        
        # Read the results to return them
        if os.path.exists(RESULTS_PATH):
            with open(RESULTS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            results = data.get("results", [])
            last_updated = data.get("last_updated", "Unknown")
            return {
                "message": f"Manual search completed successfully! Found {len(results)} tools.", 
                "results": results,
                "last_updated": last_updated,
                "total_tools": len(results)
            }
        else:
            return {"message": "Workflow completed but no results file found.", "results": []}
    except Exception as e:
        return {"error": str(e), "message": "Manual workflow failed"}

@app.get("/debug-config")
def debug_config():
    """
    Debug endpoint to check configuration and environment variables.
    """
    import config
    return {
        "langsearch_api_key_set": bool(config.LANGSEARCH_API_KEY),
        "azure_openai_api_key_set": bool(config.AZURE_OPENAI_API_KEY),
        "langsearch_endpoint": config.LANGSEARCH_SEARCH_ENDPOINT,
        "azure_openai_endpoint": config.AZURE_OPENAI_ENDPOINT,
        "results_file_exists": os.path.exists(RESULTS_PATH)
    }

@app.get("/test-search")
def test_search():
    """
    Debug endpoint to test the search agent directly.
    """
    try:
        from tools.search_agent import SearchAgent
        search_agent = SearchAgent()
        results = search_agent.search_new_ai_tools()
        return {
            "search_results_count": len(results),
            "search_results": results[:3] if results else [],  # Return first 3 for debugging
            "raw_response_sample": str(results[0]) if results else "No results"
        }
    except Exception as e:
        return {"error": str(e), "message": "Search test failed"}

@app.get("/test-search")
def test_search():
    """
    Debug endpoint to test the search agent directly.
    """
    try:
        from tools.search_agent import SearchAgent
        search_agent = SearchAgent()
        results = search_agent.search_new_ai_tools()
        
        # Extract URLs like the workflow does
        urls = [r.get('url') for r in results if r.get('url')]
        
        return {
            "search_results_count": len(results),
            "urls_extracted": len(urls),
            "first_result_keys": list(results[0].keys()) if results else [],
            "first_url": urls[0] if urls else None,
            "sample_result": results[0] if results else None
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e), 
            "traceback": traceback.format_exc(),
            "message": "Search test failed"
        }

@app.get("/debug-workflow")
def debug_workflow():
    """
    Debug endpoint to test each step of the workflow.
    """
    try:
        from tools.search_agent import SearchAgent
        from tools.article_url_extractor import extract_tool_names_llm
        
        # Step 1: Search
        search_agent = SearchAgent()
        search_results = search_agent.search_new_ai_tools()
        urls = [r.get('url') for r in search_results if r.get('url')][:4]
        
        # Step 2: Extract tool names (if we have URLs)
        tool_names = []
        if urls:
            tool_names = extract_tool_names_llm(urls)
        
        return {
            "step1_search_results": len(search_results),
            "step1_urls_extracted": len(urls),
            "step1_sample_urls": urls[:2],
            "step2_tool_names_found": len(tool_names),
            "step2_tool_names": tool_names[:5]
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/sample-tools")
def get_sample_tools():
    """
    Return sample AI tools data for testing the frontend.
    """
    return {
        "results": [
            {
                "name": "Claude AI Desktop",
                "summary": "Anthropic's Claude AI is now available as a desktop application for Windows and macOS, offering advanced conversational AI capabilities with improved context understanding and coding assistance.",
                "bullets": [
                    "Native desktop application for improved user experience",
                    "Enhanced context window up to 200K tokens",
                    "Advanced coding and analysis capabilities",
                    "Offline mode for sensitive data processing"
                ],
                "category": "AI Assistant",
                "website": "https://claude.ai"
            },
            {
                "name": "OpenAI Sora Video Generator", 
                "summary": "OpenAI's Sora is a revolutionary AI model that can generate realistic videos from text descriptions, supporting up to 60 seconds of high-quality footage.",
                "bullets": [
                    "Text-to-video generation with high fidelity",
                    "Supports up to 60 seconds of video content", 
                    "Multiple aspect ratios and resolutions",
                    "Advanced understanding of physics and motion"
                ],
                "category": "Video Generation",
                "website": "https://openai.com/sora"
            },
            {
                "name": "Google Gemini 2.0",
                "summary": "Google's latest Gemini 2.0 model offers enhanced multimodal capabilities with improved reasoning, coding, and real-time conversation features.",
                "bullets": [
                    "Multimodal AI with text, image, and audio processing",
                    "Real-time conversation capabilities", 
                    "Enhanced coding and mathematical reasoning",
                    "Integration with Google Workspace tools"
                ],
                "category": "AI Model",
                "website": "https://gemini.google.com"
            }
        ]
    }
