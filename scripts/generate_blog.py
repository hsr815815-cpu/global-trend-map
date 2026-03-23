#!/usr/bin/env python3
"""
generate_blog.py — Automated Blog Post Generator
Reads public/data/trends.json and generates MDX blog posts in EN, KR, JP.
Updates public/data/posts-index.json.
Usage: python scripts/generate_blog.py
"""

import json
import re
import time
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import quote

try:
    import requests
except ImportError:
    raise SystemExit("ERROR: 'requests' not installed. Run: pip install requests feedparser")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR     = Path(__file__).resolve().parent.parent
DATA_DIR     = BASE_DIR / "public" / "data"
BLOG_DIR     = BASE_DIR / "public" / "blog"
TRENDS_FILE  = DATA_DIR / "trends.json"
INDEX_FILE   = DATA_DIR / "posts-index.json"

BLOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("generate_blog")

BLOCKED_KEYWORDS = {
    "porn", "xxx", "nude", "naked", "sex tape", "onlyfans leak",
    "murder how to", "kill guide", "bomb making",
    "white supremacy", "nazi", "racial slur",
    "casino hack", "slot cheat", "betting exploit",
    "buy drugs", "drug synthesis", "meth recipe",
    "terrorist attack plan", "jihad recruit", "isis guide",
}

MAJOR_COUNTRIES = ["US", "KR", "JP", "GB", "DE"]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; GlobalTrendBot/1.0)"}

# ---------------------------------------------------------------------------
# Translations (UI strings only — data values are substituted directly)
# ---------------------------------------------------------------------------

