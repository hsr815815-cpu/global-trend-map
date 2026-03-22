#!/usr/bin/env python3
"""
collect_trends.py — Global Trend Data Collector
Collects trending data from Google Trends RSS, YouTube, GDELT, Wikipedia, Apple App Store RSS.
Saves to public/data/trends.json with backup.
Usage: python scripts/collect_trends.py
"""

import os
import json
import time
import re
import shutil
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from urllib.parse import quote, urlencode, quote as url_quote
from pathlib import Path

try:
    import requests
except ImportError:
    raise SystemExit("ERROR: 'requests' not installed. Run: pip install requests feedparser")

try:
    import feedparser
except ImportError:
    raise SystemExit("ERROR: 'feedparser' not installed. Run: pip install requests feedparser")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "public" / "data"
ARCHIVE_DIR = DATA_DIR / "archive"
OUTPUT_FILE = DATA_DIR / "trends.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("collect_trends")

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

COUNTRIES = {
    "US": {"name": "United States",       "flag": "🇺🇸", "hl": "en", "geo": "US"},
    "KR": {"name": "South Korea",         "flag": "🇰🇷", "hl": "en", "geo": "KR"},
    "JP": {"name": "Japan",               "flag": "🇯🇵", "hl": "en", "geo": "JP"},
    "GB": {"name": "United Kingdom",      "flag": "🇬🇧", "hl": "en", "geo": "GB"},
    "DE": {"name": "Germany",             "flag": "🇩🇪", "hl": "en", "geo": "DE"},
    "IN": {"name": "India",               "flag": "🇮🇳", "hl": "en", "geo": "IN"},
    "BR": {"name": "Brazil",              "flag": "🇧🇷", "hl": "en", "geo": "BR"},
    "FR": {"name": "France",              "flag": "🇫🇷", "hl": "en", "geo": "FR"},
    "AU": {"name": "Australia",           "flag": "🇦🇺", "hl": "en", "geo": "AU"},
    "MX": {"name": "Mexico",              "flag": "🇲🇽", "hl": "en", "geo": "MX"},
    "CA": {"name": "Canada",              "flag": "🇨🇦", "hl": "en", "geo": "CA"},
    "RU": {"name": "Russia",              "flag": "🇷🇺", "hl": "en", "geo": "RU"},
    "IT": {"name": "Italy",               "flag": "🇮🇹", "hl": "en", "geo": "IT"},
    "ES": {"name": "Spain",               "flag": "🇪🇸", "hl": "en", "geo": "ES"},
    "NL": {"name": "Netherlands",         "flag": "🇳🇱", "hl": "en", "geo": "NL"},
    "SE": {"name": "Sweden",              "flag": "🇸🇪", "hl": "en", "geo": "SE"},
    "NO": {"name": "Norway",              "flag": "🇳🇴", "hl": "en", "geo": "NO"},
    "DK": {"name": "Denmark",             "flag": "🇩🇰", "hl": "en", "geo": "DK"},
    "FI": {"name": "Finland",             "flag": "🇫🇮", "hl": "en", "geo": "FI"},
    "PL": {"name": "Poland",              "flag": "🇵🇱", "hl": "en", "geo": "PL"},
    "TR": {"name": "Turkey",              "flag": "🇹🇷", "hl": "en", "geo": "TR"},
    "TH": {"name": "Thailand",            "flag": "🇹🇭", "hl": "en", "geo": "TH"},
    "ID": {"name": "Indonesia",           "flag": "🇮🇩", "hl": "en", "geo": "ID"},
    "MY": {"name": "Malaysia",            "flag": "🇲🇾", "hl": "en", "geo": "MY"},
    "SG": {"name": "Singapore",           "flag": "🇸🇬", "hl": "en", "geo": "SG"},
    "VN": {"name": "Vietnam",             "flag": "🇻🇳", "hl": "en", "geo": "VN"},
    "PH": {"name": "Philippines",         "flag": "🇵🇭", "hl": "en", "geo": "PH"},
    "TW": {"name": "Taiwan",              "flag": "🇹🇼", "hl": "en", "geo": "TW"},
    "HK": {"name": "Hong Kong",           "flag": "🇭🇰", "hl": "en", "geo": "HK"},
    "NG": {"name": "Nigeria",             "flag": "🇳🇬", "hl": "en", "geo": "NG"},
    "ZA": {"name": "South Africa",        "flag": "🇿🇦", "hl": "en", "geo": "ZA"},
    "EG": {"name": "Egypt",               "flag": "🇪🇬", "hl": "en", "geo": "EG"},
    "AR": {"name": "Argentina",           "flag": "🇦🇷", "hl": "en", "geo": "AR"},
    "CL": {"name": "Chile",               "flag": "🇨🇱", "hl": "en", "geo": "CL"},
    "CO": {"name": "Colombia",            "flag": "🇨🇴", "hl": "en", "geo": "CO"},
    "PE": {"name": "Peru",               "flag": "🇵🇪", "hl": "en", "geo": "PE"},
}

