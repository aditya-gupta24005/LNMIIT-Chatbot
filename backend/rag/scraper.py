#!/usr/bin/env python3
"""
Polite site scraper for lnmiit.ac.in (updated)
- Uses hash-based filenames for outputs
- Resumable crawl via visited.json
- Respects robots.txt
- Crawls same-domain links
- Extracts HTML (trafilatura preferred) and PDF text (pypdf)
- Saves chunked JSONL files under backend/data/
"""

import argparse
import hashlib
import json
import os
import re
import time
from collections import deque
from datetime import datetime
from urllib.parse import urljoin, urlparse, urlunparse
import certifi
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from pypdf import PdfReader
from tqdm import tqdm
from urllib import robotparser
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
try:
    import trafilatura
    _HAS_TRAFILATURA = True
except Exception:
    _HAS_TRAFILATURA = False

# ============ Config ===============
USER_AGENT = "lnmiit-ask-scraper/1.0 (+https://lnmiit.ac.in/)"
DEFAULT_DELAY = 1.0  # seconds between requests (polite)
CHUNK_SIZE_CHARS = 2000
CHUNK_OVERLAP = 200
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")  # backend/data
PDF_DIR = os.path.join(OUTPUT_DIR, "pdfs")
RAW_DIR = os.path.join(OUTPUT_DIR, "raw")
VISITED_PATH = os.path.join(OUTPUT_DIR, "visited.json")
ALLOWED_SCHEMES = ("http", "https")
# ===================================

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})
# ensure requests uses certifi CA bundle (fixes macOS/pyenv SSL issues)
session.verify = certifi.where()

# also set SSL_CERT_FILE for any underlying ssl code in this process
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

def normalize_url_for_dedupe(url: str) -> str:
    """
    Normalize URL to scheme://netloc/path  (drops query, params, fragment)
    Good simple dedupe for most sites.
    """
    p = urlparse(url)
    normalized = urlunparse((p.scheme, p.netloc, p.path or "/", "", "", ""))
    return normalized.rstrip("/")


