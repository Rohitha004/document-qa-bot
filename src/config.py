import os
from dotenv import load_dotenv

load_dotenv()

# API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "db")

# Chunking settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval settings
TOP_K = 3

# Model names
EMBEDDING_MODEL = "gemini-embedding-001"
GENERATION_MODEL = "models/gemini-2.5-flash-lite"

# ChromaDB collection name
COLLECTION_NAME = "document_knowledge_base"