APPLE_RSS_COUNTRIES = ["US", "KR", "JP"]

BLOCKED_KEYWORDS = {
    # adult
    "porn", "xxx", "nude", "naked", "sex tape", "onlyfans leak",
    # violence
    "murder how to", "kill guide", "bomb making",
    # hate speech
    "white supremacy", "nazi", "racial slur",
    # gambling
    "casino hack", "slot cheat", "betting exploit",
    # drugs
    "buy drugs", "drug synthesis", "meth recipe",
    # terrorism
    "terrorist attack plan", "jihad recruit", "isis guide",
}

CATEGORY_KEYWORDS = {
    "sports":      ["nfl", "nba", "mlb", "nhl", "soccer", "football", "basketball", "baseball",
                    "tennis", "golf", "f1", "formula 1", "olympics", "world cup", "liga", "premier",
                    "championship", "tournament", "match", "game", "athlete", "player", "team"],
    "music":       ["album", "song", "concert", "tour", "grammy", "billboard", "single", "music",
                    "singer", "rapper", "band", "spotify", "chart", "release", "mv", "kpop"],
    "tech":        ["ai", "artificial intelligence", "chatgpt", "openai", "apple", "google", "microsoft",
                    "samsung", "iphone", "android", "app", "software", "hardware", "startup", "crypto",
                    "bitcoin", "blockchain", "meta", "tesla", "spacex"],
    "entertainment": ["movie", "film", "series", "netflix", "disney", "hbo", "tv show", "trailer",
                      "actor", "actress", "celebrity", "award", "oscar", "emmy", "box office"],
    "news":        ["election", "president", "government", "war", "conflict", "economy", "stock",
                    "inflation", "weather", "hurricane", "earthquake", "disaster", "policy", "law"],
    "health":      ["covid", "vaccine", "cancer", "heart", "mental health", "diet", "fitness",
                    "drug", "medicine", "hospital", "doctor", "treatment", "research"],
    "gaming":      ["game", "xbox", "playstation", "nintendo", "steam", "esports", "twitch",
                    "fortnite", "minecraft", "valorant", "league of legends"],
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; GlobalTrendBot/1.0; "
        "+https://global-trend-map-web.vercel.app)"
    )
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def safe_get(url: str, timeout: int = 15, max_retries: int = 3, **kwargs):
    """GET with exponential backoff retry; returns Response or None."""
    for attempt in range(max_retries):
        try:
            resp = SESSION.get(url, timeout=timeout, **kwargs)
            resp.raise_for_status()
            return resp
        except Exception as exc:
            if attempt == max_retries - 1:
                log.warning("GET %s failed after %d retries: %s", url, max_retries, exc)
                return None
            wait = 2 ** attempt
            log.info("    Retry %d/%d after %ds: %s", attempt + 1, max_retries, wait, exc)
            time.sleep(wait)


def is_blocked(keyword: str) -> bool:
    kw = keyword.lower()
    for bad in BLOCKED_KEYWORDS:
        if bad in kw:
            return True
    return False


def classify_category(keyword: str) -> str:
    kw = keyword.lower()
    for cat, words in CATEGORY_KEYWORDS.items():
        for w in words:
            if w in kw:
                return cat
    return "news"


def format_volume(n: int) -> str:
    if n >= 1_000_000:
        return f"{n // 1_000_000}M+"
    if n >= 1_000:
        return f"{n // 1_000}K+"
    return str(n)


def calculate_temperature(volume: int, rank: int, spread: int) -> int:
    """Score 0-100 based on volume, rank, and country-spread."""
    vol_score  = min(50, int(volume / 200_000))
    rank_score = max(0, 30 - rank * 2)
    spread_score = min(20, spread * 5)
    return min(100, vol_score + rank_score + spread_score)


