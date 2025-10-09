# 🎯 Multi-Strategy Trading Bot - Master Version

**Professional Trading Bot mit Multi-Strategy Orchestrierung**

Diese Master-Version konsolidiert die besten Features aus vier Evolutionsstufen in eine produktionsreife, modulare Anwendung.

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
├── requirements.txt      # Python-Abhängigkeiten
│
├── data/                 # Datenverzeichnis (automatisch erstellt)
│   ├── trades.csv        # Trade-History
│   └── backtest_results.csv  # Backtest-Ergebnisse
│
├── logs/                 # Log-Verzeichnis (automatisch erstellt)
│   └── trading_bot.log   # Vollständiges Log
│
└── config/               # Config-Verzeichnis (optional)
    └── trading_config.json  # Gespeicherte Konfiguration
```

---

## 🎯 Kern-Features

### ✅ Multi-Strategy System
- **4 professionelle Strategien:**
  - **MA Crossover**: Trend-Following mit Moving Averages (mittel- bis langfristig)
  - **RSI Mean Reversion**: Überverkauft/Überkauft Strategie (Seitwärtsmärkte)
  - **Bollinger Bands**: Volatilitäts-Breakout Strategie
  - **EMA Crossover**: Schnelle Trend-Strategie für Daytrading

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

### 🌐 Dashboard starten (NEU!)

**Professionelles Web-Dashboard mit interaktiven Charts:**

```bash
# Windows:
start_dashboard.bat

# Linux/Mac:
./start_dashboard.sh

# Oder manuell:
python dashboard.py
```

Öffne dann http://localhost:5000 im Browser.

**Dashboard Features:**
- 📈 Live Performance-Metriken (P&L, Win Rate, etc.)
- 📊 3 Interaktive Charts (Equity Curve, P&L Distribution, Strategy Performance)
- 📋 Recent Trades Übersicht
- ⚙️ Bot Configuration Display
- 🔄 Auto-Refresh alle 30 Sekunden
- 📱 Responsive Design

**Vollständige Dokumentation:** Siehe [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)

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

- [x] **Web-Dashboard mit Flask** ✅ (NEU in v1.1!)
- [x] **Real-time Charting mit Chart.js** ✅ (NEU in v1.1!)
- [ ] Echte API-Integration (Alpaca, Binance)
- [ ] Stop-Loss & Take-Profit Mechanik
- [ ] Trailing Stop Implementation
- [ ] Position Sizing basierend auf Risiko
- [ ] Machine Learning für Signal-Optimierung
- [ ] WebSocket für Live-Updates ohne Refresh
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

**v1.1 - Dashboard Update (Oktober 2024)**
- ✨ **NEU: Professional Web Dashboard** mit Flask
- ✨ **NEU: Interaktive Charts** (Equity Curve, P&L, Strategy Performance)
- ✨ **NEU: Live Performance-Metriken** mit Auto-Refresh
- 🎨 Moderne UI mit Gradient-Design
- 📱 Responsive Layout für Mobile/Tablet
- 🧹 Code-Optimierung: Repository um 433MB reduziert

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