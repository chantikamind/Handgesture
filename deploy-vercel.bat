@echo off
REM Deployment script for Vercel
echo Deploying Hand Gesture Recognition App to Vercel...
echo.

REM Check if Vercel CLI is installed
where vercel >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing Vercel CLI globally...
    call npm install -g vercel
)

REM Initialize git if not already done
if not exist .git (
    echo Initializing git repository...
    call git init
    call git add .
    call git commit -m "Initial commit - Ready for Vercel deployment"
)

REM Deploy to Vercel
echo.
echo Starting Vercel deployment...
call vercel

echo.
echo Deployment complete!
echo.
echo Your app will be available at: https://your-project-name.vercel.app
echo Check https://vercel.com/dashboard for your deployment URL
pause
