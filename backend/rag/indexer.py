# indexer.py  (FAISS + sentence-transformers)
import os, json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from tqdm import tqdm
import torch
from pathlib import Path
BASE_DIR = Path(__file__).parent.parent # This is backend/
DATA_DIR = BASE_DIR / "data" / "processed"
INDEX_DIR = BASE_DIR / "data" / "indexed_data"
INDEX_DIR.mkdir(exist_ok=True)

EMBED_MODEL = "all-MiniLM-L6-v2"   
EMB_DIM = 384                      # matches all-MiniLM-L6-v2

def load_documents():
    docs = []
    for fn in sorted(DATA_DIR.iterdir()):
        if not fn.name.lower().endswith((".json", ".jsonl", ".ndjson", ".jsonlines")):
            continue
        with open(fn, "r", encoding="utf-8") as f:
            try:
                arr = json.load(f)
            except Exception:
                # if jsonl was saved, try line-by-line
                f.seek(0)
                arr = [json.loads(line) for line in f if line.strip()]
        for item in arr:
            docs.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content"),
                "meta": {k:v for k,v in item.items() if k not in ("content",)}
            })
    return docs

def build_index(batch_size=64):
    docs = load_documents()
    if not docs:
        print("No documents found in", DATA_DIR)
        return
    device = "mps" if (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()) else "cpu"
    print("Using device:", device)

    model = SentenceTransformer(EMBED_MODEL,device=device)
    dim = model.get_sentence_embedding_dimension()
    print("Embedding dim:", dim)

    # prepare arrays
    contents = [d["content"] for d in docs]
    ids = [d["id"] or str(i) for i,d in enumerate(docs)]

    # create FAISS index (cosine via inner product on normalized vectors)
    index = faiss.IndexFlatIP(dim)
    vectors = []

    # batch embed
    for i in tqdm(range(0, len(contents), batch_size), desc="Embedding"):
        batch = contents[i:i+batch_size]
        emb = model.encode(batch, show_progress_bar=False, convert_to_numpy=True)
        # normalize for cosine similarity
        norms = np.linalg.norm(emb, axis=1, keepdims=True)
        emb = emb / (norms + 1e-10)
        vectors.append(emb)
    vectors = np.vstack(vectors).astype("float32")

    # add to index
    index.add(vectors)
    # store metadata mapping (id -> doc)
    meta_path = INDEX_DIR / "meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)

    # save index
    faiss.write_index(index, str(INDEX_DIR / "faiss.index"))
    print("Index saved to", INDEX_DIR)

if __name__ == "__main__":
    build_index()
