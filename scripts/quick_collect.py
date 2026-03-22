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
    'sports':  ['nfl','nba','mlb','soccer','football','basketball','baseball','tennis','golf',
                'f1','formula','olympics','world cup','liga','premier','championship','tournament',
                'match','athlete','player','sport','hockey','cricket','rugby'],
    'music':   ['album','song','concert','tour','grammy','billboard','single','music','singer',
                'rapper','band','spotify','chart','release','kpop','k-pop'],
    'tech':    ['ai','artificial intelligence','chatgpt','openai','apple','google','microsoft',
                'samsung','iphone','android','app','software','startup','crypto','bitcoin',
                'blockchain','meta','tesla','spacex'],
    'movies':  ['movie','film','series','netflix','disney','hbo','tv show','trailer','actor',
                'actress','celebrity','award','oscar','emmy','box office','anime'],
    'finance': ['stock','market','economy','gdp','inflation','rate','bank','fund','invest',
                'dow','nasdaq','dax','nikkei','kospi','ibovespa','cac','ftse','asx'],
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


def classify(kw):
    k = kw.lower()
    for cat, words in CATEGORY_KW.items():
        for w in words:
            if w in k:
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
            trends.append({
                'rank':        rank,
                'keyword':     kw,
                'volume':      fmt_vol(vol),
                'volumeRaw':   vol,
                'category':    classify(kw),
                'temperature': 0,
                'velocity':    velocity(rank),
                'keywordEn':   translate_to_english(kw),
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
            'keyword': t['keyword'],
            'country': t['_country'],
            'change':  t['volume'],
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

output = {
    'lastUpdated': datetime.now(timezone.utc).isoformat(),
    'countries': countries_out,
    'global': {
        'temperature':     global_temp,
        'topTrend': {
            'keyword':  top.get('keyword', ''),
            'country':  top.get('_country', ''),
            'volume':   top.get('volume', ''),
            'flag':     top.get('_flag', ''),
            'category': top.get('category', 'news'),
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
