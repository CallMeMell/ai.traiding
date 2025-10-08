@echo off
echo ========================================
echo  Multi-Strategy Trading Bot
echo  Quick Start Script
echo ========================================
echo.

REM Prüfe ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python ist nicht installiert!
    echo Bitte installiere Python 3.8+ von python.org
    pause
    exit /b 1
)

echo [1/4] Erstelle virtuelle Umgebung...
if not exist venv (
    python -m venv venv
    echo      Virtual environment erstellt!
) else (
    echo      Virtual environment existiert bereits.
)

echo.
echo [2/4] Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat

echo.
echo [3/4] Installiere Dependencies...
pip install -r requirements.txt --quiet

echo.
echo [4/4] Erstelle Verzeichnisse...
if not exist data mkdir data
if not exist logs mkdir logs
if not exist config mkdir config

echo.
echo ========================================
echo  Setup abgeschlossen!
echo ========================================
echo.
echo Verfügbare Befehle:
echo   python main.py        - Starte Live-Trading
echo   python backtester.py  - Führe Backtest durch
echo.
echo Hinweis: Virtual environment ist aktiv.
echo Zum Deaktivieren: deactivate
echo.
pause