def calculate_velocity(rank: int) -> str:
    if rank <= 3:
        return "rising"
    if rank <= 8:
        return "new"
    if rank <= 14:
        return "steady"
    return "falling"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def translate_to_english(text: str) -> str:
    """Translate non-ASCII text to English using Google Translate (free, no key)."""
    if all(ord(c) < 128 for c in text):
        return text  # Already ASCII
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={url_quote(text)}"
        r = SESSION.get(url, timeout=5)
        data = r.json()
        translated = ''.join([item[0] for item in data[0] if item[0]])
        return translated.strip() or text
    except Exception:
        return text

# ---------------------------------------------------------------------------
# Source: Google Trends RSS
# ---------------------------------------------------------------------------

def fetch_google_trends(country_code: str, meta: dict) -> list[dict]:
    geo  = meta["geo"]
    hl   = meta["hl"]
    url  = f"https://trends.google.com/trending/rss?geo={geo}&hl={hl}"
    resp = safe_get(url, timeout=20)
    if resp is None:
        return []

    feed = feedparser.parse(resp.text)
    trends = []

    for rank, entry in enumerate(feed.entries[:20], start=1):
        keyword = entry.get("title", "").strip()
        if not keyword or is_blocked(keyword):
            continue

        # ht:approx_traffic is now a direct attribute on entry
        traffic_raw = getattr(entry, "ht_approx_traffic", "") or ""
        if not traffic_raw:
            for tag in entry.get("tags", []):
                if "approx_traffic" in tag.get("term", ""):
                    traffic_raw = tag["term"]

        # Parse volume — only use real data, no fallback estimates
        vol_match = re.search(r"([\d,]+)", traffic_raw.replace("+", ""))
        if not vol_match:
            continue  # Skip entries without real traffic data
        volume_raw = int(vol_match.group(1).replace(",", ""))

        # Related news from entry summary
        related_news = []
        if hasattr(entry, "summary"):
            snippets = re.findall(r"<title>(.*?)</title>", entry.get("summary", ""))
            related_news = [re.sub(r"<[^>]+>", "", s).strip() for s in snippets[:3]]
        if not related_news and hasattr(entry, "ht_news_item_title"):
            related_news = [entry.ht_news_item_title]

        trends.append({
            "rank":        rank,
            "keyword":     keyword,
            "keywordEn":   translate_to_english(keyword),
            "volume":      format_volume(volume_raw),
            "volumeRaw":   volume_raw,
            "category":    classify_category(keyword),
            "temperature": calculate_temperature(volume_raw, rank, 1),
            "velocity":    calculate_velocity(rank),
            "isGlobal":    False,
            "source":      "google_trends",
            "description": "",
            "relatedNews": related_news,
        })

    log.info("  Google Trends %s: %d trends", country_code, len(trends))
    return trends


def collect_google_trends() -> tuple[dict, bool]:
    results = {}
    success = True
    for code, meta in COUNTRIES.items():
        try:
            trends = fetch_google_trends(code, meta)
            results[code] = trends
            time.sleep(0.5)          # polite rate-limit
        except Exception as exc:
            log.error("Google Trends %s error: %s", code, exc)
            results[code] = []
            success = False
    return results, success

# ---------------------------------------------------------------------------
# Source: YouTube Trending
# ---------------------------------------------------------------------------

def collect_youtube(country_codes: list[str]) -> tuple[dict, int, bool]:
    if not YOUTUBE_API_KEY:
        log.info("YouTube: no API key — skipping")
        return {}, 0, False

    results = {}
    quota_used = 0
    success = True

    for code in country_codes:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part":        "snippet,statistics",
            "chart":       "mostPopular",
            "regionCode":  code,
            "maxResults":  10,
            "key":         YOUTUBE_API_KEY,
        }
        resp = safe_get(url, params=params, timeout=15)
        quota_used += 1           # each list call costs ~1 unit
        if resp is None:
            success = False
            continue

        data = resp.json()
        items = data.get("items", [])
        trends = []

        for rank, item in enumerate(items, start=1):
            snippet = item.get("snippet", {})
            stats   = item.get("statistics", {})
            title   = snippet.get("title", "").strip()
            if not title or is_blocked(title):
                continue

            view_count = int(stats.get("viewCount", 0))
            trends.append({
                "rank":        rank,
                "keyword":     title,
                "volume":      format_volume(view_count),
                "volumeRaw":   view_count,
                "category":    classify_category(title),
                "temperature": calculate_temperature(view_count, rank, 1),
                "velocity":    calculate_velocity(rank),
                "isGlobal":    False,
                "source":      "youtube",
                "description": snippet.get("description", "")[:200],
                "relatedNews": [],
                "youtubeId":   item.get("id", ""),
                "channelTitle": snippet.get("channelTitle", ""),
            })

        results[code] = trends
        log.info("  YouTube %s: %d videos", code, len(trends))
        time.sleep(0.3)

    return results, quota_used, success

