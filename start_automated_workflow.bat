@echo off
REM start_automated_workflow.bat - Quick Start für Automatisierten Workflow (Windows)
REM ==================================================================================

echo ==============================================================================
echo 🤖 AUTOMATISIERTER TRADING-BOT WORKFLOW
echo ==============================================================================
echo.
echo Dieses Skript startet den vollautomatischen Workflow zur Vorbereitung
echo des KI-Trading-Bots für den Echtgeld-Einsatz.
echo.
echo Workflow-Phasen:
echo   1. Datenanalyse und -kreierung
echo   2. Strategie-Optimierung
echo   3. API-Vorbereitung
echo   4. Live-View Session Integration
echo   5. Finale Validierung
echo.
echo ==============================================================================
echo.

REM Prüfe ob Python verfügbar ist
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nicht gefunden. Bitte installiere Python 3.9+.
    pause
    exit /b 1
)

REM Erstelle notwendige Verzeichnisse
if not exist data\workflow_sessions mkdir data\workflow_sessions
if not exist logs mkdir logs

REM Starte Workflow
echo.
echo 🚀 Starte Automatisierten Workflow...
echo.

python demo_automated_workflow.py

echo.
echo ==============================================================================
echo ✅ Workflow-Skript beendet
echo ==============================================================================
echo.
echo 📁 Session-Dateien: data\workflow_sessions\
echo 📝 Log-Dateien: logs\trading_bot.log
echo.
echo Weitere Informationen: AUTOMATED_WORKFLOW_GUIDE.md
echo.

pause
