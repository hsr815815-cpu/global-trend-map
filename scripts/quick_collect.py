#!/usr/bin/env python3
"""Quick trend collector - Google Trends RSS only, no Wikipedia enrichment."""
import sys, json, time, re, shutil, logging
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote as url_quote
import requests, feedparser

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'public' / 'data'
OUTPUT_FILE = DATA_DIR / 'trends.json'
ARCHIVE_DIR = DATA_DIR / 'archive'

COUNTRIES = {
    'US': {'name': 'United States',  'flag': '🇺🇸'},
    'KR': {'name': 'South Korea',    'flag': '🇰🇷'},
    'JP': {'name': 'Japan',          'flag': '🇯🇵'},
    'GB': {'name': 'United Kingdom', 'flag': '🇬🇧'},
    'DE': {'name': 'Germany',        'flag': '🇩🇪'},
    'IN': {'name': 'India',          'flag': '🇮🇳'},
    'BR': {'name': 'Brazil',         'flag': '🇧🇷'},
    'FR': {'name': 'France',         'flag': '🇫🇷'},
    'AU': {'name': 'Australia',      'flag': '🇦🇺'},
    'MX': {'name': 'Mexico',         'flag': '🇲🇽'},
    'CA': {'name': 'Canada',         'flag': '🇨🇦'},
    'IT': {'name': 'Italy',          'flag': '🇮🇹'},
    'ES': {'name': 'Spain',          'flag': '🇪🇸'},
    'NL': {'name': 'Netherlands',    'flag': '🇳🇱'},
    'SE': {'name': 'Sweden',         'flag': '🇸🇪'},
    'PL': {'name': 'Poland',         'flag': '🇵🇱'},
    'TR': {'name': 'Turkey',         'flag': '🇹🇷'},
    'ID': {'name': 'Indonesia',      'flag': '🇮🇩'},
    'PH': {'name': 'Philippines',    'flag': '🇵🇭'},
    'NG': {'name': 'Nigeria',        'flag': '🇳🇬'},
    'ZA': {'name': 'South Africa',   'flag': '🇿🇦'},
    'AR': {'name': 'Argentina',      'flag': '🇦🇷'},
    'CO': {'name': 'Colombia',       'flag': '🇨🇴'},
    'EG': {'name': 'Egypt',          'flag': '🇪🇬'},
    'TH': {'name': 'Thailand',       'flag': '🇹🇭'},
    'MY': {'name': 'Malaysia',       'flag': '🇲🇾'},
    'SG': {'name': 'Singapore',      'flag': '🇸🇬'},
    'VN': {'name': 'Vietnam',        'flag': '🇻🇳'},
    'TW': {'name': 'Taiwan',         'flag': '🇹🇼'},
    'RU': {'name': 'Russia',         'flag': '🇷🇺'},
    'NO': {'name': 'Norway',         'flag': '🇳🇴'},
    'DK': {'name': 'Denmark',        'flag': '🇩🇰'},
    'FI': {'name': 'Finland',        'flag': '🇫🇮'},
    'CL': {'name': 'Chile',          'flag': '🇨🇱'},
    'PE': {'name': 'Peru',           'flag': '🇵🇪'},
}

BLOCKED = {'porn', 'xxx', 'nude', 'naked', 'sex tape', 'murder how to', 'bomb making'}

