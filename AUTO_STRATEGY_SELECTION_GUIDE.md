# 🎯 Automatische Strategie-Auswahl - Vollständiger Guide

**Intelligente, automatisierte Auswahl der optimalen Trading-Strategie für maximalen ROI**

---

## 📋 Überblick

Die automatische Strategie-Auswahl analysiert alle verfügbaren Trading-Strategien mittels Backtest und wählt automatisch die beste Strategie für den Live-Betrieb. Die Auswahl wird dokumentiert und direkt in die Live-Konfiguration übernommen.

### ✨ Key Features

- ✅ **Vollautomatisch**: Keine manuelle Eingabe erforderlich
- ✅ **Backtest aller Strategien**: Umfassende Analyse mit identischen Daten
- ✅ **Multi-Kriterien-Bewertung**: ROI, Sharpe, Calmar, Drawdown, Win Rate
- ✅ **Automatische Konfiguration**: Beste Strategie wird in `config/live_risk.yaml` gesetzt
- ✅ **Detaillierte Dokumentation**: Logs und CSV-Export für Nachvollziehbarkeit
- ✅ **Flexible Integration**: Standalone oder Teil des Setup-Prozesses

---

## 🚀 Verwendung

### Option 1: Standalone-Script (Empfohlen)

Das dedizierte Script `auto_select_strategy.py` ermöglicht vollautomatische Strategie-Auswahl:

#### Windows (PowerShell)
```powershell
# Einfache Ausführung mit generierten Daten
.\scripts\auto_select_strategy.ps1

# Mit benutzerdefinierten Parametern
.\scripts\auto_select_strategy.ps1 --min-trades 15 --initial-capital 50000

# Mit historischen Daten aus CSV
.\scripts\auto_select_strategy.ps1 --data-file data/historical_btc.csv

# Nur Analyse, ohne Config-Update
.\scripts\auto_select_strategy.ps1 --no-update-config

# Leise Ausgabe (für Cron-Jobs)
.\scripts\auto_select_strategy.ps1 --quiet
```

#### Linux/macOS (Bash)
```bash
# Direkte Python-Ausführung
python scripts/auto_select_strategy.py

# Mit Parametern
python scripts/auto_select_strategy.py --min-trades 15 --initial-capital 50000
```

### Option 2: Integration in Setup-Wizard

Der Setup-Wizard unterstützt jetzt automatische Strategie-Auswahl:

#### Vollautomatischer Modus
```powershell
# Windows: Automatische Strategie-Auswahl ohne Nachfragen
.\venv\Scripts\python.exe scripts\setup_live.py --auto-strategy

# Nur Strategie-Auswahl, kein API-Key-Setup
.\venv\Scripts\python.exe scripts\setup_live.py --strategy-only --auto-strategy
```

#### Interaktiver Modus (bisheriges Verhalten)
```powershell
# Normale Setup-Wizard mit Benutzerinteraktion
.\scripts\setup_live.ps1
```

---

## 📊 Analysierte Strategien

Die Auswahl umfasst **9 vorkonfigurierte Strategien**:

| Nr. | Strategie | Typ | Zeithorizont |
|-----|-----------|-----|--------------|
| 1 | **Golden Cross (50/200)** | Trend-Following | Langfristig |
| 2 | **MA Crossover (20/50)** | Trend-Following | Mittelfristig |
| 3 | **MA Crossover (10/30)** | Trend-Following | Kurzfristig |
| 4 | **RSI Mean Reversion** | Mean Reversion | Kurzfristig |
| 5 | **RSI Conservative** | Mean Reversion | Kurzfristig |
| 6 | **EMA Crossover (9/21)** | Trend-Following | Sehr kurzfristig |
| 7 | **EMA Crossover (12/26)** | Trend-Following | Kurzfristig |
| 8 | **Bollinger Bands** | Volatility Breakout | Variable |
| 9 | **Bollinger Bands Wide** | Volatility Breakout | Variable |

---

## 📈 Bewertungskriterien

### Score-Berechnung

Jede Strategie erhält einen gewichteten Score basierend auf 5 Metriken:

```
Score = (ROI × 30%) + 
        (Sharpe Ratio × 25%) + 
        (Calmar Ratio × 20%) + 
        (Win Rate × 15%) + 
        (Drawdown × 10%)
```

### Metriken im Detail

| Metrik | Gewichtung | Beschreibung | Ziel |
|--------|------------|--------------|------|
| **ROI** | 30% | Return on Investment | Maximieren |
| **Sharpe Ratio** | 25% | Risk-adjusted Returns | Maximieren |
| **Calmar Ratio** | 20% | Return / Max Drawdown | Maximieren |
| **Win Rate** | 15% | Erfolgreiche Trades (%) | Maximieren |
| **Max Drawdown** | 10% | Maximaler Verlust (%) | Minimieren |

### Robustheit-Filter

