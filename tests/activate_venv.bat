@echo off
echo Activating PixPort virtual environment...
call venv\Scripts\activate.bat
echo.
echo PixPort virtual environment activated!
echo You can now run:
echo   python main.py          - Start the Flask server
echo   python download_models.py - Download AI models
echo.
cmd /k