CATEGORY_KW = {
    'sports':  ['nfl','nba','mlb','nhl','soccer','football','basketball','baseball','tennis','golf',
                'formula 1','f1 grand prix','olympics','world cup','liga','premier league',
                'championship','tournament','playoff','draft','standings','roster','trade',
                'athlete','player','coach','manager','striker','goalkeeper','quarterback',
                'hockey','cricket','rugby','volleyball','swimming','athletics','marathon',
                'miami open','indian wells','australian open','us open','french open',
                'grand slam','wimbledon','masters','superbowl','super bowl',
                'march madness','ncaa','mls','ufc','boxing','wrestling','cycling','ski',
                'defeats','wins match','beats in','scores goal','hat trick','transfer fee',
                'signing','transferred','relegated','promoted','race winner','podium'],
    'music':   ['album','song','concert','concert tour','world tour','grammy','billboard',
                'music video','official mv','singer','rapper','spotify','music chart',
                'kpop','k-pop','mv teaser','debut album','music awards',
                'music festival','coachella','lollapalooza','hot 100',
                'streaming record','listening party','music release'],
    'movies':  ['movie','movies','film','films','series','netflix','disney','hbo','amazon prime',
                'tv show','trailer','teaser','actor','actress','actors','celebrity',
                'award','oscar','emmy','golden globe','bafta','box office','anime',
                'streaming','new season','episode','premiere','sitcom',
                'documentary','director','blockbuster','cinemas','theaters',
                'returns to movies','returns to films','new film'],
    'tech':    ['artificial intelligence','chatgpt','openai','apple','google','microsoft',
                'samsung','iphone','android','software','startup','crypto','bitcoin',
                'blockchain','meta','tesla','spacex','nvidia','amazon','aws','cloud',
                'app store','app launch','update released','cybersecurity','hack','breach',
                'data leak','autonomous','electric vehicle','ev'],
    'finance': ['stock price','stock market','share price','gdp','inflation','interest rate',
                'stock exchange','hedge fund','mutual fund','investment fund',
                'dow jones','nasdaq','dax','nikkei','kospi','ibovespa','cac 40','ftse','asx','s&p 500',
                'federal reserve','ecb','rate hike','recession','ipo','earnings report',
                'quarterly earnings','bonds','forex','currency exchange','exchange rate',
                '株価','주가','bolsa','bourse'],
}

# News source → category mapping (most reliable signal)
SOURCE_CATS = {
    'sports': ['espn', 'sports illustrated', 'si.com', 'bleacher report', 'the athletic',
               'sky sports', 'goal.com', 'marca', 'gazzetta', 'sportswire', 'sport bild',
               "l'equipe", 'transfermarkt', 'cbssports', 'fox sports', 'nfl.com', 'nba.com',
               'mlb.com', 'nhl.com', 'tennis', 'golf digest', 'cycling', 'athletics weekly',
               'fight sports', 'mma', 'ufc', 'formula1', 'motorsport'],
    'music':  ['billboard', 'rolling stone', 'pitchfork', 'nme', 'genius', 'music week',
               'consequence', 'allmusic', 'spin', 'loudwire', 'kerrang', 'clash music',
               'musicweek', 'uproxx music'],
    'movies': ['variety', 'hollywood reporter', 'deadline', 'imdb', 'screen rant',
               'collider', 'rotten tomatoes', 'indiewire', 'box office mojo', 'cinemablend',
               'den of geek', 'empire', 'total film', 'movieweb'],
    'tech':   ['techcrunch', 'the verge', 'wired', 'engadget', 'ars technica', 'gizmodo',
               'cnet', 'zdnet', "tom's guide", '9to5mac', '9to5google', 'macrumors',
               'android authority', 'gsmarena', 'pcmag', 'tomsguide'],
    'finance':['wall street journal', 'wsj', 'financial times', 'ft.com',
               'marketwatch', 'seeking alpha', 'investopedia', 'barrons',
               'morningstar', 'moneywise', 'thestreet'],
}

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; GlobalTrendBot/1.0)'}
S = requests.Session()
S.headers.update(HEADERS)


def translate_to_english(text: str) -> str:
    """Translate non-ASCII text to English using Google Translate (free, no key)."""
    if all(ord(c) < 128 for c in text):
        return text  # Already ASCII
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={url_quote(text)}"
        r = S.get(url, timeout=5)
        data = r.json()
        translated = ''.join([item[0] for item in data[0] if item[0]])
        return translated.strip() or text
    except Exception:
        return text


def classify(kw, news_title='', source=''):
    import re
    # Keyword + news title context first (more precise)
    ctx = (kw + ' ' + news_title).lower()
    for cat, words in CATEGORY_KW.items():
        for w in words:
            if re.search(r'\b' + re.escape(w) + r'\b', ctx):
                return cat
    # Source-based as fallback (only when keyword matching fails)
    src = source.lower()
    for cat, srcs in SOURCE_CATS.items():
        if any(s in src for s in srcs):
            return cat
    return 'news'


def velocity(rank):
    if rank <= 3:  return 'rising'
    if rank <= 8:  return 'new'
    if rank <= 14: return 'steady'
    return 'falling'


def fmt_vol(n):
    if n >= 1_000_000: return f'{n // 1_000_000}M+'
    if n >= 1_000:     return f'{n // 1_000}K+'
    return str(n)


def calc_temp(vol, rank, spread):
    return min(100, min(50, int(vol / 200_000)) + max(0, 30 - rank * 2) + min(20, spread * 5))


