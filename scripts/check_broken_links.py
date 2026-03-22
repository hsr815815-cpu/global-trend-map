#!/usr/bin/env python3
"""
check_broken_links.py — Internal Link Checker
Crawls the deployed site and reports any internal 404s.
Outputs a report to public/report/broken-links-report.txt.
Usage: python scripts/check_broken_links.py [base_url]
"""

import sys
import time
import logging
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urljoin

try:
    import requests
except ImportError:
    raise SystemExit("ERROR: 'requests' not installed. Run: pip install requests feedparser")

BASE_DIR    = Path(__file__).resolve().parent.parent
REPORT_DIR  = BASE_DIR / "public" / "report"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_FILE = REPORT_DIR / "broken-links-report.txt"

DEFAULT_BASE_URL = "https://global-trend-map-web.vercel.app"
MAX_PAGES        = 200
REQUEST_DELAY    = 0.5   # seconds between requests
TIMEOUT          = 15

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("check_broken_links")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GlobalTrendLinkChecker/1.0)"
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def is_internal(url: str, base: str) -> bool:
    parsed_url  = urlparse(url)
    parsed_base = urlparse(base)
    return (
        parsed_url.netloc == "" or
        parsed_url.netloc == parsed_base.netloc
    )


def normalize(url: str, base: str) -> str:
    full = urljoin(base, url)
    parsed = urlparse(full)
    # Strip fragment
    return parsed._replace(fragment="").geturl()


def extract_links(html: str, page_url: str) -> list[str]:
    import re
    hrefs = re.findall(r'href=["\']([^"\'#][^"\']*)["\']', html)
    links = []
    for href in hrefs:
        if href.startswith("mailto:") or href.startswith("javascript:"):
            continue
        links.append(normalize(href, page_url))
    return links


def check_url(url: str) -> tuple[int, float]:
    """Returns (status_code, response_time_ms). Uses HEAD first, fallback GET."""
    t0 = time.time()
    try:
        resp = SESSION.head(url, timeout=TIMEOUT, allow_redirects=True)
        elapsed = (time.time() - t0) * 1000
        # Some servers reject HEAD; retry with GET
        if resp.status_code in (405, 501):
            resp = SESSION.get(url, timeout=TIMEOUT, allow_redirects=True)
        return resp.status_code, elapsed
    except requests.exceptions.ConnectionError:
        return -1, 0.0
    except requests.exceptions.Timeout:
        return -2, 0.0
    except Exception:
        return -3, 0.0


def crawl(base_url: str) -> tuple[list[dict], list[dict]]:
    """BFS crawl; returns (all_results, broken_links)."""
    visited  = set()
    queue    = deque([base_url])
    all_res  = []
    broken   = []
    pages    = 0

    while queue and pages < MAX_PAGES:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        pages += 1

        log.info("[%d] Checking: %s", pages, url)
        code, ms = check_url(url)
        record = {"url": url, "status": code, "ms": round(ms, 1)}
        all_res.append(record)

        if code == 404:
            broken.append(record)
            log.warning("  404 BROKEN: %s", url)
        elif code < 0:
            error_map = {-1: "CONNECTION_ERROR", -2: "TIMEOUT", -3: "UNKNOWN_ERROR"}
            log.warning("  %s: %s", error_map.get(code, "ERROR"), url)

        # Only follow internal pages that returned 200
        if code == 200 and is_internal(url, base_url):
            try:
                resp = SESSION.get(url, timeout=TIMEOUT)
                for link in extract_links(resp.text, url):
                    if link not in visited and is_internal(link, base_url):
                        queue.append(link)
            except Exception:
                pass

        time.sleep(REQUEST_DELAY)

    return all_res, broken


def write_report(base_url: str, all_res: list[dict], broken: list[dict]):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "=" * 60,
        f"BROKEN LINK REPORT — {now}",
        f"Base URL: {base_url}",
        f"Pages checked: {len(all_res)}",
        f"Broken links found: {len(broken)}",
        "=" * 60,
        "",
    ]

    if broken:
        lines.append("BROKEN LINKS (404):")
        lines.append("-" * 40)
        for b in broken:
            lines.append(f"  {b['url']}")
        lines.append("")
    else:
        lines.append("✅ No broken links found!")
        lines.append("")

    lines.append("ALL RESULTS:")
    lines.append("-" * 40)
    for r in all_res:
        status_str = str(r["status"]) if r["status"] > 0 else "ERR"
        lines.append(f"  [{status_str}] {r['ms']}ms  {r['url']}")

    report_text = "\n".join(lines)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_text)

    return report_text


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL
    log.info("=" * 60)
    log.info("Broken Link Checker — base: %s", base_url)
    log.info("Max pages: %d | Delay: %.1fs", MAX_PAGES, REQUEST_DELAY)
    log.info("=" * 60)

    all_res, broken = crawl(base_url)
    report_text = write_report(base_url, all_res, broken)

    print()
    print(report_text[:2000])   # Print first 2000 chars to stdout
    if len(report_text) > 2000:
        print(f"... (full report at {REPORT_FILE})")

    log.info("Report saved → %s", REPORT_FILE)

    if broken:
        log.warning("%d broken links found!", len(broken))
        sys.exit(1)   # Non-zero exit for CI failure
    else:
        log.info("No broken links found.")


if __name__ == "__main__":
    main()