TRANSLATIONS = {
    "en": {
        "author":             "Global Trend Map",
        "trending_now":       "Trending Now",
        "top_global_trend":   "Today's Top Global Trend",
        "country_trending":   "Trending Now",
        "weekly_roundup":     "Weekly Trend Roundup",
        "what_is":            "What is",
        "why_trending":       "Why is it Trending?",
        "global_reach":       "Global Reach",
        "related_news":       "Related News",
        "faq":                "Frequently Asked Questions",
        "about_section":      "About This Trend",
        "data_source":        "Data Sources",
        "wiki_attr":          "Source: Wikipedia (CC BY-SA 4.0)",
        "yt_attr":            "Data powered by YouTube Data API by Google",
        "disclaimer":         "Trend data is collected automatically and updated hourly.",
        "read_more":          "Read More",
        "related_posts":      "Related Posts",
        "volume_label":       "Search Volume",
        "temperature_label":  "Trend Temperature",
        "countries_label":    "Countries Trending",
        "category_label":     "Category",
        "faq_q1":             "How is trend temperature calculated?",
        "faq_a1":             "Trend temperature (0–100) is calculated based on search volume, velocity (rate of growth), and geographic spread across multiple countries.",
        "faq_q2":             "How often is the data updated?",
        "faq_a2":             "Trend data is collected and updated every hour via an automated pipeline using Google Trends RSS, YouTube Data API, GDELT, and Wikipedia.",
        "faq_q3":             "What does 'Global Trend' mean?",
        "faq_a3":             "A trend is marked as global when it appears simultaneously in 3 or more countries, indicating cross-border cultural or news significance.",
    },
    "kr": {
        "author":             "글로벌 트렌드 맵",
        "trending_now":       "지금 트렌딩",
        "top_global_trend":   "오늘의 글로벌 최고 트렌드",
        "country_trending":   "지금 트렌딩",
        "weekly_roundup":     "주간 트렌드 요약",
        "what_is":            "이란 무엇인가",
        "why_trending":       "왜 트렌딩인가?",
        "global_reach":       "글로벌 확산",
        "related_news":       "관련 뉴스",
        "faq":                "자주 묻는 질문",
        "about_section":      "이 트렌드에 대해",
        "data_source":        "데이터 출처",
        "wiki_attr":          "출처: Wikipedia (CC BY-SA 4.0)",
        "yt_attr":            "YouTube Data API by Google 제공",
        "disclaimer":         "트렌드 데이터는 자동으로 수집되며 매시간 업데이트됩니다.",
        "read_more":          "더 읽기",
        "related_posts":      "관련 게시물",
        "volume_label":       "검색량",
        "temperature_label":  "트렌드 온도",
        "countries_label":    "트렌딩 국가",
        "category_label":     "카테고리",
        "faq_q1":             "트렌드 온도는 어떻게 계산되나요?",
        "faq_a1":             "트렌드 온도(0–100)는 검색량, 속도(성장률), 여러 국가에 걸친 지리적 확산을 기반으로 계산됩니다.",
        "faq_q2":             "데이터는 얼마나 자주 업데이트되나요?",
        "faq_a2":             "트렌드 데이터는 Google Trends RSS, YouTube Data API, GDELT, Wikipedia를 사용하여 매시간 자동으로 수집 및 업데이트됩니다.",
        "faq_q3":             "'글로벌 트렌드'란 무엇인가요?",
        "faq_a3":             "3개국 이상에서 동시에 나타날 때 글로벌 트렌드로 표시되며, 이는 국경을 초월한 문화적 또는 뉴스의 중요성을 나타냅니다.",
    },
    "jp": {
        "author":             "グローバルトレンドマップ",
        "trending_now":       "今トレンド中",
        "top_global_trend":   "本日のグローバルトップトレンド",
        "country_trending":   "今トレンド中",
        "weekly_roundup":     "週間トレンドまとめ",
        "what_is":            "とは何か",
        "why_trending":       "なぜトレンドになっているのか？",
        "global_reach":       "グローバルな広がり",
        "related_news":       "関連ニュース",
        "faq":                "よくある質問",
        "about_section":      "このトレンドについて",
        "data_source":        "データソース",
        "wiki_attr":          "出典：Wikipedia (CC BY-SA 4.0)",
        "yt_attr":            "YouTube Data API by Google によるデータ提供",
        "disclaimer":         "トレンドデータは自動収集され、毎時更新されます。",
        "read_more":          "続きを読む",
        "related_posts":      "関連投稿",
        "volume_label":       "検索ボリューム",
        "temperature_label":  "トレンド温度",
        "countries_label":    "トレンド国数",
        "category_label":     "カテゴリ",
        "faq_q1":             "トレンド温度はどのように計算されますか？",
        "faq_a1":             "トレンド温度（0〜100）は、検索ボリューム、速度（成長率）、および複数の国にわたる地理的な広がりに基づいて計算されます。",
        "faq_q2":             "データはどのくらいの頻度で更新されますか？",
        "faq_a2":             "トレンドデータは、Google Trends RSS、YouTube Data API、GDELT、Wikipediaを使用して、毎時間自動的に収集・更新されます。",
        "faq_q3":             "「グローバルトレンド」とは何ですか？",
        "faq_a3":             "3か国以上で同時に現れるとグローバルトレンドとしてマークされ、国境を越えた文化的またはニュースの重要性を示しています。",
    },
    "zh": {
        "author":             "全球趋势地图",
        "trending_now":       "正在趋势",
        "top_global_trend":   "今日全球热门趋势",
        "country_trending":   "正在趋势",
        "weekly_roundup":     "每周趋势汇总",
        "what_is":            "是什么",
        "why_trending":       "为什么成为趋势？",
        "global_reach":       "全球影响",
        "related_news":       "相关新闻",
        "faq":                "常见问题",
        "about_section":      "关于此趋势",
        "data_source":        "数据来源",
        "wiki_attr":          "来源：Wikipedia (CC BY-SA 4.0)",
        "yt_attr":            "数据由 YouTube Data API by Google 提供",
        "disclaimer":         "趋势数据自动收集，每小时更新一次。",
        "read_more":          "阅读更多",
        "related_posts":      "相关文章",
        "volume_label":       "搜索量",
        "temperature_label":  "趋势温度",
        "countries_label":    "趋势国家",
        "category_label":     "类别",
        "faq_q1":             "趋势温度是如何计算的？",
        "faq_a1":             "趋势温度（0–100）根据搜索量、速度（增长率）以及跨多个国家的地理分布来计算。",
        "faq_q2":             "数据多久更新一次？",
        "faq_a2":             "趋势数据通过使用 Google Trends RSS、YouTube Data API、GDELT 和 Wikipedia 的自动化管道每小时收集和更新。",
        "faq_q3":             "「全球趋势」是什么意思？",
        "faq_a3":             "当一个趋势同时出现在3个或更多国家时，它被标记为全球趋势，表明其具有跨境的文化或新闻重要性。",
    },
    "es": {
        "author":             "Mapa Global de Tendencias",
        "trending_now":       "En tendencia ahora",
        "top_global_trend":   "Tendencia global del día",
        "country_trending":   "En tendencia ahora",
        "weekly_roundup":     "Resumen semanal de tendencias",
        "what_is":            "¿Qué es",
        "why_trending":       "¿Por qué está en tendencia?",
        "global_reach":       "Alcance global",
        "related_news":       "Noticias relacionadas",
        "faq":                "Preguntas frecuentes",
        "about_section":      "Sobre esta tendencia",
        "data_source":        "Fuentes de datos",
        "wiki_attr":          "Fuente: Wikipedia (CC BY-SA 4.0)",
        "yt_attr":            "Datos proporcionados por YouTube Data API de Google",
        "disclaimer":         "Los datos de tendencias se recopilan automáticamente y se actualizan cada hora.",
        "read_more":          "Leer más",
        "related_posts":      "Artículos relacionados",
        "volume_label":       "Volumen de búsqueda",
        "temperature_label":  "Temperatura de tendencia",
        "countries_label":    "Países en tendencia",
        "category_label":     "Categoría",
        "faq_q1":             "¿Cómo se calcula la temperatura de tendencia?",
        "faq_a1":             "La temperatura de tendencia (0–100) se calcula en base al volumen de búsqueda, la velocidad (tasa de crecimiento) y la distribución geográfica en múltiples países.",
        "faq_q2":             "¿Con qué frecuencia se actualizan los datos?",
        "faq_a2":             "Los datos de tendencias se recopilan y actualizan cada hora mediante un pipeline automatizado usando Google Trends RSS, YouTube Data API, GDELT y Wikipedia.",
        "faq_q3":             "¿Qué significa 'Tendencia Global'?",
        "faq_a3":             "Una tendencia se marca como global cuando aparece simultáneamente en 3 o más países, lo que indica relevancia cultural o informativa transfronteriza.",
    },
    "pt": {
        "author":             "Mapa Global de Tendências",
        "trending_now":       "Em alta agora",
        "top_global_trend":   "Principal tendência global do dia",
        "country_trending":   "Em alta agora",
        "weekly_roundup":     "Resumo semanal de tendências",
        "what_is":            "O que é",
        "why_trending":       "Por que está em alta?",
        "global_reach":       "Alcance global",
        "related_news":       "Notícias relacionadas",
        "faq":                "Perguntas frequentes",
        "about_section":      "Sobre esta tendência",
        "data_source":        "Fontes de dados",
        "wiki_attr":          "Fonte: Wikipedia (CC BY-SA 4.0)",
        "yt_attr":            "Dados fornecidos pela YouTube Data API do Google",
        "disclaimer":         "Os dados de tendências são coletados automaticamente e atualizados a cada hora.",
        "read_more":          "Leia mais",
        "related_posts":      "Artigos relacionados",
        "volume_label":       "Volume de pesquisa",
        "temperature_label":  "Temperatura de tendência",
        "countries_label":    "Países em alta",
        "category_label":     "Categoria",
        "faq_q1":             "Como a temperatura de tendência é calculada?",
        "faq_a1":             "A temperatura de tendência (0–100) é calculada com base no volume de pesquisa, velocidade (taxa de crescimento) e distribuição geográfica em vários países.",
        "faq_q2":             "Com que frequência os dados são atualizados?",
        "faq_a2":             "Os dados de tendências são coletados e atualizados a cada hora por meio de um pipeline automatizado usando Google Trends RSS, YouTube Data API, GDELT e Wikipedia.",
        "faq_q3":             "O que significa 'Tendência Global'?",
        "faq_a3":             "Uma tendência é marcada como global quando aparece simultaneamente em 3 ou mais países, indicando relevância cultural ou jornalística transfronteiriça.",
    },
    "fr": {
        "author":             "Carte Mondiale des Tendances",
        "trending_now":       "En tendance maintenant",
        "top_global_trend":   "Tendance mondiale du jour",
        "country_trending":   "En tendance maintenant",
        "weekly_roundup":     "Récapitulatif hebdomadaire des tendances",
        "what_is":            "Qu'est-ce que",
        "why_trending":       "Pourquoi est-ce en tendance ?",
        "global_reach":       "Portée mondiale",
        "related_news":       "Actualités associées",
        "faq":                "Questions fréquentes",
        "about_section":      "À propos de cette tendance",
        "data_source":        "Sources de données",
        "wiki_attr":          "Source : Wikipedia (CC BY-SA 4.0)",
        "yt_attr":            "Données fournies par YouTube Data API de Google",
        "disclaimer":         "Les données de tendances sont collectées automatiquement et mises à jour toutes les heures.",
        "read_more":          "Lire la suite",
        "related_posts":      "Articles associés",
        "volume_label":       "Volume de recherche",
        "temperature_label":  "Température de tendance",
        "countries_label":    "Pays en tendance",
        "category_label":     "Catégorie",
        "faq_q1":             "Comment la température de tendance est-elle calculée ?",
        "faq_a1":             "La température de tendance (0–100) est calculée en fonction du volume de recherche, de la vitesse (taux de croissance) et de la répartition géographique dans plusieurs pays.",
        "faq_q2":             "À quelle fréquence les données sont-elles mises à jour ?",
        "faq_a2":             "Les données de tendances sont collectées et mises à jour toutes les heures via un pipeline automatisé utilisant Google Trends RSS, YouTube Data API, GDELT et Wikipedia.",
        "faq_q3":             "Que signifie « Tendance Mondiale » ?",
        "faq_a3":             "Une tendance est marquée comme mondiale lorsqu'elle apparaît simultanément dans 3 pays ou plus, indiquant une importance culturelle ou journalistique transfrontalière.",
    },
    "de": {
        "author":             "Globale Trend-Karte",
        "trending_now":       "Jetzt im Trend",
        "top_global_trend":   "Globaler Top-Trend des Tages",
        "country_trending":   "Jetzt im Trend",
        "weekly_roundup":     "Wöchentliche Trend-Zusammenfassung",
        "what_is":            "Was ist",
        "why_trending":       "Warum liegt es im Trend?",
        "global_reach":       "Globale Reichweite",
        "related_news":       "Verwandte Nachrichten",
        "faq":                "Häufig gestellte Fragen",
        "about_section":      "Über diesen Trend",
        "data_source":        "Datenquellen",
        "wiki_attr":          "Quelle: Wikipedia (CC BY-SA 4.0)",
        "yt_attr":            "Daten bereitgestellt von YouTube Data API von Google",
        "disclaimer":         "Trenddaten werden automatisch gesammelt und stündlich aktualisiert.",
        "read_more":          "Mehr lesen",
        "related_posts":      "Verwandte Beiträge",
        "volume_label":       "Suchvolumen",
        "temperature_label":  "Trend-Temperatur",
        "countries_label":    "Länder im Trend",
        "category_label":     "Kategorie",
        "faq_q1":             "Wie wird die Trend-Temperatur berechnet?",
        "faq_a1":             "Die Trend-Temperatur (0–100) wird auf Basis von Suchvolumen, Geschwindigkeit (Wachstumsrate) und geografischer Verteilung über mehrere Länder berechnet.",
        "faq_q2":             "Wie oft werden die Daten aktualisiert?",
        "faq_a2":             "Trenddaten werden stündlich über eine automatisierte Pipeline mit Google Trends RSS, YouTube Data API, GDELT und Wikipedia gesammelt und aktualisiert.",
        "faq_q3":             "Was bedeutet 'Globaler Trend'?",
        "faq_a3":             "Ein Trend wird als global markiert, wenn er gleichzeitig in 3 oder mehr Ländern erscheint, was auf länderübergreifende kulturelle oder nachrichtliche Bedeutung hinweist.",
    },
}

