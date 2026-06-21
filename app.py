import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
from query import query_rag_pipeline
from pypdf import PdfReader
from docx import Document

st.set_page_config(page_title="Document Q&A Bot", page_icon="📚", layout="wide")

st.title("📚 Document Q&A Bot")
st.markdown("Ask any question from the uploaded documents!")

# Sidebar
st.sidebar.title("📁 Uploaded Documents")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]

if os.path.exists(DATA_DIR):
    files = os.listdir(DATA_DIR)
    if files:
        st.sidebar.markdown("**Documents:**")
        for i, file in enumerate(files):
            color = colors[i % len(colors)]
            st.sidebar.markdown(
                f'<div style="background-color:{color}; padding:8px; border-radius:8px; margin:5px 0; color:black; font-weight:bold;">📄 {file}</div>',
                unsafe_allow_html=True
            )
    else:
        st.sidebar.markdown("No documents found!")
else:
    st.sidebar.markdown("No documents folder found!")

st.sidebar.markdown("---")
st.sidebar.markdown("**How to use:**")
st.sidebar.markdown("1. View documents listed above")
st.sidebar.markdown("2. Type your question below")
st.sidebar.markdown("3. Get answers with citations!")

# Chat section
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("---")
st.subheader("💬 Chat")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            try:
                result = query_rag_pipeline(prompt)
                answer = result["answer"]
                citations = result["citations"]

                response = f"{answer}\n\n**Sources:**\n"
                for citation in citations:
                    response += f"- {citation}\n"

                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"Error: {e}")
