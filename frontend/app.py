
import streamlit as st
import requests

st.set_page_config(page_title="AI Developer Tools Dashboard", page_icon="")
st.title("AI Developer Tools Discovery Dashboard")

# Use the real workflow endpoint instead of sample data
API_URL = "http://ai-tools.dwdwbef5fth7hwe7.eastus.azurecontainer.io:8000/weekly-ai-tools"
SAMPLE_URL = "http://ai-tools.dwdwbef5fth7hwe7.eastus.azurecontainer.io:8000/sample-tools"

st.info("Discovering AI tools specifically for developers, programmers, and technical teams!")

# Add info about tool categories
with st.expander("What types of AI tools do we discover?"):
    st.markdown("""
    **Our search focuses on developer-relevant AI tools including:**
    
    **Development Tools**
    - Code assistants and AI pair programming tools
    - IDE extensions and plugins
    - Code generation and completion tools
    
    **APIs & Platforms** 
    - AI/ML APIs and SDKs
    - Development platforms and environments
    - AI-powered development services
    
    **DevOps & Workflow**
    - CI/CD automation tools
    - Testing and quality assurance tools
    - Documentation and code review tools
    
    **ML/AI Development**
    - Machine learning frameworks and libraries
    - Model training and deployment tools
    - Data science and analytics platforms
    """)

col1, col2 = st.columns(2)

with col1:
    if st.button("Refresh & Search New Tools"):
        with st.spinner("Searching for new developer-focused AI tools..."):
            try:
                trigger_url = "http://ai-tools.dwdwbef5fth7hwe7.eastus.azurecontainer.io:8000/trigger-workflow"
                response = requests.post(trigger_url)
                response.raise_for_status()
                result = response.json()
                st.success(f"{result.get('message', 'New search completed!')}")
                st.session_state["ai_tools"] = None
            except Exception as e:
                st.error(f"Error triggering search: {e}")

with col2:
    if st.button("Load Cached Results"):
        st.session_state["ai_tools"] = None
        st.info("Loading cached results from last search...")

# Add debug section
st.sidebar.title("Debug Panel")
if st.sidebar.button("Show Search Debug Info"):
    with st.sidebar:
        try:
            debug_response = requests.get("http://ai-tools.dwdwbef5fth7hwe7.eastus.azurecontainer.io:8000/debug-config")
            debug_data = debug_response.json()
            st.json(debug_data)
        except Exception as e:
            st.error(f"Debug error: {e}")

if st.sidebar.button("Show Sample Data"):
    st.session_state["show_sample"] = True

if "ai_tools" not in st.session_state or st.session_state["ai_tools"] is None:
    with st.spinner("Fetching AI tools from backend..."):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()
            st.session_state["ai_tools"] = data.get("results", [])
            st.session_state["last_updated"] = data.get("last_updated", "Unknown")
            st.session_state["total_tools"] = data.get("total_tools", len(st.session_state["ai_tools"]))
            
            # If no real results, offer to show sample data
            if not st.session_state["ai_tools"]:
                # Check if there's an error message
                error_msg = data.get("error", "")
                diagnostic_msg = data.get("message", "")
                
                if error_msg:
                    st.error(f"Workflow Error: {error_msg}")
                if diagnostic_msg:
                    st.warning(f"{diagnostic_msg}")
                else:
                    st.warning("No real AI tools found from workflow. The search may need optimization.")
                
                st.info("This could be due to:")
                st.markdown("""
                - Search API rate limiting
                - Overly restrictive search queries  
                - Network connectivity issues
                - Search results not containing extractable tool information
                """)
                
                if st.button("Load Sample Data Instead"):
                    sample_response = requests.get(SAMPLE_URL)
                    sample_data = sample_response.json()
                    st.session_state["ai_tools"] = sample_data.get("results", [])
                    st.session_state["last_updated"] = "Sample Data"
                    st.session_state["is_sample"] = True
                    st.rerun()
            else:
                st.success(f"Successfully loaded {len(st.session_state['ai_tools'])} real AI tools from workflow!")
                st.info(f"Last updated: {st.session_state['last_updated']}")
                st.session_state["is_sample"] = False
        except Exception as e:
            st.error(f"Error fetching AI tools: {e}")
            st.session_state["ai_tools"] = []

# Handle sample data display request
if st.session_state.get("show_sample", False):
    with st.spinner("Loading sample data..."):
        try:
            sample_response = requests.get(SAMPLE_URL)
            sample_data = sample_response.json()
            st.session_state["ai_tools"] = sample_data.get("results", [])
            st.session_state["last_updated"] = "Sample Data"
            st.session_state["is_sample"] = True
            st.session_state["show_sample"] = False
        except Exception as e:
            st.error(f"Error loading sample data: {e}")

ai_tools = st.session_state["ai_tools"]

if not ai_tools:
    st.warning("No AI tools found. Please check your backend connection.")
else:
    # Show data source indicator
    if st.session_state.get("is_sample", False):
        st.info("Currently showing sample data for demonstration")
    else:
        st.success("Showing real workflow results")
    
    st.markdown(f"**Found {len(ai_tools)} AI Tools:**")
    
    for i, tool in enumerate(ai_tools, 1):
        with st.container():
            st.markdown(f"### {i}. {tool.get('name', 'AI Tool')}")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Summary:** {tool.get('summary', 'N/A')}")
                st.markdown("**Key Features:**")
                for feat in tool.get("bullets", []):
                    st.markdown(f"  • {feat}")
            
            with col2:
                st.markdown(f"**Category:** `{tool.get('category', 'AI Tool')}`")
                if tool.get('website'):
                    st.markdown(f"**Website:** [Visit]({tool.get('website', '')})")
            
            st.markdown("---")