Strategien müssen folgende Mindestkriterien erfüllen:
- **Mindestanzahl Trades**: Default 10 (konfigurierbar via `--min-trades`)
- **Erfolgreicher Backtest**: Keine Fehler bei Signalgenerierung
- **Valide Metriken**: Alle Kennzahlen müssen berechenbar sein

---

## 🔧 Konfigurationsoptionen

### Command-Line Parameter

```bash
python scripts/auto_select_strategy.py [OPTIONS]

Optionen:
  --data-file PATH          CSV-Datei mit historischen OHLCV-Daten
  --min-trades N            Mindestanzahl Trades (default: 10)
  --initial-capital N       Startkapital für Backtest (default: 10000)
  --trade-size N            Handelsgröße (default: 100)
  --export-csv PATH         Export Ranking als CSV (default: data/strategy_ranking.csv)
  --no-update-config        Strategie nicht automatisch in config schreiben
  --quiet                   Weniger Ausgaben (für Automatisierung)
```

### Beispiele

```bash
# Konservative Auswahl (höhere Robustheit)
python scripts/auto_select_strategy.py --min-trades 20

# Mit größerem Kapital
python scripts/auto_select_strategy.py --initial-capital 100000 --trade-size 500

# Nur Analyse, keine Konfigurationsänderung
python scripts/auto_select_strategy.py --no-update-config

# Mit historischen Daten
python scripts/auto_select_strategy.py --data-file data/btc_2023_2024.csv

# Für Cron-Job (minimale Ausgabe)
python scripts/auto_select_strategy.py --quiet
```

---

## 📝 Output & Dokumentation

### Console Output

```
======================================================================
🎯 AUTOMATISCHE STRATEGIE-AUSWAHL
======================================================================

📁 Lade Daten aus: data/historical_btc.csv
✓ 2000 Datenpunkte geladen

⚙️  Parameter:
   Initial Capital: $10,000.00
   Trade Size: 100.0
   Min Trades: 10

🔍 Analysiere Strategien...

======================================================================
🎯 AUTOMATISCHE STRATEGIE-AUSWAHL
======================================================================
Datenpunkte: 2000
Periode: 2023-01-01 00:00:00 bis 2024-12-31 23:45:00
Mindestanzahl Trades: 10
======================================================================

[... Backtest läuft ...]

======================================================================
📊 STRATEGIE-RANKING
======================================================================

Rank  Strategy                      Score      ROI         Sharpe    Win Rate   
--------------------------------------------------------------------------------
🥇 #1  MA Crossover (10/30)          78.23     +1801.64%   2.62       42.9%
🥈 #2  Bollinger Bands               61.57     +1379.06%   2.21       36.4%
🥉 #3  EMA Crossover (9/21)          58.94     +1245.33%   2.08       40.0%
   #4  Golden Cross (50/200)         52.18      +987.45%   1.85       45.5%
   #5  RSI Mean Reversion            48.76      +756.89%   1.62       52.3%
--------------------------------------------------------------------------------

📋 TOP 3 DETAILS:

1. MA Crossover (10/30) (Score: 78.23)
   ROI:          +1801.64%
   Sharpe:       2.62
   Calmar:       3.44
   Max DD:       -524.29%
   Win Rate:     42.9%
   Avg Trade:    $8579.24
   Total Trades: 21

[... weitere Details ...]

======================================================================
🏆 EMPFOHLENE STRATEGIE
======================================================================
✓ MA Crossover (10/30)
  Score:        78.23/100
  ROI:          +1801.64%
  Sharpe:       2.62
  Calmar:       3.44
  Max DD:       -524.29%
  Win Rate:     42.9%
  Total Trades: 21
======================================================================

✓ Ranking exportiert: data/strategy_ranking.csv
✅ Strategie in config/live_risk.yaml aktualisiert: MA Crossover (10/30)

======================================================================
✅ STRATEGIE-AUSWAHL ABGESCHLOSSEN
======================================================================

🏆 Empfohlene Strategie: MA Crossover (10/30)
   Score:        78.23/100
   ROI:          +1801.64%
   Sharpe Ratio: 2.62
   Calmar Ratio: 3.44
   Max Drawdown: -524.29%
   Win Rate:     42.9%
   Total Trades: 21

📝 Konfiguration aktualisiert: config/live_risk.yaml
📊 Ranking exportiert: data/strategy_ranking.csv

======================================================================
```

### CSV Export

Das Ranking wird automatisch als CSV exportiert:

**`data/strategy_ranking.csv`**:
```csv
strategy_name,score,roi,sharpe_ratio,calmar_ratio,max_drawdown,win_rate,total_trades,avg_trade,final_capital
MA Crossover (10/30),78.23,1801.64,2.62,3.44,-524.29,42.9,21,8579.24,190164.14
Bollinger Bands,61.57,1379.06,2.21,1.15,-1197.35,36.4,11,12536.95,147906.40
EMA Crossover (9/21),58.94,1245.33,2.08,2.87,-433.89,40.0,15,8302.20,134533.12
...
```

### Konfigurationsdatei

Die ausgewählte Strategie wird automatisch in **`config/live_risk.yaml`** gesetzt:

