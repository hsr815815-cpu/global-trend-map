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

        return textwrap.dedent(f"""\
**\"{c['keyword_en']}\"\u662f{c['date_str']}\u5168\u7403\u641c\u7d22\u91cf\u6392\u540d\u7b2c\u4e00\u7684\u8bdd\u9898\uff0c\
\u540c\u65f6\u5728{len(c['countries_list'])}\u4e2a\u56fd\u5bb6\u5f15\u53d1\u70ed\u641c\u6d6a\u6f6e\u3002\
\u5176\u4e2d\uff0c{c['top_country_name']}{top_flag}\u4ee5{c['volume']}\u6b21\u641c\u7d22\u6210\u4e3a\u672c\u6b21\u5168\u7403\u70ed\u641c\u7684\u6838\u5fc3\u9635\u5730\u3002**

\u65e0\u8bba\u4f60\u662f\u901a\u8fc7\u793e\u4ea4\u5a92\u4f53\u3001\u65b0\u95fb\u6807\u9898\u8fd8\u662f\u670b\u53cb\u5206\u4eab\u53d1\u73b0\u8fd9\u4e2a\u8bdd\u9898\uff0c\
\u4f60\u90fd\u6b63\u5728\u89c1\u8bc1\u4e00\u4e2a\u5168\u7403\u5171\u540c\u5173\u6ce8\u7684\u65f6\u523b\u3002\
\u4e0b\u9762\uff0c\u6211\u4eec\u57fa\u4e8e{c['total_countries']}\u4e2a\u56fd\u5bb6\u7684\u5b9e\u65f6\u6570\u636e\uff0c\u5168\u9762\u89e3\u6790\u8fd9\u4e00\u70ed\u70b9\u7684\u6210\u56e0\u3002

---

## "{c['keyword_en']}" \u662f\u4ec0\u4e48\uff1f\u4e3a\u4f55\u5168\u7403\u71c3\u70e7\uff1f

**\"{c['keyword_en']}\"\u5c5e\u4e8e{c['category_label']}\u7c7b\u522b\uff0c\u8d8b\u52bf\u6e29\u5ea6\u9ad8\u8fbe{c['top_temperature']}\u00b0T\uff08\u6ee1\u5206100\uff09\u3002\
\u8d77\u6e90\u4e8e{c['top_country_name']}\uff0c\u5c06\u71c3\u6210\u4e86\u5168\u7403\u641c\u7d22\u98ce\u66b4\u3002\
\u8be5\u8bdd\u9898\u8de8\u8d8a\u4e86\u5730\u57df\u548c\u8bed\u8a00\u969c\u788d\uff0c\u5728\u591a\u4e2a\u5927\u6d32\u540c\u65f6\u5f15\u53d1\u5f3a\u70c8\u53cd\u54cd\uff0c\u8fd9\u6b63\u662f\u771f\u6b63\u5168\u7403\u71c3\u70e7\u7684\u6807\u5fd7\u3002**

### \u6838\u5fc3\u6570\u636e\u4e00\u89c8

| \u6307\u6807 | \u6570\u636e |
|---|---|
| \u641c\u7d22\u91cf | {c['volume']} |
| \u8d8b\u52bf\u6e29\u5ea6 | {c['top_temperature']}\u00b0T |
| \u7c7b\u522b | {c['category_label']} |
| \u9886\u5148\u56fd\u5bb6 | {top_flag} {c['top_country_name']} |
| \u8986\u76d6\u56fd\u5bb6\u6570 | {len(c['countries_list'])} / {c['total_countries']} |
| \u6570\u636e\u66f4\u65b0\u65e5\u671f | {c['date_str']} |{yt_line}
---

## \u54ea\u4e9b\u56fd\u5bb6\u5728\u641c\u7d22 "{c['keyword_en']}"?

TrendPulse \u5b9e\u65f6\u76d1\u6d4b\u5168\u7403 **{c['total_countries']} \u4e2a\u56fd\u5bb6**\u7684\u641c\u7d22\u52a8\u6001\u3002\
\u4ee5\u4e0b\u662f\u5bf9 **\"{c['keyword_en']}\"** \u641c\u7d22\u70ed\u5ea6\u6700\u9ad8\u7684\u56fd\u5bb6\uff1a

{countries_md}

### \u6700\u5f3a\u4fe1\u53f7\u6765\u6e90

\u6700\u5f3a\u7684\u641c\u7d22\u4fe1\u53f7\u6765\u81ea **{c['top_country_name']}**\uff0c\u8be5\u56fd\u5f15\u9886\u4e86\u5168\u7403\u5173\u4e8e\
**\"{c['keyword_en']}\"** \u7684\u8ba8\u8bba\u3002\u5728{len(c['countries_list'])}\u4e2a\u56fd\u5bb6\u7684\u5e7f\u6cdb\u4f20\u64ad\u8bf4\u660e\uff0c\
\u8be5\u8bdd\u9898\u5df2\u8d85\u8d8a\u5c40\u90e8\u5730\u57df\u5c40\u9650\uff0c\u6210\u4e3a\u771f\u6b63\u5177\u6709\u5168\u7403\u5f71\u54cd\u529b\u7684\u6587\u5316\u73b0\u8c61\u3002

\U0001f5fa\ufe0f **\u67e5\u770b\u5730\u56fe\u6570\u636e\uff1a** [\u5b9e\u65f6\u5168\u7403\u8d8b\u52bf\u5730\u56fe]({c['site_url']})

---

## \u8d8b\u52bf\u6570\u636e\u8be6\u7ec6\u5206\u6790

{c['date_str']} \u7b2c\u4e00\u70ed\u641c\u8bdd\u9898 **\"{c['keyword_en']}\"** \u5b8c\u6574\u6570\u636e\uff1a

| \u6307\u6807 | \u6570\u636e |
|---|---|
| \u5cf0\u503c\u641c\u7d22\u91cf | {c['volume']} |
| \u8d8b\u52bf\u6e29\u5ea6 | {c['top_temperature']}\u00b0T |
| \u4e3b\u8981\u7c7b\u522b | {c['category_label']} |
| \u5168\u7403\u8986\u76d6 | {len(c['countries_list'])} \u4e2a\u56fd\u5bb6 |
| \u76d1\u6d4b\u56fd\u5bb6\u603b\u6570 | {c['total_countries']} |

\U0001f50d **\u5728Google\u8d8b\u52bf\u4e2d\u67e5\u770b\uff1a** \
[\u641c\u7d22 "{c['keyword_en']}" \u7684\u8d8b\u52bf\u53d8\u5316]({c['google_trends_url']})

---

## \u5f53\u524d\u5176\u4ed6\u5feb\u901f\u4e0a\u5347\u7684\u8bdd\u9898

\u5728 **\"{c['keyword_en']}\"** \u4e3b\u5bfc\u5168\u7403\u641c\u7d22\u7684\u540c\u65f6\uff0c\u8fd9\u4e9b\u8bdd\u9898\u4e5f\u5728\u5feb\u901f\u4e0a\u5347\uff1a

{rising_md}

---

## \u5f53\u524d\u5168\u7403\u641c\u7d22\u5206\u7c7b\u6982\u51b5

{cat_md}

---

## \u5e38\u89c1\u95ee\u9898\u89e3\u7b54

### "{c['keyword_en']}" \u662f\u4ec0\u4e48\uff1f

**\"{c['keyword_en']}\"** \u662f{c['date_str']}\u5168\u7403\u641c\u7d22\u7b2c\u4e00\u70ed\u8bcd\uff0c\
\u5728{len(c['countries_list'])}\u4e2a\u56fd\u5bb6\u8ffd\u8e2a\u3002\u5c5e\u4e8e{c['category_label']}\u7c7b\u522b\uff0c\
\u5728\u9886\u5148\u56fd\u5bb6\u4ea7\u751f\u4e86{c['volume']}\u6b21\u641c\u7d22\u3002\
\u8bbf\u95ee[\u5b9e\u65f6\u5730\u56fe]({c['site_url']})\u83b7\u53d6\u66f4\u591a\u5730\u7406\u6570\u636e\u3002

### \u54ea\u4e2a\u56fd\u5bb6\u641c\u7d22\u6700\u591a\uff1f

\u6839\u636e TrendPulse \u5b9e\u65f6\u6570\u636e\uff0c**{c['top_country_name']}** {top_flag} \
\u662f\u4eca\u65e5 **\"{c['keyword_en']}\"** \u641c\u7d22\u91cf\u6700\u9ad8\u7684\u56fd\u5bb6\uff0c\
\u5e76\u5df2\u8499\u5ef6\u81f3{max(0, len(c['countries_list']) - 1)}\u4e2a\u5176\u4ed6\u56fd\u5bb6\u3002

### TrendPulse \u5982\u4f55\u8861\u91cf\u8d8b\u52bf\u70ed\u5ea6\uff1f

TrendPulse \u6bcf\u5c0f\u65f6\u91c7\u96c6\u5168\u7403 **{c['total_countries']} \u4e2a\u56fd\u5bb6**\u7684\u641c\u7d22\u6570\u636e\uff0c\
\u6574\u5408Google\u641c\u7d22\u8d8b\u52bf\u3001YouTube\u3001Apple Music\u7b49\u591a\u4e2a\u6570\u636e\u6e90\u3002\
\u8d8b\u52bf\u6e29\u5ea6\uff080\uff5e100\uff09\u7efc\u5408\u641c\u7d22\u91cf\u3001\u5730\u7406\u8986\u76d6\u548c\u901f\u5ea6\uff0c\
\u751f\u6210\u5355\u4e00\u70ed\u5ea6\u6307\u6807\u3002

---

## \u5b9e\u65f6\u638c\u63e1\u5168\u7403\u8d8b\u52bf

\U0001f449 **[\u67e5\u770b\u5b9e\u65f6\u5168\u7403\u8d8b\u52bf\u5730\u56fe]({c['site_url']})** \u2014 \u6bcf\u5c0f\u65f6\u66f4\u65b0

\U0001f4f0 **[\u9605\u8bfb\u66f4\u591a\u8d8b\u52bf\u5206\u6790]({c['site_url']}/blog)** \u2014 \u6bcf\u65e5\u5168\u7403\u70ed\u70b9\u6df1\u5ea6\u89e3\u6790

*\u6570\u636e\u91c7\u96c6\u4e8e{c['date_str']}\u3002\u8d8b\u52bf\u6bcf\u5c0f\u65f6\u66f4\u65b0\u4e00\u6b21\u3002*
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

        return textwrap.dedent(f"""\
**\"{c['keyword_en']}\"** es la b\u00fasqueda #1 en todo el mundo el {c['date_str']}, \
con actividad intensa en {len(c['countries_list'])} pa\u00edses al mismo tiempo. \
El centro del fen\u00f3meno es **{c['top_country_name']}** {top_flag}, \
con {c['volume']} b\u00fasquedas registradas, convirtiendo este pa\u00eds en el epicentro de la tendencia global.

Ya sea que hayas descubierto este tema en redes sociales o en los titulares de noticias, \
eres parte de un momento mundial. Aqu\u00ed analizamos los datos reales de {c['total_countries']} pa\u00edses \
para explicar exactamente por qu\u00e9 **\"{c['keyword_en']}\"** est\u00e1 dominando la conversaci\u00f3n global.

---

## \u00bfQu\u00e9 es "{c['keyword_en']}" y por qu\u00e9 es tendencia?

**\"{c['keyword_en']}\"** pertenece a la categor\u00eda **{c['category_label']}** y ha alcanzado \
una Temperatura de Tendencia de **{c['top_temperature']}\u00b0T** en la escala 0\u2013100 de TrendPulse. \
Originado principalmente en **{c['top_country_name']}**, este tema se ha extendido \
r\u00e1pidamente a m\u00faltiples continentes, demostrando que ha trascendido el inter\u00e9s local.

### Estad\u00edsticas Principales

| M\u00e9trica | Valor |
|---|---|
| Volumen de B\u00fasqueda | {c['volume']} |
| Temperatura de Tendencia | {c['top_temperature']}\u00b0T / 100 |
| Categor\u00eda | {c['category_label']} |
| Pa\u00eds L\u00edder | {top_flag} {c['top_country_name']} |
| Pa\u00edses Rastreando | {len(c['countries_list'])} / {c['total_countries']} |
| Datos Actualizados | {c['date_str']} |{yt_line}
---

## \u00bfD\u00f3nde es tendencia "{c['keyword_en']}"?

Nuestros datos en tiempo real de {c['total_countries']} pa\u00edses muestran inter\u00e9s activo en:

{countries_md}

### El Origen del Fen\u00f3meno

La se\u00f1al m\u00e1s fuerte proviene de **{c['top_country_name']}**, que lidera la conversaci\u00f3n global. \
La distribuci\u00f3n en {len(c['countries_list'])} pa\u00edses confirma que esta tendencia ha superado \
el nivel local para convertirse en un fen\u00f3meno de alcance verdaderamente mundial.

\U0001f5fa\ufe0f **Explora los datos geogr\u00e1ficos:** \
[Ver el Mapa Global de Tendencias]({c['site_url']})

---

## Estad\u00edsticas y An\u00e1lisis de Datos

Desglose completo de la tendencia **\"{c['keyword_en']}\"** a fecha de {c['date_str']}:

| M\u00e9trica | Valor |
|---|---|
| Volumen Pico | {c['volume']} |
| Temperatura | {c['top_temperature']}\u00b0T |
| Categor\u00eda Principal | {c['category_label']} |
| Alcance Global | {len(c['countries_list'])} pa\u00edses |
| Total Pa\u00edses Monitoreados | {c['total_countries']} |

\U0001f50d **Consulta el historial:** \
[Ver en Google Trends]({c['google_trends_url']})

---

## Otras Tendencias en Ascenso Ahora Mismo

Mientras **\"{c['keyword_en']}\"** domina globalmente, estos temas tambi\u00e9n est\u00e1n subiendo con fuerza:

{rising_md}

---

## Desglose por Categor\u00edas Hoy

{cat_md}

---

## Preguntas Frecuentes

### \u00bfQu\u00e9 es "{c['keyword_en']}"?

**\"{c['keyword_en']}\"** es la tendencia #1 mundial del {c['date_str']}, rastreada en \
{len(c['countries_list'])} pa\u00edses, con {c['volume']} b\u00fasquedas en el pa\u00eds lder. \
Visita el [mapa en vivo]({c['site_url']}) para explorar datos geogr\u00e1ficos en tiempo real.

### \u00bfPor qu\u00e9 es tendencia hoy?

Ha alcanzado {c['top_temperature']}\u00b0T de Temperatura de Tendencia, con actividad en \
{len(c['countries_list'])} pa\u00edses. Esta propagaci\u00f3n masiva indica un evento viral, \
una noticia importante o un momento cultural significativo en el espacio **{c['category_label']}**. \
Consulta [Google Trends]({c['google_trends_url']}) para contexto hist\u00f3rico.

### \u00bfC\u00f3mo mide TrendPulse la intensidad?

TrendPulse recopila datos de **{c['total_countries']} pa\u00edses** cada hora, integrando \
Google Trends, YouTube, Apple Music y noticias globales. La **Temperatura de Tendencia** (0\u2013100) \
combina volumen, cobertura geogr\u00e1fica y velocidad en un \u00fanico indicador de intensidad.

---

## Monitorea las Tendencias Globales en Tiempo Real

\U0001f449 **[Explorar el Mapa Global en Vivo]({c['site_url']})** \u2014 actualizado cada hora

\U0001f4f0 **[Leer m\u00e1s an\u00e1lisis]({c['site_url']}/blog)** \u2014 las tendencias mundiales de cada d\u00eda

*Datos recopilados el {c['date_str']}. Las tendencias se actualizan cada hora.*
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

        return textwrap.dedent(f"""\
**\"{c['keyword_en']}\"** \u00e9 a busca #1 no mundo em {c['date_str']}, \
com atividade intensa em {len(c['countries_list'])} pa\u00edses simultaneamente. \
**{c['top_country_name']}** {top_flag} lidera com {c['volume']} pesquisas registradas, \
tornando-se o epicentro desta onda global de interesse digital.

---

## O que \u00e9 "{c['keyword_en']}" e por que est\u00e1 em alta?

**\"{c['keyword_en']}\"** pertence \u00e0 categoria **{c['category_label']}** e atingiu \
uma Temperatura de Tend\u00eancia de **{c['top_temperature']}\u00b0T** na escala 0\u2013100 do TrendPulse. \
Com origem em **{c['top_country_name']}**, o tema se espalhou rapidamente por m\u00faltiplos continentes, \
confirmando seu status de tend\u00eancia genuinamente global.

### Estat\u00edsticas Principais

| M\u00e9trica | Valor |
|---|---|
| Volume de Buscas | {c['volume']} |
| Temperatura de Tend\u00eancia | {c['top_temperature']}\u00b0T |
| Categoria | {c['category_label']} |
| Pa\u00eds L\u00edder | {top_flag} {c['top_country_name']} |
| Pa\u00edses Rastreando | {len(c['countries_list'])} / {c['total_countries']} |
| Atualizado em | {c['date_str']} |{yt_line}
---

## Onde "{c['keyword_en']}" \u00e9 tend\u00eancia?

Dados em tempo real de {c['total_countries']} pa\u00edses mostram interesse ativo em:

{countries_md}

O sinal mais forte vem de **{c['top_country_name']}**. A distribui\u00e7\u00e3o por {len(c['countries_list'])} pa\u00edses \
confirma que esta tend\u00eancia ultrapassou fronteiras locais.

\U0001f5fa\ufe0f **Explore os dados no mapa:** [Ver Mapa Global de Tend\u00eancias]({c['site_url']})

---

## An\u00e1lise de Dados da Tend\u00eancia

| M\u00e9trica | Valor |
|---|---|
| Pico de Buscas | {c['volume']} |
| Temperatura | {c['top_temperature']}\u00b0T |
| Categoria Principal | {c['category_label']} |
| Alcance Global | {len(c['countries_list'])} pa\u00edses |
| Total Monitorado | {c['total_countries']} pa\u00edses |

\U0001f50d **Verifique no Google Trends:** [Ver tend\u00eancia de "{c['keyword_en']}"]({c['google_trends_url']})

---

## Outras Tend\u00eancias em Alta Agora

{rising_md}

---

## Distribui\u00e7\u00e3o por Categorias Hoje

{cat_md}

---

## Perguntas Frequentes

### O que \u00e9 "{c['keyword_en']}"?

\u00c9 a tend\u00eancia #1 mundial de {c['date_str']}, rastreada em {len(c['countries_list'])} pa\u00edses \
com {c['volume']} buscas no pa\u00eds l\u00edder. Visite o [mapa ao vivo]({c['site_url']}) para explorar dados geogr\u00e1ficos.

### Por que est\u00e1 em tend\u00eancia hoje?

Atingiu {c['top_temperature']}\u00b0T de Temperatura de Tend\u00eancia, com atividade em {len(c['countries_list'])} pa\u00edses. \
Consulte o [Google Trends]({c['google_trends_url']}) para contexto hist\u00f3rico.

### Como o TrendPulse mede a intensidade?

Coletamos dados de **{c['total_countries']} pa\u00edses** por hora, integrando Google Trends, \
YouTube, Apple Music e not\u00edcias globais. A Temperatura de Tend\u00eancia (0\u2013100) \
combina volume, cobertura e velocidade em um \u00fanico indicador.

---

## Monitore as Tend\u00eancias Globais em Tempo Real

\U0001f449 **[Explorar o Mapa Global]({c['site_url']})** \u2014 atualizado a cada hora

\U0001f4f0 **[Ler mais an\u00e1lises]({c['site_url']}/blog)** \u2014 as maiores tend\u00eancias do mundo todo dia

*Dados coletados em {c['date_str']}. Tend\u00eancias atualizam a cada hora.*
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

        return textwrap.dedent(f"""\
**\"{c['keyword_en']}\"** est la recherche #1 dans le monde le {c['date_str']}, \
avec une activit\u00e9 intense dans {len(c['countries_list'])} pays simultan\u00e9ment. \
**{c['top_country_name']}** {top_flag} est en t\u00eate avec {c['volume']} recherches, \
faisant de ce pays l\u2019\u00e9picentre de cette vague d\u2019int\u00e9r\u00eat num\u00e9rique mondial.

---

## Qu'est-ce que "{c['keyword_en']}" et pourquoi est-il en tendance\u00a0?

**\"{c['keyword_en']}\"** appartient \u00e0 la cat\u00e9gorie **{c['category_label']}** et a atteint \
une Temp\u00e9rature de Tendance de **{c['top_temperature']}\u00b0T** sur l\u2019\u00e9chelle 0\u2013100 de TrendPulse. \
N\u00e9 principalement en **{c['top_country_name']}**, le sujet s\u2019est rapidement r\u00e9pandu \
sur plusieurs continents, confirmant son statut de tendance v\u00e9ritablement mondiale.

### Statistiques Cl\u00e9s

| Indicateur | Valeur |
|---|---|
| Volume de recherche | {c['volume']} |
| Temp\u00e9rature de tendance | {c['top_temperature']}\u00b0T |
| Cat\u00e9gorie | {c['category_label']} |
| Pays leader | {top_flag} {c['top_country_name']} |
| Pays suivis | {len(c['countries_list'])} / {c['total_countries']} |
| Mise \u00e0 jour | {c['date_str']} |{yt_line}
---

## O\u00f9 "{c['keyword_en']}" est-il en tendance\u00a0?

Nos donn\u00e9es en temps r\u00e9el de {c['total_countries']} pays montrent un int\u00e9r\u00eat actif dans\u00a0:

{countries_md}

Le signal le plus fort provient de **{c['top_country_name']}**. La diffusion dans {len(c['countries_list'])} pays \
confirme que ce sujet a d\u00e9pass\u00e9 les fronti\u00e8res locales pour devenir un ph\u00e9nom\u00e8ne mondial.

\U0001f5fa\ufe0f **Explorez la carte\u00a0:** [Carte mondiale des tendances en direct]({c['site_url']})

---

## Statistiques et Analyse de la Tendance

| Indicateur | Valeur |
|---|---|
| Pic de volume | {c['volume']} |
| Temp\u00e9rature | {c['top_temperature']}\u00b0T |
| Cat\u00e9gorie principale | {c['category_label']} |
| Port\u00e9e mondiale | {len(c['countries_list'])} pays |
| Total pays surveill\u00e9s | {c['total_countries']} |

\U0001f50d **V\u00e9rifiez par vous-m\u00eame\u00a0:** \
[Voir \"{c['keyword_en']}\" sur Google Trends]({c['google_trends_url']})

---

## Autres Tendances en Hausse en ce Moment

{rising_md}

---

## R\u00e9partition par Cat\u00e9gories Aujourd\u2019hui

{cat_md}

---

## Foire Aux Questions

### Qu'est-ce que "{c['keyword_en']}" ?

**\"{c['keyword_en']}\"** est la tendance mondiale #1 du {c['date_str']}, suivie dans \
{len(c['countries_list'])} pays avec {c['volume']} recherches dans le pays leader. \
Visitez la [carte en direct]({c['site_url']}) pour explorer les donn\u00e9es g\u00e9ographiques.

### Pourquoi est-il en tendance aujourd\u2019hui ?

Il a atteint {c['top_temperature']}\u00b0T de Temp\u00e9rature de Tendance, avec une activit\u00e9 dans \
{len(c['countries_list'])} pays. Cette propagation massive signale un \u00e9v\u00e9nement viral ou \
un moment culturel significatif dans l\u2019espace **{c['category_label']}**. \
Consultez [Google Trends]({c['google_trends_url']}) pour le contexte historique.

### Comment TrendPulse mesure-t-il l\u2019intensit\u00e9 ?

TrendPulse collecte les donn\u00e9es de **{c['total_countries']} pays** chaque heure, \
en agr\u00e9geant Google Trends, YouTube, Apple Music et les actualit\u00e9s mondiales. \
La Temp\u00e9rature de Tendance (0\u2013100) combine volume, couverture et v\u00e9locit\u00e9.

---

## Suivez Toutes les Tendances Mondiales en Temps R\u00e9el

\U0001f449 **[Explorer la Carte Mondiale en Direct]({c['site_url']})** \u2014 mise \u00e0 jour chaque heure

\U0001f4f0 **[Lire plus d\u2019analyses]({c['site_url']}/blog)** \u2014 les grandes tendances mondiales chaque jour

*Donn\u00e9es collect\u00e9es le {c['date_str']}. Mise \u00e0 jour toutes les heures.*
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

        return textwrap.dedent(f"""\
**\"{c['keyword_en']}\"** ist am {c['date_str']} die weltweit meistgesuchte Suchanfrage, \
mit intensiver Aktivit\u00e4t in {len(c['countries_list'])} L\u00e4ndern gleichzeitig. \
**{c['top_country_name']}** {top_flag} f\u00fchrt mit {c['volume']} Suchanfragen \
und ist damit das Epizentrum dieser globalen Trendwelle.

---

## Was ist "{c['keyword_en']}" und warum liegt es im Trend?

**\"{c['keyword_en']}\"** geh\u00f6rt zur Kategorie **{c['category_label']}** und erreicht \
eine Trend-Temperatur von **{c['top_temperature']}\u00b0T** auf der TrendPulse-Skala von 0\u2013100. \
Urspr\u00fcnglich aus **{c['top_country_name']}**, hat sich das Thema rasch \u00fcber mehrere Kontinente \
ausgebreitet und seinen Status als echten globalen Trend best\u00e4tigt.

### Wichtigste Statistiken

| Kennzahl | Wert |
|---|---|
| Suchvolumen | {c['volume']} |
| Trend-Temperatur | {c['top_temperature']}\u00b0T |
| Kategorie | {c['category_label']} |
| F\u00fchrendes Land | {top_flag} {c['top_country_name']} |
| L\u00e4nder im Tracking | {len(c['countries_list'])} / {c['total_countries']} |
| Daten aktualisiert | {c['date_str']} |{yt_line}
---

## Wo liegt "{c['keyword_en']}" im Trend?

Unsere Echtzeit-Daten aus {c['total_countries']} L\u00e4ndern zeigen aktives Suchinteresse in:

{countries_md}

Das st\u00e4rkste Signal kommt aus **{c['top_country_name']}**. Die Verteilung \u00fcber {len(c['countries_list'])} L\u00e4nder \
best\u00e4tigt, dass dieses Thema lokale Grenzen \u00fcberschritten hat.

\U0001f5fa\ufe0f **Karte erkunden:** [Globale Echtzeit-Trendkarte]({c['site_url']})

---

## Trend-Statistiken im Detail

| Kennzahl | Wert |
|---|---|
| Suchvolumen-Spitze | {c['volume']} |
| Temperatur | {c['top_temperature']}\u00b0T |
| Hauptkategorie | {c['category_label']} |
| Globale Reichweite | {len(c['countries_list'])} L\u00e4nder |
| Gesamt \u00fcberwachte L\u00e4nder | {c['total_countries']} |

\U0001f50d **Selbst pr\u00fcfen:** ["{c['keyword_en']}" auf Google Trends]({c['google_trends_url']})

---

## Weitere aufsteigende Trends gerade jetzt

{rising_md}

---

## Heutige Trendkategorien im \u00dcberblick

{cat_md}

---

## H\u00e4ufig gestellte Fragen

### Was ist "{c['keyword_en']}"?

**\"{c['keyword_en']}\"** ist der weltweite Trend #1 vom {c['date_str']}, verfolgt in \
{len(c['countries_list'])} L\u00e4ndern mit {c['volume']} Suchen im f\u00fchrenden Land. \
Besuchen Sie die [Live-Karte]({c['site_url']}) f\u00fcr geografische Echtzeitdaten.

### Warum liegt es gerade im Trend?

Es hat {c['top_temperature']}\u00b0T Trend-Temperatur erreicht, mit Aktivit\u00e4t in {len(c['countries_list'])} L\u00e4ndern. \
Diese massive Ausbreitung signalisiert ein virales Ereignis oder einen kulturellen Moment \
im Bereich **{c['category_label']}**. Konsultieren Sie [Google Trends]({c['google_trends_url']}) f\u00fcr historischen Kontext.

### Wie misst TrendPulse die Intensit\u00e4t?

TrendPulse erfasst st\u00fcndlich Daten aus **{c['total_countries']} L\u00e4ndern**, \
aggregiert aus Google Trends, YouTube, Apple Music und globalen Nachrichten. \
Die Trend-Temperatur (0\u2013100) kombiniert Volumen, geografische Abdeckung und Geschwindigkeit.

---

## Globale Trends in Echtzeit verfolgen

\U0001f449 **[Zur Live-Trendkarte]({c['site_url']})** \u2014 st\u00fcndlich aktualisiert

\U0001f4f0 **[Mehr Analysen lesen]({c['site_url']}/blog)** \u2014 die wichtigsten Trends der Welt t\u00e4glich

*Daten erhoben am {c['date_str']}. Trends werden st\u00fcndlich aktualisiert.*
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

        return textwrap.dedent(f"""\
**\"{c['keyword_en']}\"**\uc740 {c['date_str']} \uae30\uc900 \uc804 \uc138\uacc4 \uac80\uc0c9\uc5b4 1\uc704\ub97c \uae30\ub85d\ud55c \ud0a4\uc6cc\ub4dc\ub85c, \
{len(c['countries_list'])}\uac1c\uad6d\uc5d0\uc11c \ub3d9\uc2dc\uc5d0 \ud3ed\ubc1c\uc801\uc778 \uac80\uc0c9\ub7c9 \uc99d\uac00\uac00 \uad00\uce21\ub418\uace0 \uc788\uc2b5\ub2c8\ub2e4. \
\uc8fc\uc694 \uc0c1\uc2b9\uc740 **{c['top_country_name']}** {top_flag}\uc5d0\uc11c \ubc1c\uc0dd\ud588\uc73c\uba70, \
\uc774\uacf3\uc5d0\uc11c\ub9cc {c['volume']}\uac74\uc758 \uac80\uc0c9\uc774 \uae30\ub85d\ub418\uc5c8\uc2b5\ub2c8\ub2e4.

{c['total_countries']}\uac1c\uad6d \uc2e4\uc2dc\uac04 \ub370\uc774\ud130\ub97c \ubc14\ud0d5\uc73c\ub85c, \uc5d0 **\"{c['keyword_en']}\"**\uc774 \uc601\ud5a5\ub825 \uc788\ub294 \uc804 \uc138\uacc4\uc801 \ud654\uc81c\uac00 \ub41c \uc774\uc720\ub97c \uc0c1\uc138\ud788 \ubd84\uc11d\ud569\ub2c8\ub2e4.

---

## "{c['keyword_en']}"란 무엇이고, 왜 트렌드가 됐나요?

**\"{c['keyword_en']}\"**\uc740 **{c['category_label']}** \uce74\ud14c\uace0\ub9ac\uc5d0 \uc18d\ud558\uba70, \
TrendPulse\uc758 0\u2013100 \uc2a4\ucf00\uc77c\uc5d0\uc11c **{c['top_temperature']}\u00b0T**\uc758 \ud2b8\ub80c\ub4dc \uc628\ub3c4\ub97c \uae30\ub85d\ud558\uace0 \uc788\uc2b5\ub2c8\ub2e4. \
**{c['top_country_name']}**\uc5d0\uc11c \uc2dc\uc791\ub41c \uc774 \ud0a4\uc6cc\ub4dc\ub294 \ube60\ub974\uac8c \uc5ec\ub7ec \ub300\ub959\uc73c\ub85c \ud655\uc0b0\ub418\uba70 \uc9c4\uc815\ud55c \uae00\ub85c\ubc8c \ud2b8\ub80c\ub4dc\uc784\uc744 \uc785\uc99d\ud558\uace0 \uc788\uc2b5\ub2c8\ub2e4.

### 핵심 통계 요약

| \uc9c0\ud45c | \uac12 |
|---|---|
| \uac80\uc0c9\ub7c9 | {c['volume']} |
| \ud2b8\ub80c\ub4dc \uc628\ub3c4 | {c['top_temperature']}\u00b0T |
| \uce74\ud14c\uace0\ub9ac | {c['category_label']} |
| \uc8fc\uc694 \uad6d\uac00 | {top_flag} {c['top_country_name']} |
| \ucd94\uc801 \uad6d\uac00 \uc218 | {len(c['countries_list'])} / {c['total_countries']} |
| \ub370\uc774\ud130 \uae30\uc900\uc77c | {c['date_str']} |{yt_line}
---

## 어느 나라에서 "{c['keyword_en']}"을 검색하나요?

{c['total_countries']}\uac1c\uad6d \uc2e4\uc2dc\uac04 \ub370\uc774\ud130 \uae30\uc900, \ub2e4\uc74c \uad6d\uac00\ub4e4\uc5d0\uc11c \ub192\uc740 \uac80\uc0c9 \uad00\uc2ec\ub3c4\uac00 \ud655\uc778\ub429\ub2c8\ub2e4:

{countries_md}

### 가장 강한 신호가 오는 곳

\uac00\uc7a5 \uac15\ud55c \uc2e0\ud638\ub294 **{c['top_country_name']}**\uc5d0\uc11c \ubc1c\uc0dd\ud558\uace0 \uc788\uc2b5\ub2c8\ub2e4. \
{len(c['countries_list'])}\uac1c\uad6d\uc5d0 \uac78\uce5c \ud655\uc0b0\uc740 \uc774 \ud2b8\ub80c\ub4dc\uac00 \uc9c0\uc5ed\uc801 \uad00\uc2ec\uc744 \ub118\uc5b4 \
\uc9c4\uc815\ud55c \uc804 \uc138\uacc4\uc801 \ubb38\ud654 \ud604\uc0c1\uc774 \ub428\uc744 \ubcf4\uc5ec\uc90d\ub2c8\ub2e4.

\U0001f5fa\ufe0f **\uc9c0\ub3c4\uc5d0\uc11c \ud655\uc778\ud558\uae30:** [\uc2e4\uc2dc\uac04 \uae00\ub85c\ubc8c \ud2b8\ub80c\ub4dc \ub9f5]({c['site_url']})

---

## 트렌드 데이터 상세 분석

{c['date_str']} \uae30\uc900 **\"{c['keyword_en']}\"** \ud2b8\ub80c\ub4dc \uc644\uc804 \ud1b5\uacc4:

| \uc9c0\ud45c | \uac12 |
|---|---|
| \uac80\uc0c9\ub7c9 | {c['volume']} |
| \ud2b8\ub80c\ub4dc \uc628\ub3c4 | {c['top_temperature']}\u00b0T |
| \uc8fc\uc694 \uce74\ud14c\uace0\ub9ac | {c['category_label']} |
| \uc804 \uc138\uacc4 \ubc94\uc704 | {len(c['countries_list'])}\uac1c\uad6d |
| \uc804\uccb4 \ubaa8\ub2c8\ud130\ub9c1 \uad6d\uac00 | {c['total_countries']}\uac1c\uad6d |

\U0001f50d **\uc9c1\uc811 \ud655\uc778\ud558\uae30:** [Google \ud2b8\ub80c\ub4dc\uc5d0\uc11c \"\"{c['keyword_en']}\" \ubcf4\uae30]({c['google_trends_url']})

---

## 지금 빠르게 올라오는 다른 트렌드

{rising_md}

---

## 오늘의 카테고리별 검색 현황

{cat_md}

---

## 자주 묻는 질문 (FAQ)

### "{c['keyword_en']}"이란 무엇인가요?

**\"{c['keyword_en']}\"**\uc740 {c['date_str']} \uae30\uc900 \uc804 \uc138\uacc4 \uac80\uc0c9\uc5b4 1\uc704\ub85c, \
{len(c['countries_list'])}\uac1c\uad6d\uc5d0\uc11c \ucd94\uc801\ub418\uace0 \uc788\uc2b5\ub2c8\ub2e4. \
{c['category_label']} \uce74\ud14c\uace0\ub9ac\uc5d0 \uc18d\ud558\uba70, \uc8fc\uc694 \uad6d\uac00\uc5d0\uc11c\ub9cc {c['volume']}\uac74\uc758 \uac80\uc0c9\uc774 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \
[\uc2e4\uc2dc\uac04 \ud2b8\ub80c\ub4dc \ub9f5]({c['site_url']})\uc5d0\uc11c \uc9c0\ub9ac\uc801 \ub370\uc774\ud130\ub97c \ud655\uc778\ud558\uc138\uc694.

### 왜 지금 트렌드인가요?

{c['top_temperature']}\u00b0T\uc758 \ud2b8\ub80c\ub4dc \uc628\ub3c4\ub97c \uae30\ub85d\ud558\uba70 {len(c['countries_list'])}\uac1c\uad6d\uc5d0\uc11c \ub3d9\uc2dc\uc5d0 \uc5ed\ub300\uae09 \uc0c1\uc2b9 \uc911\uc785\ub2c8\ub2e4. \
\uc774\ub7ec\ud55c \ub2e4\uad6d\uc801 \uae09\uc0c1\uc2b9\uc740 \ubc14\uc774\ub7f4 \uc774\ubca4\ud2b8, \ubc14\uc774\ub7f4 \ucf58\ud150\uce20 \ub610\ub294 \ub300\uaddc\ubaa8 \ubb38\ud654\uc801 \uc21c\uac04\uc744 \uc2dc\uc0ac\ud569\ub2c8\ub2e4. \
[Google \ud2b8\ub80c\ub4dc]({c['google_trends_url']})\uc5d0\uc11c \uacfc\uac70 \ub370\uc774\ud130\ub97c \ud655\uc778\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.

### TrendPulse는 어떻게 트렌드 강도를 측정하나요?

TrendPulse\ub294 **{c['total_countries']}\uac1c\uad6d**\uc758 \ub370\uc774\ud130\ub97c \ub9e4\uc2dc\uac04 \uc218\uc9d1\ud558\uc5ec Google \ud2b8\ub80c\ub4dc, YouTube, \
Apple Music, \uc804 \uc138\uacc4 \ub274\uc2a4 \ub4f1 \ub2e4\uc591\ud55c \uc18c\uc2a4\ub97c \ud1b5\ud569\ud569\ub2c8\ub2e4. \
\ud2b8\ub80c\ub4dc \uc628\ub3c4(0\u2013100)\ub294 \uac80\uc0c9\ub7c9, \uc9c0\ub9ac\uc801 \ubc94\uc704, \uc18d\ub3c4\ub97c \ud558\ub098\uc758 \uc9c0\ud45c\ub85c \ud1b5\ud569\ud569\ub2c8\ub2e4.

---

## 실시간으로 전 세계 트렌드를 파악하세요

\U0001f449 **[\uc2e4\uc2dc\uac04 \uae00\ub85c\ubc8c \ud2b8\ub80c\ub4dc \ub9f5 \ubcf4\uae30]({c['site_url']})** \u2014 \ub9e4\uc2dc\uac04 \uc5c5\ub370\uc774\ud2b8

\U0001f4f0 **[\ub354 \ub9ce\uc740 \ud2b8\ub80c\ub4dc \ubd84\uc11d \uc77d\uae30]({c['site_url']}/blog)** \u2014 \ub9e4\uc77c \uc138\uacc4 \ud2b8\ub80c\ub4dc 1\uc704 \uc2ec\uce35 \ubd84\uc11d

*\ub370\uc774\ud130 \uc218\uc9d1\uc77c: {c['date_str']}. \ud2b8\ub80c\ub4dc\ub294 \ub9e4\uc2dc\uac04 \uc5c5\ub370\uc774\ud2b8\ub429\ub2c8\ub2e4.*
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

        return textwrap.dedent(f"""\
**\u300c{c['keyword_en']}\u300d**\u306f{c['date_str']}\u73fe\u5728\u3001\u4e16\u754c\u4e2d\u3067\u6700\u3082\u691c\u7d22\u3055\u308c\u3066\u3044\u308b\u30c8\u30d4\u30c3\u30af\u3067\u3001\
{len(c['countries_list'])}\u304b\u56fd\u3067\u540c\u6642\u306b\u6025\u4e0a\u6607\u3057\u3066\u3044\u307e\u3059\u3002\
\u4e3b\u5c0e\u3059\u308b\u306e\u306f **{c['top_country_name']}** {top_flag}\u3067\u3001\
{c['volume']}\u4ef6\u306e\u691c\u7d22\u304c\u8a18\u9332\u3055\u308c\u3001\u4eca\u65e5\u306e\u30b0\u30ed\u30fc\u30d0\u30eb\u30c8\u30ec\u30f3\u30c9\u306e\u9707\u6e90\u5730\u3068\u306a\u3063\u3066\u3044\u307e\u3059\u3002

---

## 「{c['keyword_en']}」とは何か？なぜトレンド入りしたのか？

**\u300c{c['keyword_en']}\u300d**\u306f **{c['category_label']}** \u30ab\u30c6\u30b4\u30ea\u306b\u5c5e\u3057\u3001\
TrendPulse\u306e0\u20131000\u30b9\u30b1\u30fc\u30eb\u3067 **{c['top_temperature']}\u00b0T** \u306e\u30c8\u30ec\u30f3\u30c9\u6e29\u5ea6\u3092\u8a18\u9332\u3057\u3066\u3044\u307e\u3059\u3002\
**{c['top_country_name']}**\u767a\u306e\u8a71\u984c\u304c\u8fc5\u901f\u306b\u8907\u6570\u5927\u9678\u306b\u5e83\u304c\u308a\u3001\
\u771f\u306b\u30b0\u30ed\u30fc\u30d0\u30eb\u306a\u30c8\u30ec\u30f3\u30c9\u3067\u3042\u308b\u3053\u3068\u3092\u8a3c\u660e\u3057\u3066\u3044\u307e\u3059\u3002

### 主要統計

| \u6307\u6a19 | \u5024 |
|---|---|
| \u691c\u7d22\u30dc\u30ea\u30e5\u30fc\u30e0 | {c['volume']} |
| \u30c8\u30ec\u30f3\u30c9\u6e29\u5ea6 | {c['top_temperature']}\u00b0T |
| \u30ab\u30c6\u30b4\u30ea | {c['category_label']} |
| \u30ea\u30fc\u30c9\u56fd | {top_flag} {c['top_country_name']} |
| \u8ffd\u8de1\u56fd\u6570 | {len(c['countries_list'])} / {c['total_countries']} |
| \u30c7\u30fc\u30bf\u66f4\u65b0\u65e5 | {c['date_str']} |{yt_line}
---

## 「{c['keyword_en']}」はどの国でトレンドになっているか？

{c['total_countries']}\u304b\u56fd\u306e\u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u30c7\u30fc\u30bf\u3067\u3001\u4ee5\u4e0b\u306e\u56fd\u3067\u9ad8\u3044\u691c\u7d22\u95a2\u5fc3\u304c\u78ba\u8a8d\u3055\u308c\u3066\u3044\u307e\u3059\uff1a

{countries_md}

\u6700\u3082\u5f37\u3044\u30b7\u30b0\u30ca\u30eb\u306f **{c['top_country_name']}** \u304b\u3089\u767a\u4fe1\u3055\u308c\u3066\u3044\u307e\u3059\u3002\
{len(c['countries_list'])}\u304b\u56fd\u306b\u307e\u305f\u304c\u308b\u62e1\u6563\u306f\u3001\u3053\u306e\u8a71\u984c\u304c\u5c40\u5730\u7684\u306a\u95a2\u5fc3\u3092\u8d85\u3048\u3001\
\u771f\u306e\u30b0\u30ed\u30fc\u30d0\u30eb\u30ab\u30eb\u30c1\u30e3\u30fc\u73fe\u8c61\u3068\u306a\u3063\u305f\u3053\u3068\u3092\u793a\u3057\u3066\u3044\u307e\u3059\u3002

\U0001f5fa\ufe0f **\u5730\u56f3\u3067\u78ba\u8a8d\uff1a** [\u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u30b0\u30ed\u30fc\u30d0\u30eb\u30c8\u30ec\u30f3\u30c9\u30de\u30c3\u30d7]({c['site_url']})

---

## トレンドデータの詳細分析

{c['date_str']}\u6642\u70b9\u306e **\u300c{c['keyword_en']}\u300d** \u5b8c\u5168\u30c7\u30fc\u30bf\uff1a

| \u6307\u6a19 | \u5024 |
|---|---|
| \u30d4\u30fc\u30af\u691c\u7d22\u30dc\u30ea\u30e5\u30fc\u30e0 | {c['volume']} |
| \u30c8\u30ec\u30f3\u30c9\u6e29\u5ea6 | {c['top_temperature']}\u00b0T |
| \u4e3b\u8981\u30ab\u30c6\u30b4\u30ea | {c['category_label']} |
| \u30b0\u30ed\u30fc\u30d0\u30eb\u30ea\u30fc\u30c1 | {len(c['countries_list'])}\u304b\u56fd |
| \u76e3\u8996\u5bfe\u8c61\u56fd\u6570 | {c['total_countries']} |

\U0001f50d **\u81ea\u5206\u3067\u78ba\u8a8d\uff1a** \
[Google \u30c8\u30ec\u30f3\u30c9\u3067\u300c{c['keyword_en']}\u300d\u3092\u691c\u7d22]({c['google_trends_url']})

---

## 今まさに急上昇中の他のトレンド

{rising_md}

---

## 今日のカテゴリ別トレンド分布

{cat_md}

---

## よくある質問（FAQ）

### 「{c['keyword_en']}」とは何ですか？

**\u300c{c['keyword_en']}\u300d**\u306f{c['date_str']}\u306e\u4e16\u754c\u691c\u7d22\u30e9\u30f3\u30ad\u30f31\u4f4d\u306e\u30c8\u30d4\u30c3\u30af\u3067\u3001\
{len(c['countries_list'])}\u304b\u56fd\u3067\u8ffd\u8de1\u3055\u308c\u3066\u3044\u307e\u3059\u3002\
{c['category_label']}\u30ab\u30c6\u30b4\u30ea\u306b\u5c5e\u3057\u3001\u30ea\u30fc\u30c9\u56fd\u3067\u306f{c['volume']}\u4ef6\u306e\u691c\u7d22\u304c\u767a\u751f\u3002\
[\u30e9\u30a4\u30d6\u30de\u30c3\u30d7]({c['site_url']})\u3067\u5730\u7406\u30c7\u30fc\u30bf\u3092\u78ba\u8a8d\u3067\u304d\u307e\u3059\u3002

### なぜ今トレンドになっているのですか？

{c['top_temperature']}\u00b0T\u306e\u30c8\u30ec\u30f3\u30c9\u6e29\u5ea6\u3092\u8a18\u9332\u3057\u3001{len(c['countries_list'])}\u304b\u56fd\u3067\u540c\u6642\u306b\u6025\u4e0a\u6607\u4e2d\u3067\u3059\u3002\
\u3053\u306e\u3088\u3046\u306a\u591a\u56fd\u540c\u6642\u6025\u4e0a\u6607\u306f\u3001\u30d0\u30a4\u30e9\u30eb\u30a4\u30d9\u30f3\u30c8\u3084\u91cd\u5927\u306a\u6587\u5316\u7684\u77ac\u9593\u3092\u793a\u3059\u30b7\u30b0\u30ca\u30eb\u3067\u3059\u3002\
[Google\u30c8\u30ec\u30f3\u30c9]({c['google_trends_url']})\u3067\u904e\u53bb\u306e\u30c7\u30fc\u30bf\u3082\u78ba\u8a8d\u3067\u304d\u307e\u3059\u3002

### TrendPulseはどうやってトレンド強度を測定しますか？

TrendPulse\u306f**{c['total_countries']}\u304b\u56fd**\u306e\u30c7\u30fc\u30bf\u3092\u6bce\u6642\u53ce\u96c6\u3057\u3001\
Google\u30c8\u30ec\u30f3\u30c9\u3001YouTube\u3001Apple Music\u3001\u30b0\u30ed\u30fc\u30d0\u30eb\u30cb\u30e5\u30fc\u30b9\u3092\u7d71\u5408\u3057\u307e\u3059\u3002\
\u30c8\u30ec\u30f3\u30c9\u6e29\u5ea6\uff080\u2013100\uff09\u306f\u691c\u7d22\u30dc\u30ea\u30e5\u30fc\u30e0\u3001\u5730\u7406\u7684\u7bc4\u56f2\u3001\u901f\u5ea6\u3092\u4e00\u3064\u306e\u6307\u6a19\u306b\u7d71\u5408\u3057\u305f\u3082\u306e\u3067\u3059\u3002

---

## リアルタイムで世界のトレンドを把握する

\U0001f449 **[\u30ea\u30a2\u30eb\u30bf\u30a4\u30e0\u30b0\u30ed\u30fc\u30d0\u30eb\u30c8\u30ec\u30f3\u30c9\u30de\u30c3\u30d7\u3092\u898b\u308b]({c['site_url']})** \u2014 \u6bce\u6642\u66f4\u65b0

\U0001f4f0 **[\u30c8\u30ec\u30f3\u30c9\u5206\u6790\u3092\u3082\u3063\u3068\u8aad\u3080]({c['site_url']}/blog)** \u2014 \u6bce\u65e5\u4e16\u754c\u306e\u30c8\u30c3\u30d7\u30c8\u30ec\u30f3\u30c9\u3092\u6df1\u5c64\u5206\u6790

*\u30c7\u30fc\u30bf\u53ce\u96c6\u65e5\uff1a{c['date_str']}\u3002\u30c8\u30ec\u30f3\u30c9\u306f\u6bce\u6642\u66f4\u65b0\u3055\u308c\u307e\u3059\u3002*
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

def build_mdx(lang: str, ctx: dict) -> tuple[str, str]:
    tmpl  = TEMPLATES[lang]
    title   = tmpl["title"](ctx)
    excerpt = tmpl["excerpt"](ctx)
    body    = tmpl["body"](ctx)
    locale  = LANG_META[lang]["locale"]

    slug = f"{ctx['date_iso']}-spotlight-{ctx['slug_en']}-{lang}"
    rt   = reading_time(body)

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

    new_posts = []
    for lang in ALL_LANGS:
        ctx  = build_context(trends_data, lang)
        slug, mdx_content = build_mdx(lang, ctx)
        out_path = BLOG_DIR / f"{slug}.mdx"
        out_path.write_text(mdx_content, encoding="utf-8")
        log.info(f"  Written: {out_path.name}  ({reading_time(TEMPLATES[lang]['body'](ctx))} min read)")

        new_posts.append({
            "slug":        slug,
            "title":       TEMPLATES[lang]["title"](ctx),
            "date":        today,
            "lastUpdated": now_iso(),
            "excerpt":     TEMPLATES[lang]["excerpt"](ctx),
            "category":    ctx["category"] or "news",
            "language":    lang,
            "readingTime": reading_time(TEMPLATES[lang]["body"](ctx)),
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
