import streamlit as st
import os
import qdrant_client
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.postprocessor import SentenceTransformerRerank
from ingest import setup_settings
from config import QDRANT_PATH, COLLECTION_NAME, MODEL_PROVIDER, RERANK_MODEL_NAME

# --- Streamlit UI Setup ---
st.set_page_config(
    page_title="SOTA MultiModal RAG", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ RAG Configuration")
    st.info(f"**Main Model:** {MODEL_PROVIDER}")
    st.info(f"**Reranker:** {RERANK_MODEL_NAME.split('/')[-1]}")
    st.write("---")
    st.markdown("""
    ### 🛡️ SOTA Features:
    - **Cross-Encoder Reranking:** Filters top 10 results down to 5.
    - **Multi-Vector Retrieval:** Search image descriptions.
    - **Local-First:** Ollama/Llama3.2 for reasoning.
    """)
    
    if st.button("🔄 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

st.title("🤖 MultiModal RAG Assistant (SOTA Edition)")
st.markdown(f"**Current State:** 🚀 *Reranker Enabled* | *Provider:* {MODEL_PROVIDER}")

def initialize_engine():
    """Initializes the query engine with Qdrant + SOTA Reranking."""
    setup_settings()
    
    if not os.path.exists(QDRANT_PATH):
        st.error(f"No database found at {QDRANT_PATH}. Run `python ingest.py` first.")
        st.stop()
        
    client = qdrant_client.QdrantClient(path=QDRANT_PATH)
    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)
    
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    
    # SETUP SOTA RERANKER
    # We retrieve 10 nodes (fast) then let the Reranker pick the top 5 (accurate)
    rerank_postprocessor = SentenceTransformerRerank(
        model=RERANK_MODEL_NAME, 
        top_n=5
    )
    
    return index.as_query_engine(
        similarity_top_k=10, 
        node_postprocessors=[rerank_postprocessor]
    )

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "images" in message:
            cols = st.columns(2)
            for idx, img in enumerate(message["images"]):
                with cols[idx % 2]:
                    st.image(img["path"], caption=img["caption"], use_container_width=True)

# Lazy Load Query Engine
if "query_engine" not in st.session_state:
    with st.spinner(f"Loading {MODEL_PROVIDER} & BGE Reranker..."):
        st.session_state.query_engine = initialize_engine()

# Chat Input
if prompt := st.chat_input("Ask about technical docs or diagrams..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("🔍 Retrieving and Reranking Context..."):
            try:
                response = st.session_state.query_engine.query(prompt)
                
                final_text = response.response
                source_nodes = response.source_nodes
                
                # Extract unique images from reranked results
                retrieved_images = []
                seen_paths = set()
                for node in source_nodes:
                    if "image_path" in node.metadata:
                        img_path = node.metadata["image_path"]
                        if os.path.exists(img_path) and img_path not in seen_paths:
                            retrieved_images.append({
                                "path": img_path,
                                "caption": f"Retrieved (Score: {node.score:.2f}) from Page {node.metadata.get('page', '?')}"
                            })
                            seen_paths.add(img_path)

                st.markdown(final_text)
                
                if retrieved_images:
                    st.write("---")
                    st.markdown("### 🖼️ Relevant Diagrams (Reranked)")
                    cols = st.columns(2)
                    for idx, img in enumerate(retrieved_images):
                        with cols[idx % 2]:
                            st.image(img["path"], caption=img["caption"], use_container_width=True)

                with st.expander("🔍 View Reranked Context & Confidence"):
                    for node in source_nodes:
                        st.write(f"**Type:** `{node.metadata.get('type', 'Unknown')}` | **Rerank Score:** `{node.score:.4f}`")
                        if "image_path" in node.metadata:
                            st.info(f"🖼️ **Diagram:** {node.text}")
                        else:
                            st.text(node.text[:600] + "...")
                        st.divider()

                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": final_text,
                    "images": retrieved_images
                })

            except Exception as e:
                st.error(f"Error: {e}")
