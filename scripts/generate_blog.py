#!/usr/bin/env python3
"""
generate_blog.py — Blog Post Generator (Data-Driven, No API Cost)

Strategy:
  • 1 topic/day = Spotlight #1 (global.topTrend.keywordEn)
  • Skip if same as yesterday's spotlight
  • Write EN post from trend data using parameterized templates
  • Translate EN → 7 languages (ZH, ES, PT, FR, DE, KR, JP) via pre-built templates
  • 8 posts total per day
"""

import json
import logging
import re
import textwrap
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

SITE_URL = "https://global-trend-map-web.vercel.app"

ALL_LANGS = ["en", "zh", "es", "pt", "fr", "de", "kr", "jp"]

# ─── Language metadata ────────────────────────────────────────────────────────

LANG_META = {
    "en": {"label": "English",    "hreflang": "en",    "locale": "en_US"},
    "zh": {"label": "中文",        "hreflang": "zh",    "locale": "zh_CN"},
    "es": {"label": "Español",    "hreflang": "es",    "locale": "es_ES"},
    "pt": {"label": "Português",  "hreflang": "pt",    "locale": "pt_BR"},
    "fr": {"label": "Français",   "hreflang": "fr",    "locale": "fr_FR"},
    "de": {"label": "Deutsch",    "hreflang": "de",    "locale": "de_DE"},
    "kr": {"label": "한국어",       "hreflang": "ko",    "locale": "ko_KR"},
    "jp": {"label": "日本語",       "hreflang": "ja",    "locale": "ja_JP"},
}

CATEGORY_LABELS = {
    "en": {"sports": "Sports", "tech": "Technology", "music": "Music",
           "news": "News", "movies": "Entertainment", "finance": "Finance", "": "Trending"},
    "zh": {"sports": "体育", "tech": "科技", "music": "音乐",
           "news": "新闻", "movies": "娱乐", "finance": "金融", "": "热搜"},
    "es": {"sports": "Deportes", "tech": "Tecnología", "music": "Música",
           "news": "Noticias", "movies": "Entretenimiento", "finance": "Finanzas", "": "Tendencias"},
    "pt": {"sports": "Esportes", "tech": "Tecnologia", "music": "Música",
           "news": "Notícias", "movies": "Entretenimento", "finance": "Finanças", "": "Tendências"},
    "fr": {"sports": "Sport", "tech": "Technologie", "music": "Musique",
           "news": "Actualités", "movies": "Divertissement", "finance": "Finance", "": "Tendances"},
    "de": {"sports": "Sport", "tech": "Technologie", "music": "Musik",
           "news": "Nachrichten", "movies": "Unterhaltung", "finance": "Finanzen", "": "Trends"},
    "kr": {"sports": "스포츠", "tech": "기술", "music": "음악",
           "news": "뉴스", "movies": "엔터테인먼트", "finance": "금융", "": "트렌드"},
    "jp": {"sports": "スポーツ", "tech": "テクノロジー", "music": "音楽",
           "news": "ニュース", "movies": "エンターテインメント", "finance": "ファイナンス", "": "トレンド"},
}

# ─── Multi-language templates ─────────────────────────────────────────────────
# Each entry: callable(ctx) → str, where ctx is a dict with trend data

