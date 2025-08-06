# Developer Tech Tools Discovery API

FastAPI service that discovers trending developer tools using AI-powered search.

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the API**
   ```bash
   python start.py
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Get tools: `GET /weekly-tech-tools`

5. **Optional: Run Frontend Dashboard**
   ```bash
   streamlit run frontend/app.py --server.port 8501
   ```

## Structure

```
├── backend/
│   ├── fastAPI/     # Main API server & config
│   ├── tools/       # Search & AI components
│   └── workflow/    # LangGraph workflow
├── frontend/        # Streamlit dashboard
├── start.py         # Launch script
└── requirements.txt # Dependencies
```
