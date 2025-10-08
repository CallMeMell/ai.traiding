@echo off
echo ========================================
echo  Golden Cross Trading Bot
echo  Quick Start & Setup
echo ========================================
echo.

REM Prüfe Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python ist nicht installiert!
    pause
    exit /b 1
)

echo Was möchtest du tun?
echo.
echo [1] Erste Installation (Setup)
echo [2] Golden Cross Tests ausführen
echo [3] Paper-Trading starten (BTC)
echo [4] Paper-Trading starten (ETH)
echo [5] Backtest durchführen
echo [6] Binance-Verbindung testen
echo [7] Hilfe anzeigen
echo.
set /p choice="Deine Wahl (1-7): "

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto test
if "%choice%"=="3" goto paper_btc
if "%choice%"=="4" goto paper_eth
if "%choice%"=="5" goto backtest
if "%choice%"=="6" goto test_binance
if "%choice%"=="7" goto help

echo Ungültige Wahl!
pause
exit /b 1

:setup
echo.
echo ========================================
echo  Installation wird durchgeführt...
echo ========================================
echo.

REM Virtual Environment
if not exist venv (
    echo [1/4] Erstelle Virtual Environment...
    python -m venv venv
)

echo [2/4] Aktiviere Virtual Environment...
call venv\Scripts\activate.bat

echo [3/4] Installiere Dependencies...
pip install -r requirements_golden_cross.txt

echo [4/4] Erstelle Verzeichnisse...
if not exist data mkdir data
if not exist logs mkdir logs
if not exist config mkdir config

echo.
echo ========================================
echo  Installation abgeschlossen!
echo ========================================
echo.
echo Nächste Schritte:
echo 1. Öffne .env.example und fülle deine Binance API-Keys ein
echo 2. Benenne .env.example in .env um
echo 3. Führe Tests aus: python test_golden_cross.py
echo 4. Starte Paper-Trading: python golden_cross_bot.py --mode paper
echo.
pause
exit /b 0

:test
echo.
echo ========================================
echo  Führe Golden Cross Tests aus...
echo ========================================
echo.
call venv\Scripts\activate.bat
python test_golden_cross.py
pause
exit /b 0

:paper_btc
echo.
echo ========================================
echo  Starte Paper-Trading (BTC/USDT)
echo ========================================
echo.
call venv\Scripts\activate.bat
python golden_cross_bot.py --mode paper --symbol BTCUSDT --capital 10000
pause
exit /b 0

:paper_eth
echo.
echo ========================================
echo  Starte Paper-Trading (ETH/USDT)
echo ========================================
echo.
call venv\Scripts\activate.bat
python golden_cross_bot.py --mode paper --symbol ETHUSDT --capital 10000
pause
exit /b 0

:backtest
echo.
echo ========================================
echo  Golden Cross Backtest
echo ========================================
echo.
echo Hinweis: Du kannst auch backtester.py mit Golden Cross nutzen
echo.
call venv\Scripts\activate.bat
python backtester.py
pause
exit /b 0

:test_binance
echo.
echo ========================================
echo  Teste Binance-Verbindung
echo ========================================
echo.
call venv\Scripts\activate.bat
python -c "from binance_integration import BinanceDataProvider; provider = BinanceDataProvider(testnet=True); provider.test_connection()"
pause
exit /b 0

:help
echo.
echo ========================================
echo  GOLDEN CROSS BOT - HILFE
echo ========================================
echo.
echo DATEIEN:
echo   golden_cross_strategy.py    - Kern-Strategie
echo   golden_cross_bot.py         - Vollständiger Bot
echo   binance_integration.py      - Binance API
echo   test_golden_cross.py        - Tests
echo   GOLDEN_CROSS_GUIDE.md       - Ausführliche Doku
echo.
echo BEFEHLE:
echo   Tests:
echo     python test_golden_cross.py
echo.
echo   Paper-Trading:
echo     python golden_cross_bot.py --mode paper --symbol BTCUSDT
echo.
echo   Backtest:
echo     python backtester.py
echo.
echo DOKUMENTATION:
echo   Siehe GOLDEN_CROSS_GUIDE.md für Details!
echo.
pause
exit /b 0
