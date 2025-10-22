# 🎯 Multi-Strategy Trading Bot - Master Version

**Professional Trading Bot mit Multi-Strategy Orchestrierung**

Diese Master-Version konsolidiert die besten Features aus vier Evolutionsstufen in eine produktionsreife, modulare Anwendung.

## 🧪 Test Coverage

**Sprint 0: Test Coverage Excellence - Completed!** ✅

| Module | Coverage | Status |
|--------|----------|--------|
| **Combined Critical Modules** | **80%** | ✅ Target reached! |
| utils.py | 82% | ✅ Excellent |
| binance_integration.py | 78% | ✅ Good |
| broker_api.py | 78% | ✅ Good |

📊 **175 Tests** | [View Detailed Report](TEST_COVERAGE_REPORT.md) | [Sprint 0 Validation](SPRINT_0_COVERAGE_VALIDATION.md) | [Run Coverage Check](scripts/check_coverage.ps1)

## 🔥 Now with Binance API Integration!

The bot now uses **Binance API** as the primary trading platform:
- ✅ **24/7 Cryptocurrency Trading**
- ✅ **Testnet Support** for risk-free paper trading
- ✅ **Low Fees** and high liquidity
- ✅ **1000+ Trading Pairs**
- ✅ **Production-Ready** with comprehensive error handling

📖 **[Read the Binance Migration Guide](BINANCE_MIGRATION_GUIDE.md)** for detailed setup instructions.

---

## 🎉 NEW: Stable CI/CD Pipeline! (Oktober 2025)

The project now has a **production-ready CI/CD infrastructure**:
- ✅ **Windows & Ubuntu** - Cross-platform testing
- ✅ **Python 3.10, 3.11, 3.12** - Multi-version support
- ✅ **Matrix Testing** - 6 combinations (2 OS × 3 Python)
- ✅ **100% Success Rate** - All tests passing
- ✅ **61 Test Files** - Comprehensive test coverage
- ✅ **Best Practices** - Documented and established

📖 **[Read the CI Success Summary](CI_SUCCESS_AND_NEXT_STEPS.md)** | **[Development Plan](POST_CI_DEVELOPMENT_PLAN.md)** | **[Feature Roadmap 2025](FEATURE_ROADMAP_2025.md)**

---

## 📁 Dateistruktur

```
MASTER_VERSION/
│
├── config.py              # Zentrale Konfigurationsverwaltung
├── strategy.py            # Trading-Strategien & Strategy Manager
├── utils.py               # Logging, Validierung, Hilfsfunktionen
├── main.py               # Live-Trading Hauptprogramm
├── backtester.py         # Backtesting Engine
├── dashboard.py          # Visual Dashboard & Charts
├── dashboard_demo.py     # Dashboard Demo-Anwendung
├── requirements.txt      # Python-Abhängigkeiten
│
├── data/                 # Datenverzeichnis (automatisch erstellt)
│   ├── trades.csv        # Trade-History
│   ├── dashboard.html    # Exportiertes Dashboard
│   ├── dashboard_config.json  # Dashboard-Konfiguration
│   ├── backtest_results.csv  # Backtest-Ergebnisse
│   └── charts/           # Generierte Diagramme
│
├── logs/                 # Log-Verzeichnis (automatisch erstellt)
│   └── trading_bot.log   # Vollständiges Log
│
└── config/               # Config-Verzeichnis (optional)
    └── trading_config.json  # Gespeicherte Konfiguration
```

---

## 🎯 Kern-Features

### ✅ Binance API Integration
- **Primary Trading Platform**: Binance (Cryptocurrency)
- **Testnet Support**: Risk-free paper trading
- **24/7 Trading**: Crypto markets never close
- **Real-time Data**: Live price feeds and historical data
- **Order Execution**: Market and limit orders
- **Legacy Support**: Alpaca API still available

### ✅ Multi-Strategy System
- **6+ professionelle Strategien:**
  - **MA Crossover**: Trend-Following mit Moving Averages (mittel- bis langfristig)
  - **RSI Mean Reversion**: Überverkauft/Überkauft Strategie (Seitwärtsmärkte)
  - **Bollinger Bands**: Volatilitäts-Breakout Strategie
  - **EMA Crossover**: Schnelle Trend-Strategie für Daytrading
  - **LSOB (Long-Short On Breakout)**: Advanced volatility breakout strategy
  - **Video-Based Strategy**: Enhanced base framework for implementing strategies from tutorials/videos

### ✅ Signal-Aggregation
- **AND Logic**: Konservativ - Alle Strategien müssen zustimmen
- **OR Logic**: Aggressiv - Mindestens eine Strategie reicht

### ✅ Backtesting Engine
- Historische Datenanalyse
- Detaillierte Performance-Metriken
- Win Rate, ROI, Profit Factor, etc.

### ✅ Automatische Strategie-Auswahl 🆕
- **Intelligente Optimierung**: Analysiert alle Strategien mittels Backtest und wählt automatisch die beste
- **Multi-Kriterien-Bewertung**: ROI, Sharpe Ratio, Calmar Ratio, Drawdown, Win Rate
- **Automatische Konfiguration**: Beste Strategie wird direkt in Live-Config gesetzt
- **Vollständig dokumentiert**: Logs und CSV-Export für Nachvollziehbarkeit
- **Flexible Integration**: Standalone-Script oder Teil des Setup-Wizards
- **CI/CD Ready**: Quiet Mode für Automatisierung und Cron-Jobs

📖 **[Read the Auto Strategy Selection Guide](AUTO_STRATEGY_SELECTION_GUIDE.md)** für vollständige Dokumentation und Beispiele.

### ✅ Robuste Architektur
- **Modular & OOP**: Saubere Klassenstruktur
- **Zentrales Logging**: Rotating File Handler
- **Fehlerbehandlung**: Try-Except in allen kritischen Bereichen
- **Datenvalidierung**: OHLCV-Validierung vor Verarbeitung

### ✅ Konfigurationsmanagement
- Zentrale `config.py` für alle Parameter
- Unterstützung für Umgebungsvariablen (.env)
- JSON Import/Export für Konfigurationen

### ✅ Visual Dashboard
- **Interaktive Metriken**: Total P&L, Win Rate, ROI, etc.
- **Modal-Fenster**: Metriken und Diagramme hinzufügen/entfernen
- **Mehrere Diagrammtypen**: Line, Bar, Pie Charts
- **Echtzeitdaten**: Integration mit Binance API (or simulation mode)
- **Export-Funktionen**: HTML, PNG (Matplotlib), HTML (Plotly)
- **Persistente Konfiguration**: Browser-Cache/Database Storage

### ✅ View Session Feature 🆕
- **Session Management**: View and analyze all past trading sessions
- **Performance Analytics**: Comprehensive metrics for each session (P&L, win rate, trades)
- **Interactive Charts**: Visualize trade execution prices and patterns with Chart.js
- **Search & Filter**: Real-time search and filter by profitability
- **Session Details**: Drill down into individual sessions to see complete execution history
- **Export Functionality**: Export session data to CSV for further analysis
- **Responsive UI**: Modern, mobile-friendly interface with dark mode support

📖 **[Read the View Session Guide](VIEW_SESSION_GUIDE.md)** for complete documentation.

### ✅ Live Market Monitoring 🆕
- **Real-time Monitoring**: Track multiple trading pairs simultaneously
- **Strategy Integration**: Automated signal detection with existing strategies
- **Smart Alerts**: Price changes, volume spikes, and trade signals
- **Multi-Exchange Support**: Primary support for Binance, extensible for others
- **Customizable**: Configure thresholds, intervals, and alert priorities
- **Alert Callbacks**: Integrate with Telegram, Slack, email, or custom notifications

📖 **[Read the Live Market Monitor Guide](LIVE_MARKET_MONITOR_GUIDE.md)** for complete documentation.

### ✅ Simulated Live-Trading Environment 🆕
- **Realistic Simulation**: Test strategies with near real-time conditions without risking real money
- **Order Execution Delays**: Simulates 50-200ms delays typical of real exchanges
- **Price Slippage**: 0.01-0.1% slippage based on order size and market volatility
- **Transaction Fees**: Maker/taker fee model (0.075% default)
- **Market Impact**: Larger orders experience higher slippage
- **Comprehensive Metrics**: Sharpe ratio, drawdown, P&L, fees, slippage tracking
- **Live Data Integration**: Can use real market data or simulated price feeds
- **Session Logging**: Export complete trading session logs with execution details

📖 **[Quick Start Guide](QUICK_START_SIMULATED_TRADING.md)** | **[Full Documentation](SIMULATED_LIVE_TRADING_GUIDE.md)**

