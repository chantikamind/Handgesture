@echo off
title Hand Gesture Capture - Keyboard Control
color 0A

echo.
echo ========================================
echo   Hand Gesture Capture System
echo   Keyboard: [t]=Save [n]=Custom [s]=Model [r]=Reset [q]=Quit
echo ========================================
echo.

cd /d "%~dp0"

echo [*] Starting gesture capture...
echo.

python capture_gestures.py

pause
