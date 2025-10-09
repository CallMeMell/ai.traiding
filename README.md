# 🎯 Multi-Strategy Trading Bot - Master Version

**Professional Trading Bot mit Multi-Strategy Orchestrierung**

Diese Master-Version konsolidiert die besten Features aus vier Evolutionsstufen in eine produktionsreife, modulare Anwendung.

## 🔥 Now with Binance API Integration!

The bot now uses **Binance API** as the primary trading platform:
- ✅ **24/7 Cryptocurrency Trading**
- ✅ **Testnet Support** for risk-free paper trading
- ✅ **Low Fees** and high liquidity
- ✅ **1000+ Trading Pairs**
- ✅ **Production-Ready** with comprehensive error handling

📖 **[Read the Binance Migration Guide](BINANCE_MIGRATION_GUIDE.md)** for detailed setup instructions.

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
- **5 professionelle Strategien:**
  - **MA Crossover**: Trend-Following mit Moving Averages (mittel- bis langfristig)
  - **RSI Mean Reversion**: Überverkauft/Überkauft Strategie (Seitwärtsmärkte)
  - **Bollinger Bands**: Volatilitäts-Breakout Strategie
  - **EMA Crossover**: Schnelle Trend-Strategie für Daytrading
  - **LSOB (Long-Short On Breakout)**: Advanced volatility breakout strategy

### ✅ Signal-Aggregation
- **AND Logic**: Konservativ - Alle Strategien müssen zustimmen
- **OR Logic**: Aggressiv - Mindestens eine Strategie reicht

### ✅ Backtesting Engine
- Historische Datenanalyse
- Detaillierte Performance-Metriken
- Win Rate, ROI, Profit Factor, etc.

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

## 📜 Lizenz

MIT License - Nutze und modifiziere frei für deine Zwecke.

---

**Happy Trading! 🚀📈**
#   a i . t r a i d i n g  
 