### ✅ Automatisierter Workflow (NEU) 🆕
- **Phasenbasierte Automatisierung**: Strukturierte Abfolge für Daten-, Strategie- und API-Phasen
- **Zeitlimits**: Konfigurierbare Timeouts pro Phase (Standard: 2h für Daten/Strategie, 1h für API)
- **Automatische Pausen**: Selbstprüfung zwischen Phasen ohne manuelle Bestätigung
- **Fehlerbehandlung**: Retry-Mechanismus mit Backoff bei transienten Fehlern
- **Live-Monitoring**: Heartbeat und Metriken werden in Session-Events geschrieben
- **API-Sicherheit**: Sichere Verwaltung von API-Keys aus Umgebungsvariablen

### ✅ Daten-Lifecycle & Aufräumen 🆕
- **Log-Rotation**: Automatische Archivierung alter Log-Dateien mit Kompression
- **PII-Maskierung**: Schutz sensibler Daten (E-Mails, API-Keys, Passwörter, Telefonnummern)
- **Integritätsprüfung**: Checksum-basierte Verifizierung aller Archive

### ✅ Enhanced Base Strategy Framework 🆕
- **Video-Based Strategy Support**: Framework zum Implementieren von Strategien aus YouTube-Videos und Tutorials
- **Multi-Timeframe Analysis**: Unterstützung für mehrere Zeitrahmen-Datenfeeds
- **State Management**: Persistente Zustandsspeicherung und -wiederherstellung
- **Performance Tracking**: Automatische Metriken für Execution Time, Signale, Win Rate
- **Position Lifecycle**: Callbacks für Position-Events (Öffnen/Schließen)
- **Confidence Scoring**: Bewertung der Signal-Qualität (0-1)
- **Exchange Connection Utilities**: Vorbereitung für erweiterte Exchange-Integration

📖 **[Read the Base Strategy Guide](docs/BASE_STRATEGY_GUIDE.md)** für vollständige Dokumentation und Implementierungsbeispiele.
- **Konfigurierbare Retention**: Anpassbare Aufbewahrungsfristen (Standard: 30 Tage)
- **Automatische Kompression**: Gzip-Kompression für Platzersparnis
- **Metadata-Tracking**: Vollständige Nachverfolgbarkeit archivierter Dateien

```python
from automation.data_lifecycle import rotate_logs, mask_pii, check_archive

# Log-Rotation durchführen
result = rotate_logs()
print(f"Archiviert: {result['archived_count']} Dateien")

# Sensible Daten maskieren
data = {"user": "Max Mustermann", "email": "max@example.com"}
masked = mask_pii(data)
# Ausgabe: {"user": "Ma**********nn", "email": "ma***********om"}

# Archive-Integrität prüfen
integrity_ok = check_archive()
assert integrity_ok is True
```

### ✅ Core Features - Production Ready 🆕
- **Circuit Breaker**: Dynamische Drawdown-Limits mit automatischem Trading-Stopp (13/13 tests ✅)
- **Kelly Criterion**: Optimale Positionsgrößenberechnung basierend auf historischer Performance (16/16 tests ✅)
- **Multi-Channel Alerts**: Telegram & Email Benachrichtigungen für Trades, Fehler und Performance (18/18 tests ✅)
- **Database Integration**: Automatische Trade-Historie mit SQLite (13/13 tests ✅)
- **Trailing Stop**: Dynamische Stop-Loss-Anpassung zum Gewinnschutz ✅
- **Monitoring & Alerting**: Flexible Schwellenwerte und Custom Events ✅
- **100% Test Coverage**: 102/102 Tests passing - Production ready! ✅

