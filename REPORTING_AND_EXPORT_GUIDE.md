# 📊 Reporting & Export Guide

**Erweiterte Reporting-Funktionen mit Performance-Metriken und Export**

Dieses Dokument beschreibt die neuen Reporting- und Export-Funktionen für umfassende Performance-Analyse.

---

## 🎯 Features

### ✅ Performance-Metriken
- **ROI** (Return on Investment)
- **Sharpe Ratio** - Risiko-adjustierte Performance
- **Profit Factor** - Verhältnis Gewinn/Verlust
- **Maximum Drawdown** - Größter Kapitalrückgang
- **Calmar Ratio** - Return/Drawdown Verhältnis
- **Volatilität** - Standardabweichung der Renditen
- **Win Rate** - Prozentsatz gewinnbringender Trades
- **Durchschnittliche Trade-Dauer**

### ✅ Export-Formate
- **CSV** - Kompatibel mit Excel, Python Pandas
- **JSON** - Für API-Integration und Web-Dashboards

### ✅ Report-Typen
1. **Performance Report** - Alle Metriken zusammengefasst
2. **Trade History** - Chronologische Liste aller Trades
3. **Detailed Trade History** - Mit kumulativen Metriken

---

## 🚀 Quick Start

### Einfaches Reporting

```python
from utils import ReportingModule

# Erstelle Reporting-Modul
module = ReportingModule("data/trades.csv")

# Generiere Report
report = module.generate_report(initial_capital=10000.0)

# Zeige Zusammenfassung
module.print_report_summary()
```

### Export in alle Formate

```python
# Exportiere alle Reports
exported_files = module.export_all(
    output_dir="data/reports",
    prefix="monthly_report"
)

print(f"Exportiert: {len(exported_files)} Dateien")
```

---

## 📖 Detaillierte Verwendung

### 1. ROI-Berechnung

```python
from utils import calculate_roi

initial_capital = 10000.0
final_capital = 12000.0

roi = calculate_roi(initial_capital, final_capital)
print(f"ROI: {roi:.2f}%")  # Output: ROI: 20.00%
```

### 2. Umfassender Performance-Report

```python
from utils import generate_comprehensive_report, load_trades_from_csv

# Lade Trades
trades = load_trades_from_csv("data/trades.csv")

# Erstelle Equity Curve (optional, aber empfohlen)
equity_curve = [10000]
capital = 10000
for trade in trades:
    capital += float(trade.get('pnl', 0))
    equity_curve.append(capital)

# Generiere Report
report = generate_comprehensive_report(
    trades,
    equity_curve=equity_curve,
    initial_capital=10000.0
)

# Zugriff auf Metriken
print(f"ROI: {report['roi']:.2f}%")
print(f"Sharpe Ratio: {report['sharpe_ratio']:.4f}")
print(f"Win Rate: {report['win_rate']:.2f}%")
print(f"Max Drawdown: {report['max_drawdown']:.2f}%")
```

### 3. Export als CSV

```python
from utils import export_report_to_csv, export_trade_history_with_metrics

# Export Performance Report
export_report_to_csv(
    report,
    filepath="data/performance_report.csv"
)

# Export detaillierte Trade-History
export_trade_history_with_metrics(
    trades,
    filepath="data/trade_history_detailed.csv"
)
```

### 4. Export als JSON

```python
from utils import export_report_to_json, export_trades_to_json

# Export Performance Report als JSON
export_report_to_json(
    report,
    filepath="data/performance_report.json",
    pretty=True  # Formatiert für Lesbarkeit
)

# Export Trade-History als JSON
export_trades_to_json(
    trades,
    filepath="data/trades.json",
    pretty=True
)
```

### 5. ReportingModule - Kompletter Workflow

```python
from utils import ReportingModule

# Initialisiere Modul
module = ReportingModule("data/trades.csv")

# Schritt 1: Lade Trades
trades = module.load_trades()
print(f"{len(trades)} Trades geladen")

# Schritt 2: Berechne Equity Curve
equity_curve = module.calculate_equity_curve(initial_capital=10000.0)

# Schritt 3: Generiere Report
report = module.generate_report(initial_capital=10000.0)

# Schritt 4: Zeige Zusammenfassung
module.print_report_summary()

# Schritt 5: Export alle Formate
exported_files = module.export_all(
    output_dir="data/reports",
    prefix="weekly"
)
```

