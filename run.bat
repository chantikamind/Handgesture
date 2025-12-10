@echo off
title Hand Gesture Recognition - Real-Time
color 0A

echo.
echo ========================================
echo   Hand Gesture Recognition System
echo   Real-Time with Training
echo ========================================
echo.

cd /d "%~dp0"

echo [*] Checking Python installation...
python --version

echo.
echo [*] Starting Flask server...
echo [*] Open your browser at: http://localhost:5000
echo.

python app.py

pause