# ---------------------------------------------------------------------------
# Source: GDELT News
# ---------------------------------------------------------------------------

def collect_gdelt() -> tuple[list[dict], bool]:
    """Fetch top global news from GDELT 2.0 DOC API."""
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query":      "sourcelang:english",
        "mode":       "ArtList",
        "maxrecords": 50,
        "sort":       "HybridRel",
        "format":     "json",
    }
    resp = safe_get(url, params=params, timeout=20)
    if resp is None:
        return [], False

    try:
        data  = resp.json()
        articles = data.get("articles", [])
    except Exception:
        return [], False

    headlines = []
    for art in articles[:25]:
        title = art.get("title", "").strip()
        if title and not is_blocked(title):
            headlines.append({
                "title":  title,
                "url":    art.get("url", ""),
                "source": art.get("domain", ""),
            })

    log.info("GDELT: %d headlines collected", len(headlines))
    return headlines, True


def get_gdelt_headlines_for_keyword(keyword: str, gdelt_cache: list[dict]) -> list[str]:
    kw = keyword.lower()
    matches = []
    for art in gdelt_cache:
        if kw in art["title"].lower():
            matches.append(art["title"])
        if len(matches) >= 3:
            break
    return matches

# ---------------------------------------------------------------------------
# Source: Wikipedia
# ---------------------------------------------------------------------------

_wiki_cache: dict[str, str] = {}

def fetch_wikipedia_description(keyword: str) -> str:
    if keyword in _wiki_cache:
        return _wiki_cache[keyword]

    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + quote(keyword)
    resp = safe_get(url, timeout=10)
    if resp is None:
        _wiki_cache[keyword] = ""
        return ""

    try:
        data = resp.json()
        desc = data.get("extract", "")[:300]
    except Exception:
        desc = ""

    _wiki_cache[keyword] = desc
    time.sleep(0.2)
    return desc


def fetch_wikipedia_views(keyword: str) -> int:
    """Get total views for the past 7 days from Wikipedia pageviews API."""
    today = datetime.now(timezone.utc)
    start = (today - timedelta(days=7)).strftime("%Y%m%d")
    end   = today.strftime("%Y%m%d")
    enc   = quote(keyword.replace(" ", "_"))
    url   = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{enc}/daily/{start}/{end}"
    resp  = safe_get(url, timeout=10)
    if resp is None:
        return 0
    try:
        items = resp.json().get("items", [])
        return sum(i.get("views", 0) for i in items)
    except Exception:
        return 0

# ---------------------------------------------------------------------------
# Source: Apple App Store RSS
# ---------------------------------------------------------------------------

def collect_apple_rss(country_codes: list[str]) -> tuple[dict, bool]:
    results = {}
    success = True

    for code in country_codes:
        cc = code.lower()
        url = f"https://rss.applemarketingtools.com/api/v2/{cc}/apps/top-free/10/apps.json"
        resp = safe_get(url, timeout=15)
        if resp is None:
            success = False
            continue
        try:
            feed_data = resp.json()
            items = feed_data.get("feed", {}).get("results", [])
        except Exception:
            success = False
            continue

        trends = []
        for rank, item in enumerate(items[:10], start=1):
            name = item.get("name", "").strip()
            if not name or is_blocked(name):
                continue
            trends.append({
                "rank":        rank,
                "keyword":     name,
                "volume":      "N/A",
                "volumeRaw":   0,
                "category":    "tech",
                "temperature": max(0, 60 - rank * 3),
                "velocity":    calculate_velocity(rank),
                "isGlobal":    False,
                "source":      "apple_rss",
                "description": item.get("artistName", ""),
                "relatedNews": [],
                "appUrl":      item.get("url", ""),
            })
        results[code] = trends
        log.info("  Apple RSS %s: %d apps", code, len(trends))
        time.sleep(0.3)

    return results, success

