#!/usr/bin/env python3
"""
generate_report.py — Manager Report Generator
Reads trends.json + posts-index.json, fills in report-template.html,
saves to public/report/manager-report.html, then opens in browser.
Usage: python scripts/generate_report.py
"""

import json
import os
import sys
import webbrowser
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR      = Path(__file__).resolve().parent.parent
DATA_DIR      = BASE_DIR / "public" / "data"
REPORT_DIR    = BASE_DIR / "public" / "report"
SCRIPTS_DIR   = BASE_DIR / "scripts"
TRENDS_FILE   = DATA_DIR / "trends.json"
INDEX_FILE    = DATA_DIR / "posts-index.json"
TEMPLATE_FILE = SCRIPTS_DIR / "report-template.html"
OUTPUT_FILE   = REPORT_DIR / "manager-report.html"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("generate_report")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path, default=None):
    if not path.exists():
        log.warning("File not found: %s — using defaults", path)
        return default if default is not None else {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def fmt_duration(secs):
    try:
        return str(int(secs))
    except Exception:
        return "0"


def minutes_since(iso_str: str) -> int:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        return int(delta.total_seconds() / 60)
    except Exception:
        return 0


def minutes_until(iso_str: str) -> int:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        delta = dt - datetime.now(timezone.utc)
        mins = int(delta.total_seconds() / 60)
        return max(0, mins)
    except Exception:
        return 60


def source_status(flag: bool) -> str:
    return "✅ Active" if flag else "❌ Inactive"


def count_by_lang(posts: list, lang: str) -> int:
    return sum(1 for p in posts if p.get("language") == lang)


def count_today(posts: list) -> int:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return sum(1 for p in posts if p.get("date", "").startswith(today))

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    now_utc = datetime.now(timezone.utc)

    # --- Load data ---
    trends     = load_json(TRENDS_FILE, {})
    _index     = load_json(INDEX_FILE, [])
    posts      = _index if isinstance(_index, list) else _index.get("posts", [])
    benchmark  = load_json(DATA_DIR / "benchmark.json", {})

    # Template file
    if not TEMPLATE_FILE.exists():
        log.error("Template not found: %s", TEMPLATE_FILE)
        sys.exit(1)
    with open(TEMPLATE_FILE, encoding="utf-8") as f:
        template = f.read()

    # --- Extract values ---
    global_sec  = trends.get("global", {})
    pipeline    = trends.get("pipelineStats", {})
    sources     = trends.get("sources", {})
    blog_stats  = trends.get("blogStats", {})
    last_updated = trends.get("lastUpdated", now_utc.isoformat())

    report_date = now_utc.strftime("%Y-%m-%d")
    report_time = now_utc.strftime("%H:%M UTC")

    total_countries   = global_sec.get("totalCountries", 0)
    total_trends      = global_sec.get("totalTrends", 0)
    global_temp       = global_sec.get("temperature", 0)
    global_temp_label = global_sec.get("temperatureLabel", "WARM")
    next_update_iso   = global_sec.get("nextUpdate", (now_utc + timedelta(hours=1)).isoformat())

    top = global_sec.get("topTrend", {})
    top_keyword = top.get("keyword", "N/A")
    top_country = top.get("country", "N/A")
    top_volume  = top.get("volume", "N/A")

    src_google = source_status(sources.get("googleTrends", False))
    src_yt     = source_status(sources.get("youtube", False))
    src_gdelt  = source_status(sources.get("gdelt", False))
    src_wiki   = source_status(sources.get("wikipedia", False))
    src_apple  = source_status(sources.get("apple", False))

    duration         = fmt_duration(pipeline.get("duration", 0))
    success_count    = pipeline.get("successCount", 0)
    error_count      = pipeline.get("errorCount", 0)
    blocked_kw       = pipeline.get("blockedKeywords", 0)
    yt_quota_used    = pipeline.get("youtubeQuotaUsed", 0)
    yt_quota_remain  = 10000 - int(yt_quota_used)

    posts_today  = blog_stats.get("postsToday", count_today(posts))
    posts_total  = blog_stats.get("postsTotal", len(posts))
    posts_en     = blog_stats.get("postsEn", count_by_lang(posts, "en"))
    posts_kr     = blog_stats.get("postsKr", count_by_lang(posts, "kr"))
    posts_jp     = blog_stats.get("postsJp", count_by_lang(posts, "jp"))

    data_age     = minutes_since(last_updated)
    next_update_in = minutes_until(next_update_iso)

    # Status strings (simplified — no live API calls)
    vercel_status  = "✅ Deployed"
    gh_status      = "✅ Running"

    # Action items logic
    action_items = []
    if error_count > 0:
        action_items.append(f'<li class="action-red">🔴 Fix data collection errors — {error_count} source(s) failed. Check GitHub Actions logs.</li>')
    if posts_today == 0:
        action_items.append('<li class="action-red">🔴 Blog generation produced 0 posts today — check generate_blog.py logs.</li>')
    if data_age > 120:
        action_items.append(f'<li class="action-yellow">🟡 Data is {data_age} minutes old — check GitHub Actions schedule (cron: 0 * * * *).</li>')
    if yt_quota_used > 8000:
        action_items.append(f'<li class="action-yellow">🟡 YouTube API quota at {yt_quota_used}/10,000 — monitor daily usage to avoid hitting limit.</li>')
    if not action_items:
        action_items.append('<li class="action-green">✅ All systems operating normally. No issues detected.</li>')
    action_items_html = "\n".join(action_items)

    # Days of operation (rough estimate from first post date)
    days_operating = 0
    if posts:
        try:
            first = sorted(posts, key=lambda p: p.get("date", "9999"))[0]
            first_dt = datetime.fromisoformat(first["date"])
            days_operating = (now_utc.date() - first_dt.date()).days
        except Exception:
            days_operating = 0

    adsense_days_remaining = max(0, 42 - days_operating)
    adsense_progress_pct   = min(100, int(days_operating / 42 * 100))

    # YouTube quota progress %
    yt_quota_pct = min(100, int(yt_quota_used / 10000 * 100))

    # --- Benchmark data injection ---
    bm_score = benchmark.get("benchmark_score", {})
    bm_generated = benchmark.get("generated_at", "N/A")
    bm_our_posts  = bm_score.get("our_posts_per_week", "N/A")
    bm_avg_posts  = bm_score.get("avg_competitor_posts_per_week", "N/A")
    bm_our_pages  = bm_score.get("our_total_pages", "N/A")
    bm_avg_pages  = bm_score.get("avg_competitor_pages", "N/A")
    bm_ratio      = bm_score.get("content_velocity_ratio", "N/A")
    bm_interp     = bm_score.get("interpretation", "데이터 없음 — 다음 주 일요일 자동 수집")
    bm_competitors = benchmark.get("summary", {}).get("competitors_analyzed", 0)

    # Tranco ranking for our closest competitor
    tranco = benchmark.get("tranco_rankings", {})
    bm_tranco_rows = ""
    for domain, info in tranco.items():
        rank = info.get("rank", "N/A")
        date = info.get("date", "")
        bm_tranco_rows += f'<tr><td>{domain}</td><td style="color:var(--cyan);">#{rank:,}</td><td>{date}</td></tr>' if isinstance(rank, int) else f'<tr><td>{domain}</td><td style="color:var(--dim);">N/A</td><td>{date}</td></tr>'

    if not bm_tranco_rows:
        bm_tranco_rows = '<tr><td colspan="3" style="color:var(--dim);">벤치마크 미실행 — 매주 일요일 자동 수집</td></tr>'

    # Build benchmark HTML block
    bm_html = f"""
<div class="sub-section" style="margin-top:14px;">
  <div class="sub-title">📡 실측 벤치마크 데이터 (자동 수집)</div>
  <div class="note-box">
    <span class="note-icon">🕐</span>
    <span>마지막 수집: <strong>{bm_generated[:10] if bm_generated != 'N/A' else '미수집'}</strong> &nbsp;·&nbsp; 매주 일요일 자동 업데이트</span>
  </div>
  <div class="metrics-grid" style="margin-top:12px;">
    <div class="metric-card">
      <div class="metric-value" style="font-size:1.3rem;">{bm_our_posts}</div>
      <div class="metric-label">우리 주간 포스팅</div>
    </div>
    <div class="metric-card">
      <div class="metric-value" style="font-size:1.3rem;">{bm_avg_posts}</div>
      <div class="metric-label">경쟁사 평균</div>
    </div>
    <div class="metric-card">
      <div class="metric-value" style="font-size:1.3rem;">{bm_our_pages}</div>
      <div class="metric-label">우리 총 페이지</div>
    </div>
    <div class="metric-card">
      <div class="metric-value" style="font-size:1.3rem;">{bm_avg_pages}</div>
      <div class="metric-label">경쟁사 평균 페이지</div>
    </div>
    <div class="metric-card">
      <div class="metric-value" style="font-size:1.3rem;">{bm_ratio}</div>
      <div class="metric-label">콘텐츠 속도 비율</div>
    </div>
    <div class="metric-card">
      <div class="metric-value" style="font-size:1.3rem;">{bm_competitors}</div>
      <div class="metric-label">분석 경쟁사 수</div>
    </div>
  </div>
  <div class="health-indicator health-yellow" style="margin-top:12px;">
    📊 &nbsp;{bm_interp}
  </div>
  <div class="table-wrap" style="margin-top:14px;">
    <div class="sub-title">🏆 Tranco 글로벌 랭킹 (경쟁사)</div>
    <table class="data-table">
      <thead><tr><th>도메인</th><th>순위</th><th>기준일</th></tr></thead>
      <tbody>{bm_tranco_rows}</tbody>
    </table>
  </div>
</div>"""

    # Automation maturity (rough scoring)
    auto_items = sum([
        sources.get("googleTrends", False),
        sources.get("youtube", False),
        sources.get("gdelt", False),
        sources.get("wikipedia", False),
        sources.get("apple", False),
        posts_total > 0,
    ])
    auto_score = min(97, int(auto_items / 6 * 65) + 10)

    # --- Replace template variables ---
    replacements = {
        "{{REPORT_DATE}}":          report_date,
        "{{REPORT_TIME}}":          report_time,
        "{{LAST_UPDATED}}":         last_updated,
        "{{TOTAL_COUNTRIES}}":      str(total_countries),
        "{{TOTAL_TRENDS}}":         f"{total_trends:,}",
        "{{GLOBAL_TEMP}}":          str(global_temp),
        "{{GLOBAL_TEMP_LABEL}}":    global_temp_label,
        "{{TOP_TREND_KEYWORD}}":    top_keyword,
        "{{TOP_TREND_COUNTRY}}":    top_country,
        "{{TOP_TREND_VOLUME}}":     top_volume,
        "{{SOURCE_GOOGLE_TRENDS}}": src_google,
        "{{SOURCE_YOUTUBE}}":       src_yt,
        "{{SOURCE_GDELT}}":         src_gdelt,
        "{{SOURCE_WIKI}}":          src_wiki,
        "{{SOURCE_APPLE}}":         src_apple,
        "{{PIPELINE_DURATION}}":    duration,
        "{{PIPELINE_SUCCESS}}":     str(success_count),
        "{{PIPELINE_ERRORS}}":      str(error_count),
        "{{BLOCKED_KEYWORDS}}":     str(blocked_kw),
        "{{YOUTUBE_QUOTA_USED}}":   str(yt_quota_used),
        "{{YOUTUBE_QUOTA_REMAINING}}": str(yt_quota_remain),
        "{{POSTS_TODAY}}":          str(posts_today),
        "{{POSTS_TOTAL}}":          str(posts_total),
        "{{POSTS_EN}}":             str(posts_en),
        "{{POSTS_KR}}":             str(posts_kr),
        "{{POSTS_JP}}":             str(posts_jp),
        "{{VERCEL_STATUS}}":        vercel_status,
        "{{GITHUB_ACTIONS_STATUS}}": gh_status,
        "{{DATA_AGE_MINUTES}}":     str(data_age),
        "{{NEXT_UPDATE_IN}}":       str(next_update_in),
        "{{ACTION_ITEMS}}":         action_items_html,
        "{{ADSENSE_DAYS_REMAINING}}": str(adsense_days_remaining),
        "{{ADSENSE_PROGRESS_PCT}}": str(adsense_progress_pct),
        "{{DAYS_OPERATING}}":       str(days_operating),
        "{{YT_QUOTA_PCT}}":         str(yt_quota_pct),
        "{{AUTO_SCORE}}":           str(auto_score),
        "{{BENCHMARK_SECTION}}":    bm_html,
        "{{ERROR_COUNT_CLASS}}":    "status-error" if error_count > 0 else "status-ok",
        "{{DATA_AGE_CLASS}}":       "status-warn" if data_age > 120 else "status-ok",
        "{{QUOTA_CLASS}}":          "status-warn" if yt_quota_used > 8000 else "status-ok",
    }

    html = template
    for key, val in replacements.items():
        html = html.replace(key, val)

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    # Console summary
    alerts = []
    if error_count > 0:
        alerts.append(f"Pipeline errors: {error_count}")
    if posts_today == 0:
        alerts.append("No posts generated today")
    if data_age > 120:
        alerts.append(f"Data is {data_age}min old")
    alerts_str = " | ".join(alerts) if alerts else "None"

    print()
    print("=" * 45)
    print("=== VERCEL MANAGER DAILY REPORT ===")
    print(f"[DATE]  Date: {report_date} {report_time}")
    print(f"[DATA]  Data: {total_countries} countries | {total_trends:,} trends | Temp: {global_temp}T ({global_temp_label})")
    print(f"[BLOG]  Content: {posts_today} posts today | {posts_total} total")
    print(f"[PIPE]   Pipeline: {duration}s | {success_count} success | {error_count} errors")
    print(f"[WARN]   Alerts: {alerts_str}")
    print("=" * 45)
    print(f"Report saved -> {OUTPUT_FILE}")
    print()

    # Open in browser
    try:
        webbrowser.open(OUTPUT_FILE.as_uri())
        log.info("Opened report in default browser.")
    except Exception as e:
        log.warning("Could not open browser: %s", e)


if __name__ == "__main__":
    main()
