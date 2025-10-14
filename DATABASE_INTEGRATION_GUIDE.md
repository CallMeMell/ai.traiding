# 💾 Database Integration Guide

**Status**: ✅ **IMPLEMENTIERT**  
**Version**: 1.0.0  
**Datum**: 2025-10-14

---

## 📋 Überblick

Das Database-System bietet persistente Speicherung für:
- ✅ **Trade History** - Alle ausgeführten Trades
- ✅ **Performance Metrics** - ROI, Win Rate, Sharpe Ratio, etc.
- ✅ **Equity Curve** - Kapitalverlauf über Zeit
- ✅ **Strategy Performance** - Performance einzelner Strategien
- ✅ **System Logs** - Strukturierte Log-Speicherung
- ✅ **Alert History** - Protokoll aller gesendeten Alerts

**Datenbank**: SQLite (keine Installation erforderlich)

---

## 🚀 Quick Start

### 1. Database aktivieren

```bash
# In .env
USE_DATABASE=true
DATABASE_PATH=data/trading_bot.db
```

### 2. In Python nutzen

```python
from db import DatabaseManager

# Initialisiere Database Manager
db = DatabaseManager("data/trading_bot.db")

# Trade speichern
trade_id = db.insert_trade(
    symbol="BTC/USDT",
    order_type="BUY",
    price=50000.0,
    quantity=0.1,
    strategies=["RSI", "EMA"],
    capital=10000.0,
    pnl=0.0
)

# Trades abrufen
trades = db.get_trades(limit=100)

# Als DataFrame
import pandas as pd
trades_df = db.get_trades_df()

# Statistiken
stats = db.get_trade_statistics()
print(stats)
# {
#     'total_trades': 42,
#     'winning_trades': 28,
#     'losing_trades': 14,
#     'win_rate': 66.67,
#     'total_pnl': 2500.0,
#     'avg_pnl': 59.52,
#     'worst_trade': -250.0,
#     'best_trade': 500.0
# }

# Schließen
db.close()
```

### 3. Mit Context Manager

```python
with DatabaseManager("data/trading_bot.db") as db:
    # Automatisches Schließen nach Block
    trades = db.get_trades()
```

---

## 📊 Database Schema

### Tables

1. **trades** - Trade History
   - `id`, `timestamp`, `symbol`, `order_type`, `price`, `quantity`
   - `triggering_strategies`, `capital`, `pnl`
   - `is_real_money`, `profit_factor`, `win_rate`, `sharpe_ratio`

2. **performance_metrics** - Performance Snapshots
   - `capital`, `total_pnl`, `roi_percent`
   - `total_trades`, `winning_trades`, `losing_trades`
   - `win_rate`, `profit_factor`, `sharpe_ratio`, `max_drawdown`

3. **equity_curve** - Equity Tracking
   - `timestamp`, `equity`, `drawdown_percent`

4. **strategy_performance** - Strategy Analytics
   - `strategy_name`, `total_signals`, `winning_signals`
   - `win_rate`, `total_pnl`, `avg_pnl_per_trade`

5. **system_logs** - Structured Logging
   - `timestamp`, `log_level`, `module`, `message`

6. **alerts_history** - Alert Tracking
   - `timestamp`, `alert_type`, `channel`, `success`, `message`

### Views

1. **v_recent_trades** - Letzte 100 Trades
2. **v_daily_performance** - Tägliche Performance
3. **v_strategy_summary** - Strategy Performance Übersicht

---

## 🔧 API Reference

### Trade Operations

#### Insert Trade

```python
trade_id = db.insert_trade(
    symbol: str,                    # z.B. "BTC/USDT"
    order_type: str,                # "BUY" oder "SELL"
    price: float,                   # Ausführungspreis
    quantity: float,                # Menge
    strategies: List[str],          # Liste der Strategien
    capital: float,                 # Aktuelles Kapital
    pnl: float = 0.0,              # Profit/Loss
    is_real_money: bool = False,   # Real Money Trading
    profit_factor: float = 0.0,    # Profit Factor
    win_rate: float = 0.0,         # Win Rate
    sharpe_ratio: float = 0.0,     # Sharpe Ratio
    notes: str = None              # Zusätzliche Notizen
) -> int                           # Returns: Trade ID
```

#### Get Trades

```python
trades = db.get_trades(
    limit: int = 100,              # Max Anzahl
    symbol: str = None,            # Filter nach Symbol
    order_type: str = None,        # Filter nach Order Type
    start_date: datetime = None,   # Von Datum
    end_date: datetime = None      # Bis Datum
) -> List[Dict[str, Any]]
```

#### Get Trades DataFrame

```python
df = db.get_trades_df(
    limit: int = 100,
    symbol: str = None,
    # ... gleiche Parameter wie get_trades
) -> pd.DataFrame
```

### Performance Metrics

#### Insert Performance Metric

