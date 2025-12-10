# Hand Gesture Capture - Keyboard Control
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Hand Gesture Capture System" -ForegroundColor Cyan
Write-Host "  Keyboard: [t]=Save [n]=Custom [s]=Model [r]=Reset [q]=Quit" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

Write-Host "[*] Starting gesture capture..." -ForegroundColor Green
Write-Host ""

python capture_gestures.py