COUNTRY_NAMES = {
    "en": {
        "US": "United States", "KR": "South Korea", "JP": "Japan",
        "GB": "United Kingdom", "DE": "Germany", "IN": "India",
        "BR": "Brazil", "FR": "France",
    },
    "kr": {
        "US": "미국", "KR": "대한민국", "JP": "일본",
        "GB": "영국", "DE": "독일", "IN": "인도",
        "BR": "브라질", "FR": "프랑스",
    },
    "jp": {
        "US": "アメリカ合衆国", "KR": "韓国", "JP": "日本",
        "GB": "イギリス", "DE": "ドイツ", "IN": "インド",
        "BR": "ブラジル", "FR": "フランス",
    },
    "zh": {
        "US": "美国", "KR": "韩国", "JP": "日本",
        "GB": "英国", "DE": "德国", "IN": "印度",
        "BR": "巴西", "FR": "法国",
    },
    "es": {
        "US": "Estados Unidos", "KR": "Corea del Sur", "JP": "Japón",
        "GB": "Reino Unido", "DE": "Alemania", "IN": "India",
        "BR": "Brasil", "FR": "Francia",
    },
    "pt": {
        "US": "Estados Unidos", "KR": "Coreia do Sul", "JP": "Japão",
        "GB": "Reino Unido", "DE": "Alemanha", "IN": "Índia",
        "BR": "Brasil", "FR": "França",
    },
    "fr": {
        "US": "États-Unis", "KR": "Corée du Sud", "JP": "Japon",
        "GB": "Royaume-Uni", "DE": "Allemagne", "IN": "Inde",
        "BR": "Brésil", "FR": "France",
    },
    "de": {
        "US": "Vereinigte Staaten", "KR": "Südkorea", "JP": "Japan",
        "GB": "Vereinigtes Königreich", "DE": "Deutschland", "IN": "Indien",
        "BR": "Brasilien", "FR": "Frankreich",
    },
}

