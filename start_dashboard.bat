@echo off
REM Start Trading Bot Dashboard
REM ===========================

echo ======================================================================
echo   Trading Bot Dashboard Starter
echo ======================================================================
echo.

REM Check if virtual environment is activated
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python nicht gefunden!
    echo Bitte installiere Python oder aktiviere die virtuelle Umgebung.
    pause
    exit /b 1
)

REM Install Flask if not installed
pip show Flask >nul 2>&1
if %errorlevel% neq 0 (
    echo Flask wird installiert...
    pip install Flask
)

echo.
echo Starting Dashboard Server...
echo Dashboard URL: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ======================================================================
echo.

python dashboard.py

pause
