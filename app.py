import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
from query import query_rag_pipeline
import base64
from pypdf import PdfReader

st.set_page_config(page_title="Document Q&A Bot", page_icon="📚", layout="wide")

st.title("📚 Document Q&A Bot")
st.markdown("Ask any question from the uploaded documents!")

# Show documents in sidebar
st.sidebar.title("📁 Uploaded Documents")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def show_pdf_text(file_path):
    reader = PdfReader(file_path)
    for i, page in enumerate(reader.pages):
        st.markdown(f"**--- Page {i+1} ---**")
        st.write(page.extract_text())

if os.path.exists(DATA_DIR):
    files = os.listdir(DATA_DIR)
    if files:
        selected_file = st.sidebar.radio(
            "Click to view a document:",
            files,
            index=None
        )
        if selected_file:
            file_path = os.path.join(DATA_DIR, selected_file)
            st.subheader(f"📄 {selected_file}")

            col1, col2 = st.columns([3, 1])
            with col2:
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download",
                        data=f,
                        file_name=selected_file
                    )

            if selected_file.endswith(".pdf"):
                show_pdf_text(file_path)
            elif selected_file.endswith(".docx"):
                from docx import Document
                doc = Document(file_path)
                for para in doc.paragraphs:
                    if para.text.strip():
                        st.write(para.text)
    else:
        st.sidebar.markdown("No documents found!")
else:
    st.sidebar.markdown("No documents folder found!")

st.sidebar.markdown("---")
st.sidebar.markdown("**How to use:**")
st.sidebar.markdown("1. Click a document to view it")
st.sidebar.markdown("2. Type your question below")
st.sidebar.markdown("3. Get answers with citations!")

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
