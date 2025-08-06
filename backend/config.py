# Simple configuration
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
LANGSEARCH_API_KEY = os.environ.get("LANGSEARCH_API_KEY", "")
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://newaitoolssearch-resource.cognitiveservices.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2025-01-01-preview")

# URLs
LANGSEARCH_SEARCH_ENDPOINT = "https://api.langsearch.com/v1/web-search"
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