---

## 📊 Report-Metriken im Detail

### Financial Metrics

| Metrik | Beschreibung | Interpretation |
|--------|--------------|----------------|
| **ROI** | Return on Investment | Gewinn/Verlust in % des Startkapitals |
| **Total P&L** | Profit & Loss | Absoluter Gewinn/Verlust in $ |
| **Win Rate** | Gewinnrate | % der profitablen Trades |
| **Best Trade** | Bester Trade | Höchster einzelner Gewinn |
| **Worst Trade** | Schlechtester Trade | Größter einzelner Verlust |
| **Avg P&L** | Durchschn. P&L | Durchschnittlicher Gewinn/Verlust pro Trade |

### Risk Metrics

| Metrik | Beschreibung | Gut | Schlecht |
|--------|--------------|-----|----------|
| **Sharpe Ratio** | Risiko-adjustierte Performance | > 1.5 | < 0.5 |
| **Max Drawdown** | Größter Kapitalrückgang | < 10% | > 30% |
| **Calmar Ratio** | Return/Drawdown Verhältnis | > 1.0 | < 0.5 |
| **Volatilität** | Schwankung der Renditen | < 0.3 | > 0.6 |
| **Profit Factor** | Gewinn/Verlust Verhältnis | > 2.0 | < 1.0 |

### Trading Statistics

| Metrik | Beschreibung |
|--------|--------------|
| **Total Trades** | Anzahl aller Trades |
| **Real Money Trades** | Anzahl Echtgeld-Trades |
| **Dry-Run Trades** | Anzahl Simulation-Trades |
| **Avg Trade Duration** | Durchschnittliche Haltedauer in Sekunden |

---

## 🔍 Export-Formate im Detail

### CSV-Format

**Performance Report CSV:**
```csv
metric,value
total_trades,10.0000
total_pnl,500.0000
roi,5.0000
win_rate,60.0000
sharpe_ratio,1.5000
...
```

**Detailed Trade History CSV:**
```csv
trade_number,timestamp,symbol,order_type,price,quantity,pnl,cumulative_pnl,capital,...
1,2025-10-15T10:00:00,BTC/USDT,BUY,30000.0,0.1,0.0,0.0,10000.0,...
2,2025-10-15T11:00:00,BTC/USDT,SELL,31000.0,0.1,100.0,100.0,10100.0,...
...
```

### JSON-Format

**Performance Report JSON:**
```json
{
  "total_trades": 10,
  "total_pnl": 500.0,
  "roi": 5.0,
  "win_rate": 60.0,
  "sharpe_ratio": 1.5,
  "max_drawdown": -10.5,
  "report_generated_at": "2025-10-15T10:00:00"
}
```

**Trade History JSON:**
```json
[
  {
    "timestamp": "2025-10-15T10:00:00",
    "symbol": "BTC/USDT",
    "order_type": "BUY",
    "price": 30000.0,
    "quantity": 0.1,
    "pnl": 0.0,
    "is_real_money": false
  },
  ...
]
```

---

## 💡 Best Practices

### 1. Regelmäßige Reports

```python
from datetime import datetime

# Erstelle timestamped Report
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
module = ReportingModule("data/trades.csv")
module.export_all(prefix=f"daily_{timestamp}")
```

### 2. Echtgeld vs. Dry-Run trennen

```python
# Reports zeigen automatisch beide Kategorien
report = module.generate_report()
print(f"Real Money Trades: {report['total_real_money_trades']}")
print(f"Dry-Run Trades: {report['total_dry_run_trades']}")
```

### 3. Performance-Überwachung

