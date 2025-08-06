# Developer Tech Tools Discovery System

🔍 AI-powered discovery system that finds trending developer tools across multiple technology categories using intelligent search and Azure OpenAI summarization.

## Features

- 🚀 **Multi-Category Search**: AI tools, web frameworks, mobile dev, DevOps, languages, databases, productivity, security
- 🤖 **AI Summarization**: Azure OpenAI powered tool summaries and extraction
- 📊 **Smart Filtering**: Freshness scoring, domain diversity, and quality validation
- 🎯 **Strategic Queries**: 8 targeted search strategies for comprehensive coverage
- 📈 **Interactive Dashboard**: Streamlit frontend with category tabs and real-time updates

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys:
# - LANGSEARCH_API_KEY: Your LangSearch API key
# - AZURE_OPENAI_API_KEY: Your Azure OpenAI API key  
# - AZURE_OPENAI_ENDPOINT: Your Azure OpenAI endpoint URL
```

### 3. Start the Backend API
```bash
python start.py
```

### 4. Launch the Frontend Dashboard (Optional)
```bash
streamlit run frontend/app.py --server.port 8501
```

### 5. Access the System
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend Dashboard**: http://localhost:8501
- **Get Tools**: `GET /weekly-tech-tools`
- **Trigger Discovery**: `POST /trigger-workflow`

## Project Structure

```
📁 Developer Tech Tools Discovery
├── 📄 .env.example             # Environment template
├── 📄 requirements.txt         # Python dependencies
├── 📄 start.py                 # Production startup script
├── 📁 backend/
│   ├── 📄 config.py            # Centralized configuration
│   ├── 📁 fastAPI/
│   │   ├── 📄 main.py          # FastAPI server & endpoints
│   │   └── 📄 weekly_tech_tools.json  # Cached results
│   ├── 📁 tools/
│   │   ├── 📄 search_agent.py  # Multi-strategy search engine
│   │   ├── 📄 llm_summarizer.py # Azure OpenAI integration
│   │   ├── 📄 article_url_extractor.py # Content processing
│   │   └── 📄 extractor.py     # Tool info extraction
│   └── 📁 workflow/
│       └── 📄 workflow.py      # LangGraph orchestration
└── 📁 frontend/
    └── 📄 app.py               # Streamlit dashboard
```

## API Endpoints

- `GET /weekly-tech-tools` - Get discovered tools
- `POST /trigger-workflow` - Manually trigger discovery
- `GET /health` - Health check
- `GET /debug-workflow` - Debug information

## Technology Stack

- **Backend**: FastAPI, LangGraph, LangChain
- **AI**: Azure OpenAI (GPT-4o-mini)
- **Search**: LangSearch API
- **Frontend**: Streamlit
- **Processing**: BeautifulSoup, Requests, JSON

## Search Categories

1. **AI Tools** - Development-focused AI assistants and APIs
2. **Web Frameworks** - React, Vue, Angular, Next.js, etc.
3. **Mobile Development** - Flutter, React Native, native tools
4. **DevOps** - Kubernetes, Docker, deployment tools
5. **Programming Languages** - New languages and compilers
6. **Databases** - SQL, NoSQL, and data storage solutions
7. **Productivity** - IDEs, editors, collaboration tools
8. **Security** - Testing frameworks and security tools

## Configuration

Key environment variables in `.env`:

```bash
# Required API Keys
LANGSEARCH_API_KEY=sk-your-key-here
AZURE_OPENAI_API_KEY=your-azure-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Optional Configuration
ENVIRONMENT=development|production
BACKEND_URL=http://localhost:8000
```
