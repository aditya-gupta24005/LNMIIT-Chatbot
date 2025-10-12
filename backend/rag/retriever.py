# retriever.py
import faiss, json, numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

INDEX_DIR = Path("/Users/adityagupta/Developer/LNMIIT-Chatbot/backend/data/indexed_data")
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index(str(INDEX_DIR / "faiss.index"))
with open(INDEX_DIR / "meta.json", "r", encoding="utf-8") as f:
    docs = json.load(f)

def search(query, top_k=5):
    q_emb = model.encode([query], convert_to_numpy=True)
    q_emb = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True)+1e-10)
    scores, idxs = index.search(q_emb.astype("float32"), top_k)
    results = []
    for score, idx in zip(scores[0], idxs[0]):
        d = docs[idx]
        results.append({"score": float(score), "id": d.get("id"), "title": d.get("title"), "url": d.get("url"), "content": d.get("content")})
    return results

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "anti ragging helpline"
    res = search(q, top_k=5)
    for r in res:
        print(f"[{r['score']:.3f}] {r['title']} - {r['url']}")
        print(r['content'][:400].replace("\n"," ") + "...\n")
