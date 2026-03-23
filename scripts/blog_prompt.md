# 블로그 포스트 자동 생성 태스크

## 1단계: research.json 확인
`scripts/research.json`을 읽어라.

- `status`가 `"skip"`이면 **즉시 중단**하고 skip_reason을 출력한다.
- `status`가 `"write"`이면 계속 진행한다.

## 2단계: 글쓰기 기준 확인
`scripts/WRITING_GUIDE.md`를 읽어라. 이 기준을 엄격히 따른다.

## 3단계: 영어(EN) 블로그 포스트 작성

research.json의 데이터를 바탕으로 **영어 블로그 포스트**를 작성한다.

### 핵심 원칙
- `keyword` 자체에 대한 구체적인 설명과 분석을 작성한다
- "왜 지금 이 키워드가 트렌딩인가"를 실제로 분석한다 (카테고리 공통 문단 절대 금지)
- WRITING_GUIDE.md의 9개 섹션 구조를 반드시 따른다
- 1,500~2,000 단어

### 사용할 데이터
- `keyword`: 오늘의 주제
- `category`: 카테고리
- `top_country_name` + `top_country_flag`: 진원국
- `volume`: 검색량
- `temperature`: 트렌드 강도 (0-100)
- `total_countries`: 모니터링 국가 수
- `countries`: 트렌딩 중인 국가 목록 (flag + name)
- `rising_others`: 함께 상승 중인 다른 트렌드
- `category_breakdown`: 카테고리별 트렌드 수
- `youtube_url`: YouTube 링크 (있으면 삽입)
- `google_trends_url`: Google Trends 링크 (반드시 삽입)
- `site_url`: 사이트 URL (내부링크에 사용)
- `internal_links`: 기존 발행 포스트 (본문에 1~2개 자연스럽게 삽입)

### MDX 파일 저장
파일명: `public/blog/{date}-spotlight-{keyword_slug}-en.mdx`

frontmatter 형식:
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
readingTime: {단어수 / 200, 반올림, 최소 1}
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

## 4단계: 7개 언어 번역 (EN 기준)

작성한 영어 포스트를 아래 7개 언어로 번역한다.
**구조, 섹션, 정보량이 EN과 완전히 동일**해야 한다.
readingTime은 EN과 동일한 값을 사용한다.

| 언어 | lang 코드 | locale |
|---|---|---|
| 중국어 간체 | zh | zh_CN |
| 스페인어 | es | es_ES |
| 포르투갈어 | pt | pt_BR |
| 프랑스어 | fr | fr_FR |
| 독일어 | de | de_DE |
| 한국어 | kr | ko_KR |
| 일본어 | jp | ja_JP |

각 파일 저장: `public/blog/{date}-spotlight-{keyword_slug}-{lang}.mdx`

frontmatter의 title, excerpt는 해당 언어로 번역한다.
openGraph locale은 위 표 참조.

## 5단계: posts-index.json 업데이트

`public/data/posts-index.json`을 읽고 업데이트한다.

`posts` 배열 **앞에** 8개 항목 추가 (언어 순서: en, zh, es, pt, fr, de, kr, jp):
```json
{
  "slug": "{date}-spotlight-{keyword_slug}-{lang}",
  "title": "{해당 언어 제목}",
  "date": "{date}",
  "lastUpdated": "{현재 ISO timestamp}",
  "excerpt": "{해당 언어 excerpt}",
  "category": "{category}",
  "language": "{lang}",
  "readingTime": {EN과 동일},
  "featured": true,
  "tags": ["{keyword_slug}", "{category}", "global-trends", "trending"]
}
```

`recentSpotlights` 배열 **앞에** 추가:
```json
{"keyword": "{keyword 소문자}", "date": "{date}"}
```
최근 10개만 유지하고 나머지는 제거한다.

파일 저장 후 완료 메시지 출력.
