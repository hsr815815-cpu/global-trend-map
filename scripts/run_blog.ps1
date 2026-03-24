# run_blog.ps1 — 매일 09:00 KST 실행
# Windows 작업 스케줄러 등록:
#   프로그램: powershell.exe
#   인수:     -ExecutionPolicy Bypass -File "C:\Users\seheo\global-trend-map\scripts\run_blog.ps1"

$REPO = "C:\Users\seheo\global-trend-map"
$LOG  = "$REPO\scripts\run_blog.log"

function Log($msg) {
    $ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss UTC")
    $line = "$ts  $msg"
    Write-Host $line
    Add-Content -Path $LOG -Value $line
}

Log "====== Blog generation started ======"
Set-Location $REPO

# 1. 최신 데이터 받기
Log "[1/4] git stash + pull..."
git stash 2>&1 | ForEach-Object { Log "  $_" }
git pull origin main 2>&1 | ForEach-Object { Log "  $_" }

# 2. research.json 생성 (Python)
Log "[2/4] extract_research.py..."
$result = python scripts/extract_research.py 2>&1
$result | ForEach-Object { Log "  $_" }

# research.json 확인
$research = Get-Content "$REPO\scripts\research.json" -Raw | ConvertFrom-Json
if ($research.status -eq "skip") {
    Log "SKIP: $($research.skip_reason)"
    Log "====== Done (skipped) ======"
    exit 0
}
Log "  Keyword: $($research.keyword) (rank #$($research.rank), $($research.temperature)T)"

# 3. Claude로 블로그 생성
Log "[3/4] claude -p blog_prompt.md..."
$prompt = Get-Content "$REPO\scripts\blog_prompt.md" -Raw
claude -p $prompt --allowedTools "Bash,Read,Write,WebSearch,WebFetch" 2>&1 | ForEach-Object { Log "  $_" }

# 4. 커밋 & 푸시
Log "[4/4] git commit & push..."
git add public/blog/ public/data/posts-index.json
git diff --staged --quiet
if ($LASTEXITCODE -ne 0) {
    $date = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd")
    git commit -m "Auto: Blog post - $($research.keyword) ($date)"
    git fetch origin main 2>&1 | ForEach-Object { Log "  $_" }
    git rebase origin/main 2>&1 | ForEach-Object { Log "  $_" }
    git push origin HEAD:main 2>&1 | ForEach-Object { Log "  $_" }
    Log "====== Done. Posts published. ======"
} else {
    Log "====== Done (nothing to commit). ======"
}