ALL_LANGS = ["en", "zh", "es", "pt", "fr", "de", "kr", "jp"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return s.strip("-")[:80]


def is_blocked(keyword: str) -> bool:
    kw = keyword.lower()
    return any(bad in kw for bad in BLOCKED_KEYWORDS)


def today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_sunday() -> bool:
    return datetime.now(timezone.utc).weekday() == 6


def load_trends() -> dict:
    if not TRENDS_FILE.exists():
        raise FileNotFoundError(f"trends.json not found at {TRENDS_FILE}")
    with open(TRENDS_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_index() -> dict:
    if INDEX_FILE.exists():
        with open(INDEX_FILE, encoding="utf-8") as f:
            data = json.load(f)
        # Handle legacy flat-list format
        if isinstance(data, list):
            return {"posts": data, "lastUpdated": now_iso()}
        return data
    return {"posts": [], "lastUpdated": now_iso()}


def save_index(index: dict):
    index["lastUpdated"] = now_iso()
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def existing_slugs(index: dict) -> set:
    return {p["slug"] for p in index.get("posts", [])}


def fetch_wiki_description(keyword: str) -> tuple[str, str]:
    """Returns (extract, wiki_url)."""
    enc  = quote(keyword)
    url  = f"https://en.wikipedia.org/api/rest_v1/page/summary/{enc}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("extract", "")[:500], data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{enc}")
    except Exception:
        return "", f"https://en.wikipedia.org/wiki/{enc}"


def fetch_gdelt_headlines(keyword: str) -> list[dict]:
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query":      keyword,
        "mode":       "ArtList",
        "maxrecords": 5,
        "format":     "json",
    }
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return [
            {"title": a.get("title", ""), "url": a.get("url", ""), "source": a.get("domain", "")}
            for a in data.get("articles", [])[:5]
            if a.get("title")
        ]
    except Exception:
        return []


def count_posts_by_lang(index: dict) -> dict:
    counts = {lang: 0 for lang in ALL_LANGS}
    for p in index.get("posts", []):
        lang = p.get("language", "en")
        counts[lang] = counts.get(lang, 0) + 1
    return counts


def count_posts_today(index: dict) -> int:
    today = today_str()
    return sum(1 for p in index.get("posts", []) if p.get("date", "").startswith(today))

# ---------------------------------------------------------------------------
# Keyword display helper
# ---------------------------------------------------------------------------