```python
# Automatische Warnungen bei schlechter Performance
if report['sharpe_ratio'] < 0.5:
    print("⚠️  WARNING: Niedrige Sharpe Ratio!")

if report['max_drawdown'] < -20.0:
    print("⚠️  WARNING: Hoher Drawdown!")

if report['win_rate'] < 40.0:
    print("⚠️  WARNING: Niedrige Win Rate!")
```

### 4. Integration in Trading-Bot

```python
from utils import ReportingModule, TradeLogger

# Im Trading-Bot
logger = TradeLogger("data/trades.csv")

# Nach jedem Trade
logger.log_trade(...)

# Am Ende des Trading-Tages
module = ReportingModule("data/trades.csv")
report = module.generate_report()

# Export für Analyse
module.export_all(prefix=f"daily_{datetime.now().strftime('%Y%m%d')}")
```

---

## 🧪 Testing

### Unit Tests

Alle Funktionen sind getestet in `test_reporting_export.py`:

```bash
# Alle Tests ausführen
python3 test_reporting_export.py

# Einzelne Test-Klasse
python3 -m unittest test_reporting_export.TestReportingModule
```

### Demo ausführen

```bash
# Komplette Demo mit allen Features
python3 demo_reporting_export.py
```

---

## 📁 Dateistruktur

```
data/
├── trades.csv                    # Trade-Log (TradeLogger)
├── reports/                      # Export-Verzeichnis
│   ├── {prefix}_performance_report.csv
│   ├── {prefix}_performance_report.json
│   ├── {prefix}_trades.csv
│   ├── {prefix}_trades.json
│   └── {prefix}_trade_history_detailed.csv
└── ...
```

---

## 🔧 API-Referenz

### Funktionen

#### `calculate_roi(initial_capital, final_capital) -> float`
Berechnet Return on Investment in Prozent.

#### `generate_comprehensive_report(trades, equity_curve, initial_capital) -> dict`
Erstellt umfassenden Performance-Report mit allen Metriken.

#### `export_report_to_csv(report, filepath) -> str`
Exportiert Report als CSV-Datei.

#### `export_report_to_json(report, filepath, pretty) -> str`
Exportiert Report als JSON-Datei.

#### `export_trades_to_json(trades, filepath, pretty) -> str`
Exportiert Trade-History als JSON-Datei.

#### `export_trade_history_with_metrics(trades, filepath) -> str`
Exportiert detaillierte Trade-History mit kumulativen Metriken als CSV.

### Klasse: ReportingModule

```python
class ReportingModule:
    def __init__(self, trades_file: str)
    def load_trades(self, filepath: str = None) -> list
    def calculate_equity_curve(self, initial_capital: float) -> list
    def generate_report(self, initial_capital: float) -> dict
    def export_all(self, output_dir: str, prefix: str) -> dict
    def print_report_summary(self)
```

---

## ❓ FAQ

### Wie oft sollte ich Reports erstellen?

**Empfehlung:**
- **Täglich** - Am Ende jeder Trading-Session
- **Wöchentlich** - Für Performance-Review
- **Monatlich** - Für langfristige Analyse

### Welches Format für welchen Zweck?

- **CSV** - Analyse in Excel, Python Pandas
- **JSON** - Web-Dashboards, API-Integration, externe Tools

### Wie interpretiere ich die Sharpe Ratio?

- **< 0** - Verluste (schlecht)
- **0 - 1** - Geringe risiko-adjustierte Performance
- **1 - 2** - Gut (empfohlen)
- **> 2** - Sehr gut

### Was ist ein guter Profit Factor?

- **< 1.0** - Verluste überwiegen
- **1.0 - 1.5** - Knapp profitabel
- **1.5 - 2.5** - Gut
- **> 2.5** - Sehr gut

---

## 🔗 Weitere Ressourcen

- **test_performance_metrics.py** - Tests für Performance-Metriken
- **test_reporting_export.py** - Tests für Export-Funktionen
- **demo_reporting_export.py** - Praktische Beispiele
- **PERFORMANCE_METRICS_GUIDE.md** - Detaillierte Metriken-Dokumentation

---

**Made for Windows ⭐ | Python 3.12+ | DRY_RUN Default**
