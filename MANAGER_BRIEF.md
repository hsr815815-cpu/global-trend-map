# Global Trend Map — Manager Brief
> 새 Claude Code 세션에서 이 파일 하나만 읽으면 전체 맥락 파악 가능

---

## 1. 프로젝트 기본 정보

| 항목 | 값 |
|---|---|
| 프로젝트 경로 | `C:\Users\seheo\global-trend-map` |
| GitHub | https://github.com/hsr815815-cpu/global-trend-map |
| 로컬 브랜치 | `main-work` → push 시 `git push origin HEAD:main` |
| Vercel URL | https://global-trend-map-web.vercel.app |
| Vercel 프로젝트명 | `global-trend-map-web` |
| 연락처 이메일 | hsr815815@gmail.com |
| 매니저 리포트 | https://global-trend-map-web.vercel.app/report/manager-report.html |

---

## 2. 비밀값 / 토큰 / 환경변수

### GitHub Actions Secrets (레포지토리에 등록 완료)
| 시크릿명 | 용도 |
|---|---|
| `YOUTUBE_API_KEY` | YouTube Data API v3 — 트렌딩 영상 수집 |
| `GA4_PROPERTY_ID` | `529444444` — Google Analytics 4 |
| `GA4_SERVICE_ACCOUNT_JSON` | `trend-report-bot@globaltrendmap.iam.gserviceaccount.com` 서비스 계정 |
| `GSC_SITE_URL` | `https://global-trend-map-web.vercel.app` — Search Console |

### Vercel 환경변수 (대시보드에 등록 완료)
| 변수명 | 값 | 용도 |
|---|---|---|
| `GITHUB_PAT` | Vercel 대시보드 → global-trend-map-web → Settings → Environment Variables에서 확인 | cron-job.org → GitHub Actions 트리거 |
| `CRON_SECRET` | `trendpulse2026` | `/api/trigger-collect` 인증 |

---

## 3. 외부 서비스 연동

### cron-job.org
- 작업명: **"TrendPulse Collect"**
- 동작: 매 시간 → `POST https://global-trend-map-web.vercel.app/api/trigger-collect`
- 헤더: `x-cron-secret: trendpulse2026`
- 이 요청이 GitHub API를 통해 `collect-data.yml` 워크플로우를 트리거함
- GitHub Actions schedule은 백업용 (신뢰도 낮아 cron-job.org가 주 트리거)

### Vercel
- GitHub main 브랜치 push 시 자동 배포
- CLI 배포: `export PATH="/c/Program Files/nodejs:$PATH" && "C:/Users/seheo/AppData/Roaming/npm/vercel.cmd" deploy --prod --yes`

### UptimeRobot
- 5분 간격 모니터링 등록 완료 (100% uptime 목표)

---

## 4. 자동화 파이프라인 전체 구조

```
[데이터 수집 — 매 시간]
cron-job.org → POST /api/trigger-collect (CRON_SECRET 인증)
  → GitHub API workflow_dispatch
    → collect-data.yml (ubuntu-latest)
      → python scripts/collect_trends.py
        → public/data/trends.json (36개국 실시간 트렌드)
        → public/sitemap.xml
        → public/rss.xml
      → git commit & push to main

[블로그 생성 — 매일 09:00 KST]
Claude Code cron (session-only, 세션 유지 필수)
  → git pull origin main
  → python scripts/extract_research.py
      → scripts/research.json (오늘의 키워드 선정)
  → WebSearch로 키워드 실시간 리서치
  → EN 블로그 작성 (1,400~1,800단어, Format A~E 선택)
  → 7개 언어 현지화 재작성 (zh/es/pt/fr/de/kr/jp)
  → 8개 MDX 파일 → public/blog/
  → posts-index.json 업데이트
  → git commit & push
  → daily_report.html 생성 + 브라우저 오픈

[매니저 리포트 — 매일 10:30 KST]
generate-report.yml → python scripts/generate_report.py
  → GA4 Reporting API + Search Console API
  → public/report/manager-report.html → git push

[주간 유지보수 — 매주 일요일 11:00 KST]
maintenance.yml:
  - archive 30일 초과 파일 정리
  - 깨진 링크 검사
  - 경쟁사 벤치마크
  - npm/pip 보안 감사
```

---

## 5. GitHub Actions 워크플로우

| 파일 | 스케줄 | 역할 |
|---|---|---|
| `collect-data.yml` | cron-job.org 매 시간 | trends.json + sitemap + rss 수집 |
| `generate-report.yml` | 매일 01:30 UTC | 매니저 리포트 생성 |
| `maintenance.yml` | 매주 일요일 02:00 UTC | 정리 + 검사 + 감사 |

