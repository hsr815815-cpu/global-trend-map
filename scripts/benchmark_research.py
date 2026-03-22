#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
benchmark_research.py
─────────────────────
경쟁 사이트 벤치마크 리서치 (100% 무료 소스)

수집 항목:
  1. RSS 피드 파싱       → 콘텐츠 업데이트 빈도, 최근 포스팅 주제
  2. sitemap.xml 파싱   → 총 페이지 수, 최근 7일 신규 페이지 수
  3. Common Crawl CDX   → 크롤링 빈도 (인덱싱 활성도 간접 지표)
  4. Google Trends RSS  → 타겟 키워드 관심도 비교
  5. Tranco 랭킹        → 글로벌 트래픽 순위 (주간 업데이트 CSV)

출력: public/data/benchmark.json
"""

import json
import logging
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

BASE_DIR   = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "public" / "data"
OUTPUT_FILE = OUTPUT_DIR / "benchmark.json"

REQUEST_TIMEOUT = 15  # seconds
SLEEP_BETWEEN  = 1.5  # seconds between requests (polite crawling)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TrendPulseBot/1.0; research-bot)",
    "Accept": "application/xml,text/xml,application/rss+xml,*/*;q=0.9",
}

# ─────────────────────────────────────────────────────────────────────────────
# Target sites (공개 RSS/sitemap이 있는 유사 서비스만 포함)
# ─────────────────────────────────────────────────────────────────────────────

TARGETS = [
    {
        "name": "Exploding Topics",
        "domain": "explodingtopics.com",
        "rss": "https://explodingtopics.com/blog/feed",
        "sitemap": "https://explodingtopics.com/sitemap.xml",
    },
    {
        "name": "Trends24",
        "domain": "trends24.in",
        "rss": None,
        "sitemap": "https://trends24.in/sitemap.xml",
    },
    {
        "name": "Treendly",
        "domain": "treendly.com",
        "rss": None,
        "sitemap": "https://treendly.com/sitemap.xml",
    },
    {
        "name": "Google Trends (Reference)",
        "domain": "trends.google.com",
        "rss": "https://trends.google.com/trending/rss?geo=US",
        "sitemap": None,
    },
    {
        "name": "TrendPulse (Our Site)",
        "domain": "global-trend-map.vercel.app",
        "rss": None,
        "sitemap": "https://global-trend-map.vercel.app/sitemap.xml",
    },
]

# Google Trends 비교 키워드 (RSS 기반)
BENCHMARK_GEO_CODES = ["US", "KR", "JP", "GB", "DE"]

# Tranco 순위 확인 대상 도메인
TRANCO_DOMAINS = ["explodingtopics.com", "trends24.in", "treendly.com"]


# ─────────────────────────────────────────────────────────────────────────────
# HTTP helpers
# ─────────────────────────────────────────────────────────────────────────────

def safe_fetch(url: str, timeout: int = REQUEST_TIMEOUT, retries: int = 2) -> Optional[bytes]:
    """URL을 fetch하고 raw bytes 반환. 실패 시 None."""
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except HTTPError as e:
            log.warning("HTTP %d: %s", e.code, url)
            return None
        except URLError as e:
            if attempt < retries:
                log.warning("URLError (attempt %d/%d): %s — %s", attempt + 1, retries + 1, url, e)
                time.sleep(2 ** attempt)
            else:
                log.error("Failed after %d attempts: %s", retries + 1, url)
                return None
        except Exception as e:
            log.error("Unexpected error fetching %s: %s", url, e)
            return None
    return None


def parse_xml_safe(data: bytes) -> Optional[ET.Element]:
    """XML 파싱. 실패 시 None."""
    try:
        return ET.fromstring(data)
    except ET.ParseError as e:
        log.warning("XML parse error: %s", e)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 1. RSS 피드 분석
# ─────────────────────────────────────────────────────────────────────────────

def analyze_rss(rss_url: str) -> dict:
    """RSS 피드에서 포스팅 빈도, 최신 주제, 마지막 업데이트 추출."""
    result = {
        "status": "error",
        "post_count": 0,
        "last_post_date": None,
        "posts_last_7d": 0,
        "recent_topics": [],
        "avg_posts_per_week": 0.0,
    }
    if not rss_url:
        result["status"] = "no_rss"
        return result

    data = safe_fetch(rss_url)
    if not data:
        return result

    root = parse_xml_safe(data)
    if root is None:
        return result

    now = datetime.now(timezone.utc)
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)

    # RSS 2.0 items
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = root.findall(".//item") or root.findall(".//atom:entry", ns)

    dates = []
    topics = []
    posts_last_7d = 0

    for item in items[:50]:  # 최대 50개
        # 제목
        title_el = item.find("title")
        if title_el is not None and title_el.text:
            topics.append(title_el.text.strip()[:80])

        # 날짜
        pub_date_el = item.find("pubDate") or item.find("updated") or item.find("{http://www.w3.org/2005/Atom}updated")
        if pub_date_el is not None and pub_date_el.text:
            try:
                # 여러 날짜 형식 시도
                date_str = pub_date_el.text.strip()
                for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"]:
                    try:
                        dt = datetime.strptime(date_str[:len(fmt)], fmt).replace(tzinfo=timezone.utc)
                        dates.append(dt)
                        if dt > cutoff_7d:
                            posts_last_7d += 1
                        break
                    except ValueError:
                        continue
            except Exception:
                pass

    if dates:
        dates.sort(reverse=True)
        last_post = dates[0]
        oldest = dates[-1]
        days_range = max((now - oldest).days, 1)
        avg_per_week = (len(dates) / days_range) * 7

        result.update({
            "status": "ok",
            "post_count": len(items),
            "last_post_date": last_post.strftime("%Y-%m-%d"),
            "posts_last_7d": posts_last_7d,
            "recent_topics": topics[:5],
            "avg_posts_per_week": round(avg_per_week, 1),
        })
    else:
        result.update({
            "status": "ok",
            "post_count": len(items),
            "recent_topics": topics[:5],
        })

    return result


# ─────────────────────────────────────────────────────────────────────────────
# 2. sitemap.xml 분석
# ─────────────────────────────────────────────────────────────────────────────

def analyze_sitemap(sitemap_url: str) -> dict:
    """sitemap.xml에서 총 URL 수, 최근 7일 신규 URL 수 추출."""
    result = {
        "status": "error",
        "total_urls": 0,
        "urls_last_7d": 0,
        "urls_last_30d": 0,
        "sitemap_type": "unknown",
    }
    if not sitemap_url:
        result["status"] = "no_sitemap"
        return result

    data = safe_fetch(sitemap_url)
    if not data:
        return result

    root = parse_xml_safe(data)
    if root is None:
        return result

    now = datetime.now(timezone.utc)
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)

    tag = root.tag.lower()
    total_urls = 0
    urls_7d = 0
    urls_30d = 0

    # Sitemap index (sitemapindex → 하위 sitemap 리스트)
    if "sitemapindex" in tag:
        result["sitemap_type"] = "index"
        sub_sitemaps = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap")
        for sm in sub_sitemaps[:5]:  # 최대 5개 서브 sitemap만 확인
            loc = sm.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if loc is None or not loc.text:
                continue
            sub_url = loc.text.strip()
            # 블로그/포스트 관련 sitemap만 파싱
            if any(k in sub_url.lower() for k in ["post", "blog", "article", "news"]):
                time.sleep(SLEEP_BETWEEN)
                sub_data = safe_fetch(sub_url)
                if sub_data:
                    sub_root = parse_xml_safe(sub_data)
                    if sub_root:
                        urls, u7d, u30d = _count_sitemap_urls(sub_root, cutoff_7d, cutoff_30d)
                        total_urls += urls
                        urls_7d += u7d
                        urls_30d += u30d

    # Regular sitemap (urlset)
    elif "urlset" in tag:
        result["sitemap_type"] = "urlset"
        total_urls, urls_7d, urls_30d = _count_sitemap_urls(root, cutoff_7d, cutoff_30d)

    result.update({
        "status": "ok",
        "total_urls": total_urls,
        "urls_last_7d": urls_7d,
        "urls_last_30d": urls_30d,
    })
    return result


def _count_sitemap_urls(root: ET.Element, cutoff_7d: datetime, cutoff_30d: datetime):
    """URL 개수, 7일/30일 신규 URL 카운트."""
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    urls = root.findall(f"{ns}url")
    total = len(urls)
    u7d = 0
    u30d = 0

    for url in urls:
        lastmod = url.find(f"{ns}lastmod")
        if lastmod is not None and lastmod.text:
            try:
                dt_str = lastmod.text.strip()[:10]
                dt = datetime.strptime(dt_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if dt > cutoff_7d:
                    u7d += 1
                if dt > cutoff_30d:
                    u30d += 1
            except ValueError:
                pass

    return total, u7d, u30d


# ─────────────────────────────────────────────────────────────────────────────
# 3. Common Crawl CDX API 분석
# ─────────────────────────────────────────────────────────────────────────────

def analyze_commoncrawl(domain: str) -> dict:
    """Common Crawl CDX API로 도메인 크롤링 빈도 측정 (무료)."""
    result = {
        "status": "error",
        "total_indexed_pages": 0,
        "crawl_index": "CC-MAIN-2024-51",
    }

    # 최신 인덱스 사용
    index = "CC-MAIN-2024-51"
    params = urlencode({
        "url": f"*.{domain}/*",
        "output": "json",
        "limit": 1,
        "fl": "urlkey",
        "showNumPages": "true",
    })
    cdx_url = f"https://index.commoncrawl.org/{index}-index?{params}"

    try:
        data = safe_fetch(cdx_url, timeout=20)
        if data:
            lines = data.decode("utf-8", errors="ignore").strip().split("\n")
            for line in lines:
                try:
                    obj = json.loads(line)
                    if "pages" in obj:
                        result.update({
                            "status": "ok",
                            "total_indexed_pages": int(obj.get("pages", 0)),
                            "crawl_index": index,
                        })
                        break
                except json.JSONDecodeError:
                    pass
        else:
            result["status"] = "no_data"
    except Exception as e:
        log.warning("CDX error for %s: %s", domain, e)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# 4. Google Trends RSS 수집 (키워드 관심도 간접 측정)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_google_trends_sample(geo: str) -> dict:
    """Google Trends RSS에서 현재 상위 트렌드 수집."""
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    data = safe_fetch(url)
    if not data:
        return {"status": "error", "geo": geo, "top_trends": []}

    root = parse_xml_safe(data)
    if root is None:
        return {"status": "error", "geo": geo, "top_trends": []}

    trends = []
    for item in root.findall(".//item")[:10]:
        title = item.find("title")
        if title is not None and title.text:
            # 검색량 (ht:approx_traffic)
            traffic = item.find("{https://trends.google.com/trending/rss}approx_traffic")
            trends.append({
                "keyword": title.text.strip(),
                "approx_traffic": traffic.text.strip() if traffic is not None else "N/A",
            })

    return {
        "status": "ok",
        "geo": geo,
        "top_trends": trends,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. Tranco 랭킹 (무료 글로벌 트래픽 순위)
# ─────────────────────────────────────────────────────────────────────────────

def check_tranco_ranking(domains: list) -> dict:
    """Tranco 최신 랭킹 CSV에서 도메인 순위 조회."""
    result = {k: {"rank": None, "status": "not_found"} for k in domains}

    # Tranco latest list (1M 도메인, 주간 업데이트)
    # API: https://tranco-list.eu/api/ranks/domain/explodingtopics.com
    for domain in domains:
        try:
            api_url = f"https://tranco-list.eu/api/ranks/domain/{domain}"
            data = safe_fetch(api_url, timeout=10)
            if data:
                obj = json.loads(data.decode("utf-8", errors="ignore"))
                ranks = obj.get("ranks", [])
                if ranks:
                    # 가장 최신 순위 사용
                    latest = sorted(ranks, key=lambda x: x.get("date", ""), reverse=True)[0]
                    result[domain] = {
                        "rank": latest.get("rank"),
                        "date": latest.get("date"),
                        "status": "ok",
                    }
            time.sleep(SLEEP_BETWEEN)
        except Exception as e:
            log.warning("Tranco error for %s: %s", domain, e)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# 점수 계산 (우리 사이트와 비교)
# ─────────────────────────────────────────────────────────────────────────────

def calculate_benchmark_score(our_data: dict, competitors: list) -> dict:
    """경쟁 사이트 평균 대비 우리 사이트 상대 점수 계산."""
    competitor_data = [c for c in competitors if c["name"] != "TrendPulse (Our Site)"]

    # 평균 주간 포스팅 수
    avg_posts_per_week = 0
    valid_count = 0
    for c in competitor_data:
        rss = c.get("rss_analysis", {})
        if rss.get("status") == "ok" and rss.get("avg_posts_per_week", 0) > 0:
            avg_posts_per_week += rss["avg_posts_per_week"]
            valid_count += 1
    if valid_count > 0:
        avg_posts_per_week /= valid_count

    our_posts = our_data.get("rss_analysis", {}).get("avg_posts_per_week", 0)
    our_pages = our_data.get("sitemap_analysis", {}).get("total_urls", 0)

    avg_pages = 0
    valid_count = 0
    for c in competitor_data:
        sm = c.get("sitemap_analysis", {})
        if sm.get("status") == "ok" and sm.get("total_urls", 0) > 0:
            avg_pages += sm["total_urls"]
            valid_count += 1
    if valid_count > 0:
        avg_pages /= valid_count

    return {
        "content_velocity_ratio": round(our_posts / max(avg_posts_per_week, 0.1), 2),
        "page_count_ratio": round(our_pages / max(avg_pages, 1), 2),
        "avg_competitor_posts_per_week": round(avg_posts_per_week, 1),
        "avg_competitor_pages": int(avg_pages),
        "our_posts_per_week": our_posts,
        "our_total_pages": our_pages,
        "interpretation": _interpret_score(our_posts, avg_posts_per_week, our_pages, avg_pages),
    }


def _interpret_score(our_posts, avg_posts, our_pages, avg_pages) -> str:
    if avg_posts == 0:
        return "경쟁 사이트 RSS 없음 — 직접 비교 불가"
    ratio = our_posts / max(avg_posts, 0.1)
    if ratio >= 0.8:
        return "콘텐츠 업데이트 속도 — 경쟁 사이트와 대등"
    elif ratio >= 0.4:
        return "콘텐츠 업데이트 속도 — 경쟁 사이트 대비 약 50% 수준, 확대 필요"
    else:
        return "콘텐츠 업데이트 속도 — 경쟁 사이트 대비 낮음, 자동화 강화 필요"


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    start = time.time()
    log.info("벤치마크 리서치 시작")

    all_site_data = []
    our_site_data = None

    for target in TARGETS:
        log.info("분석 중: %s (%s)", target["name"], target["domain"])
        site_result = {
            "name": target["name"],
            "domain": target["domain"],
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

        # RSS 분석
        if target.get("rss"):
            log.info("  RSS 분석: %s", target["rss"])
            site_result["rss_analysis"] = analyze_rss(target["rss"])
            time.sleep(SLEEP_BETWEEN)

        # sitemap 분석
        if target.get("sitemap"):
            log.info("  sitemap 분석: %s", target["sitemap"])
            site_result["sitemap_analysis"] = analyze_sitemap(target["sitemap"])
            time.sleep(SLEEP_BETWEEN)

        # Common Crawl (우리 사이트 제외 — 너무 새로워서 인덱싱 안 됨)
        if target["domain"] != "global-trend-map.vercel.app":
            log.info("  Common Crawl 분석: %s", target["domain"])
            site_result["commoncrawl"] = analyze_commoncrawl(target["domain"])
            time.sleep(SLEEP_BETWEEN)

        all_site_data.append(site_result)

        if target["name"] == "TrendPulse (Our Site)":
            our_site_data = site_result

    # Tranco 순위
    log.info("Tranco 랭킹 조회")
    tranco = check_tranco_ranking(TRANCO_DOMAINS)
    time.sleep(SLEEP_BETWEEN)

    # Google Trends 샘플 (US만 — 비교 기준)
    log.info("Google Trends 샘플 수집")
    gt_sample = fetch_google_trends_sample("US")
    time.sleep(SLEEP_BETWEEN)

    # 점수 계산
    benchmark_score = {}
    if our_site_data:
        benchmark_score = calculate_benchmark_score(our_site_data, all_site_data)

    # 최종 출력
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(time.time() - start, 1),
        "sites": all_site_data,
        "tranco_rankings": tranco,
        "google_trends_sample_US": gt_sample,
        "benchmark_score": benchmark_score,
        "summary": {
            "competitors_analyzed": len([s for s in all_site_data if s["name"] != "TrendPulse (Our Site)"]),
            "data_sources_used": ["RSS", "sitemap.xml", "Common Crawl CDX", "Tranco API", "Google Trends RSS"],
            "cost": "$0 (모두 무료 소스)",
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    log.info("완료. 저장: %s (%.1f초)", OUTPUT_FILE, time.time() - start)

    # 콘솔 요약
    print("\n" + "=" * 50)
    print("=== 벤치마크 리서치 완료 ===")
    score = output["benchmark_score"]
    print(f"  분석 사이트: {output['summary']['competitors_analyzed']}개 경쟁사")
    print(f"  우리 주간 포스팅: {score.get('our_posts_per_week', 0)}")
    print(f"  경쟁사 평균: {score.get('avg_competitor_posts_per_week', 0)}")
    print(f"  콘텐츠 속도 비율: {score.get('content_velocity_ratio', 0)}")
    print(f"  판단: {score.get('interpretation', 'N/A')}")
    print("=" * 50)


if __name__ == "__main__":
    main()
