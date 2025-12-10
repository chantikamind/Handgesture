# Hand Gesture Recognition - Real-Time Training
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Hand Gesture Recognition System" -ForegroundColor Cyan
Write-Host "  Real-Time with Training" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

Write-Host "[*] Checking Python installation..." -ForegroundColor Yellow
python --version

Write-Host ""
Write-Host "[*] Starting Flask server..." -ForegroundColor Green
Write-Host "[*] Open your browser at: http://localhost:5000" -ForegroundColor Green
Write-Host ""

python app.py
