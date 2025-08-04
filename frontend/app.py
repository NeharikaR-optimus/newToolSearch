
import streamlit as st
import requests

st.set_page_config(page_title="AI Tools Discovery Dashboard", page_icon="🤖")
st.title("🤖 Weekly AI Tools Discovery Dashboard")

API_URL = "http://ai-tools.dwdwbef5fth7hwe7.eastus.azurecontainer.io:8000/weekly-ai-tools"

st.info("Connected to Azure backend - Auto-updates weekly, manual refresh triggers new search!")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Refresh & Search New Tools"):
        with st.spinner("Triggering new AI tools search..."):
            try:
                trigger_url = "http://ai-tools.dwdwbef5fth7hwe7.eastus.azurecontainer.io:8000/trigger-workflow"
                response = requests.post(trigger_url)
                response.raise_for_status()
                result = response.json()
                st.success(f"✅ {result.get('message', 'New search completed!')}")
                st.session_state["ai_tools"] = None
            except Exception as e:
                st.error(f"❌ Error triggering search: {e}")

with col2:
    if st.button("📄 Load Cached Results"):
        st.session_state["ai_tools"] = None
        st.info("Loading cached results from last search...")

if "ai_tools" not in st.session_state or st.session_state["ai_tools"] is None:
    with st.spinner("Fetching AI tools from backend..."):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()
            st.session_state["ai_tools"] = data.get("results", [])
            st.session_state["last_updated"] = data.get("last_updated", "Unknown")
            st.session_state["total_tools"] = data.get("total_tools", len(st.session_state["ai_tools"]))
            
            if st.session_state["ai_tools"]:
                st.success(f"✅ Successfully loaded {len(st.session_state['ai_tools'])} AI tools!")
                st.info(f"🕒 Last updated: {st.session_state['last_updated']}")
            else:
                st.warning("⚠️ No tools found. Try clicking 'Refresh & Search New Tools' to trigger a new search.")
        except Exception as e:
            st.error(f"❌ Error fetching AI tools: {e}")
            st.session_state["ai_tools"] = []

ai_tools = st.session_state["ai_tools"]

if not ai_tools:
    st.warning("⚠️ No AI tools found. Please check your backend connection.")
else:
    st.markdown(f"**📊 Found {len(ai_tools)} AI Tools:**")
    
    for i, tool in enumerate(ai_tools, 1):
        with st.container():
            st.markdown(f"### {i}. {tool.get('name', 'AI Tool')} 🎯")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**📝 Summary:** {tool.get('summary', 'N/A')}")
                st.markdown("**🎯 Key Features:**")
                for feat in tool.get("bullets", []):
                    st.markdown(f"  • {feat}")
            
            with col2:
                st.markdown(f"**🏷️ Category:** `{tool.get('category', 'AI Tool')}`")
                if tool.get('website'):
                    st.markdown(f"**🔗 Website:** [Visit]({tool.get('website', '')})")
            
            st.markdown("---")
