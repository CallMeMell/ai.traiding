# 🚀 Quick Start: Live Market Monitor

Get started with live market monitoring in 5 minutes!

---

## Prerequisites

Ensure you have the dependencies installed:

```bash
pip install -r requirements.txt
```

---

## Option 1: Interactive Demo (Recommended for First-Time Users)

Run the interactive demo to explore all features:

```bash
python demo_live_monitor.py
```

This will show you:
1. Basic market monitoring
2. Strategy integration
3. Custom alert handling
4. Continuous monitoring

---

## Option 2: Quick Monitor from Command Line

Start monitoring with default settings:

```bash
python main.py --monitor
```

This will:
- Monitor BTC/USDT and ETH/USDT (configurable in `config.py`)
- Update every 60 seconds
- Alert on 2% price changes
- Integrate with your active strategies
- Run until you press Ctrl+C

---

## Option 3: Custom Python Script

Create your own monitoring script in 5 lines:

```python
from live_market_monitor import LiveMarketMonitor

# Initialize and start monitoring
monitor = LiveMarketMonitor(
    symbols=['BTCUSDT', 'ETHUSDT'],
    interval='15m',
    update_interval=60,
    testnet=True
)

monitor.start_monitoring()
```

---

## Option 4: With Strategy Integration

Monitor markets with your trading strategies:

```python
from live_market_monitor import LiveMarketMonitor
from strategy import TradingStrategy
from config import config

# Setup monitor
monitor = LiveMarketMonitor(
    symbols=['BTCUSDT'],
    testnet=True,
    price_alert_threshold=1.5
)

# Add strategy
strategy = TradingStrategy(config.to_dict())
monitor.integrate_strategy(strategy)

# Start monitoring
monitor.start_monitoring()
```

---

## Configuration

Edit `config.py` to customize:

```python
# Live Market Monitoring Settings
enable_live_monitoring: bool = True
monitor_symbols: list = ["BTC/USDT", "ETH/USDT"]
monitor_interval: str = "15m"
monitor_update_interval: int = 60
price_alert_threshold: float = 2.0
```

---

## API Keys (Optional)

For full functionality, add Binance API keys to `.env`:

```env
# For testing (recommended)
BINANCE_TESTNET_API_KEY=your_testnet_key
BINANCE_TESTNET_SECRET_KEY=your_testnet_secret

# For production (use with caution)
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
```

Get testnet keys: https://testnet.binance.vision/

**Note**: The monitor works without API keys for public data (prices, history).

---

## Understanding Alerts

The monitor generates three types of alerts:

### 1. Price Change Alerts 📢
```
📢 [PRICE_CHANGE] BTCUSDT: Price UP 2.34% ($50,234.50)
```
Triggered when price changes exceed threshold.

### 2. Strategy Signal Alerts ⚠️
```
⚠️ [STRATEGY_SIGNAL] BTCUSDT: BUY signal from 2 strategies: RSI, EMA_Crossover at $50,234.50
```
Triggered when trading strategies generate signals.

### 3. Volume Spike Alerts 📢
```
📢 [VOLUME_SPIKE] BTCUSDT: Volume spike detected: 2.8x average
```
Triggered when trading volume spikes significantly.

---

## Common Use Cases

### Monitor and Paper Trade
```bash
# Run monitor with strategy in testnet
python main.py --monitor
```

### Quick Market Check
```python
from live_market_monitor import LiveMarketMonitor

monitor = LiveMarketMonitor(symbols=['BTCUSDT'], testnet=True)
results = monitor.monitor_once()  # Single check

for symbol, data in results.items():
    print(f"{symbol}: ${data['current_price']:,.2f}")
```

### Send Alerts to Telegram
```python
import requests

def send_telegram(alert):
    if alert.priority in ['high', 'critical']:
        # Your Telegram bot code
        print(f"📱 Telegram: {alert.message}")

monitor.register_alert_callback(send_telegram)
```

---

## Testing

Run the test suite to verify installation:

```bash
python test_live_market_monitor.py
```

Expected output:
```
Ran 33 tests in 0.XXXs
OK
```

---

## Troubleshooting

### Problem: Connection Failed
**Solution**: Check internet connection and API keys

### Problem: No Alerts
**Solution**: Lower `price_alert_threshold` in config.py

### Problem: Rate Limiting
**Solution**: Increase `monitor_update_interval` (e.g., to 120 seconds)

---

## Next Steps

1. ✅ Run the interactive demo: `python demo_live_monitor.py`
2. ✅ Read the full guide: [LIVE_MARKET_MONITOR_GUIDE.md](LIVE_MARKET_MONITOR_GUIDE.md)
3. ✅ Check the example with Reversal strategy: `python example_monitor_reversal_strategy.py`
4. ✅ Customize for your needs in `config.py`
5. ✅ Add your own alert callbacks

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `python main.py --monitor` | Start monitoring mode |
| `python demo_live_monitor.py` | Interactive demo |
| `python test_live_market_monitor.py` | Run tests |
| `python example_monitor_reversal_strategy.py` | Reversal strategy example |

---

## Support

- 📖 Full Documentation: [LIVE_MARKET_MONITOR_GUIDE.md](LIVE_MARKET_MONITOR_GUIDE.md)
- 📊 Main README: [README.md](README.md)
- 🧪 Test Examples: [test_live_market_monitor.py](test_live_market_monitor.py)

---

**Happy Monitoring! 🔍📊**
