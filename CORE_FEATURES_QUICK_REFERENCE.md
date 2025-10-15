# 🚀 Core Features - Quick Reference Guide

**Version**: 1.0.0  
**Date**: 2025-10-15  
**Status**: Production Ready ✅

---

## 📋 Overview

This quick reference provides a summary of all core trading bot features with configuration examples and usage patterns. For detailed documentation, see the comprehensive guides listed at the end.

---

## ✅ Feature Checklist

| Feature | Status | Tests | Config Location | Documentation |
|---------|--------|-------|-----------------|---------------|
| Circuit Breaker | ✅ Ready | 13/13 | config.py, .env | [Guide](#circuit-breaker) |
| Kelly Criterion | ✅ Ready | 16/16 | config.py | [Guide](#kelly-criterion) |
| Telegram Alerts | ✅ Ready | 7/7 | .env | [Guide](#telegram-alerts) |
| Email Alerts | ✅ Ready | 6/6 | .env | [Guide](#email-alerts) |
| Database | ✅ Ready | 13/13 | config.py, .env | [Guide](#database-integration) |
| Trailing Stop | ✅ Ready | ✅ | config.py | [Guide](#trailing-stop) |
| Dashboard Export | ✅ Ready | ✅ | - | [Guide](#dashboard-export) |

---

## 🔧 Configuration Quick Start

### Minimal Configuration (.env)

```bash
# Safe defaults for testing
DRY_RUN=true
BINANCE_TESTNET_API_KEY=your_testnet_key
BINANCE_TESTNET_SECRET_KEY=your_testnet_secret
```

### Production Configuration (.env)

```bash
# Production trading (DANGEROUS - only if you know what you're doing)
DRY_RUN=false
LIVE_TRADING=true
LIVE_ACK=I_UNDERSTAND

# Binance Live
BINANCE_API_KEY=your_live_api_key
BINANCE_SECRET_KEY=your_live_secret
BINANCE_BASE_URL=https://api.binance.com

# Database (Recommended for production)
USE_DATABASE=true
DATABASE_PATH=data/trading_bot.db

# Alerts (Highly recommended)
ENABLE_TELEGRAM_ALERTS=true
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

ENABLE_EMAIL_ALERTS=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=your_email@gmail.com
```

### Advanced Configuration (config.py)

```python
from config import config

# Circuit Breaker
config.max_drawdown_limit = 0.20  # 20% maximum drawdown

# Kelly Criterion (Advanced users only)
config.enable_kelly_criterion = True
config.kelly_fraction = 0.5  # Half Kelly (conservative)
config.kelly_max_position_pct = 0.25  # Max 25% per position

# Trailing Stop
config.enable_trailing_stop = True
config.trailing_stop_percent = 2.0  # 2% trailing distance

# Database
config.use_database = True
config.database_path = "data/trading_bot.db"
```

---

## 🚨 Circuit Breaker

### What It Does
Automatically stops trading when drawdown exceeds configured limit (default: 20%).

### Configuration

```python
# config.py
max_drawdown_limit: float = 0.20  # 20%

# .env (optional override)
MAX_DRAWDOWN_LIMIT=0.15  # 15%
```

### Usage

```python
from main import LiveTradingBot

# Circuit breaker is automatically active in production mode
bot = LiveTradingBot(use_live_data=True, paper_trading=False)
bot.run()  # Will stop if drawdown > 20%
```

### Key Features
- ✅ Only active in production (not DRY_RUN)
- ✅ Sends critical alert via Telegram/Email
- ✅ Logs event to database
- ✅ Preserves capital and state

### Testing

```bash
python3 -m pytest test_circuit_breaker.py -v
# 13 tests passing
```

### Documentation
- CIRCUIT_BREAKER_IMPLEMENTATION_SUMMARY.md
- demo_circuit_breaker.py

---

## 💰 Kelly Criterion

### What It Does
Optimizes position sizing based on historical win rate and profit factor.

### Configuration

```python
# config.py
enable_kelly_criterion: bool = False  # Default: disabled (safety first)
kelly_fraction: float = 0.5           # Half Kelly (conservative)
kelly_max_position_pct: float = 0.25  # Max 25% of capital
kelly_lookback_trades: int = 20       # Historical trades for calculation
```

### Usage

```python
from utils import calculate_kelly_criterion, calculate_kelly_position_size

# Calculate optimal Kelly percentage
kelly_pct = calculate_kelly_criterion(
    win_rate=0.60,      # 60% win rate
    avg_win=150.0,      # Average win $150
    avg_loss=100.0      # Average loss $100
)
# Returns: 0.2 (20% of capital)

# Calculate actual position size
position_size = calculate_kelly_position_size(
    capital=10000.0,
    kelly_pct=kelly_pct,
    kelly_fraction=0.5,  # Half Kelly for safety
    max_position_pct=0.25
)
# Returns: $1,000 (10% of capital)
```

### Key Features
- ✅ Mathematically optimal position sizing
- ✅ Fractional Kelly for risk reduction
- ✅ Maximum position limits
- ✅ Automatic calculation from trade history
- ✅ Disabled by default (safety first)

### Testing

```bash
python3 -m pytest test_kelly_criterion.py -v
# 16 tests passing
```

### Documentation
- KELLY_CRITERION_SUMMARY.md
- KELLY_CRITERION_GUIDE.md
- demo_kelly_criterion.py

---

## 📱 Telegram Alerts

### What It Does
Sends real-time notifications to your Telegram account for trades, circuit breaker events, and performance updates.

### Setup

1. **Create Telegram Bot**
   - Open Telegram and search for @BotFather
   - Send `/newbot` and follow instructions
   - Copy the bot token

2. **Get Chat ID**
   - Send a message to your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Copy the `chat.id` value

3. **Configure .env**
   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ENABLE_TELEGRAM_ALERTS=true
   ```

### Usage

```python
from alerts import TelegramAlert

# Initialize
telegram = TelegramAlert(
    bot_token="your_bot_token",
    chat_id="your_chat_id"
)

# Send trade alert
telegram.send_trade_alert(
    order_type='BUY',
    symbol='BTC/USDT',
    price=50000.0,
    quantity=0.1,
    strategies=['RSI', 'EMA'],
    capital=10000.0
)

# Send circuit breaker alert
telegram.send_circuit_breaker_alert(
    drawdown=22.5,
    loss=2250.0,
    remaining_capital=7750.0
)
```

### Alert Types
- ✅ Trade execution (BUY/SELL)
- ✅ Circuit breaker triggers
- ✅ Performance updates (ROI, Win Rate, Sharpe)
- ✅ Error notifications

### Testing

```bash
python3 -m pytest test_alert_system.py::TestTelegramAlert -v
# 7 tests passing
```

### Documentation
- ALERT_SYSTEM_GUIDE.md

---

## 📧 Email Alerts

### What It Does
Sends professional HTML email notifications for critical trading events.

### Setup

1. **Gmail Setup** (Recommended)
   - Enable 2-Factor Authentication
   - Generate App Password: https://myaccount.google.com/apppasswords
   - Use app password (not your regular password)

2. **Configure .env**
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   EMAIL_FROM=your_email@gmail.com
   EMAIL_TO=recipient@example.com
   ENABLE_EMAIL_ALERTS=true
   ```

### Usage

```python
from alerts import EmailAlert

# Initialize
email = EmailAlert(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_user="your_email@gmail.com",
    smtp_password="your_app_password",
    email_from="your_email@gmail.com",
    email_to="recipient@example.com"
)

# Send trade alert
email.send_trade_alert(
    order_type='BUY',
    symbol='BTC/USDT',
    price=50000.0,
    quantity=0.1,
    strategies=['RSI'],
    capital=10000.0
)
```

### Key Features
- ✅ Professional HTML templates
- ✅ Detailed trade information
- ✅ Performance metrics
- ✅ Error context
- ✅ Mobile-friendly design

### Testing

```bash
python3 -m pytest test_alert_system.py::TestEmailAlert -v
# 6 tests passing
```

### Documentation
- ALERT_SYSTEM_GUIDE.md

---

## 💾 Database Integration

### What It Does
Automatically stores all trades, performance metrics, and equity curve in a persistent SQLite database.

### Setup

```bash
# .env
USE_DATABASE=true
DATABASE_PATH=data/trading_bot.db
```

Database is automatically created on first use.

### Usage

```python
from db import DatabaseManager

# Initialize
db = DatabaseManager("data/trading_bot.db")

# Insert trade
trade_id = db.insert_trade(
    symbol="BTC/USDT",
    order_type="BUY",
    price=50000.0,
    quantity=0.1,
    strategies=["RSI", "EMA"],
    capital=10000.0,
    pnl=0.0
)

# Get trade statistics
stats = db.get_trade_statistics()
print(f"Total Trades: {stats['total_trades']}")
print(f"Win Rate: {stats['win_rate']:.2f}%")
print(f"Total P&L: ${stats['total_pnl']:,.2f}")

# Export to DataFrame
trades_df = db.get_trades_df(limit=100)
trades_df.to_csv("reports/trades.csv")
```

### Database Schema

- **trades** - Complete trade history with metadata
- **performance_metrics** - ROI, Win Rate, Sharpe Ratio snapshots
- **equity_curve** - Capital over time with drawdown tracking
- **strategy_performance** - Strategy-specific analytics
- **system_logs** - Structured logging
- **alerts_history** - Alert audit trail

### Export Options

```python
# Daily performance
daily_perf = db.get_daily_performance()
daily_perf.to_csv("reports/daily_performance.csv")

# Strategy summary
strategy_summary = db.get_strategy_summary()
strategy_summary.to_excel("reports/strategy_summary.xlsx")

# All trades
all_trades = db.get_trades_df()
all_trades.to_parquet("reports/trades.parquet")
```

### Testing

```bash
python3 -m pytest test_database.py -v
# 13 tests passing
```

### Documentation
- DATABASE_INTEGRATION_GUIDE.md

---

## 📈 Trailing Stop

### What It Does
Dynamically adjusts stop-loss to follow favorable price movements, locking in profits.

### Configuration

```python
# config.py
enable_trailing_stop: bool = True
trailing_stop_percent: float = 2.0  # 2% trailing distance
```

### Usage

```python
from strategy_core import ReversalTrailingStopStrategy

# Create strategy with trailing stop
strategy = ReversalTrailingStopStrategy(
    initial_capital=10000.0,
    stop_loss_percent=2.0,
    take_profit_percent=4.0,
    trailing_stop_percent=1.0  # 1% trailing stop
)

# Process market data
for candle in market_data:
    strategy.process_candle(candle)
    # Trailing stop automatically updates when in profit
```

### How It Works

1. **Entry**: Position opened at market price
2. **Initial Stop**: Set at entry_price - stop_loss_percent
3. **In Profit**: When price moves favorably, stop-loss trails behind
4. **Lock Profit**: If price reverses, trailing stop triggers exit

### Example

```
Entry: $50,000 (LONG)
Initial Stop: $49,000 (2% below entry)

Price rises to $51,000:
  → Trailing stop: $50,490 (1% below current price)
  
Price rises to $52,000:
  → Trailing stop: $51,480 (1% below current price)
  
Price drops to $51,400:
  → Trailing stop triggers at $51,480
  → Profit: $1,480 locked in
```

### Testing

```bash
python3 -m pytest test_strategy_core.py::TestReversalTrailingStopStrategy::test_trailing_stop_updates -v
# Test passing
```

### Documentation
- strategy_core.py
- demo_reversal_strategy.py

---

## 📊 Dashboard Export

### What It Does
Export trading data and performance metrics to various formats for analysis and visualization.

### Usage

```python
from db import DatabaseManager

db = DatabaseManager("data/trading_bot.db")

# Export Options:

# 1. CSV Export
trades_df = db.get_trades_df()
trades_df.to_csv("exports/all_trades.csv", index=False)

# 2. Excel Export with multiple sheets
with pd.ExcelWriter("exports/trading_report.xlsx") as writer:
    db.get_trades_df().to_excel(writer, sheet_name="Trades", index=False)
    db.get_daily_performance().to_excel(writer, sheet_name="Daily Performance", index=False)
    db.get_strategy_summary().to_excel(writer, sheet_name="Strategy Summary", index=False)

# 3. Parquet Export (efficient for large datasets)
trades_df.to_parquet("exports/trades.parquet")

# 4. JSON Export
trades_json = db.get_trades()
import json
with open("exports/trades.json", "w") as f:
    json.dump(trades_json, f, indent=2)
```

### Available Reports

```python
# Daily Performance
daily_perf = db.get_daily_performance()
# Columns: date, total_trades, win_rate, total_pnl, avg_pnl, max_drawdown

# Strategy Summary
strategy_summary = db.get_strategy_summary()
# Columns: strategy, total_trades, win_rate, avg_pnl, total_pnl, sharpe_ratio

# Equity Curve
equity_curve = db.get_equity_curve()
# Columns: timestamp, capital, drawdown

# Trade Statistics
stats = db.get_trade_statistics()
# Returns: total_trades, winning_trades, losing_trades, win_rate, 
#          total_pnl, avg_pnl, best_trade, worst_trade, etc.
```

### Documentation
- DATABASE_INTEGRATION_GUIDE.md
- DASHBOARD_GUIDE.md

---

## 🎯 Complete Integration Example

### All Features Enabled

```python
from main import LiveTradingBot
from config import config
import os

# Configure environment
os.environ['DRY_RUN'] = 'false'  # Production mode (DANGER)
os.environ['ENABLE_TELEGRAM_ALERTS'] = 'true'
os.environ['ENABLE_EMAIL_ALERTS'] = 'true'
os.environ['USE_DATABASE'] = 'true'

# Update config
config.use_database = True
config.enable_kelly_criterion = True  # Advanced users only
config.enable_trailing_stop = True
config.max_drawdown_limit = 0.20  # 20% circuit breaker

# Create and run bot
bot = LiveTradingBot(
    use_live_data=True,      # Use Binance API
    paper_trading=True       # Use testnet (safe)
)

# Features automatically active:
# ✅ Circuit Breaker monitoring (20% limit)
# ✅ Kelly Criterion position sizing
# ✅ Trailing Stop in strategies
# ✅ Telegram alerts on trades
# ✅ Email alerts on circuit breaker
# ✅ Database persistence
# ✅ Monitoring & Alerting

bot.run()
```

### Safety Checklist Before Production

- [ ] Tested with DRY_RUN=true
- [ ] Tested with paper_trading=True
- [ ] Verified alert system working
- [ ] Reviewed circuit breaker settings
- [ ] Checked Kelly Criterion parameters
- [ ] Database backup configured
- [ ] Emergency contacts notified
- [ ] Kill switch tested
- [ ] Sufficient capital allocated
- [ ] Risk management understood

---

## 🧪 Testing All Features

### Run All Core Feature Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python3 -m pytest test_alert_system.py test_database.py test_kelly_criterion.py test_circuit_breaker.py test_strategy_core.py -v

# Expected result: 71 tests passing
```

### Individual Feature Tests

```bash
# Circuit Breaker
python3 -m pytest test_circuit_breaker.py -v
# 13 tests

# Kelly Criterion
python3 -m pytest test_kelly_criterion.py -v
# 16 tests

# Alerts (Telegram + Email)
python3 -m pytest test_alert_system.py -v
# 18 tests

# Database
python3 -m pytest test_database.py -v
# 13 tests

# Trailing Stop Strategy
python3 -m pytest test_strategy_core.py -v
# 11 tests
```

### Demo Scripts

```bash
# Circuit Breaker Demo
python demo_circuit_breaker.py

# Kelly Criterion Demo
python demo_kelly_criterion.py

# Core Features Demo
python demo_core_features.py

# Reversal Strategy Demo (includes trailing stop)
python demo_reversal_strategy.py
```

---

## 📚 Complete Documentation

### Comprehensive Guides

1. **CORE_FEATURES_IMPLEMENTATION_SUMMARY.md** - Implementation overview
2. **CORE_FEATURES_VERIFICATION_REPORT.md** - Detailed verification results
3. **ISSUE_RESOLUTION_SUMMARY.md** - Complete issue resolution details
4. **ALERT_SYSTEM_GUIDE.md** - Alert system setup and usage
5. **DATABASE_INTEGRATION_GUIDE.md** - Database integration guide
6. **KELLY_CRITERION_SUMMARY.md** - Kelly Criterion implementation
7. **KELLY_CRITERION_GUIDE.md** - Kelly Criterion detailed guide
8. **CIRCUIT_BREAKER_IMPLEMENTATION_SUMMARY.md** - Circuit breaker details
9. **LIVE_TRADING_SETUP_GUIDE.md** - Complete live trading setup

### Quick References

- **README.md** - Project overview
- **ROADMAP.md** - Project roadmap
- **BEST_PRACTICES_GUIDE.md** - Best practices
- **FAQ.md** - Frequently asked questions

---

## 🚀 Getting Started Workflow

### 1. Initial Setup (5 minutes)

```bash
# Clone repository
git clone https://github.com/CallMeMell/ai.traiding.git
cd ai.traiding

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your settings
# At minimum, set:
# - DRY_RUN=true
# - BINANCE_TESTNET_API_KEY
# - BINANCE_TESTNET_SECRET_KEY
```

### 2. Test the Bot (2 minutes)

```bash
# Run tests to verify everything works
python3 -m pytest test_alert_system.py test_database.py test_kelly_criterion.py test_circuit_breaker.py -v

# Should see: 60 tests passing
```

### 3. Configure Alerts (5 minutes)

```bash
# Setup Telegram (optional but recommended)
# 1. Create bot with @BotFather
# 2. Get chat ID
# 3. Update .env:
#    TELEGRAM_BOT_TOKEN=your_token
#    TELEGRAM_CHAT_ID=your_chat_id
#    ENABLE_TELEGRAM_ALERTS=true
```

### 4. Enable Database (1 minute)

```bash
# Update .env:
USE_DATABASE=true
DATABASE_PATH=data/trading_bot.db

# Database auto-creates on first run
```

### 5. Run Paper Trading (Start trading!)

```bash
# Paper trading with testnet
python main.py

# Bot will:
# ✅ Use Binance Testnet (safe)
# ✅ Monitor circuit breaker
# ✅ Send alerts on trades
# ✅ Store data in database
# ✅ Use trailing stops
```

### 6. Monitor & Analyze

```bash
# Export reports
python -c "
from db import DatabaseManager
db = DatabaseManager('data/trading_bot.db')

# Get statistics
stats = db.get_trade_statistics()
print(f'Win Rate: {stats[\"win_rate\"]:.2f}%')
print(f'Total P&L: ${stats[\"total_pnl\"]:,.2f}')

# Export to CSV
db.get_trades_df().to_csv('my_trades.csv')
"
```

---

## ⚠️ Important Safety Notes

### DRY_RUN Mode

**Always** start with `DRY_RUN=true` in your `.env` file:

```bash
# Safe - simulated trading
DRY_RUN=true

# DANGER - real money
DRY_RUN=false  # Only use after extensive testing
```

### Circuit Breaker

The circuit breaker is your safety net. **Never disable it** in production:

```python
# config.py
max_drawdown_limit: float = 0.20  # 20% - adjust based on risk tolerance

# Recommended values:
# Conservative: 0.10 (10%)
# Moderate:     0.20 (20%)
# Aggressive:   0.30 (30%)
# NEVER:        > 0.50 (50%)
```

### Kelly Criterion

**Only enable after 20+ trades** of historical data:

```python
# config.py
enable_kelly_criterion: bool = False  # Start disabled

# After 20+ trades with proven win rate:
enable_kelly_criterion: bool = True
kelly_fraction: float = 0.5  # Half Kelly (conservative)
```

---

## 🆘 Troubleshooting

### Tests Failing

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Run tests with verbose output
python3 -m pytest -v --tb=short
```

### Alerts Not Working

```bash
# Test Telegram
python -c "
from alerts import TelegramAlert
t = TelegramAlert('your_token', 'your_chat_id')
t.send_message('Test message')
"

# Test Email
python -c "
from alerts import EmailAlert
e = EmailAlert('smtp.gmail.com', 587, 'your_email', 'your_password', 'from@email.com', 'to@email.com')
e.send_email('Test Subject', 'Test message')
"
```

### Database Issues

```bash
# Check database file
ls -lh data/trading_bot.db

# Test database connection
python -c "
from db import DatabaseManager
db = DatabaseManager('data/trading_bot.db')
print(f'Database OK: {len(db.get_trades())} trades')
"
```

---

## 📞 Support

For detailed help:

1. Check comprehensive guides in documentation
2. Review test files for usage examples
3. Run demo scripts for interactive examples
4. Check troubleshooting sections in guides

**Documentation Files**:
- Issues: TROUBLESHOOTING.md (if exists)
- Questions: FAQ.md
- Setup: LIVE_TRADING_SETUP_GUIDE.md

---

**Made for Windows ⭐ | PowerShell-First | python-dotenv CLI | DRY_RUN Default | 100% Tested**

**Version**: 1.0.0  
**Last Updated**: 2025-10-15  
**Status**: ✅ Production Ready
