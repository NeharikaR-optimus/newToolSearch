
from fastapi import FastAPI, Request
from pydantic import BaseModel
from workflow.workflow import Workflow
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os

app = FastAPI()


# Instantiate workflow with path to weekly_ai_tools.json
JSON_PATH = os.path.join(os.path.dirname(__file__), "weekly_ai_tools.json")
workflow = Workflow(top_n_tools=5)

RESULTS_PATH = os.path.join(os.path.dirname(__file__), "weekly_ai_tools.json")

def run_and_store_weekly_results():
    results = workflow.run()
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, ensure_ascii=False, indent=2)


# APScheduler setup (run every minute for testing)
scheduler = BackgroundScheduler()
scheduler.add_job(run_and_store_weekly_results, "interval", minutes=1)
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
            return json.load(f)
    else:
        return {"results": []}

@app.post("/trigger-workflow")
def trigger_workflow_manually():
    """
    Manually trigger the workflow to search for AI tools.
    """
    try:
        results = workflow.run()
        with open(RESULTS_PATH, "w", encoding="utf-8") as f:
            json.dump({"results": results}, f, ensure_ascii=False, indent=2)
        return {"message": f"Workflow completed successfully. Found {len(results)} tools.", "results": results}
    except Exception as e:
        return {"error": str(e), "message": "Workflow failed"}

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