def get_display_keyword(keyword: str, keyword_en: str, lang: str) -> str:
    """Return the most appropriate keyword string for the given language.

    - EN posts: always use English translation (keywordEn)
    - KR posts: keep original if it contains Hangul, else use keywordEn
    - JP posts: keep original if it contains Hiragana/Katakana, else use keywordEn
    - Other languages: always use keywordEn
    """
    kw_en = keyword_en or keyword
    if lang == "en":
        return kw_en
    if lang == "kr":
        # Contains Hangul?
        if any('\uAC00' <= c <= '\uD7A3' or '\u1100' <= c <= '\u11FF' for c in keyword):
            return keyword
        return kw_en
    if lang == "jp":
        # Contains Hiragana or Katakana?
        if any('\u3040' <= c <= '\u30FF' for c in keyword):
            return keyword
        return kw_en
    # All other languages (zh, es, pt, fr, de, ...): use English
    return kw_en


# ---------------------------------------------------------------------------
# MDX generators
# ---------------------------------------------------------------------------

def build_top_global_post(trends_data: dict, lang: str) -> tuple[str, dict]:
    """Build post type (a): Today's Top Global Trend."""
    t_str = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    global_sec = trends_data.get("global", {})
    top = global_sec.get("topTrend", {})
    keyword = top.get("keyword", "")
    keyword_slug = top.get("keywordEn", keyword) or keyword
    country_code = top.get("country", "US")
    countries_data = trends_data.get("countries", {})
    country_meta = countries_data.get(country_code, {})

    if not keyword or is_blocked(keyword):
        return "", {}

    # Find trend details
    trend_detail = next(
        (t for t in country_meta.get("trends", []) if t["keyword"].lower() == keyword.lower()),
        {}
    )

    wiki_desc, wiki_url = fetch_wiki_description(keyword)
    gdelt_news = fetch_gdelt_headlines(keyword)
    time.sleep(0.5)

    date   = today_str()
    flag   = top.get("flag", "🌐")
    volume = top.get("volume", "N/A")
    temp   = global_sec.get("temperature", 0)
    temp_label = global_sec.get("temperatureLabel", "HOT")
    total_countries = global_sec.get("totalCountries", 0)
    category = trend_detail.get("category", "news")
    velocity = trend_detail.get("velocity", "+1000%")
    is_global = trend_detail.get("isGlobal", False)

    kw_display = get_display_keyword(keyword, top.get("keywordEn", keyword), lang)

    t_str = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    title_map = {
        "en": f"Today's Top Global Trend: {kw_display}",
        "zh": f"今日全球热门趋势：{kw_display}",
        "es": f"Tendencia global del día: {kw_display}",
        "pt": f"Principal tendência global do dia: {kw_display}",
        "fr": f"Tendance mondiale du jour : {kw_display}",
        "de": f"Globaler Top-Trend des Tages: {kw_display}",
        "kr": f"오늘의 글로벌 최고 트렌드: {kw_display}",
        "jp": f"本日のグローバルトップトレンド: {kw_display}",
    }
    title = title_map.get(lang, title_map["en"])

    excerpt_map = {
        "en": f"{kw_display} is trending globally with {volume} searches. Discover why this topic is dominating today's conversation.",
        "zh": f"{kw_display} 正以 {volume} 次搜索在全球趋势。了解为何这个话题主导今天的讨论。",
        "es": f"{kw_display} está en tendencia global con {volume} búsquedas. Descubre por qué este tema domina la conversación de hoy.",
        "pt": f"{kw_display} está em alta globalmente com {volume} pesquisas. Descubra por que este tema domina a conversa de hoje.",
        "fr": f"{kw_display} est en tendance mondiale avec {volume} recherches. Découvrez pourquoi ce sujet domine la conversation d'aujourd'hui.",
        "de": f"{kw_display} ist mit {volume} Suchanfragen weltweit im Trend. Erfahren Sie, warum dieses Thema das Gespräch des Tages dominiert.",
        "kr": f"{kw_display}이(가) {volume} 검색으로 전 세계에서 트렌딩 중입니다. 오늘의 화제를 파악해보세요.",
        "jp": f"{kw_display}は{volume}件の検索でグローバルにトレンドしています。今日の話題を探りましょう。",
    }
    excerpt = excerpt_map.get(lang, excerpt_map["en"])

    slug = f"{date}-top-global-trend-{safe_slug(keyword_slug)}-{lang}"
    lang_slug = f"{safe_slug(keyword_slug)}-top-global"

    # Related news bullets
    news_section = ""
    if gdelt_news:
        bullets = "\n".join(f"- [{n['title']}]({n['url']}) — *{n['source']}*" for n in gdelt_news[:5])
        news_section = f"\n## {t_str['related_news']}\n\n{bullets}\n"

    # Country breakdown
    country_breakdown = ""
    top_countries = []
    for cc, cdata in countries_data.items():
        for t in cdata.get("trends", [])[:5]:
            if t["keyword"].lower() == keyword.lower():
                top_countries.append(f"- {cdata['flag']} **{cdata['name']}**: {t['volume']}")
                break
    if top_countries:
        country_breakdown = f"\n## {t_str['global_reach']}\n\n" + "\n".join(top_countries[:10]) + "\n"

    # Attribution
    use_youtube = trends_data.get("sources", {}).get("youtube", False)
    attribs = [f"- {t_str['wiki_attr']} — [{wiki_url}]({wiki_url})"]
    if use_youtube:
        attribs.append(f"- {t_str['yt_attr']}")
    attribs_str = "\n".join(attribs)

    body = f"""# {title}

> {excerpt}

**{t_str['volume_label']}:** {volume} &nbsp;|&nbsp; **{t_str['temperature_label']}:** {temp}°T ({temp_label}) &nbsp;|&nbsp; **{t_str['category_label']}:** {category.title()}

---

## {t_str['what_is']} {keyword}?

{wiki_desc or f"{keyword} is currently one of the most-searched topics globally, reflecting widespread public interest."}

## {t_str['why_trending']}

**{keyword}** {flag} is trending across {total_countries} countries with a velocity of {velocity}. The trend temperature of **{temp}°T** places it in the **{temp_label}** category, signalling exceptional cross-border interest.

{f"This topic is classified as a **Global Trend**, appearing simultaneously in multiple countries." if is_global else ""}

{country_breakdown}
{news_section}

## {t_str['faq']}

**{t_str['faq_q1']}**
{t_str['faq_a1']}

**{t_str['faq_q2']}**
{t_str['faq_a2']}

**{t_str['faq_q3']}**
{t_str['faq_a3']}

---

## {t_str['data_source']}

{attribs_str}

*{t_str['disclaimer']}*
"""

    frontmatter = f"""---
title: "{title}"
date: "{date}"
slug: "{slug}"
excerpt: "{excerpt}"
author: "{t_str['author']}"
category: "{category}"
tags: ["{safe_slug(keyword)}", "global-trends", "{category}", "{lang}"]
language: "{lang}"
keyword: "{keyword}"
volume: "{volume}"
temperature: {temp}
temperatureLabel: "{temp_label}"
countryCode: "{country_code}"
flag: "{flag}"
isGlobal: {str(is_global).lower()}
wikiUrl: "{wiki_url}"
---

{body}
"""

    meta = {
        "slug":     slug,
        "title":    title,
        "date":     date,
        "excerpt":  excerpt,
        "category": category,
        "language": lang,
        "keyword":  keyword,
        "type":     "top_global",
        "flag":     flag,
    }
    return frontmatter, meta


