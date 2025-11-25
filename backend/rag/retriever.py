import os
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from pymilvus import connections, Collection, utility

# --- CONFIG ---
# Assuming this file is in backend/ directory
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = (BASE_DIR / "data" / "milvus.db").resolve()
print("Using DB:", DB_PATH)
COLLECTION_NAME = "lnmiit_rag"
EMBED_MODEL = "all-MiniLM-L6-v2"

# Load model once to avoid reloading on every request
print("Loading Embedding Model...")
model = SentenceTransformer(EMBED_MODEL)

def connect_milvus():
    """Helper to ensure connection exists"""
    if not connections.has_connection("default"):
        print(f"Connecting to Milvus: {DB_PATH}")
        connections.connect("default", uri=str(DB_PATH))

def search(query, top_k=5):
    connect_milvus()
    
    if not utility.has_collection(COLLECTION_NAME):
        print(f"Collection {COLLECTION_NAME} not found.")
        return []

    collection = Collection(COLLECTION_NAME)
    collection.load()  # Load into memory

    # 1. Embed Query
    q_emb = model.encode([query], convert_to_numpy=True)
    
    # 2. Normalize (for Inner Product/Cosine match)
    norms = np.linalg.norm(q_emb, axis=1, keepdims=True)
    q_emb = q_emb / (norms + 1e-10)

    # 3. Search Milvus
    search_params = {"metric_type": "IP", "params": {"level": 2}}
    results = collection.search(
        data=q_emb,
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=["content", "url", "title"]
    )

    # 4. Format results for the Generator
    formatted_results = []
    for hits in results:
        for hit in hits:
            formatted_results.append({
                "score": float(hit.score),
                "id": hit.id,
                "title": hit.entity.get("title"),
                "url": hit.entity.get("url"),
                "content": hit.entity.get("content")
            })
            
    return formatted_results

if __name__ == "__main__":
    # Test block
    import sys
    q = " ".join(sys.argv[1:]) or "hostel facilities"
    print(f"Searching for: {q}")
    res = search(q, top_k=3)
    for r in res:
        print(f"[{r['score']:.3f}] {r['title']}")
        print(f"{r['content'][:100]}...\n")