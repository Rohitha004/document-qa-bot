import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
from query import query_rag_pipeline

st.set_page_config(page_title="Document Q&A Bot", page_icon="📚", layout="wide")

st.title("📚 Document Q&A Bot")
st.markdown("Upload your documents and ask any question!")

# Sidebar
st.sidebar.title("📁 Document Manager")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# File uploader
st.sidebar.markdown("### ⬆️ Upload Documents")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF or DOCX files",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

if uploaded_files:
    os.makedirs(DATA_DIR, exist_ok=True)
    for uploaded_file in uploaded_files:
        file_path = os.path.join(DATA_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    st.sidebar.success(f"✅ {len(uploaded_files)} file(s) uploaded!")

    if st.sidebar.button("🔄 Index Documents"):
        with st.spinner("Indexing documents... Please wait..."):
            try:
                from ingest import extract_pdf_pages, extract_docx_pages, chunk_extracted_pages, save_to_vector_db
                all_pages = []
                files = os.listdir(DATA_DIR)
                for file in files:
                    file_path = os.path.join(DATA_DIR, file)
                    if file.endswith(".pdf"):
                        all_pages.extend(extract_pdf_pages(file_path))
                    elif file.endswith(".docx"):
                        all_pages.extend(extract_docx_pages(file_path))
                chunks = chunk_extracted_pages(all_pages)
                save_to_vector_db(chunks)
                st.sidebar.success("✅ Documents indexed successfully!")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

# Show existing documents
st.sidebar.markdown("---")
st.sidebar.markdown("### 📄 Documents:")

if os.path.exists(DATA_DIR):
    files = os.listdir(DATA_DIR)
    if files:
        for file in files:
            st.sidebar.markdown(f"📄 {file}")
    else:
        st.sidebar.markdown("No documents yet. Upload some!")

st.sidebar.markdown("---")
st.sidebar.markdown("**How to use:**")
st.sidebar.markdown("1. Upload PDF or DOCX files")
st.sidebar.markdown("2. Click Index Documents")
st.sidebar.markdown("3. Ask questions below!")

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
