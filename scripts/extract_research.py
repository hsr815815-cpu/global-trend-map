#!/usr/bin/env python3
"""
extract_research.py
trends.json → research.json 변환
- 전체 키워드 temperature 순으로 랭킹
- 최근 5개 스포트라이트 체크, 중복 스킵
- 중복 아닌 최고 순위 키워드 선택
"""

import json
import re
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR    = Path(__file__).resolve().parent.parent
TRENDS_FILE = BASE_DIR / "public" / "data" / "trends.json"
INDEX_FILE  = BASE_DIR / "public" / "data" / "posts-index.json"
OUTPUT_FILE = BASE_DIR / "scripts" / "research.json"

SKIP_RECENT = 5  # 최근 N개 스포트라이트 중복 스킵
SITE_URL    = "https://global-trend-map-web.vercel.app"


def normalize_kw(text: str) -> str:
    """곡선 따옴표 등 유니코드 변형 문자를 직선 ASCII로 통일 (중복 스킵 비교용)"""
    return (
        text.lower()
        .replace("\u2018", "'").replace("\u2019", "'")  # ' '
        .replace("\u201c", '"').replace("\u201d", '"')  # " "
        .replace("\u2032", "'").replace("\u2033", '"')  # ′ ″
        .strip()
    )


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)  # ASCII only (비ASCII 제거)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60].strip("-")


def build_ranked_list(trends_data: dict) -> list:
    """국가별 트렌드에서 temperature 기준 전체 랭킹 생성"""
    countries = trends_data.get("countries", {})
    seen = {}  # keyword_lower → best entry

    for code, cdata in countries.items():
        flag = cdata.get("flag", "🌐")
        name = cdata.get("name", code)
        for t in cdata.get("trends", []):
            kw = t.get("keywordEn") or t.get("keyword", "")
            if not kw:
                continue
            kw_lower = normalize_kw(kw)
            temp = t.get("temperature", 0)

            if kw_lower not in seen or temp > seen[kw_lower]["temperature"]:
                seen[kw_lower] = {
                    "keyword": kw,
                    "keyword_lower": kw_lower,
                    "category": t.get("category", ""),
                    "temperature": temp,
                    "volume": t.get("volume", "N/A"),
                    "youtube_id": t.get("youtubeId"),
                    "source": t.get("source", "google"),
                    "top_country_name": name,
                    "top_country_flag": flag,
                }

    ranked = sorted(seen.values(), key=lambda x: -x["temperature"])
    return ranked


def get_recent_spotlights(index: dict) -> list:
    """최근 SKIP_RECENT개 스포트라이트 키워드(소문자) 반환"""
    spotlights = index.get("recentSpotlights", [])
    return [normalize_kw(s["keyword"]) for s in spotlights[:SKIP_RECENT]]


def get_countries_for_keyword(trends_data: dict, kw_lower: str) -> list:
    """키워드가 트렌딩인 국가 목록 반환"""
    countries = trends_data.get("countries", {})
    result = []
    for code, cdata in countries.items():
        for t in cdata.get("trends", []):
            kw = normalize_kw(t.get("keywordEn") or t.get("keyword", ""))
            if kw == kw_lower:
                result.append((cdata.get("flag", "🌐"), cdata.get("name", code)))
                break
    return result[:12]


def get_internal_links(index: dict) -> list:
    """내부링크용 최근 EN 포스트 5개"""
    posts = index.get("posts", [])
    en_posts = [p for p in posts if p.get("language") == "en"][:5]
    return [
        {
            "slug": p["slug"],
            "title": p.get("title", ""),
            "url": f"{SITE_URL}/blog/{p['slug']}",
        }
        for p in en_posts
    ]


def main():
    if not TRENDS_FILE.exists():
        result = {"status": "skip", "skip_reason": "trends.json not found"}
        OUTPUT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print("SKIP: trends.json not found")
        return

    trends_data = json.loads(TRENDS_FILE.read_text(encoding="utf-8"))
    index = json.loads(INDEX_FILE.read_text(encoding="utf-8")) if INDEX_FILE.exists() else {"posts": [], "recentSpotlights": []}

    ranked = build_ranked_list(trends_data)
    recent = get_recent_spotlights(index)

    print(f"Recent spotlights (last {SKIP_RECENT}): {recent or '(none)'}")
    print(f"Total ranked keywords: {len(ranked)}")

    # 최근 스포트라이트에 없는 최고 순위 키워드 선택
    selected = None
    for rank, item in enumerate(ranked, start=1):
        if item["keyword_lower"] not in recent:
            selected = item
            selected["rank"] = rank
            print(f"Selected rank #{rank}: {item['keyword']} ({item['temperature']}°T)")
            break

    if not selected:
        result = {"status": "skip", "skip_reason": "All top keywords already covered recently"}
        OUTPUT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print("SKIP: no new keyword found")
        return

    now = datetime.now(timezone.utc)
    kw = selected["keyword"]
    kw_lower = selected["keyword_lower"]
    kw_slug = slugify(kw)

    countries_list = get_countries_for_keyword(trends_data, kw_lower)
    internal_links = get_internal_links(index)

    # risingFast에서 이 키워드 제외한 상위 5개
    g = trends_data.get("global", {})
    rising = []
    for r in g.get("risingFast", []):
        rk = (r.get("keywordEn") or r.get("keyword", "")).lower()
        if rk != kw_lower:
            cn_code = r.get("country", "")
            cn_name = trends_data.get("countries", {}).get(cn_code, {}).get("name", cn_code)
            rising.append({
                "keyword": r.get("keywordEn") or r.get("keyword", ""),
                "country": cn_name,
                "change": r.get("change") or r.get("volume", ""),
            })
        if len(rising) >= 5:
            break

    youtube_url = (
        f"https://www.youtube.com/watch?v={selected['youtube_id']}"
        if selected.get("youtube_id") else None
    )
    google_trends_url = f"https://trends.google.com/trends/explore?q={urllib.parse.quote_plus(kw)}"

    result = {
        "status": "write",
        "keyword": kw,
        "keyword_slug": kw_slug,
        "category": selected["category"],
        "rank": selected["rank"],
        "date": now.strftime("%Y-%m-%d"),
        "date_str": now.strftime("%B %d, %Y"),
        "top_country_name": selected["top_country_name"],
        "top_country_flag": selected["top_country_flag"],
        "volume": selected["volume"],
        "temperature": selected["temperature"],
        "total_countries": g.get("totalCountries", len(trends_data.get("countries", {}))),
        "countries": countries_list,
        "rising_others": rising,
        "category_breakdown": g.get("categoryBreakdown", {}),
        "youtube_url": youtube_url,
        "google_trends_url": google_trends_url,
        "site_url": SITE_URL,
        "internal_links": internal_links,
    }

    OUTPUT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"research.json written -> {kw} (rank #{selected['rank']}, {selected['temperature']}T)")


if __name__ == "__main__":
    main()