# ============================================================
# CATEGORY-SPECIFIC CHART COLLECTION
# ============================================================

def collect_itunes_music(limit=50):
    """iTunes Top Songs chart (US) — free, no API key."""
    items = []
    try:
        url = f'https://itunes.apple.com/us/rss/topsongs/limit={limit}/json'
        r = S.get(url, timeout=20)
        entries = r.json().get('feed', {}).get('entry', [])
        for rank, entry in enumerate(entries[:limit], 1):
            name   = (entry.get('im:name', {}).get('label') or '').strip()
            artist = (entry.get('im:artist', {}).get('label') or '').strip()
            kw = f"{name} — {artist}" if artist else name
            if not kw:
                continue
            vol_raw = max(500_000 - rank * 9_000, 1_000)
            items.append({
                'rank': rank, 'keyword': kw, 'keywordEn': kw,
                'volume': fmt_vol(vol_raw), 'volumeRaw': vol_raw,
                'category': 'music', 'temperature': max(90 - rank, 25),
                'velocity': velocity(rank), 'source': 'Apple Music',
            })
        log.info('iTunes Music: %d songs', len(items))
    except Exception as ex:
        log.warning('iTunes Music chart failed: %s', ex)
    return items


def collect_itunes_movies(limit=50):
    """iTunes Top Movies chart (US) — free, no API key."""
    items = []
    try:
        url = f'https://itunes.apple.com/us/rss/topmovies/limit={limit}/json'
        r = S.get(url, timeout=20)
        entries = r.json().get('feed', {}).get('entry', [])
        for rank, entry in enumerate(entries[:limit], 1):
            name = (entry.get('im:name', {}).get('label') or '').strip()
            if not name:
                continue
            vol_raw = max(200_000 - rank * 3_500, 1_000)
            items.append({
                'rank': rank, 'keyword': name, 'keywordEn': name,
                'volume': fmt_vol(vol_raw), 'volumeRaw': vol_raw,
                'category': 'movies', 'temperature': max(90 - rank, 25),
                'velocity': velocity(rank), 'source': 'iTunes Movies',
            })
        log.info('iTunes Movies: %d movies', len(items))
    except Exception as ex:
        log.warning('iTunes Movies chart failed: %s', ex)
    return items


def collect_hackernews(limit=50):
    """Hacker News top stories — free, no API key."""
    items = []
    try:
        ids = S.get(
            'https://hacker-news.firebaseio.com/v0/topstories.json', timeout=10
        ).json()[:(limit * 2)]
        rank = 1
        for story_id in ids:
            if rank > limit:
                break
            try:
                item = S.get(
                    f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json', timeout=5
                ).json()
                if item.get('type') != 'story':
                    continue
                title = (item.get('title') or '').strip()
                if not title:
                    continue
                score = item.get('score', 10)
                vol_raw = score * 150
                items.append({
                    'rank': rank, 'keyword': title, 'keywordEn': title,
                    'volume': fmt_vol(vol_raw), 'volumeRaw': vol_raw,
                    'category': 'tech', 'temperature': max(88 - rank, 20),
                    'velocity': velocity(rank), 'source': 'Hacker News',
                })
                rank += 1
                time.sleep(0.05)
            except Exception:
                continue
        log.info('Hacker News: %d stories', len(items))
    except Exception as ex:
        log.warning('Hacker News failed: %s', ex)
    return items


def collect_finance_rss(limit=50):
    """MarketWatch RSS feeds — free."""
    items = []
    seen = set()
    feeds = [
        'https://feeds.marketwatch.com/marketwatch/topstories/',
        'https://feeds.marketwatch.com/marketwatch/realtimeheadlines/',
        'https://feeds.marketwatch.com/marketwatch/marketpulse/',
    ]
    rank = 1
    for feed_url in feeds:
        if rank > limit:
            break
        try:
            r = S.get(feed_url, timeout=10)
            feed = feedparser.parse(r.text)
            for e in feed.entries:
                if rank > limit:
                    break
                title = (e.get('title') or '').strip()
                if not title or title in seen:
                    continue
                seen.add(title)
                vol_raw = max(100_000 - rank * 1_800, 500)
                items.append({
                    'rank': rank, 'keyword': title, 'keywordEn': title,
                    'volume': fmt_vol(vol_raw), 'volumeRaw': vol_raw,
                    'category': 'finance', 'temperature': max(80 - rank, 20),
                    'velocity': velocity(rank), 'source': 'MarketWatch',
                })
                rank += 1
        except Exception as ex:
            log.warning('Finance RSS %s failed: %s', feed_url, ex)
    log.info('Finance RSS: %d stories', len(items))
    return items


