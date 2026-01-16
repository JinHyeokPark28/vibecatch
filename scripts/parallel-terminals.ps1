#
# 🚀 Claude Code 병렬 터미널 (Windows Terminal)
#
# 사용법: .\scripts\parallel-terminals.ps1
#
# Windows Terminal에 5개 탭이 생성됩니다.

$ProjectDir = Get-Location
$ProjectName = Split-Path -Leaf $ProjectDir

Write-Host "🚀 Claude Code 병렬 터미널 시작" -ForegroundColor Blue
Write-Host "프로젝트: $ProjectDir" -ForegroundColor Yellow
Write-Host ""

# Windows Terminal 설치 확인
if (-not (Get-Command wt -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Windows Terminal이 설치되어 있지 않습니다." -ForegroundColor Red
    Write-Host ""
    Write-Host "설치 방법:"
    Write-Host "  winget install Microsoft.WindowsTerminal"
    exit 1
}

Write-Host "✅ 5개 탭 생성 중..." -ForegroundColor Green

# Windows Terminal로 5개 탭 열기
wt -w 0 `
    new-tab --title "1-Main" -d $ProjectDir `; `
    new-tab --title "2-Test" -d $ProjectDir `; `
    new-tab --title "3-Refactor" -d $ProjectDir `; `
    new-tab --title "4-Docs" -d $ProjectDir `; `
    new-tab --title "5-Review" -d $ProjectDir

Write-Host ""
Write-Host "✅ 5개 탭 생성 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "Windows Terminal 단축키:" -ForegroundColor Blue
Write-Host "  Ctrl+Tab        다음 탭"
Write-Host "  Ctrl+Shift+Tab  이전 탭"
Write-Host "  Ctrl+Alt+1-5    탭 직접 이동"
Write-Host "  Ctrl+Shift+W    탭 닫기"
