# 📝 Erweiterter TradeLogger - Echtgeld-Flag & erweiterte Metriken

## 🎯 Übersicht

Der TradeLogger wurde erweitert um:
- **Echtgeld-Flag** (`is_real_money`): Unterscheidung zwischen Dry-Run und Echtgeld-Trades
- **Erweiterte Metriken**: `profit_factor`, `win_rate`, `sharpe_ratio` pro Trade
- **Dashboard-Integration**: Automatische Anzeige und Auswertung

## 🔐 Sicherheit zuerst!

⚠️ **WICHTIG**: Das Echtgeld-Flag ist **standardmäßig FALSE**!

```python
# Dry-Run (Standard - SICHER!)
logger.log_trade('BUY', 30000.0, 0.1, ['RSI'], 10000.0)

# Echtgeld (explizit aktivieren)
logger.log_trade('BUY', 30000.0, 0.1, ['RSI'], 10000.0, is_real_money=True)
```

## 📋 Neue Features

### 1. Echtgeld-Flag (`is_real_money`)

**Zweck**: Klare Trennung zwischen Test- und Echtgeld-Trades

**Parameter**:
- Typ: `bool`
- Default: `False` (Dry-Run)
- Verwendung: `is_real_money=True` für Echtgeld-Trades

**Beispiel**:
```python
from utils import TradeLogger

logger = TradeLogger("data/trades.csv")

# Dry-Run Trade (Standard)
logger.log_trade(
    order_type='BUY',
    price=30000.0,
    quantity=0.1,
    strategies=['RSI', 'MACD'],
    capital=10000.0,
    pnl=0.0
)  # is_real_money = False (default)

# Echtgeld Trade
logger.log_trade(
    order_type='SELL',
    price=31000.0,
    quantity=0.1,
    strategies=['RSI'],
    capital=10500.0,
    pnl=500.0,
    is_real_money=True  # ⚠️ ECHTGELD!
)
```

### 2. Erweiterte Metriken

**Neue Felder**:
- `profit_factor`: Profit Factor (Gross Profit / Gross Loss)
- `win_rate`: Win Rate in Prozent
- `sharpe_ratio`: Sharpe Ratio (Rendite/Risiko)

**Parameter**:
- Alle optional, Default: `0.0`
- Können pro Trade gesetzt werden

**Beispiel**:
```python
logger.log_trade(
    order_type='SELL',
    price=31000.0,
    quantity=0.1,
    strategies=['RSI', 'MACD'],
    capital=10500.0,
    pnl=500.0,
    is_real_money=True,
    profit_factor=1.8,    # Profit Factor
    win_rate=75.0,        # 75% Win Rate
    sharpe_ratio=1.5      # Sharpe Ratio
)
```

## 🎨 Dashboard-Integration

### Neue Metriken im Dashboard

Das Dashboard zeigt automatisch:
- `real_money_trades`: Anzahl Echtgeld-Trades 💰
- `dry_run_trades`: Anzahl Dry-Run Trades 🧪
- `profit_factor`: Profit Factor aus allen Trades
- `sharpe_ratio`: Sharpe Ratio aus allen Trades

**Beispiel**:
```python
from dashboard import create_dashboard

dashboard = create_dashboard()
dashboard.display_metrics_console()
```

**Output**:
```
============================================================
📊 DASHBOARD METRICS
============================================================
Total Trades.................. 5
Total Pnl..................... $600.00
Win Rate...................... 60.00
Profit Factor................. 2.50
Sharpe Ratio.................. 1.80
Current Capital............... $10,600.00
Real Money Trades............. 2
Dry Run Trades................ 3
============================================================
```

### Visuelle Indikatoren

**Console-Logging**:
- `💰 ECHTGELD` - Echtgeld-Trade
- `🧪 DRY-RUN` - Dry-Run Trade

**HTML-Dashboard**:
- Real Money Trades: Rote Umrandung 🔴
- Dry-Run Trades: Grüne Umrandung 🟢

## 📊 CSV-Struktur

Die Trades-CSV hat jetzt folgende Spalten:

```csv
timestamp,symbol,order_type,price,quantity,triggering_strategies,capital,pnl,is_real_money,profit_factor,win_rate,sharpe_ratio
2024-01-01T10:00:00,BTC/USDT,BUY,30000.00,0.1,"RSI,MACD",10000.00,0.00,False,0.00,0.00,0.00
2024-01-01T12:00:00,BTC/USDT,SELL,31000.00,0.1,RSI,10500.00,500.00,True,1.50,100.00,1.20
```

## 🧪 Tests

### Unit Tests

**test_trade_logger_extended.py** (6 Tests):
```bash
pytest test_trade_logger_extended.py -v
```

- ✅ CSV-Header enthalten neue Felder
- ✅ Dry-Run Trades (default)
- ✅ Echtgeld-Trades
- ✅ Trades mit erweiterten Metriken
- ✅ Gemischte Trade-Typen
- ✅ Rückwärtskompatibilität

**test_dashboard_extended.py** (6 Tests):
```bash
pytest test_dashboard_extended.py -v
```

- ✅ Config enthält neue Metriken
- ✅ get_metrics() zählt Trade-Typen
- ✅ Metriken-Filterung funktioniert
- ✅ Console-Display funktioniert
- ✅ HTML-Export enthält neue Felder
- ✅ Factory-Funktion funktioniert

### Demo-Script

```bash
python demo_extended_tradelogger.py
```

Zeigt alle Features in Aktion:
- Dry-Run Trades
- Echtgeld-Trades
- Erweiterte Metriken
- Dashboard-Anzeige
- HTML-Export

