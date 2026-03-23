#!/usr/bin/env python3
"""
generate_blog.py — SEO-Optimized Blog Post Generator (Data-Driven, No API Cost)

Strategy:
  - 1 topic/day: Spotlight #1 (global.topTrend.keywordEn)
  - Skip if same topic published within SKIP_WINDOW_DAYS
  - 8 languages per day: EN, ZH, ES, PT, FR, DE, KR, JP
  - SEO: H2/H3 hierarchy, FAQ section, 1500+ words, YouTube + Google Trends links
"""

import json
import logging
import re
import textwrap
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR    = Path(__file__).resolve().parent.parent
DATA_DIR    = BASE_DIR / "public" / "data"
BLOG_DIR    = BASE_DIR / "public" / "blog"
TRENDS_FILE = DATA_DIR / "trends.json"
INDEX_FILE  = DATA_DIR / "posts-index.json"

BLOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("generate_blog")

SITE_URL         = "https://global-trend-map-web.vercel.app"
SKIP_WINDOW_DAYS = 3
ALL_LANGS        = ["en", "zh", "es", "pt", "fr", "de", "kr", "jp"]

LANG_META = {
    "en": {"label": "English",    "hreflang": "en", "locale": "en_US"},
    "zh": {"label": "\u4e2d\u6587",       "hreflang": "zh", "locale": "zh_CN"},
    "es": {"label": "Espa\u00f1ol",   "hreflang": "es", "locale": "es_ES"},
    "pt": {"label": "Portugu\u00eas", "hreflang": "pt", "locale": "pt_BR"},
    "fr": {"label": "Fran\u00e7ais",  "hreflang": "fr", "locale": "fr_FR"},
    "de": {"label": "Deutsch",   "hreflang": "de", "locale": "de_DE"},
    "kr": {"label": "\ud55c\uad6d\uc5b4",      "hreflang": "ko", "locale": "ko_KR"},
    "jp": {"label": "\u65e5\u672c\u8a9e",      "hreflang": "ja", "locale": "ja_JP"},
}

CATEGORY_LABELS = {
    "en": {"sports": "Sports", "tech": "Technology", "music": "Music",
           "news": "News", "movies": "Entertainment", "finance": "Finance", "": "Trending"},
    "zh": {"sports": "\u4f53\u80b2", "tech": "\u79d1\u6280", "music": "\u97f3\u4e50",
           "news": "\u65b0\u95fb", "movies": "\u5a31\u4e50", "finance": "\u91d1\u878d", "": "\u70ed\u641c"},
    "es": {"sports": "Deportes", "tech": "Tecnolog\u00eda", "music": "M\u00fasica",
           "news": "Noticias", "movies": "Entretenimiento", "finance": "Finanzas", "": "Tendencias"},
    "pt": {"sports": "Esportes", "tech": "Tecnologia", "music": "M\u00fasica",
           "news": "Not\u00edcias", "movies": "Entretenimento", "finance": "Finan\u00e7as", "": "Tend\u00eancias"},
    "fr": {"sports": "Sport", "tech": "Technologie", "music": "Musique",
           "news": "Actualit\u00e9s", "movies": "Divertissement", "finance": "Finance", "": "Tendances"},
    "de": {"sports": "Sport", "tech": "Technologie", "music": "Musik",
           "news": "Nachrichten", "movies": "Unterhaltung", "finance": "Finanzen", "": "Trends"},
    "kr": {"sports": "\uc2a4\ud3ec\uce20", "tech": "\uae30\uc220", "music": "\uc74c\uc545",
           "news": "\ub274\uc2a4", "movies": "\uc5d4\ud130\ud14c\uc778\uba3c\ud2b8", "finance": "\uae08\uc735", "": "\ud2b8\ub80c\ub4dc"},
    "jp": {"sports": "\u30b9\u30dd\u30fc\u30c4", "tech": "\u30c6\u30af\u30ce\u30ed\u30b8\u30fc",
           "music": "\u97f3\u697d", "news": "\u30cb\u30e5\u30fc\u30b9",
           "movies": "\u30a8\u30f3\u30bf\u30fc\u30c6\u30a4\u30f3\u30e1\u30f3\u30c8",
           "finance": "\u30d5\u30a1\u30a4\u30ca\u30f3\u30b9", "": "\u30c8\u30ec\u30f3\u30c9"},
}

# ---------------------------------------------------------------------------
# Template factory
# ---------------------------------------------------------------------------