```yaml
pairs: BTCUSDT
strategy: MA Crossover (10/30)  # ← Automatisch aktualisiert
max_risk_per_trade: 0.005
daily_loss_limit: 0.01
max_open_exposure: 0.05
allowed_order_types: LIMIT_ONLY
max_slippage: 0.003
```

---

## 🔄 Integration in Workflows

### Cron-Job (Tägliche Strategie-Optimierung)

**Windows (Task Scheduler)**:
```powershell
# Task erstellen für tägliche Ausführung um 2:00 Uhr
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\path\to\ai.traiding\scripts\auto_select_strategy.ps1 --quiet"

$trigger = New-ScheduledTaskTrigger -Daily -At 2am

Register-ScheduledTask -TaskName "AI Trading - Daily Strategy Optimization" `
    -Action $action -Trigger $trigger
```

**Linux/macOS (Crontab)**:
```bash
# Täglich um 2:00 Uhr
0 2 * * * cd /path/to/ai.traiding && python scripts/auto_select_strategy.py --quiet >> logs/strategy_selection.log 2>&1
```

### CI/CD Pipeline

**GitHub Actions**:
```yaml
name: Weekly Strategy Optimization

on:
  schedule:
    - cron: '0 2 * * 0'  # Jeden Sonntag um 2:00 Uhr

jobs:
  optimize-strategy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run strategy selection
        run: python scripts/auto_select_strategy.py --quiet
      
      - name: Commit updated config
        run: |
          git config user.name "Bot"
          git config user.email "bot@example.com"
          git add config/live_risk.yaml data/strategy_ranking.csv
          git commit -m "chore: automated strategy optimization"
          git push
```

### Pre-Trading Check

Als Teil des Live-Trading-Starts:

```powershell
# scripts/start_live_prod.ps1 (erweitert)

# 1. Strategie-Optimierung durchführen
Write-Host "🎯 Optimiere Strategie..." -ForegroundColor Yellow
.\scripts\auto_select_strategy.ps1 --quiet

# 2. Preflight Checks
Write-Host "✅ Führe Preflight Checks durch..." -ForegroundColor Yellow
.\venv\Scripts\python.exe scripts\live_preflight.py

# 3. Live-Trading starten
Write-Host "🚀 Starte Live-Trading..." -ForegroundColor Green
.\venv\Scripts\python.exe main.py --live
```

---

## 🧪 Testing & Validation

### Test mit verschiedenen Datenquellen

```bash
# Test mit generierten Daten (Standard)
python scripts/auto_select_strategy.py

# Test mit historischen Daten
python scripts/auto_select_strategy.py --data-file data/btc_historical.csv

# Test mit verschiedenen Parametern
python scripts/auto_select_strategy.py --min-trades 5 --initial-capital 5000
python scripts/auto_select_strategy.py --min-trades 20 --initial-capital 100000
```

### Dry-Run (ohne Config-Update)

```bash
# Nur Analyse, keine Konfigurationsänderung
python scripts/auto_select_strategy.py --no-update-config
```

---

## 📚 Weitere Ressourcen

- **[STRATEGY_SELECTION_GUIDE.md](STRATEGY_SELECTION_GUIDE.md)** - Detaillierte technische Dokumentation
- **[STRATEGY_SELECTION_IMPLEMENTATION_SUMMARY.md](STRATEGY_SELECTION_IMPLEMENTATION_SUMMARY.md)** - Implementation Details
- **[BACKTESTING_GUIDE.md](BACKTESTING_GUIDE.md)** - Backtest-Engine Dokumentation
- **[LIVE_TRADING_SETUP_GUIDE.md](LIVE_TRADING_SETUP_GUIDE.md)** - Live-Trading Setup

---

## ❓ FAQ

### Wie oft sollte die Strategie-Auswahl durchgeführt werden?

**Empfehlung**: Wöchentlich oder monatlich, je nach Marktvolatilität. Zu häufiges Wechseln kann zu Overfitting führen.

### Kann ich eigene Strategien hinzufügen?

Ja! Implementiere deine Strategie in `strategy.py` und füge sie in `StrategySelector.setup_strategies()` hinzu.

### Was passiert bei Gleichstand im Score?

Die Strategie mit dem höheren ROI wird bevorzugt.

### Wie kann ich die Gewichtung anpassen?

Programmatisch durch Übergabe von `weights` beim Erstellen des `StrategySelector`:

```python
custom_weights = {
    'roi': 0.40,           # Mehr Fokus auf ROI
    'sharpe_ratio': 0.30,  # Mehr Fokus auf Sharpe
    'calmar_ratio': 0.15,
    'win_rate': 0.10,
    'max_drawdown': 0.05
}

selector = StrategySelector(weights=custom_weights)
```

### Funktioniert das auch im Testnet?

Ja! Die Strategie-Auswahl ist unabhängig vom Trading-Modus und funktioniert mit simulierten, historischen oder Live-Daten.

---

**Made for Windows ⭐ | PowerShell-First | Fully Automated | DRY_RUN Default**