## 🔄 Rückwärtskompatibilität

Alle bestehenden Aufrufe funktionieren **ohne Änderungen**:

```python
# Alter Code - funktioniert weiterhin
logger.log_trade(
    order_type='BUY',
    price=30000.0,
    quantity=0.1,
    strategies=['RSI'],
    capital=10000.0
)
# Neue Felder bekommen automatisch Standardwerte:
# - is_real_money = False
# - profit_factor = 0.0
# - win_rate = 0.0
# - sharpe_ratio = 0.0
```

## 📈 Best Practices

### 1. Echtgeld immer explizit markieren

```python
# ✅ GUT: Explizit als Echtgeld markiert
logger.log_trade(..., is_real_money=True)

# ❌ SCHLECHT: Implizit - könnte übersehen werden
# (nutzt Default = False)
logger.log_trade(...)
```

### 2. Metriken pro Trade berechnen

```python
# Berechne Metriken aus Trade-Historie
all_trades = logger.get_all_trades()
metrics = calculate_performance_metrics(all_trades)

# Logge Trade mit aktuellen Metriken
logger.log_trade(
    ...,
    profit_factor=metrics['profit_factor'],
    win_rate=metrics['win_rate'],
    sharpe_ratio=metrics['sharpe_ratio']
)
```

### 3. Dashboard regelmäßig aktualisieren

```python
class TradingBot:
    def __init__(self):
        self.logger = TradeLogger()
        self.dashboard = create_dashboard()
        self.trade_count = 0
    
    def on_trade(self, ...):
        # Trade loggen
        self.logger.log_trade(...)
        
        # Dashboard alle 10 Trades aktualisieren
        self.trade_count += 1
        if self.trade_count % 10 == 0:
            self.dashboard.display_metrics_console()
            self.dashboard.export_dashboard_html()
```

## 🛡️ Sicherheitshinweise

1. **Default ist Dry-Run**: Echtgeld muss explizit aktiviert werden
2. **Logging-Ausgabe**: Trades zeigen deutlich ob Echtgeld oder Dry-Run
3. **Dashboard-Visualisierung**: Klare farbliche Trennung
4. **CSV-Nachvollziehbarkeit**: Jeder Trade ist eindeutig markiert

## 📚 API-Referenz

### TradeLogger.log_trade()

```python
def log_trade(
    self,
    order_type: str,              # 'BUY' oder 'SELL'
    price: float,                 # Ausführungspreis
    quantity: float,              # Menge
    strategies: list,             # Liste der Strategien
    capital: float,               # Aktuelles Kapital
    pnl: float = 0.0,            # Profit/Loss
    symbol: str = "BTC/USDT",    # Trading-Symbol
    is_real_money: bool = False, # ⚠️ Echtgeld-Flag (default: False)
    profit_factor: float = 0.0,  # Profit Factor Metrik
    win_rate: float = 0.0,       # Win Rate Metrik (%)
    sharpe_ratio: float = 0.0    # Sharpe Ratio Metrik
) -> None
```

### Dashboard-Metriken

Neue Metriken in `DashboardConfig.DEFAULT_METRICS`:
- `profit_factor`: Profit Factor aus allen Trades
- `sharpe_ratio`: Sharpe Ratio aus allen Trades
- `real_money_trades`: Anzahl Echtgeld-Trades
- `dry_run_trades`: Anzahl Dry-Run Trades

## 🎯 Beispiele

### Beispiel 1: Einfacher Trade-Zyklus

```python
from utils import TradeLogger
from dashboard import create_dashboard

# Setup
logger = TradeLogger("data/trades.csv")
dashboard = create_dashboard()

# Buy Trade (Dry-Run)
logger.log_trade('BUY', 30000.0, 0.1, ['RSI'], 10000.0)

# Sell Trade (Echtgeld mit Gewinn)
logger.log_trade(
    'SELL', 31000.0, 0.1, ['MACD'], 10500.0, 
    pnl=500.0,
    is_real_money=True,
    profit_factor=1.5,
    win_rate=100.0,
    sharpe_ratio=1.2
)

# Dashboard anzeigen
dashboard.display_metrics_console()
```

### Beispiel 2: Integration in Trading-Bot

```python
from utils import TradeLogger, calculate_performance_metrics

class TradingBot:
    def __init__(self, is_live: bool = False):
        self.logger = TradeLogger()
        self.is_live = is_live  # Echtgeld-Modus
    
    def execute_trade(self, order_type, price, quantity, strategies):
        # Trade ausführen...
        
        # Metriken berechnen
        all_trades = self.logger.get_all_trades()
        metrics = calculate_performance_metrics(all_trades)
        
        # Trade loggen mit allen Infos
        self.logger.log_trade(
            order_type=order_type,
            price=price,
            quantity=quantity,
            strategies=strategies,
            capital=self.current_capital,
            pnl=self.calculate_pnl(),
            is_real_money=self.is_live,  # ⚠️ Basiert auf Bot-Modus
            profit_factor=metrics.get('profit_factor', 0.0),
            win_rate=metrics.get('win_rate', 0.0),
            sharpe_ratio=metrics.get('sharpe_ratio', 0.0)
        )
```

## 📞 Hilfe & Support

- Demo ausführen: `python demo_extended_tradelogger.py`
- Tests ausführen: `pytest test_trade_logger_extended.py test_dashboard_extended.py -v`
- Bestehende Tests: `pytest test_dashboard.py -v`

---

**Stand**: 2024-10-12  
**Version**: 1.0.0  
**Status**: ✅ Production-Ready