---

## 6. 블로그 자동화 상세

### 키워드 선정 로직 (`scripts/extract_research.py`)
1. `trends.json` 에서 모든 키워드를 temperature 순으로 랭킹
2. `posts-index.json`의 `recentSpotlights` 최근 5개와 비교 (정규화된 소문자 비교)
3. 중복 없는 최고 순위 키워드 선택 → `scripts/research.json` 저장

### 블로그 작성 규칙 (`scripts/WRITING_GUIDE.md`, `scripts/blog_prompt.md`)
- **포맷 5종** — 매번 다른 포맷 선택:
  - A: 서사형 (아티스트 컴백, 영화)
  - B: 뉴스 브리핑형 (사건, 정치)
  - C: 데이터 심층형 (금융, 기록)
  - D: 논쟁/양면 분석형 (찬반 이슈)
  - E: Q&A 심화형 (생소한 개념)
- **Our Take 섹션 필수** — 편집팀 의견 100~200단어
- **H2 제목 매번 창작** — 템플릿 제목 금지
- **7개 언어 현지화** — 번역 아닌 재작성 (언어별 독자 관점)

### MDX 파일 경로
`public/blog/{date}-spotlight-{keyword_slug}-{lang}.mdx`

### 최근 스포트라이트 (중복 스킵용)
`public/data/posts-index.json`의 `recentSpotlights` 배열 참조 (동적으로 업데이트됨).
최근 5개 키워드를 소문자 정규화해서 비교 — 중복이면 다음 순위 키워드 선택.

---

## 7. 로컬 개발 환경

### ⚠️ 블로그 cron 세션 의존성 주의
Claude Code cron은 **session-only**다. 세션이 끊기면 다음날 09:00 자동 실행이 누락된다.
- 세션이 끊겼을 경우: 이 채팅을 열고 수동으로 `scripts/blog_prompt.md` 지시사항 실행
- 근본 해결 (권장): Windows 작업 스케줄러 + `scripts/run_blog.ps1` 등록
  - 프로그램: `powershell.exe`
  - 인수: `-ExecutionPolicy Bypass -File "C:\Users\seheo\global-trend-map\scripts\run_blog.ps1"`
  - 스케줄: 매일 09:00

### Git 작업 방식
```bash
# 항상 최신 pull 먼저 (로컬 변경사항 있을 경우 stash)
git stash && git pull origin main

# 작업 후 push (rebase 방식)
git add ... && git commit -m "..."
git fetch origin main && git rebase origin/main && git push origin HEAD:main
```

### Python 스크립트 실행
```bash
cd C:\Users\seheo\global-trend-map
python scripts/extract_research.py
```

### Vercel 수동 배포
```bash
export PATH="/c/Program Files/nodejs:$PATH"
"C:/Users/seheo/AppData/Roaming/npm/vercel.cmd" deploy --prod --yes
```

---

## 8. 기술 스택

- **프론트엔드**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **지도**: react-simple-maps (195개국)
- **데이터 파이프라인**: GitHub Actions + Python
- **데이터 소스**: Google Trends RSS (36개국), YouTube API v3, GDELT News API, Apple App Store RSS
- **분석**: GA4 Reporting API, Google Search Console API
- **호스팅**: Vercel Hobby (무료)

---

## 9. 운영 규칙 (절대 금지)

- Wikipedia 언급/링크 금지
- Yandex 언급 금지
- 유료 API 사용 금지 (사전 승인 없이)
- 카테고리 공통 문단 금지
- Our Take 섹션 생략 금지

---

## 10. 현재 상태 (2026-03-25 기준)

- 발행된 포스트: 16개 (8개 언어 × 2일)
- 최신 포스트: Body to Body (2026-03-24)
- AdSense: 미신청 (콘텐츠 축적 중, 4~6주 후 신청 예정)
- 미구현: Playwright 자동 검증, Telegram 알림, PageSpeed API

---

## 11. 세션 시작 시 해야 할 일

1. 이 파일 읽기 ✅
2. 블로그 자동화 cron 등록:
   ```
   cron: "0 9 * * *"
   prompt: "C:\Users\seheo\global-trend-map\scripts\blog_prompt.md 파일을 읽고 그 지시사항을 처음부터 끝까지 모두 실행해라. allowedTools는 Bash, Read, Write, WebSearch, WebFetch를 모두 사용한다."
   recurring: true
   ```
3. 사용자에게 "✅ 블로그 자동화 cron 등록됨 (매일 09:00)" 표시
