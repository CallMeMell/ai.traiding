# ❓ FAQ - Häufig gestellte Fragen

## Allgemeine Fragen

### Was ist dieser Trading-Bot?
Ein professioneller Multi-Strategy Trading-Bot, der verschiedene technische Analyse-Strategien kombiniert, um Trading-Signale zu generieren. Der Bot kann im Backtest-Modus (mit historischen Daten) oder im Live-Modus (simuliert) betrieben werden.

### Ist dieser Bot produktionsreif?
Die Master-Version ist architektonisch produktionsreif, simuliert aber derzeit die Marktdaten. Für echtes Live-Trading müsste die API-Integration zu einer Börse (Alpaca, Binance, etc.) implementiert werden.

### Kann ich damit echtes Geld verdienen?
**WARNUNG:** Trading birgt erhebliche Risiken. Dieser Bot ist primär zu Bildungszwecken gedacht. Teste ausgiebig mit Paper-Trading bevor du echtes Kapital riskierst. Keine Garantie für Profite.

### Welche Börsen werden unterstützt?
**PRIMARY**: Binance API (Krypto) - vollständig integriert, 24/7 Trading
**LEGACY**: Alpaca API (Aktien/ETFs/Krypto) - für Abwärtskompatibilität
**ZUKUNFT**: Interactive Brokers, andere via CCXT

Der Bot nutzt primär Binance für Live-Trading. Alpaca-Integration ist weiterhin verfügbar für Legacy-Support.

---

## Installation & Setup

### Ich bekomme "ModuleNotFoundError"
```bash
# Lösung: Installiere Dependencies
pip install -r requirements.txt

# Wenn das nicht hilft, nutze pip3:
pip3 install -r requirements.txt
```

### Muss ich API-Keys haben?
**Nein**, für Backtests und simuliertes Live-Trading sind keine API-Keys nötig. Der Bot läuft im Simulationsmodus ohne Keys.

**Ja**, für echtes Live-Trading mit Binance brauchst du API Keys.

### Wo speichere ich meine API-Keys?
**NEU**: Erstelle eine `keys.env` Datei im Hauptverzeichnis:
```env
# keys.env
BINANCE_API_KEY=dein_binance_api_key_hier
BINANCE_SECRET_KEY=dein_binance_secret_hier

# Für Testnet (Paper Trading)
BINANCE_TESTNET_API_KEY=dein_testnet_key_hier
BINANCE_TESTNET_SECRET_KEY=dein_testnet_secret_hier
```

**Alternativ**: Nutze `.env` Datei (Kopie von `.env.example`):
```env
BINANCE_API_KEY=dein_binance_api_key_hier
BINANCE_SECRET_KEY=dein_binance_secret_hier
```

**Wichtig:** 
- `keys.env` und `.env` sind bereits in `.gitignore`
- Niemals API Keys in Git committen!
- Für Production: Nutze Umgebungsvariablen des Systems

### Welche Python-Version brauche ich?
- **Minimum:** Python 3.8
- **Empfohlen:** Python 3.10 oder 3.11
- **Check:** `python --version`

---

## Konfiguration

### Wie ändere ich die Trading-Parameter?
Öffne `config.py` und passe die Werte in der `TradingConfig` Klasse an:
```python
initial_capital: float = 10000.0  # Startkapital
trade_size: float = 100.0         # Größe pro Trade
```

### Wie aktiviere/deaktiviere ich Strategien?
In `config.py`:
```python
active_strategies: list = [
    "rsi",           # ✓ Aktiviert
    "ema_crossover"  # ✓ Aktiviert
    # "ma_crossover" # ✗ Deaktiviert (auskommentiert)
]
```

### Was ist AND vs OR Logic?
- **AND Logic:** Alle aktiven Strategien müssen das gleiche Signal geben
  - Beispiel: Wenn RSI sagt BUY und EMA sagt BUY → BUY Signal
  - Konservativ, weniger Trades
  
- **OR Logic:** Mindestens eine Strategie muss Signal geben
  - Beispiel: Wenn RSI sagt BUY (egal was EMA sagt) → BUY Signal
  - Aggressiv, mehr Trades

