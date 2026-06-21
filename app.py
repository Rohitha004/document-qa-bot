import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
from query import query_rag_pipeline
import base64

st.set_page_config(page_title="Document Q&A Bot", page_icon="📚", layout="wide")

st.title("📚 Document Q&A Bot")
st.markdown("Ask any question from the uploaded documents!")

# Show documents in sidebar
st.sidebar.title("📁 Uploaded Documents")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'''
        <iframe 
            src="data:application/pdf;base64,{base64_pdf}" 
            width="100%" 
            height="600px" 
            type="application/pdf">
        </iframe>
    '''
    st.markdown(pdf_display, unsafe_allow_html=True)

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
            if selected_file.endswith(".pdf"):
                show_pdf(file_path)
            elif selected_file.endswith(".docx"):
                st.info("DOCX preview not supported. Please download to view.")
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Document",
                        data=f,
                        file_name=selected_file
                    )
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