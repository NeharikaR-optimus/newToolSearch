
import streamlit as st
import requests

st.set_page_config(page_title="AI Tools Discovery Dashboard", page_icon="🤖")
st.title("🤖 Weekly AI Tools Discovery Dashboard")

# Azure backend URL - Container Instance deployment
API_URL = "http://ai-tools.dwdwbef5fth7hwe7.eastus.azurecontainer.io:8000/sample-tools"

st.info("📡 Connected to Azure backend - This dashboard displays the latest AI tools discovered!")

if st.button("🔄 Refresh AI Tools List"):
    st.session_state["ai_tools"] = None

if "ai_tools" not in st.session_state or st.session_state["ai_tools"] is None:
    with st.spinner("Fetching AI tools from Azure backend..."):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()
            st.session_state["ai_tools"] = data.get("results", [])
            st.success(f"✅ Successfully loaded {len(st.session_state['ai_tools'])} AI tools from Azure!")
        except Exception as e:
            st.error(f"❌ Error fetching AI tools from backend: {e}")
            st.session_state["ai_tools"] = []

ai_tools = st.session_state["ai_tools"]

if not ai_tools:
    st.warning("⚠️ No AI tools found. Please check your backend connection.")
else:
    st.markdown(f"**📊 Found {len(ai_tools)} AI Tools:**")
    
    for i, tool in enumerate(ai_tools, 1):
        with st.container():
            st.markdown(f"### {i}. {tool.get('name', 'AI Tool')} 🎯")
            
            # Create two columns for better layout
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