```python
metric_id = db.insert_performance_metric(
    capital: float,
    total_pnl: float,
    roi_percent: float,
    total_trades: int,
    winning_trades: int,
    losing_trades: int,
    win_rate: float,
    profit_factor: float,
    sharpe_ratio: float,
    max_drawdown: float,
    avg_trade_duration: float = None
) -> int
```

#### Get Latest Performance

```python
performance = db.get_latest_performance()
# Returns: Dict mit allen Performance-Metriken oder None
```

### Equity Curve

#### Insert Equity Point

```python
point_id = db.insert_equity_point(
    equity: float,
    drawdown_percent: float
) -> int
```

#### Get Equity Curve

```python
curve = db.get_equity_curve(limit: int = 1000)
# Returns: List[Dict] mit allen Equity Points
```

### Analytics

#### Get Trade Statistics

```python
stats = db.get_trade_statistics()
# Returns: {
#     'total_trades': int,
#     'winning_trades': int,
#     'losing_trades': int,
#     'win_rate': float,
#     'total_pnl': float,
#     'avg_pnl': float,
#     'worst_trade': float,
#     'best_trade': float,
#     'avg_capital': float
# }
```

#### Get Daily Performance

```python
df = db.get_daily_performance()
# Returns: DataFrame mit täglicher Performance
# Columns: trade_date, total_trades, winning_trades,
#          losing_trades, daily_pnl, avg_pnl_per_trade,
#          min_capital, max_capital
```

#### Get Strategy Summary

```python
df = db.get_strategy_summary()
# Returns: DataFrame mit Strategy Performance
# Columns: strategy_name, total_trades, winning_trades,
#          losing_trades, win_rate, total_pnl,
#          avg_pnl_per_trade, worst_trade, best_trade
```

---

## 🔄 Migration from CSV

### Automatische Migration

```python
from db import DatabaseManager

db = DatabaseManager("data/trading_bot.db")

# Migriere alle Trades aus CSV
count = db.migrate_from_csv("data/trades.csv")
print(f"Migrated {count} trades")
```

### Manueller Export/Import

```python
# Export zu CSV
trades_df = db.get_trades_df()
trades_df.to_csv("data/trades_backup.csv", index=False)

# Import von CSV
import pandas as pd
df = pd.read_csv("data/trades_backup.csv")

for _, row in df.iterrows():
    db.insert_trade(
        symbol=row['symbol'],
        order_type=row['order_type'],
        price=row['price'],
        quantity=row['quantity'],
        strategies=row['triggering_strategies'].split(','),
        capital=row['capital'],
        pnl=row['pnl']
    )
```

---

## 📈 Integration mit Trading Bot

### In config.py

```python
# config.py
use_database: bool = True
database_path: str = "data/trading_bot.db"
```

### In main.py

```python
from db import DatabaseManager

class LiveTradingBot:
    def __init__(self):
        # ...
        
        # Database Manager
        if config.use_database:
            self.db = DatabaseManager(config.database_path)
        else:
            self.db = None
    
    def process_signal(self, analysis):
        # Nach Trade-Ausführung
        if self.db:
            self.db.insert_trade(
                symbol=config.trading_symbol,
                order_type=order_type,
                price=current_price,
                quantity=config.trade_size,
                strategies=strategies,
                capital=self.capital,
                pnl=pnl
            )
            
            # Equity Curve Update
            drawdown = calculate_current_drawdown(self.equity_curve)
            self.db.insert_equity_point(self.capital, drawdown)
```

---

## 🧪 Testing

### Run Tests

```powershell
python -m pytest test_database.py -v
```

**Expected Output:**
```
test_database.py::TestDatabaseManager::test_init PASSED
test_database.py::TestDatabaseManager::test_insert_trade PASSED
test_database.py::TestDatabaseManager::test_get_trades PASSED
test_database.py::TestDatabaseManager::test_get_trades_df PASSED
test_database.py::TestDatabaseManager::test_insert_performance_metric PASSED
test_database.py::TestDatabaseManager::test_get_latest_performance PASSED
test_database.py::TestDatabaseManager::test_insert_equity_point PASSED
test_database.py::TestDatabaseManager::test_get_equity_curve PASSED
test_database.py::TestDatabaseManager::test_insert_strategy_performance PASSED
test_database.py::TestDatabaseManager::test_get_trade_statistics PASSED
test_database.py::TestDatabaseManager::test_get_daily_performance PASSED
test_database.py::TestDatabaseManager::test_get_strategy_summary PASSED
test_database.py::TestDatabaseManager::test_context_manager PASSED

=================== 13 passed in 0.71s ===================
```

---

## 📊 SQL Queries

### Direkte SQL Queries (Advanced)

```python
# Custom Query
cursor = db.conn.cursor()
cursor.execute("""
    SELECT 
        DATE(timestamp) as date,
        COUNT(*) as trades,
        SUM(pnl) as daily_pnl
    FROM trades
    WHERE timestamp >= date('now', '-7 days')
    GROUP BY DATE(timestamp)
""")

results = cursor.fetchall()
```

