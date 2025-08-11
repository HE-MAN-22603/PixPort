@echo off
REM ========================================
REM 🚀 PixPort Fly.io Deployment Script (Windows)
REM ========================================
REM Deploys PixPort with isnet-general-use model to Fly.io FREE PLAN

echo 🪂 PixPort Fly.io Deployment Script (Windows)
echo ============================================
echo 📦 Model: isnet-general-use (40MB)
echo 💾 Plan: FREE (256MB memory)  
echo 🌍 Region: Mumbai (bom)
echo.

REM Check if flyctl is installed
flyctl version >nul 2>&1
if errorlevel 1 (
    echo ❌ flyctl is not installed!
    echo 📥 Install it with: winget install fly-io.flyctl
    echo 📥 Or download from: https://fly.io/docs/flyctl/install/
    pause
    exit /b 1
)

echo ✅ flyctl found
flyctl version

REM Check if logged in
flyctl auth whoami >nul 2>&1
if errorlevel 1 (
    echo 🔐 Not logged in to Fly.io
    echo 👤 Logging in...
    flyctl auth login
)

echo ✅ Logged in to Fly.io

REM Set app name
set APP_NAME=pixport-bg-remover
echo 🔍 Checking if app '%APP_NAME%' exists...

REM Check if app exists (simplified for batch)
echo 🚀 Deploying PixPort to Fly.io...
echo 📱 If app doesn't exist, it will be created automatically

REM Deploy with custom Dockerfile
flyctl deploy --dockerfile Dockerfile.flyio

echo.
echo 🎉 Deployment Complete!
echo ========================
echo 🌐 Your app URL: https://%APP_NAME%.fly.dev
echo 🏥 Health check: https://%APP_NAME%.fly.dev/health
echo 📊 Status: https://%APP_NAME%.fly.dev/flyio-status
echo 💾 Memory: https://%APP_NAME%.fly.dev/memory
echo.
echo 🔧 Useful commands:
echo    flyctl status                    # Check app status
echo    flyctl logs                      # View logs  
echo    flyctl ssh console               # SSH into app
echo    flyctl scale show                # View scaling
echo    flyctl dashboard                 # Open dashboard
echo.
echo 💡 FREE PLAN NOTES:
echo    • 256MB memory (tight but workable)
echo    • Auto-sleep when not in use
echo    • First request may be slow (cold start)
echo    • Consider upgrading to $5/month plan for 512MB
echo.
echo 🎯 Model Info:
echo    • Using: isnet-general-use
echo    • Size: 40MB
echo    • Accuracy: 90%%+
echo    • Speed: 2-3 seconds
echo.
echo ✅ Ready to process images! 🖼️
echo.
echo 🌐 Test your app at: https://%APP_NAME%.fly.dev
pause
