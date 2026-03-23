# run_blog.ps1 — 매일 09:00 KST 실행
# Windows 작업 스케줄러에 등록: powershell -File "C:\Users\seheo\global-trend-map\scripts\run_blog.ps1"

$REPO = "C:\Users\seheo\global-trend-map"
$LOG  = "$REPO\scripts\run_blog.log"

function Log($msg) {
    $ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss")
    "$ts $msg" | Tee-Object -FilePath $LOG -Append
}

Log "=== Blog generation started ==="

Set-Location $REPO

# 최신 데이터 받기
Log "git pull..."
git pull origin main 2>&1 | ForEach-Object { Log $_ }

# Claude Code로 블로그 생성
Log "Running claude -p..."
$prompt = Get-Content "$REPO\scripts\blog_prompt.md" -Raw
claude -p $prompt --allowedTools "Read,Write" 2>&1 | ForEach-Object { Log $_ }

# 변경사항 커밋 & 푸시
Log "Committing..."
git add public/blog/ public/data/posts-index.json
$status = git diff --staged --quiet; $changed = -not $?

if ($changed) {
    $date = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd")
    git commit -m "Auto: Generate blog posts $date"
    git push origin HEAD:main 2>&1 | ForEach-Object { Log $_ }
    Log "=== Done. Posts pushed. ==="
} else {
    Log "=== No new posts (skipped or already exists). ==="
}
