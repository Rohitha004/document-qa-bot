import os
import chromadb
from google import genai
from config import GEMINI_API_KEY, DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL, GENERATION_MODEL, TOP_K

genai_client = genai.Client(api_key=GEMINI_API_KEY)

def query_rag_pipeline(user_query: str, db_path: str = DB_PATH, k: int = TOP_K) -> dict:
    client = chromadb.PersistentClient(path=db_path)

    collection = client.get_collection(name=COLLECTION_NAME)

    # Embed the user query
    result = genai_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=user_query
    )
    query_embedding = result.embeddings[0].values

    # Search for top k relevant chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    # Format retrieved chunks with citations
    context_blocks = []
    citations = []

    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        source_name = meta['source']
        page_num = meta['page']
        citation_str = f"Source: {source_name}, Page: {page_num}"
        context_blocks.append(f"[{citation_str}]\nContext: {doc}")
        citations.append(citation_str)

    context_payload = "\n\n---\n\n".join(context_blocks)

    # Grounding system prompt
    prompt = (
        "You are a helpful and accurate document Q&A assistant. "
        "You will be given context extracted from documents. "
        "Answer the user's question based on the context provided. "
        "Always cite the source filename and page number next to each fact. "
        "Give a detailed and helpful answer using the context. "
        "Only say you cannot find the answer if the context is truly unrelated.\n\n"
        f"CONTEXT INFORMATION:\n{context_payload}\n\n"
        f"USER QUESTION: {user_query}\n\n"
        f"ANSWER:"
    )

    # Call Gemini to generate answer
    response = genai_client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt
    )

    return {
        "answer": response.text,
        "citations": citations,
        "raw_context": results['documents'][0]
    }