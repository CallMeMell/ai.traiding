@echo off
REM Start Flask Web Dashboard for Trading Bot
REM Windows Batch Script

echo ============================================================
echo Starting Trading Bot Web Dashboard...
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Error: Flask is not installed
    echo Installing Flask...
    pip install Flask
    if errorlevel 1 (
        echo Failed to install Flask
        pause
        exit /b 1
    )
)

REM Start the dashboard
echo Starting web dashboard on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python dashboard.py --web

pause