def build_country_post(country_code: str, trends_data: dict, lang: str) -> tuple[str, dict]:
    """Build post type (b): per-country trending post."""
    t_str = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    countries_data = trends_data.get("countries", {})
    cdata = countries_data.get(country_code, {})
    if not cdata:
        return "", {}

    trends = cdata.get("trends", [])
    if not trends:
        return "", {}

    top_trend = trends[0]
    keyword   = top_trend.get("keyword", "")
    keyword_slug = top_trend.get("keywordEn", keyword) or keyword
    if not keyword or is_blocked(keyword):
        return "", {}

    flag  = cdata.get("flag", "")
    cname_map = COUNTRY_NAMES.get(lang, COUNTRY_NAMES["en"])
    cname = cname_map.get(country_code, cdata.get("name", country_code))
    cname_en = COUNTRY_NAMES["en"].get(country_code, cdata.get("name", country_code))

    wiki_desc, wiki_url = fetch_wiki_description(keyword)
    gdelt_news = fetch_gdelt_headlines(keyword)
    time.sleep(0.5)

    date     = today_str()
    volume   = top_trend.get("volume", "N/A")
    temp     = top_trend.get("temperature", 0)
    velocity = top_trend.get("velocity", "+1000%")
    category = top_trend.get("category", "news")
    related_news_in_trend = top_trend.get("relatedNews", [])

    kw_display = get_display_keyword(keyword, top_trend.get("keywordEn", keyword), lang)

    t_str = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    tn = t_str["trending_now"]
    title_map = {
        "en": f"{flag} {cname} Trending Now: {kw_display}",
        "zh": f"{flag} {cname} 热搜：{kw_display}",
        "es": f"{flag} {cname} En tendencia: {kw_display}",
        "pt": f"{flag} {cname} Em alta: {kw_display}",
        "fr": f"{flag} {cname} En tendance : {kw_display}",
        "de": f"{flag} {cname} Im Trend: {kw_display}",
        "kr": f"{flag} {cname} {tn}: {kw_display}",
        "jp": f"{flag} {cname} {tn}: {kw_display}",
    }
    title = title_map.get(lang, title_map["en"])

    excerpt_map = {
        "en": f"'{kw_display}' is the #1 trending search in {cname} right now with {volume} searches.",
        "zh": f"'{kw_display}' 目前是 {cname} 的第一热搜，共有 {volume} 次搜索。",
        "es": f"'{kw_display}' es la búsqueda #1 en tendencia en {cname} ahora mismo con {volume} búsquedas.",
        "pt": f"'{kw_display}' é a pesquisa #1 em alta em {cname} agora com {volume} pesquisas.",
        "fr": f"'{kw_display}' est la recherche tendance n°1 en {cname} en ce moment avec {volume} recherches.",
        "de": f"'{kw_display}' ist aktuell die meistgesuchte Suchanfrage in {cname} mit {volume} Suchen.",
        "kr": f"'{kw_display}'이(가) 현재 {cname}에서 {volume} 검색으로 1위 트렌딩 검색어입니다.",
        "jp": f"'{kw_display}'は現在{cname}で{volume}件の検索で第1位のトレンドです。",
    }
    excerpt = excerpt_map.get(lang, excerpt_map["en"])

    slug = f"{date}-{safe_slug(cname_en)}-trending-{safe_slug(keyword_slug)}-{lang}"

    # Top 5 trends list
    top5 = "\n".join(
        f"{i+1}. **{t['keyword']}** — {t['volume']} ({t['category'].title()})"
        for i, t in enumerate(trends[:5])
        if not is_blocked(t["keyword"])
    )

    # News bullets
    all_news = gdelt_news or [{"title": h, "url": "#", "source": "News"} for h in related_news_in_trend[:3]]
    news_bullets = "\n".join(
        f"- [{n['title']}]({n['url']}) — *{n.get('source', '')}*"
        for n in all_news[:5]
    )

    use_youtube = trends_data.get("sources", {}).get("youtube", False)
    attribs = [f"- {t_str['wiki_attr']} — [{wiki_url}]({wiki_url})"]
    if use_youtube:
        attribs.append(f"- {t_str['yt_attr']}")
    attribs_str = "\n".join(attribs)

    body = f"""# {title}

> {excerpt}

**{t_str['volume_label']}:** {volume} &nbsp;|&nbsp; **{t_str['temperature_label']}:** {temp}°T &nbsp;|&nbsp; **{t_str['category_label']}:** {category.title()} &nbsp;|&nbsp; Velocity: {velocity}

---

## {t_str['what_is']} {keyword}?

{wiki_desc or f"{keyword} is currently trending in {cname}, capturing widespread public attention."}

## {t_str['why_trending']}

**{keyword}** has surged to the top of search trends in {cname} with a growth rate of **{velocity}**. The trend temperature of **{temp}°T** reflects the intensity of current public interest.

## Top 5 {t_str['trending_now']} in {cname}

{top5}

## {t_str['related_news']}

{news_bullets if news_bullets else "_No related news available at this time._"}

## {t_str['faq']}

**{t_str['faq_q1']}**
{t_str['faq_a1']}

**{t_str['faq_q2']}**
{t_str['faq_a2']}

**{t_str['faq_q3']}**
{t_str['faq_a3']}

---

## {t_str['data_source']}

{attribs_str}

*{t_str['disclaimer']}*
"""

    frontmatter = f"""---
title: "{title}"
date: "{date}"
slug: "{slug}"
excerpt: "{excerpt}"
author: "{t_str['author']}"
category: "{category}"
tags: ["{safe_slug(keyword)}", "{safe_slug(cname)}", "trending", "{lang}"]
language: "{lang}"
keyword: "{keyword}"
volume: "{volume}"
temperature: {temp}
countryCode: "{country_code}"
countryName: "{cname}"
flag: "{flag}"
wikiUrl: "{wiki_url}"
---

{body}
"""

    meta = {
        "slug":        slug,
        "title":       title,
        "date":        date,
        "excerpt":     excerpt,
        "category":    category,
        "language":    lang,
        "keyword":     keyword,
        "countryCode": country_code,
        "flag":        flag,
        "type":        "country",
    }
    return frontmatter, meta