def collect_sports_rss(limit=50):
    """ESPN + BBC Sport RSS — free."""
    items = []
    seen = set()
    feeds = [
        ('ESPN',      'https://www.espn.com/espn/rss/news'),
        ('BBC Sport', 'https://feeds.bbci.co.uk/sport/rss.xml'),
    ]
    rank = 1
    for source_name, feed_url in feeds:
        if rank > limit:
            break
        try:
            r = S.get(feed_url, timeout=10)
            feed = feedparser.parse(r.text)
            for e in feed.entries:
                if rank > limit:
                    break
                title = (e.get('title') or '').strip()
                if not title or title in seen:
                    continue
                seen.add(title)
                vol_raw = max(300_000 - rank * 5_500, 1_000)
                items.append({
                    'rank': rank, 'keyword': title, 'keywordEn': title,
                    'volume': fmt_vol(vol_raw), 'volumeRaw': vol_raw,
                    'category': 'sports', 'temperature': max(85 - rank, 20),
                    'velocity': velocity(rank), 'source': source_name,
                })
                rank += 1
        except Exception as ex:
            log.warning('Sports RSS %s failed: %s', feed_url, ex)
    log.info('Sports RSS: %d stories', len(items))
    return items


countries_out = {}
keyword_country_map = {}

log.info('=== Starting quick trend collection ===')

for code, meta in COUNTRIES.items():
    try:
        url = f'https://trends.google.com/trending/rss?geo={code}&hl=en'
        r = S.get(url, timeout=15)
        r.raise_for_status()
        feed = feedparser.parse(r.text)
        trends = []
        for rank, e in enumerate(feed.entries[:20], 1):
            kw = e.get('title', '').strip()
            if not kw or any(b in kw.lower() for b in BLOCKED):
                continue
            traffic = getattr(e, 'ht_approx_traffic', '') or ''
            m = re.search(r'([\d,]+)', traffic.replace('+', ''))
            if not m:
                continue
            vol = int(m.group(1).replace(',', ''))
            news_title = (getattr(e, 'ht_news_item_title', '') or '').strip()
            source = (getattr(e, 'ht_news_item_source', '') or '').strip()
            keyword_en = translate_to_english(kw)
            trends.append({
                'rank':        rank,
                'keyword':     kw,
                'volume':      fmt_vol(vol),
                'volumeRaw':   vol,
                'category':    classify(keyword_en, news_title, source),
                'temperature': 0,
                'velocity':    velocity(rank),
                'keywordEn':   keyword_en,
                'isGlobal':    False,
            })
            keyword_country_map.setdefault(kw.lower(), []).append(code)
        countries_out[code] = {'name': meta['name'], 'flag': meta['flag'], 'trends': trends}
        log.info('%s: %d trends', code, len(trends))
        time.sleep(0.4)
    except Exception as ex:
        log.warning('%s failed: %s', code, ex)
        countries_out[code] = {'name': meta['name'], 'flag': meta['flag'], 'trends': []}

# Recalculate temperature with cross-country spread
all_trends = []
for code, cdata in countries_out.items():
    for t in cdata['trends']:
        spread = len(keyword_country_map.get(t['keyword'].lower(), []))
        t['isGlobal'] = spread >= 3
        t['temperature'] = calc_temp(t['volumeRaw'], t['rank'], spread)
        all_trends.append({**t, '_country': code, '_flag': cdata['flag']})

all_trends.sort(key=lambda x: (-x['temperature'], -x['volumeRaw']))

# Global stats
top = all_trends[0] if all_trends else {}
global_temp = int(sum(t['temperature'] for t in all_trends) / max(len(all_trends), 1))

rising_fast = []
seen_rf = set()
for t in all_trends[:15]:
    if t['keyword'] not in seen_rf and len(rising_fast) < 3:
        rising_fast.append({
            'keyword':   t['keyword'],
            'keywordEn': t.get('keywordEn', t['keyword']),
            'country':   t['_country'],
            'change':    t['volume'],
        })
        seen_rf.add(t['keyword'])

