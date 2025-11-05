# processor.py
import os
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime, timezone

from pathlib import Path
BASE_DIR = Path(__file__).parent.parent # This is backend/
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHUNK_CHAR_SIZE = 2000
MIN_CHUNK_CHAR = 200

def ensure_dirs():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

def clean_html_or_text(raw_text: str) -> str:
    if not raw_text:
        return ""
    if "<" in raw_text and ">" in raw_text and (raw_text.lstrip().startswith("<") or "<p" in raw_text or "<div" in raw_text):
        soup = BeautifulSoup(raw_text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
    else:
        text = raw_text
    text = re.sub(r"\s+", " ", text).strip()
    return text

def chunk_text(content: str, size: int = CHUNK_CHAR_SIZE, min_size: int = MIN_CHUNK_CHAR):
    if not content:
        return []
    if len(content) <= size:
        return [content]
    sentences = re.split(r'(?<=[\.\?\!])\s+', content)
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) + 1 <= size:
            current = (current + " " + s).strip()
        else:
            if current:
                chunks.append(current)
            current = s
    if current:
        chunks.append(current)
    if len(chunks) > 1 and len(chunks[-1]) < min_size:
        chunks[-2] = chunks[-2] + " " + chunks[-1]
        chunks = chunks[:-1]
    return chunks

def normalize_item(item: dict):
    _id = item.get("id") or item.get("url") or None
    raw_text = item.get("text") or item.get("content") or item.get("body") or ""
    meta = item.get("meta", {}) if isinstance(item.get("meta", {}), dict) else {}
    url = meta.get("url") or item.get("url") or ""
    title = meta.get("title") or item.get("title") or ""
    fetched_at = meta.get("fetched_at") or meta.get("fetched") or None
    chunk_index = meta.get("chunk_index")
    source_type = meta.get("type") or item.get("type") or ""

    cleaned = clean_html_or_text(raw_text)

    processed_entries = []
    chunks = chunk_text(cleaned)
    for i, chunk in enumerate(chunks):
        proc = {
            "id": f"{_id}::chunk_{i}" if _id else None,
            "source_id": _id,
            "url": url,
            "title": title,
            "content": chunk,
            "chunk_index": chunk_index if chunk_index is not None else i,
            "fetched_at": fetched_at,
            "source_type": source_type,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "content_len": len(chunk),
        }
        processed_entries.append(proc)
    return processed_entries

def load_json_or_jsonl(path: str):
    """
    Load .json or .jsonl files and return a list of items (dicts).
    """
    items = []
    if path.endswith(".jsonl") or path.endswith(".jsonlines") or path.endswith(".ndjson"):
        with open(path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    items.append(obj)
                except json.JSONDecodeError as e:
                    print(f"  WARNING: JSON decode error in {os.path.basename(path)} line {i}: {e}")
                    # skip bad line
    else:
        with open(path, "r", encoding="utf-8") as f:
            try:
                raw = json.load(f)
            except json.JSONDecodeError as e:
                print(f"ERROR reading {path}: {e}")
                return []
            if isinstance(raw, list):
                items = raw
            elif isinstance(raw, dict):
                if "chunks" in raw and isinstance(raw["chunks"], list):
                    items = raw["chunks"]
                elif "items" in raw and isinstance(raw["items"], list):
                    items = raw["items"]
                else:
                    items = [raw]
            else:
                print(f"Unknown JSON structure in {path}.")
                return []
    return items

def process_file(path_in: str, path_out: str):
    items = load_json_or_jsonl(path_in)
    if not items:
        return 0

    all_processed = []
    seen_texts = set()
    for item in items:
        processed_entries = normalize_item(item)
        for p in processed_entries:
            h = p["content"][:200]
            if h in seen_texts:
                continue
            seen_texts.add(h)
            all_processed.append(p)

    with open(path_out, "w", encoding="utf-8") as out_f:
        json.dump(all_processed, out_f, ensure_ascii=False, indent=2)

    return len(all_processed)

def process_all():
    ensure_dirs()
    total = 0
    for fn in sorted(os.listdir(RAW_DIR)):
        if not (fn.endswith(".json") or fn.endswith(".jsonl") or fn.endswith(".ndjson") or fn.endswith(".jsonlines")):
            continue
        in_path = os.path.join(RAW_DIR, fn)
        out_path = os.path.join(PROCESSED_DIR, fn)
        try:
            count = process_file(in_path, out_path)
            total += count
            print(f"Processed {fn} -> {out_path} ({count} chunks)")
        except Exception as e:
            print(f"Failed processing {fn}: {e}")
    print(f"Total processed chunks: {total}")

if __name__ == "__main__":
    process_all()