Setzen in `config.py`:
```python
cooperation_logic: str = "OR"  # oder "AND"
```

### Welche Strategien gibt es?

1. **MA Crossover** (Moving Average Crossover)
   - Trend-Following
   - Best für: Mittelfristige Trends
   - Parameter: `short_window`, `long_window`

2. **RSI** (Relative Strength Index)
   - Mean Reversion
   - Best für: Seitwärtsmärkte
   - Parameter: `window`, `oversold_threshold`, `overbought_threshold`

3. **Bollinger Bands**
   - Volatility Breakout
   - Best für: Hohe Volatilität
   - Parameter: `window`, `std_dev`

4. **EMA Crossover**
   - Fast Trend-Following
   - Best für: Daytrading
   - Parameter: `short_window`, `long_window`

5. **LSOB (Long-Short On Breakout)** 🆕
   - Breakout Strategy mit Risk Management
   - Best für: Intraday bis mittelfristig
   - Features: ATR-basierte Stops, Volume-Bestätigung, Volatility-Filter
   - Parameter: `bb_window`, `atr_window`, `stop_loss_atr_mult`, `take_profit_atr_mult`

4. **EMA Crossover** (Exponential Moving Average)
   - Schnelle Trends
   - Best für: Daytrading
   - Parameter: `short_window`, `long_window`

---

## Backtesting

### Wie führe ich einen Backtest durch?
```bash
python backtester.py
```
Dann wähle:
- `[1]` CSV-Datei mit historischen Daten laden
- `[2]` Simulierte Daten generieren (für Testing)

### Welches CSV-Format brauche ich?
```csv
timestamp,open,high,low,close,volume
2024-01-01 00:00:00,30000.0,30100.0,29900.0,30050.0,1250.5
```

**Anforderungen:**
- Spalten: timestamp, open, high, low, close, volume
- Numerische Werte (keine Strings außer timestamp)
- Keine NaN-Werte
- OHLC-Logik muss stimmen (High >= Low, etc.)

