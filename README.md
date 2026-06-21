**# Document Q\&A Bot with RAG**



A Python-based Retrieval-Augmented Generation (RAG) system that answers questions from custom documents using Google Gemini AI.



**## Tech Stack**

\- Python 3.11+

\- Google Gemini AI (gemini-2.5-flash-lite)

\- ChromaDB (Vector Database)

\- PyPDF \& Python-DOCX (Document Processing)

\- Streamlit (UI)



**## Project Structure**

document-qa-bot/

├── .env

├── requirements.txt

├── data/

├── db/

└── src/

&#x20;   ├── config.py

&#x20;   ├── ingest.py

&#x20;   ├── query.py

&#x20;   └── main.py



**## Setup Instructions**

1\. Clone the repository

2\. Create virtual environment: python -m venv venv

3\. Activate: venv\\Scripts\\activate

4\. Install dependencies: pip install -r requirements.txt

5\. Add your Gemini API key to .env file: GEMINI\_API\_KEY=your\_key

6\. Add documents to data/ folder



**## How to Run**



Step 1 - Index documents:

python src/ingest.py



Step 2 - Start the bot:

python src/main.py



**## How it Works**

1\. Documents are loaded and split into chunks

2\. Chunks are embedded using Google Gemini embeddings

3\. Embeddings are stored in ChromaDB

4\. User query is embedded and matched against stored chunks

5\. Relevant chunks are sent to Gemini to generate a grounded answer



**## Example Questions**

\- What is machine learning?

\- What are the types of AI?

\- What is deep learning?

