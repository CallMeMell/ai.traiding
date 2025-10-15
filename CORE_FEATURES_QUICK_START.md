# 🚀 Core Features - Quick Start Guide

**Quick reference for all trading bot core features**

---

## ⚡ Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example and edit with your values
cp .env.example .env

# Required for live trading
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key

# Optional but recommended
ENABLE_TELEGRAM_ALERTS=true
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

ENABLE_EMAIL_ALERTS=true
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_TO=recipient@example.com

USE_DATABASE=true
```

### 3. Run Tests
```bash
# Verify everything works
python -m pytest test_circuit_breaker.py test_kelly_criterion.py test_alert_system.py test_database.py -v
```

### 4. Start Trading
```bash
# Paper trading (safe, recommended)
python main.py  # DRY_RUN=true by default

# Live trading (real money)
# Set DRY_RUN=false in .env first!
python main.py
```

---

## 🎯 Core Features Overview

### 🚨 Circuit Breaker (Risk Management)

**What**: Automatic trading halt on excessive drawdown

**Configuration**:
```python
# config.py or .env
MAX_DRAWDOWN_LIMIT=0.15  # 15% max drawdown
```

**Usage**:
```python
from main import LiveTradingBot

bot = LiveTradingBot(paper_trading=False)  # Enable circuit breaker
bot.run()  # Automatically monitored
```

**Behavior**:
- ✅ Active in production mode (`DRY_RUN=false`)
- ❌ Disabled in DRY_RUN mode (safe for testing)
- 🚨 Sends critical alerts on trigger
- 🛑 Gracefully shuts down trading

**Demo**: `python demo_circuit_breaker.py`  
**Docs**: `CIRCUIT_BREAKER_IMPLEMENTATION_SUMMARY.md`

---

### 💰 Kelly Criterion (Position Sizing)

**What**: Optimal position sizing based on win rate and profit factor

**Configuration**:
```python
# config.py or .env
ENABLE_KELLY_CRITERION=false  # Safe default: disabled
KELLY_FRACTION=0.5  # Half Kelly (conservative)
KELLY_MAX_POSITION_PCT=0.25  # Max 25% per position
```

**Usage**:
```python
from utils import calculate_kelly_criterion, calculate_kelly_position_size

# Calculate Kelly percentage
kelly_pct = calculate_kelly_criterion(
    win_rate=0.60,
    avg_win=150.0,
    avg_loss=100.0
)
# Returns: 0.2 (20% recommended)

# Calculate position size
position_size = calculate_kelly_position_size(
    capital=10000.0,
    kelly_pct=0.2,
    kelly_fraction=0.5,  # Half Kelly
    max_position_pct=0.25
)
# Returns: $1,000
```

**Safety**:
- ❌ Disabled by default (manual opt-in)
- ✅ Half Kelly default (conservative)
- ✅ Maximum position cap (25%)
- ✅ Negative edge detection (no trade)

**Demo**: `python demo_kelly_criterion.py`  
**Docs**: `KELLY_CRITERION_GUIDE.md`

---

### 📱 Alerts (Telegram + Email)

**What**: Real-time notifications for trades, risks, and performance

**Setup**:

**Telegram**:
1. Find @BotFather on Telegram
2. Send `/newbot` and follow instructions
3. Copy bot token
4. Send message to your bot
5. Get chat ID from `https://api.telegram.org/bot<TOKEN>/getUpdates`

**Email** (Gmail):
1. Enable 2-factor authentication
2. Generate App Password: Google Account → Security → App Passwords
3. Use App Password (not regular password)

**Configuration**:
```bash
# .env
ENABLE_TELEGRAM_ALERTS=true
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

ENABLE_EMAIL_ALERTS=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@example.com
```