def _mk_templates():

    # ── Shared helpers ───────────────────────────────────────────────────────

    def _temp_desc_en(t):
        if t >= 90: return "an exceptionally viral trend with massive global reach"
        if t >= 75: return "a very hot trend with strong international momentum"
        if t >= 60: return "a warm and growing trend gaining traction worldwide"
        if t >= 40: return "a rising trend picking up search interest globally"
        return "an emerging topic beginning to capture global attention"

    def _why_context_en(cat, kw):
        if cat == "music":
            return (
                f"Music trends explode when artists release new content, receive major award recognition, "
                f"or go viral across social platforms. **\"{kw}\"** has achieved exactly that, "
                f"combining streaming platform momentum with fan-driven sharing to create a self-amplifying "
                f"surge across borders. When a track reaches the top of global charts simultaneously, "
                f"it signals both cultural resonance and the power of connected digital audiences. "
                f"The multi-country search pattern confirms this is a genuinely global music moment, "
                f"not a regional phenomenon limited to one market."
            )
        elif cat == "movies":
            return (
                f"Entertainment trends peak around major trailer drops, theatrical releases, or award "
                f"ceremony moments. **\"{kw}\"** has captured worldwide audience attention today, "
                f"reflecting how the global film industry unites viewers across languages and cultures. "
                f"When a title trends simultaneously across dozens of countries, it points to either "
                f"a highly anticipated release or a viral marketing moment that has crossed geographic "
                f"boundaries and entered mainstream global conversation."
            )
        elif cat == "tech":
            return (
                f"Technology topics trend when significant product launches, major announcements, or "
                f"controversies emerge in the tech world. **\"{kw}\"** has captured global attention today, "
                f"suggesting either a major product reveal, an industry development, or a viral tech story "
                f"that has spread far beyond its original audience. The multi-country search pattern "
                f"indicates a globally relevant tech event that resonates across different markets and "
                f"user communities simultaneously."
            )
        elif cat == "sports":
            return (
                f"Sports trends surge around major match results, tournament milestones, or breaking "
                f"news about high-profile athletes. The global search activity around **\"{kw}\"** "
                f"suggests a significant sporting event or announcement resonating across international "
                f"markets. Sports have a unique ability to transcend language barriers and generate "
                f"simultaneous engagement worldwide, making multi-country trending a strong signal of "
                f"a genuinely important moment in global athletics."
            )
        elif cat == "finance":
            return (
                f"Financial topics trend during market volatility, major economic announcements, or "
                f"viral investment stories. The global interest in **\"{kw}\"** today may reflect "
                f"economic uncertainty, a market-moving event, or a financial story that has crossed "
                f"from niche investor circles into mainstream public consciousness. Multi-country "
                f"trending in financial topics often signals broader macroeconomic significance that "
                f"affects people beyond just investors and traders."
            )
        else:
            return (
                f"News and information trends reflect the collective curiosity of millions of people "
                f"searching simultaneously across the globe. **\"{kw}\"** has captured international "
                f"attention today, suggesting a significant development, breaking story, or viral "
                f"moment that resonates across cultures and borders. When a single topic trends in "
                f"dozens of countries at once, it typically represents something with universal "
                f"relevance or deep cultural impact that transcends geographic boundaries."
            )

    def _source_label_en(source):
        return {
            "youtube":       "YouTube Trending",
            "apple_music":   "Apple Music Charts",
            "itunes_movies": "iTunes Movie Charts",
            "google":        "Google Search Trends",
            "gdelt":         "Global News (GDELT)",
            "espn":          "ESPN Sports",
            "marketwatch":   "MarketWatch Finance",
        }.get(source or "", "Global Trend Tracker")

    # ── English ──────────────────────────────────────────────────────────────

    def en_title(c):
        return f"Why Is \"{c['keyword_en']}\" Trending Globally? {c['date_str']} Analysis"

    def en_excerpt(c):
        return (
            f"\"{c['keyword_en']}\" is the #1 global search trend on {c['date_str']}, "
            f"surging across {len(c['countries_list'])} countries with {c['volume']} searches "
            f"in {c['top_country_name']} alone. Here's why the world is searching for it."
        )

    def en_body(c):
        countries_md = "\n".join(f"- {f} **{n}**" for f, n in c["countries_list"])
        rising_md = "\n".join(
            f"- **{kw}** \u2014 {cn} ({vol})" for kw, cn, vol in c["rising_list"]
        ) or "- No additional rising trend data at this time."
        cat_md = "\n".join(
            f"- **{k.capitalize()}**: {v} active trends"
            for k, v in sorted(c["cat_breakdown"].items(), key=lambda x: -x[1]) if v > 0
        ) or "- Category data updating..."

        yt_line = (
            f"\n\n\U0001f4fa **Watch on YouTube:** [{c['keyword_en']}]({c['youtube_url']})\n"
            if c.get("youtube_url") else ""
        )
        why = _why_context_en(c["category"], c["keyword_en"])
        tdesc = _temp_desc_en(c["top_temperature"])
        src = _source_label_en(c.get("source"))
        top_flag = c["countries_list"][0][0] if c["countries_list"] else "\U0001f310"
        other_countries = ", ".join(n for _, n in c["countries_list"][1:4]) if len(c["countries_list"]) > 1 else "multiple regions"

        return textwrap.dedent(f"""\
**\"{c['keyword_en']}\"** is the #1 trending search worldwide on {c['date_str']}, \
generating intense activity across {len(c['countries_list'])} countries simultaneously. \
The surge is being led by **{c['top_country_name']}** {top_flag}, where {c['volume']} searches \
have been recorded, making it today's undisputed epicenter of global digital interest.

Whether you discovered this topic through social media, news headlines, or a friend's message, \
you're part of a worldwide moment. Below, we break down exactly why **\"{c['keyword_en']}\"** \
is capturing the world's attention right now — backed by real-time data from \
{c['total_countries']} countries.

---

## What Is "{c['keyword_en']}"?

**\"{c['keyword_en']}\"** is a {c['category_label'].lower()} topic that has surged to the top \
of global search rankings today. It belongs to the **{c['category_label']}** category and carries \
a Trend Temperature of **{c['top_temperature']}\u00b0T** on TrendPulse's 0\u2013100 scale \
\u2014 indicating {tdesc}.

The topic originated primarily in **{c['top_country_name']}** but has rapidly spread across borders, \
gaining measurable traction in {other_countries}, and beyond. \
This cross-border momentum is what separates a genuinely global trend from a local news story.

### Key Statistics at a Glance

| Metric | Value |
|---|---|
| Search Volume | {c['volume']} |
| Trend Temperature | {c['top_temperature']}\u00b0T / 100 |
| Category | {c['category_label']} |
| Leading Country | {top_flag} {c['top_country_name']} |
| Countries Tracking | {len(c['countries_list'])} / {c['total_countries']} |
| Data Source | {src} |
| Last Updated | {c['date_str']} |{yt_line}
---

## Why Is "{c['keyword_en']}" Trending Today?

{why}

Beyond category-specific factors, the scale of **\"{c['keyword_en']}\"** today is remarkable. \
Trending across {len(c['countries_list'])} countries simultaneously means this topic has achieved \
what analysts call "escape velocity" \u2014 the point at which organic sharing and media coverage \
reinforce each other in a self-amplifying loop. At {c['top_temperature']}\u00b0T, this ranks among \
the most intense trends tracked across our network today.

\U0001f50d **Verify this trend yourself:** \
[Explore "{c['keyword_en']}" on Google Trends]({c['google_trends_url']})

---

## Which Countries Are Searching for "{c['keyword_en']}"?

TrendPulse monitors search activity across **{c['total_countries']} countries** in real time. \
Here are the countries where **\"{c['keyword_en']}\"** is generating active search interest today:

{countries_md}

### Where the Signal Is Strongest

The dominant search signal comes from **{c['top_country_name']}**, leading the global conversation \
around **\"{c['keyword_en']}\"**. The spread across {len(c['countries_list'])} countries indicates \
this topic has transcended local interest and entered the realm of genuine global culture.

When a trend reaches this level of geographic spread, it signals strong media coverage, \
viral social sharing, or a culturally significant event resonating with audiences worldwide \
\u2014 regardless of language or location.

\U0001f5fa\ufe0f **See it on the map:** \
[View the Interactive Global Trend Map]({c['site_url']})

---

## Trend Data & Deep Dive Statistics

Full statistical breakdown of the **\"{c['keyword_en']}\"** trend as of {c['date_str']}:

| Metric | Value |
|---|---|
| Peak Search Volume | {c['volume']} |
| Trend Temperature | {c['top_temperature']}\u00b0T |
| Temperature Meaning | {tdesc.capitalize()} |
| Primary Category | {c['category_label']} |
| Global Reach | {len(c['countries_list'])} countries |
| Total Countries Monitored | {c['total_countries']} |

**About Trend Temperature:** TrendPulse's proprietary score (0\u2013100) combines search volume, \
geographic spread, and velocity into a single intensity metric. A score of {c['top_temperature']}\u00b0T \
means {tdesc}.

---

## What Else Is Trending Right Now?

While **\"{c['keyword_en']}\"** dominates the global stage, these topics are also rising fast \
across our {c['total_countries']}-country network:

{rising_md}

Each of these represents a real-time signal from millions of people searching simultaneously. \
The variety of topics reflects the breadth of global digital conversation happening right now.

\U0001f4ca **Explore all live trends:** \
[Open the Full Global Trend Map]({c['site_url']})

---

## Today's Global Search Landscape by Category

How today's trending topics break down across major content categories:

{cat_md}

This snapshot captures what millions of people across {c['total_countries']} countries are \
actively searching for right now. The **{c['category_label']}** category is particularly active \
today, driven in large part by **\"{c['keyword_en']}\"** and closely related searches.

---

## Frequently Asked Questions

### What is "{c['keyword_en']}"?

**\"{c['keyword_en']}\"** is currently the #1 trending search worldwide, tracked across \
{len(c['countries_list'])} countries on {c['date_str']}. It falls under the {c['category_label']} \
category and is generating {c['volume']} searches in the leading country alone. \
Visit the [live trend map]({c['site_url']}) to explore real-time geographic data.

### Why is "{c['keyword_en']}" trending today?

**\"{c['keyword_en']}\"** reached the top of global searches due to rapid spread across \
{len(c['countries_list'])} countries, with a Trend Temperature of {c['top_temperature']}\u00b0T \u2014 \
indicating {tdesc}. This multi-country surge typically signals a viral event, breaking story, \
or major cultural moment. Check [Google Trends]({c['google_trends_url']}) for historical context.

### Which country is searching for "{c['keyword_en']}" the most?

According to TrendPulse real-time data, **{c['top_country_name']}** {top_flag} is the leading \
country for **\"{c['keyword_en']}\"** searches today, with {c['volume']} queries recorded. \
The trend has since spread to {max(0, len(c['countries_list']) - 1)} additional countries. \
Explore the [interactive map]({c['site_url']}) for the full geographic breakdown.

### How does TrendPulse measure global trend intensity?

TrendPulse collects real-time data from **{c['total_countries']} countries** every hour, \
aggregating signals from Google Search Trends, YouTube, Apple Music Charts, and global news feeds. \
Our **Trend Temperature** score (0\u2013100) combines search volume, geographic spread, and velocity \
to produce a single intensity metric for each trending topic worldwide.

### Where can I explore more global trend data?

You can explore live global trends \u2014 including country-by-country breakdowns, category filters, \
and hourly updates \u2014 at [Global Trend Map]({c['site_url']}). \
We track trends across {c['total_countries']} countries, updated every hour. \
Browse our [daily trend blog]({c['site_url']}/blog) for in-depth analyses.

---

## Stay Ahead of Every Global Trend

**\"{c['keyword_en']}\"** is one of hundreds of trends being monitored right now across \
{c['total_countries']} countries. Whether you're a researcher, journalist, content creator, \
marketer, or simply curious about what the world is thinking \u2014 TrendPulse gives you \
instant access to the global pulse.

\U0001f449 **[Explore the Live Global Trend Map]({c['site_url']})** \u2014 updated every hour

\U0001f4f0 **[Read more trend analyses]({c['site_url']}/blog)** \u2014 daily breakdowns of the world's #1 trends

*Data collected on {c['date_str']}. All trends refresh hourly. \
Trend Temperature scores reflect data at time of collection.*
""")

    # ── Chinese (Simplified) ──────────────────────────────────────────────────

    def zh_title(c):
        return f"\"{c['keyword_en']}\"\u4e3a\u4f55\u5728\u5168\u7403\u70ed\u641c\uff1f{c['date_str']}\u8d8b\u52bf\u6df1\u5ea6\u5206\u6790"

    def zh_excerpt(c):
        return (
            f"\"{c['keyword_en']}\"\u662f{c['date_str']}\u5168\u7403\u641c\u7d22\u91cf\u6392\u540d\u7b2c\u4e00\uff0c"
            f"\u5728{len(c['countries_list'])}\u4e2a\u56fd\u5bb6\u5f15\u53d1\u641c\u7d22\u70ed\u6f6e\uff0c"
            f"\u4ec5\u5728{c['top_country_name']}\u5c31\u4ea7\u751f\u4e86{c['volume']}\u6b21\u641c\u7d22\u3002"
            f"\u672c\u6587\u5168\u9762\u89e3\u6790\u8fd9\u4e00\u5168\u7403\u70ed\u70b9\u7684\u6210\u56e0\u3002"
        )

    def zh_body(c):
        countries_md = "\n".join(f"- {f} **{n}**" for f, n in c["countries_list"])
        rising_md = "\n".join(
            f"- **{kw}** \u2014 {cn}\uff08{vol}\uff09" for kw, cn, vol in c["rising_list"]
        ) or "- \u6682\u65e0\u5176\u4ed6\u4e0a\u5347\u8d8b\u52bf\u6570\u636e"
        cat_md = "\n".join(
            f"- **{k.capitalize()}**\uff1a{v} \u4e2a\u70ed\u641c\u8bdd\u9898"
            for k, v in sorted(c["cat_breakdown"].items(), key=lambda x: -x[1]) if v > 0
        ) or "- \u5206\u7c7b\u6570\u636e\u66f4\u65b0\u4e2d..."
        yt_line = (
            f"\n\n\U0001f4fa **\u5728YouTube\u4e0a\u89c2\u770b\uff1a** [{c['keyword_en']}]({c['youtube_url']})\n"
            if c.get("youtube_url") else ""
        )
        top_flag = c["countries_list"][0][0] if c["countries_list"] else "\U0001f310"
        other_countries = "\u3001".join(n for _, n in c["countries_list"][1:4]) if len(c["countries_list"]) > 1 else "\u591a\u4e2a\u5730\u533a"

        t = c["top_temperature"]
        if t >= 90:
            tdesc = "\u8d85\u7ea7\u75c5\u6bd2\u5f0f\u4f20\u64ad\u8d8b\u52bf\uff0c\u5177\u6709\u5de8\u5927\u7684\u5168\u7403\u5f71\u54cd\u529b"
        elif t >= 75:
            tdesc = "\u975e\u5e38\u70ed\u95e8\u7684\u8d8b\u52bf\uff0c\u5728\u56fd\u9645\u4e0a\u5177\u6709\u5f3a\u52b2\u52bf\u5934"
        elif t >= 60:
            tdesc = "\u6e29\u70ed\u4e14\u4e0d\u65ad\u589e\u957f\u7684\u8d8b\u52bf\uff0c\u5728\u5168\u7403\u8303\u56f4\u5185\u6301\u7eed\u83b7\u5f97\u5173\u6ce8"
        elif t >= 40:
            tdesc = "\u4e0a\u5347\u8d8b\u52bf\uff0c\u5728\u5168\u7403\u8303\u56f4\u5185\u5f15\u53d1\u641c\u7d22\u5174\u8da3"
        else:
            tdesc = "\u65b0\u5174\u8bdd\u9898\uff0c\u5f00\u59cb\u5f15\u53d1\u5168\u7403\u5173\u6ce8"

        src = {
            "youtube": "YouTube \u8d8b\u52bf",
            "apple_music": "Apple Music \u699c\u5355",
            "itunes_movies": "iTunes \u7535\u5f71\u699c\u5355",
            "google": "Google \u641c\u7d22\u8d8b\u52bf",
            "gdelt": "\u5168\u7403\u65b0\u95fb (GDELT)",
            "espn": "ESPN \u4f53\u80b2",
            "marketwatch": "MarketWatch \u91d1\u878d",
        }.get(c.get("source") or "", "\u5168\u7403\u8d8b\u52bf\u8ffd\u8e2a\u5668")

        cat = c["category"]
        kw = c["keyword_en"]
        if cat == "music":
            why = (
                f"\u5f53\u827a\u4eba\u53d1\u5e03\u65b0\u5185\u5bb9\u3001\u83b7\u5f97\u91cd\u8981\u5956\u9879\u8ba4\u53ef\u6216\u5728\u793e\u4ea4\u5e73\u53f0\u4e0a\u75af\u4f20\u65f6\uff0c\u97f3\u4e50\u8d8b\u52bf\u4fbf\u4f1a\u7206\u53d1\u3002**\"{kw}\"** \u6b63\u662f\u5982\u6b64\uff0c\u5c06\u6d41\u5a92\u4f53\u5e73\u53f0\u7684\u52bf\u5934\u4e0e\u7c89\u4e1d\u9a71\u52a8\u7684\u5206\u4eab\u7ed3\u5408\u5728\u4e00\u8d77\uff0c\u5f62\u6210\u4e86\u8de8\u8d8a\u56fd\u754c\u7684\u81ea\u6211\u653e\u5927\u6d6a\u6f6e\u3002\u5f53\u4e00\u9996\u6b4c\u540c\u65f6\u767b\u4e0a\u5168\u7403\u591a\u56fd\u699c\u9996\u65f6\uff0c\u610f\u5473\u7740\u5b83\u4e0d\u4ec5\u5177\u6709\u6587\u5316\u5171\u9e23\uff0c\u66f4\u5c55\u73b0\u4e86\u4e92\u8054\u6570\u5b57\u53d7\u4f17\u7684\u529b\u91cf\u3002\u591a\u56fd\u641c\u7d22\u6a21\u5f0f\u8bc1\u5b9e\uff0c\u8fd9\u662f\u4e00\u4e2a\u771f\u6b63\u7684\u5168\u7403\u97f3\u4e50\u65f6\u523b\uff0c\u800c\u975e\u5c40\u9650\u4e8e\u5355\u4e00\u5e02\u573a\u7684\u5730\u533a\u6027\u73b0\u8c61\u3002"
            )
        elif cat == "movies":
            why = (
                f"\u5a31\u4e50\u8d8b\u52bf\u5728\u91cd\u5927\u9884\u544a\u7247\u53d1\u5e03\u3001\u9662\u7ebf\u4e0a\u6620\u6216\u9881\u5956\u5178\u793c\u6cbb\u5019\u8fbe\u5230\u9ad8\u5cf0\u3002**\"{kw}\"** \u4eca\u65e5\u5438\u5f15\u4e86\u5168\u7403\u89c2\u4f17\u7684\u5174\u8da3\uff0c\u5c55\u793a\u4e86\u5168\u7403\u7535\u5f71\u4e1a\u5982\u4f55\u8de8\u8d8a\u8bed\u8a00\u548c\u6587\u5316\u8054\u7cfb\u89c2\u4f17\u3002\u5f53\u4e00\u90e8\u5f71\u7247\u540c\u65f6\u5728\u51e0\u5341\u4e2a\u56fd\u5bb6\u5f15\u53d1\u8d8b\u52bf\uff0c\u5c31\u8868\u660e\u5b83\u8981\u4e48\u662f\u975e\u5e38\u671f\u5f85\u7684\u4f5c\u54c1\uff0c\u8981\u4e48\u662f\u5df2\u8d8a\u8fc7\u5730\u7406\u8fb9\u754c\u3001\u8fdb\u5165\u4e3b\u6d41\u5168\u7403\u8bdd\u9898\u7684\u75c5\u6bd2\u5f0f\u8425\u9500\u6d3b\u52a8\u3002"
            )
        elif cat == "tech":
            why = (
                f"\u5f53\u91cd\u5927\u4ea7\u54c1\u53d1\u5e03\u3001\u91cd\u8981\u516c\u544a\u6216\u4e89\u8bae\u5728\u79d1\u6280\u754c\u6d4c\u8d77\u65f6\uff0c\u79d1\u6280\u8bdd\u9898\u4fbf\u4f1a\u5f15\u53d1\u8d8b\u52bf\u3002**\"{kw}\"** \u4eca\u65e5\u5438\u5f15\u4e86\u5168\u7403\u76ee\u5149\uff0c\u8868\u660e\u53ef\u80fd\u5c55\u73b0\u4e86\u91cd\u5927\u4ea7\u54c1\u53d1\u5e03\u3001\u884c\u4e1a\u52a8\u6001\u6216\u8fdc\u8d85\u539f\u59cb\u53d7\u4f17\u7684\u75c5\u6bd2\u5f0f\u79d1\u6280\u8bdd\u9898\u3002\u591a\u56fd\u641c\u7d22\u6a21\u5f0f\u8868\u660e\uff0c\u8fd9\u662f\u4e00\u4e2a\u5728\u4e0d\u540c\u5e02\u573a\u548c\u7528\u6237\u793e\u7fa4\u4e2d\u540c\u65f6\u4ea7\u751f\u5171\u9e23\u7684\u5168\u7403\u76f8\u5173\u79d1\u6280\u4e8b\u4ef6\u3002"
            )
        elif cat == "sports":
            why = (
                f"\u4f53\u80b2\u8d8b\u52bf\u5728\u91cd\u5927\u8d5b\u4e8b\u7ed3\u679c\u3001\u8d5b\u4e8b\u91cc\u7a0b\u7891\u6216\u77e5\u540d\u8fd0\u52a8\u5458\u7684\u7a81\u53d1\u65b0\u95fb\u65f6\u6025\u5897\u3002**\"{kw}\"** \u5468\u56f4\u7684\u5168\u7403\u641c\u7d22\u6d3b\u52a8\u8868\u660e\uff0c\u4e00\u4e2a\u91cd\u5927\u4f53\u80b2\u8d5b\u4e8b\u6216\u516c\u544a\u6b63\u5728\u5f15\u53d1\u56fd\u9645\u5e02\u573a\u7684\u5171\u9e23\u3002\u4f53\u80b2\u5177\u6709\u72ec\u7279\u7684\u80fd\u529b\uff0c\u8d85\u8d8a\u8bed\u8a00\u969c\u788d\uff0c\u5728\u5168\u7403\u8303\u56f4\u5185\u4ea7\u751f\u540c\u6b65\u53c2\u4e0e\uff0c\u4f7f\u591a\u56fd\u8d8b\u52bf\u6210\u4e3a\u5168\u7403\u4f53\u80b2\u91cd\u8981\u65f6\u523b\u7684\u5f3a\u70c8\u4fe1\u53f7\u3002"
            )
        elif cat == "finance":
            why = (
                f"\u91d1\u878d\u8bdd\u9898\u5728\u5e02\u573a\u52a8\u8361\u3001\u91cd\u5927\u7ecf\u6d4e\u516c\u544a\u6216\u75c5\u6bd2\u5f0f\u6295\u8d44\u6545\u4e8b\u65f6\u5f15\u53d1\u8d8b\u52bf\u3002**\"{kw}\"** \u4eca\u65e5\u7684\u5168\u7403\u5173\u6ce8\u53ef\u80fd\u53cd\u6620\u7ecf\u6d4e\u4e0d\u786e\u5b9a\u6027\u3001\u5e02\u573a\u5f71\u54cd\u4e8b\u4ef6\u6216\u4e00\u4e2a\u5df2\u4ece\u5c0f\u5708\u6295\u8d44\u8005\u8fdb\u5165\u4e3b\u6d41\u516c\u4f17\u610f\u8bc6\u7684\u91d1\u878d\u8bdd\u9898\u3002\u91d1\u878d\u8bdd\u9898\u7684\u591a\u56fd\u8d8b\u52bf\u5f80\u5f80\u610f\u5473\u7740\u66f4\u5e7f\u6cdb\u7684\u5b8f\u89c2\u7ecf\u6d4e\u91cd\u8981\u6027\uff0c\u5f71\u54cd\u8303\u56f4\u8d85\u8d8a\u4e86\u6295\u8d44\u8005\u548c\u4ea4\u6613\u5546\u3002"
            )
        else:
            why = (
                f"\u65b0\u95fb\u548c\u4fe1\u606f\u8d8b\u52bf\u53cd\u6620\u4e86\u6570\u767e\u4e07\u4eba\u5728\u5168\u7403\u540c\u65f6\u641c\u7d22\u7684\u96c6\u4f53\u597d\u5947\u5fc3\u3002**\"{kw}\"** \u4eca\u65e5\u5438\u5f15\u4e86\u56fd\u9645\u5173\u6ce8\uff0c\u8868\u660e\u4e00\u4e2a\u91cd\u5927\u8fdb\u5c55\u3001\u7a81\u53d1\u65b0\u95fb\u6216\u8de8\u6587\u5316\u548c\u8fb9\u754c\u5171\u9e23\u7684\u75c5\u6bd2\u5f0f\u65f6\u523b\u6b63\u5728\u53d1\u751f\u3002\u5f53\u4e00\u4e2a\u8bdd\u9898\u540c\u65f6\u5728\u5c71\u4e2a\u56fd\u5bb6\u5f15\u53d1\u8d8b\u52bf\uff0c\u901a\u5e38\u4ee3\u8868\u4e00\u4e2a\u5177\u6709\u666e\u9042\u610f\u4e49\u6216\u6df1\u523b\u6587\u5316\u5f71\u54cd\u7684\u4e8b\u4ef6\u3002"
            )

        return textwrap.dedent(f"""\
**\"{c['keyword_en']}\"\u662f{c['date_str']}\u5168\u7403\u641c\u7d22\u91cf\u6392\u540d\u7b2c\u4e00\u7684\u8bdd\u9898\uff0c\
\u540c\u65f6\u5728{len(c['countries_list'])}\u4e2a\u56fd\u5bb6\u5f15\u53d1\u5f3a\u70c8\u6d3b\u52a8\u3002\
\u5f15\u9886\u7684\u662f **{c['top_country_name']}** {top_flag}\uff0c\u5728\u8be5\u56fd\u5171\u8bb0\u5f55\u4e86 {c['volume']} \u6b21\u641c\u7d22\uff0c\
\u6210\u4e3a\u4eca\u65e5\u5168\u7403\u6570\u5b57\u5174\u8da3\u65e0\u53ef\u4e89\u8bae\u7684\u9707\u5fc3\u3002

\u65e0\u8bba\u4f60\u662f\u901a\u8fc7\u793e\u4ea4\u5a92\u4f53\u3001\u65b0\u95fb\u6807\u9898\u8fd8\u662f\u670b\u53cb\u5206\u4eab\u53d1\u73b0\u8fd9\u4e2a\u8bdd\u9898\uff0c\
\u4f60\u90fd\u6b63\u5728\u89c1\u8bc1\u4e00\u4e2a\u5168\u7403\u5171\u540c\u5173\u6ce8\u7684\u65f6\u523b\u3002\
\u4e0b\u9762\uff0c\u6211\u4eec\u57fa\u4e8e{c['total_countries']}\u4e2a\u56fd\u5bb6\u7684\u5b9e\u65f6\u6570\u636e\uff0c\u5168\u9762\u89e3\u6790\u8fd9\u4e00\u70ed\u70b9\u7684\u6210\u56e0\u3002

---

## \u201c{c['keyword_en']}\u201d \u662f\u4ec0\u4e48\uff1f

**\"{c['keyword_en']}\"** \u662f\u4e00\u4e2a{c['category_label'].lower()}\u7c7b\u8bdd\u9898\uff0c\u4eca\u65e5\u51b2\u4e0a\u4e86\u5168\u7403\u641c\u7d22\u6392\u884c\u699c\u9876\u7aef\u3002\
\u5c5e\u4e8e **{c['category_label']}** \u7c7b\u522b\uff0c\u5728TrendPulse\u7684\u0030\u20131\u0030\u0030\u5206\u5236\u8d8b\u52bf\u6e29\u5ea6\u91cf\u8868\u4e0a\u8bb0\u5f55\u4e86 **{c['top_temperature']}\u00b0T**\u2014\
\u8868\u660e{tdesc}\u3002

\u8be5\u8bdd\u9898\u4e3b\u8981\u8d77\u6e90\u4e8e **{c['top_country_name']}**\uff0c\u4f46\u5df2\u8fc5\u901f\u8de8\u8d8a\u56fd\u754c\uff0c\
\u5728{other_countries}\u7b49\u5730\u83b7\u5f97\u4e86\u53ef\u9274\u5b9a\u7684\u5173\u6ce8\u5ea6\u3002\
\u8fd9\u79cd\u8de8\u5883\u52a8\u80fd\u6b63\u662f\u5c06\u771f\u6b63\u5168\u7403\u8d8b\u52bf\u4e0e\u5c40\u90e8\u65b0\u95fb\u533a\u5206\u5f00\u6765\u7684\u5173\u952e\u6240\u5728\u3002

### \u6838\u5fc3\u6570\u636e\u4e00\u89c8

| \u6307\u6807 | \u6570\u636e |
|---|---|
| \u641c\u7d22\u91cf | {c['volume']} |
| \u8d8b\u52bf\u6e29\u5ea6 | {c['top_temperature']}\u00b0T / 100 |
| \u7c7b\u522b | {c['category_label']} |
| \u9886\u5148\u56fd\u5bb6 | {top_flag} {c['top_country_name']} |
| \u8986\u76d6\u56fd\u5bb6\u6570 | {len(c['countries_list'])} / {c['total_countries']} |
| \u6570\u636e\u6765\u6e90 | {src} |
| \u6700\u540e\u66f4\u65b0 | {c['date_str']} |{yt_line}
---

## \u4e3a\u4ec0\u4e48 \u201c{c['keyword_en']}\u201d \u4eca\u65e5\u8d8b\u52bf\uff1f

{why}

\u9664\u4e86\u7c7b\u522b\u7279\u6709\u56e0\u7d20\u4e4b\u5916\uff0c**\"{c['keyword_en']}\"**\u4eca\u65e5\u7684\u89c4\u6a21\u4ee4\u4eba\u77a9\u76ee\u3002\
\u5728{len(c['countries_list'])}\u4e2a\u56fd\u5bb6\u540c\u65f6\u8d8b\u52bf\u5316\uff0c\
\u610f\u5473\u7740\u8be5\u8bdd\u9898\u5df2\u5b9e\u73b0\u5206\u6790\u4eba\u58eb\u6240\u79f0\u7684\u201c\u9003\u9038\u901f\u5ea6\u201d\u2014\
\u6709\u673a\u4f20\u64ad\u4e0e\u5a92\u4f53\u62a5\u9053\u76f8\u4e92\u5f3a\u5316\uff0c\u5f62\u6210\u81ea\u6211\u653e\u5927\u5faa\u73af\u7684\u4e34\u754c\u70b9\u3002\
\u4ee5{c['top_temperature']}\u00b0T\u7684\u6e29\u5ea6\uff0c\u8fd9\u662f\u4eca\u65e5\u6211\u4eec\u5168\u7403\u7f51\u7edc\u4e2d\u8ffd\u8e2a\u5230\u7684\u6700\u5f3a\u8d8b\u52bf\u4e4b\u4e00\u3002

\U0001f50d **\u81ea\u884c\u9a8c\u8bc1\u6b64\u8d8b\u52bf\uff1a** \
[\u5728Google\u8d8b\u52bf\u4e2d\u67e5\u770b\u201c{c['keyword_en']}\u201d]({c['google_trends_url']})

---

## \u54ea\u4e9b\u56fd\u5bb6\u5728\u641c\u7d22 \u201c{c['keyword_en']}\u201d\uff1f

TrendPulse \u5b9e\u65f6\u76d1\u6d4b\u5168\u7403 **{c['total_countries']} \u4e2a\u56fd\u5bb6**\u7684\u641c\u7d22\u52a8\u6001\u3002\
\u4ee5\u4e0b\u662f\u4eca\u65e5 **\"{c['keyword_en']}\"** \u5f15\u53d1\u6d3b\u8dc3\u641c\u7d22\u5174\u8da3\u7684\u56fd\u5bb6\uff1a

{countries_md}

### \u6700\u5f3a\u4fe1\u53f7\u6765\u6e90

\u6700\u5f3a\u7684\u641c\u7d22\u4fe1\u53f7\u6765\u81ea **{c['top_country_name']}**\uff0c\u8be5\u56fd\u5f15\u9886\u4e86\u5168\u7403\u5173\u4e8e\
**\"{c['keyword_en']}\"** \u7684\u8ba8\u8bba\u3002\u5728{len(c['countries_list'])}\u4e2a\u56fd\u5bb6\u7684\u5e7f\u6cdb\u4f20\u64ad\u8bf4\u660e\uff0c\
\u8be5\u8bdd\u9898\u5df2\u8d85\u8d8a\u5c40\u90e8\u5730\u57df\u5c40\u9650\uff0c\u6210\u4e3a\u771f\u6b63\u5177\u6709\u5168\u7403\u5f71\u54cd\u529b\u7684\u6587\u5316\u73b0\u8c61\u3002

\u5f53\u4e00\u4e2a\u8d8b\u52bf\u8fbe\u5230\u8fd9\u79cd\u5730\u7406\u6269\u6563\u7a0b\u5ea6\u65f6\uff0c\u610f\u5473\u7740\u5f3a\u52b2\u7684\u5a92\u4f53\u62a5\u9053\u3001\u75c5\u6bd2\u5f0f\u793e\u4ea4\u5206\u4eab\uff0c\
\u6216\u4e00\u4e2a\u8de8\u8d8a\u8bed\u8a00\u548c\u5730\u57df\u8fb9\u754c\u3001\u5728\u5168\u7403\u8303\u56f4\u5185\u5f15\u53d1\u53d7\u4f17\u5171\u9e23\u7684\u6587\u5316\u91cd\u8981\u4e8b\u4ef6\u3002

\U0001f5fa\ufe0f **\u67e5\u770b\u5730\u56fe\u6570\u636e\uff1a** [\u5b9e\u65f6\u5168\u7403\u8d8b\u52bf\u5730\u56fe]({c['site_url']})

---

## \u8d8b\u52bf\u6570\u636e\u4e0e\u6df1\u5ea6\u5206\u6790\u7edf\u8ba1

{c['date_str']} \u7b2c\u4e00\u70ed\u641c\u8bdd\u9898 **\"{c['keyword_en']}\"** \u5b8c\u6574\u7edf\u8ba1\u6570\u636e\uff1a

| \u6307\u6807 | \u6570\u636e |
|---|---|
| \u5cf0\u503c\u641c\u7d22\u91cf | {c['volume']} |
| \u8d8b\u52bf\u6e29\u5ea6 | {c['top_temperature']}\u00b0T |
| \u6e29\u5ea6\u542b\u4e49 | {tdesc} |
| \u4e3b\u8981\u7c7b\u522b | {c['category_label']} |
| \u5168\u7403\u8986\u76d6 | {len(c['countries_list'])} \u4e2a\u56fd\u5bb6 |
| \u76d1\u6d4b\u56fd\u5bb6\u603b\u6570 | {c['total_countries']} |

**\u5173\u4e8e\u8d8b\u52bf\u6e29\u5ea6\uff1a** TrendPulse \u7684\u4e13\u6709\u8bc4\u5206\uff080\u20131\u0030\u0030\uff09\u5c06\u641c\u7d22\u91cf\u3001\u5730\u7406\u8986\u76d6\u8303\u56f4\u548c\u901f\u5ea6\u7efc\u5408\u4e3a\u5355\u4e00\u5f3a\u5ea6\u6307\u6807\u3002{c['top_temperature']}\u00b0T \u7684\u8bc4\u5206\u610f\u5473\u7740{tdesc}\u3002

---

## \u5f53\u524d\u5176\u4ed6\u5feb\u901f\u4e0a\u5347\u7684\u8bdd\u9898

\u5728 **\"{c['keyword_en']}\"** \u4e3b\u5bfc\u5168\u7403\u641c\u7d22\u7684\u540c\u65f6\uff0c\u8fd9\u4e9b\u8bdd\u9898\u4e5f\u5728\u6211\u4eec\u7684{c['total_countries']}\u4e2a\u56fd\u5bb6\u7f51\u7edc\u4e2d\u5feb\u901f\u5d1b\u8d77\uff1a

{rising_md}

\u6bcf\u4e00\u6761\u90fd\u4ee3\u8868\u6765\u81ea\u6570\u767e\u4e07\u4eba\u540c\u65f6\u641c\u7d22\u7684\u5b9e\u65f6\u4fe1\u53f7\u3002\u8bdd\u9898\u7684\u591a\u6837\u6027\u53cd\u6620\u4e86\u5f53\u4e0b\u5168\u7403\u6570\u5b57\u5bf9\u8bdd\u7684\u5e7f\u5ea6\u3002

\U0001f4ca **\u63a2\u7d22\u6240\u6709\u5b9e\u65f6\u8d8b\u52bf\uff1a** [\u67e5\u770b\u5b8c\u6574\u5168\u7403\u8d8b\u52bf\u5730\u56fe]({c['site_url']})

---

## \u4eca\u65e5\u5168\u7403\u6309\u7c7b\u522b\u5212\u5206\u7684\u641c\u7d22\u683c\u5c40

\u4eca\u65e5\u7684\u8d8b\u52bf\u8bdd\u9898\u5728\u5404\u4e3b\u8981\u5185\u5bb9\u7c7b\u522b\u4e2d\u7684\u5206\u5e03\u60c5\u51b5\uff1a

{cat_md}

\u8fd9\u4e00\u5feb\u7167\u53cd\u6620\u4e86{c['total_countries']}\u4e2a\u56fd\u5bb6\u6570\u767e\u4e07\u4eba\u5f53\u524d\u6b63\u5728\u79ef\u6781\u641c\u7d22\u7684\u5185\u5bb9\u3002**{c['category_label']}**\u7c7b\u522b\u4eca\u65e5\u5c24\u4e3a\u6d3b\u8dc3\uff0c**\"{c['keyword_en']}\"**\u53ca\u76f8\u5173\u641c\u7d22\u8d21\u732e\u4e86\u5927\u91cf\u6d41\u91cf\u3002

---

## \u5e38\u89c1\u95ee\u9898\u89e3\u7b54

### \u201c{c['keyword_en']}\u201d \u662f\u4ec0\u4e48\uff1f

**\"{c['keyword_en']}\"** \u662f{c['date_str']}\u5168\u7403\u641c\u7d22\u7b2c\u4e00\u70ed\u8bcd\uff0c\
\u5728{len(c['countries_list'])}\u4e2a\u56fd\u5bb6\u8ffd\u8e2a\u3002\u5c5e\u4e8e{c['category_label']}\u7c7b\u522b\uff0c\
\u5728\u9886\u5148\u56fd\u5bb6\u4ea7\u751f\u4e86{c['volume']}\u6b21\u641c\u7d22\u3002\
\u8bbf\u95ee[\u5b9e\u65f6\u5730\u56fe]({c['site_url']})\u83b7\u53d6\u66f4\u591a\u5730\u7406\u6570\u636e\u3002

### \u4e3a\u4ec0\u4e48 \u201c{c['keyword_en']}\u201d \u4eca\u65e5\u8d8b\u52bf\uff1f

**\"{c['keyword_en']}\"** \u56e0\u5728{len(c['countries_list'])}\u4e2a\u56fd\u5bb6\u7684\u8fc5\u901f\u4f20\u64ad\u800c\u767b\u4e0a\u5168\u7403\u641c\u7d22\u9876\u7aef\uff0c\
\u8d8b\u52bf\u6e29\u5ea6\u8fbe{c['top_temperature']}\u00b0T\u2014\u8868\u660e{tdesc}\u3002\
\u8fd9\u79cd\u591a\u56fd\u6025\u5c04\u901a\u5e38\u610f\u5473\u7740\u75c5\u6bd2\u4e8b\u4ef6\u3001\u7a81\u53d1\u65b0\u95fb\u6216\u91cd\u5927\u6587\u5316\u65f6\u523b\u3002\
\u67e5\u770b[Google\u8d8b\u52bf]({c['google_trends_url']})\u4e86\u89e3\u5386\u53f2\u80cc\u666f\u3002

### \u54ea\u4e2a\u56fd\u5bb6\u5bf9 \u201c{c['keyword_en']}\u201d \u7684\u641c\u7d22\u91cf\u6700\u9ad8\uff1f

\u6839\u636eTrendPulse\u5b9e\u65f6\u6570\u636e\uff0c**{c['top_country_name']}** {top_flag}\u662f\u4eca\u65e5 **\"{c['keyword_en']}\"** \u641c\u7d22\u91cf\u6700\u9ad8\u7684\u56fd\u5bb6\uff0c\
\u5171\u8bb0\u5f55{c['volume']}\u6b21\u67e5\u8be2\u3002\u8be5\u8d8b\u52bf\u5df2\u8499\u5ef6\u81f3\u5176\u4ed6{max(0, len(c['countries_list']) - 1)}\u4e2a\u56fd\u5bb6\u3002\
\u8bbf\u95ee[\u4e92\u52a8\u5730\u56fe]({c['site_url']})\u67e5\u770b\u5b8c\u6574\u5730\u7406\u5206\u5e03\u3002

### TrendPulse \u5982\u4f55\u8861\u91cf\u5168\u7403\u8d8b\u52bf\u5f3a\u5ea6\uff1f

TrendPulse \u6bcf\u5c0f\u65f6\u91c7\u96c6\u5168\u7403 **{c['total_countries']} \u4e2a\u56fd\u5bb6**\u7684\u6570\u636e\uff0c\
\u6574\u5408\u6765\u81eaGoogle\u641c\u7d22\u8d8b\u52bf\u3001YouTube\u3001Apple Music\u56fe\u8868\u548c\u5168\u7403\u65b0\u95fb\u6e90\u7684\u4fe1\u53f7\u3002\
\u6211\u4eec\u7684 **\u8d8b\u52bf\u6e29\u5ea6** \u8bc4\u5206\uff080\u20131\u0030\u0030\uff09\u7efc\u5408\u641c\u7d22\u91cf\u3001\u5730\u7406\u8986\u76d6\u548c\u901f\u5ea6\uff0c\
\u4e3a\u5168\u7403\u6bcf\u4e2a\u8d8b\u52bf\u8bdd\u9898\u751f\u6210\u5355\u4e00\u5f3a\u5ea6\u6307\u6807\u3002

### \u5728\u54ea\u91cc\u53ef\u4ee5\u63a2\u7d22\u66f4\u591a\u5168\u7403\u8d8b\u52bf\u6570\u636e\uff1f

\u60a8\u53ef\u4ee5\u5728[\u5168\u7403\u8d8b\u52bf\u5730\u56fe]({c['site_url']})\u63a2\u7d22\u5b9e\u65f6\u5168\u7403\u8d8b\u52bf\u2014\u2014\u5305\u62ec\u9010\u56fd\u5206\u7c7b\u3001\u7c7b\u522b\u7b5b\u9009\u548c\u6bcf\u5c0f\u65f6\u66f4\u65b0\u3002\
\u6211\u4eec\u8ffd\u8e2a{c['total_countries']}\u4e2a\u56fd\u5bb6\u7684\u8d8b\u52bf\uff0c\u6bcf\u5c0f\u65f6\u66f4\u65b0\u4e00\u6b21\u3002\
\u6d4f\u89c8\u6211\u4eec\u7684[\u6bcf\u65e5\u8d8b\u52bf\u535a\u5ba2]({c['site_url']}/blog)\u83b7\u53d6\u6df1\u5ea6\u5206\u6790\u3002

---

## \u5b9e\u65f6\u638c\u63e1\u5168\u7403\u8d8b\u52bf

**\"{c['keyword_en']}\"** \u662f\u76ee\u524d\u6b63\u5728{c['total_countries']}\u4e2a\u56fd\u5bb6\u76d1\u6d4b\u7684\u6570\u767e\u4e2a\u8d8b\u52bf\u4e4b\u4e00\u3002\
\u65e0\u8bba\u4f60\u662f\u7814\u7a76\u4eba\u5458\u3001\u8bb0\u8005\u3001\u5185\u5bb9\u521b\u4f5c\u8005\u3001\u8425\u9500\u4eba\u5458\u8fd8\u662f\u5bf9\u5168\u7403\u7126\u70b9\u611f\u5174\u8da3\u7684\u666e\u901a\u4eba\u2014\
TrendPulse\u4e3a\u60a8\u63d0\u4f9b\u5168\u7403\u8109\u52a8\u7684\u5373\u65f6\u8bbf\u95ee\u3002

\U0001f449 **[\u67e5\u770b\u5b9e\u65f6\u5168\u7403\u8d8b\u52bf\u5730\u56fe]({c['site_url']})** \u2014 \u6bcf\u5c0f\u65f6\u66f4\u65b0

\U0001f4f0 **[\u9605\u8bfb\u66f4\u591a\u8d8b\u52bf\u5206\u6790]({c['site_url']}/blog)** \u2014 \u6bcf\u65e5\u5168\u7403\u70ed\u70b9\u6df1\u5ea6\u89e3\u6790

*\u6570\u636e\u91c7\u96c6\u4e8e{c['date_str']}\u3002\u6240\u6709\u8d8b\u52bf\u6bcf\u5c0f\u65f6\u5237\u65b0\u3002\u8d8b\u52bf\u6e29\u5ea6\u8bc4\u5206\u53cd\u6620\u91c7\u96c6\u65f6\u7684\u6570\u636e\u3002*
""")

    # ── Spanish ───────────────────────────────────────────────────────────────

    def es_title(c):
        return f"\u00bfPor qu\u00e9 \"{c['keyword_en']}\" es tendencia mundial? An\u00e1lisis del {c['date_str']}"

    def es_excerpt(c):
        return (
            f"\"{c['keyword_en']}\" es la b\u00fasqueda #1 a nivel mundial el {c['date_str']}, "
            f"con {c['volume']} b\u00fasquedas en {c['top_country_name']} y actividad en "
            f"{len(c['countries_list'])} pa\u00edses. Descubre qu\u00e9 impulsa esta tendencia global."
        )

    def es_body(c):
        countries_md = "\n".join(f"- {f} **{n}**" for f, n in c["countries_list"])
        rising_md = "\n".join(
            f"- **{kw}** \u2014 {cn} ({vol})" for kw, cn, vol in c["rising_list"]
        ) or "- Sin datos de tendencias en ascenso disponibles."
        cat_md = "\n".join(
            f"- **{k.capitalize()}**: {v} tendencias activas"
            for k, v in sorted(c["cat_breakdown"].items(), key=lambda x: -x[1]) if v > 0
        ) or "- Datos de categor\u00eda actualizando..."
        yt_line = (
            f"\n\n\U0001f4fa **Ver en YouTube:** [{c['keyword_en']}]({c['youtube_url']})\n"
            if c.get("youtube_url") else ""
        )
        top_flag = c["countries_list"][0][0] if c["countries_list"] else "\U0001f310"
        other_countries = ", ".join(n for _, n in c["countries_list"][1:4]) if len(c["countries_list"]) > 1 else "m\u00faltiples regiones"

        t = c["top_temperature"]
        if t >= 90:
            tdesc = "una tendencia excepcionalmente viral con alcance global masivo"
        elif t >= 75:
            tdesc = "una tendencia muy caliente con fuerte impulso internacional"
        elif t >= 60:
            tdesc = "una tendencia c\u00e1lida y en crecimiento que gana tracci\u00f3n mundial"
        elif t >= 40:
            tdesc = "una tendencia ascendente que genera inter\u00e9s de b\u00fasqueda global"
        else:
            tdesc = "un tema emergente que comienza a capturar la atenci\u00f3n global"

        src = {
            "youtube": "YouTube Tendencias",
            "apple_music": "Apple Music Charts",
            "itunes_movies": "iTunes Movie Charts",
            "google": "Google Tendencias",
            "gdelt": "Noticias Globales (GDELT)",
            "espn": "ESPN Deportes",
            "marketwatch": "MarketWatch Finanzas",
        }.get(c.get("source") or "", "Rastreador Global de Tendencias")

        cat = c["category"]
        kw = c["keyword_en"]
        if cat == "music":
            why = (
                f"Las tendencias musicales explotan cuando los artistas lanzan nuevo contenido, reciben reconocimientos importantes o se vuelven virales en plataformas sociales. "
                f"**\"{kw}\"** ha logrado exactamente eso, combinando el impulso de las plataformas de streaming con el intercambio impulsado por los fans para crear una oleada que se amplifica a s\u00ed misma m\u00e1s all\u00e1 de las fronteras. "
                f"Cuando una canci\u00f3n alcanza la cima de los charts globales simult\u00e1neamente, se\u00f1ala tanto la resonancia cultural como el poder de las audiencias digitales conectadas. "
                f"El patr\u00f3n de b\u00fasqueda en m\u00faltiples pa\u00edses confirma que este es un momento musical genuinamente global, no un fen\u00f3meno regional limitado a un solo mercado."
            )
        elif cat == "movies":
            why = (
                f"Las tendencias de entretenimiento alcanzan su punto m\u00e1ximo alrededor de grandes lanzamientos de tr\u00e1ileres, estrenos teatrales o momentos de ceremonias de premios. "
                f"**\"{kw}\"** ha captado la atenci\u00f3n de la audiencia mundial hoy, reflejando c\u00f3mo la industria cinematogr\u00e1fica global une a los espectadores a trav\u00e9s de idiomas y culturas. "
                f"Cuando un t\u00edtulo genera tendencia simult\u00e1neamente en docenas de pa\u00edses, apunta a un lanzamiento muy esperado o un momento de marketing viral que ha cruzado fronteras geogr\u00e1ficas y entrado en la conversaci\u00f3n global."
            )
        elif cat == "tech":
            why = (
                f"Los temas tecnol\u00f3gicos generan tendencia cuando surgen lanzamientos de productos significativos, grandes anuncios o controversias en el mundo tecnol\u00f3gico. "
                f"**\"{kw}\"** ha captado la atenci\u00f3n global hoy, lo que sugiere una revelaci\u00f3n importante de producto, un desarrollo de la industria o una historia tecnol\u00f3gica viral que se ha extendido m\u00e1s all\u00e1 de su audiencia original. "
                f"El patr\u00f3n de b\u00fasqueda en varios pa\u00edses indica un evento tecnol\u00f3gico globalmente relevante que resuena en diferentes mercados y comunidades de usuarios simult\u00e1neamente."
            )
        elif cat == "sports":
            why = (
                f"Las tendencias deportivas aumentan en torno a grandes resultados de partidos, hitos de torneos o noticias de \u00faltima hora sobre atletas de alto perfil. "
                f"La actividad de b\u00fasqueda global en torno a **\"{kw}\"** sugiere un evento deportivo o anuncio significativo que resuena en los mercados internacionales. "
                f"Los deportes tienen una capacidad \u00fanica para trascender las barreras idiom\u00e1ticas y generar participaci\u00f3n simult\u00e1nea en todo el mundo, haciendo que la tendencia en m\u00faltiples pa\u00edses sea una fuerte se\u00f1al de un momento genuinamente importante en el atletismo global."
            )
        elif cat == "finance":
            why = (
                f"Los temas financieros generan tendencia durante la volatilidad del mercado, grandes anuncios econ\u00f3micos o historias de inversi\u00f3n virales. "
                f"El inter\u00e9s global en **\"{kw}\"** hoy puede reflejar incertidumbre econ\u00f3mica, un evento que mueve el mercado o una historia financiera que ha cruzado de los c\u00edrculos de inversores especializados a la conciencia p\u00fablica general. "
                f"Las tendencias en varios pa\u00edses en temas financieros a menudo se\u00f1alan una relevancia macroecon\u00f3mica m\u00e1s amplia que afecta a personas m\u00e1s all\u00e1 de los inversores y operadores."
            )
        else:
            why = (
                f"Las tendencias de noticias e informaci\u00f3n reflejan la curiosidad colectiva de millones de personas que buscan simult\u00e1neamente en todo el mundo. "
                f"**\"{kw}\"** ha captado la atenci\u00f3n internacional hoy, lo que sugiere un desarrollo significativo, una historia de \u00faltima hora o un momento viral que resuena entre culturas y fronteras. "
                f"Cuando un solo tema genera tendencia en docenas de pa\u00edses a la vez, normalmente representa algo con relevancia universal o un profundo impacto cultural que trasciende las fronteras geogr\u00e1ficas."
            )

        return textwrap.dedent(f"""\
**\"{c['keyword_en']}\"** es la b\u00fasqueda #1 en todo el mundo el {c['date_str']}, \
generando intensa actividad en {len(c['countries_list'])} pa\u00edses simult\u00e1neamente. \
El surgimiento est\u00e1 liderado por **{c['top_country_name']}** {top_flag}, donde se han registrado {c['volume']} b\u00fasquedas, \
convirti\u00e9ndolo en el epicentro indiscutible del inter\u00e9s digital global de hoy.

Ya sea que hayas descubierto este tema en redes sociales, titulares de noticias o el mensaje de un amigo, \
eres parte de un momento mundial. A continuaci\u00f3n, desglosamos exactamente por qu\u00e9 **\"{c['keyword_en']}\"** \
est\u00e1 capturando la atenci\u00f3n del mundo ahora mismo, respaldado por datos en tiempo real de \
{c['total_countries']} pa\u00edses.

---

## \u00bfQu\u00e9 es "{c['keyword_en']}"?

**\"{c['keyword_en']}\"** es un tema de {c['category_label'].lower()} que ha escalado a la cima de los rankings de b\u00fasqueda global hoy. \
Pertenece a la categor\u00eda **{c['category_label']}** y tiene una Temperatura de Tendencia de **{c['top_temperature']}\u00b0T** en la escala 0\u2013100 de TrendPulse \
\u2014 lo que indica {tdesc}.

El tema se origin\u00f3 principalmente en **{c['top_country_name']}** pero se ha extendido r\u00e1pidamente m\u00e1s all\u00e1 de las fronteras, \
ganando tracci\u00f3n medible en {other_countries}, y m\u00e1s all\u00e1. \
Este impulso transfronterizo es lo que separa una tendencia verdaderamente global de una noticia local.

### Estad\u00edsticas Principales

| M\u00e9trica | Valor |
|---|---|
| Volumen de B\u00fasqueda | {c['volume']} |
| Temperatura de Tendencia | {c['top_temperature']}\u00b0T / 100 |
| Categor\u00eda | {c['category_label']} |
| Pa\u00eds L\u00edder | {top_flag} {c['top_country_name']} |
| Pa\u00edses Rastreando | {len(c['countries_list'])} / {c['total_countries']} |
| Fuente de Datos | {src} |
| \u00daltima Actualizaci\u00f3n | {c['date_str']} |{yt_line}
---

## \u00bfPor qu\u00e9 es tendencia "{c['keyword_en']}" hoy?

{why}

M\u00e1s all\u00e1 de los factores espec\u00edficos de la categor\u00eda, la escala de **\"{c['keyword_en']}\"** hoy es notable. \
Ser tendencia en {len(c['countries_list'])} pa\u00edses simult\u00e1neamente significa que este tema ha alcanzado lo que los analistas llaman \u00abvelocidad de escape\u00bb \
\u2014 el punto en que el intercambio org\u00e1nico y la cobertura medi\u00e1tica se refuerzan mutuamente en un bucle de auto-amplificaci\u00f3n. \
A {c['top_temperature']}\u00b0T, esto se encuentra entre las tendencias m\u00e1s intensas rastreadas en nuestra red hoy.

\U0001f50d **Verifica esta tendencia t\u00fa mismo:** \
[Explorar "{c['keyword_en']}" en Google Trends]({c['google_trends_url']})

---

## \u00bfQu\u00e9 pa\u00edses est\u00e1n buscando "{c['keyword_en']}"?

TrendPulse monitorea la actividad de b\u00fasqueda en **{c['total_countries']} pa\u00edses** en tiempo real. \
Estos son los pa\u00edses donde **\"{c['keyword_en']}\"** genera inter\u00e9s de b\u00fasqueda activo hoy:

{countries_md}

### D\u00f3nde la Se\u00f1al es M\u00e1s Fuerte

La se\u00f1al de b\u00fasqueda dominante proviene de **{c['top_country_name']}**, liderando la conversaci\u00f3n global \
sobre **\"{c['keyword_en']}\"**. La distribuci\u00f3n en {len(c['countries_list'])} pa\u00edses indica \
que este tema ha trascendido el inter\u00e9s local y ha entrado en el \u00e1mbito de la cultura verdaderamente global.

Cuando una tendencia alcanza este nivel de difusi\u00f3n geogr\u00e1fica, se\u00f1ala una cobertura medi\u00e1tica s\u00f3lida, intercambio viral en redes sociales, o un evento culturalmente significativo que resuena entre audiencias de todo el mundo, independientemente del idioma o ubicaci\u00f3n.

\U0001f5fa\ufe0f **Ver en el mapa:** \
[Ver el Mapa Global de Tendencias Interactivo]({c['site_url']})

---

## Datos de Tendencia y Estad\u00edsticas Detalladas

Desglose estad\u00edstico completo de la tendencia **\"{c['keyword_en']}\"** a fecha de {c['date_str']}:

| M\u00e9trica | Valor |
|---|---|
| Volumen Pico de B\u00fasqueda | {c['volume']} |
| Temperatura de Tendencia | {c['top_temperature']}\u00b0T |
| Significado de la Temperatura | {tdesc.capitalize()} |
| Categor\u00eda Principal | {c['category_label']} |
| Alcance Global | {len(c['countries_list'])} pa\u00edses |
| Total Pa\u00edses Monitoreados | {c['total_countries']} |

**Sobre la Temperatura de Tendencia:** La puntuaci\u00f3n propietaria de TrendPulse (0\u2013100) combina volumen de b\u00fasqueda, cobertura geogr\u00e1fica y velocidad en una \u00fanica m\u00e9trica de intensidad. Una puntuaci\u00f3n de {c['top_temperature']}\u00b0T significa {tdesc}.

---

## \u00bfQu\u00e9 M\u00e1s Es Tendencia Ahora Mismo?

Mientras **\"{c['keyword_en']}\"** domina el escenario global, estos temas tambi\u00e9n est\u00e1n subiendo r\u00e1pido \
en nuestra red de {c['total_countries']} pa\u00edses:

{rising_md}

Cada uno de estos representa una se\u00f1al en tiempo real de millones de personas buscando simult\u00e1neamente. La variedad de temas refleja la amplitud de la conversaci\u00f3n digital global que est\u00e1 ocurriendo ahora mismo.

\U0001f4ca **Explora todas las tendencias en vivo:** [Abrir el Mapa Global de Tendencias]({c['site_url']})

---

## El Panorama Global de B\u00fasqueda de Hoy por Categor\u00eda

C\u00f3mo se distribuyen los temas de tendencia de hoy entre las principales categor\u00edas de contenido:

{cat_md}

Esta instant\u00e1nea captura lo que millones de personas en {c['total_countries']} pa\u00edses est\u00e1n buscando activamente ahora mismo. La categor\u00eda **{c['category_label']}** est\u00e1 particularmente activa hoy, impulsada en gran parte por **\"{c['keyword_en']}\"** y b\u00fasquedas estrechamente relacionadas.

---

## Preguntas Frecuentes

### \u00bfQu\u00e9 es "{c['keyword_en']}"?

**\"{c['keyword_en']}\"** es actualmente la b\u00fasqueda #1 a nivel mundial, rastreada en \
{len(c['countries_list'])} pa\u00edses el {c['date_str']}. Pertenece a la categor\u00eda {c['category_label']} \
y est\u00e1 generando {c['volume']} b\u00fasquedas solo en el pa\u00eds l\u00edder. \
Visita el [mapa de tendencias en vivo]({c['site_url']}) para explorar datos geogr\u00e1ficos en tiempo real.

### \u00bfPor qu\u00e9 es tendencia "{c['keyword_en']}" hoy?

**\"{c['keyword_en']}\"** lleg\u00f3 a la cima de las b\u00fasquedas globales debido a su r\u00e1pida propagaci\u00f3n en \
{len(c['countries_list'])} pa\u00edses, con una Temperatura de Tendencia de {c['top_temperature']}\u00b0T \u2014 \
lo que indica {tdesc}. Esta oleada en m\u00faltiples pa\u00edses normalmente se\u00f1ala un evento viral, una historia de \u00faltima hora \
o un momento cultural importante. Consulta [Google Trends]({c['google_trends_url']}) para contexto hist\u00f3rico.

### \u00bfQu\u00e9 pa\u00eds busca m\u00e1s "{c['keyword_en']}"?

Seg\u00fan los datos en tiempo real de TrendPulse, **{c['top_country_name']}** {top_flag} es el pa\u00eds l\u00edder en b\u00fasquedas de **\"{c['keyword_en']}\"** hoy, con {c['volume']} consultas registradas. La tendencia se ha extendido a otros {max(0, len(c['countries_list']) - 1)} pa\u00edses. Explora el [mapa interactivo]({c['site_url']}) para ver el desglose geogr\u00e1fico completo.

### \u00bfC\u00f3mo mide TrendPulse la intensidad de la tendencia global?

TrendPulse recopila datos en tiempo real de **{c['total_countries']} pa\u00edses** cada hora, \
agregando se\u00f1ales de Google Search Trends, YouTube, Apple Music Charts y noticias globales. \
Nuestro puntaje de **Temperatura de Tendencia** (0\u2013100) combina volumen de b\u00fasqueda, cobertura geogr\u00e1fica y velocidad \
para producir una \u00fanica m\u00e9trica de intensidad para cada tema de tendencia mundial.

### \u00bfD\u00f3nde puedo explorar m\u00e1s datos de tendencias globales?

Puedes explorar tendencias globales en vivo \u2014 incluyendo desgloses por pa\u00eds, filtros de categor\u00eda y actualizaciones por hora \u2014 en [Global Trend Map]({c['site_url']}). Rastreamos tendencias en {c['total_countries']} pa\u00edses, actualizados cada hora. Explora nuestro [blog de tendencias diarias]({c['site_url']}/blog) para an\u00e1lisis en profundidad.

---

## Mant\u00e9n el Ritmo de Cada Tendencia Global

**\"{c['keyword_en']}\"** es una de las cientos de tendencias que se monitorean ahora mismo en \
{c['total_countries']} pa\u00edses. Ya seas investigador, periodista, creador de contenido, \
mercad\u00f3logo o simplemente curioso sobre lo que piensa el mundo \u2014 TrendPulse te da \
acceso instant\u00e1neo al pulso global.

\U0001f449 **[Explorar el Mapa Global de Tendencias en Vivo]({c['site_url']})** \u2014 actualizado cada hora

\U0001f4f0 **[Leer m\u00e1s an\u00e1lisis de tendencias]({c['site_url']}/blog)** \u2014 an\u00e1lisis diarios de las tendencias #1 del mundo

*Datos recopilados el {c['date_str']}. Todas las tendencias se actualizan cada hora. \
Las puntuaciones de Temperatura de Tendencia reflejan los datos en el momento de la recolecci\u00f3n.*
""")

    # ── Portuguese ────────────────────────────────────────────────────────────

    def pt_title(c):
        return f"Por que \"{c['keyword_en']}\" \u00e9 tend\u00eancia mundial? An\u00e1lise de {c['date_str']}"

    def pt_excerpt(c):
        return (
            f"\"{c['keyword_en']}\" \u00e9 a busca #1 no mundo em {c['date_str']}, "
            f"com {c['volume']} pesquisas em {c['top_country_name']} e atividade em "
            f"{len(c['countries_list'])} pa\u00edses. Entenda o que est\u00e1 impulsionando essa tend\u00eancia global."
        )

    def pt_body(c):
        countries_md = "\n".join(f"- {f} **{n}**" for f, n in c["countries_list"])
        rising_md = "\n".join(
            f"- **{kw}** \u2014 {cn} ({vol})" for kw, cn, vol in c["rising_list"]
        ) or "- Sem dados de tend\u00eancias em alta dispon\u00edveis."
        cat_md = "\n".join(
            f"- **{k.capitalize()}**: {v} tend\u00eancias ativas"
            for k, v in sorted(c["cat_breakdown"].items(), key=lambda x: -x[1]) if v > 0
        ) or "- Dados de categoria atualizando..."
        yt_line = (
            f"\n\n\U0001f4fa **Assistir no YouTube:** [{c['keyword_en']}]({c['youtube_url']})\n"
            if c.get("youtube_url") else ""
        )
        top_flag = c["countries_list"][0][0] if c["countries_list"] else "\U0001f310"
        other_countries = ", ".join(n for _, n in c["countries_list"][1:4]) if len(c["countries_list"]) > 1 else "m\u00faltiplas regi\u00f5es"

        t = c["top_temperature"]
        if t >= 90:
            tdesc = "uma tend\u00eancia excepcionalmente viral com alcance global massivo"
        elif t >= 75:
            tdesc = "uma tend\u00eancia muito quente com forte impulso internacional"
        elif t >= 60:
            tdesc = "uma tend\u00eancia quente e crescente que ganha tra\u00e7\u00e3o mundial"
        elif t >= 40:
            tdesc = "uma tend\u00eancia ascendente que gera interesse de busca global"
        else:
            tdesc = "um t\u00f3pico emergente que come\u00e7a a capturar a aten\u00e7\u00e3o global"

        src = {
            "youtube": "YouTube Tend\u00eancias",
            "apple_music": "Apple Music Charts",
            "itunes_movies": "iTunes Movie Charts",
            "google": "Google Tend\u00eancias",
            "gdelt": "Not\u00edcias Globais (GDELT)",
            "espn": "ESPN Esportes",
            "marketwatch": "MarketWatch Finan\u00e7as",
        }.get(c.get("source") or "", "Rastreador Global de Tend\u00eancias")

        cat = c["category"]
        kw = c["keyword_en"]
        if cat == "music":
            why = (
                f"As tend\u00eancias musicais explodem quando artistas lan\u00e7am novo conte\u00fado, recebem reconhecimento importante em pr\u00eamios ou se tornam virais nas plataformas sociais. "
                f"**\"{kw}\"** conseguiu exatamente isso, combinando o impulso das plataformas de streaming com o compartilhamento impulsionado pelos f\u00e3s para criar uma onda que se amplifica al\u00e9m das fronteiras. "
                f"Quando uma m\u00fasica chega ao topo dos charts globais simultaneamente, sinaliza tanto a resson\u00e2ncia cultural quanto o poder das audi\u00eancias digitais conectadas. "
                f"O padr\u00e3o de busca em m\u00faltiplos pa\u00edses confirma que este \u00e9 um momento musical genuinamente global, n\u00e3o um fen\u00f4meno regional limitado a um \u00fanico mercado."
            )
        elif cat == "movies":
            why = (
                f"As tend\u00eancias de entretenimento atingem seu pico em torno de grandes lan\u00e7amentos de tr\u00e3ilas, estreias teatrais ou momentos de cerim\u00f4nias de pr\u00eamios. "
                f"**\"{kw}\"** capturou a aten\u00e7\u00e3o da audi\u00eancia mundial hoje, refletindo como a ind\u00fastria cinematogr\u00e1fica global une espectadores atrav\u00e9s de idiomas e culturas. "
                f"Quando um t\u00edtulo gera tend\u00eancia simultaneamente em dezenas de pa\u00edses, aponta para um lan\u00e7amento muito esperado ou um momento de marketing viral que cruzou fronteiras geogr\u00e1ficas e entrou na conversa global."
            )
        elif cat == "tech":
            why = (
                f"T\u00f3picos de tecnologia geram tend\u00eancia quando surgem lan\u00e7amentos significativos de produtos, grandes an\u00fancios ou controv\u00e9rsias no mundo tech. "
                f"**\"{kw}\"** capturou a aten\u00e7\u00e3o global hoje, sugerindo uma revela\u00e7\u00e3o importante de produto, um desenvolvimento do setor ou uma hist\u00f3ria tech viral que se espalhou al\u00e9m do seu p\u00fablico original. "
                f"O padr\u00e3o de busca em v\u00e1rios pa\u00edses indica um evento tecnol\u00f3gico globalmente relevante que ressoa em diferentes mercados e comunidades de usu\u00e1rios simultaneamente."
            )
        elif cat == "sports":
            why = (
                f"As tend\u00eancias esportivas surgem em torno de grandes resultados de partidas, marcos de torneios ou not\u00edcias de \u00faltima hora sobre atletas de alto perfil. "
                f"A atividade de busca global em torno de **\"{kw}\"** sugere um evento esportivo significativo ou an\u00fancio que ressoa nos mercados internacionais. "
                f"O esporte tem uma capacidade \u00fanica de transcender barreiras idiom\u00e1ticas e gerar engajamento simult\u00e2neo em todo o mundo, tornando a tend\u00eancia em m\u00faltiplos pa\u00edses um forte sinal de um momento genuinamente importante no atletismo global."
            )
        elif cat == "finance":
            why = (
                f"T\u00f3picos financeiros geram tend\u00eancia durante volatilidade de mercado, grandes an\u00fancios econ\u00f4micos ou hist\u00f3rias virais de investimento. "
                f"O interesse global em **\"{kw}\"** hoje pode refletir incerteza econ\u00f4mica, um evento que move o mercado ou uma hist\u00f3ria financeira que cruzou de c\u00edrculos de investidores especializados para a consci\u00eancia p\u00fablica geral. "
                f"A tend\u00eancia em v\u00e1rios pa\u00edses em t\u00f3picos financeiros frequentemente sinaliza uma relev\u00e2ncia macroecon\u00f4mica mais ampla que afeta pessoas al\u00e9m de investidores e traders."
            )
        else:
            why = (
                f"As tend\u00eancias de not\u00edcias e informa\u00e7\u00f5es refletem a curiosidade coletiva de milh\u00f5es de pessoas pesquisando simultaneamente ao redor do mundo. "
                f"**\"{kw}\"** capturou a aten\u00e7\u00e3o internacional hoje, sugerindo um desenvolvimento significativo, uma not\u00edcia de \u00faltima hora ou um momento viral que ressoa entre culturas e fronteiras. "
                f"Quando um \u00fanico t\u00f3pico gera tend\u00eancia em dezenas de pa\u00edses de uma vez, normalmente representa algo com relev\u00e2ncia universal ou profundo impacto cultural que transcende fronteiras geogr\u00e1ficas."
            )

        return textwrap.dedent(f"""\
**\"{c['keyword_en']}\"** \u00e9 a busca #1 no mundo em {c['date_str']}, \
gerando atividade intensa em {len(c['countries_list'])} pa\u00edses simultaneamente. \
O surgimento est\u00e1 sendo liderado por **{c['top_country_name']}** {top_flag}, onde {c['volume']} pesquisas \
foram registradas, tornando-o o epicentro incontestado do interesse digital global de hoje.

Seja voc\u00ea quem descobriu este t\u00f3pico atrav\u00e9s das redes sociais, manchetes de not\u00edcias ou a mensagem de um amigo, \
voc\u00ea faz parte de um momento mundial. Abaixo, detalhamos exatamente por que **\"{c['keyword_en']}\"** \
est\u00e1 capturando a aten\u00e7\u00e3o do mundo agora \u2014 respaldado por dados em tempo real de \
{c['total_countries']} pa\u00edses.

---

## O que \u00e9 "{c['keyword_en']}"?

**\"{c['keyword_en']}\"** \u00e9 um t\u00f3pico de {c['category_label'].lower()} que subiu ao topo dos rankings de busca global hoje. \
Pertence \u00e0 categoria **{c['category_label']}** e carrega uma Temperatura de Tend\u00eancia de **{c['top_temperature']}\u00b0T** na escala 0\u2013100 do TrendPulse \
\u2014 indicando {tdesc}.

O t\u00f3pico se originou principalmente em **{c['top_country_name']}** mas se espalhou rapidamente al\u00e9m das fronteiras, \
ganhando tra\u00e7\u00e3o mensur\u00e1vel em {other_countries}, e al\u00e9m. \
Esse impulso transfrontei\u00e7o \u00e9 o que separa uma tend\u00eancia verdadeiramente global de uma not\u00edcia local.

### Estat\u00edsticas Principais

| M\u00e9trica | Valor |
|---|---|
| Volume de Buscas | {c['volume']} |
| Temperatura de Tend\u00eancia | {c['top_temperature']}\u00b0T / 100 |
| Categoria | {c['category_label']} |
| Pa\u00eds L\u00edder | {top_flag} {c['top_country_name']} |
| Pa\u00edses Rastreando | {len(c['countries_list'])} / {c['total_countries']} |
| Fonte de Dados | {src} |
| \u00daltima Atualiza\u00e7\u00e3o | {c['date_str']} |{yt_line}
---

## Por que "{c['keyword_en']}" \u00e9 tend\u00eancia hoje?

{why}

Al\u00e9m dos fatores espec\u00edficos da categoria, a escala de **\"{c['keyword_en']}\"** hoje \u00e9 not\u00e1vel. \
Ser tend\u00eancia em {len(c['countries_list'])} pa\u00edses simultaneamente significa que este t\u00f3pico alcan\u00e7ou o que os analistas chamam de \u00abvelocidade de escape\u00bb \
\u2014 o ponto em que o compartilhamento org\u00e2nico e a cobertura da m\u00eddia se refor\u00e7am mutuamente em um ciclo de auto-amplifica\u00e7\u00e3o. \
A {c['top_temperature']}\u00b0T, isso est\u00e1 entre as tend\u00eancias mais intensas monitoradas em nossa rede hoje.

\U0001f50d **Verifique esta tend\u00eancia voc\u00ea mesmo:** \
[Explorar "{c['keyword_en']}" no Google Trends]({c['google_trends_url']})

---

## Quais Pa\u00edses Est\u00e3o Pesquisando "{c['keyword_en']}"?

O TrendPulse monitora a atividade de busca em **{c['total_countries']} pa\u00edses** em tempo real. \
Estes s\u00e3o os pa\u00edses onde **\"{c['keyword_en']}\"** est\u00e1 gerando interesse de busca ativo hoje:

{countries_md}

### Onde o Sinal \u00c9 Mais Forte

O sinal de busca dominante vem de **{c['top_country_name']}**, liderando a conversa\u00e7\u00e3o global \
sobre **\"{c['keyword_en']}\"**. A distribui\u00e7\u00e3o em {len(c['countries_list'])} pa\u00edses indica \
que este t\u00f3pico transcendeu o interesse local e entrou no reino da cultura verdadeiramente global.

Quando uma tend\u00eancia atinge esse n\u00edvel de dispers\u00e3o geogr\u00e1fica, sinaliza forte cobertura da m\u00eddia, compartilhamento viral nas redes sociais, ou um evento culturalmente significativo que ressoa com p\u00fablicos em todo o mundo, independentemente de idioma ou localiza\u00e7\u00e3o.

\U0001f5fa\ufe0f **Ver no mapa:** \
[Ver o Mapa Global de Tend\u00eancias Interativo]({c['site_url']})

---

## Dados de Tend\u00eancia e Estat\u00edsticas Detalhadas

Detalhamento estat\u00edstico completo da tend\u00eancia **\"{c['keyword_en']}\"** em {c['date_str']}:

| M\u00e9trica | Valor |
|---|---|
| Volume Pico de Buscas | {c['volume']} |
| Temperatura de Tend\u00eancia | {c['top_temperature']}\u00b0T |
| Significado da Temperatura | {tdesc.capitalize()} |
| Categoria Principal | {c['category_label']} |
| Alcance Global | {len(c['countries_list'])} pa\u00edses |
| Total Pa\u00edses Monitorados | {c['total_countries']} |

**Sobre a Temperatura de Tend\u00eancia:** A pontua\u00e7\u00e3o propriet\u00e1ria do TrendPulse (0\u2013100) combina volume de busca, cobertura geogr\u00e1fica e velocidade em uma \u00fanica m\u00e9trica de intensidade. Uma pontua\u00e7\u00e3o de {c['top_temperature']}\u00b0T significa {tdesc}.

---

## O que Mais Est\u00e1 em Tend\u00eancia Agora?

Enquanto **\"{c['keyword_en']}\"** domina o cen\u00e1rio global, estes t\u00f3picos tamb\u00e9m est\u00e3o subindo r\u00e1pido \
em nossa rede de {c['total_countries']} pa\u00edses:

{rising_md}

Cada um desses representa um sinal em tempo real de milh\u00f5es de pessoas pesquisando simultaneamente. A variedade de t\u00f3picos reflete a amplitude da conversa\u00e7\u00e3o digital global que est\u00e1 acontecendo agora.

\U0001f4ca **Explore todas as tend\u00eancias ao vivo:** [Abrir o Mapa Global de Tend\u00eancias]({c['site_url']})

---

## O Panorama Global de Busca de Hoje por Categoria

Como os t\u00f3picos de tend\u00eancia de hoje se distribuem entre as principais categorias de conte\u00fado:

{cat_md}

Este instant\u00e2neo captura o que milh\u00f5es de pessoas em {c['total_countries']} pa\u00edses est\u00e3o pesquisando ativamente agora. A categoria **{c['category_label']}** est\u00e1 particularmente ativa hoje, impulsionada em grande parte por **\"{c['keyword_en']}\"** e buscas intimamente relacionadas.

---

## Perguntas Frequentes

### O que \u00e9 "{c['keyword_en']}"?

**\"{c['keyword_en']}\"** \u00e9 atualmente a busca #1 a n\u00edvel mundial, rastreada em \
{len(c['countries_list'])} pa\u00edses em {c['date_str']}. Pertence \u00e0 categoria {c['category_label']} \
e est\u00e1 gerando {c['volume']} buscas apenas no pa\u00eds l\u00edder. \
Visite o [mapa de tend\u00eancias ao vivo]({c['site_url']}) para explorar dados geogr\u00e1ficos em tempo real.

### Por que "{c['keyword_en']}" \u00e9 tend\u00eancia hoje?

**\"{c['keyword_en']}\"** chegou ao topo das buscas globais devido \u00e0 r\u00e1pida dissemina\u00e7\u00e3o em \
{len(c['countries_list'])} pa\u00edses, com uma Temperatura de Tend\u00eancia de {c['top_temperature']}\u00b0T \u2014 \
indicando {tdesc}. Essa onda em m\u00faltiplos pa\u00edses normalmente sinaliza um evento viral, uma not\u00edcia de \u00faltima hora \
ou um momento cultural importante. Consulte [Google Trends]({c['google_trends_url']}) para contexto hist\u00f3rico.

### Qual pa\u00eds est\u00e1 pesquisando mais "{c['keyword_en']}"?

Segundo os dados em tempo real do TrendPulse, **{c['top_country_name']}** {top_flag} \u00e9 o pa\u00eds l\u00edder em buscas por **\"{c['keyword_en']}\"** hoje, com {c['volume']} consultas registradas. A tend\u00eancia se espalhou para outros {max(0, len(c['countries_list']) - 1)} pa\u00edses. Explore o [mapa interativo]({c['site_url']}) para ver a distribui\u00e7\u00e3o geogr\u00e1fica completa.

### Como o TrendPulse mede a intensidade da tend\u00eancia global?

O TrendPulse coleta dados em tempo real de **{c['total_countries']} pa\u00edses** a cada hora, \
agregando sinais do Google Search Trends, YouTube, Apple Music Charts e not\u00edcias globais. \
Nossa pontua\u00e7\u00e3o de **Temperatura de Tend\u00eancia** (0\u2013100) combina volume de busca, cobertura geogr\u00e1fica e velocidade \
para produzir uma \u00fanica m\u00e9trica de intensidade para cada t\u00f3pico de tend\u00eancia mundial.

### Onde posso explorar mais dados de tend\u00eancias globais?

Voc\u00ea pode explorar tend\u00eancias globais ao vivo \u2014 incluindo detalhamentos por pa\u00eds, filtros de categoria e atualiza\u00e7\u00f5es por hora \u2014 em [Global Trend Map]({c['site_url']}). Rastreamos tend\u00eancias em {c['total_countries']} pa\u00edses, atualizadas a cada hora. Navegue pelo nosso [blog de tend\u00eancias di\u00e1rias]({c['site_url']}/blog) para an\u00e1lises aprofundadas.

---

## Fique \u00c0 Frente de Cada Tend\u00eancia Global

**\"{c['keyword_en']}\"** \u00e9 uma das centenas de tend\u00eancias sendo monitoradas agora mesmo em \
{c['total_countries']} pa\u00edses. Seja voc\u00ea pesquisador, jornalista, criador de conte\u00fado, \
profissional de marketing ou simplesmente curioso sobre o que o mundo est\u00e1 pensando \u2014 o TrendPulse d\u00e1 a voc\u00ea \
acesso instant\u00e2neo ao pulso global.

\U0001f449 **[Explorar o Mapa Global de Tend\u00eancias Ao Vivo]({c['site_url']})** \u2014 atualizado a cada hora

\U0001f4f0 **[Ler mais an\u00e1lises de tend\u00eancias]({c['site_url']}/blog)** \u2014 an\u00e1lises di\u00e1rias das tend\u00eancias #1 do mundo

*Dados coletados em {c['date_str']}. Todas as tend\u00eancias se atualizam a cada hora. \
As pontua\u00e7\u00f5es de Temperatura de Tend\u00eancia refletem os dados no momento da coleta.*
""")

    # ── French ────────────────────────────────────────────────────────────────

    def fr_title(c):
        return f"Pourquoi \"{c['keyword_en']}\" est-il en tendance mondiale\u00a0? Analyse du {c['date_str']}"

    def fr_excerpt(c):
        return (
            f"\"{c['keyword_en']}\" est la recherche #1 dans le monde le {c['date_str']}, "
            f"avec {c['volume']} recherches en {c['top_country_name']} et une activit\u00e9 dans "
            f"{len(c['countries_list'])} pays. D\u00e9couvrez ce qui alimente cette tendance mondiale."
        )

    def fr_body(c):
        countries_md = "\n".join(f"- {f} **{n}**" for f, n in c["countries_list"])
        rising_md = "\n".join(
            f"- **{kw}** \u2014 {cn} ({vol})" for kw, cn, vol in c["rising_list"]
        ) or "- Aucune donn\u00e9e de tendance montante disponible."
        cat_md = "\n".join(
            f"- **{k.capitalize()}\u00a0**: {v} tendances actives"
            for k, v in sorted(c["cat_breakdown"].items(), key=lambda x: -x[1]) if v > 0
        ) or "- Donn\u00e9es de cat\u00e9gorie en cours de mise \u00e0 jour..."
        yt_line = (
            f"\n\n\U0001f4fa **Regarder sur YouTube\u00a0:** [{c['keyword_en']}]({c['youtube_url']})\n"
            if c.get("youtube_url") else ""
        )
        top_flag = c["countries_list"][0][0] if c["countries_list"] else "\U0001f310"
        other_countries = ", ".join(n for _, n in c["countries_list"][1:4]) if len(c["countries_list"]) > 1 else "plusieurs r\u00e9gions"

        t = c["top_temperature"]
        if t >= 90:
            tdesc = "une tendance exceptionnellement virale avec une port\u00e9e mondiale massive"
        elif t >= 75:
            tdesc = "une tendance tr\u00e8s chaude avec un fort \u00e9lan international"
        elif t >= 60:
            tdesc = "une tendance chaude et croissante qui gagne en traction mondiale"
        elif t >= 40:
            tdesc = "une tendance montante qui suscite un int\u00e9r\u00eat de recherche mondial"
        else:
            tdesc = "un sujet \u00e9mergent qui commence \u00e0 capturer l\u2019attention mondiale"

        src = {
            "youtube": "YouTube Tendances",
            "apple_music": "Apple Music Charts",
            "itunes_movies": "iTunes Film Charts",
            "google": "Google Tendances",
            "gdelt": "Actualit\u00e9s mondiales (GDELT)",
            "espn": "ESPN Sports",
            "marketwatch": "MarketWatch Finance",
        }.get(c.get("source") or "", "Suivi des tendances mondiales")

        cat = c["category"]
        kw = c["keyword_en"]
        if cat == "music":
            why = (
                f"Les tendances musicales explosent quand les artistes publient du nouveau contenu, re\u00e7oivent une reconnaissance majeure ou deviennent viraux sur les plateformes sociales. "
                f"**\"{kw}\"** a r\u00e9alis\u00e9 exactement cela, combinant l\u2019\u00e9lan des plateformes de streaming avec le partage port\u00e9 par les fans pour cr\u00e9er une vague qui s\u2019amplifie d\u2019elle-m\u00eame au-del\u00e0 des fronti\u00e8res. "
                f"Quand un titre atteint simultan\u00e9ment le sommet des charts mondiaux, cela signale \u00e0 la fois une r\u00e9sonance culturelle et la puissance des audiences num\u00e9riques connect\u00e9es. "
                f"Le sch\u00e9ma de recherche dans plusieurs pays confirme qu\u2019il s\u2019agit d\u2019un v\u00e9ritable moment musical mondial, non d\u2019un ph\u00e9nom\u00e8ne r\u00e9gional limit\u00e9 \u00e0 un seul march\u00e9."
            )
        elif cat == "movies":
            why = (
                f"Les tendances du divertissement atteignent leur apog\u00e9e autour des grandes sorties de bandes-annonces, des sorties en salle ou des c\u00e9r\u00e9monies de r\u00e9compenses. "
                f"**\"{kw}\"** a captur\u00e9 l\u2019attention du public mondial aujourd\u2019hui, refl\u00e9tant comment l\u2019industrie cin\u00e9matographique mondiale unit les spectateurs \u00e0 travers les langues et les cultures. "
                f"Quand un titre g\u00e9n\u00e8re simultan\u00e9ment des tendances dans des dizaines de pays, cela pointe vers une sortie tr\u00e8s attendue ou un moment de marketing viral qui a travers\u00e9 les fronti\u00e8res g\u00e9ographiques et est entr\u00e9 dans la conversation mondiale."
            )
        elif cat == "tech":
            why = (
                f"Les sujets technologiques g\u00e9n\u00e8rent des tendances lors de lancements de produits significatifs, d\u2019annonces importantes ou de controverses dans le monde tech. "
                f"**\"{kw}\"** a captur\u00e9 l\u2019attention mondiale aujourd\u2019hui, sugg\u00e9rant soit une r\u00e9v\u00e9lation majeure de produit, un d\u00e9veloppement industriel ou une histoire tech virale qui s\u2019est r\u00e9pandue bien au-del\u00e0 de son audience d\u2019origine. "
                f"Le sch\u00e9ma de recherche dans plusieurs pays indique un \u00e9v\u00e9nement technologique globalement pertinent qui r\u00e9sonne dans diff\u00e9rents march\u00e9s et communaut\u00e9s d\u2019utilisateurs simultan\u00e9ment."
            )
        elif cat == "sports":
            why = (
                f"Les tendances sportives augmentent autour des r\u00e9sultats de grands matchs, des \u00e9tapes de tournois ou des derni\u00e8res nouvelles sur des athl\u00e8tes de haut niveau. "
                f"L\u2019activit\u00e9 de recherche mondiale autour de **\"{kw}\"** sugg\u00e8re un \u00e9v\u00e9nement sportif significatif ou une annonce qui r\u00e9sonne sur les march\u00e9s internationaux. "
                f"Le sport a une capacit\u00e9 unique \u00e0 transcender les barri\u00e8res linguistiques et \u00e0 g\u00e9n\u00e9rer un engagement simultan\u00e9 dans le monde entier, faisant des tendances multi-pays un signal fort d\u2019un moment v\u00e9ritablement important dans l\u2019athl\u00e9tisme mondial."
            )
        elif cat == "finance":
            why = (
                f"Les sujets financiers g\u00e9n\u00e8rent des tendances lors de la volatilit\u00e9 des march\u00e9s, des grandes annonces \u00e9conomiques ou des histoires d\u2019investissement virales. "
                f"L\u2019int\u00e9r\u00eat mondial pour **\"{kw}\"** aujourd\u2019hui peut refl\u00e9ter une incertitude \u00e9conomique, un \u00e9v\u00e9nement qui fait bouger les march\u00e9s ou une histoire financi\u00e8re qui est pass\u00e9e des cercles d\u2019investisseurs sp\u00e9cialis\u00e9s \u00e0 la conscience publique g\u00e9n\u00e9rale. "
                f"Les tendances multi-pays dans les sujets financiers signalent souvent une pertinence macro\u00e9conomique plus large qui affecte des personnes au-del\u00e0 des seuls investisseurs et traders."
            )
        else:
            why = (
                f"Les tendances d\u2019actualit\u00e9s et d\u2019informations refl\u00e8tent la curiosit\u00e9 collective de millions de personnes qui recherchent simultan\u00e9ment \u00e0 travers le monde. "
                f"**\"{kw}\"** a captur\u00e9 l\u2019attention internationale aujourd\u2019hui, sugg\u00e9rant un d\u00e9veloppement significatif, une histoire de derni\u00e8re minute ou un moment viral qui r\u00e9sonne entre les cultures et les fronti\u00e8res. "
                f"Quand un seul sujet g\u00e9n\u00e8re des tendances dans des dizaines de pays \u00e0 la fois, cela repr\u00e9sente g\u00e9n\u00e9ralement quelque chose avec une pertinence universelle ou un impact culturel profond qui transcende les fronti\u00e8res g\u00e9ographiques."
            )

        return textwrap.dedent(f"""\
**\"{c['keyword_en']}\"** est la recherche #1 dans le monde le {c['date_str']}, \
g\u00e9n\u00e9rant une activit\u00e9 intense dans {len(c['countries_list'])} pays simultan\u00e9ment. \
La mont\u00e9e est men\u00e9e par **{c['top_country_name']}** {top_flag}, o\u00f9 {c['volume']} recherches \
ont \u00e9t\u00e9 enregistr\u00e9es, faisant de ce pays l\u2019\u00e9picentre incontestable de l\u2019int\u00e9r\u00eat num\u00e9rique mondial d\u2019aujourd\u2019hui.

Que vous ayez d\u00e9couvert ce sujet via les r\u00e9seaux sociaux, les titres d\u2019actualit\u00e9 ou le message d\u2019un ami, \
vous faites partie d\u2019un moment mondial. Ci-dessous, nous d\u00e9taillons exactement pourquoi **\"{c['keyword_en']}\"** \
capte l\u2019attention du monde en ce moment \u2014 soutenu par des donn\u00e9es en temps r\u00e9el de \
{c['total_countries']} pays.

---

## Qu\u2019est-ce que \u00ab\u00a0{c['keyword_en']}\u00a0\u00bb\u00a0?

**\"{c['keyword_en']}\"** est un sujet de {c['category_label'].lower()} qui a gravi les sommets des classements de recherche mondiale aujourd\u2019hui. \
Il appartient \u00e0 la cat\u00e9gorie **{c['category_label']}** et porte une Temp\u00e9rature de Tendance de **{c['top_temperature']}\u00b0T** sur l\u2019\u00e9chelle 0\u2013100 de TrendPulse \
\u2014 indiquant {tdesc}.

Le sujet est principalement originaire de **{c['top_country_name']}** mais s\u2019est rapidement r\u00e9pandu au-del\u00e0 des fronti\u00e8res, \
gagnant une traction mesurable en {other_countries}, et au-del\u00e0. \
Cette dynamique transfronti\u00e8re est ce qui s\u00e9pare une v\u00e9ritable tendance mondiale d\u2019un fait divers local.

### Statistiques Cl\u00e9s

| Indicateur | Valeur |
|---|---|
| Volume de recherche | {c['volume']} |
| Temp\u00e9rature de tendance | {c['top_temperature']}\u00b0T / 100 |
| Cat\u00e9gorie | {c['category_label']} |
| Pays leader | {top_flag} {c['top_country_name']} |
| Pays suivis | {len(c['countries_list'])} / {c['total_countries']} |
| Source de donn\u00e9es | {src} |
| Derni\u00e8re mise \u00e0 jour | {c['date_str']} |{yt_line}
---

## Pourquoi \u00ab\u00a0{c['keyword_en']}\u00a0\u00bb est-il en tendance aujourd\u2019hui\u00a0?

{why}

Au-del\u00e0 des facteurs sp\u00e9cifiques \u00e0 la cat\u00e9gorie, l\u2019ampleur de **\"{c['keyword_en']}\"** aujourd\u2019hui est remarquable. \
\u00catre en tendance dans {len(c['countries_list'])} pays simultan\u00e9ment signifie que ce sujet a atteint ce que les analystes appellent la \u00ab\u00a0vitesse d\u2019\u00e9chappement\u00a0\u00bb \
\u2014 le point o\u00f9 le partage organique et la couverture m\u00e9diatique se renforcent mutuellement dans une boucle auto-amplifiante. \
\u00c0 {c['top_temperature']}\u00b0T, cela figure parmi les tendances les plus intenses suivies dans notre r\u00e9seau aujourd\u2019hui.

\U0001f50d **V\u00e9rifiez cette tendance vous-m\u00eame\u00a0:** \
[Explorer \u00ab\u00a0{c['keyword_en']}\u00a0\u00bb sur Google Trends]({c['google_trends_url']})

---

## Quels pays recherchent \u00ab\u00a0{c['keyword_en']}\u00a0\u00bb\u00a0?

TrendPulse surveille l\u2019activit\u00e9 de recherche dans **{c['total_countries']} pays** en temps r\u00e9el. \
Voici les pays o\u00f9 **\"{c['keyword_en']}\"** g\u00e9n\u00e8re un int\u00e9r\u00eat de recherche actif aujourd\u2019hui\u00a0:

{countries_md}

### O\u00f9 le Signal est le Plus Fort

Le signal de recherche dominant provient de **{c['top_country_name']}**, qui m\u00e8ne la conversation mondiale \
sur **\"{c['keyword_en']}\"**. La diffusion dans {len(c['countries_list'])} pays indique \
que ce sujet a transcend\u00e9 l\u2019int\u00e9r\u00eat local et est entr\u00e9 dans le domaine de la v\u00e9ritable culture mondiale.

Quand une tendance atteint ce niveau de diffusion g\u00e9ographique, cela signale une forte couverture m\u00e9diatique, un partage viral sur les r\u00e9seaux sociaux, ou un \u00e9v\u00e9nement culturellement significatif qui r\u00e9sonne aupr\u00e8s des audiences du monde entier, quelle que soit la langue ou la localisation.

\U0001f5fa\ufe0f **Voir sur la carte\u00a0:** \
[Voir la Carte Mondiale des Tendances Interactive]({c['site_url']})

---

## Donn\u00e9es de Tendance et Statistiques D\u00e9taill\u00e9es

D\u00e9taillage statistique complet de la tendance **\"{c['keyword_en']}\"** au {c['date_str']}\u00a0:

| Indicateur | Valeur |
|---|---|
| Pic de volume de recherche | {c['volume']} |
| Temp\u00e9rature de tendance | {c['top_temperature']}\u00b0T |
| Signification de la temp\u00e9rature | {tdesc.capitalize()} |
| Cat\u00e9gorie principale | {c['category_label']} |
| Port\u00e9e mondiale | {len(c['countries_list'])} pays |
| Total pays surveill\u00e9s | {c['total_countries']} |

**\u00c0 propos de la Temp\u00e9rature de Tendance\u00a0:** Le score propri\u00e9taire de TrendPulse (0\u2013100) combine volume de recherche, couverture g\u00e9ographique et vitesse en une seule m\u00e9trique d\u2019intensit\u00e9. Un score de {c['top_temperature']}\u00b0T signifie {tdesc}.

---

## Qu\u2019est-ce qui D\u2019Autre Est en Tendance en ce Moment\u00a0?

Tandis que **\"{c['keyword_en']}\"** domine la sc\u00e8ne mondiale, ces sujets montent \u00e9galement rapidement \
dans notre r\u00e9seau de {c['total_countries']} pays\u00a0:

{rising_md}

Chacun d\u2019eux repr\u00e9sente un signal en temps r\u00e9el de millions de personnes qui recherchent simultan\u00e9ment. La vari\u00e9t\u00e9 des sujets refl\u00e8te l\u2019ampleur de la conversation num\u00e9rique mondiale qui se d\u00e9roule en ce moment.

\U0001f4ca **Explorez toutes les tendances en direct\u00a0:** [Ouvrir la Carte Mondiale des Tendances]({c['site_url']})

---

## Le Paysage de Recherche Mondial d\u2019Aujourd\u2019hui par Cat\u00e9gorie

Comment les sujets tendance d\u2019aujourd\u2019hui se r\u00e9partissent entre les grandes cat\u00e9gories de contenu\u00a0:

{cat_md}

Cette photo instantan\u00e9e capture ce que des millions de personnes dans {c['total_countries']} pays recherchent activement en ce moment. La cat\u00e9gorie **{c['category_label']}** est particuli\u00e8rement active aujourd\u2019hui, port\u00e9e en grande partie par **\"{c['keyword_en']}\"** et les recherches \u00e9troitement li\u00e9es.

---

## Foire Aux Questions

### Qu\u2019est-ce que \u00ab\u00a0{c['keyword_en']}\u00a0\u00bb\u00a0?

**\"{c['keyword_en']}\"** est actuellement la recherche #1 \u00e0 l\u2019\u00e9chelle mondiale, suivie dans \
{len(c['countries_list'])} pays le {c['date_str']}. Il appartient \u00e0 la cat\u00e9gorie {c['category_label']} \
et g\u00e9n\u00e8re {c['volume']} recherches dans le seul pays leader. \
Visitez la [carte des tendances en direct]({c['site_url']}) pour explorer les donn\u00e9es g\u00e9ographiques en temps r\u00e9el.

### Pourquoi \u00ab\u00a0{c['keyword_en']}\u00a0\u00bb est-il en tendance aujourd\u2019hui\u00a0?

**\"{c['keyword_en']}\"** a atteint le sommet des recherches mondiales gr\u00e2ce \u00e0 sa rapide propagation dans \
{len(c['countries_list'])} pays, avec une Temp\u00e9rature de Tendance de {c['top_temperature']}\u00b0T \u2014 \
indiquant {tdesc}. Cette vague dans plusieurs pays signale g\u00e9n\u00e9ralement un \u00e9v\u00e9nement viral, une histoire de derni\u00e8re minute \
ou un moment culturel important. Consultez [Google Trends]({c['google_trends_url']}) pour le contexte historique.

### Quel pays recherche le plus \u00ab\u00a0{c['keyword_en']}\u00a0\u00bb\u00a0?

Selon les donn\u00e9es en temps r\u00e9el de TrendPulse, **{c['top_country_name']}** {top_flag} est le pays leader pour les recherches sur **\"{c['keyword_en']}\"** aujourd\u2019hui, avec {c['volume']} requ\u00eates enregistr\u00e9es. La tendance s\u2019est depuis propag\u00e9e \u00e0 {max(0, len(c['countries_list']) - 1)} pays suppl\u00e9mentaires. Explorez la [carte interactive]({c['site_url']}) pour voir la r\u00e9partition g\u00e9ographique compl\u00e8te.

### Comment TrendPulse mesure-t-il l\u2019intensit\u00e9 de la tendance mondiale\u00a0?

TrendPulse collecte des donn\u00e9es en temps r\u00e9el de **{c['total_countries']} pays** chaque heure, \
en agr\u00e9geant les signaux de Google Search Trends, YouTube, Apple Music Charts et des actualit\u00e9s mondiales. \
Notre score de **Temp\u00e9rature de Tendance** (0\u2013100) combine volume de recherche, couverture g\u00e9ographique et vitesse \
pour produire une seule m\u00e9trique d\u2019intensit\u00e9 pour chaque sujet tendance mondial.

### O\u00f9 puis-je explorer plus de donn\u00e9es sur les tendances mondiales\u00a0?

Vous pouvez explorer les tendances mondiales en direct \u2014 y compris les analyses par pays, les filtres de cat\u00e9gorie et les mises \u00e0 jour horaires \u2014 sur [Global Trend Map]({c['site_url']}). Nous suivons les tendances dans {c['total_countries']} pays, mis \u00e0 jour chaque heure. Parcourez notre [blog de tendances quotidiennes]({c['site_url']}/blog) pour des analyses approfondies.

---

## Restez en Avance sur Chaque Tendance Mondiale

**\"{c['keyword_en']}\"** est l\u2019une des centaines de tendances surveill\u00e9es en ce moment dans \
{c['total_countries']} pays. Que vous soyez chercheur, journaliste, cr\u00e9ateur de contenu, \
marketeur ou simplement curieux de ce que pense le monde \u2014 TrendPulse vous donne \
un acc\u00e8s instantan\u00e9 au pouls mondial.

\U0001f449 **[Explorer la Carte Mondiale des Tendances en Direct]({c['site_url']})** \u2014 mise \u00e0 jour chaque heure

\U0001f4f0 **[Lire plus d\u2019analyses de tendances]({c['site_url']}/blog)** \u2014 analyses quotidiennes des tendances #1 mondiales

*Donn\u00e9es collect\u00e9es le {c['date_str']}. Toutes les tendances se mettent \u00e0 jour toutes les heures. \
Les scores de Temp\u00e9rature de Tendance refl\u00e8tent les donn\u00e9es au moment de la collecte.*
""")

    # ── German ────────────────────────────────────────────────────────────────

    def de_title(c):
        return f"Warum liegt \"{c['keyword_en']}\" weltweit im Trend? Analyse vom {c['date_str']}"

    def de_excerpt(c):
        return (
            f"\"{c['keyword_en']}\" ist am {c['date_str']} die meistgesuchte Suchanfrage weltweit, "
            f"mit {c['volume']} Suchen in {c['top_country_name']} und Aktivit\u00e4t in "
            f"{len(c['countries_list'])} L\u00e4ndern. Erfahren Sie, was diesen globalen Trend antreibt."
        )

    def de_body(c):
        countries_md = "\n".join(f"- {f} **{n}**" for f, n in c["countries_list"])
        rising_md = "\n".join(
            f"- **{kw}** \u2014 {cn} ({vol})" for kw, cn, vol in c["rising_list"]
        ) or "- Keine aufsteigenden Trenddaten verf\u00fcgbar."
        cat_md = "\n".join(
            f"- **{k.capitalize()}**: {v} aktive Trends"
            for k, v in sorted(c["cat_breakdown"].items(), key=lambda x: -x[1]) if v > 0
        ) or "- Kategoriedaten werden aktualisiert..."
        yt_line = (
            f"\n\n\U0001f4fa **Auf YouTube ansehen:** [{c['keyword_en']}]({c['youtube_url']})\n"
            if c.get("youtube_url") else ""
        )
        top_flag = c["countries_list"][0][0] if c["countries_list"] else "\U0001f310"
        other_countries = ", ".join(n for _, n in c["countries_list"][1:4]) if len(c["countries_list"]) > 1 else "mehrere Regionen"

        t = c["top_temperature"]
        if t >= 90:
            tdesc = "ein au\u00dferordentlich viraler Trend mit massiver globaler Reichweite"
        elif t >= 75:
            tdesc = "ein sehr hei\u00dfer Trend mit starkem internationalem Schwung"
        elif t >= 60:
            tdesc = "ein warmer und wachsender Trend, der weltweit an Dynamik gewinnt"
        elif t >= 40:
            tdesc = "ein aufsteigender Trend, der globales Suchinteresse weckt"
        else:
            tdesc = "ein aufkommendes Thema, das beginnt, globale Aufmerksamkeit zu erregen"

        src = {
            "youtube": "YouTube Trends",
            "apple_music": "Apple Music Charts",
            "itunes_movies": "iTunes Film-Charts",
            "google": "Google Trends",
            "gdelt": "Globale Nachrichten (GDELT)",
            "espn": "ESPN Sport",
            "marketwatch": "MarketWatch Finanzen",
        }.get(c.get("source") or "", "Globaler Trend-Tracker")

        cat = c["category"]
        kw = c["keyword_en"]
        if cat == "music":
            why = (
                f"Musiktrends explodieren, wenn K\u00fcnstler neue Inhalte ver\u00f6ffentlichen, wichtige Auszeichnungen erhalten oder auf sozialen Plattformen viral gehen. "
                f"**\"{kw}\"** hat genau das erreicht und kombiniert den Schwung von Streaming-Plattformen mit fangetriebenem Sharing, um eine sich selbst verst\u00e4rkende Welle \u00fcber Grenzen hinweg zu erzeugen. "
                f"Wenn ein Song gleichzeitig die Spitze globaler Charts erreicht, signalisiert das sowohl kulturelle Resonanz als auch die Kraft vernetzter digitaler Zielgruppen. "
                f"Das Suchmuster in mehreren L\u00e4ndern best\u00e4tigt, dass dies ein wahrhaft globaler Musikmoment ist, kein regionales Ph\u00e4nomen, das auf einen einzigen Markt beschr\u00e4nkt ist."
            )
        elif cat == "movies":
            why = (
                f"Unterhaltungstrends erreichen ihren H\u00f6hepunkt rund um gro\u00dfe Trailer-Ver\u00f6ffentlichungen, Kinostarts oder Preisverleihungsmomente. "
                f"**\"{kw}\"** hat heute die Aufmerksamkeit des weltweiten Publikums auf sich gezogen und zeigt, wie die globale Filmindustrie Zuschauer \u00fcber Sprachen und Kulturen hinweg vereint. "
                f"Wenn ein Titel gleichzeitig in Dutzenden von L\u00e4ndern Trends erzeugt, deutet das entweder auf eine hei\u00df erwartete Ver\u00f6ffentlichung oder einen viralen Marketingmoment hin, der geografische Grenzen \u00fcberschritten hat."
            )
        elif cat == "tech":
            why = (
                f"Technologiethemen liegen im Trend, wenn bedeutende Produktlaunches, gro\u00dfe Ank\u00fcndigungen oder Kontroversen in der Tech-Welt auftauchen. "
                f"**\"{kw}\"** hat heute globale Aufmerksamkeit erregt, was entweder auf eine gro\u00dfe Produktenth\u00fcllung, eine Branchenentwicklung oder eine virale Tech-Geschichte hindeutet, die weit \u00fcber ihr urspr\u00fcngliches Publikum hinaus verbreitet wurde. "
                f"Das Suchmuster in mehreren L\u00e4ndern weist auf ein global relevantes Tech-Ereignis hin, das gleichzeitig in verschiedenen M\u00e4rkten und Nutzergemeinschaften Anklang findet."
            )
        elif cat == "sports":
            why = (
                f"Sporttrends steigen rund um gro\u00dfe Spielergebnisse, Turnier-Meilensteine oder Eilmeldungen \u00fcber prominente Athleten an. "
                f"Die globale Suchaktivit\u00e4t rund um **\"{kw}\"** deutet auf ein bedeutendes Sportereignis oder eine Ank\u00fcndigung hin, die auf internationalen M\u00e4rkten Anklang findet. "
                f"Sport hat eine einzigartige F\u00e4higkeit, Sprachbarrieren zu \u00fcberwinden und gleichzeitiges Engagement weltweit zu erzeugen, was Trends in mehreren L\u00e4ndern zu einem starken Signal f\u00fcr einen wirklich wichtigen Moment im globalen Sport macht."
            )
        elif cat == "finance":
            why = (
                f"Finanzthemen liegen w\u00e4hrend Marktvolatibilit\u00e4t, wichtigen Wirtschaftsank\u00fcndigungen oder viralen Investitionsgeschichten im Trend. "
                f"Das globale Interesse an **\"{kw}\"** heute k\u00f6nnte wirtschaftliche Unsicherheit, ein marktbewegendes Ereignis oder eine Finanzgeschichte widerspiegeln, die von Nischeninvestorenkreisen in das allgemeine \u00f6ffentliche Bewusstsein \u00fcbergegangen ist. "
                f"Multi-L\u00e4nder-Trends bei Finanzthemen signalisieren oft eine breitere makro\u00f6konomische Bedeutung, die Menschen \u00fcber Investoren und H\u00e4ndler hinaus betrifft."
            )
        else:
            why = (
                f"Nachrichten- und Informationstrends spiegeln die kollektive Neugier von Millionen von Menschen wider, die gleichzeitig auf der ganzen Welt suchen. "
                f"**\"{kw}\"** hat heute internationale Aufmerksamkeit erregt, was auf eine bedeutende Entwicklung, eine Eilmeldung oder einen viralen Moment hindeutet, der \u00fcber Kulturen und Grenzen hinweg Anklang findet. "
                f"Wenn ein einzelnes Thema gleichzeitig in Dutzenden von L\u00e4ndern Trends erzeugt, repr\u00e4sentiert es typischerweise etwas mit universeller Relevanz oder tiefem kulturellen Einfluss, der geografische Grenzen transzendiert."
            )

        return textwrap.dedent(f"""\
**\"{c['keyword_en']}\"** ist am {c['date_str']} die weltweit meistgesuchte Suchanfrage, \
mit intensiver Aktivit\u00e4t in {len(c['countries_list'])} L\u00e4ndern gleichzeitig. \
Der Anstieg wird von **{c['top_country_name']}** {top_flag} angeführt, wo {c['volume']} Suchanfragen \
verzeichnet wurden, was es zum unbestrittenen Epizentrum des globalen digitalen Interesses von heute macht.

Egal ob Sie dieses Thema \u00fcber soziale Medien, Nachrichtenzeilen oder die Nachricht eines Freundes entdeckt haben, \
Sie sind Teil eines weltweiten Moments. Im Folgenden schlüsseln wir genau auf, warum **\"{c['keyword_en']}\"** \
gerade jetzt die Aufmerksamkeit der Welt auf sich zieht \u2014 gestützt auf Echtzeit-Daten aus \
{c['total_countries']} Ländern.

---

## Was ist \u201e{c['keyword_en']}\u201c?

**\"{c['keyword_en']}\"** ist ein {c['category_label'].lower()}-Thema, das heute an die Spitze der globalen Suchrankings geklettert ist. \
Es gehört zur Kategorie **{c['category_label']}** und trägt eine Trend-Temperatur von **{c['top_temperature']}\u00b0T** auf der TrendPulse-Skala von 0\u2013100 \
\u2014 was {tdesc} anzeigt.

Das Thema stammt ursprünglich hauptsächlich aus **{c['top_country_name']}**, hat sich aber schnell über Grenzen hinweg verbreitet \
und in {other_countries} und darüber hinaus messbaren Schwung gewonnen. \
Diese grenzüberschreitende Dynamik ist das, was einen echten globalen Trend von einer lokalen Nachricht unterscheidet.

### Wichtigste Statistiken

| Kennzahl | Wert |
|---|---|
| Suchvolumen | {c['volume']} |
| Trend-Temperatur | {c['top_temperature']}\u00b0T / 100 |
| Kategorie | {c['category_label']} |
| Führendes Land | {top_flag} {c['top_country_name']} |
| Länder im Tracking | {len(c['countries_list'])} / {c['total_countries']} |
| Datenquelle | {src} |
| Zuletzt aktualisiert | {c['date_str']} |{yt_line}
---

## Warum liegt \u201e{c['keyword_en']}\u201c heute im Trend?

{why}

Über kategoriespezifische Faktoren hinaus ist das Ausmaß von **\"{c['keyword_en']}\"** heute bemerkenswert. \
In {len(c['countries_list'])} Ländern gleichzeitig zu trenden bedeutet, dass dieses Thema das erreicht hat, was Analysten als \u00abFluchtgeschwindigkeit\u00bb bezeichnen \
\u2014 den Punkt, an dem organisches Teilen und Medienberichterstattung sich gegenseitig in einer sich selbst verstärkenden Schleife verstärken. \
Mit {c['top_temperature']}\u00b0T gehört dies zu den intensivsten Trends, die heute in unserem Netzwerk verfolgt werden.

\U0001f50d **Diesen Trend selbst überprüfen:** \
[„{c['keyword_en']}" auf Google Trends erkunden]({c['google_trends_url']})

---

## Welche Länder suchen nach \u201e{c['keyword_en']}\u201c?

TrendPulse überwacht die Suchaktivität in **{c['total_countries']} Ländern** in Echtzeit. \
Hier sind die Länder, in denen **\"{c['keyword_en']}\"** heute aktives Suchinteresse generiert:

{countries_md}

### Wo das Signal am Stärksten Ist

Das dominante Suchsignal kommt aus **{c['top_country_name']}**, das die globale Konversation \
über **\"{c['keyword_en']}\"** anführt. Die Verteilung über {len(c['countries_list'])} Länder zeigt an, \
dass dieses Thema das lokale Interesse überschritten hat und in den Bereich echter globaler Kultur eingetreten ist.

Wenn ein Trend dieses Maß an geografischer Verbreitung erreicht, signalisiert das starke Medienberichterstattung, virales Social-Media-Sharing oder ein kulturell bedeutsames Ereignis, das bei Zielgruppen weltweit ankommt \u2014 unabhängig von Sprache oder Standort.

\U0001f5fa\ufe0f **Auf der Karte ansehen:** \
[Die Interaktive Globale Trendkarte anzeigen]({c['site_url']})

---

## Trenddaten & Detaillierte Statistiken

Vollständige statistische Aufschlüsselung des **\"{c['keyword_en']}\"**-Trends zum {c['date_str']}:

| Kennzahl | Wert |
|---|---|
| Spitzen-Suchvolumen | {c['volume']} |
| Trend-Temperatur | {c['top_temperature']}\u00b0T |
| Temperaturbedeutung | {tdesc.capitalize()} |
| Hauptkategorie | {c['category_label']} |
| Globale Reichweite | {len(c['countries_list'])} Länder |
| Gesamt überwachte Länder | {c['total_countries']} |

**Über Trend-Temperatur:** TrendPulse's proprietärer Score (0\u2013100) kombiniert Suchvolumen, geografische Abdeckung und Geschwindigkeit zu einer einzigen Intensitätsmetrik. Ein Score von {c['top_temperature']}\u00b0T bedeutet {tdesc}.

---

## Was Liegt Sonst Noch im Trend?

Während **\"{c['keyword_en']}\"** die globale Bühne dominiert, steigen auch diese Themen schnell \
in unserem {c['total_countries']}-Länder-Netzwerk auf:

{rising_md}

Jeder davon repräsentiert ein Echtzeitsignal von Millionen Menschen, die gleichzeitig suchen. Die Vielfalt der Themen spiegelt die Breite des globalen digitalen Gesprächs wider, das gerade stattfindet.

\U0001f4ca **Alle Live-Trends erkunden:** [Vollständige globale Trendkarte öffnen]({c['site_url']})

---

## Die Heutige Globale Suchlandschaft nach Kategorie

Wie sich die heutigen Trendthemen auf die wichtigsten Inhaltskategorien verteilen:

{cat_md}

Dieser Schnappschuss erfasst, was Millionen von Menschen in {c['total_countries']} Ländern gerade aktiv suchen. Die Kategorie **{c['category_label']}** ist heute besonders aktiv, angetrieben größtenteils von **\"{c['keyword_en']}\"** und eng verwandten Suchanfragen.

---

## Häufig Gestellte Fragen

### Was ist \u201e{c['keyword_en']}\u201c?

**\"{c['keyword_en']}\"** ist derzeit die weltweite Suchanfrage #1, verfolgt in \
{len(c['countries_list'])} Ländern am {c['date_str']}. Es gehört zur Kategorie {c['category_label']} \
und generiert {c['volume']} Suchen allein im führenden Land. \
Besuchen Sie die [Live-Trendkarte]({c['site_url']}), um geografische Echtzeit-Daten zu erkunden.

### Warum liegt \u201e{c['keyword_en']}\u201c heute im Trend?

**\"{c['keyword_en']}\"** hat die Spitze der globalen Suchen durch die schnelle Verbreitung in \
{len(c['countries_list'])} Ländern erreicht, mit einer Trend-Temperatur von {c['top_temperature']}\u00b0T \u2014 \
was {tdesc} anzeigt. Dieser Mehrländer-Anstieg signalisiert typischerweise ein virales Ereignis, eine Eilmeldung \
oder einen wichtigen kulturellen Moment. Konsultieren Sie [Google Trends]({c['google_trends_url']}) für historischen Kontext.

### Welches Land sucht am häufigsten nach \u201e{c['keyword_en']}\u201c?

Laut TrendPulse-Echtzeitdaten ist **{c['top_country_name']}** {top_flag} das führende Land bei **\"{c['keyword_en']}\"**-Suchen heute, mit {c['volume']} aufgezeichneten Anfragen. Der Trend hat sich seitdem auf {max(0, len(c['countries_list']) - 1)} weitere Länder ausgebreitet. Erkunde die [interaktive Karte]({c['site_url']}) für eine vollständige geografische Aufschlüsselung.

### Wie misst TrendPulse die globale Trend-Intensität?

TrendPulse erfasst stündlich Echtzeit-Daten aus **{c['total_countries']} Ländern** \
und aggregiert Signale aus Google Search Trends, YouTube, Apple Music Charts und globalen Nachrichtenfeeds. \
Unser **Trend-Temperatur**-Score (0\u2013100) kombiniert Suchvolumen, geografische Abdeckung und Geschwindigkeit, \
um eine einzige Intensitätsmetrik für jedes weltweite Trendthema zu erzeugen.

### Wo kann ich mehr globale Trenddaten erkunden?

Sie können Live-Globaltrends \u2014 einschließlich länderspezifischer Aufschlüsselungen, Kategoriefilter und stündlicher Updates \u2014 auf [Global Trend Map]({c['site_url']}) erkunden. Wir verfolgen Trends in {c['total_countries']} Ländern, stündlich aktualisiert. Durchsuchen Sie unseren [täglichen Trend-Blog]({c['site_url']}/blog) für detaillierte Analysen.

---

## Bleiben Sie Jedem Globalen Trend Einen Schritt Voraus

**\"{c['keyword_en']}\"** ist einer von Hunderten von Trends, die gerade jetzt in \
{c['total_countries']} Ländern überwacht werden. Ob Sie Forscher, Journalist, Content-Creator, \
Marketer oder einfach neugierig auf das sind, was die Welt denkt \u2014 TrendPulse gibt Ihnen \
sofortigen Zugang zum globalen Puls.

\U0001f449 **[Die Live Globale Trendkarte erkunden]({c['site_url']})** \u2014 stündlich aktualisiert

\U0001f4f0 **[Mehr Trendanalysen lesen]({c['site_url']}/blog)** \u2014 tägliche Analysen der weltweiten #1-Trends

*Daten erhoben am {c['date_str']}. Alle Trends werden stündlich aktualisiert. \
Trend-Temperatur-Scores spiegeln die Daten zum Zeitpunkt der Erhebung wider.*
""")

    # ── Korean ────────────────────────────────────────────────────────────────

    def kr_title(c):
        return f"\"{c['keyword_en']}\"\uc774 \uc804 \uc138\uacc4 \ud2b8\ub80c\ub4dc 1\uc704\uc778 \uc774\uc720? {c['date_str']} \uc2ec\uce35 \ubd84\uc11d"

    def kr_excerpt(c):
        return (
            f"\"{c['keyword_en']}\"\uc774 {c['date_str']} \uc804 \uc138\uacc4 \uac80\uc0c9\uc5b4 1\uc704\ub97c \uae30\ub85d\ud588\uc2b5\ub2c8\ub2e4. "
            f"{c['top_country_name']}\uc5d0\uc11c\ub9cc {c['volume']}\uac74\uc758 \uac80\uc0c9\uc774 \ubc1c\uc0dd\ud588\uc73c\uba70, "
            f"{len(c['countries_list'])}\uac1c\uad6d\uc5d0\uc11c \ub3d9\uc2dc\uc5d0 \uae09\uc0c1\uc2b9 \uc911\uc785\ub2c8\ub2e4. "
            f"\uc774 \uae00\ub85c\ubc8c \ud2b8\ub80c\ub4dc\uc758 \ubc30\uacbd\uc744 \uc2e4\uc2dc\uac04 \ub370\uc774\ud130\ub85c \ubd84\uc11d\ud569\ub2c8\ub2e4."
        )

    def kr_body(c):
        countries_md = "\n".join(f"- {f} **{n}**" for f, n in c["countries_list"])
        rising_md = "\n".join(
            f"- **{kw}** \u2014 {cn} ({vol})" for kw, cn, vol in c["rising_list"]
        ) or "- \uc0c1\uc2b9 \ud2b8\ub80c\ub4dc \ub370\uc774\ud130 \uc5c6\uc74c"
        cat_md = "\n".join(
            f"- **{k.capitalize()}**: {v}\uac1c \ud2b8\ub80c\ub4dc"
            for k, v in sorted(c["cat_breakdown"].items(), key=lambda x: -x[1]) if v > 0
        ) or "- \uce74\ud14c\uace0\ub9ac \ub370\uc774\ud130 \uc5c5\ub370\uc774\ud2b8 \uc911..."
        yt_line = (
            f"\n\n\U0001f4fa **YouTube\uc5d0\uc11c \ubcf4\uae30:** [{c['keyword_en']}]({c['youtube_url']})\n"
            if c.get("youtube_url") else ""
        )
        top_flag = c["countries_list"][0][0] if c["countries_list"] else "\U0001f310"
        other_countries = ", ".join(n for _, n in c["countries_list"][1:4]) if len(c["countries_list"]) > 1 else "\uc5ec\ub7ec \uc9c0\uc5ed"

        t = c["top_temperature"]
        if t >= 90:
            tdesc = "\uac70\ub300\ud55c \uae00\ub85c\ubc8c \ub3c4\ub2ec\ubc94\uc704\ub97c \uac00\uc9c4 \uc608\uc678\uc801\uc73c\ub85c \ubc14\uc774\ub7f4\ud55c \ud2b8\ub80c\ub4dc"
        elif t >= 75:
            tdesc = "\uac15\ud55c \uad6d\uc81c\uc801 \ubaa8\uba58\ud140\uc744 \uac00\uc9c4 \ub9e4\uc6b0 \ub728\uac70\uc6b4 \ud2b8\ub80c\ub4dc"
        elif t >= 60:
            tdesc = "\uc804 \uc138\uacc4\uc801\uc73c\ub85c \uacac\uc778\ub825\uc744 \uc5bb\uace0 \uc788\ub294 \ub530\ub73b\ud558\uace0 \uc131\uc7a5\ud558\ub294 \ud2b8\ub80c\ub4dc"
        elif t >= 40:
            tdesc = "\uc804 \uc138\uacc4\uc801\uc73c\ub85c \uac80\uc0c9 \uad00\uc2ec\uc744 \ub192\uc774\uace0 \uc788\ub294 \uc0c1\uc2b9 \ud2b8\ub80c\ub4dc"
        else:
            tdesc = "\uae00\ub85c\ubc8c \uad00\uc2ec\uc744 \ud3ec\ucc29\ud558\uae30 \uc2dc\uc791\ud55c \uc2e0\ud765 \uc8fc\uc81c"

        src = {
            "youtube": "YouTube \ud2b8\ub80c\ub4dc",
            "apple_music": "Apple Music \ucc28\ud2b8",
            "itunes_movies": "iTunes \uc601\ud654 \ucc28\ud2b8",
            "google": "Google \uac80\uc0c9 \ud2b8\ub80c\ub4dc",
            "gdelt": "\uae00\ub85c\ubc8c \ub274\uc2a4 (GDELT)",
            "espn": "ESPN \uc2a4\ud3ec\uce20",
            "marketwatch": "MarketWatch \uae08\uc735",
        }.get(c.get("source") or "", "\uae00\ub85c\ubc8c \ud2b8\ub80c\ub4dc \ud2b8\ub798\ucee4")

        cat = c["category"]
        kw = c["keyword_en"]
        if cat == "music":
            why = (
                f"\uc74c\uc545 \ud2b8\ub80c\ub4dc\ub294 \uc544\ud2f0\uc2a4\ud2b8\uac00 \uc0c8\ub85c\uc6b4 \ucf58\ud150\uce20\ub97c \ucd9c\uc2dc\ud558\uac70\ub098, \uc8fc\uc694 \uc2dc\uc0c1\uc2dd\uc5d0\uc11c \uc778\uc815\ubc1b\uac70\ub098, \uc18c\uc15c \ud50c\ub7ab\ud3fc\uc5d0\uc11c \ubc14\uc774\ub7f4\ub420 \ub54c \ud3ed\ubc1c\ud569\ub2c8\ub2e4. "
                f"**\"{kw}\"**\uc774 \ubc14\ub85c \uadf8\ub7f0 \uacbd\uc6b0\ub85c, \uc2a4\ud2b8\ub9ac\ubc0d \ud50c\ub7ab\ud3fc\uc758 \ubaa8\uba58\ud140\uacfc \ud300 \uc8fc\ub3c4 \uacf5\uc720\uac00 \uacb0\ud569\ub418\uc5b4 \uad6d\uacbd\uc744 \ucd08\uc6d4\ud55c \uc790\uae30 \uc99d\ud3ed \uc11c\uc9c0\ub97c \ub9cc\ub4e4\uc5b4\ub0c8\uc2b5\ub2c8\ub2e4. "
                f"\ud55c \uace1\uc774 \ub3d9\uc2dc\uc5d0 \uae00\ub85c\ubc8c \ucc28\ud2b8 \uc815\uc0c1\uc5d0 \uc624\ub97c \ub54c, \uc774\ub294 \ubb38\ud654\uc801 \uacf5\uba85\uacfc \uc5f0\uacb0\ub41c \ub514\uc9c0\ud138 \uccad\uc911\uc758 \ud798\uc744 \ubaa8\ub450 \ubcf4\uc5ec\uc90d\ub2c8\ub2e4. "
                f"\ub2e4\uad6d\uc801 \uac80\uc0c9 \ud328\ud134\uc740 \uc774\uac83\uc774 \ub2e8\uc77c \uc2dc\uc7a5\uc5d0 \uad6d\ud55c\ub41c \uc9c0\uc5ed \ud604\uc0c1\uc774 \uc544\ub2cc, \uc9c4\uc815\ud55c \uae00\ub85c\ubc8c \uc74c\uc545 \uc21c\uac04\uc784\uc744 \ud655\uc778\uc2dc\ucf1c \uc90d\ub2c8\ub2e4."
            )
        elif cat == "movies":
            why = (
                f"\uc5d4\ud130\ud14c\uc778\uba3c\ud2b8 \ud2b8\ub80c\ub4dc\ub294 \ub300\ud615 \ud2b8\ub808\uc77c\ub7ec \uacf5\uac1c, \uadf9\uc7a5 \uac1c\ubd09 \ub610\ub294 \uc2dc\uc0c1\uc2dd \uc21c\uac04\uc5d0 \uc808\uc815\uc5d0 \ub2ec\ud569\ub2c8\ub2e4. "
                f"**\"{kw}\"**\uc740 \uc624\ub298 \uc804 \uc138\uacc4 \uad00\uac1d\uc758 \uc8fc\ubaa9\uc744 \uc7a1\uc558\uc73c\uba70, \uae00\ub85c\ubc8c \uc601\ud654 \uc0b0\uc5c5\uc774 \uc5b4\ub5bb\uac8c \uc5b8\uc5b4\uc640 \ubb38\ud654\ub97c \ub118\uc5b4 \uad00\uac1d\uc744 \uc5f0\uacb0\ud558\ub294\uc9c0 \ubcf4\uc5ec\uc90d\ub2c8\ub2e4. "
                f"\ud55c \uc791\ud488\uc774 \ub3d9\uc2dc\uc5d0 \uc218\uc2ed \uac1c\uad6d\uc5d0\uc11c \ud2b8\ub80c\ub4dc\uad00련\ub41c\ub2e4\uba74, \ub192\uc740 \uae30\ub300\ub97c \ubc1b\ub294 \uac1c\ubd09\uc774\uac70\ub098 \uc9c0\ub9ac\uc801 \uacbd\uacc4\ub97c \ub118\uc5b4 \uc8fc\ub958 \uae00\ub85c\ubc8c \ub300\ud654\uc5d0 \uc9c4\uc785\ud55c \ubc14\uc774\ub7f4 \ub9c8\ucf00\ud305 \uc21c\uac04\uc784\uc744 \uc2dc\uc0ac\ud569\ub2c8\ub2e4."
            )
        elif cat == "tech":
            why = (
                f"\uae30\uc220 \uc8fc\uc81c\ub294 \uc911\uc694\ud55c \uc81c\ud488 \ucd9c\uc2dc, \uc8fc\uc694 \ubc1c\ud45c \ub610\ub294 \uae30\uc220 \uc138\uacc4\uc5d0\uc11c \ub17c\ub780\uc774 \ud2b8\ub80c\ub4dc\ud560 \ub54c \ub5a0\uc624\ub985\ub2c8\ub2e4. "
                f"**\"{kw}\"**\uc740 \uc624\ub298 \uae00\ub85c\ubc8c \uc8fc\ubaa9\uc744 \uc7a1\uc558\uc73c\uba70, \ub300\uaddc\ubaa8 \uc81c\ud488 \uacf5\uac1c, \uc0b0\uc5c5 \ub3d9\ud5a5 \ub610\ub294 \uc6d0\ub798 \uccad\uc911\uc744 \ud6e8\uc52c \ub118\uc5b4 \ud655\uc0b0\ub41c \ubc14\uc774\ub7f4 \uae30\uc220 \uc774\uc57c\uae30\ub97c \uc2dc\uc0ac\ud569\ub2c8\ub2e4. "
                f"\uc5ec\ub7ec \ub098\ub77c\uc758 \uac80\uc0c9 \ud328\ud134\uc740 \ub2e4\uc591\ud55c \uc2dc\uc7a5\uacfc \uc0ac\uc6a9\uc790 \ucee4\ubba4\ub2c8\ud2f0\uc5d0\uc11c \ub3d9\uc2dc\uc5d0 \uacf5\uba85\ud558\ub294 \uae00\ub85c\ubc8c\uc801\uc73c\ub85c \uad00\ub828\ub41c \uae30\uc220 \uc774\ubca4\ud2b8\ub97c \ub098\ud0c0\ub0c5\ub2c8\ub2e4."
            )
        elif cat == "sports":
            why = (
                f"\uc2a4\ud3ec\uce20 \ud2b8\ub80c\ub4dc\ub294 \ub300\ud615 \uacbd\uae30 \uacb0\uacfc, \ud1a0\ub108\uba3c\ud2b8 \uc774\uc815\ud45c \ub610\ub294 \uace0\ud504\ub85c\ud30c\uc77c \uc120\uc218\uc5d0 \ub300\ud55c \uc18d\ubcf4 \ub4f1\uc774 \uc788\uc744 \ub54c \uae09\uc99d\ud569\ub2c8\ub2e4. "
                f"**\"{kw}\"** \uc8fc\ubcc0\uc758 \uae00\ub85c\ubc8c \uac80\uc0c9 \ud65c\ub3d9\uc740 \uad6d\uc81c \uc2dc\uc7a5\uc5d0\uc11c \uacf5\uba85\ud558\ub294 \uc911\uc694\ud55c \uc2a4\ud3ec\uce20 \uc774\ubca4\ud2b8\ub098 \ubc1c\ud45c\ub97c \uc2dc\uc0ac\ud569\ub2c8\ub2e4. "
                f"\uc2a4\ud3ec\uce20\ub294 \uc5b8\uc5b4 \uc7a5\ubcbd\uc744 \ucd08\uc6d4\ud558\uace0 \uc804 \uc138\uacc4\uc801\uc73c\ub85c \ub3d9\uc2dc \ucc38\uc5ec\ub97c \uc774\ub048\ub0b4\ub294 \ud2b9\ubcc4\ud55c \ub2a5\ub825\uc774 \uc788\uc5b4, \ub2e4\uad6d\uc801 \ud2b8\ub80c\ub4dc\uac00 \uae00\ub85c\ubc8c \uccb4\uc721\uc5d0\uc11c \uc9c4\uc815\uc73c\ub85c \uc911\uc694\ud55c \uc21c\uac04\uc758 \uac15\ub825\ud55c \uc2e0\ud638\uac00 \ub429\ub2c8\ub2e4."
            )
        elif cat == "finance":
            why = (
                f"\uae08\uc735 \uc8fc\uc81c\ub294 \uc2dc\uc7a5 \ubcc0\ub3d9\uc131, \uc8fc\uc694 \uacbd\uc81c \ubc1c\ud45c \ub610\ub294 \ubc14\uc774\ub7f4 \ud22c\uc790 \uc774\uc57c\uae30 \ub3d9\uc548 \ud2b8\ub80c\ub4dc\ud569\ub2c8\ub2e4. "
                f"**\"{kw}\"**\uc5d0 \ub300\ud55c \uc624\ub298\uc758 \uae00\ub85c\ubc8c \uad00\uc2ec\uc740 \uacbd\uc81c\uc801 \ubd88\ud655\uc2e4\uc131, \uc2dc\uc7a5 \uc6c0\uc9c1\uc784 \uc774\ubca4\ud2b8, \ub610\ub294 \uc0c1\uc7a5 \ud22c\uc790\uc790 \uadf8\ub8f9\uc5d0\uc11c \uc8fc\ub958 \ub300\uc911 \uc758\uc2dd\uc73c\ub85c \ub118\uc5b4 \uc2e0\uc774\ud55c \uae08\uc735 \uc774\uc57c\uae30\ub97c \ubc18\uc601\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4. "
                f"\uae08\uc735 \uc8fc\uc81c\uc758 \ub2e4\uad6d\uc801 \ud2b8\ub80c\ub4dc\ub294 \uc885\uc885 \ud22c\uc790\uc790\uc640 \ud2b8\ub808\uc774\ub354\ub97c \ub118\uc5b4 \uc0ac\ub78c\ub4e4\uc5d0\uac8c \uc601\ud5a5\uc744 \ubbf8\uce58\ub294 \ub354 \ub113\uc740 \uac70\uc2dc\uacbd\uc81c\uc801 \uc911\uc694\uc131\uc744 \ub098\ud0c0\ub0c5\ub2c8\ub2e4."
            )
        else:
            why = (
                f"\ub274\uc2a4\uc640 \uc815\ubcf4 \ud2b8\ub80c\ub4dc\ub294 \uc804 \uc138\uacc4\uc5d0\uc11c \ub3d9\uc2dc\uc5d0 \uac80\uc0c9\ud558\ub294 \uc218\ubc31\ub9cc \uba85\uc758 \uc9d1\ub2e8\uc801 \ud638\uae30\uc2ec\uc744 \ubc18\uc601\ud569\ub2c8\ub2e4. "
                f"**\"{kw}\"**\uc740 \uc624\ub298 \uad6d\uc81c\uc801 \uc8fc\ubaa9\uc744 \uc7a1\uc558\uc73c\uba70, \ubb38\ud654\uc640 \uad6d\uacbd\uc744 \ub118\uc5b4 \uacf5\uba85\ud558\ub294 \uc911\uc694\ud55c \uc5c5\ub370\uc774\ud2b8, \uc18d\ubcf4 \ub610\ub294 \ubc14\uc774\ub7f4 \uc21c\uac04\uc744 \uc2dc\uc0ac\ud569\ub2c8\ub2e4. "
                f"\ub2e8\uc77c \uc8fc\uc81c\uac00 \ub3d9\uc2dc\uc5d0 \uc218\uc2ed \uac1c\uad6d\uc5d0\uc11c \ud2b8\ub80c\ub4dc\ud560 \ub54c, \uc774\ub294 \uc77c\ubc18\uc801\uc73c\ub85c \ubcf4\ud3b8\uc801 \uad00\ub828\uc131\uc774\ub098 \uc9c0\ub9ac\uc801 \uacbd\uacc4\ub97c \ucd08\uc6d4\ud558\ub294 \uae4a\uc740 \ubb38\ud654\uc801 \uc601\ud5a5\uc744 \uac00\uc9c4 \ubb34\uc5b8\uac00\ub97c \ub098\ud0c0\ub0c5\ub2c8\ub2e4."
            )

        return textwrap.dedent(f"""\
**\"{c['keyword_en']}\"**\uc740 {c['date_str']} \uae30\uc900 \uc804 \uc138\uacc4 \uac80\uc0c9\uc5b4 1\uc704\ub97c \uae30\ub85d\ud55c \ud0a4\uc6cc\ub4dc\ub85c, \
{len(c['countries_list'])}\uac1c\uad6d\uc5d0\uc11c \ub3d9\uc2dc\uc5d0 \uac15\ub825\ud55c \ud65c\ub3d9\uc744 \uc77c\uc73c\ud0a4\uace0 \uc788\uc2b5\ub2c8\ub2e4. \
\uc0c1\uc2b9\uc740 **{c['top_country_name']}** {top_flag}\uc774 \uc8fc\ub3c4\ud558\uace0 \uc788\uc73c\uba70, \uc774 \uad6d\uac00\uc5d0\uc11c\ub9cc {c['volume']}\uac74\uc758 \uac80\uc0c9\uc774 \
\uae30\ub85d\ub418\uc5b4 \uc624\ub298 \uae00\ub85c\ubc8c \ub514\uc9c0\ud138 \uad00\uc2ec\uc758 \ud2bc\ub9bc\uc5c6\ub294 \uc9c4\uc6d0\uc9c0\uac00 \ub418\uace0 \uc788\uc2b5\ub2c8\ub2e4.

\uc18c\uc15c\ubbf8\ub514\uc5b4, \ub274\uc2a4 \ud5e4\ub4dc\ub77c\uc778, \ub610\ub294 \uce5c\uad6c\uc758 \uba54\uc2dc\uc9c0\ub97c \ud1b5\ud574 \uc774 \uc8fc\uc81c\ub97c \ub9c8\uc8fc\ucce4\ub4e0 \uac04\uc5d0, \
\ub2f9\uc2e0\uc740 \uc790\uae08 \uc804 \uc138\uacc4\uc801 \uc21c\uac04\uc758 \uc77c\ubd80\uc785\ub2c8\ub2e4. \uc544\ub798\uc5d0\uc11c {c['total_countries']}\uac1c\uad6d\uc758 \uc2e4\uc2dc\uac04 \ub370\uc774\ud130\ub97c \ubc14\ud0d5\uc73c\ub85c \
**\"{c['keyword_en']}\"**\uc774 \uc9c0\uae08 \uc138\uacc4\uc758 \uc8fc\ubaa9\uc744 \ubc1b\ub294 \uc774\uc720\ub97c \uc0c1\uc138\ud788 \ubd84\uc11d\ud569\ub2c8\ub2e4.

---

## \"{c['keyword_en']}\"란 무엇인가요?

**\"{c['keyword_en']}\"**\ub294 \uc624\ub298 \uae00\ub85c\ubc8c \uac80\uc0c9 \uc21c\uc704 \uc815\uc0c1\uc5d0 \uc624\ub978 {c['category_label'].lower()} \uc8fc\uc81c\uc785\ub2c8\ub2e4. \
**{c['category_label']}** \uce74\ud14c\uace0\ub9ac\uc5d0 \uc18d\ud558\uba70 TrendPulse\uc758 0\u2013100 \uc2a4\ucf00\uc77c\uc5d0\uc11c \
**{c['top_temperature']}\u00b0T**\uc758 \ud2b8\ub80c\ub4dc \uc628\ub3c4\ub97c \uae30\ub85d\ud558\uace0 \uc788\uc2b5\ub2c8\ub2e4\u2014\uc774\ub294 {tdesc}\ub97c \uc758\ubbf8\ud569\ub2c8\ub2e4.

\uc774 \uc8fc\uc81c\ub294 \uc8fc\ub85c **{c['top_country_name']}**\uc5d0\uc11c \uc2dc\uc791\ub418\uc5c8\uc9c0\ub9cc \uc2e0\uc18d\ud558\uac8c \uad6d\uacbd\uc744 \ub118\uc5b4, \
{other_countries} \ub4f1\uc5d0\uc11c \uce21\uc815 \uac00\ub2a5\ud55c \uc544\uc6c0\uc9c1\uc784\uc744 \uc5bb\uace0 \uc788\uc2b5\ub2c8\ub2e4. \
\uc774\ub7ec\ud55c \uad6d\uacbd \ucd08\uc6d4 \ubaa8\uba58\ud140\uc774 \uc9c4\uc815\ud55c \uae00\ub85c\ubc8c \ud2b8\ub80c\ub4dc\uc640 \uc9c0\uc5ed \ub274\uc2a4\ub97c \uad6c\ubd84\uc9d3\ub294 \ud575\uc2ec\uc785\ub2c8\ub2e4.

### 핵심 통계 요약

| \uc9c0\ud45c | \uac12 |
|---|---|
| \uac80\uc0c9\ub7c9 | {c['volume']} |
| \ud2b8\ub80c\ub4dc \uc628\ub3c4 | {c['top_temperature']}\u00b0T / 100 |
| \uce74\ud14c\uace0\ub9ac | {c['category_label']} |
| \uc8fc\uc694 \uad6d\uac00 | {top_flag} {c['top_country_name']} |
| \ucd94\uc801 \uad6d\uac00 \uc218 | {len(c['countries_list'])} / {c['total_countries']} |
| \ub370\uc774\ud130 \ucd9c\uc2a4 | {src} |
| \ub9c8\uc9c0\ub9c9 \uc5c5\ub370\uc774\ud2b8 | {c['date_str']} |{yt_line}
---

## \"{c['keyword_en']}\"은 왜 오늘 트렌드인가요?

{why}

\uce74\ud14c\uace0\ub9ac \ud2b9\uc720\uc758 \uc694\uc778\uc744 \ub118\uc5b4, \uc624\ub298 **\"{c['keyword_en']}\"**\uc758 \uaddc\ubaa8\ub294 \uc8fc\ubaa9\ud560 \ub9cc\ud569\ub2c8\ub2e4. \
{len(c['countries_list'])}\uac1c\uad6d\uc5d0\uc11c \ub3d9\uc2dc\uc5d0 \ud2b8\ub80c\ub529\ub41c\ub2e4\ub294 \uac83\uc740 \uc774 \uc8fc\uc81c\uac00 \ubd84\uc11d\uac00\ub4e4\uc774 '\ud0c8\ucd9c \uc18d\ub3c4'\ub77c\uace0 \ubd80\ub974\ub294 \uac83\uc744 \ub2ec\uc131\ud588\uc74c\uc744 \uc758\ubbf8\ud569\ub2c8\ub2e4 \u2014 \
\uc720\uae30\uc801 \uacf5\uc720\uc640 \ubbf8\ub514\uc5b4 \ubcf4\ub3c4\uac00 \uc11c\ub85c \uac15\ud654\ud558\uba70 \uc790\uae30 \uc99d\ud3ed \ub8e8\ud504\ub97c \ud615\uc131\ud558\ub294 \uc9c0\uc810. \
{c['top_temperature']}\u00b0T\uc5d0\uc11c, \uc774\ub294 \uc624\ub298 \uc6b0\ub9ac \ub124\ud2b8\uc6cc\ud06c\uc5d0\uc11c \ucd94\uc801\ub41c \uac00\uc7a5 \uac15\ub825\ud55c \ud2b8\ub80c\ub4dc \uc911 \ud558\ub098\uc785\ub2c8\ub2e4.

\U0001f50d **\uc9c1\uc811 \ud655\uc778\ud558\uae30:** \
[Google \ud2b8\ub80c\ub4dc\uc5d0\uc11c \"{c['keyword_en']}\" \ud0d0\uc0c9]({c['google_trends_url']})

---

## 어느 나라에서 \"{c['keyword_en']}\"을 검색하나요?

TrendPulse\ub294 **{c['total_countries']}\uac1c\uad6d**\uc758 \uac80\uc0c9 \ud65c\ub3d9\uc744 \uc2e4\uc2dc\uac04\uc73c\ub85c \ubaa8\ub2c8\ud130\ub9c1\ud569\ub2c8\ub2e4. \
\uc544\ub798\ub294 \uc624\ub298 **\"{c['keyword_en']}\"**\uc5d0 \ub300\ud55c \ud65c\ubc1c\ud55c \uac80\uc0c9 \uad00\uc2ec\uc774 \ud655\uc778\ub418\ub294 \uad6d\uac00\ub4e4\uc785\ub2c8\ub2e4:

{countries_md}

### 가장 강한 신호가 오는 곳

\uac00\uc7a5 \uc9c0\ubc30\uc801\uc778 \uac80\uc0c9 \uc2e0\ud638\ub294 **{c['top_country_name']}**\uc5d0\uc11c \uc624\uace0 \uc788\uc73c\uba70, \uc774 \uad6d\uac00\uac00 **\"{c['keyword_en']}\"** \uc8fc\ubcc0\uc758 \uae00\ub85c\ubc8c \ub300\ud654\ub97c \uc774\ub04c\uace0 \uc788\uc2b5\ub2c8\ub2e4. \
{len(c['countries_list'])}\uac1c\uad6d\uc5d0 \uac78\uce5c \ud655\uc0b0\uc740 \uc774 \uc8fc\uc81c\uac00 \uc9c0\uc5ed\uc801 \uad00\uc2ec\uc744 \ub118\uc5b4 \uc9c4\uc815\ud55c \uae00\ub85c\ubc8c \ubb38\ud654 \uc601\uc5ed\uc5d0 \uc9c4\uc785\ud588\uc74c\uc744 \ub098\ud0c0\ub0c5\ub2c8\ub2e4.

\ud2b8\ub80c\ub4dc\uac00 \uc774 \uc218\uc900\uc758 \uc9c0\ub9ac\uc801 \ud655\uc0b0\uc5d0 \ub3c4\ub2ec\ud558\uba74, \uac15\ud55c \ubbf8\ub514\uc5b4 \ubcf4\ub3c4, \ubc14\uc774\ub7f4 \uc18c\uc15c \ubbf8\ub514\uc5b4 \uacf5\uc720, \ub610\ub294 \uc5b8\uc5b4\ub098 \uc704\uce58\uc5d0 \uad00\uacc4\uc5c6\uc774 \uc804 \uc138\uacc4 \uc2dc\uccad\uc790\uc5d0\uac8c \uacf5\uba85\ud558\ub294 \ubb38\ud654\uc801\uc73c\ub85c \uc911\uc694\ud55c \uc774\ubca4\ud2b8\ub97c \ub098\ud0c0\ub0c5\ub2c8\ub2e4.

\U0001f5fa\ufe0f **\uc9c0\ub3c4\uc5d0\uc11c \ud655\uc778\ud558\uae30:** [\uc778\ud130\ub799\ud2f0\ube0c \uae00\ub85c\ubc8c \ud2b8\ub80c\ub4dc \ub9f5 \ubcf4\uae30]({c['site_url']})

---

## 트렌드 데이터 및 심층 통계

{c['date_str']} \uae30\uc900 **\"{c['keyword_en']}\"** \ud2b8\ub80c\ub4dc\uc758 \uc644\uc804\ud55c \ud1b5\uacc4 \ubd84\uc11d:

| \uc9c0\ud45c | \uac12 |
|---|---|
| \ucd5c\ub300 \uac80\uc0c9\ub7c9 | {c['volume']} |
| \ud2b8\ub80c\ub4dc \uc628\ub3c4 | {c['top_temperature']}\u00b0T |
| \uc628\ub3c4 \uc758\ubbf8 | {tdesc} |
| \uc8fc\uc694 \uce74\ud14c\uace0\ub9ac | {c['category_label']} |
| \uae00\ub85c\ubc8c \ubc94\uc704 | {len(c['countries_list'])}\uac1c\uad6d |
| \uc804\uccb4 \ubaa8\ub2c8\ud130\ub9c1 \uad6d\uac00 | {c['total_countries']}\uac1c\uad6d |

**\ud2b8\ub80c\ub4dc \uc628\ub3c4\uc5d0 \ub300\ud558\uc5ec:** TrendPulse\uc758 \ub3c5\uc790\uc801 \uc810\uc218(0\u2013100)\ub294 \uac80\uc0c9\ub7c9, \uc9c0\ub9ac\uc801 \ubc94\uc704, \uc18d\ub3c4\ub97c \ub2e8\uc77c \uac15\ub3c4 \uc9c0\ud45c\ub85c \uacb0\ud569\ud569\ub2c8\ub2e4. {c['top_temperature']}\u00b0T \uc810\uc218\ub294 {tdesc}\ub97c \uc758\ubbf8\ud569\ub2c8\ub2e4.

---

## 지금 또 무엇이 트렌딩 중인가요?

**\"{c['keyword_en']}\"**\uc774 \uae00\ub85c\ubc8c \ubb34\ub300\ub97c \uc9c0\ubc30\ud558\ub294 \ub3d9\uc548, \uc774 \uc8fc\uc81c\ub4e4\ub3c4 \uc6b0\ub9ac\uc758 {c['total_countries']}\uac1c\uad6d \ub124\ud2b8\uc6cc\ud06c\uc5d0\uc11c \ube60\ub974\uac8c \uc0c1\uc2b9 \uc911\uc785\ub2c8\ub2e4:

{rising_md}

\uc774 \uac01\uac01\uc740 \uc218\ubc31\ub9cc \uba85\uc774 \ub3d9\uc2dc\uc5d0 \uac80\uc0c9\ud558\ub294 \uc2e4\uc2dc\uac04 \uc2e0\ud638\ub97c \ub098\ud0c0\ub0c5\ub2c8\ub2e4. \uc8fc\uc81c\uc758 \ub2e4\uc591\uc131\uc740 \ud604\uc7ac \uc77c\uc5b4\ub098\uace0 \uc788\ub294 \uc804 \uc138\uacc4 \ub514\uc9c0\ud138 \ub300\ud654\uc758 \ud3ed\uc744 \ubc18\uc601\ud569\ub2c8\ub2e4.

\U0001f4ca **\ubaa8\ub4e0 \uc2e4\uc2dc\uac04 \ud2b8\ub80c\ub4dc \ud0d0\uc0c9:** [\uc804\uccb4 \uae00\ub85c\ubc8c \ud2b8\ub80c\ub4dc \ub9f5 \uc5f4\uae30]({c['site_url']})

---

## 오늘의 카테고리별 글로벌 검색 현황

\uc624\ub298\uc758 \ud2b8\ub80c\ub529 \uc8fc\uc81c\ub4e4\uc774 \uc8fc\uc694 \ucf58\ud150\uce20 \uce74\ud14c\uace0\ub9ac\ubcc4\ub85c \uc5b4\ub5bb\uac8c \ubd84\ud3ec\ub418\ub294\uc9c0:

{cat_md}

\uc774 \uc2a4\ub0c5\uc0f7\uc740 \ud604\uc7ac {c['total_countries']}\uac1c\uad6d \uc218\ubc31\ub9cc \uba85\uc774 \uc801\uadf9\uc801\uc73c\ub85c \uac80\uc0c9\ud558\ub294 \ub0b4\uc6a9\uc744 \ud3ec\ucc29\ud569\ub2c8\ub2e4. **{c['category_label']}** \uce74\ud14c\uace0\ub9ac\ub294 \uc624\ub298 \ud2b9\ud788 \ud65c\ubc1c\ud558\uba70, **\"{c['keyword_en']}\"** \ubc0f \ubc00\uc811\ud558\uac8c \uad00\ub828\ub41c \uac80\uc0c9\uc774 \uc8fc\uc694 \ub3d9\uc778\uc785\ub2c8\ub2e4.

---

## 자주 묻는 질문 (FAQ)

### \"{c['keyword_en']}\"이란 무엇인가요?

**\"{c['keyword_en']}\"**\uc740 \ud604\uc7ac \uc804 \uc138\uacc4 \uac80\uc0c9\uc5b4 1\uc704\ub85c, \
{c['date_str']} \uae30\uc900 {len(c['countries_list'])}\uac1c\uad6d\uc5d0\uc11c \ucd94\uc801\ub418\uace0 \uc788\uc2b5\ub2c8\ub2e4. \
{c['category_label']} \uce74\ud14c\uace0\ub9ac\uc5d0 \uc18d\ud558\uba70 \uc120\ub450 \uad6d\uac00\uc5d0\uc11c\ub9cc {c['volume']}\uac74\uc758 \uac80\uc0c9\uc774 \ubc1c\uc0dd\ud558\uace0 \uc788\uc2b5\ub2c8\ub2e4. \
[\uc2e4\uc2dc\uac04 \ud2b8\ub80c\ub4dc \ub9f5]({c['site_url']})\uc5d0\uc11c \uc9c0\ub9ac\uc801 \ub370\uc774\ud130\ub97c \ud655\uc778\ud558\uc138\uc694.

### \"{c['keyword_en']}\"은 왜 지금 트렌드인가요?

**\"{c['keyword_en']}\"**\uc740 {len(c['countries_list'])}\uac1c\uad6d\uc5d0\uc11c\uc758 \ube60\ub978 \ud655\uc0b0\uc73c\ub85c \uae00\ub85c\ubc8c \uac80\uc0c9 \uc815\uc0c1\uc5d0 \uc62c\ub790\uc73c\uba70, \
\ud2b8\ub80c\ub4dc \uc628\ub3c4 {c['top_temperature']}\u00b0T\ub97c \uae30\ub85d\ud558\uace0 \uc788\uc2b5\ub2c8\ub2e4\u2014\uc774\ub294 {tdesc}\ub97c \ub098\ud0c0\ub0c5\ub2c8\ub2e4. \
\uc774\ub7ec\ud55c \ub2e4\uad6d\uc801 \uc11c\uc9c0\ub294 \uc77c\ubc18\uc801\uc73c\ub85c \ubc14\uc774\ub7f4 \uc774\ubca4\ud2b8, \uc18d\ubcf4 \ub610\ub294 \uc911\uc694\ud55c \ubb38\ud654\uc801 \uc21c\uac04\uc744 \uc2dc\uc0ac\ud569\ub2c8\ub2e4. \
[Google \ud2b8\ub80c\ub4dc]({c['google_trends_url']})\uc5d0\uc11c \uacfc\uac70 \ub370\uc774\ud130\ub97c \ud655\uc778\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.

### 어느 나라가 \"{c['keyword_en']}\"을 가장 많이 검색하나요?

TrendPulse \uc2e4\uc2dc\uac04 \ub370\uc774\ud130\uc5d0 \ub530\ub974\uba74, **{c['top_country_name']}** {top_flag}\uc774 \uc624\ub298 **\"{c['keyword_en']}\"** \uac80\uc0c9\uc5d0\uc11c \uc120\ub450 \uad6d\uac00\ub85c, {c['volume']}\uac74\uc758 \ucffc\ub9ac\uac00 \uae30\ub85d\ub418\uc5c8\uc2b5\ub2c8\ub2e4. \uc774 \ud2b8\ub80c\ub4dc\ub294 \uc774\ud6c4 {max(0, len(c['countries_list']) - 1)}\uac1c\uc758 \ucd94\uac00 \uad6d\uac00\ub85c \ud655\uc0b0\ub418\uc5c8\uc2b5\ub2c8\ub2e4. \uc644\uc804\ud55c \uc9c0\ub9ac\uc801 \ubd84\ud3ec\ub294 [\uc778\ud130\ub799\ud2f0\ube0c \ub9f5]({c['site_url']})\uc5d0\uc11c \ud655\uc778\ud558\uc138\uc694.

### TrendPulse는 어떻게 글로벌 트렌드 강도를 측정하나요?

TrendPulse\ub294 **{c['total_countries']}\uac1c\uad6d**\uc758 \uc2e4\uc2dc\uac04 \ub370\uc774\ud130\ub97c \ub9e4\uc2dc\uac04 \uc218\uc9d1\ud558\uc5ec \
Google \uac80\uc0c9 \ud2b8\ub80c\ub4dc, YouTube, Apple Music \ucc28\ud2b8, \uae00\ub85c\ubc8c \ub274\uc2a4 \ud53c\ub4dc\ub4f1\uc758 \uc2e0\ud638\ub97c \uc9d1\uacc4\ud569\ub2c8\ub2e4. \
\uc800\ud76c **\ud2b8\ub80c\ub4dc \uc628\ub3c4** \uc810\uc218(0\u2013100)\ub294 \uac80\uc0c9\ub7c9, \uc9c0\ub9ac\uc801 \ubc94\uc704, \uc18d\ub3c4\ub97c \uacb0\ud569\ud558\uc5ec \
\uc804 \uc138\uacc4 \uac01 \ud2b8\ub80c\ub529 \uc8fc\uc81c\uc5d0 \ub300\ud55c \ub2e8\uc77c \uac15\ub3c4 \uc9c0\ud45c\ub97c \uc0dd\uc131\ud569\ub2c8\ub2e4.

### 더 많은 글로벌 트렌드 데이터를 어디서 탐색할 수 있나요?

[\uae00\ub85c\ubc8c \ud2b8\ub80c\ub4dc \ub9f5]({c['site_url']})\uc5d0\uc11c \uc2e4\uc2dc\uac04 \uae00\ub85c\ubc8c \ud2b8\ub80c\ub4dc\ub97c \ud0d0\uc0c9\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4 \u2014 \uad6d\uac00\ubcc4 \ubd84\ub958, \uce74\ud14c\uace0\ub9ac \ud544\ud130, \uc2dc\uac04\ubcc4 \uc5c5\ub370\uc774\ud2b8\ub97c \ud3ec\ud568\ud569\ub2c8\ub2e4. {c['total_countries']}\uac1c\uad6d \ud2b8\ub80c\ub4dc\ub97c \ucd94\uc801\ud558\uba70, \ub9e4\uc2dc\uac04 \uc5c5\ub370\uc774\ud2b8\ub429\ub2c8\ub2e4. \uc2ec\uce35 \ubd84\uc11d\uc744 \uc704\ud574 [\uc77c\uc77c \ud2b8\ub80c\ub4dc \ube14\ub85c\uadf8]({c['site_url']}/blog)\ub97c \ud0d0\uc0c9\ud574 \ubcf4\uc138\uc694.

---

## 모든 글로벌 트렌드를 앞서 파악하세요

**\"{c['keyword_en']}\"**\uc740 \uc9c0\uae08 \ubc14\ub85c {c['total_countries']}\uac1c\uad6d\uc5d0\uc11c \ubaa8\ub2c8\ud130\ub9c1 \uc911\uc778 \uc218\ubc31 \uac1c\uc758 \ud2b8\ub80c\ub4dc \uc911 \ud558\ub098\uc785\ub2c8\ub2e4. \
\uc5f0\uad6c\uc790, \uae30\uc790, \ucf58\ud150\uce20 \uc81c\uc791\uc790, \ub9c8\ucf00\ud130 \ub610\ub294 \ub2e8\uc21c\ud788 \uc138\uc0c1\uc774 \ub208\uc5d0 \ubb34\uc5c7\uc774 \ub208\ub9ac\ub294\uc9c0 \ud655\uc778\ud558\uace0 \uc2f6\uc740 \ubd84\uc774\ub77c\uba74 \u2014 \
TrendPulse\ub294 \uae00\ub85c\ubc8c \ud30c\ub3d9\uc5d0 \ub300\ud55c \uc989\uac01\uc801\uc778 \uc811\uadfc\uc744 \uc81c\uacf5\ud569\ub2c8\ub2e4.

\U0001f449 **[\uc2e4\uc2dc\uac04 \uae00\ub85c\ubc8c \ud2b8\ub80c\ub4dc \ub9f5 \ubcf4\uae30]({c['site_url']})** \u2014 \ub9e4\uc2dc\uac04 \uc5c5\ub370\uc774\ud2b8

\U0001f4f0 **[\ub354 \ub9ce\uc740 \ud2b8\ub80c\ub4dc \ubd84\uc11d \uc77d\uae30]({c['site_url']}/blog)** \u2014 \ub9e4\uc77c \uc138\uacc4 \ud2b8\ub80c\ub4dc 1\uc704 \uc2ec\uce35 \ubd84\uc11d

*\ub370\uc774\ud130 \uc218\uc9d1\uc77c: {c['date_str']}. \ubaa8\ub4e0 \ud2b8\ub80c\ub4dc\ub294 \ub9e4\uc2dc\uac04 \uc5c5\ub370\uc774\ud2b8\ub429\ub2c8\ub2e4. \ud2b8\ub80c\ub4dc \uc628\ub3c4 \uc810\uc218\ub294 \ub370\uc774\ud130 \uc218\uc9d1 \uc2dc\uc810\uc758 \ub370\uc774\ud130\ub97c \ubc18\uc601\ud569\ub2c8\ub2e4.*
""")

    # ── Japanese ──────────────────────────────────────────────────────────────

    def jp_title(c):
        return f"\u300c{c['keyword_en']}\u300d\u304c\u4e16\u754c\u3067\u30c8\u30ec\u30f3\u30c9\u5165\u308a\u3057\u305f\u7406\u7531\u306f\uff1f\u300a{c['date_str']}\u300b\u6df1\u5c64\u5206\u6790"

    def jp_excerpt(c):
        return (
            f"\u300c{c['keyword_en']}\u300d\u304c{c['date_str']}\u306e\u4e16\u754c\u691c\u7d22\u30e9\u30f3\u30ad\u30f31\u4f4d\u3092\u8a18\u9332\u3002"
            f"{c['top_country_name']}\u3060\u3051\u3067{c['volume']}\u4ef6\u306e\u691c\u7d22\u304c\u767a\u751f\u3057\u3001"
            f"{len(c['countries_list'])}\u304b\u56fd\u3067\u540c\u6642\u306b\u6025\u4e0a\u6607\u3002"
            f"\u3053\u306e\u30b0\u30ed\u30fc\u30d0\u30eb\u30c8\u30ec\u30f3\u30c9\u306e\u80cc\u666f\u3092\u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u30c7\u30fc\u30bf\u3067\u89e3\u8aac\u3002"
        )

    def jp_body(c):
        countries_md = "\n".join(f"- {f} **{n}**" for f, n in c["countries_list"])
        rising_md = "\n".join(
            f"- **{kw}** \u2014 {cn}\uff08{vol}\uff09" for kw, cn, vol in c["rising_list"]
        ) or "- \u4e0a\u6607\u30c8\u30ec\u30f3\u30c9\u30c7\u30fc\u30bf\u306a\u3057"
        cat_md = "\n".join(
            f"- **{k.capitalize()}**\uff1a{v}\u4ef6\u306e\u30c8\u30ec\u30f3\u30c9"
            for k, v in sorted(c["cat_breakdown"].items(), key=lambda x: -x[1]) if v > 0
        ) or "- \u30ab\u30c6\u30b4\u30ea\u30c7\u30fc\u30bf\u66f4\u65b0\u4e2d..."
        yt_line = (
            f"\n\n\U0001f4fa **YouTube\u3067\u898b\u308b\uff1a** [{c['keyword_en']}]({c['youtube_url']})\n"
            if c.get("youtube_url") else ""
        )
        top_flag = c["countries_list"][0][0] if c["countries_list"] else "\U0001f310"
        other_countries = "\u3001".join(n for _, n in c["countries_list"][1:4]) if len(c["countries_list"]) > 1 else "\u8907\u6570\u306e\u5730\u57df"

        t = c["top_temperature"]
        if t >= 90:
            tdesc = "\u5927\u898f\u6a21\u306a\u30b0\u30ed\u30fc\u30d0\u30eb\u30ea\u30fc\u30c1\u3092\u6301\u3064\u4f8b\u5916\u7684\u306b\u30d0\u30a4\u30e9\u30eb\u306a\u30c8\u30ec\u30f3\u30c9"
        elif t >= 75:
            tdesc = "\u5f37\u3044\u56fd\u969b\u7684\u30e2\u30e1\u30f3\u30bf\u30e0\u3092\u6301\u3064\u975e\u5e38\u306b\u30db\u30c3\u30c8\u306a\u30c8\u30ec\u30f3\u30c9"
        elif t >= 60:
            tdesc = "\u4e16\u754c\u7684\u306b\u7259\u5c05\u529b\u3092\u5897\u3057\u3066\u3044\u308b\u6e29\u304b\u304f\u6210\u9577\u3059\u308b\u30c8\u30ec\u30f3\u30c9"
        elif t >= 40:
            tdesc = "\u30b0\u30ed\u30fc\u30d0\u30eb\u306b\u691c\u7d22\u95a2\u5fc3\u3092\u9ad8\u3081\u3066\u3044\u308b\u4e0a\u6607\u30c8\u30ec\u30f3\u30c9"
        else:
            tdesc = "\u30b0\u30ed\u30fc\u30d0\u30eb\u306a\u6ce8\u76ee\u3092\u96c6\u3081\u59cb\u3081\u3066\u3044\u308b\u65b0\u8208\u30c8\u30d4\u30c3\u30af"

        src = {
            "youtube": "YouTube\u30c8\u30ec\u30f3\u30c9",
            "apple_music": "Apple Music\u30c1\u30e3\u30fc\u30c8",
            "itunes_movies": "iTunes\u6620\u753b\u30c1\u30e3\u30fc\u30c8",
            "google": "Google\u691c\u7d22\u30c8\u30ec\u30f3\u30c9",
            "gdelt": "\u30b0\u30ed\u30fc\u30d0\u30eb\u30cb\u30e5\u30fc\u30b9 (GDELT)",
            "espn": "ESPN\u30b9\u30dd\u30fc\u30c4",
            "marketwatch": "MarketWatch\u30d5\u30a1\u30a4\u30ca\u30f3\u30b9",
        }.get(c.get("source") or "", "\u30b0\u30ed\u30fc\u30d0\u30eb\u30c8\u30ec\u30f3\u30c9\u30c8\u30e9\u30c3\u30ab\u30fc")

        cat = c["category"]
        kw = c["keyword_en"]
        if cat == "music":
            why = (
                f"\u97f3\u697d\u30c8\u30ec\u30f3\u30c9\u306f\u3001\u30a2\u30fc\u30c6\u30a3\u30b9\u30c8\u304c\u65b0\u30b3\u30f3\u30c6\u30f3\u30c4\u3092\u30ea\u30ea\u30fc\u30b9\u3057\u305f\u308a\u3001\u4e3b\u8981\u306a\u8cde\u3067\u8a8d\u3081\u3089\u308c\u305f\u308a\u3001\u30bd\u30fc\u30b7\u30e3\u30eb\u30d7\u30e9\u30c3\u30c8\u30d5\u30a9\u30fc\u30e0\u3067\u30d0\u30a4\u30e9\u30eb\u306b\u306a\u3063\u305f\u308a\u3059\u308b\u3068\u7206\u767a\u3057\u307e\u3059\u3002"
                f"**\"{kw}\"**\u306f\u307e\u3055\u306b\u305d\u308c\u3092\u9054\u6210\u3057\u3001\u30b9\u30c8\u30ea\u30fc\u30df\u30f3\u30b0\u30d7\u30e9\u30c3\u30c8\u30d5\u30a9\u30fc\u30e0\u306e\u52e2\u3044\u3068\u30d5\u30a1\u30f3\u4e3b\u5c0e\u306e\u30b7\u30a7\u30a2\u3092\u7d44\u307f\u5408\u308f\u305b\u3066\u3001\u56fd\u5883\u3092\u8d85\u3048\u305f\u81ea\u5df1\u5897\u5e45\u30b5\u30fc\u30b8\u3092\u751f\u307f\u51fa\u3057\u307e\u3057\u305f\u3002"
                f"1\u66f2\u304c\u540c\u6642\u306b\u30b0\u30ed\u30fc\u30d0\u30eb\u30c1\u30e3\u30fc\u30c8\u306e\u9802\u70b9\u306b\u9054\u3059\u308b\u3068\u304d\u3001\u305d\u308c\u306f\u6587\u5316\u7684\u5171\u9cf4\u3068\u30b3\u30cd\u30af\u30c6\u30c3\u30c9\u30c7\u30b8\u30bf\u30eb\u30aa\u30fc\u30c7\u30a3\u30a8\u30f3\u30b9\u306e\u529b\u306e\u4e21\u65b9\u3092\u793a\u3057\u307e\u3059\u3002"
                f"\u8907\u6570\u56fd\u306e\u691c\u7d22\u30d1\u30bf\u30fc\u30f3\u306f\u3001\u3053\u308c\u304c\u5358\u4e00\u5e02\u5834\u306b\u9650\u5b9a\u3055\u308c\u305f\u5730\u57df\u7684\u306a\u73fe\u8c61\u3067\u306f\u306a\u304f\u3001\u771f\u306e\u30b0\u30ed\u30fc\u30d0\u30eb\u97f3\u697d\u30e2\u30fc\u30e1\u30f3\u30c8\u3067\u3042\u308b\u3053\u3068\u3092\u78ba\u8a8d\u3057\u3066\u3044\u307e\u3059\u3002"
            )
        elif cat == "movies":
            why = (
                f"\u30a8\u30f3\u30bf\u30fc\u30c6\u30a4\u30f3\u30e1\u30f3\u30c8\u30c8\u30ec\u30f3\u30c9\u306f\u3001\u5927\u304d\u306a\u30c8\u30ec\u30fc\u30e9\u30fc\u516c\u958b\u3001\u6620\u753b\u306e\u5c4a\u51fa\u3001\u307e\u305f\u306f\u8cde\u306e\u30bb\u30ec\u30e2\u30cb\u30fc\u306e\u77ac\u9593\u306b\u30d4\u30fc\u30af\u306b\u9054\u3057\u307e\u3059\u3002"
                f"**\"{kw}\"**\u306f\u4eca\u65e5\u5168\u4e16\u754c\u306e\u89b3\u5ba2\u306e\u6ce8\u76ee\u3092\u96c6\u3081\u3001\u30b0\u30ed\u30fc\u30d0\u30eb\u6620\u753b\u696d\u754c\u304c\u8a00\u8a9e\u3084\u6587\u5316\u3092\u8d8a\u3048\u3066\u5982\u4f55\u306b\u89b3\u5ba2\u3092\u7d50\u3073\u3064\u3051\u308b\u304b\u3092\u793a\u3057\u3066\u3044\u307e\u3059\u3002"
                f"\u4f5c\u54c1\u304c\u6570\u5341\u304b\u56fd\u3067\u540c\u6642\u306b\u30c8\u30ec\u30f3\u30c9\u5165\u308a\u3059\u308b\u3068\u304d\u3001\u305d\u308c\u306f\u975e\u5e38\u306b\u671f\u5f85\u3055\u308c\u308b\u30ea\u30ea\u30fc\u30b9\u304b\u3001\u5730\u7406\u7684\u5883\u754c\u3092\u8d8a\u3048\u3066\u4e3b\u6d41\u306e\u30b0\u30ed\u30fc\u30d0\u30eb\u306a\u4f1a\u8a71\u306b\u5165\u3063\u305f\u30d0\u30a4\u30e9\u30eb\u30de\u30fc\u30b1\u30c6\u30a3\u30f3\u30b0\u306e\u77ac\u9593\u3092\u793a\u3057\u3066\u3044\u307e\u3059\u3002"
            )
        elif cat == "tech":
            why = (
                f"\u6280\u8853\u30c8\u30d4\u30c3\u30af\u306f\u3001\u6280\u8853\u754c\u3067\u91cd\u8981\u306a\u88fd\u54c1\u767a\u8868\u3001\u5927\u304d\u306a\u767a\u8868\u3001\u307e\u305f\u306f\u8ad6\u4e89\u304c\u8d77\u304d\u308b\u3068\u30c8\u30ec\u30f3\u30c9\u5165\u308a\u3057\u307e\u3059\u3002"
                f"**\"{kw}\"**\u306f\u4eca\u65e5\u30b0\u30ed\u30fc\u30d0\u30eb\u306a\u6ce8\u76ee\u3092\u96c6\u3081\u3001\u5927\u898f\u6a21\u306a\u88fd\u54c1\u767a\u8868\u3001\u696d\u754c\u306e\u52d5\u5411\u3001\u307e\u305f\u306f\u5143\u306e\u30aa\u30fc\u30c7\u30a3\u30a8\u30f3\u30b9\u3092\u306f\u308b\u304b\u306b\u8d85\u3048\u3066\u5e83\u304c\u3063\u305f\u30d0\u30a4\u30e9\u30eb\u306a\u6280\u8853\u306e\u8a71\u984c\u3092\u793a\u3057\u3066\u3044\u307e\u3059\u3002"
                f"\u8907\u6570\u56fd\u306e\u691c\u7d22\u30d1\u30bf\u30fc\u30f3\u306f\u3001\u7570\u306a\u308b\u5e02\u5834\u3068\u30e6\u30fc\u30b6\u30fc\u30b3\u30df\u30e5\u30cb\u30c6\u30a3\u3067\u540c\u6642\u306b\u5171\u9cf4\u3059\u308b\u30b0\u30ed\u30fc\u30d0\u30eb\u306b\u95a2\u9023\u3059\u308b\u6280\u8853\u30a4\u30d9\u30f3\u30c8\u3092\u793a\u3057\u3066\u3044\u307e\u3059\u3002"
            )
        elif cat == "sports":
            why = (
                f"\u30b9\u30dd\u30fc\u30c4\u30c8\u30ec\u30f3\u30c9\u306f\u3001\u5927\u304d\u306a\u8a66\u5408\u7d50\u679c\u3001\u30c8\u30fc\u30ca\u30e1\u30f3\u30c8\u306e\u30de\u30a4\u30eb\u30b9\u30c8\u30fc\u30f3\u3001\u307e\u305f\u306f\u9ad8\u30d7\u30ed\u30d5\u30a1\u30a4\u30eb\u306a\u30a2\u30b9\u30ea\u30fc\u30c8\u306b\u95a2\u3059\u308b\u30d6\u30ec\u30fc\u30ad\u30f3\u30b0\u30cb\u30e5\u30fc\u30b9\u306e\u5468\u308a\u3067\u6fc0\u5897\u3057\u307e\u3059\u3002"
                f"**\"{kw}\"**\u5468\u8fba\u306e\u30b0\u30ed\u30fc\u30d0\u30eb\u691c\u7d22\u6d3b\u52d5\u306f\u3001\u56fd\u969b\u5e02\u5834\u3067\u5171\u9cf4\u3059\u308b\u91cd\u8981\u306a\u30b9\u30dd\u30fc\u30c4\u30a4\u30d9\u30f3\u30c8\u307e\u305f\u306f\u767a\u8868\u3092\u793a\u3057\u3066\u3044\u307e\u3059\u3002"
                f"\u30b9\u30dd\u30fc\u30c4\u306f\u8a00\u8a9e\u306e\u58c1\u3092\u8d8a\u3048\u3001\u4e16\u754c\u4e2d\u3067\u540c\u6642\u306b\u53c2\u52a0\u3092\u751f\u307f\u51fa\u3059\u72ec\u7279\u306e\u80fd\u529b\u3092\u6301\u3063\u3066\u304a\u308a\u3001\u8907\u6570\u56fd\u306e\u30c8\u30ec\u30f3\u30c9\u3092\u30b0\u30ed\u30fc\u30d0\u30eb\u30b9\u30dd\u30fc\u30c4\u306b\u304a\u3051\u308b\u771f\u306b\u91cd\u8981\u306a\u77ac\u9593\u306e\u5f37\u529b\u306a\u30b7\u30b0\u30ca\u30eb\u306b\u3057\u307e\u3059\u3002"
            )
        elif cat == "finance":
            why = (
                f"\u91d1\u878d\u30c8\u30d4\u30c3\u30af\u306f\u3001\u5e02\u5834\u306e\u30dc\u30e9\u30c6\u30a3\u30ea\u30c6\u30a3\u3001\u5927\u304d\u306a\u7d4c\u6e08\u767a\u8868\u3001\u307e\u305f\u306f\u30d0\u30a4\u30e9\u30eb\u306a\u6295\u8cc4\u30b9\u30c8\u30fc\u30ea\u30fc\u306e\u969b\u306b\u30c8\u30ec\u30f3\u30c9\u5165\u308a\u3057\u307e\u3059\u3002"
                f"**\"{kw}\"**\u306b\u5bfe\u3059\u308b\u4eca\u65e5\u306e\u30b0\u30ed\u30fc\u30d0\u30eb\u306a\u95a2\u5fc3\u306f\u3001\u7d4c\u6e08\u7684\u4e0d\u78ba\u5b9f\u6027\u3001\u5e02\u5834\u3092\u52d5\u304b\u3059\u30a4\u30d9\u30f3\u30c8\u3001\u307e\u305f\u306f\u30cb\u30c3\u30c1\u306a\u6295\u8cc4\u5bb6\u30b5\u30fc\u30af\u30eb\u304b\u3089\u4e00\u822c\u516c\u8846\u306e\u610f\u8b58\u306b\u5165\u308a\u8fbc\u3093\u3060\u91d1\u878d\u30b9\u30c8\u30fc\u30ea\u30fc\u3092\u53cd\u6620\u3057\u3066\u3044\u308b\u53ef\u80fd\u6027\u304c\u3042\u308a\u307e\u3059\u3002"
                f"\u91d1\u878d\u30c8\u30d4\u30c3\u30af\u306e\u8907\u6570\u56fd\u30c8\u30ec\u30f3\u30c9\u306f\u3001\u6295\u8cc4\u5bb6\u3084\u30c8\u30ec\u30fc\u30c0\u30fc\u3092\u8d85\u3048\u3066\u4eba\u3005\u306b\u5f71\u97ff\u3092\u4e0e\u3048\u308b\u3088\u308a\u5e83\u3044\u30de\u30af\u30ed\u7d4c\u6e08\u7684\u91cd\u8981\u6027\u3092\u793a\u3057\u3066\u3044\u307e\u3059\u3002"
            )
        else:
            why = (
                f"\u30cb\u30e5\u30fc\u30b9\u3068\u60c5\u5831\u306e\u30c8\u30ec\u30f3\u30c9\u306f\u3001\u4e16\u754c\u4e2d\u3067\u540c\u6642\u306b\u691c\u7d22\u3059\u308b\u4f55\u767e\u4e07\u4eba\u3082\u306e\u96c6\u5408\u7684\u306a\u597d\u5947\u5fc3\u3092\u53cd\u6620\u3057\u3066\u3044\u307e\u3059\u3002"
                f"**\"{kw}\"**\u306f\u4eca\u65e5\u56fd\u969b\u7684\u306a\u6ce8\u76ee\u3092\u96c6\u3081\u3001\u6587\u5316\u3084\u56fd\u5883\u3092\u8d8a\u3048\u3066\u5171\u9cf4\u3059\u308b\u91cd\u8981\u306a\u5c55\u958b\u3001\u7b2c\u4e00\u5831\u3001\u307e\u305f\u306f\u30d0\u30a4\u30e9\u30eb\u306a\u77ac\u9593\u3092\u793a\u3057\u3066\u3044\u307e\u3059\u3002"
                f"\u4e00\u3064\u306e\u30c8\u30d4\u30c3\u30af\u304c\u540c\u6642\u306b\u6570\u5341\u304b\u56fd\u3067\u30c8\u30ec\u30f3\u30c9\u5165\u308a\u3059\u308b\u3068\u304d\u3001\u305d\u308c\u306f\u901a\u5e38\u3001\u5730\u7406\u7684\u5883\u754c\u3092\u8d85\u3048\u308b\u666e\u9061\u7684\u306a\u95a2\u9023\u6027\u307e\u305f\u306f\u6df1\u3044\u6587\u5316\u7684\u5f71\u97ff\u3092\u6301\u3064\u4f55\u304b\u3092\u8868\u3057\u3066\u3044\u307e\u3059\u3002"
            )

        return textwrap.dedent(f"""\
**\u300c{c['keyword_en']}\u300d**\u306f{c['date_str']}\u73fe\u5728\u3001\u4e16\u754c\u4e2d\u3067\u6700\u3082\u691c\u7d22\u3055\u308c\u3066\u3044\u308b\u30c8\u30d4\u30c3\u30af\u3067\u3001\
{len(c['countries_list'])}\u304b\u56fd\u3067\u540c\u6642\u306b\u5f37\u70c8\u306a\u30a2\u30af\u30c6\u30a3\u30d3\u30c6\u30a3\u3092\u751f\u307f\u51fa\u3057\u3066\u3044\u307e\u3059\u3002\
\u4e3b\u5c0e\u3059\u308b\u306e\u306f **{c['top_country_name']}** {top_flag}\u3067\u3001{c['volume']}\u4ef6\u306e\u691c\u7d22\u304c\u8a18\u9332\u3055\u308c\u3001\
\u4eca\u65e5\u306e\u30b0\u30ed\u30fc\u30d0\u30eb\u30c7\u30b8\u30bf\u30eb\u95a2\u5fc3\u306e\u7d2b\u308c\u306a\u304d\u9707\u6e90\u5730\u3068\u306a\u3063\u3066\u3044\u307e\u3059\u3002

\u30bd\u30fc\u30b7\u30e3\u30eb\u30e1\u30c7\u30a3\u30a2\u3001\u30cb\u30e5\u30fc\u30b9\u306e\u898b\u51fa\u3057\u3001\u307e\u305f\u306f\u53cb\u4eba\u306e\u30e1\u30c3\u30bb\u30fc\u30b8\u3092\u901a\u3058\u3066\u3053\u306e\u30c8\u30d4\u30c3\u30af\u3092\u898b\u3064\u3051\u305f\u3068\u3057\u3066\u3082\u3001\
\u3042\u306a\u305f\u306f\u4eca\u308f\u307e\u3057\u304f\u4e16\u754c\u7684\u306a\u77ac\u9593\u306e\u4e00\u90e8\u3067\u3059\u3002\
\u4ee5\u4e0b\u3067\u306f\u3001{c['total_countries']}\u304b\u56fd\u306e\u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u30c7\u30fc\u30bf\u3092\u5143\u306b\u3001**\u300c{c['keyword_en']}\u300d**\u304c\u4eca\u307e\u3055\u306b\u4e16\u754c\u306e\u6ce8\u76ee\u3092\u96c6\u3081\u3066\u3044\u308b\u7406\u7531\u3092\u8a73\u3057\u304f\u5206\u6790\u3057\u307e\u3059\u3002

---

## \u300c{c['keyword_en']}\u300d\u3068\u306f\u4f55\u304b\uff1f

**\u300c{c['keyword_en']}\u300d**\u306f\u3001\u4eca\u65e5\u30b0\u30ed\u30fc\u30d0\u30eb\u691c\u7d22\u30e9\u30f3\u30ad\u30f3\u30b0\u306e\u30c8\u30c3\u30d7\u306b\u7acb\u3063\u305f{c['category_label'].lower()}\u30c8\u30d4\u30c3\u30af\u3067\u3059\u3002\
**{c['category_label']}**\u30ab\u30c6\u30b4\u30ea\u306b\u5c5e\u3057\u3001TrendPulse\u306e0\u20131\u0030\u0030\u30b9\u30b1\u30fc\u30eb\u3067\u30c8\u30ec\u30f3\u30c9\u6e29\u5ea6 **{c['top_temperature']}\u00b0T**\u3092\u8a18\u9332\u3057\u3066\u3044\u307e\u3059 \
\u2014 {tdesc}\u3092\u793a\u3057\u3066\u3044\u307e\u3059\u3002

\u3053\u306e\u30c8\u30d4\u30c3\u30af\u306f\u4e3b\u306b **{c['top_country_name']}**\u767a\u3067\u3059\u304c\u3001\u8fc5\u901f\u306b\u56fd\u5883\u3092\u8d8a\u3048\u3066\u5e83\u304c\u308a\u3001\
{other_countries}\u306a\u3069\u3067\u6e2c\u5b9a\u53ef\u80fd\u306a\u7af6\u4e89\u529b\u3092\u5f97\u3066\u3044\u307e\u3059\u3002\
\u3053\u306e\u56fd\u5883\u3092\u8d8a\u3048\u305f\u52d5\u8133\u304c\u3001\u771f\u306e\u30b0\u30ed\u30fc\u30d0\u30eb\u30c8\u30ec\u30f3\u30c9\u3068\u30ed\u30fc\u30ab\u30eb\u30cb\u30e5\u30fc\u30b9\u3092\u533a\u5225\u3059\u308b\u9375\u3068\u306a\u308a\u307e\u3059\u3002

### 主要統計

| \u6307\u6a19 | \u5024 |
|---|---|
| \u691c\u7d22\u30dc\u30ea\u30e5\u30fc\u30e0 | {c['volume']} |
| \u30c8\u30ec\u30f3\u30c9\u6e29\u5ea6 | {c['top_temperature']}\u00b0T / 100 |
| \u30ab\u30c6\u30b4\u30ea | {c['category_label']} |
| \u30ea\u30fc\u30c9\u56fd | {top_flag} {c['top_country_name']} |
| \u8ffd\u8de1\u56fd\u6570 | {len(c['countries_list'])} / {c['total_countries']} |
| \u30c7\u30fc\u30bf\u30bd\u30fc\u30b9 | {src} |
| \u6700\u7d42\u66f4\u65b0 | {c['date_str']} |{yt_line}
---

## \u300c{c['keyword_en']}\u300d\u306f\u306a\u305c\u4eca\u65e5\u30c8\u30ec\u30f3\u30c9\u5165\u308a\u3057\u3066\u3044\u308b\u306e\u304b\uff1f

{why}

\u30ab\u30c6\u30b4\u30ea\u56fa\u6709\u306e\u8981\u56e0\u3092\u8d85\u3048\u3066\u3001\u4eca\u65e5\u306e**\u300c{c['keyword_en']}\u300d**\u306e\u898f\u6a21\u306f\u6ce8\u76ee\u306b\u5024\u3057\u307e\u3059\u3002\
{len(c['countries_list'])}\u304b\u56fd\u3067\u540c\u6642\u306b\u30c8\u30ec\u30f3\u30c9\u5165\u308a\u3059\u308b\u3068\u3044\u3046\u3053\u3068\u306f\u3001\u3053\u306e\u30c8\u30d4\u30c3\u30af\u304c\u30a2\u30ca\u30ea\u30b9\u30c8\u304c\u300c\u8131\u51fa\u901f\u5ea6\u300d\u3068\u547c\u3076\u3082\u306e\u3092\u9054\u6210\u3057\u305f\u3053\u3068\u3092\u610f\u5473\u3057\u307e\u3059 \u2014 \
\u6709\u6a5f\u7684\u306a\u30b7\u30a7\u30a2\u3068\u30e1\u30c7\u30a3\u30a2\u5831\u9053\u304c\u4e92\u3044\u3092\u5f37\u5316\u3057\u5408\u3044\u3001\u81ea\u5df1\u5897\u5e45\u30eb\u30fc\u30d7\u3092\u5f62\u6210\u3059\u308b\u30dd\u30a4\u30f3\u30c8\u3002\
{c['top_temperature']}\u00b0T\u3067\u306f\u3001\u3053\u308c\u306f\u4eca\u65e5\u306e\u30cd\u30c3\u30c8\u30ef\u30fc\u30af\u3067\u8ffd\u8de1\u3055\u308c\u308b\u6700\u3082\u6fc0\u3057\u3044\u30c8\u30ec\u30f3\u30c9\u306e\u4e00\u3064\u3067\u3059\u3002

\U0001f50d **\u81ea\u5206\u3067\u78ba\u8a8d\uff1a** \
[Google\u30c8\u30ec\u30f3\u30c9\u3067\u300c{c['keyword_en']}\u300d\u3092\u63a2\u7d22]({c['google_trends_url']})

---

## \u300c{c['keyword_en']}\u300d\u306f\u3069\u306e\u56fd\u3067\u691c\u7d22\u3055\u308c\u3066\u3044\u308b\u304b\uff1f

TrendPulse\u306f**{c['total_countries']}\u304b\u56fd**\u306e\u691c\u7d22\u30a2\u30af\u30c6\u30a3\u30d3\u30c6\u30a3\u3092\u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u3067\u30e2\u30cb\u30bf\u30ea\u30f3\u30b0\u3057\u3066\u3044\u307e\u3059\u3002\
\u4ee5\u4e0b\u306f\u4eca\u65e5**\u300c{c['keyword_en']}\u300d**\u304c\u6d3b\u767a\u306a\u691c\u7d22\u95a2\u5fc3\u3092\u751f\u307f\u51fa\u3057\u3066\u3044\u308b\u56fd\u3005\u3067\u3059\uff1a

{countries_md}

### シグナルが最も強い場所

\u652f\u914d\u7684\u306a\u691c\u7d22\u30b7\u30b0\u30ca\u30eb\u306f **{c['top_country_name']}**\u304b\u3089\u767a\u4fe1\u3055\u308c\u3066\u304a\u308a\u3001\
**\u300c{c['keyword_en']}\u300d**\u3092\u3081\u3050\u308b\u30b0\u30ed\u30fc\u30d0\u30eb\u306a\u4f1a\u8a71\u3092\u30ea\u30fc\u30c9\u3057\u3066\u3044\u307e\u3059\u3002\
{len(c['countries_list'])}\u304b\u56fd\u306b\u307e\u305f\u304c\u308b\u5e83\u304c\u308a\u306f\u3001\u3053\u306e\u30c8\u30d4\u30c3\u30af\u304c\u30ed\u30fc\u30ab\u30eb\u306a\u95a2\u5fc3\u3092\u8d85\u3048\u3001\u771f\u306e\u30b0\u30ed\u30fc\u30d0\u30eb\u6587\u5316\u306e\u9818\u57df\u306b\u5165\u3063\u305f\u3053\u3068\u3092\u793a\u3057\u3066\u3044\u307e\u3059\u3002

\u30c8\u30ec\u30f3\u30c9\u304c\u3053\u306e\u30ec\u30d9\u30eb\u306e\u5730\u7406\u7684\u62e1\u6563\u306b\u9054\u3059\u308b\u3068\u304d\u3001\u305d\u308c\u306f\u5f37\u529b\u306a\u30e1\u30c7\u30a3\u30a2\u5831\u9053\u3001\u30d0\u30a4\u30e9\u30eb\u306a\u30bd\u30fc\u30b7\u30e3\u30eb\u30e1\u30c7\u30a3\u30a2\u5171\u6709\u3001\u307e\u305f\u306f\u8a00\u8a9e\u3084\u5834\u6240\u306b\u95a2\u4fc2\u306a\u304f\u4e16\u754c\u4e2d\u306e\u89b3\u5ba2\u306b\u97ff\u304f\u6587\u5316\u7684\u306b\u91cd\u8981\u306a\u30a4\u30d9\u30f3\u30c8\u3092\u793a\u3057\u3066\u3044\u307e\u3059\u3002

\U0001f5fa\ufe0f **\u5730\u56f3\u3067\u78ba\u8a8d\uff1a** \
[\u30a4\u30f3\u30bf\u30e9\u30af\u30c6\u30a3\u30d6\u30b0\u30ed\u30fc\u30d0\u30eb\u30c8\u30ec\u30f3\u30c9\u30de\u30c3\u30d7\u3092\u898b\u308b]({c['site_url']})

---

## トレンドデータ＆詳細統計

{c['date_str']}\u6642\u70b9\u306e**\u300c{c['keyword_en']}\u300d**\u30c8\u30ec\u30f3\u30c9\u306e\u5b8c\u5168\u306a\u7d71\u8a08\u5206\u6790\uff1a

| \u6307\u6a19 | \u5024 |
|---|---|
| \u30d4\u30fc\u30af\u691c\u7d22\u30dc\u30ea\u30e5\u30fc\u30e0 | {c['volume']} |
| \u30c8\u30ec\u30f3\u30c9\u6e29\u5ea6 | {c['top_temperature']}\u00b0T |
| \u6e29\u5ea6\u306e\u610f\u5473 | {tdesc} |
| \u4e3b\u8981\u30ab\u30c6\u30b4\u30ea | {c['category_label']} |
| \u30b0\u30ed\u30fc\u30d0\u30eb\u30ea\u30fc\u30c1 | {len(c['countries_list'])}\u304b\u56fd |
| \u76e3\u8996\u5bfe\u8c61\u56fd\u6570 | {c['total_countries']} |

**\u30c8\u30ec\u30f3\u30c9\u6e29\u5ea6\u306b\u3064\u3044\u3066\uff1a** TrendPulse\u306e\u72ec\u81ea\u30b9\u30b3\u30a2\uff080\u20131\u0030\u0030\uff09\u306f\u3001\u691c\u7d22\u30dc\u30ea\u30e5\u30fc\u30e0\u3001\u5730\u7406\u7684\u7bc4\u56f2\u3001\u901f\u5ea6\u3092\u5358\u4e00\u306e\u5f37\u5ea6\u6307\u6a19\u306b\u7d44\u307f\u5408\u308f\u305b\u307e\u3059\u3002{c['top_temperature']}\u00b0T\u306e\u30b9\u30b3\u30a2\u306f{tdesc}\u3092\u610f\u5473\u3057\u307e\u3059\u3002

---

## 今まさに急上昇中の他のトレンド

**\u300c{c['keyword_en']}\u300d**\u304c\u30b0\u30ed\u30fc\u30d0\u30eb\u30b9\u30c6\u30fc\u30b8\u3092\u652f\u914d\u3059\u308b\u4e2d\u3001\u3053\u308c\u3089\u306e\u30c8\u30d4\u30c3\u30af\u3082\u79c1\u305f\u3061\u306e{c['total_countries']}\u304b\u56fd\u30cd\u30c3\u30c8\u30ef\u30fc\u30af\u3067\u6025\u4e0a\u6607\u3057\u3066\u3044\u307e\u3059\uff1a

{rising_md}

\u3053\u308c\u3089\u306f\u305d\u308c\u305e\u308c\u3001\u4f55\u767e\u4e07\u4eba\u3082\u306e\u4eba\u3005\u304c\u540c\u6642\u306b\u691c\u7d22\u3057\u3066\u3044\u308b\u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u30b7\u30b0\u30ca\u30eb\u3092\u8868\u3057\u3066\u3044\u307e\u3059\u3002\u30c8\u30d4\u30c3\u30af\u306e\u591a\u69d8\u6027\u306f\u3001\u4eca\u307e\u3055\u306b\u8d77\u304d\u3066\u3044\u308b\u30b0\u30ed\u30fc\u30d0\u30eb\u306a\u30c7\u30b8\u30bf\u30eb\u4f1a\u8a71\u306e\u5e45\u5e83\u3055\u3092\u53cd\u6620\u3057\u3066\u3044\u307e\u3059\u3002

\U0001f4ca **\u3059\u3079\u3066\u306e\u30e9\u30a4\u30d6\u30c8\u30ec\u30f3\u30c9\u3092\u63a2\u7d22\uff1a** [\u5b8c\u5168\u306a\u30b0\u30ed\u30fc\u30d0\u30eb\u30c8\u30ec\u30f3\u30c9\u30de\u30c3\u30d7\u3092\u958b\u304f]({c['site_url']})

---

## 今日のカテゴリ別グローバル検索状況

\u4eca\u65e5\u306e\u30c8\u30ec\u30f3\u30c9\u30c8\u30d4\u30c3\u30af\u304c\u4e3b\u8981\u30b3\u30f3\u30c6\u30f3\u30c4\u30ab\u30c6\u30b4\u30ea\u3054\u3068\u306b\u3069\u306e\u3088\u3046\u306b\u5206\u5e03\u3057\u3066\u3044\u308b\u304b\uff1a

{cat_md}

\u3053\u306e\u30b9\u30ca\u30c3\u30d7\u30b7\u30e7\u30c3\u30c8\u306f\u3001{c['total_countries']}\u304b\u56fd\u306e\u4f55\u767e\u4e07\u4eba\u3082\u306e\u4eba\u3005\u304c\u4eca\u307e\u3055\u306b\u7a4d\u6975\u7684\u306b\u691c\u7d22\u3057\u3066\u3044\u308b\u3053\u3068\u3092\u6355\u3048\u3066\u3044\u307e\u3059\u3002**{c['category_label']}**\u30ab\u30c6\u30b4\u30ea\u306f\u4eca\u65e5\u7279\u306b\u6d3b\u767a\u3067\u3001**\u300c{c['keyword_en']}\u300d**\u304a\u3088\u3073\u5bc6\u63a5\u306b\u95a2\u9023\u3059\u308b\u691c\u7d22\u304c\u5927\u304d\u304f\u724c\u5f15\u3057\u3066\u3044\u307e\u3059\u3002

---

## よくある質問（FAQ）

### 「{c['keyword_en']}」とは何ですか？

**\u300c{c['keyword_en']}\u300d**\u306f\u73fe\u5728\u4e16\u754c\u691c\u7d22\u30e9\u30f3\u30ad\u30f31\u4f4d\u3067\u3001\
{c['date_str']}\u6642\u70b9\u3067{len(c['countries_list'])}\u304b\u56fd\u3067\u8ffd\u8de1\u3055\u308c\u3066\u3044\u307e\u3059\u3002\
{c['category_label']}\u30ab\u30c6\u30b4\u30ea\u306b\u5c5e\u3057\u3001\u30ea\u30fc\u30c9\u56fd\u3060\u3051\u3067{c['volume']}\u4ef6\u306e\u691c\u7d22\u304c\u767a\u751f\u3057\u3066\u3044\u307e\u3059\u3002\
[\u30e9\u30a4\u30d6\u30c8\u30ec\u30f3\u30c9\u30de\u30c3\u30d7]({c['site_url']})\u3067\u5730\u7406\u30c7\u30fc\u30bf\u3092\u78ba\u8a8d\u3067\u304d\u307e\u3059\u3002

### なぜ今「{c['keyword_en']}」がトレンドになっているのですか？

**\u300c{c['keyword_en']}\u300d**\u306f\u3001{len(c['countries_list'])}\u304b\u56fd\u3067\u306e\u8fc5\u901f\u306a\u62e1\u6563\u306b\u3088\u308a\u30b0\u30ed\u30fc\u30d0\u30eb\u691c\u7d22\u306e\u30c8\u30c3\u30d7\u306b\u9054\u3057\u307e\u3057\u305f\u3002\
\u30c8\u30ec\u30f3\u30c9\u6e29\u5ea6{c['top_temperature']}\u00b0T \u2014 {tdesc}\u3092\u793a\u3057\u3066\u3044\u307e\u3059\u3002\
\u3053\u306e\u3088\u3046\u306a\u591a\u56fd\u540c\u6642\u30b5\u30fc\u30b8\u306f\u901a\u5e38\u3001\u30d0\u30a4\u30e9\u30eb\u30a4\u30d9\u30f3\u30c8\u3001\u7b2c\u4e00\u5831\u3001\u307e\u305f\u306f\u91cd\u8981\u306a\u6587\u5316\u7684\u77ac\u9593\u3092\u793a\u3057\u307e\u3059\u3002\
[Google\u30c8\u30ec\u30f3\u30c9]({c['google_trends_url']})\u3067\u904e\u53bb\u306e\u30c7\u30fc\u30bf\u3092\u78ba\u8a8d\u3067\u304d\u307e\u3059\u3002

### どの国が最も「{c['keyword_en']}」を検索していますか？

TrendPulse\u306e\u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u30c7\u30fc\u30bf\u306b\u3088\u308b\u3068\u3001**{c['top_country_name']}** {top_flag}\u304c\u4eca\u65e5\u306e**\u300c{c['keyword_en']}\u300d**\u691c\u7d22\u306e\u30ea\u30fc\u30c9\u56fd\u3067\u3001{c['volume']}\u4ef6\u306e\u30af\u30a8\u30ea\u304c\u8a18\u9332\u3055\u308c\u3066\u3044\u307e\u3059\u3002\u3053\u306e\u30c8\u30ec\u30f3\u30c9\u306f\u305d\u306e\u5f8c{max(0, len(c['countries_list']) - 1)}\u304b\u56fd\u306b\u5e83\u304c\u3063\u3066\u3044\u307e\u3059\u3002\u5b8c\u5168\u306a\u5730\u7406\u7684\u5185\u8a33\u306f[\u30a4\u30f3\u30bf\u30e9\u30af\u30c6\u30a3\u30d6\u30de\u30c3\u30d7]({c['site_url']})\u3092\u3054\u89a7\u304f\u3060\u3055\u3044\u3002

### TrendPulseはどうやってグローバルトレンド強度を測定しますか？

TrendPulse\u306f**{c['total_countries']}\u304b\u56fd**\u306e\u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u30c7\u30fc\u30bf\u3092\u6bce\u6642\u53ce\u96c6\u3057\u3001\
Google\u691c\u7d22\u30c8\u30ec\u30f3\u30c9\u3001YouTube\u3001Apple Music\u30c1\u30e3\u30fc\u30c8\u3001\u30b0\u30ed\u30fc\u30d0\u30eb\u30cb\u30e5\u30fc\u30b9\u30d5\u30a3\u30fc\u30c9\u304b\u3089\u306e\u30b7\u30b0\u30ca\u30eb\u3092\u96c6\u7d04\u3057\u307e\u3059\u3002\
\u79c1\u305f\u3061\u306e**\u30c8\u30ec\u30f3\u30c9\u6e29\u5ea6**\u30b9\u30b3\u30a2\uff080\u20131\u0030\u0030\uff09\u306f\u3001\u691c\u7d22\u30dc\u30ea\u30e5\u30fc\u30e0\u3001\u5730\u7406\u7684\u7bc4\u56f2\u3001\u901f\u5ea6\u3092\u7d44\u307f\u5408\u308f\u305b\u3066\u3001\
\u4e16\u754c\u306e\u5404\u30c8\u30ec\u30f3\u30c9\u30c8\u30d4\u30c3\u30af\u306e\u5358\u4e00\u306e\u5f37\u5ea6\u6307\u6a19\u3092\u751f\u6210\u3057\u307e\u3059\u3002

### もっとグローバルトレンドデータを探索するにはどこへ？

[\u30b0\u30ed\u30fc\u30d0\u30eb\u30c8\u30ec\u30f3\u30c9\u30de\u30c3\u30d7]({c['site_url']})\u3067\u3001\u56fd\u5225\u306e\u5185\u8a33\u3001\u30ab\u30c6\u30b4\u30ea\u30d5\u30a3\u30eb\u30bf\u30fc\u3001\u6bce\u6642\u66f4\u65b0\u3092\u542b\u3080\u30e9\u30a4\u30d6\u30b0\u30ed\u30fc\u30d0\u30eb\u30c8\u30ec\u30f3\u30c9\u3092\u63a2\u7d22\u3067\u304d\u307e\u3059\u3002{c['total_countries']}\u304b\u56fd\u306e\u30c8\u30ec\u30f3\u30c9\u3092\u8ffd\u8de1\u3057\u3001\u6bce\u6642\u66f4\u65b0\u3055\u308c\u307e\u3059\u3002\u8a73\u7d30\u306a\u5206\u6790\u306f[\u30c7\u30a4\u30ea\u30fc\u30c8\u30ec\u30f3\u30c9\u30d6\u30ed\u30b0]({c['site_url']}/blog)\u3092\u3054\u89a7\u304f\u3060\u3055\u3044\u3002

---

## すべてのグローバルトレンドを先取りする

**\u300c{c['keyword_en']}\u300d**\u306f\u3001\u4eca\u307e\u3055\u306b{c['total_countries']}\u304b\u56fd\u3067\u30e2\u30cb\u30bf\u30ea\u30f3\u30b0\u3055\u308c\u3066\u3044\u308b\u6570\u767e\u306e\u30c8\u30ec\u30f3\u30c9\u306e\u4e00\u3064\u3067\u3059\u3002\
\u7814\u7a76\u8005\u3001\u30b8\u30e3\u30fc\u30ca\u30ea\u30b9\u30c8\u3001\u30b3\u30f3\u30c6\u30f3\u30c4\u30af\u30ea\u30a8\u30a4\u30bf\u30fc\u3001\u30de\u30fc\u30b1\u30bf\u30fc\u3001\u307e\u305f\u306f\u4e16\u754c\u304c\u4f55\u3092\u8003\u3048\u3066\u3044\u308b\u306e\u304b\u306b\u5174\u5473\u306e\u3042\u308b\u65b9\u306a\u3069 \u2014 \
TrendPulse\u306f\u30b0\u30ed\u30fc\u30d0\u30eb\u306a\u30d1\u30eb\u30b9\u3078\u306e\u5373\u5ea7\u30a2\u30af\u30bb\u30b9\u3092\u63d0\u4f9b\u3057\u307e\u3059\u3002

\U0001f449 **[\u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u30b0\u30ed\u30fc\u30d0\u30eb\u30c8\u30ec\u30f3\u30c9\u30de\u30c3\u30d7\u3092\u898b\u308b]({c['site_url']})** \u2014 \u6bce\u6642\u66f4\u65b0

\U0001f4f0 **[\u30c8\u30ec\u30f3\u30c9\u5206\u6790\u3092\u3082\u3063\u3068\u8aad\u3080]({c['site_url']}/blog)** \u2014 \u6bce\u65e5\u4e16\u754c\u306e\u30c8\u30c3\u30d7\u30c8\u30ec\u30f3\u30c9\u3092\u6df1\u5c64\u5206\u6790

*\u30c7\u30fc\u30bf\u53ce\u96c6\u65e5\uff1a{c['date_str']}\u3002\u30c8\u30ec\u30f3\u30c9\u306f\u6bce\u6642\u66f4\u65b0\u3055\u308c\u307e\u3059\u3002\u30c8\u30ec\u30f3\u30c9\u6e29\u5ea6\u30b9\u30b3\u30a2\u306f\u30c7\u30fc\u30bf\u53ce\u96c6\u6642\u306e\u30c7\u30fc\u30bf\u3092\u53cd\u6620\u3057\u3066\u3044\u307e\u3059\u3002*
""")

    return {
        "en": {"title": en_title, "excerpt": en_excerpt, "body": en_body},
        "zh": {"title": zh_title, "excerpt": zh_excerpt, "body": zh_body},
        "es": {"title": es_title, "excerpt": es_excerpt, "body": es_body},
        "pt": {"title": pt_title, "excerpt": pt_excerpt, "body": pt_body},
        "fr": {"title": fr_title, "excerpt": fr_excerpt, "body": fr_body},
        "de": {"title": de_title, "excerpt": de_excerpt, "body": de_body},
        "kr": {"title": kr_title, "excerpt": kr_excerpt, "body": kr_body},
        "jp": {"title": jp_title, "excerpt": jp_excerpt, "body": jp_body},
    }