📖 **[Core Features Verification Report](CORE_FEATURES_OPTIMIZATION_VERIFICATION.md)** - Vollständige Dokumentation aller Core Features mit Tests und Beispielen.  
📖 **[Issue #182 Resolution Summary](ISSUE_182_RESOLUTION_SUMMARY.md)** - Executive Summary der Feature-Verifizierung.

### ✅ View Session Dashboard (NEU) 🆕
- **Echtzeit-Visualisierung**: Streamlit-basiertes Dashboard mit Plotly-Charts
- **PnL/Equity Curve**: Liniendiagramm für Gewinn-/Verlustentwicklung
- **Wins/Losses**: Balkendiagramm nach Zeitfenster
- **Flexible Filter**: Zeitbereich (letzte N Stunden/Tage, benutzerdefiniert) und Strategy-Tags
- **URL-Persistenz**: Filterzustand wird in URL gespeichert
- **Auto-Refresh**: Live-Updates alle paar Sekunden
- **Null-Risiko**: Komplett entkoppelt von Trading-Logik

### ✅ Live-Überwachung (View Session) 🆕
Full live observability of automation runner execution with structured events and real-time monitoring:

#### **Activity Feed** 📰
- Latest 100 events with timestamps, types, phases, and messages
- Emoji indicators for different event types (🚀 phase start, 🏁 phase end, ✅ checkpoint pass, 💓 heartbeat)
- Real-time updates with automatic refresh
- Color-coded by level (info, warning, error)

#### **Current Status Panel** 📡
- **Current Phase**: Shows which phase is currently executing
- **Session Uptime**: Total runtime since session start
- **Last Heartbeat**: Time since last heartbeat event (helps detect if runner is stuck)
- **Session Status**: Overall status (running, success, failed)

#### **Performance Metrics** 📊
- Real-time KPIs: Equity, P&L, Win Rate
- Trade statistics: Total trades, wins, losses
- ROI and progress tracking

#### **Filters & Controls** 🔍
- **Timeframe Presets**: 15min, 1h, 4h, Today, All, Custom
- **Phase Filter**: Filter by specific phases (data, strategy, api)
- **Event Type Filter**: Filter by event types (runner_start, phase_start, checkpoint, heartbeat, etc.)
- **Manual Refresh Button**: Force immediate data refresh
- **Auto-refresh Toggle**: Enable/disable automatic updates (every 10s)

#### **Starten**
```bash
# Start the automation runner (generates events)
python automation/runner.py

# In a separate terminal, start the View Session dashboard
streamlit run tools/view_session_app.py
```

#### **Via VS Code Tasks**
Add to `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "View Session Dashboard",
      "type": "shell",
      "command": "streamlit run tools/view_session_app.py",
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Run Automation",
      "type": "shell",
      "command": "python automation/runner.py",
      "problemMatcher": []
    }
  ]
}
```

Then press `Ctrl+Shift+P` → "Tasks: Run Task" → select "View Session Dashboard" or "Run Automation".

---

## 🎯 Ein-Klick Dev Live Session (NEU) 🆕

**Automatisierter One-Click-Workflow für lokales Dev-Setup und Monitoring!**

Starte den kompletten Dev-Workflow mit nur einem Klick: Automation Runner (Dry-Run) + Streamlit View Session laufen parallel, Port 8501 wird automatisch weitergeleitet.

### ✨ Features

- ✅ **Ein-Klick-Start**: Task "Dev: Live Session" startet beide Prozesse parallel
- ✅ **Automatisches Setup**: venv wird angelegt, Dependencies installiert (idempotent)
- ✅ **Keine Secrets nötig**: DRY_RUN=true ist Standard
- ✅ **Port-Weiterleitung**: Port 8501 öffnet automatisch Preview
- ✅ **Cross-Platform**: Windows, macOS, Linux, Codespaces
- ✅ **Reproduzierbar**: Funktioniert immer, ohne Datenbeschädigung

---

## 🚀 QUICKSTART - Windows (PowerShell) ⭐

**🎯 Ziel: Live-Session mit einem Befehl starten - Windows-optimiert!**

### ⚡ Schnellstart für Windows (3 Schritte)

**1️⃣ Repository klonen:**
```powershell
git clone https://github.com/CallMeMell/ai.traiding.git
cd ai.traiding
```

**2️⃣ Optional: .env Datei erstellen (für eigene Konfiguration):**
```powershell
# Kopiere die Beispiel-Datei
Copy-Item .env.example .env

# Bearbeite .env nach Bedarf (Standard: DRY_RUN=true)
```

**3️⃣ Live-Session starten:**

**Windows PowerShell:**
```powershell
.\scripts\start_live.ps1
```

**💡 Tipp: Bei ExecutionPolicy-Fehler**
Falls PowerShell die Skript-Ausführung blockiert, verwende den Wrapper:
```powershell
.\scripts\set-executionpolicy.ps1
```

Oder setze die Policy manuell:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\start_live.ps1
```

### ⚡ Schnellstart für Linux/macOS

**Live-Session starten:**
```bash
./scripts/start_live.sh
```

**Das war's!** 🎉 Die Skripte machen alles automatisch:
- ✅ Virtual Environment anlegen
- ✅ Dependencies installieren
- ✅ Automation Runner starten (DRY_RUN Modus)
- ✅ Streamlit Dashboard starten (http://localhost:8501)

Nach dem Start öffne deinen Browser: **http://localhost:8501**

---

### 🎯 Automatische Strategie-Auswahl (Bonus)

Finde automatisch die beste Strategie für maximalen ROI:

**Windows:**
```powershell
# Vollautomatisch - wählt beste Strategie und aktualisiert Config
.\scripts\auto_select_strategy.ps1

# Mit benutzerdefinierten Parametern
.\scripts\auto_select_strategy.ps1 --min-trades 15 --initial-capital 50000
```

**Linux/macOS:**
```bash
python scripts/auto_select_strategy.py
```

**Ergebnis**: Die beste Strategie wird automatisch in `config/live_risk.yaml` gesetzt! 🏆

📖 Siehe **[AUTO_STRATEGY_SELECTION_GUIDE.md](AUTO_STRATEGY_SELECTION_GUIDE.md)** für Details.

---

### 🚀 Schnellstart - VS Code (Alternative)

**Option 1: Über Command Palette (empfohlen)**
1. Drücke `Ctrl+Shift+P` (Windows/Linux) oder `Cmd+Shift+P` (macOS)
2. Tippe "Tasks: Run Task"
3. Wähle **"Dev: Live Session"**
4. Beide Prozesse starten automatisch
5. Port 8501 öffnet sich automatisch mit View Session Dashboard

**Option 2: Über Terminal**
```bash
# Run the "Dev: Live Session" task
# In VS Code Terminal → Run Task → Dev: Live Session
```

### 🛠️ Manuelle Installation (einmalig)

Falls du die Dependencies manuell installieren möchtest:

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install streamlit plotly pandas requests python-dotenv pydantic jsonschema

# Windows
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install streamlit plotly pandas requests python-dotenv pydantic jsonschema
```

Aber das ist **nicht nötig** - der Task "Install Dev Deps" macht das automatisch!

### 📋 Verfügbare VS Code Tasks

- **Install Dev Deps**: Erstellt venv und installiert alle Dependencies
- **Run: Automation Runner (Dry-Run)**: Startet Runner im DRY_RUN-Modus (keine API-Keys)
- **Run: View Session (Streamlit)**: Startet Streamlit Dashboard auf Port 8501
- **Dev: Live Session**: ⭐ Startet beide Prozesse parallel (empfohlen)
- **Stop: All Sessions**: Stoppt alle laufenden Streamlit-Prozesse

### 🖥️ Außerhalb von VS Code (Shell-Skripte)

**Schnellstart mit einem Befehl:**

**Linux/macOS:**
```bash
./scripts/start_live.sh
```

**Windows PowerShell:**
```powershell
.\scripts\start_live.ps1
```

**Was die Skripte machen:**
1. ✅ venv anlegen (falls nicht vorhanden)
2. ✅ Dependencies automatisch installieren
3. ✅ `.env` Datei laden (falls vorhanden)
4. ✅ Automation Runner starten (mit DRY_RUN Einstellungen)
5. ✅ Streamlit View Session starten (Port 8501)
6. ✅ Beide Prozesse laufen parallel, Ctrl+C stoppt alle

**⚙️ Konfiguration über .env Datei:**

Die Skripte respektieren deine `.env` Datei. Erstelle eine `.env` Datei im Projekt-Root:

```bash
# .env - Beispielkonfiguration
DRY_RUN=true                                    # false für echtes Trading
BROKER_NAME=binance
BINANCE_BASE_URL=https://testnet.binance.vision

# Optional: API-Keys für echtes Trading (nur wenn DRY_RUN=false)
# BINANCE_API_KEY=your_api_key
# BINANCE_SECRET_KEY=your_secret_key
```

**Standard-Werte (wenn keine .env existiert):**
- `DRY_RUN=true` (sicherer Modus ohne echte API-Calls)
- `BROKER_NAME=binance`
- `BINANCE_BASE_URL=https://testnet.binance.vision`

Du kannst auch die `.env.example` als Vorlage kopieren:
```bash
cp .env.example .env
```

### 🌐 Zugriff auf View Session

Nach dem Start ist das Dashboard erreichbar unter:
- **Lokal**: http://localhost:8501
- **Codespaces/Remote**: Port 8501 wird automatisch weitergeleitet
- **Preview**: Öffnet sich automatisch in VS Code

### 🔍 Was passiert im DRY_RUN-Modus?

- ✅ Keine echten API-Calls zu Binance/Alpaca
- ✅ Simulierte Daten für Demo
- ✅ Events werden generiert und gespeichert
- ✅ View Session zeigt Live-Updates
- ✅ Perfekt zum Testen und Entwickeln

### 🐛 Troubleshooting

#### Windows-Spezifisch

**Problem: "ExecutionPolicy" - Skript kann nicht ausgeführt werden**

**Einfachste Lösung:** Verwende den Wrapper-Skript:
```powershell
.\scripts\set-executionpolicy.ps1
```

**Alternative Lösungen:**
```powershell
# Temporär für aktuelle PowerShell-Session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Oder dauerhaft für aktuellen Benutzer
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

📖 **Weitere Informationen:** Siehe [POWERSHELL_DEVELOPMENT.md](POWERSHELL_DEVELOPMENT.md) für Details zum Wrapper-Skript.

**Problem: "Python not found" (Windows)**
```powershell
# Installiere Python von python.org (3.8 oder höher)
# Stelle sicher, dass "Add Python to PATH" aktiviert ist
# Nach Installation PowerShell neu starten

# Prüfen ob Python verfügbar ist:
python --version
```

**Problem: "Port 8501 already in use" (Windows)**
```powershell
# Stoppe alte Streamlit-Prozesse
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *streamlit*"
# Oder:
taskkill /F /IM streamlit.exe

# Oder nutze den VS Code Task "Stop: All Sessions"
```

**Problem: "python-dotenv not found" (Windows)**
```powershell
# Installiere python-dotenv im venv
.\venv\Scripts\python.exe -m pip install python-dotenv
```

#### Allgemein (alle Plattformen)

**Problem: "Python not found" (Linux/macOS)**
```bash
# Ubuntu/Debian:
sudo apt update && sudo apt install python3 python3-venv python3-pip

# macOS (mit Homebrew):
brew install python3
```

**Problem: "Port 8501 already in use" (Linux/macOS)**
```bash
# Stoppe alte Streamlit-Prozesse
pkill -f streamlit

# Oder nutze den VS Code Task "Stop: All Sessions"
```

**Problem: "No module named 'core'"**
```bash
# Stelle sicher, dass du im Projekt-Root bist
cd /pfad/zu/ai.traiding

# Python path setzen (falls nötig)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
$env:PYTHONPATH = "$(pwd)"                # Windows PowerShell
```

**Problem: View Session zeigt "No data available"**
- ✅ Der Automation Runner muss zuerst laufen und Events generieren
- ✅ Warte 5-10 Sekunden nach Runner-Start
- ✅ Drücke "Refresh Now" im View Session Dashboard
- ✅ Prüfe ob `data/session/events.jsonl` existiert und Daten enthält

**Problem: Script-Ausführung nicht erlaubt (Linux/macOS)**
```bash
# Script ausführbar machen
chmod +x scripts/start_live.sh
./scripts/start_live.sh
```

**Problem: "ModuleNotFoundError" bei Dependencies**
```bash
# Lösche venv und installiere neu
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

# Dann Script erneut ausführen (erstellt venv automatisch)
./scripts/start_live.sh  # Linux/Mac
.\scripts\start_live.ps1  # Windows
```

**Problem: DRY_RUN Modus wird nicht respektiert**
- ✅ Prüfe ob `.env` Datei im Projekt-Root existiert
- ✅ Prüfe Syntax: `DRY_RUN=true` (ohne Leerzeichen um `=`)
- ✅ Die Skripte zeigen die aktuelle Konfiguration beim Start
- ✅ Konsolen-Output zeigt: "Configuration: DRY_RUN: true"

### 📚 Weitere Dokumentation

**Projekt-Status & Planung:**
- [REPOSITORY_ANALYSIS.md](REPOSITORY_ANALYSIS.md) - 📊 Vollständige Repository-Analyse mit Status, Gaps und Optimierungspotenzial
- [EPIC_REPOSITORY_ANALYSIS_SUMMARY.md](EPIC_REPOSITORY_ANALYSIS_SUMMARY.md) - 🎯 Epic Summary mit empfohlenen Sub-Issues und Aktionsplan
- [ROADMAP.md](ROADMAP.md) - 🗺️ Projekt-Roadmap und Milestones
- [PROGRESS.md](PROGRESS.md) - 📊 Laufende Arbeiten und Issue-Tracking

**Feature-Guides:**
- [AUTOMATION_RUNNER_GUIDE.md](AUTOMATION_RUNNER_GUIDE.md) - Automation Runner Details
- [VIEW_SESSION_GUIDE.md](VIEW_SESSION_GUIDE.md) - View Session Features
- [VIEW_SESSION_STREAMLIT_GUIDE.md](VIEW_SESSION_STREAMLIT_GUIDE.md) - Streamlit Dashboard

---

## ⚙️ Umgebungsvariablen (ENV) - Vollständige Referenz

Alle Umgebungsvariablen können in der `.env` Datei im Projekt-Root gesetzt werden. Verwende `.env.example` als Vorlage.

### 🔧 Grundlegende Konfiguration

| Variable | Zweck | Beispielwert | Standard | Pflicht |
|----------|-------|--------------|----------|---------|
| `DRY_RUN` | Aktiviert sicheren Trockenlauf ohne echte API-Calls | `true` / `false` | `true` | ✅ |
| `BROKER_NAME` | Trading-Platform Auswahl | `binance` / `alpaca` | `binance` | ✅ |
| `LOG_LEVEL` | Logging-Detailgrad | `DEBUG` / `INFO` / `WARNING` / `ERROR` | `INFO` | ❌ |

### 🔐 Binance API Credentials (Haupt-Plattform)

| Variable | Zweck | Beispielwert | Standard | Pflicht |
|----------|-------|--------------|----------|---------|
| `BINANCE_API_KEY` | Binance API-Schlüssel für Live-Trading | `xyz123abc...` | - | ⚠️ Nur für Live |
| `BINANCE_SECRET_KEY` | Binance Secret Key für Live-Trading | `secret789...` | - | ⚠️ Nur für Live |
| `BINANCE_BASE_URL` | Binance API Endpoint | `https://api.binance.com` (Live)<br>`https://testnet.binance.vision` (Test) | `https://testnet.binance.vision` | ❌ |

### 🧪 Binance Testnet Credentials (Paper Trading)

| Variable | Zweck | Beispielwert | Standard | Pflicht |
|----------|-------|--------------|----------|---------|
| `BINANCE_TESTNET_API_KEY` | Testnet API-Schlüssel (Papierhandel) | `testkey123...` | - | ❌ |
| `BINANCE_TESTNET_SECRET_KEY` | Testnet Secret Key (Papierhandel) | `testsecret...` | - | ❌ |

### 🚨 Live-Trading Flags (DANGER ZONE)

| Variable | Zweck | Beispielwert | Standard | Pflicht |
|----------|-------|--------------|----------|---------|
| `LIVE_TRADING` | Aktiviert echtes Trading (erfordert API-Keys) | `true` / `false` | `false` | ⚠️ Nur für Live |
| `LIVE_ACK` | Bestätigung für Live-Trading (Sicherheitscheck) | `I_UNDERSTAND` | - | ⚠️ Nur für Live |
| `KILL_SWITCH` | Notfall-Stopp: Blockiert alle Live-Orders sofort | `true` / `false` | `false` | ❌ |

### 🤖 Optional: OpenAI Integration

| Variable | Zweck | Beispielwert | Standard | Pflicht |
|----------|-------|--------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API-Key für KI-Features | `sk-proj-...` | - | ❌ |

### 💰 Trading-Parameter (Optional - überschreibt config.py)

| Variable | Zweck | Beispielwert | Standard | Pflicht |
|----------|-------|--------------|----------|---------|
| `INITIAL_CAPITAL` | Startkapital für Backtests und Simulationen | `10000` | `10000` | ❌ |
| `TRADE_SIZE` | Handelsvolumen pro Trade | `100` | `100` | ❌ |
| `UPDATE_INTERVAL` | Update-Intervall in Sekunden | `60` | `60` | ❌ |

### 🛡️ Risk-Management Parameter

| Variable | Zweck | Beispielwert | Standard | Pflicht |
|----------|-------|--------------|----------|---------|
| `STOP_LOSS_PERCENT` | Stop-Loss in Prozent | `10` | `10` | ❌ |
| `TAKE_PROFIT_PERCENT` | Take-Profit in Prozent | `20` | `20` | ❌ |
| `MAX_DAILY_LOSS` | Maximaler Tagesverlust in Prozent | `5` | `5` | ❌ |

### 📋 Beispiel: Komplette .env Datei

**Für DRY_RUN / Testnet (Standard - sicher):**
```bash
# Safe Mode Configuration
DRY_RUN=true
BROKER_NAME=binance
BINANCE_BASE_URL=https://testnet.binance.vision

# Optional: Testnet Keys für Paper Trading
BINANCE_TESTNET_API_KEY=your_testnet_api_key
BINANCE_TESTNET_SECRET_KEY=your_testnet_secret_key

# Logging
LOG_LEVEL=INFO

# Risk Management
STOP_LOSS_PERCENT=10
TAKE_PROFIT_PERCENT=20
MAX_DAILY_LOSS=5
```

**Für Live-Trading (DANGER - nur mit echten Keys):**
```bash
# ⚠️ ACHTUNG: Live-Trading mit echtem Geld
DRY_RUN=false
LIVE_TRADING=true
LIVE_ACK=I_UNDERSTAND

# Binance Live API (NIEMALS committen!)
BINANCE_API_KEY=your_real_api_key_here
BINANCE_SECRET_KEY=your_real_secret_key_here
BINANCE_BASE_URL=https://api.binance.com

# Broker Configuration
BROKER_NAME=binance

# Risk Management (wichtig für Live!)
STOP_LOSS_PERCENT=5
TAKE_PROFIT_PERCENT=10
MAX_DAILY_LOSS=2

# Emergency Kill Switch (auf false lassen)
KILL_SWITCH=false
```

### 🔒 Sicherheitshinweise

**✅ Best Practices:**
- Verwende **Windows Credential Manager** für Live-Trading Keys (siehe Setup-Guide)
- Nutze `.env` nur für DRY_RUN und Testnet
- Stelle sicher, dass `.env` in `.gitignore` steht (ist standardmäßig der Fall)
- Rotiere API-Keys regelmäßig

**❌ Niemals:**
- API-Keys in Git committen
- `.env` mit echten Keys teilen oder in Chat posten
- Withdrawals-Permission auf API-Keys aktivieren
- Ohne IP-Einschränkungen handeln

**📖 Weitere Informationen:**
- [SECURITY.md](SECURITY.md) - Vollständige Sicherheitsrichtlinien
- [LIVE_TRADING_SETUP_GUIDE.md](LIVE_TRADING_SETUP_GUIDE.md) - Setup für Live-Trading
- [.env.example](.env.example) - Komplette ENV-Template-Datei

---

## 🚨 GEFAHRZONE: Live-Trading

**⚠️ ACHTUNG: Live-Trading mit echtem Geld - Nur für erfahrene Trader!**

### 🔐 Sicherer Setup-Prozess (Windows-First)

Diese Anleitung zeigt, wie du **sicher** Live-Trading aktivierst ohne deine API-Keys im Dateisystem zu speichern.

#### 🛡️ Sicherheits-Prinzipien

1. **✅ Windows Credential Manager**: API-Keys werden sicher im Windows Credential Manager gespeichert
2. **✅ Keine Secrets in Dateien**: API-Keys werden nie in `.env` oder anderen Dateien gespeichert
3. **✅ Preflight Checks**: Automatische Validierung vor jedem Live-Trading-Start
4. **✅ Explizite Bestätigung**: `LIVE_ACK=I_UNDERSTAND` muss gesetzt sein
5. **✅ Kill Switch**: Notfall-Abschaltung mit `KILL_SWITCH=true`

#### 📋 Voraussetzungen

**BEVOR du anfängst:**

- [ ] ⚠️ **API-Keys widerrufen**: Falls du API-Keys versehentlich geteilt hast, widerrufe sie SOFORT auf Binance
- [ ] ✅ **Neue Keys erstellen**: Erstelle neue API-Keys auf Binance mit folgenden Einstellungen:
  - **Nur Reading + Spot Trading aktivieren**
  - **NIEMALS Withdrawals aktivieren**
  - **IP-Einschränkungen setzen** (nur deine IP)
  - **2FA aktivieren** auf deinem Binance-Account
- [ ] ✅ **Minimales Kapital**: Verwende nur Geld, das du dir leisten kannst zu verlieren
- [ ] ✅ **Testing abgeschlossen**: Habe ausreichend mit DRY_RUN und Testnet getestet

#### 🔧 Schritt 1: Setup-Wizard ausführen

Der Setup-Wizard fragt deine API-Keys ab und speichert sie sicher im Windows Credential Manager:

**Windows PowerShell:**
```powershell
# Führe den Setup-Wizard aus
.\scripts\setup_live.ps1
```

**Was der Wizard macht:**
1. ✅ Fragt Binance API-Key und Secret ab (sichere Eingabe ohne Anzeige)
2. ✅ Speichert Keys im Windows Credential Manager (nicht auf Disk!)
3. ✅ Fragt Risk-Management-Parameter ab (Trading-Pairs, Risk-Limits, Order-Types)
4. ✅ Erstellt `config/live_risk.yaml` (enthält KEINE Secrets, nur Risk-Config)

**VS Code Task Alternative:**
```
Ctrl+Shift+P → "Tasks: Run Task" → "Live: Setup"
```

#### 🔍 Schritt 2: Risk-Config überprüfen

Nach dem Setup überprüfe die generierte `config/live_risk.yaml`:

```yaml
pairs: BTCUSDT
max_risk_per_trade: 0.005    # 0.5% Risk pro Trade
daily_loss_limit: 0.01       # 1% maximaler Tagesverlust
max_open_exposure: 0.05      # 5% maximales offenes Exposure
allowed_order_types: LIMIT_ONLY  # Nur Limit-Orders (sicherer)
max_slippage: 0.003          # 0.3% maximales Slippage
max_drawdown_limit: 0.20     # 20% Circuit Breaker (stoppt Trading automatisch)
```

**Empfohlene Anfangs-Einstellungen:**
- **Pairs**: Starte mit `BTCUSDT` (hohes Volumen, niedrige Spreads)
- **Order Types**: `LIMIT_ONLY` (sicherer, weniger Slippage)
- **Risk per Trade**: `0.005` (0.5%) oder weniger
- **Daily Loss Limit**: `0.01` (1%) als Circuit-Breaker
- **Drawdown Limit**: `0.20` (20%) - stoppt automatisch bei größerem Verlust

#### 🚀 Schritt 3: Live-Trading starten

**Windows PowerShell:**
```powershell
# Setze LIVE_ACK (explizite Bestätigung)
$env:LIVE_ACK = "I_UNDERSTAND"

# Starte Live-Trading
.\scripts\start_live_prod.ps1
```

**VS Code Task Alternative:**
```
# In PowerShell Terminal:
$env:LIVE_ACK = "I_UNDERSTAND"

# Dann:
Ctrl+Shift+P → "Tasks: Run Task" → "Live: Runner"
```

**Was beim Start passiert:**
1. ✅ Lädt API-Keys aus Windows Credential Manager (nicht aus Dateien!)
2. ✅ Setzt Production-Flags (`DRY_RUN=false`, `LIVE_TRADING=true`)
3. ✅ Überprüft `LIVE_ACK=I_UNDERSTAND`
4. ✅ Führt Preflight-Checks aus:
   - Environment-Variablen validieren
   - Production-Endpoint überprüfen (`https://api.binance.com`)
   - Zeit-Synchronisation mit Binance-Server (max 1000ms Abweichung)
   - Exchange-Info validieren (Trading-Pairs, Filter, Limits)
   - Account-Balance überprüfen (mindestens 10 USDT)
5. ✅ Startet Live-Trading Runner (`automation/runner.py` mit Production-Flags)

**Bei Preflight-Fehler:**
- ❌ Trading wird NICHT gestartet
- 📋 Fehlermeldungen werden angezeigt
- 🔧 Behebe die Fehler und versuche es erneut

#### 🔄 Alternative: Live-Umschaltung mit live_switch.py

**Sichere Umschaltung zwischen Modi:**

Die neue `automation/live_switch.py` bietet eine einfache, sichere Methode zum Wechseln zwischen DRY_RUN und LIVE Modi:

**Option 1: PowerShell-Script (empfohlen):**
```powershell
# Aktuellen Status prüfen
.\scripts\live_switch.ps1 -Status

# Zu DRY_RUN wechseln
.\scripts\live_switch.ps1 -DryRun

# Zu Live-Modus wechseln (mit Bestätigung)
.\scripts\live_switch.ps1 -Live
```

**Option 2: Direkter Python-Aufruf:**
```powershell
# Windows PowerShell (venv\Scripts verwenden)
.\venv\Scripts\python.exe -m automation.live_switch --status
.\venv\Scripts\python.exe -m automation.live_switch --dry-run
.\venv\Scripts\python.exe -m automation.live_switch --live
```

**Python API Verwendung:**
```python
from automation.live_switch import switch_to_live, switch_to_dry_run, check_api_key

# Prüfe API-Key vor Umschaltung
if not check_api_key()[0]:
    raise Exception("API-Key fehlt oder ungültig")

# Wechsel zu Live-Modus (mit Bestätigung)
result = switch_to_live()

# Wechsel zurück zu DRY_RUN
switch_to_dry_run()
```

**Was live_switch macht:**
1. ✅ Validiert API-Keys und Secrets
2. ✅ Prüft Umgebung (KILL_SWITCH, Base-URL)
3. ✅ Fordert explizite Bestätigung ("LIVE_TRADING_BESTÄTIGT")
4. ✅ Führt Preflight-Checks aus
5. ✅ Setzt Environment-Variablen (DRY_RUN, LIVE_TRADING)

#### 🛑 Notfall-Abschaltung: Kill Switch

Falls du sofort alle Live-Orders stoppen möchtest:

```powershell
# Setze Kill Switch
$env:KILL_SWITCH = "true"

# Preflight läuft durch, aber keine neuen Orders
# Offene Orders werden gecancelt (falls implementiert)
```

**Kill Switch deaktivieren:**
```powershell
$env:KILL_SWITCH = "false"
# Oder entfernen:
Remove-Item Env:KILL_SWITCH
```

#### 📊 Live-Trading überwachen

**View Session Dashboard parallel starten:**
```powershell
# In separater PowerShell-Session:
.\venv\Scripts\python.exe -m streamlit run tools/view_session_app.py --server.port 8501
```

Öffne Browser: `http://localhost:8501`

**Was zu überwachen ist:**
- 📈 **P&L**: Gewinn/Verlust in Echtzeit
- 📊 **Open Positions**: Aktuell offene Positionen
- 🎯 **Win Rate**: Erfolgsquote deiner Trades
- 🚨 **Daily Loss**: Tagesverlust (sollte unter `daily_loss_limit` bleiben)
- 💸 **Exposure**: Offenes Exposure (sollte unter `max_open_exposure` bleiben)

#### ⚠️ Wichtige Sicherheitshinweise

**🚫 NIEMALS:**
- ❌ API-Keys in `.env`, Git oder Chat teilen
- ❌ Withdrawals-Permission aktivieren
- ❌ Ohne IP-Einschränkungen handeln
- ❌ Mit mehr Kapital starten als du verlieren kannst
- ❌ Unbeaufsichtigt laufen lassen (erste Sessions)

**✅ IMMER:**
- ✅ API-Keys regelmäßig rotieren (neue Keys erstellen)
- ✅ Logs überwachen (`logs/trading_bot.log`)
- ✅ Alerts für große Verluste einrichten
- ✅ Mit minimalem Kapital testen (z.B. 50-100 USDT)
- ✅ Binance-Account regelmäßig überprüfen
- ✅ 2FA aktiviert lassen

#### 🔒 Secrets Management

**Wie Keys gespeichert werden:**
```
Windows Credential Manager
└── Service: "ai.traiding"
    ├── binance_api_key: [DEIN_API_KEY]
    └── binance_api_secret: [DEIN_SECRET]
```

**Keys anzeigen (Windows):**
```powershell
# Credential Manager öffnen
control keymgr.dll

# Oder via Python:
.\venv\Scripts\python.exe -c "import keyring; print('Key exists:', keyring.get_password('ai.traiding', 'binance_api_key') is not None)"
```

**Keys löschen:**
```powershell
.\venv\Scripts\python.exe -c "import keyring; keyring.delete_password('ai.traiding', 'binance_api_key'); keyring.delete_password('ai.traiding', 'binance_api_secret'); print('Keys deleted')"
```

#### 📝 Checkliste vor dem ersten Live-Trade

- [ ] Setup-Wizard erfolgreich durchgeführt (`.\scripts\setup_live.ps1`)
- [ ] `config/live_risk.yaml` überprüft und angepasst
- [ ] API-Keys im Windows Credential Manager gespeichert (nicht in Dateien!)
- [ ] Binance API-Keys haben NUR "Reading + Spot Trading" (KEINE Withdrawals)
- [ ] IP-Einschränkungen auf Binance-Keys gesetzt
- [ ] 2FA auf Binance-Account aktiviert
- [ ] Minimales Test-Kapital aufgeladen (z.B. 50-100 USDT)
- [ ] `LIVE_ACK=I_UNDERSTAND` gesetzt
- [ ] Preflight-Checks erfolgreich durchlaufen
- [ ] View Session Dashboard läuft für Monitoring
- [ ] Notfall-Plan bereit (Kill Switch, manuelles Order-Cancel auf Binance)

#### 🚨 Was tun bei Problemen?

**Problem: Preflight Check failed**
```
❌ [ERR] Time drift too large: 1500ms (max 1000ms)
```
**Lösung:** Synchronisiere deine System-Zeit mit einem Zeitserver.

**Problem: Authentication failed**
```
❌ [ERR] Authentication failed - check API keys
```
**Lösung:**
1. Überprüfe Keys im Credential Manager
2. Prüfe ob Keys auf Binance gültig sind
3. Prüfe IP-Einschränkungen (deine IP muss erlaubt sein)

**Problem: Balance too low**
```
❌ [ERR] USDT balance too low: 5.00 (minimum: 10)
```
**Lösung:** Lade mindestens 10 USDT auf deinen Binance Spot-Account.

**Problem: Keys nicht gefunden**
```
❌ Error: Credentials not found in Windows Credential Manager
```
**Lösung:** Führe Setup-Wizard erneut aus: `.\scripts\setup_live.ps1`

#### 📚 Weiterführende Dokumentation

- **[LIVE_TRADING_SETUP_GUIDE.md](LIVE_TRADING_SETUP_GUIDE.md)** - Vollständige Setup-Anleitung für Live-Trading
- **[SECURE_LIVE_TRADING_IMPLEMENTATION_SUMMARY.md](SECURE_LIVE_TRADING_IMPLEMENTATION_SUMMARY.md)** - Implementation Summary
- **[LIVE_TRADING_MANUAL_TEST_GUIDE.md](LIVE_TRADING_MANUAL_TEST_GUIDE.md)** - 🧪 **NEU:** Schritt-für-Schritt Manuelle Test-Anleitung
- **[LIVE_TRADING_TEST_CHECKLIST.md](LIVE_TRADING_TEST_CHECKLIST.md)** - ✅ **NEU:** Schnell-Checkliste für Tests
- [BINANCE_INTEGRATION_SUMMARY.md](BINANCE_INTEGRATION_SUMMARY.md) - Binance API Details
- [BINANCE_MIGRATION_GUIDE.md](BINANCE_MIGRATION_GUIDE.md) - Binance Setup Guide
- [AUTOMATION_RUNNER_GUIDE.md](AUTOMATION_RUNNER_GUIDE.md) - Automation Runner

---

## 🚀 Installation

### 1. Virtuelle Umgebung erstellen (empfohlen)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 3. Verzeichnisse werden automatisch erstellt
- `data/` - Für Trades und Ergebnisse
- `logs/` - Für Log-Dateien

---

## ⚙️ Konfiguration

### Option 1: Direkt in config.py

Öffne `config.py` und passe die Parameter in der `TradingConfig` Klasse an:

```python
# Trading Parameters
trading_symbol: str = "BTC/USDT"
timeframe: str = "15m"
initial_capital: float = 10000.0
trade_size: float = 100.0

# Active Strategies
active_strategies: list = ["rsi", "ema_crossover"]
cooperation_logic: str = "OR"  # "AND" oder "OR"

# Strategy Parameters
strategies: Dict[str, Dict[str, Any]] = {
    "rsi": {
        "window": 14,
        "oversold_threshold": 35,
        "overbought_threshold": 65
    },
    "ema_crossover": {
        "short_window": 9,
        "long_window": 21
    },
    # ...
}
```

### Option 2: Über .env Datei (für API-Keys)

Erstelle eine `.env` Datei im Hauptverzeichnis:

```env
# API Credentials (optional, für Production)
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Logging
LOG_LEVEL=INFO
```

---

## 📊 Verwendung

### 🏃 Backtest durchführen

Teste deine Strategie mit historischen oder simulierten Daten:

```bash
python backtester.py
```

**Interaktiver Modus:**
1. Wähle Datenquelle:
   - `[1]` CSV-Datei laden (benötigt OHLCV-Format)
   - `[2]` Simulierte Daten generieren
2. Bei CSV: Pfad angeben (default: `data/historical_data.csv`)
3. Bei Simulation: Anzahl Kerzen angeben (default: 1000)
4. Backtest läuft und zeigt detaillierten Report

**Output:**
```
📊 BACKTEST REPORT
======================================================================
💰 KAPITAL:
  Initial Capital:  $10,000.00
  Final Capital:    $12,450.00
  Total P&L:        $2,450.00
  ROI:              24.50%

📈 TRADES:
  Total Trades:     45
  Winning Trades:   28
  Losing Trades:    17
  Win Rate:         62.22%
  Average Win:      $150.00
  Average Loss:     -$80.00
  Best Trade:       $450.00
  Worst Trade:      -$220.00
  Profit Factor:    2.05
```

### 🚀 Live-Trading starten

Starte den Bot im simulierten Live-Modus:

```bash
python main.py
```

**Was passiert:**
- Bot generiert fortlaufend neue Marktdaten (simuliert)
- Analysiert Daten mit allen aktiven Strategien
- Gibt BUY/SELL Signale basierend auf Cooperation Logic
- Protokolliert alle Trades in `data/trades.csv`
- Zeigt Live-Updates im Terminal und Log-Datei

**Beenden:** Drücke `Ctrl+C` für sauberes Shutdown

**Terminal Output:**
```
🚀 LIVE TRADING BOT GESTARTET
======================================================================
Initial Capital: $10,000.00
Trading Symbol: BTC/USDT
Update Interval: 60s
Active Strategies: ['rsi', 'ema_crossover']
Cooperation Logic: OR
======================================================================

🔄 Trading-Loop aktiv
Drücke Ctrl+C zum Beenden

📈 BUY @ $30,250.00 | Strategien: ['rsi', 'ema_crossover']
💹 Preis: $30,280.00 | Position: Long @ $30,250.00 | Capital: $10,000.00
...
💰 SELL @ $30,580.00 | P&L: $33.00 | Capital: $10,033.00 | Strategien: ['rsi']
```

### 🔍 Live Market Monitoring 🆕

Monitor real-time market data with automated alerts:

```bash
# Start live market monitoring
python main.py --monitor

# Or run interactive demo
python demo_live_monitor.py
```

**Features:**
- Monitor multiple trading pairs simultaneously (BTC, ETH, etc.)
- Real-time price tracking with percentage change calculations
- Automated strategy signal detection
- Configurable alerts for price changes and volume spikes
- Custom alert callbacks for notifications

**Quick Example:**
```python
from live_market_monitor import LiveMarketMonitor
from strategy import TradingStrategy
from config import config

# Initialize monitor
monitor = LiveMarketMonitor(
    symbols=['BTCUSDT', 'ETHUSDT'],
    interval='15m',
    update_interval=60,
    testnet=True,
    price_alert_threshold=2.0  # Alert on 2% change
)

# Integrate strategy
strategy = TradingStrategy(config.to_dict())
monitor.integrate_strategy(strategy)

# Start monitoring
monitor.start_monitoring()
```

**Alert Examples:**
```
📢 [PRICE_CHANGE] BTCUSDT: Price UP 2.34% ($50,234.50)
⚠️ [STRATEGY_SIGNAL] ETHUSDT: BUY signal from 2 strategies: RSI, EMA_Crossover at $3,124.67
📢 [VOLUME_SPIKE] BTCUSDT: Volume spike detected: 2.8x average
```

📖 **See [LIVE_MARKET_MONITOR_GUIDE.md](LIVE_MARKET_MONITOR_GUIDE.md) for detailed setup and usage.**

### 🤖 Automatisierter Workflow ausführen 🆕

Starte den automatisierten Real-Money-Readiness Workflow:

```bash
python automation/runner.py
```

**Was passiert:**
- **Phase 1 (Daten)**: Lädt und validiert Daten (Timeout: 2 Stunden)
- **Pause & Check**: Automatische Selbstprüfung (max. 10 Minuten)
- **Phase 2 (Strategie)**: Testet und validiert Strategien (Timeout: 2 Stunden)
- **Pause & Check**: Automatische Selbstprüfung
- **Phase 3 (API)**: Validiert API-Keys und Konnektivität (Timeout: 1 Stunde)
- **Abschluss**: Speichert vollständiges Session-Log und Metriken

**Ausgabe:**
```
======================================================================
AUTOMATION RUNNER - REAL-MONEY READINESS WORKFLOW
======================================================================

--- Phase 1: Data Phase ---
Executing data phase...

--- Pause and Self-Check ---
Running self-check...

--- Phase 2: Strategy Phase ---
Executing strategy phase...

--- Pause and Self-Check ---
Running self-check...

--- Phase 3: API Phase ---
Executing API phase...

======================================================================
WORKFLOW COMPLETED - Status: success
======================================================================

AUTOMATION SUMMARY
======================================================================
Status: success
Duration: 16.00 seconds

Phases completed:
  - data_phase: success (2.00s)
  - strategy_phase: success (2.00s)
  - api_phase: success (2.00s)
======================================================================
```

**Session-Dateien:**
- `data/session/events.jsonl` - Alle Events (JSONL-Format)
- `data/session/summary.json` - Zusammenfassung mit ROI

### 📊 View Session Dashboard starten 🆕

Visualisiere Sessions und Trades in Echtzeit:

```bash
# Optional: Installiere Streamlit (falls nicht vorhanden)
pip install streamlit plotly

# Starte Dashboard
streamlit run tools/view_session_app.py
```

**Features:**
- **Echtzeit-Metriken**: Initial Capital, Current Equity, ROI, Fortschritt
- **Equity Curve**: Liniendiagramm zeigt PnL-Entwicklung
- **Wins vs Losses**: Balkendiagramm pro Phase
- **Event-Historie**: Tabelle mit letzten 20 Events

**Filter:**
- **Zeitbereich**: Alle, letzte 1h, letzte 24h, letzte 7 Tage, benutzerdefiniert
- **Strategy Tag**: Alle, data_phase, strategy_phase, api_phase
- **Auto-Refresh**: Aktivierbar für Live-Updates alle 5 Sekunden

**Browser öffnet automatisch:** `http://localhost:8501`

### 🔐 API-Keys konfigurieren

Erstelle eine `.env` Datei für API-Keys:

```bash
# .env Datei im Hauptverzeichnis
BINANCE_API_KEY=dein_binance_api_key
BINANCE_API_SECRET=dein_binance_api_secret
ALPACA_API_KEY=dein_alpaca_api_key
ALPACA_API_SECRET=dein_alpaca_api_secret
```

**Wichtig:** Niemals API-Keys direkt im Code committen!

---

## 🔧 Strategien anpassen

### Aktivierte Strategien ändern

In `config.py`:

```python
active_strategies: list = ["ma_crossover", "bollinger_bands"]
```

### Parameter anpassen

Für **konservativeres** Trading (längere Perioden, weniger Signale):
```python
"rsi": {
    "window": 14,
    "oversold_threshold": 25,  # Niedriger = konservativer
    "overbought_threshold": 75  # Höher = konservativer
}
```

Für **aggressiveres** Trading (kürzere Perioden, mehr Signale):
```python
"ema_crossover": {
    "short_window": 5,   # Kürzer = reaktiver
    "long_window": 13    # Kürzer = mehr Signale
}
```

### Neue Strategie hinzufügen

1. Erstelle neue Klasse in `strategy.py`:
```python
class MyCustomStrategy(BaseStrategy):
    def __init__(self, params: Dict[str, Any]):
        super().__init__("MyCustomStrategy", params)
        # Parameter initialisieren
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        # Logik implementieren
        # Return: 1 (BUY), 0 (HOLD), -1 (SELL)
        pass
```

2. Registriere in `STRATEGY_MAP`:
```python
STRATEGY_MAP = {
    'my_custom': MyCustomStrategy,
    # ...
}
```

3. Aktiviere in Config:
```python
active_strategies: list = ["my_custom"]
```

### Neue Strategie mit Enhanced Base Framework (Video-basiert)

Für komplexere Strategien aus YouTube-Videos oder Tutorials verwende das Enhanced Base Framework:

1. Erstelle neue Klasse mit `EnhancedBaseStrategy`:
```python
from base_strategy import EnhancedBaseStrategy

class MyVideoStrategy(EnhancedBaseStrategy):
    def __init__(self, params: Dict[str, Any]):
        super().__init__("MyVideoStrategy", params)
        # Deine Parameter
        self.indicator1 = params.get('indicator1', 14)
        self.indicator2 = params.get('indicator2', 20)
    
    def generate_signal(self, df: pd.DataFrame) -> int:
        if not self.validate_data(df):
            return 0
        
        # Implementiere Video-Strategie-Logik
        # ... berechne Indikatoren
        # ... generiere Signal
        
        return 0  # 1=BUY, 0=HOLD, -1=SELL
```

2. Nutze erweiterte Features:
```python
# Multi-Timeframe Analysis
strategy.add_data_feed('BTC/USDT', '1h', df_1h)
strategy.add_data_feed('BTC/USDT', '4h', df_4h)

# Signal mit Kontext
signal, context = strategy.generate_signal_with_context(df)
print(f"Confidence: {context['confidence']}")

# State Management
strategy.update_state(custom_value=42)
strategy.export_state('data/strategy_state.json')
```

3. Registriere und aktiviere wie normale Strategie

📖 **[Vollständige Dokumentation](docs/BASE_STRATEGY_GUIDE.md)** mit Beispielen und Best Practices

---

## 📈 CSV-Format für historische Daten

Deine CSV-Datei muss folgende Spalten enthalten:

```csv
timestamp,open,high,low,close,volume
2024-01-01 00:00:00,30000.0,30100.0,29900.0,30050.0,1250.5
2024-01-01 00:15:00,30050.0,30200.0,30000.0,30150.0,1180.2
...
```

**Anforderungen:**
- `timestamp`: Datetime oder ISO-Format
- `open, high, low, close`: Numerisch (float)
- `volume`: Numerisch (float)
- Keine NaN-Werte
- Logische OHLC-Beziehungen (High >= Low, etc.)

---

## 📊 Trade History analysieren

Alle Trades werden in `data/trades.csv` gespeichert:

```csv
timestamp,symbol,order_type,price,quantity,triggering_strategies,capital,pnl
2024-10-08 10:30:00,BTC/USDT,BUY,30250.00,100,rsi,10000.00,0.00
2024-10-08 11:00:00,BTC/USDT,SELL,30580.00,100,"rsi, ema_crossover",10033.00,33.00
```

**Analysieren mit pandas:**
```python
import pandas as pd

trades = pd.read_csv('data/trades.csv')
print(trades.describe())

# Performance
wins = trades[trades['pnl'] > 0]
print(f"Win Rate: {len(wins)/len(trades)*100:.2f}%")
```

---

## 📊 Visual Dashboard verwenden

Das Enhanced Visual Dashboard bietet umfassende Metriken und Visualisierungen.

### Dashboard-Demo starten

```bash
python dashboard_demo.py
```

**Hauptfunktionen:**
1. **Metriken anzeigen**: Zeigt aktuelle Performance-Metriken
2. **Modal öffnen**: Verwaltet Metriken und Diagramme
3. **Charts generieren**: Erstellt interaktive Visualisierungen
4. **HTML exportieren**: Exportiert Dashboard als HTML-Datei

### Programmatische Verwendung

```python
from dashboard import create_dashboard, DashboardModal

# Dashboard erstellen
dashboard = create_dashboard()

# Metriken anzeigen
dashboard.display_metrics_console()

# HTML exportieren
dashboard.export_dashboard_html('data/dashboard.html')

# Interaktive Charts generieren
charts = dashboard.generate_all_charts(use_plotly=True)
```

### Modal-Verwaltung

```python
# Modal erstellen und öffnen
modal = DashboardModal(dashboard)
modal.open()

# Metrik hinzufügen
modal.add_metric('custom_roi')

# Chart hinzufügen
modal.add_chart('line', 'Custom P&L', 'pnl_history')

# Modal schließen
modal.close()
```

**Weitere Details:** Siehe [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)

---

## 🎯 Cooperation Logic erklärt

### AND Logic (Konservativ)
```
Strategie 1: BUY     ─┐
Strategie 2: BUY     ─┤  → BUY Signal
Strategie 3: BUY     ─┘

Strategie 1: BUY     ─┐
Strategie 2: HOLD    ─┤  → Kein Signal
Strategie 3: BUY     ─┘
```
**Nutzen:** Höhere Genauigkeit, weniger False Positives

### OR Logic (Aggressiv)
```
Strategie 1: BUY     ─┐
Strategie 2: HOLD    ─┤  → BUY Signal
Strategie 3: HOLD    ─┘

Strategie 1: HOLD    ─┐
Strategie 2: HOLD    ─┤  → Kein Signal
Strategie 3: HOLD    ─┘
```
**Nutzen:** Mehr Signale, schnellere Reaktion auf Markt

---

## 🔍 Logging

Alle wichtigen Events werden geloggt:

**Wo:** `logs/trading_bot.log`

**Was:**
- Bot Start/Stop
- Strategien-Initialisierung
- Trade-Execution (BUY/SELL)
- Fehler und Warnungen
- Performance-Metriken

**Log Rotation:**
- Maximale Größe: 10 MB
- Backup-Count: 5 Dateien
- Automatische Kompression älterer Logs

**Beispiel:**
```
2024-10-08 10:30:15 - root - INFO - 📈 BUY @ $30250.00 | Strategien: ['rsi']
2024-10-08 11:00:42 - root - INFO - 💰 SELL @ $30580.00 | P&L: $33.00 | Capital: $10033.00
```

---

## 🛠️ Troubleshooting

### Problem: ModuleNotFoundError

**Lösung:**
```bash
pip install -r requirements.txt
```

### Problem: "Ungültige Daten" beim Backtest

**Lösung:** Prüfe CSV-Format:
- Alle erforderlichen Spalten vorhanden?
- Numerische Werte korrekt?
- Keine NaN-Werte?
- OHLC-Logik korrekt? (High >= Low, etc.)

### Problem: Keine Signale generiert

**Mögliche Ursachen:**
1. AND Logic + zu viele Strategien → Keine Übereinstimmung
2. Zu wenig historische Daten für Indikatoren
3. Extreme Parameter-Werte

**Lösung:**
- Nutze OR Logic für mehr Signale
- Verwende mindestens 200+ Kerzen für Backtests
- Teste mit Standard-Parametern (Balanced Preset)

### Problem: Schlechte Performance im Backtest

**Optimierung:**
1. **Parameter-Tuning**: Teste verschiedene Parameter-Kombinationen
2. **Strategie-Mix**: Kombiniere verschiedene Strategien (Trend + Mean Reversion)
3. **Timeframe**: Teste verschiedene Zeitrahmen (5m, 15m, 1h)
4. **Marktbedingungen**: Manche Strategien funktionieren besser in Trends, andere in Range-Märkten

---

## 📚 Erweiterte Nutzung

### Parameter-Presets

**Conservative** (Lange Perioden, hohe Genauigkeit):
```python
"ma_crossover": {"short_window": 50, "long_window": 200}
"rsi": {"oversold_threshold": 25, "overbought_threshold": 75}
```

**Balanced** (Standard-Einstellungen):
```python
"ma_crossover": {"short_window": 20, "long_window": 50}
"rsi": {"oversold_threshold": 35, "overbought_threshold": 65}
```

**Aggressive** (Kurze Perioden, viele Signale):
```python
"ma_crossover": {"short_window": 10, "long_window": 30}
"rsi": {"oversold_threshold": 40, "overbought_threshold": 60}
```

### Eigene CSV-Daten verwenden

1. Exportiere Daten von deiner Börse (Binance, Kraken, etc.)
2. Konvertiere zu OHLCV-Format
3. Speichere als `data/my_data.csv`
4. Führe Backtest aus: `python backtester.py` → Option [1]

---

## 🚧 Nächste Schritte / TODO

- [ ] Echte API-Integration (Alpaca, Binance)
- [ ] Stop-Loss & Take-Profit Mechanik
- [ ] Trailing Stop Implementation
- [ ] Position Sizing basierend auf Risiko
- [ ] Machine Learning für Signal-Optimierung
- [ ] Web-Dashboard mit Flask/FastAPI
- [ ] Real-time Charting mit Plotly
- [ ] Telegram/Discord Benachrichtigungen
- [ ] Database Support (SQLite/PostgreSQL)
- [ ] Multi-Symbol Trading

---

## 👨‍💻 Developer Workflow

### VS Code Setup für Entwickler

Dieses Projekt enthält vorkonfigurierte VS Code-Einstellungen für optimale Entwicklungserfahrung:

**Empfohlene Extensions** (automatische Installation-Prompts):
- **GitHub Pull Requests and Issues**: Direkte Integration von Issues und PRs
- **GitLens**: Erweiterte Git-Funktionen und Code-Historie
- **Markdown All in One**: Markdown-Bearbeitung mit Vorschau

**GitHub Issues-Ansicht nutzen**:
1. Installiere die empfohlenen Extensions
2. Öffne die GitHub-Seitenleiste (Sidebar → GitHub-Icon)
3. Melde dich mit deinem GitHub-Account an
4. Vordefinierte Queries sind bereits konfiguriert:
   - **Open: View Session (#42)**: Aktuelle Arbeiten an View Session Features
   - **Open: Echtgeld-Automatisierung (#44)**: Echtgeld-Trading Automatisierung
   - **Open PRs (me)**: Deine offenen Pull Requests

**Live-Progress verfolgen**:
- Öffne `PROGRESS.md` und pinne den Tab (Rechtsklick → "Pin Tab")
- Dort findest du detaillierte Checklisten für aktuelle Issues
- Aktualisiere die Checklisten während der Entwicklung

**Aktuelle Arbeiten**:
- [Issue #42](https://github.com/CallMeMell/ai.traiding/issues/42): View Session Visualisierung & Filter
- [Issue #44](https://github.com/CallMeMell/ai.traiding/issues/44): Echtgeld-Automatisierung

Siehe `PROGRESS.md` für detaillierte Checklisten und Workflow-Beschreibung.

### Run Tasks

Dieses Projekt enthält vordefinierte VS Code Tasks für schnelle Entwicklung in VS Code und Codespaces:

**Verfügbare Tasks** (über `Terminal → Run Task...`):

1. **Install Dev Deps**
   - Erstellt Virtual Environment (venv)
   - Aktualisiert pip
   - Installiert benötigte Dependencies: streamlit, plotly, pandas, requests, python-dotenv
   - Nutzen: Einmalige Einrichtung der Entwicklungsumgebung

2. **Run: Automation Runner (Dry-Run)**
   - Aktiviert Virtual Environment
   - Setzt Umgebungsvariablen: `DRY_RUN=true`, `BROKER_NAME=binance`, `BINANCE_BASE_URL=https://testnet.binance.vision`
   - Führt `python automation/runner.py` aus
   - Nutzen: Testen des automatisierten Workflows ohne echte API-Keys
   - **Standardmäßig im Dry-Run-Modus** (keine echten Trades)

3. **Run: View Session (Streamlit)**
   - Aktiviert Virtual Environment
   - Startet Streamlit-Dashboard auf Port 8501
   - Nutzen: Live-Visualisierung von Session-Daten und Events
   - **Port 8501 wird automatisch weitergeleitet** und öffnet Preview in Codespaces

**Umschalten auf Live-Trading:**
- Wenn API-Keys verfügbar sind, Task "Run: Automation Runner (Dry-Run)" in `.vscode/tasks.json` bearbeiten
- Entferne `export DRY_RUN=true` (Linux/macOS) oder `set DRY_RUN=true` (Windows)
- Füge echte API-Keys in `.env` Datei ein
- ⚠️ **Achtung**: Nur mit Testnet-Keys oder sehr kleinen Beträgen testen!

**Referenzen:**
- [#42](https://github.com/CallMeMell/ai.traiding/issues/42) - View Session Dashboard
- [#44](https://github.com/CallMeMell/ai.traiding/issues/44) - Echtgeld-Automatisierung

---

## ⚠️ Disclaimer

**Dieses Projekt dient ausschließlich zu Bildungszwecken.**

- Keine Finanzberatung
- Teste ausschließlich mit Paper-Trading / Simulationen
- Trading birgt erhebliche Risiken
- Verluste sind möglich
- Nutze auf eigene Verantwortung

---

## 📝 Version History

**v1.0 - Master Version (Oktober 2024)**
- Konsolidierung aller vier Entwicklungsstufen
- 4 professionelle Strategien
- Multi-Strategy Orchestrierung mit AND/OR Logic
- Vollständiges Logging & Fehlerbehandlung
- Backtesting Engine mit Performance-Metriken
- Modulare, produktionsreife Architektur

---

## 🙌 Support

Bei Fragen oder Problemen:
1. Prüfe diese README
2. Schaue in die Log-Dateien (`logs/trading_bot.log`)
3. Validiere deine CSV-Daten
4. Teste mit simulierten Daten zuerst

---

## 📋 Effiziente Issues

Dieses Projekt nutzt **GitHub Issue Forms** für standardisierte und effiziente Issue-Erstellung. Wähle beim Erstellen eines neuen Issues die passende Vorlage:

### Verfügbare Issue-Vorlagen

1. **[Auto] Automation Task** – Für automatisierte Aufgaben
   - ✅ Outcome-orientierter Titel
   - ✅ Messbare Akzeptanzkriterien
   - ✅ Klar definierter Scope und Non-Goals
   - Beispiel: `[Auto] Live-Observability für Automation Runner`

2. **[Manual] Manual Task** – Für manuelle Schritt-für-Schritt Aufgaben
   - ✅ Checkliste mit konkreten Schritten
   - ✅ Proof/Nachweis für Abschluss
   - ✅ Voraussetzungen dokumentiert
   - Beispiel: `[Manual] API Keys für Binance Testnet einrichten`

3. **[Epic] Epic Tracking** – Für größere Initiativen
   - ✅ Milestones und Sub-Issues
   - ✅ Definition of Done (DoD)
   - ✅ Risiken und Success Metrics
   - Beispiel: `[Epic] Live Observability Enhancement`

### Best Practices für Issue-Titel

**✅ Gut (outcome-orientiert):**
- `[Auto] Live-Observability für Automation Runner mit strukturierten Events`
- `[Manual] Ein-Klick Dev Live Session Setup mit Port-Forwarding`
- `[Epic] Projektabschluss: Sichtbarkeit & Monitoring-Features`

**❌ Schlecht (task-orientiert):**
- `View Session verbessern`
- `Code aufräumen`
- `Tests hinzufügen`

### Messbare Acceptance Criteria

**✅ Gut (messbar):**
```markdown
- [ ] Event-Schema mit 8+ Feldern implementiert
- [ ] 10+ Tests passing (pytest)
- [ ] Dokumentation auf Deutsch (min. 200 Zeilen)
- [ ] Real-time monitoring funktioniert (< 100ms Latenz)
```

**❌ Schlecht (vage):**
```markdown
- [ ] Code funktioniert
- [ ] Tests sind da
- [ ] Doku ist gut
```

### Mehr Informationen

- Alle Vorlagen sind unter [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/) verfügbar
- Labels werden automatisch gesetzt: `automation`, `manual`, `meta`, `epic`
- Siehe [PROGRESS.md](PROGRESS.md) für Beispiele und Workflow-Beschreibungen

---

## 📜 Lizenz

MIT License - Nutze und modifiziere frei für deine Zwecke.

---

**Happy Trading! 🚀📈**
#   a i . t r a i d i n g  
 