**Usage**:
```python
from alerts import AlertManager

alerts = AlertManager()

# Trade alert
alerts.send_trade_alert(
    order_type='BUY',
    price=50000.0,
    quantity=0.1,
    capital=10000.0
)

# Circuit breaker alert
alerts.send_circuit_breaker_alert(
    drawdown_pct=15.2,
    current_capital=8480.0,
    initial_capital=10000.0
)

# Performance update
alerts.send_performance_update(
    capital=10500.0,
    initial_capital=10000.0,
    total_trades=42,
    win_rate=65.0
)
```

**Alert Types**:
- 📊 Trade execution (BUY/SELL)
- 🚨 Circuit breaker triggered
- 📈 Performance updates
- ❌ Error notifications

**Test**: `python -m pytest test_alert_system.py -v`  
**Docs**: `ALERT_SYSTEM_GUIDE.md`

---

### 💾 Database (Trade History)

**What**: Persistent storage for all trades, metrics, and analytics

**Configuration**:
```bash
# .env
USE_DATABASE=true
DATABASE_PATH=data/trading_bot.db
```

**Usage**:
```python
from db import DatabaseManager

db = DatabaseManager("data/trading_bot.db")

# Insert trade
db.insert_trade(
    symbol="BTC/USDT",
    order_type="BUY",
    price=50000.0,
    quantity=0.1,
    strategies=["RSI", "EMA"],
    capital=10000.0
)

# Get trades as DataFrame
df = db.get_trades_df(limit=100, symbol="BTC/USDT")

# Export to CSV
db.export_trades_to_csv("trades_export.csv")

# Get statistics
stats = db.get_trade_statistics()
print(f"Win Rate: {stats['win_rate']:.1f}%")
print(f"Total P&L: ${stats['total_pnl']:,.2f}")

# Daily performance
daily_perf = db.get_daily_performance()

# Strategy comparison
strategy_summary = db.get_strategy_summary()
```

**Features**:
- ✅ Auto-initialization (no manual setup)
- ✅ Transaction safety (ACID compliance)
- ✅ Error resilience (graceful degradation)
- ✅ Export to CSV/Excel/DataFrame
- ✅ Pre-computed views for performance

**Test**: `python -m pytest test_database.py -v`  
**Docs**: `DATABASE_INTEGRATION_GUIDE.md`

---

### 📈 Trailing Stop (Profit Protection)

**What**: Dynamic stop-loss that follows price favorably

**Configuration**:
```python
# config.py or .env
ENABLE_TRAILING_STOP=true
TRAILING_STOP_PERCENT=1.0  # 1% trailing distance
```

**Usage**:
```python
from strategy_core import ReversalTrailingStopStrategy

strategy = ReversalTrailingStopStrategy(
    initial_capital=10000.0,
    initial_stop_loss_percent=2.0,
    take_profit_percent=5.0,
    trailing_stop_percent=1.0  # 1% trailing
)

# Automatic in strategy execution
signal = strategy.generate_signal(df)
```

**How It Works**:
- 🎯 Tracks highest price since entry
- 📊 Updates stop-loss as price moves up
- 🛡️ Protects profits if price reverses
- ⚙️ Configurable trailing distance

**Demo**: `python demo_reversal_strategy.py`  
**Docs**: `STRATEGY_CORE_README.md`

---

### 📊 Dashboard & Export

**What**: Visualization and data export for analysis

**Usage**:
```python
from dashboard import create_dashboard

# Create dashboard
dashboard = create_dashboard()

# Display in console
dashboard.display_metrics_console()

# Export to HTML
dashboard.export_dashboard_html("dashboard.html")

# Generate charts
dashboard.generate_equity_chart()
dashboard.generate_pnl_chart()
```

**Export Options**:
```python
from db import DatabaseManager

db = DatabaseManager("data/trading_bot.db")

# CSV export
db.export_trades_to_csv("trades.csv")

# DataFrame export
df = db.get_trades_df()
df.to_excel("report.xlsx")

# Performance reports
daily_perf = db.get_daily_performance()
strategy_summary = db.get_strategy_summary()
```

