@echo off
echo Starting PixPort Development Server...
echo =====================================

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set development environment variables
set FLASK_ENV=development
set FLASK_DEBUG=1
set SKIP_AI_MODELS=1
set DEVELOPMENT_MODE=1

REM Clear any existing Flask cache
if exist __pycache__ rmdir /s /q __pycache__
if exist app\__pycache__ rmdir /s /q app\__pycache__

echo.
echo Virtual environment activated
echo Development mode enabled
echo AI model preload skipped
echo Cache disabled
echo.

REM Start the development server
python dev_start.py

pause
