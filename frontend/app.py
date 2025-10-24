"""
Streamlit frontend for Project Samarth Phase 2
Simple chat interface for the Q&A system
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Project Samarth Q&A",
    page_icon="🌾",
    layout="wide"
)

# API endpoint
API_BASE = "http://localhost:8000"

def ask_question(question):
    """Send question to API"""
    try:
        response = requests.post(f"{API_BASE}/ask", json={"question": question})
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_datasets():
    """Get available datasets"""
    try:
        response = requests.get(f"{API_BASE}/datasets")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Main app
st.title("🌾 Project Samarth Q&A System")
st.markdown("*Intelligent Q&A for Indian Agriculture and Climate Data*")

# Sidebar with dataset info
with st.sidebar:
    st.header("📊 Available Datasets")
    
    datasets_info = get_datasets()
    if "error" not in datasets_info:
        st.success(f"✅ {datasets_info['count']} datasets loaded")
        
        with st.expander("View Datasets"):
            for dataset in datasets_info['datasets']:
                st.write(f"**{dataset['title']}**")
                st.write(f"- Publisher: {dataset['publisher']}")
                st.write(f"- Granularity: {dataset['geo_granularity']}")
                st.write(f"- Years: {dataset['available_years']}")
                st.write("---")
    else:
        st.error("❌ Could not load datasets")

# Sample questions
st.header("💡 Sample Questions")
sample_questions = [
    "Compare the average annual rainfall in Maharashtra and Punjab",
    "Show me the rice production trend in Punjab from 2010 to 2014",
    "Which state has the highest wheat production?",
    "Analyze the correlation between rainfall and crop production",
    "What is the average cotton production in Gujarat?"
]

cols = st.columns(len(sample_questions))
for i, question in enumerate(sample_questions):
    with cols[i]:
        if st.button(f"Q{i+1}", help=question):
            st.session_state.question = question

# Main chat interface
st.header("💬 Ask Your Question")

# Question input
question = st.text_input(
    "Enter your question about Indian agriculture and climate:",
    value=st.session_state.get('question', ''),
    placeholder="e.g., Compare rainfall in Maharashtra and Punjab"
)

if st.button("🔍 Ask", type="primary") and question:
    with st.spinner("Processing your question..."):
        response = ask_question(question)
    
    if "error" in response:
        st.error(f"❌ Error: {response['error']}")
    else:
        # Display answer
        st.success("✅ Answer Generated")
        
        # Answer text
        st.subheader("📝 Answer")
        st.write(response['answer_text'])
        
        # Structured results
        if response['structured_results']:
            st.subheader("📊 Data Results")
            df = pd.DataFrame(response['structured_results'])
            st.dataframe(df, use_container_width=True)
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"samarth_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # Citations
        if response['citations']:
            st.subheader("📚 Data Sources")
            for i, citation in enumerate(response['citations'], 1):
                with st.expander(f"Source {i}: {citation['dataset_title']}"):
                    st.write(f"**Publisher:** {citation.get('publisher', 'Unknown')}")
                    st.write(f"**URL:** {citation['resource_url']}")
                    st.write(f"**Usage:** {citation.get('query_summary', 'Used in analysis')}")
        
        # Processing info
        if 'processing_info' in response:
            with st.expander("🔧 Processing Details"):
                st.json(response['processing_info'])

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>🌾 Project Samarth Phase 2 - Built with FastAPI + Streamlit</p>
        <p>Data sources: data.gov.in, India Meteorological Department</p>
    </div>
    """,
    unsafe_allow_html=True
)