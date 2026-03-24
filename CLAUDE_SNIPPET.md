# CLAUDE_SNIPPET — 새 CLAUDE.md 상단에 붙여넣기

아래 블록을 새 프로젝트의 CLAUDE.md 파일 맨 앞에 붙여넣으면 된다.

---

```markdown
# Global Trend Map — Claude 자동화 지시사항

## ⚡ 세션 시작 시 즉시 실행

**MANAGER_BRIEF.md를 반드시 먼저 읽는다** (전체 맥락, 토큰, 파이프라인 포함).

그 다음 블로그 자동화 cron을 등록한다:

cron: "0 9 * * *"
prompt: "C:\Users\seheo\global-trend-map\scripts\blog_prompt.md 파일을 읽고 그 지시사항을 처음부터 끝까지 모두 실행해라. allowedTools는 Bash, Read, Write, WebSearch, WebFetch를 모두 사용한다."
recurring: true

등록 후 "✅ 블로그 자동화 cron 등록됨 (매일 09:00)" 표시.

---

## 핵심 정보 (요약)

- **경로**: `C:\Users\seheo\global-trend-map`
- **GitHub**: https://github.com/hsr815815-cpu/global-trend-map
- **로컬 브랜치**: `main-work` → push: `git push origin HEAD:main`
- **Vercel**: https://global-trend-map-web.vercel.app
- **CRON_SECRET**: `trendpulse2026`

## Git 작업 방식

```bash
# pull
git stash && git pull origin main

# push
git fetch origin main && git rebase origin/main && git push origin HEAD:main
```

## Vercel 수동 배포

```bash
export PATH="/c/Program Files/nodejs:$PATH"
"C:/Users/seheo/AppData/Roaming/npm/vercel.cmd" deploy --prod --yes
```

## 절대 금지

- Wikipedia / Yandex 언급 금지
- 유료 API 사전 승인 없이 사용 금지
- 블로그 Our Take 섹션 생략 금지
- 카테고리 공통 문단 사용 금지
```

---

## 붙여넣기 후 확인사항

1. `MANAGER_BRIEF.md` 파일이 프로젝트 루트에 있는지 확인
2. `scripts/blog_prompt.md` 경로가 맞는지 확인
3. 세션을 열면 Claude가 자동으로 cron을 등록하는지 확인