### Nützliche Queries

#### Top 10 Profitable Trades

```sql
SELECT * FROM trades
WHERE pnl > 0
ORDER BY pnl DESC
LIMIT 10;
```

#### Worst 10 Losing Trades

```sql
SELECT * FROM trades
WHERE pnl < 0
ORDER BY pnl ASC
LIMIT 10;
```

#### Strategy Performance

```sql
SELECT 
    triggering_strategies,
    COUNT(*) as total_trades,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
    AVG(pnl) as avg_pnl
FROM trades
GROUP BY triggering_strategies;
```

#### Monthly ROI

```sql
SELECT 
    strftime('%Y-%m', timestamp) as month,
    MIN(capital) as start_capital,
    MAX(capital) as end_capital,
    (MAX(capital) - MIN(capital)) as monthly_pnl,
    ((MAX(capital) - MIN(capital)) / MIN(capital) * 100) as roi_percent
FROM trades
GROUP BY strftime('%Y-%m', timestamp);
```

---

## 🔍 Database Management

### Backup

```powershell
# Windows
Copy-Item data/trading_bot.db data/backups/trading_bot_$(Get-Date -Format 'yyyyMMdd_HHmmss').db

# Linux/Mac
cp data/trading_bot.db data/backups/trading_bot_$(date +%Y%m%d_%H%M%S).db
```

### Optimize

```python
# Vacuum (komprimiere Datenbank)
db.conn.execute("VACUUM")

# Analyze (update Statistiken)
db.conn.execute("ANALYZE")
```

### Reset

```python
# Lösche alle Trades (VORSICHT!)
db.conn.execute("DELETE FROM trades")
db.conn.commit()

# Oder lösche Datenbank-Datei
import os
os.remove("data/trading_bot.db")
```

---

## 📱 Dashboard Integration

### Export für Dashboard

```python
# Performance Report
performance = db.get_latest_performance()

# Equity Curve Chart
curve = db.get_equity_curve()
equity_data = [point['equity'] for point in curve]
timestamps = [point['timestamp'] for point in curve]

# Strategy Comparison
strategy_summary = db.get_strategy_summary()

# Daily Performance Chart
daily_perf = db.get_daily_performance()
```

### JSON Export

```python
import json

# Export Trades zu JSON
trades = db.get_trades(limit=1000)
with open("data/trades.json", "w") as f:
    json.dump(trades, f, indent=2, default=str)
```

---

## 🐛 Troubleshooting

### Problem: "database is locked"

**Lösung:**
```python
# Nutze Context Manager für automatisches Schließen
with DatabaseManager(db_path) as db:
    # Operationen

# Oder explizites Schließen
db.close()
```

### Problem: Datenbank-Datei zu groß

**Lösung:**
```python
# 1. Alte Daten löschen
db.conn.execute("""
    DELETE FROM trades 
    WHERE timestamp < date('now', '-90 days')
""")

# 2. Vacuum
db.conn.execute("VACUUM")
db.conn.commit()
```

### Problem: Schema-Änderungen

**Lösung:**
```sql
-- Neue Spalte hinzufügen
ALTER TABLE trades ADD COLUMN new_column TEXT;

-- Oder neue Tabelle erstellen und Daten migrieren
CREATE TABLE trades_new (...);
INSERT INTO trades_new SELECT * FROM trades;
DROP TABLE trades;
ALTER TABLE trades_new RENAME TO trades;
```

---

## 🔒 Best Practices

### 1. Backup-Strategie

```python
import shutil
from datetime import datetime

def backup_database(db_path: str):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"data/backups/trading_bot_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    print(f"✓ Backup created: {backup_path}")

# Täglich um 00:00
import schedule
schedule.every().day.at("00:00").do(lambda: backup_database("data/trading_bot.db"))
```

### 2. Transaktionen nutzen

```python
try:
    db.conn.execute("BEGIN TRANSACTION")
    
    # Mehrere Operationen
    db.insert_trade(...)
    db.insert_equity_point(...)
    db.insert_performance_metric(...)
    
    db.conn.commit()
except Exception as e:
    db.conn.rollback()
    logger.error(f"Transaction failed: {e}")
```

### 3. Indizes optimieren

```sql
-- Wenn oft nach Symbol gesucht wird
CREATE INDEX idx_trades_symbol_timestamp 
ON trades(symbol, timestamp);

-- Wenn oft nach Strategien gesucht wird
CREATE INDEX idx_trades_strategies 
ON trades(triggering_strategies);
```

---

## 📚 Referenzen

- **SQLite Docs**: https://www.sqlite.org/docs.html
- **Python sqlite3**: https://docs.python.org/3/library/sqlite3.html
- **Pandas SQL**: https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html

---

**Implementiert von**: GitHub Copilot  
**Datum**: 2025-10-14  
**Status**: ✅ PRODUCTION READY