**Examples**: `python dashboard_examples.py`  
**Docs**: `DASHBOARD_GUIDE.md`

---

### 🔍 Monitoring & Alerting

**What**: Real-time monitoring with configurable alerts

**Configuration**:
```python
# Custom thresholds
alert_config = {
    'performance_update_interval': 3600,  # 1 hour
    'critical_drawdown_threshold': 0.15,  # 15%
    'min_pnl_for_alert': 100.0,           # $100
    'error_alert_enabled': True
}
```

**Alert Triggers**:
- 📊 **Trade Events**: Buy/Sell execution
- 🚨 **Risk Events**: Circuit breaker, drawdown exceeded
- 📈 **Performance Events**: New equity high, milestones
- ⚠️ **System Events**: Startup, shutdown, errors

**Statistics**:
```python
from alerts import AlertManager

alerts = AlertManager()

# Get statistics
stats = alerts.get_statistics()
print(f"Telegram sent: {stats['telegram_sent']}")
print(f"Email sent: {stats['email_sent']}")
```

**Test**: `python -m pytest test_alert_system.py -v`

---

### 🎯 Multi-Strategy Support

**What**: Run multiple strategies simultaneously

**Configuration**:
```python
# config.py
active_strategies: list = ["rsi", "ema_crossover", "bollinger_bands"]
cooperation_logic: str = "OR"  # "AND" or "OR"

strategies = {
    "ma_crossover": {"short_window": 50, "long_window": 200},
    "rsi": {"window": 14, "oversold_threshold": 35},
    "bollinger_bands": {"window": 20, "std_dev": 2.0},
    "ema_crossover": {"short_window": 9, "long_window": 21}
}
```

**Usage**:
```python
from strategy import StrategyManager

manager = StrategyManager(config={
    'active_strategies': ['rsi', 'ema_crossover'],
    'cooperation_logic': 'OR',
    'strategies': config.strategies
})

# Get aggregated signal
signal, strategies = manager.get_aggregated_signal(df)

if signal == 1:  # BUY
    print(f"BUY from: {', '.join(strategies)}")
```

**Available Strategies**:
- ✅ MA Crossover
- ✅ RSI Mean Reversion
- ✅ Bollinger Bands
- ✅ EMA Crossover
- ✅ LSOB (Liquidity Sweep Order Block)
- ✅ Golden Cross
- ✅ Reversal Trailing Stop
- ✅ Video-Based Strategy

**Docs**: `STRATEGY_CORE_README.md`

---

## 🧪 Testing

### Run All Tests
```bash
# Core features (60 tests)
python -m pytest test_circuit_breaker.py test_kelly_criterion.py test_alert_system.py test_database.py -v

# All tests (133 tests)
python -m pytest -v

# With coverage
python -m pytest --cov=. --cov-report=html
```

### Individual Tests
```bash
# Circuit Breaker
python -m pytest test_circuit_breaker.py -v

# Kelly Criterion
python -m pytest test_kelly_criterion.py -v

# Alerts
python -m pytest test_alert_system.py -v

# Database
python -m pytest test_database.py -v
```

---

## 🎬 Demo Scripts

All features have interactive demos:

```bash
# Circuit Breaker
python demo_circuit_breaker.py

# Kelly Criterion
python demo_kelly_criterion.py

# Core Features (comprehensive)
python demo_core_features.py

# Trailing Stop Strategy
python demo_reversal_strategy.py

# Dashboard
python dashboard_examples.py

# Alerts (requires configuration)
# Configure .env first, then:
python -c "from alerts import AlertManager; AlertManager().send_trade_alert('BUY', 50000, 0.1, 10000)"
```

---

## 📚 Documentation