def build_weekly_roundup(trends_data: dict, lang: str) -> tuple[str, dict]:
    """Build post type (c): weekly trend roundup (Sundays only)."""
    t_str = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    global_sec = trends_data.get("global", {})
    countries_data = trends_data.get("countries", {})
    date = today_str()

    title_map = {
        "en": f"Weekly Trend Roundup — {date}",
        "kr": f"주간 트렌드 요약 — {date}",
        "jp": f"週間トレンドまとめ — {date}",
    }
    title = title_map[lang]
    slug  = f"{date}-weekly-roundup-{lang}"

    excerpt_map = {
        "en": f"This week's biggest trends across {global_sec.get('totalCountries', 36)} countries — a data-driven global overview.",
        "kr": f"이번 주 {global_sec.get('totalCountries', 36)}개국의 가장 큰 트렌드 — 데이터 기반 글로벌 개요.",
        "jp": f"今週の{global_sec.get('totalCountries', 36)}か国のトップトレンド — データドリブンなグローバル概要。",
    }
    excerpt = excerpt_map[lang]

    top_by_cat = global_sec.get("topByCategory", {})
    cat_rows = ""
    for cat, info in top_by_cat.items():
        cat_rows += (
            f"| {cat.title()} | {info.get('flag', '')} {info.get('keyword', '')} "
            f"| {info.get('country', '')} | {info.get('temperature', 0)}°T |\n"
        )

    # Top trends per major country
    country_sections = ""
    for cc in MAJOR_COUNTRIES:
        cdata = countries_data.get(cc, {})
        if not cdata:
            continue
        top = cdata.get("trends", [{}])[0]
        if not top.get("keyword") or is_blocked(top["keyword"]):
            continue
        cname_map = COUNTRY_NAMES.get(lang, COUNTRY_NAMES["en"])
        cname = cname_map.get(cc, cdata.get("name", cc))
        kw_disp = get_display_keyword(top['keyword'], top.get('keywordEn', top['keyword']), lang)
        country_sections += (
            f"### {cdata['flag']} {cname}\n"
            f"**#{1} {kw_disp}** — {top['volume']} ({top['category'].title()})\n\n"
        )

    body = f"""# {title}

> {excerpt}

**{t_str['volume_label']}:** {global_sec.get('totalTrends', 0):,} total trends &nbsp;|&nbsp; **{t_str['temperature_label']}:** {global_sec.get('temperature', 0)}°T ({global_sec.get('temperatureLabel', 'HOT')}) &nbsp;|&nbsp; **{t_str['countries_label']}:** {global_sec.get('totalCountries', 36)}

---

## Top Trends by Category

| Category | Keyword | Country | Temperature |
|----------|---------|---------|-------------|
{cat_rows}

## Country Highlights

{country_sections}

## {t_str['faq']}

**{t_str['faq_q1']}**
{t_str['faq_a1']}

**{t_str['faq_q2']}**
{t_str['faq_a2']}

**{t_str['faq_q3']}**
{t_str['faq_a3']}

---

*{t_str['disclaimer']}*
"""

    frontmatter = f"""---
title: "{title}"
date: "{date}"
slug: "{slug}"
excerpt: "{excerpt}"
author: "{t_str['author']}"
category: "roundup"
tags: ["weekly-roundup", "global-trends", "{lang}"]
language: "{lang}"
type: "weekly"
totalCountries: {global_sec.get('totalCountries', 36)}
totalTrends: {global_sec.get('totalTrends', 0)}
globalTemp: {global_sec.get('temperature', 0)}
---

{body}
"""

    meta = {
        "slug":     slug,
        "title":    title,
        "date":     date,
        "excerpt":  excerpt,
        "category": "roundup",
        "language": lang,
        "type":     "weekly",
    }
    return frontmatter, meta

# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    start = datetime.now(timezone.utc)
    log.info("=" * 60)
    log.info("Blog Generator — %s", start.isoformat())
    log.info("=" * 60)

    trends_data = load_trends()
    index       = load_index()
    slugs       = existing_slugs(index)
    new_posts   = 0
    skipped     = 0

    posts_to_write: list[tuple[str, dict]] = []

    # --- Post type (a): Top Global Trend ---
    for lang in ALL_LANGS:
        content, meta = build_top_global_post(trends_data, lang)
        if not content or not meta:
            log.warning("Skipped top global post for lang=%s (no content)", lang)
            continue
        if meta["slug"] in slugs:
            log.info("SKIP (exists): %s", meta["slug"])
            skipped += 1
        else:
            posts_to_write.append((content, meta))

    # --- Post type (b): Per-country posts ---
    for cc in MAJOR_COUNTRIES:
        for lang in ALL_LANGS:
            content, meta = build_country_post(cc, trends_data, lang)
            if not content or not meta:
                continue
            if meta["slug"] in slugs:
                log.info("SKIP (exists): %s", meta["slug"])
                skipped += 1
            else:
                posts_to_write.append((content, meta))

    # --- Post type (c): Weekly roundup (Sundays) ---
    if is_sunday():
        for lang in ALL_LANGS:
            content, meta = build_weekly_roundup(trends_data, lang)
            if not content or not meta:
                continue
            if meta["slug"] in slugs:
                log.info("SKIP (exists): %s", meta["slug"])
                skipped += 1
            else:
                posts_to_write.append((content, meta))

    # Write all posts
    for content, meta in posts_to_write:
        out_path = BLOG_DIR / f"{meta['slug']}.mdx"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        index["posts"].append(meta)
        slugs.add(meta["slug"])
        new_posts += 1
        log.info("WROTE: %s", out_path.name)

    save_index(index)

    # Pipeline stats
    end = datetime.now(timezone.utc)
    duration = int((end - start).total_seconds())
    lang_counts = count_posts_by_lang(index)
    today_count = count_posts_today(index)
    total_count = len(index["posts"])

    # Save pipeline stats into trends.json (if writable)
    try:
        with open(TRENDS_FILE, encoding="utf-8") as f:
            td = json.load(f)
        td["blogStats"] = {
            "postsToday":   today_count,
            "postsTotal":   total_count,
            **{f"posts_{l}": lang_counts.get(l, 0) for l in ALL_LANGS},
            "lastRun":      now_iso(),
            "duration":     duration,
            "newPostsThisRun": new_posts,
        }
        with open(TRENDS_FILE, "w", encoding="utf-8") as f:
            json.dump(td, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.warning("Could not save blog stats to trends.json: %s", e)

    log.info("=" * 60)
    log.info("DONE — %d new posts | %d skipped | %ds", new_posts, skipped, duration)
    log.info("Total: %d | EN:%d KR:%d JP:%d",
             total_count, lang_counts.get("en", 0),
             lang_counts.get("kr", 0), lang_counts.get("jp", 0))
    log.info("=" * 60)


if __name__ == "__main__":
    main()