TEMPLATES = _mk_templates()


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

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
            return {"posts": data, "lastUpdated": now_iso(), "recentSpotlights": []}
        if "lastSpotlight" in data and "recentSpotlights" not in data:
            legacy = data.pop("lastSpotlight")
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            data["recentSpotlights"] = [{"keyword": legacy, "date": today}] if legacy else []
        data.setdefault("recentSpotlights", [])
        return data
    return {"posts": [], "lastUpdated": now_iso(), "recentSpotlights": []}


def save_index(index: dict):
    index["lastUpdated"] = now_iso()
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60].strip("-")


def reading_time(body: str) -> int:
    # CJK languages (Chinese, Japanese, Korean) don't use spaces between words
    cjk_chars = sum(1 for ch in body if '\u4e00' <= ch <= '\u9fff'
                    or '\uac00' <= ch <= '\ud7a3'
                    or '\u3040' <= ch <= '\u30ff'
                    or '\u3400' <= ch <= '\u4dbf')
    if cjk_chars > len(body) * 0.15:
        return max(1, round(cjk_chars / 500))
    return max(1, round(len(body.split()) / 200))


def format_date_str(dt: datetime) -> str:
    return dt.strftime("%B %d, %Y")


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------

def build_context(trends_data: dict, lang: str) -> dict:
    g = trends_data["global"]
    countries_data = trends_data["countries"]
    top = g["topTrend"]
    keyword_en = top.get("keywordEn") or top["keyword"]
    category = top.get("category", "")
    category_label = CATEGORY_LABELS.get(lang, CATEGORY_LABELS["en"]).get(category, category or "Trending")

    kw_lower = keyword_en.lower()

    # Find countries + extract top_temperature, youtube_id from actual trend item
    countries_with_trend = []
    top_temperature = g.get("temperature", 0)
    youtube_id = None
    source = top.get("source", "google")

    for code, cdata in countries_data.items():
        for t in cdata["trends"]:
            t_kw = (t.get("keywordEn") or t["keyword"]).lower()
            if t_kw == kw_lower:
                if not countries_with_trend:
                    top_temperature = t.get("temperature", top_temperature)
                    youtube_id = t.get("youtubeId")
                countries_with_trend.append((cdata.get("flag", "\U0001f310"), cdata["name"]))
                break

    # Also check categoryCharts (topTrend may come from there)
    if not youtube_id:
        for _cat, items in (trends_data.get("categoryCharts") or {}).items():
            for item in items:
                i_kw = (item.get("keywordEn") or item["keyword"]).lower()
                if i_kw == kw_lower:
                    top_temperature = item.get("temperature", top_temperature)
                    youtube_id = item.get("youtubeId")
                    break

    # Fallback country
    if not countries_with_trend:
        top_cc = top.get("country", "")
        if top_cc and top_cc in countries_data:
            countries_with_trend = [(countries_data[top_cc].get("flag", "\U0001f310"), countries_data[top_cc]["name"])]
        else:
            countries_with_trend = [(top.get("flag", "\U0001f310"), top_cc or "Global")]

    top_country_name = countries_with_trend[0][1] if countries_with_trend else top.get("country", "")

    # Rising fast (exclude spotlight itself)
    rising_list = []
    for r in g.get("risingFast", []):
        rk = r.get("keywordEn") or r["keyword"]
        if rk.lower() == kw_lower:
            continue
        cn_code = r.get("country", "")
        cn_name = countries_data.get(cn_code, {}).get("name", cn_code) if cn_code else ""
        rising_list.append((rk, cn_name, r.get("change", r.get("volume", ""))))

    # External links
    kw_encoded = urllib.parse.quote_plus(keyword_en)
    google_trends_url = f"https://trends.google.com/trends/explore?q={kw_encoded}"
    youtube_url = f"https://www.youtube.com/watch?v={youtube_id}" if youtube_id else None

    now = datetime.now(timezone.utc)
    return {
        "keyword":           top["keyword"],
        "keyword_en":        keyword_en,
        "category":          category,
        "category_label":    category_label,
        "top_country":       top.get("country", ""),
        "top_country_name":  top_country_name,
        "volume":            top.get("volume", "N/A"),
        "temperature":       g.get("temperature", 0),
        "top_temperature":   top_temperature,
        "total_countries":   g.get("totalCountries", len(countries_data)),
        "countries_list":    countries_with_trend[:12],
        "rising_list":       rising_list[:5],
        "cat_breakdown":     g.get("categoryBreakdown", {}),
        "source":            source,
        "youtube_url":       youtube_url,
        "google_trends_url": google_trends_url,
        "date_str":          format_date_str(now),
        "date_iso":          now.strftime("%Y-%m-%d"),
        "slug_en":           slugify(keyword_en),
        "site_url":          SITE_URL,
    }


