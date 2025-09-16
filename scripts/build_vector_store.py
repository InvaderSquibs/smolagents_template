#!/usr/bin/env python3
"""
Build vector store for RAG knowledge base.
Embeds the knowledge.json data and stores it in Chroma for retrieval.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# Configuration
DATA_PATH = Path("data/knowledge.json")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

def chunk_text(text: str, max_chars: int = 400):
    """
    Simple text chunking for longer texts.
    For our knowledge base, most entries are already short enough.
    """
    if len(text) <= max_chars:
        return [text]
    
    # Simple greedy splitter on sentences/periods
    parts, cur = [], []
    chars = 0
    for token in text.split(". "):
        token = token.strip()
        if not token:
            continue
        if chars + len(token) + 2 > max_chars and cur:
            parts.append(". ".join(cur) + ".")
            cur, chars = [token], len(token)
        else:
            cur.append(token)
            chars += len(token) + 2
    
    if cur:
        last = ". ".join(cur)
        if not last.endswith("."):
            last += "."
        parts.append(last)
    
    return parts

def main():
    """Build the vector store from knowledge.json"""
    print(f"🔧 Building vector store...")
    print(f"📁 Data path: {DATA_PATH}")
    print(f"🗄️  Chroma directory: {CHROMA_DIR}")
    print(f"🧠 Embedding model: {EMBEDDING_MODEL_NAME}")
    
    # Check if data file exists
    if not DATA_PATH.exists():
        print(f"❌ Error: Missing {DATA_PATH}")
        return
    
    # Load knowledge data
    print(f"📖 Loading knowledge data...")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)
    
    print(f"📊 Found {len(records)} knowledge entries")
    
    # Initialize embedding model
    print(f"🧠 Loading embedding model...")
    embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    
    # Initialize Chroma (persist to disk)
    print(f"🗄️  Initializing Chroma database...")
    # Ensure the directory exists
    Path(CHROMA_DIR).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    
    # Recreate collection for a clean build
    collection_name = "knowledge_base"
    if collection_name in [c.name for c in client.list_collections()]:
        print(f"🗑️  Removing existing collection: {collection_name}")
        client.delete_collection(collection_name)
    
    collection = client.create_collection(name=collection_name)
    print(f"✅ Created collection: {collection_name}")
    
    # Prepare documents and embeddings
    print(f"🔄 Processing documents...")
    doc_ids, texts, metadatas, embeddings = [], [], [], []
    
    for rec in records:
        base_id = rec.get("id") or f"doc_{len(doc_ids)}"
        chunks = chunk_text(rec["text"])
        
        for idx, chunk in enumerate(chunks):
            cid = f"{base_id}::chunk_{idx}"
            doc_ids.append(cid)
            texts.append(chunk)
            metadatas.append({
                "title": rec.get("title", ""), 
                "source_id": base_id, 
                "chunk_id": idx
            })
    
    print(f"📝 Generated {len(texts)} text chunks")
    
    # Compute embeddings
    print(f"🧮 Computing embeddings...")
    vectors = embedder.encode(texts, convert_to_numpy=True)
    print(f"✅ Generated {len(vectors)} embeddings (dimension: {vectors.shape[1]})")
    
    # Upsert to Chroma
    print(f"💾 Storing in Chroma...")
    collection.add(
        ids=doc_ids, 
        documents=texts, 
        metadatas=metadatas, 
        embeddings=vectors
    )
    
    # Persist to disk (Chroma auto-persists when using persist_directory)
    # client.persist()  # Not needed in newer Chroma versions
    
    print(f"🎉 Successfully indexed {len(texts)} chunks into Chroma at {CHROMA_DIR}")
    print(f"📊 Collection '{collection_name}' is ready for retrieval!")

if __name__ == "__main__":
    main()