cat_counts: dict = {}
for t in all_trends:
    cat_counts[t.get('category', 'news')] = cat_counts.get(t.get('category', 'news'), 0) + 1
total_cat = max(len(all_trends), 1)
cat_breakdown = {
    c: round(n / total_cat * 100)
    for c, n in sorted(cat_counts.items(), key=lambda x: -x[1])
}

total_trends = sum(len(c['trends']) for c in countries_out.values())
active_countries = len([c for c in countries_out.values() if c['trends']])

if active_countries < 5:
    log.warning('Only %d countries collected — aborting', active_countries)
    sys.exit(0)

# ============================================================
# CATEGORY CHARTS
# ============================================================
log.info('=== Collecting category charts ===')
category_charts = {
    'music':   collect_itunes_music(50),
    'movies':  collect_itunes_movies(50),
    'tech':    collect_hackernews(50),
    'finance': collect_finance_rss(50),
    'sports':  collect_sports_rss(50),
}
log.info('Charts: %s', {k: len(v) for k, v in category_charts.items()})

output = {
    'lastUpdated': datetime.now(timezone.utc).isoformat(),
    'countries': countries_out,
    'categoryCharts': category_charts,
    'global': {
        'temperature':     global_temp,
        'topTrend': {
            'keyword':   top.get('keyword', ''),
            'keywordEn': top.get('keywordEn', top.get('keyword', '')),
            'country':   top.get('_country', ''),
            'volume':    top.get('volume', ''),
            'flag':      top.get('_flag', ''),
            'category':  top.get('category', 'news'),
        },
        'totalCountries':   active_countries,
        'totalTrends':      total_trends,
        'risingFast':       rising_fast,
        'categoryBreakdown': cat_breakdown,
    }
}

ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
if OUTPUT_FILE.exists():
    ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')
    shutil.copy2(OUTPUT_FILE, ARCHIVE_DIR / f'trends_{ts}.json')

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

log.info('=== DONE — %d countries | %d trends | temp=%d° ===', active_countries, total_trends, global_temp)
log.info('Top trend: %s (%s)', top.get('keyword'), top.get('_country'))

# ============================================================
# GENERATE STATIC SITEMAP (avoids Next.js RSC Vary headers)
# ============================================================
SITE_URL = 'https://global-trend-map-web.vercel.app'
SITEMAP_FILE = BASE_DIR / 'public' / 'sitemap.xml'
POSTS_INDEX_FILE = DATA_DIR / 'posts-index.json'

def _url(loc, lastmod, changefreq, priority):
    return f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>{changefreq}</changefreq>\n    <priority>{priority}</priority>\n  </url>'

today = datetime.now(timezone.utc).strftime('%Y-%m-%dT00:00:00Z')
static_pages = [
    (SITE_URL,                        'hourly',  '1.0'),
    (f'{SITE_URL}/blog',              'hourly',  '0.9'),
    (f'{SITE_URL}/about',             'monthly', '0.7'),
    (f'{SITE_URL}/contact',           'monthly', '0.6'),
    (f'{SITE_URL}/privacy-policy',    'yearly',  '0.3'),
    (f'{SITE_URL}/terms',             'yearly',  '0.3'),
    (f'{SITE_URL}/cookie-policy',     'yearly',  '0.3'),
    (f'{SITE_URL}/dmca',              'yearly',  '0.2'),
    (f'{SITE_URL}/disclaimer',        'yearly',  '0.2'),
    (f'{SITE_URL}/editorial-policy',  'yearly',  '0.3'),
]

sitemap_urls = [_url(loc, today, freq, prio) for loc, freq, prio in static_pages]

# Blog posts
try:
    raw = json.loads(POSTS_INDEX_FILE.read_text(encoding='utf-8'))
    posts = raw.get('posts', raw) if isinstance(raw, dict) else raw
    for p in posts:
        sitemap_urls.append(_url(f"{SITE_URL}/blog/{p['slug']}", p.get('date', today), 'weekly', '0.8'))
except Exception:
    pass

# Country pages
for code in countries_out:
    sitemap_urls.append(_url(f"{SITE_URL}/country/{code.lower()}", today, 'hourly', '0.85'))

sitemap_xml = '\n'.join([
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    *sitemap_urls,
    '</urlset>',
])

SITEMAP_FILE.write_text(sitemap_xml, encoding='utf-8')
log.info('Sitemap written → %s (%d URLs)', SITEMAP_FILE, len(sitemap_urls))
