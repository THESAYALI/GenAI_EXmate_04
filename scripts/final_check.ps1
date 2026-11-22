# Run from the repo root:  powershell -ExecutionPolicy Bypass -File scripts\final_check.ps1 -LiveUrl "https://your-app.onrender.com"
param(
    [Parameter(Mandatory=$true)][string]$LiveUrl
)

$ok = $true

Write-Host "1) Placeholder check" -ForegroundColor Cyan
$ph = Select-String -Path README.md,docs\interview.md,docs\resume.md,PROGRESS.md -Pattern "YOUR-HF-USERNAME","\[FILL" -ErrorAction SilentlyContinue
if ($ph) { $ok = $false; $ph | ForEach-Object { Write-Host "  LEFT: $($_.Path):$($_.LineNumber)  $($_.Line.Trim())" -ForegroundColor Yellow } }
else { Write-Host "  none left" -ForegroundColor Green }

Write-Host "2) Required files" -ForegroundColor Cyan
$files = "README.md","PROGRESS.md","docs\interview.md","docs\resume.md",".github\workflows\ci.yml","render.yaml"
foreach ($f in $files) {
    if (Test-Path $f) { Write-Host "  ok       $f" -ForegroundColor Green }
    else { $ok = $false; Write-Host "  MISSING  $f" -ForegroundColor Yellow }
}

Write-Host "3) Live /health" -ForegroundColor Cyan
try {
    $r = Invoke-RestMethod -Uri ($LiveUrl.TrimEnd('/') + "/health") -TimeoutSec 90
    Write-Host "  responded: $($r | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    $ok = $false
    Write-Host "  FAILED: $($_.Exception.Message) (free tier may be waking up, try again)" -ForegroundColor Yellow
}

Write-Host "4) Git state" -ForegroundColor Cyan
git status --short
git log --oneline -n 3

if ($ok) { Write-Host "`nAll checks passed. Safe to tag final." -ForegroundColor Green }
else { Write-Host "`nFix the yellow items before tagging final." -ForegroundColor Yellow }
