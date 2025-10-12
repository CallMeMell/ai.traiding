# 🚀 Binance Testnet Adapter - Quick Reference

## 📋 Usage Cheat Sheet

### Import
```python
from system.adapters import AdapterFactory, OrderSide, OrderType
```

### Create Adapter
```python
# Via factory (recommended)
adapter = AdapterFactory.create('binance', testnet=True)

# Direct instantiation
from automation.brokers.binance import BinanceTestnetClient
adapter = BinanceTestnetClient()
```

### Connect & Health Check
```python
adapter.connect()                # Connect to testnet
is_healthy = adapter.health_check()  # Check health
```

### Place Order (Dry-Run)
```python
order = adapter.place_order(
    'BTCUSDT',              # Symbol
    OrderSide.BUY,          # Side (BUY/SELL)
    OrderType.MARKET,       # Type (MARKET/LIMIT)
    0.001                   # Quantity
)
```

### Get Account Info
```python
balance = adapter.get_account_balance()  # Account balance
price = adapter.get_market_price('BTCUSDT')  # Current price
```

### Query Orders
```python
status = adapter.get_order_status(order_id)  # Order status
open_orders = adapter.get_open_orders()      # Open orders
```

### Historical Data
```python
data = adapter.get_historical_data(
    'BTCUSDT',     # Symbol
    '1h',          # Interval
    limit=100      # Number of candles
)
```

### Disconnect
```python
adapter.disconnect()
```

---

## 🔐 Environment Variables

Add to `.env`:
```env
# Testnet API Keys (get from https://testnet.binance.vision)
BINANCE_TESTNET_API_KEY=your_testnet_api_key
BINANCE_TESTNET_SECRET_KEY=your_testnet_secret_key

# Safety: Keep dry-run enabled
DRY_RUN=true
```

---

## 🧪 Testing

```bash
# Run adapter tests
python3 -m pytest tests/test_binance_adapter.py -v

# Run verification
python3 verify_binance_adapter.py

# Run demo
python3 demo_binance_testnet_adapter.py
```

---

## 🛡️ Safety Features

- ✅ **Testnet-Only**: Cannot connect to production
- ✅ **DRY_RUN Default**: Orders simulated by default
- ✅ **No Hardcoded Keys**: Keys from environment only
- ✅ **Error Handling**: Comprehensive try-catch blocks

---

## 📖 Documentation

- Full docs: `BINANCE_TESTNET_ADAPTER_SUMMARY.md`
- API reference: Docstrings in `automation/brokers/binance.py`
- Examples: `tests/test_binance_adapter.py`

---

## ⚡ Common Patterns

### Pattern 1: Simple Health Check
```python
adapter = AdapterFactory.create('binance')
if adapter.connect() and adapter.health_check():
    print("✓ Ready to trade")
else:
    print("❌ Connection issues")
```

### Pattern 2: Price Monitoring
```python
adapter = AdapterFactory.create('binance')
adapter.connect()

price = adapter.get_market_price('BTCUSDT')
print(f"BTC Price: ${price:,.2f}")
```

### Pattern 3: Order Placement
```python
adapter = AdapterFactory.create('binance')
adapter.connect()

# Place order
order = adapter.place_order(
    'BTCUSDT', OrderSide.BUY, OrderType.MARKET, 0.001
)

# Check status
if order.get('status') == 'filled':
    print(f"✓ Order filled: {order['order_id']}")
```

---

**Made for Windows ⭐ | Testnet-Only | DRY_RUN Default**
