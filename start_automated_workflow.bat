@echo off
REM start_automated_workflow.bat - Start Automated Workflow System
REM ================================================================

echo.
echo ======================================================================
echo   AUTOMATED TRADING BOT WORKFLOW
echo ======================================================================
echo   Preparing AI trading bot for real money deployment
echo ======================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import pandas, numpy, flask" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some dependencies missing. Installing...
    pip install -r requirements.txt
)

echo.
echo Starting automated workflow...
echo.

REM Start the workflow
python automated_workflow.py

echo.
echo ======================================================================
echo   Workflow execution completed
echo ======================================================================
echo.

pause