# ---------------------------------------------------------------------------
# MDX builder
# ---------------------------------------------------------------------------

def build_mdx(lang: str, ctx: dict, rt: int = None) -> tuple[str, str]:
    tmpl  = TEMPLATES[lang]
    title   = tmpl["title"](ctx)
    excerpt = tmpl["excerpt"](ctx)
    body    = tmpl["body"](ctx)
    locale  = LANG_META[lang]["locale"]

    slug = f"{ctx['date_iso']}-spotlight-{ctx['slug_en']}-{lang}"
    if rt is None:
        rt = reading_time(body)

    alts_yaml = "\n".join(
        f'  {LANG_META[l]["hreflang"]}: /blog/{ctx["date_iso"]}-spotlight-{ctx["slug_en"]}-{l}'
        for l in ALL_LANGS
    )

    mdx = f"""---
slug: {slug}
title: "{title.replace('"', '\\"')}"
date: "{ctx['date_iso']}"
lastUpdated: "{now_iso()}"
excerpt: "{excerpt.replace('"', '\\"')}"
category: {ctx['category'] or 'news'}
language: {lang}
featured: true
readingTime: {rt}
tags:
  - {ctx['slug_en']}
  - {ctx['category'] or 'news'}
  - global-trends
  - trending
alternates:
{alts_yaml}
openGraph:
  title: "{title.replace('"', '\\"')}"
  description: "{excerpt.replace('"', '\\"')}"
  locale: {locale}
---

{body}"""

    return slug, mdx


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def main():
    log.info("=== Blog Post Generator Starting ===")
    trends_data = load_trends()
    index = load_index()

    g   = trends_data["global"]
    top = g["topTrend"]
    spotlight = (top.get("keywordEn") or top["keyword"]).strip().lower()

    today  = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=SKIP_WINDOW_DAYS)).strftime("%Y-%m-%d")

    recent = [r for r in index.get("recentSpotlights", []) if r.get("date", "") >= cutoff]
    index["recentSpotlights"] = recent
    recent_keywords = {r["keyword"].lower() for r in recent}

    log.info(f"Today's spotlight: '{spotlight}'")
    log.info(f"Recent spotlights (last {SKIP_WINDOW_DAYS}d): {sorted(recent_keywords) or '(none)'}")

    if spotlight in recent_keywords:
        matching = next(r for r in recent if r["keyword"].lower() == spotlight)
        log.info(f"'{spotlight}' already covered on {matching['date']} — skipping.")
        return

    log.info(f"New spotlight — generating {len(ALL_LANGS)} posts...")
    en_ctx = build_context(trends_data, "en")
    log.info(f"  Keyword: {en_ctx['keyword_en']}")
    log.info(f"  Category: {en_ctx['category_label']}, Temp: {en_ctx['top_temperature']}°T")
    log.info(f"  Countries: {len(en_ctx['countries_list'])}, YouTube: {bool(en_ctx['youtube_url'])}")

    # Use EN reading time for all languages (same article = same reading time)
    shared_rt = reading_time(TEMPLATES["en"]["body"](en_ctx))
    log.info(f"  Reading time (all langs): {shared_rt} min")

    new_posts = []
    for lang in ALL_LANGS:
        ctx  = build_context(trends_data, lang)
        slug, mdx_content = build_mdx(lang, ctx, rt=shared_rt)
        out_path = BLOG_DIR / f"{slug}.mdx"
        out_path.write_text(mdx_content, encoding="utf-8")
        log.info(f"  Written: {out_path.name}  ({shared_rt} min read)")

        new_posts.append({
            "slug":        slug,
            "title":       TEMPLATES[lang]["title"](ctx),
            "date":        today,
            "lastUpdated": now_iso(),
            "excerpt":     TEMPLATES[lang]["excerpt"](ctx),
            "category":    ctx["category"] or "news",
            "language":    lang,
            "readingTime": shared_rt,
            "featured":    True,
            "tags":        [ctx["slug_en"], ctx["category"] or "news", "global-trends", "trending"],
        })

    existing = index.get("posts", [])
    index["posts"] = new_posts + existing
    index["recentSpotlights"] = [{"keyword": spotlight, "date": today}] + [
        r for r in index.get("recentSpotlights", []) if r["keyword"].lower() != spotlight
    ]
    save_index(index)

    log.info(f"=== Done. {len(new_posts)} posts written. ===")


if __name__ == "__main__":
    main()
