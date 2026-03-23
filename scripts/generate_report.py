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
# Search Console API
# ---------------------------------------------------------------------------

def fetch_gsc_data() -> dict:
    """Fetch SEO data from Google Search Console API. Returns {} on any failure."""
    try:
        from googleapiclient.discovery import build
        from google.oauth2 import service_account

        sa_json_str = os.environ.get("GA4_SERVICE_ACCOUNT_JSON", "").strip()
        site_url    = os.environ.get("GSC_SITE_URL", "").strip()

        if not sa_json_str or not site_url:
            logging.getLogger("generate_report").warning("GSC_SITE_URL or GA4_SERVICE_ACCOUNT_JSON not set")
            return {}

        sa_info = json.loads(sa_json_str)
        credentials = service_account.Credentials.from_service_account_info(
            sa_info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
        service = build("searchconsole", "v1", credentials=credentials, cache_discovery=False)

        from datetime import date, timedelta
        today     = date.today()
        end_date  = (today - timedelta(days=3)).isoformat()   # GSC has 3-day lag
        start_7d  = (today - timedelta(days=10)).isoformat()
        start_28d = (today - timedelta(days=31)).isoformat()

        def query(start, end, dimensions=None, row_limit=10):
            body = {"startDate": start, "endDate": end, "rowLimit": row_limit}
            if dimensions:
                body["dimensions"] = dimensions
            return service.searchanalytics().query(siteUrl=site_url, body=body).execute()

        # Summary (no dimension)
        s7  = query(start_7d,  end_date)
        s28 = query(start_28d, end_date)

        def parse_summary(r):
            rows = r.get("rows", [{}])
            row  = rows[0] if rows else {}
            return {
                "clicks":      int(row.get("clicks",      0)),
                "impressions": int(row.get("impressions", 0)),
                "ctr":         round(row.get("ctr", 0) * 100, 2),
                "position":    round(row.get("position", 0), 1),
            }

        # Top queries
        q7 = query(start_7d, end_date, dimensions=["query"], row_limit=10)
        top_queries = []
        for i, row in enumerate(q7.get("rows", [])[:10], 1):
            top_queries.append({
                "rank":        i,
                "query":       row["keys"][0],
                "clicks":      int(row.get("clicks", 0)),
                "impressions": int(row.get("impressions", 0)),
                "ctr":         round(row.get("ctr", 0) * 100, 1),
                "position":    round(row.get("position", 0), 1),
            })

        # Top pages
        p7 = query(start_7d, end_date, dimensions=["page"], row_limit=5)
        top_pages = []
        for i, row in enumerate(p7.get("rows", [])[:5], 1):
            page = row["keys"][0].replace(site_url, "") or "/"
            top_pages.append({
                "rank":    i,
                "page":    page,
                "clicks":  int(row.get("clicks", 0)),
                "ctr":     round(row.get("ctr", 0) * 100, 1),
            })

        result = {
            "7d":  parse_summary(s7),
            "28d": parse_summary(s28),
            "top_queries": top_queries,
            "top_pages":   top_pages,
        }
        logging.getLogger("generate_report").info("GSC fetched: %s", result.get("7d"))
        return result

    except ImportError:
        logging.getLogger("generate_report").warning("google-api-python-client not installed — skipping GSC")
        return {}
    except Exception as e:
        logging.getLogger("generate_report").warning("GSC fetch failed: %s", e)
        return {}


# ---------------------------------------------------------------------------
# GA4 Reporting API
# ---------------------------------------------------------------------------

def fetch_ga4_data() -> dict:
    """Fetch real traffic data from GA4 Data API. Returns {} on any failure."""
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
        from google.oauth2 import service_account

        property_id = os.environ.get("GA4_PROPERTY_ID", "").strip()
        sa_json_str = os.environ.get("GA4_SERVICE_ACCOUNT_JSON", "").strip()

        if not property_id or not sa_json_str:
            logging.getLogger("generate_report").warning("GA4_PROPERTY_ID or GA4_SERVICE_ACCOUNT_JSON not set")
            return {}

        sa_info = json.loads(sa_json_str)
        credentials = service_account.Credentials.from_service_account_info(
            sa_info, scopes=["https://www.googleapis.com/auth/analytics.readonly"]
        )
        client = BetaAnalyticsDataClient(credentials=credentials)

        def run(start_date, end_date):
            req = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                metrics=[
                    Metric(name="activeUsers"),
                    Metric(name="newUsers"),
                    Metric(name="sessions"),
                    Metric(name="screenPageViews"),
                    Metric(name="bounceRate"),
                    Metric(name="averageSessionDuration"),
                ],
            )
            resp = client.run_report(req)
            if not resp.rows:
                return {}
            v = resp.rows[0].metric_values
            mins, secs = divmod(int(float(v[5].value)), 60)
            return {
                "users":       int(v[0].value),
                "new_users":   int(v[1].value),
                "sessions":    int(v[2].value),
                "pageviews":   int(v[3].value),
                "bounce_rate": round(float(v[4].value) * 100, 1),
                "avg_session": f"{mins}m {secs:02d}s",
            }

        result = {"7d": run("7daysAgo", "today"), "30d": run("30daysAgo", "today")}
        logging.getLogger("generate_report").info("GA4 fetched: %s", result)
        return result

    except ImportError:
        logging.getLogger("generate_report").warning("google-analytics-data not installed — skipping GA4")
        return {}
    except Exception as e:
        logging.getLogger("generate_report").warning("GA4 fetch failed: %s", e)
        return {}

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

    # --- GA4 real traffic data ---
    ga4 = fetch_ga4_data()
    g7  = ga4.get("7d",  {})
    g30 = ga4.get("30d", {})

    def fmt_num(v, default="—"):
        return f"{v:,}" if isinstance(v, int) else default

    ga4_html = f"""
<div class="section">
  <div class="section-header">
    <span class="section-icon">📈</span>
    <h2 class="section-title">GA4 실제 트래픽</h2>
    <span class="section-badge">실시간 데이터</span>
  </div>
  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-value">{fmt_num(g7.get('users'))}</div>
      <div class="metric-label">활성 사용자 (7일)</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{fmt_num(g7.get('sessions'))}</div>
      <div class="metric-label">세션 (7일)</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{fmt_num(g7.get('pageviews'))}</div>
      <div class="metric-label">페이지뷰 (7일)</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{g7.get('bounce_rate', '—')}%</div>
      <div class="metric-label">이탈률 (7일)</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{g7.get('avg_session', '—')}</div>
      <div class="metric-label">평균 세션 시간 (7일)</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">{fmt_num(g7.get('new_users'))}</div>
      <div class="metric-label">신규 사용자 (7일)</div>
    </div>
  </div>
  <div class="sub-section" style="margin-top:14px;">
    <div class="sub-title">30일 누적</div>
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-value" style="font-size:1.3rem;">{fmt_num(g30.get('users'))}</div>
        <div class="metric-label">활성 사용자</div>
      </div>
      <div class="metric-card">
        <div class="metric-value" style="font-size:1.3rem;">{fmt_num(g30.get('sessions'))}</div>
        <div class="metric-label">세션</div>
      </div>
      <div class="metric-card">
        <div class="metric-value" style="font-size:1.3rem;">{fmt_num(g30.get('pageviews'))}</div>
        <div class="metric-label">페이지뷰</div>
      </div>
      <div class="metric-card">
        <div class="metric-value" style="font-size:1.3rem;">{fmt_num(g30.get('new_users'))}</div>
        <div class="metric-label">신규 사용자</div>
      </div>
    </div>
  </div>
</div>""" if g7 else """
<div class="section">
  <div class="section-header">
    <span class="section-icon">📈</span>
    <h2 class="section-title">GA4 실제 트래픽</h2>
  </div>
  <div class="note-box"><span class="note-icon">⚠️</span><span>GA4 데이터 없음 — GA4_PROPERTY_ID / GA4_SERVICE_ACCOUNT_JSON 환경변수 확인</span></div>
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

    # --- Search Console real SEO data ---
    gsc = fetch_gsc_data()
    gs7  = gsc.get("7d",  {})
    gs28 = gsc.get("28d", {})
    gsc_queries = gsc.get("top_queries", [])
    gsc_pages   = gsc.get("top_pages",   [])

    def fmt_pos(v, default="—"):
        return f"#{v}" if isinstance(v, (int, float)) and v > 0 else default

    if gs7:
        query_rows = "".join(
            f'<tr><td>{q["rank"]}</td><td style="max-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{q["query"]}</td>'
            f'<td>{q["clicks"]:,}</td><td>{q["impressions"]:,}</td><td>{q["ctr"]}%</td><td>#{q["position"]}</td></tr>'
            for q in gsc_queries
        ) or '<tr><td colspan="6" style="color:var(--dim);">데이터 없음 (아직 검색 노출 없음)</td></tr>'

        page_rows = "".join(
            f'<tr><td>{p["rank"]}</td><td style="max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{p["page"]}</td>'
            f'<td>{p["clicks"]:,}</td><td>{p["ctr"]}%</td></tr>'
            for p in gsc_pages
        ) or '<tr><td colspan="4" style="color:var(--dim);">데이터 없음</td></tr>'

        gsc_html = f"""
      <div class="note-box" style="background:rgba(16,185,129,0.08);border-color:rgba(16,185,129,0.3);">
        <span class="note-icon">✅</span>
        <span>Search Console API 연결됨 — 실제 SEO 데이터 자동 표시 중 (최근 7일 / 28일)</span>
      </div>
      <div class="metrics-grid" style="margin-top:14px;">
        <div class="metric-card">
          <div class="metric-value" style="font-size:1.4rem;">{gs7.get('clicks', 0):,}</div>
          <div class="metric-label">클릭수 (7일)</div>
        </div>
        <div class="metric-card">
          <div class="metric-value" style="font-size:1.4rem;">{gs7.get('impressions', 0):,}</div>
          <div class="metric-label">노출수 (7일)</div>
        </div>
        <div class="metric-card">
          <div class="metric-value" style="font-size:1.4rem;">{gs7.get('ctr', 0)}%</div>
          <div class="metric-label">평균 CTR (7일)</div>
        </div>
        <div class="metric-card">
          <div class="metric-value" style="font-size:1.4rem;">#{gs7.get('position', '—')}</div>
          <div class="metric-label">평균 순위 (7일)</div>
        </div>
        <div class="metric-card">
          <div class="metric-value" style="font-size:1.4rem;">{gs28.get('clicks', 0):,}</div>
          <div class="metric-label">클릭수 (28일)</div>
        </div>
        <div class="metric-card">
          <div class="metric-value" style="font-size:1.4rem;">{gs28.get('impressions', 0):,}</div>
          <div class="metric-label">노출수 (28일)</div>
        </div>
      </div>
      <div class="sub-section">
        <div class="sub-title">🔎 상위 검색 쿼리 (최근 7일)</div>
        <div class="table-wrap">
          <table class="data-table">
            <thead><tr><th>#</th><th>쿼리</th><th>클릭</th><th>노출수</th><th>CTR</th><th>순위</th></tr></thead>
            <tbody>{query_rows}</tbody>
          </table>
        </div>
      </div>
      <div class="sub-section">
        <div class="sub-title">📄 상위 페이지 (최근 7일)</div>
        <div class="table-wrap">
          <table class="data-table">
            <thead><tr><th>#</th><th>페이지</th><th>클릭</th><th>CTR</th></tr></thead>
            <tbody>{page_rows}</tbody>
          </table>
        </div>
      </div>"""
        gsc_badge = "Search Console — 실시간"
    else:
        gsc_html = """
      <div class="note-box">
        <span class="note-icon">💡</span>
        <span>GSC_SITE_URL / GA4_SERVICE_ACCOUNT_JSON 환경변수 확인 필요 — 현재 수동 확인 필요</span>
      </div>
      <div class="metrics-grid" style="margin-top:14px;">
        <div class="metric-card"><div class="metric-value" style="font-size:1.4rem;">—</div><div class="metric-label">전체 클릭수</div></div>
        <div class="metric-card"><div class="metric-value" style="font-size:1.4rem;">—</div><div class="metric-label">노출수</div></div>
        <div class="metric-card"><div class="metric-value" style="font-size:1.4rem;">—%</div><div class="metric-label">평균 CTR</div></div>
        <div class="metric-card"><div class="metric-value" style="font-size:1.4rem;">#—</div><div class="metric-label">평균 순위</div></div>
      </div>"""
        gsc_badge = "Search Console — 수동"

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
        "{{GA4_TRAFFIC_SECTION}}":  ga4_html,
        "{{GSC_SECTION}}":          gsc_html,
        "{{GSC_BADGE}}":            gsc_badge,
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
