
import streamlit as st
import requests

st.set_page_config(page_title="AI Tools Discovery Dashboard", page_icon="🤖")
st.title("🤖 Weekly AI Tools Discovery Dashboard")

# Azure backend URL - Container Instance deployment
API_URL = "http://ai-tools.dwdwbef5fth7hwe7.eastus.azurecontainer.io:8000/weekly-ai-tools"

st.info("This dashboard displays the latest AI tools discovered in the past week.")

if st.button("Refresh AI Tools List"):
    st.session_state["ai_tools"] = None

if "ai_tools" not in st.session_state or st.session_state["ai_tools"] is None:
    with st.spinner("Fetching latest AI tools..."):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()
            st.session_state["ai_tools"] = data.get("results", [])
        except Exception as e:
            st.error(f"Error fetching AI tools: {e}")
            st.session_state["ai_tools"] = []

ai_tools = st.session_state["ai_tools"]

if not ai_tools:
    st.warning("No new AI tools found for the past week.")
else:
    for tool in ai_tools:
        st.subheader(f"{tool.get('name', 'AI Tool')}")
        st.markdown(f"**Summary:** {tool.get('summary', 'N/A')}")
        st.markdown("**Key Features:**")
        for feat in tool.get("bullets", []):
            st.markdown(f"- {feat}")
        st.markdown(f"**Category:** {tool.get('category', 'AI Tool')}")
        st.markdown(f"**Website:** [{tool.get('website', '')}]({tool.get('website', '')})")
        st.markdown("---")
