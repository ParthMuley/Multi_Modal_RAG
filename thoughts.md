# MultiModal RAG: Development Thoughts & Planning

This document tracks the architectural decisions, features, and implementation steps for the MultiModal RAG system.

## Project Vision
A production-grade RAG system capable of retrieving and reasoning across text and images from technical documentation (e.g., AWS/Azure architecture guides).

---

## Phase 1: MVP (Minimal Viable Product) - COMPLETED
**Goal:** Build a functional text-based RAG pipeline using cloud LLMs and local embeddings to minimize cost and avoid rate limits.

### Features Implemented
- [x] **Project Scaffolding:** Python virtual environment, `requirements.txt`.
- [x] **Local Vector Store:** Qdrant (Local/In-memory mode) for fast, zero-cost storage.
- [x] **Local Embeddings:** Switched from Google API to `BAAI/bge-small-en-v1.5` to bypass rate limits (429 errors) during heavy ingestion.
- [x] **Cloud LLM Reasoning:** Gemini 1.5 Flash for high-quality, long-context answers.
- [x] **Ingestion Pipeline:** Automated PDF parsing and chunking (153 chunks for the sample AWS PDF).
- [x] **Chat UI:** Streamlit interface with chat history and "Source Context" expanders.

### Steps Taken
1.  **Step 1:** Initialized environment and installed LlamaIndex + Qdrant.
2.  **Step 2:** Attempted Google Cloud Embeddings; hit rate limits.
3.  **Step 3:** Implemented `ingest.py` with local HuggingFace embeddings.
4.  **Step 4:** Built `app.py` Streamlit interface.

---

## Phase 2: Adding the "MultiModal" (Vision) - COMPLETED (Core)
**Goal:** Extract architecture diagrams from PDFs and allow the model to "see" them when answering.

### Features Implemented
- [x] **Image Extraction:** Using `pdfplumber` for high-resolution diagram extraction.
- [x] **SOTA Multi-Vector Ingestion:** 
    - Descriptions generated via **LLava-v1.5 (7B)**.
    - Captions stored as searchable nodes with pointers to raw images.
- [x] **Vision Caching:** Persistent `caption_cache.json` to prevent re-captioning expensive images.

---

## Phase 2.2: Incremental Ingestion & Persistence
**Goal:** Optimize the pipeline to handle large document sets without full re-processing.

### Features Implemented
- [x] **MD5 Manifest System:** Track `ingestion_manifest.json` with file hashes.
- [x] **Skip Logic:** Automatically detect unchanged PDFs, images, and web content.
- [x] **Persistent Vector DB:** Stopped wiping the `qdrant_data` folder; the system now appends and updates.

---

## Phase 2.3: SOTA Retrieval Accuracy
**Goal:** Move beyond basic vector search for enterprise-grade precision.

### Features Implemented
- [x] **Two-Stage Retrieval:** Retrieve top 10 (Vector) -> Rerank to top 5 (Cross-Encoder).
- [x] **BGE Reranker:** Integrated `BAAI/bge-reranker-base` as a local post-processor.

---

## Phase 2.5: Recursive Link Ingestion - COMPLETED
**Goal:** Expand the knowledge base by crawling external links found within the PDF documents.

### Features Implemented
- [x] **Recursive Crawler:** Crawls depth=1 for documentation domains (AWS/Azure).
- [x] **Trafilatura Integration:** High-quality text extraction that removes ads, headers, and navigation noise.
- [x] **Unified Indexing:** Web content is treated as first-class context in the RAG pipeline.

---

## Hallucination Guardrails & Truthfulness
**Goal:** Ensure the system never "makes up" technical facts.

### Best Practices to Implement
- [ ] **Negative Constraints:** Update system prompts to force "I don't know" responses when context is missing.
- [ ] **Self-Correction Loop:** Implement a "Reflector" step where the LLM critiques its own answer against the source text.
- [ ] **RAGAS Evaluation:** Implement automated scoring for Faithfulness, Relevancy, and Precision.
- [ ] **Citation UI:** Make the UI "clickable"—clicking a sentence in the AI's answer should highlight the source chunk it came from.

---

## Phase 3: Production Readiness
**Goal:** Move from local scripts to a scalable architecture.

### Planned Features
- [ ] **Managed Vector DB:** Move from local Qdrant to Qdrant Cloud or Milvus.
- [ ] **Asynchronous Ingestion:** Use a task queue (Celery/Redis) for PDF processing.
- [ ] **Semantic Caching:** Store common queries in Redis to save LLM costs.
- [ ] **Evaluation:** Implement RAGAS or a "Vibe Check" framework to measure accuracy.

---

## Technical Trade-offs Made
1.  **Local vs. Cloud Embeddings:** Chose local `BGE` to avoid the 429 "Resource Exhausted" errors on the Gemini Free Tier. This makes the system more robust for large document ingestion.
2.  **Gemini 2.5 Flash:** Using Gemini 2.5 Flash for both LLM and Vision tasks as it's the stable high-quota model for the Feb 2026 environment.
3.  **Robust Ingestion:** Implemented a 5-second delay and retry logic (3 attempts with 15s wait) during image captioning to gracefully handle the 20 RPM rate limit on the Gemini Free Tier.