def url_hash(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()


def is_same_domain(seed_netloc, url):
    try:
        return urlparse(url).netloc.endswith(seed_netloc)
    except Exception:
        return False


def sanitize_url(url):
    p = urlparse(url)
    if not p.scheme:
        url = "http://" + url
        p = urlparse(url)
    # remove fragment for canonicalization
    return p._replace(fragment="").geturl()


def get_robots_parser(seed_url):
    parsed = urlparse(seed_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
    except Exception:
        rp = None
    return rp


def allowed_by_robots(rp, url):
    if rp is None:
        return True
    return rp.can_fetch(USER_AGENT, url)


# Change this function in your script
def fetch_url(url, timeout=15):
    try:
        # Add verify=False to this call
        r = session.get(url, timeout=timeout, verify=False) 
        r.raise_for_status()
        
        # Requests will show a warning when verify=False, you can disable it
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return r
    except Exception as e:
        logging.warning(f"[fetch] Error fetching {url}: {e}")
        return None


def extract_text_from_html(html, url):
    if _HAS_TRAFILATURA:
        try:
            text = trafilatura.extract(html, url=url)
            if text and text.strip():
                return text.strip()
        except Exception:
            pass

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
        tag.decompose()

    parts = []
    for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        text = el.get_text(separator=" ", strip=True)
        if text:
            parts.append(text)
    return "\n\n".join(parts).strip()


def find_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("mailto:") or href.startswith("tel:"):
            continue
        joined = urljoin(base_url, href)
        p = urlparse(joined)
        if p.scheme not in ALLOWED_SCHEMES:
            continue
        joined = p._replace(fragment="").geturl()
        links.add(joined)
    return links


def is_pdf_link(url):
    return url.lower().split("?")[0].endswith(".pdf")


def download_pdf(url, out_dir=PDF_DIR):
    os.makedirs(out_dir, exist_ok=True)
    safe_name = url_hash(url) + ".pdf"
    local_name = os.path.join(out_dir, safe_name)
    if os.path.exists(local_name):
        return local_name
    r = fetch_url(url)
    if r is None:
        return None
    try:
        with open(local_name, "wb") as f:
            f.write(r.content)
        return local_name
    except Exception as e:
        logging.warning(f"[pdf] Failed to save {url}: {e}")
        return None


def extract_text_from_pdf(local_pdf_path):
    try:
        reader = PdfReader(local_pdf_path)
        texts = []
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                continue
        return "\n\n".join(texts).strip()
    except Exception as e:
        logging.warning(f"[pdf] extraction failed for {local_pdf_path}: {e}")
        return ""


def chunk_text(text, chunk_size=CHUNK_SIZE_CHARS, overlap=CHUNK_OVERLAP):
    if not text:
        return []
    text = text.replace("\r\n", "\n").strip()
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


def write_chunks_jsonl(chunks, metadata):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Use SHA1 hash of URL as base filename
    url = metadata.get("url", "")
    fname_base = url_hash(url)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = os.path.join(RAW_DIR, f"{fname_base}_{ts}.jsonl")
    with open(filename, "w", encoding="utf-8") as fh:
        for i, chunk in enumerate(chunks):
            record = {
                "id": f"{metadata.get('url','')}_chunk_{i}",
                "text": chunk,
                "meta": {
                    **metadata,
                    "chunk_index": i
                }
            }
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return filename


def load_visited():
    try:
        if os.path.exists(VISITED_PATH):
            with open(VISITED_PATH, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                return set(data.get("visited", []))
    except Exception:
        logging.warning("Could not load visited.json, starting fresh")
    return set()


def save_visited(visited_set):
    try:
        with open(VISITED_PATH, "w", encoding="utf-8") as fh:
            json.dump({"visited": list(visited_set)}, fh, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.warning(f"Failed to write visited.json: {e}")


def crawl(seed_url, max_pages=200, max_depth=3, delay=DEFAULT_DELAY, verbose=True, resume=True):
    seed_url = sanitize_url(seed_url)
    parsed_seed = urlparse(seed_url)
    seed_netloc = parsed_seed.netloc

    rp = get_robots_parser(seed_url)
    visited = load_visited() if resume else set()
    q = deque()
    q.append((seed_url, 0))
    pages_crawled = 0
    out_files = []

    pbar = tqdm(total=max_pages, desc="Crawling", unit="page") if verbose else None

    while q and pages_crawled < max_pages:
        url, depth = q.popleft()
        normalized = normalize_url_for_dedupe(url)
        if normalized in visited:
            continue

        # enforce depth
        if depth > max_depth:
            continue

        if not allowed_by_robots(rp, url):
            if verbose:
                logging.info(f"[robots] skipping {url}")
            visited.add(normalized)
            save_visited(visited)
            continue

        # rate limit
        time.sleep(delay)

        r = fetch_url(url)
        if r is None:
            visited.add(normalized)
            save_visited(visited)
            continue

        content_type = r.headers.get("Content-Type", "")
        if is_pdf_link(url) or "application/pdf" in content_type.lower():
            local_pdf = download_pdf(url)
            if not local_pdf:
                visited.add(normalized)
                save_visited(visited)
                continue
            text = extract_text_from_pdf(local_pdf)
            if not text:
                visited.add(normalized)
                save_visited(visited)
                continue
            metadata = {"url": url, "title": os.path.basename(local_pdf), "fetched_at": datetime.utcnow().isoformat(), "type": "pdf"}
            chunks = chunk_text(text)
            if chunks:
                fname = write_chunks_jsonl(chunks, metadata)
                out_files.append(fname)
                pages_crawled += 1
                if pbar: pbar.update(1)
            visited.add(normalized)
            save_visited(visited)
            continue

        html = r.text
        text = extract_text_from_html(html, url)
        if text:
            title = ""
            try:
                soup = BeautifulSoup(html, "html.parser")
                if soup.title and soup.title.string:
                    title = soup.title.string.strip()
            except Exception:
                pass
            metadata = {"url": url, "title": title, "fetched_at": datetime.utcnow().isoformat(), "type": "html"}
            chunks = chunk_text(text)
            if chunks:
                fname = write_chunks_jsonl(chunks, metadata)
                out_files.append(fname)
                pages_crawled += 1
                if pbar: pbar.update(1)

        # queue same-domain links
        links = find_links(html, url)
        for link in links:
            if is_same_domain(seed_netloc, link):
                normalized_link = normalize_url_for_dedupe(link)
                if normalized_link not in visited:
                    q.append((link, depth + 1))

        # persist visited immediately so progress isn't lost
        visited.add(normalized)
        save_visited(visited)

    if pbar:
        pbar.close()
    return out_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Polite resuming site scraper")
    parser.add_argument("--seed", required=True, help="Seed URL, e.g., https://lnmiit.ac.in/")
    parser.add_argument("--max-pages", type=int, default=200, help="Max number of pages to fetch")
    parser.add_argument("--max-depth", type=int, default=3, help="Max crawl depth")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="Delay between requests (seconds)")
    parser.add_argument("--no-resume", action="store_true", help="Start fresh (ignore visited.json)")
    args = parser.parse_args()

    logging.info("Trafilatura available: %s", _HAS_TRAFILATURA)
    out = crawl(
        args.seed,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        delay=args.delay,
        verbose=True,
        resume=not args.no_resume,
    )
    logging.info("Wrote %d files to %s", len(out), OUTPUT_DIR)
