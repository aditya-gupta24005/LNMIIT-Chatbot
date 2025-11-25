# indexer.py  (Milvus-Lite + sentence-transformers)

import os, json, hashlib
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm
import torch

from pymilvus import (
    connections, Collection, FieldSchema, CollectionSchema,
    DataType, utility
)

BASE_DIR = Path(__file__).resolve().parent.parent          # backend/
DATA_DIR = BASE_DIR / "data" / "processed"                 # processed docs
INDEX_DIR = BASE_DIR / "data" / "indexed_data"             # metadata dumps

# Ensure folders exist
INDEX_DIR.mkdir(exist_ok=True)
(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)


EMBED_MODEL = "all-MiniLM-L6-v2"
EMB_DIM = 384
COLLECTION_NAME = "lnmiit_rag"

def load_documents():
    docs = []
    if not DATA_DIR.exists():
        print(f"Processed directory does not exist: {DATA_DIR}")
        return []

    for fn in sorted(DATA_DIR.iterdir()):
        if not fn.name.lower().endswith((".json", ".jsonl", ".ndjson", ".jsonlines")):
            continue

        with open(fn, "r", encoding="utf-8") as f:
            try:
                arr = json.load(f)
            except Exception:
                f.seek(0)
                arr = [json.loads(line) for line in f if line.strip()]

        docs.extend(arr)

    print(f"Loaded {len(docs)} processed chunks.")
    return docs

def connect_milvus():
    db_path = BASE_DIR / "data" / "milvus.db"
    print(f"Connecting to Milvus Lite at: {db_path}")
    connections.connect("default", uri=str(db_path))


def create_collection(dim=EMB_DIM):
    if utility.has_collection(COLLECTION_NAME):
        print(f"Dropping existing collection: {COLLECTION_NAME}")
        Collection(COLLECTION_NAME).drop()

    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=200, is_primary=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=5000),
        FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
    ]

    schema = CollectionSchema(fields, description="LNMIIT RAG collection")
    collection = Collection(COLLECTION_NAME, schema)

    index_params = {
        "index_type": "AUTOINDEX",
        "metric_type": "IP",
        "params": {},
    }

    collection.create_index("embedding", index_params)
    return collection


def safe_id(raw_id: str, index: int) -> str:
    raw = str(raw_id) if raw_id else str(index)
    h = hashlib.sha1(raw.encode()).hexdigest()
    return h[:40]          # 40 characters, guaranteed < 200


def build_index(batch_size=64):
    connect_milvus()

    docs = load_documents()
    if not docs:
        print("No processed documents found.")
        return

    # Device
    device = "mps" if (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()) else "cpu"
    print("Using device:", device)

    model = SentenceTransformer(EMBED_MODEL, device=device)
    dim = model.get_sentence_embedding_dimension()
    print("Embedding dim:", dim)

    collection = create_collection(dim)

    # Extract fields
    contents = [d["content"] for d in docs]
    ids = [safe_id(d.get("id"), i) for i, d in enumerate(docs)]
    urls = [d.get("url", "") for d in docs]
    titles = [d.get("title", "") for d in docs]

    # Embeddings
    all_embeddings = []

    for i in tqdm(range(0, len(contents), batch_size), desc="Embedding"):
        batch = contents[i:i+batch_size]
        emb = model.encode(batch, show_progress_bar=False, convert_to_numpy=True)

        norms = np.linalg.norm(emb, axis=1, keepdims=True)
        emb = emb / (norms + 1e-10)

        all_embeddings.append(emb)

    vectors = np.vstack(all_embeddings).astype("float32")

    # Insert into Milvus
    print("Inserting vectors into Milvus...")
    collection.insert([
        ids,
        vectors.tolist(),
        contents,
        urls,
        titles,
    ])

    collection.flush()
    print("Milvus index built and data inserted successfully.")

    # Save metadata
    meta_path = INDEX_DIR / "meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_index()
