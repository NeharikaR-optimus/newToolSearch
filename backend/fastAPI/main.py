
from fastapi import FastAPI, Request
from pydantic import BaseModel
from backend.workflow.workflow import Workflow
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
