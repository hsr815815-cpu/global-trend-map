# Global Trend Map — Blog Writing Guide

## 목적
오늘의 글로벌 트렌드 1위 키워드를 분석한 SEO 최적화 블로그 포스트를 작성한다.
독자는 "왜 이게 지금 전 세계에서 검색되고 있는가"가 궁금한 일반인이다.

---

## 포맷 선택 (키워드 성격에 맞게 1개 선택)

키워드를 파악한 후, 아래 5가지 포맷 중 **가장 어울리는 것 1개**를 선택한다.
매번 같은 포맷을 쓰지 않는다. 이전 글과 다른 포맷을 우선 고려한다.

### 포맷 A — 서사형 (Narrative)
**어울리는 키워드:** 아티스트 컴백, 영화 개봉, 스포츠 우승
구조: 오프닝 훅 → 배경/맥락 → 왜 지금인가 → 반응 → 데이터 → Our Take → FAQ → CTA
특징: 스토리처럼 읽힌다. 데이터 표는 중반 이후에 등장.

### 포맷 B — 뉴스 브리핑형 (Breaking News)
**어울리는 키워드:** 사건/사고, 정치, 긴급 이슈
구조: 핵심 요약 (무슨 일이 일어났나) → 타임라인 → 국가별 반응 → 데이터 → Our Take → FAQ → CTA
특징: 짧고 빠르게 읽힌다. 1,000~1,400단어.

### 포맷 C — 데이터 심층형 (Data Deep-Dive)
**어울리는 키워드:** 금융, 스포츠 기록, 기술 발표
구조: 인트로 → 핵심 통계 → 왜 이 수치가 의미 있는가 → 국가별 분석 → 비교 맥락 → Our Take → FAQ → CTA
특징: 표와 수치가 본문의 주인공. 분석 텍스트가 표를 감싼다.

### 포맷 D — 논쟁/양면 분석형 (Both Sides)
**어울리는 키워드:** 논란, 논쟁, 찬반이 갈리는 이슈
구조: 논쟁 소개 → A 측 주장 → B 측 주장 → 데이터로 보면 → Our Take (입장 명시) → FAQ → CTA
특징: "Our Take"에서 반드시 입장을 취한다. 열린 결말 금지.

### 포맷 E — Q&A 심화형 (FAQ-First)
**어울리는 키워드:** 처음 듣는 이름, 생소한 개념, 대중이 기본부터 궁금해하는 것
구조: 한 줄 요약 → "X가 뭔가요?" 심화 답변 → "왜 지금?" 심화 답변 → 데이터 → Our Take → 추가 FAQ 3개 → CTA
특징: FAQ가 단순 목록이 아니라 각각 200자 이상의 심층 답변.

---

## 필수 섹션: Our Take (모든 포맷 공통)

**모든 포맷에 반드시 포함한다.**

- 이 트렌드가 무엇을 의미하는지에 대한 **편집팀의 해석과 의견**
- "데이터가 보여주는 것 이상으로 우리는 이렇게 본다"는 관점
- 단순 사실 요약 금지. 반드시 판단/예측/시사점 중 하나를 포함
- 100~200단어. H2 제목은 키워드에 맞게 창작 (예: "The Bigger Picture", "What This Really Means", "읽어야 할 신호" 등)

---

## H2 섹션 제목 규칙

- **고정 제목 사용 금지.** "Why Is X Trending Today?", "Which Countries Are Searching?" 같은 템플릿 제목 반복 금지
- 키워드와 포맷에 맞게 매번 창작한다
- 예시 (BTS 컴백): "Four Years in the Making", "The ARMY Effect", "From Seoul to Stockholm"
- 예시 (금융 이슈): "The Numbers That Shocked Markets", "Where the Panic Spread First"

---

## 길이 기준

- 포맷 B: 1,000~1,400단어
- 포맷 A, D, E: 1,400~1,800단어
- 포맷 C: 1,600~2,200단어
- **매번 비슷한 단어 수가 되지 않도록 의식적으로 변화를 준다**

---

## 7개 언어 번역 → 현지화 재작성

번역이 아니다. **해당 언어 독자의 관점으로 재작성**한다.

| 언어 | 현지화 관점 |
|---|---|
| zh | 웨이보/빌리빌리 반응, 중국 팬덤 시각 |
| es | 라틴아메리카 팬 문화, 스페인어권 미디어 반응 |
| pt | 브라질 소셜미디어 반응, 포르투갈어권 맥락 |
| fr | 프랑스/유럽 미디어 시각, 프랑스어권 반응 |
| de | 독일어권 독자 관점, 유럽 시장 맥락 |
| kr | 한국 팬덤/커뮤니티 반응, 국내 미디어 시각 |
| jp | 일본 트위터(X) 반응, 일본 미디어 맥락 |

- EN과 동일한 데이터/팩트를 사용하되, 독자에게 말을 거는 방식과 강조점이 달라야 한다
- 구조(포맷)는 EN과 동일하게 유지한다
- readingTime은 EN과 동일한 값을 사용한다

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
- 고정된 H2 제목 반복 사용
- Wikipedia 언급
- Yandex 언급
- 키워드와 무관한 일반적 설명
- Our Take 섹션 생략
