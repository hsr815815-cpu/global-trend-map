# Global Trend Map — Blog Writing Guide

## 목적
오늘의 글로벌 트렌드 1위 키워드를 분석한 SEO 최적화 블로그 포스트를 작성한다.
독자는 "왜 이게 지금 전 세계에서 검색되고 있는가"가 궁금한 일반인이다.

---

## 필수 구조 (9개 섹션, 순서 고정)

### 1. 인트로 (2문단)
- 1문단: 키워드가 오늘 몇 개국에서 1위인지, 검색량, 진원국 명시
- 2문단: 독자를 글로 끌어당기는 문장 + 이 글이 무엇을 분석하는지

### 2. ## What Is "{keyword}"? (키워드별 고유 설명)
- **이 키워드가 실제로 무엇인지** 구체적으로 설명 (가수면 가수, 영화면 영화, 사건이면 사건)
- 트렌드 온도, 카테고리, 진원국 언급
- ### Key Statistics 표 (검색량/온도/카테고리/국가/데이터소스)
- YouTube 링크 있으면 삽입

### 3. ## Why Is "{keyword}" Trending Today? (핵심 섹션)
- **이 키워드가 왜 지금 이 시점에 트렌딩인지** 구체적으로 분석
- 카테고리 공통 문단 절대 금지. 키워드 자체에 대한 내용만
- 예: BTS SWIM → 컴백 맥락, ARMY 반응, 스트리밍 수치
- 예: 외계인 출현 → 어디서 발생한 뉴스인지, 어떤 맥락인지
- Google Trends 링크 삽입

### 4. ## Which Countries Are Searching?
- 국가 목록 (데이터에서 추출)
- ### Where the Signal Is Strongest: 진원국 + 확산 패턴 설명

### 5. ## Trend Data & Statistics
- 전체 통계 표
- 트렌드 온도 설명 (0-100 척도)

### 6. ## What Else Is Trending Right Now?
- risingFast 목록
- 1문단 설명

### 7. ## Today's Global Search Landscape by Category
- categoryBreakdown 목록
- 1문단 설명

### 8. ## Frequently Asked Questions (5개 고정)
Q1: {keyword}이란 무엇인가?
Q2: 왜 오늘 트렌딩인가?
Q3: 어느 나라가 가장 많이 검색하는가?
Q4: TrendPulse는 어떻게 강도를 측정하는가?
Q5: 더 많은 트렌드 데이터는 어디서 볼 수 있는가?

### 9. ## Stay Ahead (CTA)
- 사이트 링크, 블로그 링크
- 데이터 수집일 명시

---

## 길이 기준
- 영어 기준 1,500~2,000 단어
- 8개 언어 모두 동일한 구조, 동일한 정보량
- 번역이 아니라 각 언어로 자연스럽게 작성

---

## 8개 언어
en, zh, es, pt, fr, de, kr, jp

---

## MDX 파일 형식

```
---
slug: {YYYY-MM-DD}-spotlight-{keyword-slug}-{lang}
title: "{제목}"
date: "{YYYY-MM-DD}"
lastUpdated: "{ISO timestamp}"
excerpt: "{2-3문장 요약}"
category: {music|sports|tech|finance|movies|news}
language: {lang}
featured: true
readingTime: {EN 기준 분 수, 8개 언어 동일}
tags:
  - {keyword-slug}
  - {category}
  - global-trends
  - trending
alternates:
  en: /blog/{date}-spotlight-{keyword-slug}-en
  zh: /blog/{date}-spotlight-{keyword-slug}-zh
  es: /blog/{date}-spotlight-{keyword-slug}-es
  pt: /blog/{date}-spotlight-{keyword-slug}-pt
  fr: /blog/{date}-spotlight-{keyword-slug}-fr
  de: /blog/{date}-spotlight-{keyword-slug}-de
  kr: /blog/{date}-spotlight-{keyword-slug}-kr
  jp: /blog/{date}-spotlight-{keyword-slug}-jp
openGraph:
  title: "{제목}"
  description: "{excerpt}"
  locale: {en_US|zh_CN|es_ES|pt_BR|fr_FR|de_DE|ko_KR|ja_JP}
---

{본문}
```

---

## 슬러그 규칙
- 키워드 소문자, 특수문자 제거, 공백→하이픈
- 최대 60자
- 예: `bts-bulletproof-boys-swim-official-mv`

---

## 내부링크
- posts-index.json의 기존 포스트 URL을 본문에 자연스럽게 1~3개 삽입
- 앵커텍스트는 키워드와 관련된 자연스러운 문구

---

## 절대 금지
- 카테고리별 미리 작성된 공통 문단 사용
- Wikipedia 언급
- Yandex 언급
- 키워드와 무관한 일반적 설명