# ---------------------------------------------------------------------------
# Trend enrichment and aggregation
# ---------------------------------------------------------------------------

def enrich_trends(
    gt_data: dict,
    yt_data: dict,
    gdelt_headlines: list[dict],
    apple_data: dict,
) -> dict:
    """Merge per-country trends, add Wikipedia descriptions, GDELT headlines."""
    countries_out = {}
    keyword_country_map: dict[str, list[str]] = {}

    for code, meta in COUNTRIES.items():
        google_trends = gt_data.get(code, [])
        youtube_trends = yt_data.get(code, [])
        apple_trends   = apple_data.get(code, [])

        # De-duplicate by keyword (prefer Google Trends)
        seen: dict[str, dict] = {}
        for t in google_trends + youtube_trends + apple_trends:
            kw = t["keyword"].lower()
            if kw not in seen:
                seen[kw] = t
            else:
                # Merge: take higher volume
                if t["volumeRaw"] > seen[kw]["volumeRaw"]:
                    seen[kw] = t

        merged = sorted(seen.values(), key=lambda x: (-x["volumeRaw"], x["rank"]))

        # Re-rank and enrich
        enriched = []
        for new_rank, t in enumerate(merged[:20], start=1):
            t["rank"] = new_rank
            # GDELT related news only (skip slow Wikipedia enrichment)
            if not t.get("relatedNews"):
                t["relatedNews"] = get_gdelt_headlines_for_keyword(t["keyword"], gdelt_headlines)
            # Track keyword spread
            kw = t["keyword"].lower()
            if kw not in keyword_country_map:
                keyword_country_map[kw] = []
            keyword_country_map[kw].append(code)
            enriched.append(t)

        countries_out[code] = {
            "name":   meta["name"],
            "flag":   meta["flag"],
            "trends": enriched,
        }

    # Second pass: update isGlobal and recalculate temperature with spread
    for code, cdata in countries_out.items():
        for t in cdata["trends"]:
            kw     = t["keyword"].lower()
            spread = len(keyword_country_map.get(kw, []))
            t["isGlobal"]    = spread >= 3
            t["temperature"] = calculate_temperature(t["volumeRaw"], t["rank"], spread)

    return countries_out, keyword_country_map


def build_global_section(
    countries_data: dict,
    keyword_country_map: dict,
) -> dict:
    """Aggregate global stats and find top trends."""
    all_trends = []
    for code, cdata in countries_data.items():
        for t in cdata["trends"]:
            all_trends.append({**t, "_country": code, "_flag": cdata["flag"]})

    if not all_trends:
        return {}

    # Sort by temperature then volumeRaw
    all_trends.sort(key=lambda x: (-x["temperature"], -x["volumeRaw"]))

    top = all_trends[0]
    global_temp = int(sum(t["temperature"] for t in all_trends) / max(len(all_trends), 1))

    def temp_label(t: int) -> str:
        if t >= 80: return "VIRAL"
        if t >= 60: return "HOT"
        if t >= 40: return "WARM"
        return "COOL"

    # Top by category
    top_by_category: dict[str, dict] = {}
    seen_cats: set[str] = set()
    for t in all_trends:
        cat = t.get("category", "news")
        if cat not in seen_cats:
            top_by_category[cat] = {
                "keyword": t["keyword"],
                "country": t["_country"],
                "flag":    t["_flag"],
                "volume":  t["volume"],
                "temperature": t["temperature"],
            }
            seen_cats.add(cat)

    total_trends = sum(len(cd["trends"]) for cd in countries_data.values())

    next_update = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    # risingFast: top 3 trends by temperature
    rising_fast = []
    seen_rf = set()
    for t in all_trends[:10]:
        kw = t["keyword"]
        if kw not in seen_rf and len(rising_fast) < 3:
            rising_fast.append({
                "keyword": kw,
                "country": t["_country"],
                "change": t["volume"],
            })
            seen_rf.add(kw)

    # categoryBreakdown: % of trends per category
    cat_counts: dict[str, int] = {}
    for t in all_trends:
        cat = t.get("category", "news")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    total_cat = max(len(all_trends), 1)
    category_breakdown = {
        cat: round(count / total_cat * 100)
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])
    }

    return {
        "temperature":     global_temp,
        "temperatureLabel": temp_label(global_temp),
        "topTrend": {
            "keyword":  top["keyword"],
            "country":  top["_country"],
            "volume":   top["volume"],
            "flag":     top["_flag"],
            "category": top.get("category", "news"),
        },
        "topByCategory":  top_by_category,
        "totalCountries": len(countries_data),
        "totalTrends":    total_trends,
        "nextUpdate":     next_update,
        "risingFast":        rising_fast,
        "categoryBreakdown": category_breakdown,
    }

# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    pipeline_start = datetime.now(timezone.utc)
    log.info("=" * 60)
    log.info("Global Trend Collector — %s", pipeline_start.isoformat())
    log.info("=" * 60)

    blocked_count   = 0
    success_count   = 0
    error_count     = 0
    youtube_quota   = 0

    sources_status = {
        "googleTrends": False,
        "youtube":      False,
        "gdelt":        False,
        "wikipedia":    False,
        "apple":        False,
    }

    # 1. Google Trends
    log.info("[1/5] Collecting Google Trends RSS...")
    gt_data, gt_ok = collect_google_trends()
    sources_status["googleTrends"] = gt_ok
    success_count += sum(1 for v in gt_data.values() if v)
    error_count   += sum(1 for v in gt_data.values() if not v)

    # 2. YouTube
    log.info("[2/5] Collecting YouTube Trending...")
    yt_data, youtube_quota, yt_ok = collect_youtube(list(COUNTRIES.keys()))
    sources_status["youtube"] = yt_ok

    # 3. GDELT
    log.info("[3/5] Collecting GDELT News Headlines...")
    gdelt_headlines, gdelt_ok = collect_gdelt()
    sources_status["gdelt"] = gdelt_ok

    # 4. Apple App Store RSS
    log.info("[4/5] Collecting Apple App Store RSS...")
    apple_data, apple_ok = collect_apple_rss(APPLE_RSS_COUNTRIES)
    sources_status["apple"] = apple_ok

    # 5. Enrich with Wikipedia (happens inside enrich_trends)
    log.info("[5/5] Enriching trends with Wikipedia descriptions...")
    countries_data, keyword_country_map = enrich_trends(gt_data, yt_data, gdelt_headlines, apple_data)
    sources_status["wikipedia"] = True   # Wikipedia runs inline; mark true if no exception

    # Build global section
    global_section = build_global_section(countries_data, keyword_country_map)

    pipeline_end  = datetime.now(timezone.utc)
    duration_secs = int((pipeline_end - pipeline_start).total_seconds())

    output = {
        "lastUpdated": now_iso(),
        "sources":     sources_status,
        "countries":   countries_data,
        "global":      global_section,
        "pipelineStats": {
            "startTime":        pipeline_start.isoformat(),
            "endTime":          pipeline_end.isoformat(),
            "duration":         duration_secs,
            "successCount":     success_count,
            "errorCount":       error_count,
            "blockedKeywords":  blocked_count,
            "youtubeQuotaUsed": youtube_quota,
        },
    }

    # Minimum threshold guard
    successful_countries = len([c for c in output['countries'] if output['countries'][c]['trends']])
    if successful_countries < 5:
        log.warning("WARNING: Only %d countries collected. Keeping existing trends.json.", successful_countries)
        import sys
        sys.exit(0)

    # Backup previous data
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    if OUTPUT_FILE.exists():
        ts    = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
        backup = ARCHIVE_DIR / f"trends_{ts}.json"
        shutil.copy2(OUTPUT_FILE, backup)
        log.info("Backed up previous data to %s", backup)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    log.info("=" * 60)
    log.info("DONE — %d countries | %d total trends | %ds",
             global_section.get("totalCountries", 0),
             global_section.get("totalTrends", 0),
             duration_secs)
    log.info("Global temperature: %d°T (%s)",
             global_section.get("temperature", 0),
             global_section.get("temperatureLabel", ""))
    log.info("Top trend: %s (%s)",
             global_section.get("topTrend", {}).get("keyword", "N/A"),
             global_section.get("topTrend", {}).get("country", "N/A"))
    log.info("Saved → %s", OUTPUT_FILE)
    log.info("=" * 60)


if __name__ == "__main__":
    main()
