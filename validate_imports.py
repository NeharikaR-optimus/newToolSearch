#!/usr/bin/env python3
"""
Import validation script to ensure all modules load correctly after cleanup.
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def validate_imports():
    """Test all critical imports"""
    try:
        print("🔍 Validating imports...")
        
        # Test backend config
        from config import AZURE_OPENAI_API_KEY, LANGSEARCH_API_KEY
        print("✅ Config imports: OK")
        
        # Test search agent
        from tools.search_agent import SearchAgent
        print("✅ SearchAgent import: OK")
        
        # Test workflow
        from workflow.workflow import Workflow
        print("✅ Workflow import: OK")
        
        # Test LLM components
        from tools.llm_summarizer import get_llm_tool_names_from_text
        print("✅ LLM Summarizer import: OK")
        
        # Test extractors
        from tools.article_url_extractor import extract_tool_names_llm
        print("✅ Article URL Extractor import: OK")
        
        print("\n🎉 All imports validated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Import validation failed: {e}")
        return False

if __name__ == "__main__":
    success = validate_imports()
    sys.exit(0 if success else 1)
