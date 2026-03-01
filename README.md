# MultiModal RAG (SOTA MVP)

A production-grade MultiModal RAG (Retrieval-Augmented Generation) system designed to retrieve and reason across **text, diagrams, and web content**. Optimized for technical documentation (AWS/Azure) with a **Local-First** architecture.

## 🚀 Key Features (SOTA Implementation)

- **🖼️ Multi-Vector Ingestion:** Automatically extracts and captions images from PDFs using **LLava (Ollama)** or **Gemini**.
- **🔍 Two-Stage Retrieval:** 
    1. **Vector Search:** Fast initial retrieval of top 10 candidates.
    2. **BGE Reranker:** Cross-Encoder reranking to pick the top 5 most relevant nodes for extreme precision.
- **💾 Incremental Ingestion:** Uses an **MD5 Manifest System** to skip already-processed files, making updates near-instant.
- **🌐 Recursive Web Ingestion:** Crawls depth=1 documentation links found in PDFs using **Trafilatura** for clean text extraction.
- **🤖 Local-First Architecture:** Supports **Ollama** (Llama 3.2 + LLava) for free, unlimited development without API rate limits.

## 🛠️ Tech Stack

- **LLM / Vision:** Ollama (Local) or Gemini 1.5 Flash (Cloud).
- **Reranker:** `BAAI/bge-reranker-base` (Local).
- **Vector Database:** Qdrant (Local).
- **Orchestration:** LlamaIndex.
- **UI:** Streamlit.

## 📦 Getting Started

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) (for local inference)
- [Qdrant](https://qdrant.tech/)

### 2. Setup
```bash
# Clone the repo
git clone <your-repo-url>
cd multi-modal-rag

# Install dependencies
pip install -r requirements.txt

# Pull local models
ollama pull llama3.2:3b
ollama pull llava:7b
```

### 3. Configuration
Copy `.env.example` to `.env` and set your preferred provider:
```env
MODEL_PROVIDER=OLLAMA # Options: OLLAMA, GEMINI
GOOGLE_API_KEY=your_key_here
```

### 4. Run the Pipeline
```bash
# 1. Scrape recursive links from PDFs
python web_ingest.py

# 2. Ingest PDFs, Images, and Web Content
python ingest.py

# 3. Start the UI
streamlit run app.py
```

## 🧠 Architectural Decisions
- **Caption Caching:** All image descriptions are cached in `caption_cache.json` to avoid re-running expensive vision models.
- **Hybrid Context:** The system blends local technical diagrams with live web content for a unified "Knowledge Assistant" experience.
- **BGE Reranking:** Mandatory for technical docs where simple vector similarity often retrieves the wrong service (e.g., S3 vs S3 Glacier).

---
*Developed as a high-performance RAG MVP.*
