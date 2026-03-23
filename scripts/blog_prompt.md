# 블로그 포스트 자동 생성 태스크

## 1단계: 최신 데이터 받기
아래 명령어를 실행한다:
```bash
cd C:\Users\seheo\global-trend-map && git pull origin main
```

## 2단계: research.json 생성
아래 명령어를 실행한다:
```bash
cd C:\Users\seheo\global-trend-map && python scripts/extract_research.py
```

## 3단계: research.json 확인
`scripts/research.json`을 읽어라.

- `status`가 `"skip"`이면 **즉시 중단**. skip_reason을 출력한다.
- `status`가 `"write"`이면 계속 진행한다.

## 4단계: 키워드 실시간 리서치 (핵심)
research.json의 `keyword`를 가지고 아래 2개를 웹 검색한다.

검색 1: `{keyword} trending news 2026`
검색 2: `{keyword} why viral today`

검색 결과에서 다음을 파악한다:
- 이 키워드가 정확히 무엇인가?
- 오늘 왜 갑자기 트렌딩이 됐는가? (신곡 발매? 사건? 예고편 공개? 수상?)
- 어떤 반응이 있는가?

이 내용을 블로그 본문 특히 "## Why Is X Trending Today?" 섹션에 반영한다.

## 5단계: 글쓰기 기준 확인
`scripts/WRITING_GUIDE.md`를 읽어라.

## 6단계: 영어(EN) 블로그 포스트 작성

research.json 데이터 + 4단계 리서치 결과를 바탕으로 영어 블로그를 작성한다.

### 핵심 원칙
- "왜 트렌딩인가" 섹션은 실시간 리서치로 파악한 실제 이유를 쓴다
- 카테고리 공통 문단 절대 금지. 이 키워드만의 고유한 내용
- WRITING_GUIDE.md의 9개 섹션 구조 준수
- 1,500~2,000 단어

### 사용할 데이터 (research.json)
- `keyword`, `category`, `date_str`
- `top_country_name`, `top_country_flag`, `volume`, `temperature`
- `total_countries`, `countries` (트렌딩 국가 목록)
- `rising_others` (함께 상승 중인 트렌드)
- `category_breakdown`
- `youtube_url` (있으면 삽입)
- `google_trends_url` (반드시 삽입)
- `site_url` (내부링크)
- `internal_links` (기존 포스트, 1~2개 자연스럽게 삽입)

### MDX 파일 저장
`public/blog/{date}-spotlight-{keyword_slug}-en.mdx`

frontmatter:
```
---
slug: {date}-spotlight-{keyword_slug}-en
title: "{영어 제목}"
date: "{date}"
lastUpdated: "{현재 ISO timestamp}"
excerpt: "{2-3문장 요약}"
category: {category}
language: en
featured: true
readingTime: {단어수/200 반올림, 최소 1}
tags:
  - {keyword_slug}
  - {category}
  - global-trends
  - trending
alternates:
  en: /blog/{date}-spotlight-{keyword_slug}-en
  zh: /blog/{date}-spotlight-{keyword_slug}-zh
  es: /blog/{date}-spotlight-{keyword_slug}-es
  pt: /blog/{date}-spotlight-{keyword_slug}-pt
  fr: /blog/{date}-spotlight-{keyword_slug}-fr
  de: /blog/{date}-spotlight-{keyword_slug}-de
  kr: /blog/{date}-spotlight-{keyword_slug}-kr
  jp: /blog/{date}-spotlight-{keyword_slug}-jp
openGraph:
  title: "{영어 제목}"
  description: "{excerpt}"
  locale: en_US
---
```

## 7단계: 7개 언어 번역

EN 포스트를 아래 7개 언어로 번역한다.
구조, 섹션, 정보량은 EN과 완전히 동일하게 유지한다.
readingTime은 EN과 동일한 값을 사용한다.

| lang | locale |
|---|---|
| zh | zh_CN |
| es | es_ES |
| pt | pt_BR |
| fr | fr_FR |
| de | de_DE |
| kr | ko_KR |
| jp | ja_JP |

각 파일: `public/blog/{date}-spotlight-{keyword_slug}-{lang}.mdx`
title, excerpt는 해당 언어로 번역. openGraph locale은 위 표 참조.

## 8단계: posts-index.json 업데이트

`public/data/posts-index.json`을 읽고 업데이트한다.

`posts` 배열 앞에 8개 항목 추가 (en, zh, es, pt, fr, de, kr, jp 순):
```json
{
  "slug": "{date}-spotlight-{keyword_slug}-{lang}",
  "title": "{해당 언어 제목}",
  "date": "{date}",
  "lastUpdated": "{ISO timestamp}",
  "excerpt": "{해당 언어 excerpt}",
  "category": "{category}",
  "language": "{lang}",
  "readingTime": {EN과 동일},
  "featured": true,
  "tags": ["{keyword_slug}", "{category}", "global-trends", "trending"]
}
```

`recentSpotlights` 앞에 추가:
```json
{"keyword": "{keyword 소문자}", "date": "{date}"}
```
최근 10개만 유지한다.

## 9단계: 커밋 & 푸시
아래 명령어를 실행한다:
```bash
cd C:\Users\seheo\global-trend-map && git add public/blog/ public/data/posts-index.json && git diff --staged --quiet || git commit -m "Auto: Blog - {keyword} ({date})" && git push origin HEAD:main
```

완료 후 "✅ {keyword} — 8개 언어 포스트 발행 완료" 출력.
