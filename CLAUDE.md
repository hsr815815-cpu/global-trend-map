# Global Trend Map — Claude 자동화 지시사항

## 프로젝트 시작 시 (Startup)

이 프로젝트가 열릴 때마다 **반드시** 아래를 실행한다:

### 1. 블로그 자동화 cron 등록
매일 09:00에 블로그 포스트를 자동 생성하는 cron을 등록한다.

```
cron: "0 9 * * *"
prompt: "C:\Users\seheo\global-trend-map\scripts\blog_prompt.md 파일을 읽고 그 지시사항을 처음부터 끝까지 모두 실행해라. allowedTools는 Bash, Read, Write, WebSearch, WebFetch를 모두 사용한다."
recurring: true
```

등록 후 사용자에게 "✅ 블로그 자동화 cron 등록됨 (매일 09:00)" 메시지를 표시한다.

---

## 프로젝트 구조

- `public/data/trends.json` — 매 시간 수집되는 실시간 트렌드 데이터
- `public/data/posts-index.json` — 발행된 블로그 포스트 인덱스
- `public/blog/` — MDX 블로그 포스트
- `scripts/extract_research.py` — trends.json → research.json 변환
- `scripts/research.json` — 오늘의 블로그 주제 데이터 (임시)
- `scripts/blog_prompt.md` — 블로그 생성 전체 지시사항
- `scripts/WRITING_GUIDE.md` — SEO 글쓰기 기준
- `scripts/run_blog.ps1` — 수동 실행용 PowerShell 스크립트

## 자동화 구조

```
매일 09:00 (Claude Code cron)
  → git pull
  → python extract_research.py  (trends.json → research.json)
  → WebSearch로 키워드 실시간 리서치
  → EN 블로그 작성 (1500~2000 단어, 키워드 특정 내용)
  → 7개 언어 번역 (zh, es, pt, fr, de, kr, jp)
  → 8개 MDX 파일 저장
  → posts-index.json 업데이트
  → git commit & push
```

## 주요 규칙

- Wikipedia 언급 금지
- Yandex 언급 금지
- 유료 API 사용 금지
- 카테고리 공통 문단 금지 (키워드별 고유 내용만)
- 최근 5개 스포트라이트 중복 스킵 → 다음 순위 키워드 사용
