#!/usr/bin/env python3
"""
generate_blog.py — Blog Post Generator (skeleton, pending redesign)
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR    = Path(__file__).resolve().parent.parent
DATA_DIR    = BASE_DIR / "public" / "data"
BLOG_DIR    = BASE_DIR / "public" / "blog"
TRENDS_FILE = DATA_DIR / "trends.json"
INDEX_FILE  = DATA_DIR / "posts-index.json"

BLOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("generate_blog")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_trends() -> dict:
    if not TRENDS_FILE.exists():
        raise FileNotFoundError(f"trends.json not found at {TRENDS_FILE}")
    with open(TRENDS_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_index() -> dict:
    if INDEX_FILE.exists():
        with open(INDEX_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return {"posts": data, "lastUpdated": now_iso()}
        return data
    return {"posts": [], "lastUpdated": now_iso()}


def save_index(index: dict):
    index["lastUpdated"] = now_iso()
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def main():
    log.info("Blog generation skipped — pending redesign.")


if __name__ == "__main__":
    main()
