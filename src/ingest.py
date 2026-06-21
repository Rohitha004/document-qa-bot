import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pypdf import PdfReader
from docx import Document
from tqdm import tqdm
import chromadb
from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction
from config import GEMINI_API_KEY, DATA_DIR, DB_PATH, CHUNK_SIZE, CHUNK_OVERLAP, COLLECTION_NAME, EMBEDDING_MODEL


# Step 1: Extract text from PDF
def extract_pdf_pages(file_path: str) -> list:
    extracted_data = []
    file_name = os.path.basename(file_path)
    try:
        reader = PdfReader(file_path)
        for index, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                clean_text = " ".join(text.split())
                extracted_data.append({
                    "text": clean_text,
                    "metadata": {"source": file_name, "page": index + 1}
                })
    except Exception as e:
        print(f"Error reading PDF {file_name}: {e}")
    return extracted_data


# Step 2: Extract text from DOCX
def extract_docx_pages(file_path: str) -> list:
    extracted_data = []
    file_name = os.path.basename(file_path)
    try:
        doc = Document(file_path)
        full_text = " ".join([para.text for para in doc.paragraphs if para.text.strip()])
        extracted_data.append({
            "text": full_text,
            "metadata": {"source": file_name, "page": 1}
        })
    except Exception as e:
        print(f"Error reading DOCX {file_name}: {e}")
    return extracted_data


# Step 3: Chunk the extracted text
def chunk_extracted_pages(pages: list, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> list:
    chunks = []
    for page in pages:
        text = page["text"]
        metadata = page["metadata"]
        start = 0
        text_length = len(text)
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": metadata["source"],
                    "page": metadata["page"],
                    "chunk_range": f"{start}-{end}"
                }
            })
            start += (chunk_size - chunk_overlap)
    return chunks


# Step 4: Save chunks to ChromaDB
def save_to_vector_db(chunks: list, db_path: str = DB_PATH):
    client = chromadb.PersistentClient(path=db_path)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    from google import genai
    from google.genai import types
    genai_client = genai.Client(
   	 api_key=GEMINI_API_KEY,
   	 http_options={"api_version": "v1"}
    )
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    ids = [f"id_{i}" for i in range(len(chunks))]

    # Generate embeddings in batches
    embeddings = []
    for doc in tqdm(documents, desc="Generating embeddings"):
        result = genai_client.models.embed_content(
            model="gemini-embedding-001",
            contents=doc
        )
        embeddings.append(result.embeddings[0].values)

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )
    print(f"Successfully indexed {len(chunks)} chunks in the vector database.")

# Main ingestion pipeline
if __name__ == "__main__":
    all_pages = []
    files = os.listdir(DATA_DIR)

    for file in tqdm(files, desc="Processing documents"):
        file_path = os.path.join(DATA_DIR, file)
        if file.endswith(".pdf"):
            all_pages.extend(extract_pdf_pages(file_path))
        elif file.endswith(".docx"):
            all_pages.extend(extract_docx_pages(file_path))

    print(f"Total pages extracted: {len(all_pages)}")

    chunks = chunk_extracted_pages(all_pages)
    print(f"Total chunks created: {len(chunks)}")

    save_to_vector_db(chunks)