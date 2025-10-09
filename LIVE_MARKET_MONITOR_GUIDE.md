# 🔍 Live Market Monitor Guide

Complete guide for setting up and using the Live Market Monitoring Integration.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Alert System](#alert-system)
7. [Strategy Integration](#strategy-integration)
8. [API Reference](#api-reference)
9. [Troubleshooting](#troubleshooting)

---

## 🌟 Overview

The Live Market Monitor is a comprehensive module that provides real-time market monitoring capabilities with:

- **Multi-Exchange Support**: Primary support for Binance, extensible for other exchanges
- **Real-Time Data**: Live price feeds and OHLCV data
- **Strategy Integration**: Seamless integration with existing trading strategies
- **Alert System**: Configurable alerts for price changes, volume spikes, and trade signals
- **Data Validation**: Comprehensive OHLCV data validation and processing

---

## ✨ Features

### 🔄 Real-Time Monitoring
- Live price tracking for multiple trading pairs
- Configurable update intervals
- Historical data fetching and caching

### 📊 Data Processing
- OHLCV data validation
- Price change calculations (absolute and percentage)
- Volume spike detection
- Data caching for performance

### 🔔 Alert System
- **Price Change Alerts**: Triggered when price changes exceed threshold
- **Strategy Signal Alerts**: BUY/SELL signals from integrated strategies
- **Volume Spike Alerts**: Unusual volume activity detection
- **Custom Alerts**: Extensible alert system for custom conditions

### 🎯 Strategy Integration
- Compatible with all existing strategies:
  - MA Crossover
  - RSI Mean Reversion
  - Bollinger Bands
  - EMA Crossover
  - LSOB Strategy
  - Reversal-Trailing-Stop (via strategy_core.py)

### 🛡️ Robust Architecture
- Comprehensive error handling
- Rate limit management
- Retry logic for API calls
- Detailed logging

---

## 📦 Installation

### Prerequisites

Ensure you have the required dependencies installed:

```bash
pip install pandas numpy python-binance python-dotenv
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

### API Keys Setup

For live data from Binance, you'll need API keys:

1. **Create API Keys** (if not already done):
   - For testing: [Binance Testnet](https://testnet.binance.vision/)
   - For production: [Binance](https://www.binance.com/en/my/settings/api-management)

2. **Configure Keys** in `.env` or `keys.env`:

```env
# Binance Testnet (for testing)
BINANCE_TESTNET_API_KEY=your_testnet_api_key
BINANCE_TESTNET_SECRET_KEY=your_testnet_secret_key

# Binance Production (for live trading)
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
```

**Note**: You can monitor markets without API keys for public data (prices, historical data), but some features require authentication.

---

## ⚙️ Configuration

### Option 1: Using config.py

Edit `config.py` to set monitoring parameters:

```python
# Live Market Monitoring
enable_live_monitoring: bool = True
monitor_symbols: list = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
monitor_interval: str = "15m"  # 1m, 5m, 15m, 1h, 4h, 1d
monitor_update_interval: int = 60  # seconds
price_alert_threshold: float = 2.0  # %
volume_spike_multiplier: float = 2.0
enable_strategy_alerts: bool = True
```

### Option 2: Programmatic Configuration

```python
from live_market_monitor import LiveMarketMonitor

monitor = LiveMarketMonitor(
    symbols=['BTCUSDT', 'ETHUSDT'],
    interval='15m',
    update_interval=60,
    exchange='binance',
    testnet=True,
    price_alert_threshold=2.0
)
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `symbols` | List[str] | `['BTCUSDT']` | Trading pairs to monitor |
| `interval` | str | `'15m'` | Data timeframe (1m, 5m, 15m, 1h, 4h, 1d) |
| `update_interval` | int | `60` | Update frequency in seconds |
| `exchange` | str | `'binance'` | Exchange name (currently only Binance) |
| `testnet` | bool | `True` | Use testnet for testing |
| `price_alert_threshold` | float | `2.0` | Price change % for alerts |
| `volume_spike_multiplier` | float | `2.0` | Volume multiplier for spike detection |

---

## 🚀 Usage Examples

### Example 1: Basic Monitoring

Monitor BTC and ETH prices with default settings:

```python
from live_market_monitor import LiveMarketMonitor

# Initialize monitor
monitor = LiveMarketMonitor(
    symbols=['BTCUSDT', 'ETHUSDT'],
    interval='15m',
    update_interval=30,
    testnet=True
)

# Test connection
if monitor.test_connection():
    print("✓ Connected to exchange")
    
    # Start monitoring (runs indefinitely)
    monitor.start_monitoring()
else:
    print("❌ Connection failed")
```

### Example 2: Monitoring with Strategy Integration

Integrate with existing trading strategies:

```python
from live_market_monitor import LiveMarketMonitor
from strategy import TradingStrategy
from config import config

# Initialize monitor
monitor = LiveMarketMonitor(
    symbols=['BTCUSDT'],
    interval='15m',
    update_interval=60,
    testnet=True,
    price_alert_threshold=1.5
)

# Create and integrate strategy
strategy = TradingStrategy(config.to_dict())
monitor.integrate_strategy(strategy)

# Start monitoring
monitor.start_monitoring(duration=3600)  # Monitor for 1 hour
```

### Example 3: Custom Alert Handling

Register custom callbacks for alerts:

```python
from live_market_monitor import LiveMarketMonitor, Alert

def send_email_alert(alert: Alert):
    """Send email notification for critical alerts"""
    if alert.priority == "critical":
        # Your email sending logic here
        print(f"📧 Email sent: {alert.message}")

def log_to_database(alert: Alert):
    """Log alert to database"""
    # Your database logging logic here
    print(f"💾 Logged to DB: {alert}")

# Initialize monitor
monitor = LiveMarketMonitor(symbols=['BTCUSDT'], testnet=True)

# Register callbacks
monitor.register_alert_callback(send_email_alert)
monitor.register_alert_callback(log_to_database)

# Start monitoring
monitor.start_monitoring()
```

### Example 4: Single Monitoring Cycle

Perform a single monitoring cycle (useful for scheduled tasks):

```python
from live_market_monitor import LiveMarketMonitor

monitor = LiveMarketMonitor(
    symbols=['BTCUSDT', 'ETHUSDT'],
    testnet=True
)

# Perform one monitoring cycle
results = monitor.monitor_once()

# Process results
for symbol, data in results.items():
    print(f"\n{symbol}:")
    print(f"  Price: ${data['current_price']:.2f}")
    print(f"  Change: {data['price_metrics']['percent_change']:+.2f}%")
    
    if data['signal_info']:
        print(f"  Signal: {data['signal_info']['signal_text']}")
        print(f"  Strategies: {data['signal_info']['strategies']}")
```

### Example 5: Monitoring with Time Limit

Monitor for a specific duration:

```python
from live_market_monitor import LiveMarketMonitor

monitor = LiveMarketMonitor(
    symbols=['BTCUSDT'],
    interval='5m',
    update_interval=30,
    testnet=True
)

# Monitor for 10 minutes (600 seconds)
monitor.start_monitoring(duration=600)
```

---

## 🔔 Alert System

### Alert Types

The system supports multiple alert types:

1. **PRICE_CHANGE**: Significant price movements
2. **STRATEGY_SIGNAL**: BUY/SELL signals from strategies
3. **VOLUME_SPIKE**: Unusual volume activity
4. **VOLATILITY**: High volatility detected
5. **CUSTOM**: User-defined alerts

### Alert Priorities

- **low** ℹ️: Informational
- **normal** 📢: Standard alert
- **high** ⚠️: Important alert
- **critical** 🚨: Urgent attention required

### Configuring Alerts

```python
from live_market_monitor import AlertSystem

# Create alert system
alert_system = AlertSystem(
    price_change_threshold=2.0,    # Alert on 2% change
    volume_spike_multiplier=2.5    # Alert on 2.5x volume
)

# Register callback
def handle_alert(alert):
    if alert.priority == "critical":
        # Take immediate action
        print(f"🚨 CRITICAL: {alert}")
    else:
        print(f"📢 {alert}")

alert_system.register_callback(handle_alert)
```

### Alert History

Access alert history for analysis:

```python
# Get recent alerts
recent_alerts = monitor.alert_system.get_recent_alerts(limit=20)

for alert in recent_alerts:
    print(f"{alert.timestamp}: {alert.message}")

# Clear history
monitor.alert_system.clear_history()
```

---

## 🎯 Strategy Integration

### Compatible Strategies

The Live Market Monitor works with all strategies in the system:

- **MA Crossover**: Long-term trend following
- **RSI Mean Reversion**: Oversold/overbought detection
- **Bollinger Bands**: Volatility breakouts
- **EMA Crossover**: Fast trend detection
- **LSOB**: Long-Short on breakout
- **Reversal-Trailing-Stop**: Advanced reversal strategy

### Integration Example

```python
from live_market_monitor import LiveMarketMonitor
from strategy import TradingStrategy
from config import config

# Configure active strategies
config.active_strategies = ['rsi', 'ema_crossover']
config.cooperation_logic = 'OR'

# Initialize monitor and strategy
monitor = LiveMarketMonitor(symbols=['BTCUSDT'], testnet=True)
strategy = TradingStrategy(config.to_dict())

# Integrate
monitor.integrate_strategy(strategy)

# Monitor will now trigger alerts for strategy signals
monitor.start_monitoring()
```

### Strategy Signal Alerts

When strategies generate signals, alerts are triggered:

```
⚠️ [STRATEGY_SIGNAL] BTCUSDT: BUY signal from 2 strategies: RSI, EMA_Crossover at $50,234.50
```

---

## 📚 API Reference

### LiveMarketMonitor

Main monitoring class that orchestrates all components.

```python
LiveMarketMonitor(
    symbols: List[str],
    interval: str = '15m',
    update_interval: int = 60,
    exchange: str = 'binance',
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
    testnet: bool = True,
    price_alert_threshold: float = 2.0
)
```

**Methods:**

- `integrate_strategy(strategy)`: Integrate trading strategy
- `register_alert_callback(callback)`: Register alert callback
- `monitor_once()`: Perform single monitoring cycle
- `start_monitoring(duration=None)`: Start continuous monitoring
- `stop_monitoring()`: Stop monitoring
- `test_connection()`: Test exchange connection

### MarketDataFetcher

Fetches live market data from exchanges.

```python
MarketDataFetcher(
    exchange: str = 'binance',
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
    testnet: bool = True
)
```

**Methods:**

- `fetch_current_price(symbol)`: Get current price
- `fetch_historical_data(symbol, interval, limit)`: Get OHLCV data
- `test_connection()`: Test connection

### DataProcessor

Processes and validates OHLCV data.

```python
DataProcessor()
```

**Methods:**

- `process_ohlcv(df, symbol)`: Process and validate data
- `calculate_price_change(df)`: Calculate price metrics
- `get_cached_data(symbol)`: Retrieve cached data

### AlertSystem

Manages alerts and notifications.

```python
AlertSystem(
    price_change_threshold: float = 2.0,
    volume_spike_multiplier: float = 2.0
)
```

**Methods:**

- `register_callback(callback)`: Register alert callback
- `check_price_change(symbol, price_metrics)`: Check price alerts
- `check_strategy_signal(symbol, signal, strategies, price)`: Check signal alerts
- `check_volume_spike(symbol, df)`: Check volume alerts
- `get_recent_alerts(limit)`: Get recent alerts
- `clear_history()`: Clear alert history

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Connection Failures

**Problem**: Cannot connect to exchange

**Solution**:
```python
# Test connection
if not monitor.test_connection():
    print("Connection failed. Check:")
    print("- API keys are correct")
    print("- Network connectivity")
    print("- Exchange API status")
```

#### 2. Missing Data

**Problem**: No historical data fetched

**Solutions**:
- Verify symbol format (e.g., 'BTCUSDT' not 'BTC/USDT' for Binance)
- Check timeframe is valid (1m, 5m, 15m, 1h, 4h, 1d)
- Ensure sufficient data history exists

#### 3. No Alerts Triggered

**Problem**: Expected alerts not appearing

**Solutions**:
```python
# Lower thresholds for testing
monitor.alert_system.price_change_threshold = 0.5  # 0.5%
monitor.alert_system.volume_spike_multiplier = 1.5

# Verify callbacks are registered
print(f"Callbacks: {len(monitor.alert_system.alert_callbacks)}")
```

#### 4. Rate Limiting

**Problem**: API rate limit exceeded

**Solutions**:
- Increase `update_interval` (e.g., from 30 to 60 seconds)
- Reduce number of symbols monitored
- Use authenticated API for higher limits

### Logging

Enable detailed logging for debugging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now run monitor
monitor = LiveMarketMonitor(...)
```

### Testing

Run the test suite to verify installation:

```bash
python test_live_market_monitor.py
```

Expected output:
```
======================================================================
  Live Market Monitor - Test Suite
======================================================================
...
Ran 33 tests in 0.XXXs

OK
```

---

## 📝 Best Practices

### 1. Start with Testnet

Always test with testnet before using production:

```python
monitor = LiveMarketMonitor(..., testnet=True)
```

### 2. Reasonable Update Intervals

Balance between real-time data and API limits:

- **Very active**: 30-60 seconds
- **Normal**: 60-120 seconds
- **Background**: 300+ seconds

### 3. Alert Thresholds

Set appropriate thresholds based on asset volatility:

- **Stable assets** (stablecoins): 0.5-1%
- **Major crypto** (BTC, ETH): 1-2%
- **Altcoins**: 2-5%

### 4. Error Handling

Always handle potential errors:

```python
try:
    results = monitor.monitor_once()
except Exception as e:
    logger.error(f"Monitoring error: {e}")
    # Implement retry logic or alerts
```

### 5. Resource Management

Stop monitoring gracefully:

```python
try:
    monitor.start_monitoring()
except KeyboardInterrupt:
    monitor.stop_monitoring()
finally:
    # Cleanup resources
    pass
```

---

## 🎓 Advanced Usage

### Custom Data Fetchers

Extend for other exchanges:

```python
from live_market_monitor import MarketDataFetcher

class KrakenDataFetcher(MarketDataFetcher):
    def __init__(self, api_key, api_secret):
        # Implement Kraken-specific initialization
        pass
    
    def fetch_current_price(self, symbol):
        # Implement Kraken API call
        pass
```

### Custom Alert Conditions

Create custom alert logic:

```python
def check_custom_condition(symbol: str, df: pd.DataFrame) -> Optional[Alert]:
    """Check for specific market conditions"""
    # Your custom logic here
    if custom_condition_met:
        return Alert(
            alert_type=AlertType.CUSTOM,
            symbol=symbol,
            message="Custom condition met",
            priority="high"
        )
    return None

# Add to monitoring cycle
results = monitor.monitor_once()
for symbol, data in results.items():
    alert = check_custom_condition(symbol, data['df'])
    if alert:
        # Handle alert
        pass
```

### Integration with Notification Services

Send alerts via various channels:

```python
def send_telegram_alert(alert: Alert):
    """Send alert via Telegram"""
    import requests
    # Telegram bot API call
    pass

def send_slack_alert(alert: Alert):
    """Send alert via Slack"""
    import requests
    # Slack webhook call
    pass

monitor.register_alert_callback(send_telegram_alert)
monitor.register_alert_callback(send_slack_alert)
```

---

## 📞 Support

For issues or questions:

1. Check this documentation
2. Review test examples in `test_live_market_monitor.py`
3. Check the main README.md
4. Review existing issues in the repository

---

## 📄 License

This module is part of the ai.traiding project. See the main repository for license information.

---

**Happy Monitoring! 📊🚀**