### Implementation Guides
- `CIRCUIT_BREAKER_IMPLEMENTATION_SUMMARY.md`
- `KELLY_CRITERION_SUMMARY.md`
- `KELLY_CRITERION_GUIDE.md`
- `ALERT_SYSTEM_GUIDE.md`
- `DATABASE_INTEGRATION_GUIDE.md`
- `CORE_FEATURES_IMPLEMENTATION_SUMMARY.md`
- `CORE_FEATURES_OPTIMIZATION_VERIFICATION.md`
- `CORE_FEATURES_COMPLETE_VERIFICATION.md`

### User Guides
- `LIVE_TRADING_SETUP_GUIDE.md`
- `BACKTESTING_GUIDE.md`
- `DASHBOARD_GUIDE.md`
- `TESTING_GUIDE.md`
- `README.md`

### Quick References
- This file: `CORE_FEATURES_QUICK_START.md`
- `FOLLOW_UP_ISSUES_RECOMMENDATIONS.md`

---

## 🔧 Troubleshooting

### Telegram Alerts Not Working
```bash
# Test connection
python -c "from alerts import TelegramAlert; t = TelegramAlert(); t.verify_connection()"

# Common issues:
# 1. Wrong bot token → Check .env
# 2. Wrong chat ID → Send message to bot, get ID from getUpdates
# 3. Bot not started → Send /start to your bot
```

### Email Alerts Not Working
```bash
# Test SMTP connection
python -c "from alerts import EmailAlert; e = EmailAlert(); e.verify_connection()"

# Common issues:
# 1. App Password not App Password → Use App Password, not regular password
# 2. 2FA not enabled → Enable 2-factor authentication first
# 3. Port blocked → Try port 465 with SSL
```

### Database Issues
```bash
# Reinitialize database
rm data/trading_bot.db
python -c "from db import DatabaseManager; DatabaseManager('data/trading_bot.db')"

# Check schema
python -c "from db import DatabaseManager; db = DatabaseManager('data/trading_bot.db'); print(db.get_table_info())"
```

### Tests Failing
```bash
# Install dependencies
pip install -r requirements.txt

# Run specific test
python -m pytest test_circuit_breaker.py::TestDrawdownCalculations::test_calculate_current_drawdown_20_percent -v

# Clear cache
rm -rf .pytest_cache __pycache__
python -m pytest --cache-clear
```

---

## 🚀 Production Deployment

### Pre-Production Checklist

- [ ] Configure API keys in `.env`
- [ ] Set `DRY_RUN=false` for live trading
- [ ] Configure circuit breaker (recommend 15%)
- [ ] Set up Telegram alerts
- [ ] Configure email alerts
- [ ] Test alert notifications
- [ ] Review position sizing
- [ ] Set up database backup
- [ ] Configure log rotation
- [ ] Test with paper trading (1 week minimum)
- [ ] Monitor initial trades closely
- [ ] Have emergency shutdown procedure

### Recommended Production Config
```bash
# .env for production
DRY_RUN=false  # Live trading
MAX_DRAWDOWN_LIMIT=0.15  # 15%
ENABLE_KELLY_CRITERION=false  # Start conservative
KELLY_FRACTION=0.5  # Half Kelly
ENABLE_TRAILING_STOP=true  # Protect profits
ENABLE_TELEGRAM_ALERTS=true  # Critical
ENABLE_EMAIL_ALERTS=true  # Backup
USE_DATABASE=true  # Track everything
```

### Emergency Shutdown
```bash
# Graceful shutdown
Ctrl+C  # Sends SIGINT, triggers cleanup

# Force shutdown
Ctrl+\ or kill <pid>

# Check running status
ps aux | grep python | grep main.py
```

---

## 📞 Support

**Documentation**: See `docs/` directory  
**Tests**: `python -m pytest -v`  
**Demos**: `python demo_*.py`  
**Issues**: Create GitHub issue with error details

---

**Made for Windows ⭐ | PowerShell-First | DRY_RUN Default**  
**Version**: 2.0.0  
**Last Updated**: 2025-10-15