def _mk_templates():
    """
    Returns dict: lang → dict of section builders.
    ctx keys:
      keyword, keyword_en, category, category_label,
      top_country, top_country_name, volume,
      temperature, total_countries,
      countries_list,          # list of (flag, name) tuples
      rising_list,             # list of (keyword_en, country_name, volume)
      cat_breakdown,           # dict category→count
      date_str, date_iso, slug_en, site_url
    """

    # ── English ──────────────────────────────────────────────────────────────
    def en_title(c):
        return f"Why Is \"{c['keyword_en']}\" Trending Globally? {c['date_str']} Analysis"

    def en_excerpt(c):
        return (
            f"\"{c['keyword_en']}\" is the #1 global search trend today, "
            f"leading in {c['top_country_name']} with {c['volume']} searches. "
            f"Discover what's driving this worldwide surge."
        )

    def en_body(c):
        countries_md = "\n".join(
            f"- {flag} **{name}**" for flag, name in c["countries_list"]
        )
        rising_md = "\n".join(
            f"- **{kw}** — {cn} ({vol})" for kw, cn, vol in c["rising_list"]
        ) or "- No velocity data available"
        cat_md = "\n".join(
            f"- **{k.capitalize()}**: {v} trends"
            for k, v in sorted(c["cat_breakdown"].items(), key=lambda x: -x[1])
            if v > 0
        )

        return textwrap.dedent(f"""\
## What Is "{c['keyword_en']}" and Why Is It Trending?

**"{c['keyword_en']}"** is the #1 trending search worldwide right now, \
spiking across {len(c['countries_list'])} countries simultaneously. \
The topic falls under the **{c['category_label']}** category and is generating \
significant search interest with **{c['volume']}** searches logged in {c['top_country_name']} alone.

Global search trends often reflect breaking events, viral moments, or major cultural \
milestones — and today, **"{c['keyword_en']}"** is at the center of that conversation.

---

## Where in the World Is "{c['keyword_en']}" Trending?

Our real-time data from {c['total_countries']} countries shows active search interest in:

{countries_md}

The strongest signal originates from **{c['top_country_name']}**, \
making it the primary driver of today's global surge.

---

## Trend Statistics at a Glance

| Metric | Value |
|---|---|
| Search Volume | {c['volume']} |
| Trend Temperature | {c['temperature']}°T |
| Category | {c['category_label']} |
| Countries Tracking | {len(c['countries_list'])} |
| Total Countries Monitored | {c['total_countries']} |

A **Trend Temperature** of **{c['temperature']}°T** on TrendPulse's 0–100 scale \
indicates {_temp_desc_en(c['temperature'])}.

---

## Other Rising Trends Right Now

While **"{c['keyword_en']}"** dominates globally, these topics are also climbing fast:

{rising_md}

---

## Today's Global Search Landscape

The current breakdown of trending topics by category:

{cat_md}

This snapshot reflects what millions of people across {c['total_countries']} countries \
are actively searching for at this moment.

---

## Stay Ahead of Global Trends

TrendPulse monitors search trends across {c['total_countries']} countries in real time. \
Whether you're a researcher, journalist, content creator, or simply curious about \
what the world is thinking — our live data gives you an instant pulse on global interest.

👉 [Explore the Live Global Trend Map]({c['site_url']})

*Data collected {c['date_str']}. Trends update hourly.*
""")

    def _temp_desc_en(t):
        if t >= 90: return "an exceptionally viral trend with massive global reach"
        if t >= 75: return "a very hot trend with strong international momentum"
        if t >= 60: return "a warm and growing trend gaining traction worldwide"
        if t >= 40: return "a rising trend picking up search interest globally"
        return "an emerging topic beginning to capture global attention"

    # ── Chinese (Simplified) ──────────────────────────────────────────────────
    def zh_title(c):
        kw = c['keyword_en']
        return f'\u201c{kw}\u201d\u4e3a\u4f55\u5728\u5168\u7403\u8d70\u7ea2\uff1f{c["date_str"]}\u8d8b\u52bf\u5206\u6790'

    def zh_excerpt(c):
        kw = c['keyword_en']
        cn = c['top_country_name']
        vol = c['volume']
        return (
            f'\u201c{kw}\u201d\u662f\u4eca\u65e5\u5168\u7403\u641c\u7d22\u699c\u7b2c\u4e00\uff0c'
            f'\u5728{cn}\u4ea7\u751f\u4e86{vol}\u6b21\u641c\u7d22\u3002'
            '\u63a2\u7d22\u8fd9\u4e00\u5168\u7403\u70ed\u6f6e\u80cc\u540e\u7684\u9a71\u52a8\u529b\u3002'
        )

    def zh_body(c):
        countries_md = "\n".join(
            f"- {flag} **{name}**" for flag, name in c["countries_list"]
        )
        rising_md = "\n".join(
            f"- **{kw}** — {cn}（{vol}）" for kw, cn, vol in c["rising_list"]
        ) or "- 暂无速度数据"

        return textwrap.dedent(f"""\
## "{c['keyword_en']}"是什么？为何走红全球？

**"{c['keyword_en']}"** 是目前全球搜索量排名第一的话题，\
同时在{len(c['countries_list'])}个国家引发搜索热潮。\
该话题属于**{c['category_label']}**类别，\
仅在{c['top_country_name']}就产生了**{c['volume']}**次搜索。

---

## "{c['keyword_en']}"在哪些国家最热搜？

我们实时监测了{c['total_countries']}个国家的数据，以下国家的搜索热度最高：

{countries_md}

**{c['top_country_name']}**是本次全球热搜的主要来源地。

---

## 趋势数据一览

| 指标 | 数值 |
|---|---|
| 搜索量 | {c['volume']} |
| 趋势温度 | {c['temperature']}°T |
| 类别 | {c['category_label']} |
| 覆盖国家数 | {len(c['countries_list'])} |
| 监测国家总数 | {c['total_countries']} |

---

## 当前其他上升中的趋势

{rising_md}

---

## 实时掌握全球趋势

TrendPulse 实时监测全球{c['total_countries']}个国家的搜索趋势。

👉 [查看实时全球趋势地图]({c['site_url']})

*数据采集于{c['date_str']}，每小时更新。*
""")

    # ── Spanish ───────────────────────────────────────────────────────────────
    def es_title(c):
        return f"¿Por qué \"{c['keyword_en']}\" es tendencia mundial? Análisis del {c['date_str']}"

    def es_excerpt(c):
        return (
            f"\"{c['keyword_en']}\" es la búsqueda #1 a nivel mundial hoy, "
            f"con {c['volume']} búsquedas en {c['top_country_name']}. "
            f"Descubre qué está impulsando este fenómeno global."
        )

    def es_body(c):
        countries_md = "\n".join(
            f"- {flag} **{name}**" for flag, name in c["countries_list"]
        )
        rising_md = "\n".join(
            f"- **{kw}** — {cn} ({vol})" for kw, cn, vol in c["rising_list"]
        ) or "- Sin datos de velocidad disponibles"

        return textwrap.dedent(f"""\
## ¿Qué es "{c['keyword_en']}" y por qué es tendencia?

**"{c['keyword_en']}"** es la búsqueda #1 en todo el mundo ahora mismo, \
con actividad en {len(c['countries_list'])} países simultáneamente. \
Pertenece a la categoría **{c['category_label']}** y registra \
**{c['volume']}** búsquedas solo en {c['top_country_name']}.

---

## ¿Dónde es tendencia "{c['keyword_en']}"?

Nuestros datos en tiempo real de {c['total_countries']} países muestran interés activo en:

{countries_md}

La señal más fuerte proviene de **{c['top_country_name']}**.

---

## Estadísticas de la tendencia

| Métrica | Valor |
|---|---|
| Volumen de búsqueda | {c['volume']} |
| Temperatura de tendencia | {c['temperature']}°T |
| Categoría | {c['category_label']} |
| Países | {len(c['countries_list'])} |

---

## Otras tendencias en ascenso ahora mismo

{rising_md}

---

## Mantente al día con las tendencias globales

👉 [Explorar el mapa de tendencias en vivo]({c['site_url']})

*Datos recopilados el {c['date_str']}. Actualizaciones cada hora.*
""")

    # ── Portuguese ────────────────────────────────────────────────────────────
    def pt_title(c):
        return f"Por que \"{c['keyword_en']}\" é tendência mundial? Análise de {c['date_str']}"

    def pt_excerpt(c):
        return (
            f"\"{c['keyword_en']}\" é a busca #1 no mundo hoje, "
            f"com {c['volume']} pesquisas em {c['top_country_name']}. "
            f"Saiba o que está impulsionando essa tendência global."
        )

    def pt_body(c):
        countries_md = "\n".join(
            f"- {flag} **{name}**" for flag, name in c["countries_list"]
        )
        rising_md = "\n".join(
            f"- **{kw}** — {cn} ({vol})" for kw, cn, vol in c["rising_list"]
        ) or "- Sem dados de velocidade disponíveis"

        return textwrap.dedent(f"""\
## O que é "{c['keyword_en']}" e por que está em alta?

**"{c['keyword_en']}"** é o termo mais buscado no mundo agora, \
com atividade em {len(c['countries_list'])} países. \
Pertence à categoria **{c['category_label']}** e registra \
**{c['volume']}** buscas apenas em {c['top_country_name']}.

---

## Onde "{c['keyword_en']}" é tendência?

Nossos dados em tempo real de {c['total_countries']} países mostram interesse ativo em:

{countries_md}

O sinal mais forte vem de **{c['top_country_name']}**.

---

## Estatísticas da tendência

| Métrica | Valor |
|---|---|
| Volume de busca | {c['volume']} |
| Temperatura | {c['temperature']}°T |
| Categoria | {c['category_label']} |
| Países | {len(c['countries_list'])} |

---

## Outras tendências em alta agora

{rising_md}

---

## Fique por dentro das tendências globais

👉 [Explorar o mapa de tendências ao vivo]({c['site_url']})

*Dados coletados em {c['date_str']}. Atualizações a cada hora.*
""")

    # ── French ────────────────────────────────────────────────────────────────
    def fr_title(c):
        return f"Pourquoi \"{c['keyword_en']}\" est-il en tendance mondiale ? Analyse du {c['date_str']}"

    def fr_excerpt(c):
        return (
            f"\"{c['keyword_en']}\" est la recherche #1 dans le monde aujourd'hui, "
            f"avec {c['volume']} recherches en {c['top_country_name']}. "
            f"Découvrez ce qui alimente ce phénomène mondial."
        )

    def fr_body(c):
        countries_md = "\n".join(
            f"- {flag} **{name}**" for flag, name in c["countries_list"]
        )
        rising_md = "\n".join(
            f"- **{kw}** — {cn} ({vol})" for kw, cn, vol in c["rising_list"]
        ) or "- Aucune donnée de vitesse disponible"

        return textwrap.dedent(f"""\
## Qu'est-ce que "{c['keyword_en']}" et pourquoi est-il en tendance ?

**"{c['keyword_en']}"** est la recherche #1 dans le monde en ce moment, \
avec une activité dans {len(c['countries_list'])} pays simultanément. \
Il appartient à la catégorie **{c['category_label']}** et génère \
**{c['volume']}** recherches rien qu'en {c['top_country_name']}.

---

## Où "{c['keyword_en']}" est-il en tendance ?

Nos données en temps réel de {c['total_countries']} pays montrent un intérêt actif dans :

{countries_md}

Le signal le plus fort provient de **{c['top_country_name']}**.

---

## Statistiques de la tendance

| Métrique | Valeur |
|---|---|
| Volume de recherche | {c['volume']} |
| Température | {c['temperature']}°T |
| Catégorie | {c['category_label']} |
| Pays | {len(c['countries_list'])} |

---

## Autres tendances en hausse en ce moment

{rising_md}

---

## Restez à l'affût des tendances mondiales

👉 [Explorer la carte des tendances en direct]({c['site_url']})

*Données collectées le {c['date_str']}. Mises à jour toutes les heures.*
""")

    # ── German ────────────────────────────────────────────────────────────────
    def de_title(c):
        return f"Warum liegt \"{c['keyword_en']}\" weltweit im Trend? Analyse vom {c['date_str']}"

    def de_excerpt(c):
        return (
            f"\"{c['keyword_en']}\" ist heute die weltweit meistgesuchte Suchanfrage, "
            f"mit {c['volume']} Suchen in {c['top_country_name']}. "
            f"Entdecken Sie, was diesen globalen Trend antreibt."
        )

    def de_body(c):
        countries_md = "\n".join(
            f"- {flag} **{name}**" for flag, name in c["countries_list"]
        )
        rising_md = "\n".join(
            f"- **{kw}** — {cn} ({vol})" for kw, cn, vol in c["rising_list"]
        ) or "- Keine Geschwindigkeitsdaten verfügbar"

        return textwrap.dedent(f"""\
## Was ist "{c['keyword_en']}" und warum liegt es im Trend?

**"{c['keyword_en']}"** ist momentan die meistgesuchte Suchanfrage weltweit, \
mit Aktivität in {len(c['countries_list'])} Ländern gleichzeitig. \
Es gehört zur Kategorie **{c['category_label']}** und generiert \
**{c['volume']}** Suchanfragen allein in {c['top_country_name']}.

---

## Wo liegt "{c['keyword_en']}" im Trend?

Unsere Echtzeit-Daten aus {c['total_countries']} Ländern zeigen aktives Interesse in:

{countries_md}

Das stärkste Signal kommt aus **{c['top_country_name']}**.

---

## Trend-Statistiken im Überblick

| Kennzahl | Wert |
|---|---|
| Suchvolumen | {c['volume']} |
| Trend-Temperatur | {c['temperature']}°T |
| Kategorie | {c['category_label']} |
| Länder | {len(c['countries_list'])} |

---

## Weitere aufsteigende Trends gerade jetzt

{rising_md}

---

## Globale Trends immer im Blick

👉 [Live-Trendkarte erkunden]({c['site_url']})

*Daten erhoben am {c['date_str']}. Stündliche Aktualisierungen.*
""")

    # ── Korean ────────────────────────────────────────────────────────────────
    def kr_title(c):
        return f"\"{c['keyword_en']}\"가 전 세계 트렌드 1위인 이유? {c['date_str']} 분석"

    def kr_excerpt(c):
        return (
            f"\"{c['keyword_en']}\"이 오늘 전 세계 검색어 1위를 기록했습니다. "
            f"{c['top_country_name']}에서만 {c['volume']}건의 검색이 발생했습니다. "
            f"이 글로벌 트렌드의 배경을 알아보세요."
        )

    def kr_body(c):
        countries_md = "\n".join(
            f"- {flag} **{name}**" for flag, name in c["countries_list"]
        )
        rising_md = "\n".join(
            f"- **{kw}** — {cn} ({vol})" for kw, cn, vol in c["rising_list"]
        ) or "- 속도 데이터 없음"

        return textwrap.dedent(f"""\
## "{c['keyword_en']}"란 무엇이고, 왜 트렌드가 되었나요?

**"{c['keyword_en']}"**은 현재 전 세계 검색어 1위로, \
{len(c['countries_list'])}개국에서 동시에 검색이 급증하고 있습니다. \
이 키워드는 **{c['category_label']}** 카테고리에 속하며, \
{c['top_country_name']}에서만 **{c['volume']}**건의 검색이 발생했습니다.

---

## "{c['keyword_en']}"은 어느 나라에서 트렌드인가요?

{c['total_countries']}개국 실시간 데이터에 따르면 다음 국가에서 높은 관심도를 보입니다:

{countries_md}

가장 강한 신호는 **{c['top_country_name']}**에서 발생하고 있습니다.

---

## 트렌드 통계 요약

| 지표 | 값 |
|---|---|
| 검색량 | {c['volume']} |
| 트렌드 온도 | {c['temperature']}°T |
| 카테고리 | {c['category_label']} |
| 추적 국가 수 | {len(c['countries_list'])} |

---

## 지금 빠르게 올라오는 다른 트렌드

{rising_md}

---

## 실시간 글로벌 트렌드를 파악하세요

👉 [실시간 글로벌 트렌드 맵 보기]({c['site_url']})

*데이터 수집일: {c['date_str']}. 매시간 업데이트.*
""")

    # ── Japanese ──────────────────────────────────────────────────────────────
    def jp_title(c):
        return f"「{c['keyword_en']}」が世界でトレンド入りした理由は？{c['date_str']}分析"

    def jp_excerpt(c):
        return (
            f"「{c['keyword_en']}」が本日の世界検索ランキング1位を記録。"
            f"{c['top_country_name']}だけで{c['volume']}件の検索が発生しました。"
            f"このグローバルトレンドの背景を解説します。"
        )

    def jp_body(c):
        countries_md = "\n".join(
            f"- {flag} **{name}**" for flag, name in c["countries_list"]
        )
        rising_md = "\n".join(
            f"- **{kw}** — {cn}（{vol}）" for kw, cn, vol in c["rising_list"]
        ) or "- 速度データなし"

        return textwrap.dedent(f"""\
## 「{c['keyword_en']}」とは何か？なぜトレンド入りしたのか？

**「{c['keyword_en']}」**は現在、世界中で検索数ランキング1位となっており、\
{len(c['countries_list'])}か国で同時に検索が急増しています。\
このキーワードは**{c['category_label']}**カテゴリに属し、\
{c['top_country_name']}だけで**{c['volume']}**件の検索が記録されています。

---

## 「{c['keyword_en']}」はどの国でトレンドになっているのか？

{c['total_countries']}か国のリアルタイムデータでは、以下の国で高い関心が見られます：

{countries_md}

最も強いシグナルは**{c['top_country_name']}**から発信されています。

---

## トレンド統計の概要

| 指標 | 値 |
|---|---|
| 検索ボリューム | {c['volume']} |
| トレンド温度 | {c['temperature']}°T |
| カテゴリ | {c['category_label']} |
| 追跡国数 | {len(c['countries_list'])} |

---

## 今まさに急上昇中の他のトレンド

{rising_md}

---

## グローバルトレンドをリアルタイムで把握

👉 [ライブグローバルトレンドマップを見る]({c['site_url']})

*データ収集日：{c['date_str']}。毎時更新。*
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


# ─── Utility functions ────────────────────────────────────────────────────────

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
            return {"posts": data, "lastUpdated": now_iso(), "lastSpotlight": ""}
        data.setdefault("lastSpotlight", "")
        return data
    return {"posts": [], "lastUpdated": now_iso(), "lastSpotlight": ""}


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
    words = len(body.split())
    return max(1, round(words / 200))


def format_date_str(dt: datetime) -> str:
    return dt.strftime("%B %d, %Y")


# ─── Context builder ──────────────────────────────────────────────────────────

def build_context(trends_data: dict, lang: str) -> dict:
    """Build the template context dict from trends.json data."""
    g = trends_data["global"]
    countries_data = trends_data["countries"]
    top = g["topTrend"]
    keyword_en = top.get("keywordEn") or top["keyword"]
    category = top.get("category", "")
    category_label = CATEGORY_LABELS.get(lang, CATEGORY_LABELS["en"]).get(category, category or "Trending")

    # Find all countries where this keyword appears
    kw_lower = keyword_en.lower()
    countries_with_trend = []
    for code, cdata in countries_data.items():
        for t in cdata["trends"]:
            t_kw = (t.get("keywordEn") or t["keyword"]).lower()
            if t_kw == kw_lower:
                countries_with_trend.append((cdata.get("flag", "🌐"), cdata["name"]))
                break

    # Fallback: use top_country
    if not countries_with_trend:
        top_cc = top.get("country", "")
        if top_cc and top_cc in countries_data:
            countries_with_trend = [(countries_data[top_cc].get("flag", "🌐"), countries_data[top_cc]["name"])]
        else:
            countries_with_trend = [(top.get("flag", "🌐"), top_cc or "Global")]

    top_country_name = countries_with_trend[0][1] if countries_with_trend else top.get("country", "")

    # Rising fast
    rising_list = []
    for r in g.get("risingFast", []):
        rk = (r.get("keywordEn") or r["keyword"])
        if rk.lower() == kw_lower:
            continue  # skip if same as spotlight
        cn_code = r.get("country", "")
        cn_name = countries_data.get(cn_code, {}).get("name", cn_code) if cn_code else ""
        rising_list.append((rk, cn_name, r.get("change", r.get("volume", ""))))

    now = datetime.now(timezone.utc)
    return {
        "keyword": top["keyword"],
        "keyword_en": keyword_en,
        "category": category,
        "category_label": category_label,
        "top_country": top.get("country", ""),
        "top_country_name": top_country_name,
        "volume": top.get("volume", "N/A"),
        "temperature": g.get("temperature", 0),
        "total_countries": g.get("totalCountries", len(countries_data)),
        "countries_list": countries_with_trend[:12],
        "rising_list": rising_list[:5],
        "cat_breakdown": g.get("categoryBreakdown", {}),
        "date_str": format_date_str(now),
        "date_iso": now.strftime("%Y-%m-%d"),
        "slug_en": slugify(keyword_en),
        "site_url": SITE_URL,
    }


# ─── MDX builder ──────────────────────────────────────────────────────────────

def build_mdx(lang: str, ctx: dict) -> tuple[str, str]:
    """
    Returns (slug, mdx_content).
    slug format: {date}-spotlight-{slug_en}-{lang}
    """
    tmpl = TEMPLATES[lang]
    title = tmpl["title"](ctx)
    excerpt = tmpl["excerpt"](ctx)
    body = tmpl["body"](ctx)
    hreflang = LANG_META[lang]["hreflang"]
    locale = LANG_META[lang]["locale"]

    slug = f"{ctx['date_iso']}-spotlight-{ctx['slug_en']}-{lang}"
    rt = reading_time(body)

    # Build alternate links
    alts = []
    for l in ALL_LANGS:
        alt_slug = f"{ctx['date_iso']}-spotlight-{ctx['slug_en']}-{l}"
        alts.append(f'  {LANG_META[l]["hreflang"]}: /blog/{alt_slug}')
    alts_yaml = "\n".join(alts)

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


# ─── Main logic ───────────────────────────────────────────────────────────────

def main():
    log.info("=== Blog Post Generator Starting ===")
    trends_data = load_trends()
    index = load_index()

    g = trends_data["global"]
    top = g["topTrend"]
    spotlight = (top.get("keywordEn") or top["keyword"]).strip().lower()

    last_spotlight = index.get("lastSpotlight", "").strip().lower()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    log.info(f"Today's spotlight: '{spotlight}'")
    log.info(f"Last spotlight: '{last_spotlight}'")

    if spotlight == last_spotlight:
        log.info("Spotlight unchanged — skipping blog generation.")
        return

    log.info(f"New spotlight detected — generating {len(ALL_LANGS)} posts...")

    # Build EN context (canonical source of data)
    en_ctx = build_context(trends_data, "en")
    log.info(f"  Spotlight keyword: {en_ctx['keyword_en']}")
    log.info(f"  Category: {en_ctx['category_label']}")
    log.info(f"  Top country: {en_ctx['top_country_name']}")
    log.info(f"  Countries with trend: {len(en_ctx['countries_list'])}")

    new_posts = []
    for lang in ALL_LANGS:
        ctx = build_context(trends_data, lang)
        slug, mdx_content = build_mdx(lang, ctx)
        out_path = BLOG_DIR / f"{slug}.mdx"
        out_path.write_text(mdx_content, encoding="utf-8")
        log.info(f"  ✅ Written: {out_path.name}")

        new_posts.append({
            "slug": slug,
            "title": TEMPLATES[lang]["title"](ctx),
            "date": today,
            "lastUpdated": now_iso(),
            "excerpt": TEMPLATES[lang]["excerpt"](ctx),
            "category": ctx["category"] or "news",
            "language": lang,
            "readingTime": reading_time(TEMPLATES[lang]["body"](ctx)),
            "featured": True,
            "tags": [ctx["slug_en"], ctx["category"] or "news", "global-trends", "trending"],
        })

    # Prepend new posts to index (newest first)
    existing = index.get("posts", [])
    index["posts"] = new_posts + existing
    index["lastSpotlight"] = spotlight
    save_index(index)

    log.info(f"=== Done. {len(new_posts)} posts written. Index updated. ===")


if __name__ == "__main__":
    main()
