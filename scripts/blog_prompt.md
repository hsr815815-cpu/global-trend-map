# 블로그 포스트 자동 생성

## 작업 순서

### 1단계: 데이터 확인
`public/data/trends.json`을 읽어라.
- `global.topTrend`에서 오늘의 스포트라이트 키워드를 추출한다
- 키워드, 카테고리, 진원국, 검색량, 트렌드 온도, youtubeId 확인
- `countries` 데이터에서 이 키워드가 트렌딩 중인 국가 목록 추출
- `global.risingFast`에서 상위 5개 추출
- `global.categoryBreakdown` 추출

### 2단계: 중복 체크
`public/data/posts-index.json`을 읽어라.
- `recentSpotlights` 배열에서 오늘 기준 최근 3일 이내 날짜인 항목 확인
- 같은 키워드가 있으면 **작업 중단** (이미 발행된 글)
- 없으면 계속 진행

### 3단계: 글쓰기 기준 확인
`scripts/WRITING_GUIDE.md`를 읽어라.
이 기준에 따라 글을 작성한다.

### 4단계: 내부링크 후보 확인
`public/data/posts-index.json`의 `posts` 배열에서
language가 "en"인 최근 5개 포스트의 slug를 추출한다.
내부링크 URL 형식: `https://global-trend-map-web.vercel.app/blog/{slug}`

### 5단계: 블로그 포스트 작성
WRITING_GUIDE.md 기준에 따라 **8개 언어 MDX 파일**을 작성한다.

각 파일 저장 경로:
`public/blog/{YYYY-MM-DD}-spotlight-{keyword-slug}-{lang}.mdx`

오늘 날짜: 파일 작성 시점의 UTC 날짜 사용

**중요:**
- 섹션 3 (Why Trending)은 이 키워드에 대한 실제 분석을 작성한다
- 카테고리 공통 문단 절대 금지
- EN 기준 readingTime을 계산해 8개 언어 모두 동일하게 적용
- 각 언어로 자연스럽게 작성 (기계 번역 말투 금지)

### 6단계: posts-index.json 업데이트
`public/data/posts-index.json`을 업데이트한다.

`posts` 배열 앞에 8개 언어 항목 추가:
```json
{
  "slug": "{slug}",
  "title": "{제목}",
  "date": "{YYYY-MM-DD}",
  "lastUpdated": "{ISO timestamp}",
  "excerpt": "{excerpt}",
  "category": "{category}",
  "language": "{lang}",
  "readingTime": {EN과 동일한 숫자},
  "featured": true,
  "tags": ["{keyword-slug}", "{category}", "global-trends", "trending"]
}
```

`recentSpotlights` 배열 앞에 추가:
```json
{"keyword": "{키워드 소문자}", "date": "{YYYY-MM-DD}"}
```

3일 이전 항목은 제거한다.
