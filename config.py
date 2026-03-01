import os
from dotenv import load_dotenv

load_dotenv()

# --- PROVIDER SELECTION ---
# Options: "OLLAMA", "GEMINI"
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "OLLAMA")

# --- OLLAMA SETTINGS ---
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TEXT_MODEL = "llama3.2:3b"
OLLAMA_VISION_MODEL = "llava:7b"

# --- GEMINI SETTINGS ---
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"

# --- VECTOR STORE SETTINGS ---
QDRANT_PATH = "./qdrant_data"
COLLECTION_NAME = "multi_modal_docs"

# --- EMBEDDING & RERANKING ---
# We keep these local (BGE) to ensure stability during dev
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"
RERANK_MODEL_NAME = "BAAI/bge-reranker-base"

# --- DIRECTORIES ---
EXTRACTED_IMAGES_DIR = "extracted_images"
SCRAPED_CONTENT_DIR = "scraped_content"
DATA_DIR = "data"