### Wo bekomme ich historische Daten?
- **Krypto:** [CryptoDataDownload](https://www.cryptodatadownload.com/)
- **Aktien:** [Yahoo Finance](https://finance.yahoo.com/) (mit yfinance Python-Package)
- **Forex:** [Dukascopy](https://www.dukascopy.com/swiss/english/marketwatch/historical/)

### Mein Backtest zeigt schlechte Performance
**Mögliche Gründe:**

1. **Falsche Parameter**
   - Teste verschiedene Parameter-Kombinationen
   - Nutze Parameter-Presets (Conservative, Balanced, Aggressive)

2. **Ungeeignete Strategie für Marktphase**
   - Trend-Strategien funktionieren schlecht in Seitwärtsmärkten
   - Mean-Reversion funktioniert schlecht in starken Trends
   - Kombiniere verschiedene Strategien!

3. **Overfitting**
   - Nicht zu sehr auf historische Daten optimieren
   - Teste auf Out-of-Sample Daten

4. **Zu wenig Daten**
   - Mindestens 200+ Kerzen für aussagekräftige Ergebnisse
   - Mehr Daten = bessere Statistik

### Was bedeuten die Performance-Metriken?

- **Total P&L:** Gesamt Profit/Loss in $
- **ROI:** Return on Investment in % (P&L / Initial Capital)
- **Win Rate:** Prozentsatz gewinnender Trades
- **Best/Worst Trade:** Bester/Schlechtester einzelner Trade
- **Profit Factor:** Summe Gewinne / Summe Verluste (>1 = profitabel)

---

## Live-Trading

### Wie starte ich Live-Trading?
```bash
python main.py
```
**Wichtig:** Dies simuliert nur Live-Trading mit fortlaufenden Daten. Keine echte Börsen-Verbindung!

### Wie stoppe ich den Bot?
Drücke `Ctrl+C` für sauberes Shutdown. Der Bot zeigt dann einen Final Report.

### Wo finde ich die Trade-History?
In `data/trades.csv` - Alle Trades werden automatisch protokolliert.

### Wie oft updated der Bot?
Standard: Alle 60 Sekunden (konfigurierbar in `config.py`):
```python
update_interval: int = 60  # Sekunden
```

---

## Strategien & Parameter

### Wie finde ich die besten Parameter?
1. **Manuelles Testing:**
   - Teste verschiedene Parameter-Kombinationen im Backtest
   - Dokumentiere Ergebnisse
   - Wähle Parameter mit bestem Risk/Reward

2. **Grid Search** (Fortgeschritten):
   - Systematisch alle Kombinationen testen
   - Nutze Python-Script dafür (kann ich bereitstellen)

3. **Walk-Forward Analysis:**
   - Optimiere auf Trainings-Periode
   - Teste auf Test-Periode
   - Verhindert Overfitting

### Was sind gute Parameter für Anfänger?
Nutze den **Balanced Preset**:
```python
"ma_crossover": {"short_window": 20, "long_window": 50}
"rsi": {"window": 14, "oversold": 35, "overbought": 65}
"bollinger_bands": {"window": 20, "std_dev": 2.0}
"ema_crossover": {"short_window": 9, "long_window": 21}
```

### Sollte ich alle Strategien gleichzeitig nutzen?
**Kommt drauf an:**

- **Mehr Strategien + AND Logic:** Sehr konservativ, extrem wenige Trades
- **Mehr Strategien + OR Logic:** Sehr viele Signale, eventuell zu viel Rauschen
- **2-3 Strategien + OR Logic:** Guter Kompromiss (empfohlen)

**Empfehlung für Start:**
```python
active_strategies: ["rsi", "ema_crossover"]
cooperation_logic: "OR"
```

### Kann ich eigene Strategien hinzufügen?
**Ja!** Siehe README.md Sektion "Strategien anpassen". Kurz:

1. Erstelle neue Klasse in `strategy.py`:
```python
class MyStrategy(BaseStrategy):
    def generate_signal(self, df):
        # Deine Logik hier
        return 1  # BUY, 0 = HOLD, -1 = SELL
```

2. Registriere in `STRATEGY_MAP`
3. Aktiviere in `config.py`

---

## Fehlerbehebung

### "Ungültige Daten" Fehler beim Backtest
**Prüfe deine CSV:**
```python
import pandas as pd

df = pd.read_csv('deine_datei.csv')
print(df.head())
print(df.info())
print(df.isnull().sum())  # Zeigt NaN-Werte
```

**Häufige Probleme:**
- Fehlende Spalten
- NaN-Werte (→ `df.dropna()`)
- Falsche Datentypen (→ `df['close'].astype(float)`)
- OHLC-Logik verletzt

### Bot generiert keine Signale
**Mögliche Ursachen:**

1. **AND Logic + viele Strategien:**
   ```python
   # Teste erstmal mit OR Logic
   cooperation_logic: "OR"
   ```

2. **Extreme Parameter:**
   ```python
   # RSI mit oversold=5 wird nie triggern
   # Nutze Standard-Werte (30/70 oder 35/65)
   ```

3. **Zu wenig Daten:**
   ```python
   # MA(200) braucht mindestens 200 Kerzen
   # Bei wenig Daten: Kleinere Windows nutzen
   ```

### Performance ist schlecht
Siehe "Mein Backtest zeigt schlechte Performance" oben.

### "Permission Denied" bei Log/Data Files
**Windows:**
```cmd
# Als Administrator ausführen
# ODER Ordner-Rechte prüfen
```

**Linux/Mac:**
```bash
chmod -R 755 data logs
```

---

## Erweiterte Nutzung

### Kann ich mehrere Symbole handeln?
Aktuell: Nein. Aber die Architektur ist vorbereitet. Für Multi-Symbol Trading:
1. Loop über Symbole in `main.py`
2. Separate Position-Tracking pro Symbol
3. Portfolio-basiertes Risk-Management

### Wie implementiere ich Stop-Loss?
In `main.py`, in der `process_signal` Methode:
```python
# Nach BUY
stop_loss_price = entry_price * (1 - config.stop_loss_percent / 100)

# Im Loop prüfen
if current_price <= stop_loss_price:
    # SELL ausführen
```

### Wie integriere ich Binance API?
**NEU**: Binance ist bereits vollständig integriert!

1. **API Keys holen:**
   - Für Testnet (empfohlen): https://testnet.binance.vision/
   - Für Production: https://www.binance.com/ (Vorsicht!)
   - Erstelle API Keys mit nur Trading-Rechten (KEINE Withdrawal-Rechte!)

2. **Keys konfigurieren:**
   ```bash
   # Erstelle keys.env Datei
   cp keys.env.template keys.env
   
   # Füge deine Keys ein:
   BINANCE_API_KEY=dein_api_key
   BINANCE_SECRET_KEY=dein_secret_key
   
   # Für Testnet:
   BINANCE_TESTNET_API_KEY=dein_testnet_key
   BINANCE_TESTNET_SECRET_KEY=dein_testnet_secret
   ```

3. **Bot starten:**
   ```bash
   # Paper Trading (Testnet)
   python3 main.py
   
   # Golden Cross Bot
   python3 golden_cross_bot.py --mode paper --symbol BTCUSDT
   ```
   
Der Bot erkennt automatisch die API Keys und nutzt Binance!

**WICHTIG**: Starte IMMER mit Testnet zum Testen!

### Wie erstelle ich eine Web-GUI?
Nutze FastAPI + React:
1. FastAPI Backend (API Endpoints für Trades, Status, etc.)
2. React Frontend (Charts mit Plotly/Chart.js)
3. WebSocket für Live-Updates

---

## Performance & Optimierung

### Bot ist zu langsam
**Optimierungen:**

1. **Weniger Indikatoren berechnen:**
   ```python
   # Deaktiviere ungenutzte Strategien
   active_strategies: ["rsi"]  # Nur eine
   ```

2. **Größere Update-Intervalle:**
   ```python
   update_interval: 300  # 5 Minuten statt 60 Sekunden
   ```

3. **Caching für Indikatoren** (fortgeschritten)

### Zu viele Log-Dateien
Die Logs rotieren automatisch (max 5 Backups). Ältere Logs können gelöscht werden:
```bash
# Windows
del logs\*.log.1
del logs\*.log.2

# Linux/Mac
rm logs/*.log.[1-5]
```

---

## Sicherheit & Best Practices

### Sollte ich API-Keys im Code haben?
**NIEMALS!** Nutze immer `.env` Dateien:
```python
# FALSCH
api_key = "mein_geheimer_key"

# RICHTIG
api_key = os.getenv("ALPACA_API_KEY")
```

### Wie sichere ich meine Trades?
1. **Backup der Trade-CSV:**
   ```bash
   cp data/trades.csv backups/trades_2024-10-08.csv
   ```

2. **Git für Code** (ohne `.env`!)

3. **Datenbank** für Production (PostgreSQL empfohlen)

### Was passiert bei Netzwerk-Ausfall?
Aktuell: Bot stoppt. Für Production:
1. Retry-Logik für API-Calls
2. Error-Recovery
3. Offene Positionen speichern & wiederherstellen

---

## Sonstiges

### Kann ich den Bot auf einem Server laufen lassen?
**Ja!** 
```bash
# Linux Server
nohup python main.py > output.log 2>&1 &

# Mit tmux/screen (empfohlen)
tmux new -s trading_bot
python main.py
# Ctrl+B, dann D zum Detachen
```

### Wo finde ich weitere Hilfe?
1. **README.md** - Vollständige Dokumentation
2. **EVOLUTION_ANALYSIS.md** - Architektur-Details
3. **Code-Kommentare** - Ausführlich dokumentiert
4. **demo.py** - Interaktive Beispiele

### Kann ich zur Entwicklung beitragen?
Gerne! Fork das Projekt und erstelle Pull Requests für:
- Neue Strategien
- Bug-Fixes
- Dokumentations-Verbesserungen
- Feature-Erweiterungen

---

## Kontakt & Support

Bei weiteren Fragen:
1. Schaue erst in diese FAQ
2. Prüfe die Log-Dateien (`logs/trading_bot.log`)
3. Teste mit `python test_system.py`
4. Nutze `python demo.py` für Beispiele

---

**Viel Erfolg mit dem Trading-Bot! 📈🚀**
