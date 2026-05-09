import os
import time
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Configuration
# os.environ["HF_HUB_OFFLINE"] = "1"
# Use the official model ID for automatic download
MODEL_ID = "BAAI/bge-small-en-v1.5"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorEngine:
    """
    Professional Vector Engine using ChromaDB and BGE-v1.5 for Retrieval.
    """
    def __init__(self, db_path: str = "rag_storage/chroma_db"):
        self.db_path = db_path
        
        # Initialize Embedding Model
        logger.info(f"Loading embedding model: {MODEL_ID}")
        self.model = SentenceTransformer(MODEL_ID)
        
        # Initialize ChromaDB (Persistent)
        self.client = chromadb.PersistentClient(path=self.db_path)
        
    def populate_from_json(self, chunks_json_path: str, collection_name: str):
        with open(chunks_json_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"} # L2 Normalization handled by cosine space
        )

        documents = []
        metadatas = []
        ids = []
        
        logger.info(f"Preparing {len(chunks)} chunks for vectorization...")
        
        for chunk in chunks:
            # PROFESSIONAL STRATEGY: Augmented Context
            # We "bake" the headers into the text so the vector understands the context.
            metadata = chunk.get("metadata", {})
            headings = metadata.get("headings")
            if not isinstance(headings, (list, tuple)):
                headings = [str(headings)] if headings else []
            
            labels = metadata.get("labels")
            if not isinstance(labels, (list, tuple)):
                labels = [str(labels)] if labels else []
            
            # Ensure all items are strings for joining
            safe_headings = [str(h) for h in headings if h is not None]
            safe_labels = [str(l) for l in labels if l is not None]
            
            header_context = " > ".join(safe_headings)
            labels_context = ", ".join(safe_labels)
            augmented_text = f"CONTEXT: [{header_context}] TYPE: [{labels_context}] CONTENT: {chunk.get('text', '')}"
            
            documents.append(augmented_text)
            
            # Prepare metadata (ChromaDB requires flat dicts)
            flat_meta = {
                "source": metadata.get("source", "unknown"),
                "doc_title": metadata.get("doc_title", "unknown"),
                "headings": json.dumps(safe_headings),
                "page_numbers": json.dumps(metadata.get("page_numbers", [])),
                "labels": json.dumps(safe_labels),
                "chunk_id": chunk.get("id", "unknown")
            }
            metadatas.append(flat_meta)
            ids.append(chunk.get("id", str(time.time())))

        # Batch add to Chroma (Chroma handles the model call if we passed an embedding function,
        # but here we generate them manually for maximum professional control).
        logger.info("Generating embeddings (Batching enabled)...")
        # Optimization: Lower batch size to reduce peak CPU load/heat
        embeddings = self.model.encode(documents, show_progress_bar=True, batch_size=8).tolist()
        
        logger.info("Updating Vector Database...")
        collection.add(
            embeddings=embeddings,
            documents=documents, # We store the augmented text
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Vector Store updated successfully with collection: {collection_name}")

    def query(self, collection_name: str, query_text: str, n_results: int = 5):
        collection = self.client.get_collection(name=collection_name)
        
        # Encode the query
        query_embedding = self.model.encode([query_text]).tolist()
        
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        return results

if __name__ == "__main__":
    # Example usage (assuming ingestion was run and model files are present)
    # Change collection name based on your PDF
    v_engine = VectorEngine()
    
    # Example Query
    # results = v_engine.query("ResNet_Paper", "What is identity mapping?")
    # print(results)
