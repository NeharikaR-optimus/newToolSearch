import streamlit as st
import requests
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import BACKEND_URL

st.set_page_config(page_title="Developer Tech Tools Dashboard", page_icon="🔧")
st.title("Developer Tech Tools Discovery Dashboard")

# Dynamic API URLs based on environment
API_URL = f"{BACKEND_URL}/weekly-tech-tools"
TRIGGER_URL = f"{BACKEND_URL}/trigger-workflow"
DEBUG_URL = f"{BACKEND_URL}/debug-workflow"

def display_tool(tool):
    """Display a single tool in a nice format"""
    with st.container():
        st.markdown("---")
        
        # Tool header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### 🔧 {tool.get('name', 'Unknown Tool')}")
            if tool.get('url'):
                st.markdown(f"🔗 **Link:** [{tool['url']}]({tool['url']})")
        
        with col2:
            if tool.get('freshness_score'):
                score = tool['freshness_score']
                if score >= 0.8:
                    st.success(f"🔥 Fresh: {score:.1f}")
                elif score >= 0.6:
                    st.warning(f"⚡ Recent: {score:.1f}")
                else:
                    st.info(f"📅 Older: {score:.1f}")
        
        # Tool description
        if tool.get('description'):
            st.markdown(f"**Description:** {tool['description']}")
        
        # Tool summary (AI-generated)
        if tool.get('summary'):
            with st.expander("🤖 AI Summary"):
                st.markdown(tool['summary'])
        
        # Additional metadata
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if tool.get('category'):
                st.markdown(f"**Category:** {tool['category']}")
        
        with col2:
            if tool.get('source'):
                st.markdown(f"**Source:** {tool['source']}")
        
        with col3:
            if tool.get('discovered_at'):
                st.markdown(f"**Discovered:** {tool['discovered_at']}")

def fetch_tools():
    """Fetch tools from the API"""
    try:
        response = requests.get(API_URL, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def trigger_workflow():
    """Trigger the workflow manually"""
    try:
        response = requests.post(TRIGGER_URL, timeout=60)
        if response.status_code == 200:
            result = response.json()
            st.success("Workflow triggered successfully!")
            st.json(result)
            return True
        else:
            st.error(f"Workflow Error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return False

def debug_workflow():
    """Get workflow debug information"""
    try:
        response = requests.get(DEBUG_URL, timeout=30)
        if response.status_code == 200:
            debug_info = response.json()
            st.json(debug_info)
            return debug_info
        else:
            st.error(f"Debug Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# Main UI
st.markdown("### 🔍 Discover Weekly Tech Tools")
st.markdown("Find trending developer tools across multiple categories with AI-powered search and summarization.")

# Control buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Refresh Tools", type="primary"):
        st.rerun()

with col2:
    if st.button("🚀 Trigger Workflow"):
        with st.spinner("Running workflow..."):
            if trigger_workflow():
                st.rerun()

with col3:
    if st.button("🔍 Debug Info"):
        with st.spinner("Fetching debug info..."):
            debug_workflow()

# Fetch and display tools
with st.spinner("Loading tools..."):
    tools_data = fetch_tools()

if tools_data:
    tools = tools_data.get('results', [])  # Changed from 'tools' to 'results'
    
    if tools:
        st.success(f"Found {len(tools)} trending tools!")
        
        # Create tabs for different categories
        categories = {}
        for tool in tools:
            category = tool.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(tool)
        
        if len(categories) > 1:
            tab_names = list(categories.keys())
            tabs = st.tabs(tab_names)
            
            for i, (category, category_tools) in enumerate(categories.items()):
                with tabs[i]:
                    st.markdown(f"### {category}")
                    for tool in category_tools:
                        display_tool(tool)
        else:
            # Single category or no categories
            for tool in tools:
                display_tool(tool)
    else:
        st.warning("No tools found. Try triggering the workflow to discover new tools.")
else:
    st.error("Unable to fetch tools. Please check if the backend is running.")

# Sidebar with additional info
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.markdown("""
    This dashboard shows trending developer tools discovered through:
    
    🔍 **Smart Search**: Multiple search strategies across tech categories
    
    🤖 **AI Summarization**: Azure OpenAI powered summaries
    
    📊 **Freshness Scoring**: Prioritizes recent discoveries
    
    🎯 **Category Coverage**: AI, Web, Mobile, DevOps, Languages, Databases, Productivity, Security
    """)
    
    st.markdown("### 🔧 API Status")
    try:
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health_response.status_code == 200:
            st.success("✅ Backend Online")
        else:
            st.error("❌ Backend Issues")
    except requests.exceptions.RequestException:
        st.error("❌ Backend Offline")
    
    st.markdown(f"**Backend URL:** {BACKEND_URL}")
    
    st.markdown("### 📈 Quick Stats")
    if tools_data:
        st.metric("Total Tools", len(tools_data.get('results', [])))
        if tools_data.get('total_tools', 0) > 0:
            st.metric("Total Available", tools_data.get('total_tools', 0))
        if 'last_updated' in tools_data:
            st.metric("Last Updated", tools_data['last_updated'])
