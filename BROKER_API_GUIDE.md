# 📈 Broker API Integration Guide

Complete guide for integrating and using the unified broker API for automated trading.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Broker Types](#broker-types)
6. [API Reference](#api-reference)
7. [Integration with Strategies](#integration-with-strategies)
8. [Logging and Debugging](#logging-and-debugging)
9. [Best Practices](#best-practices)
10. [Examples](#examples)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The Broker API module (`broker_api.py`) provides a unified interface for interacting with different broker APIs for automated trading. It abstracts broker-specific implementations and provides a consistent interface for placing orders, managing positions, and tracking account balances.

### Key Benefits

- **Unified Interface**: Work with multiple brokers using the same API
- **Easy Testing**: Built-in paper trading support for risk-free testing
- **Comprehensive Logging**: Track all trading actions for debugging and compliance
- **Strategy Integration**: Seamless integration with existing trading strategies
- **Error Handling**: Robust error handling and recovery

---

## Features

### Trading Operations
- ✅ Market orders (immediate execution)
- ✅ Limit orders (execute at specific price)
- ✅ Order cancellation
- ✅ Order status tracking
- ✅ Position management
- ✅ Account balance queries

### Supported Brokers
- ✅ **Binance** (Spot trading with testnet support)
- ✅ **Paper Trading** (Simulated trading for testing)
- 🔜 Interactive Brokers (planned)
- 🔜 Alpaca (legacy support available)

### Advanced Features
- ✅ Comprehensive action logging
- ✅ Position tracking and management
- ✅ Multi-asset portfolio support
- ✅ Paper trading mode for all brokers
- ✅ Automatic error recovery

---

## Installation

### Prerequisites

```bash
# Core dependencies
pip install pandas numpy python-dotenv

# For Binance support
pip install python-binance

# For Alpaca support (optional)
pip install alpaca-py
```

### Setup

1. **Clone or download** the repository

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure API keys** (for live trading):

Create a `.env` file or `keys.env`:

```env
# For Binance Testnet (recommended for testing)
BINANCE_TESTNET_API_KEY=your_testnet_api_key
BINANCE_TESTNET_SECRET_KEY=your_testnet_secret_key

# For Binance Production (use with caution!)
BINANCE_API_KEY=your_production_api_key
BINANCE_SECRET_KEY=your_production_secret_key
```

**Get Binance Testnet Keys**: https://testnet.binance.vision/

---

## Quick Start

### Paper Trading (No API Keys Required)

```python
from broker_api import BrokerFactory

# Create paper trading broker
broker = BrokerFactory.create_broker('paper', initial_capital=10000)

# Check balance
balance = broker.get_account_balance('USDT')
print(f"Balance: ${balance['total']:.2f}")

# Place a market buy order
order = broker.place_market_order(
    symbol='BTCUSDT',
    quantity=0.1,
    side='BUY',
    current_price=50000  # For paper trading
)
print(f"Order placed: {order['order_id']}")

# Check positions
positions = broker.get_positions()
for pos in positions:
    print(f"Position: {pos['symbol']} - {pos['quantity']}")

# Sell position
sell_order = broker.place_market_order(
    symbol='BTCUSDT',
    quantity=0.1,
    side='SELL',
    current_price=51000
)
print(f"Position closed with profit")
```

### Live Trading with Binance Testnet

```python
from broker_api import BrokerFactory
import os
from dotenv import load_dotenv

load_dotenv()

# Create Binance broker (testnet)
broker = BrokerFactory.create_broker(
    'binance',
    api_key=os.getenv('BINANCE_TESTNET_API_KEY'),
    api_secret=os.getenv('BINANCE_TESTNET_SECRET_KEY'),
    paper_trading=True  # Use testnet
)

# Get account balance
balance = broker.get_account_balance('USDT')
print(f"USDT Balance: ${balance['total']:.2f}")

# Place limit buy order
order = broker.place_limit_order(
    symbol='BTCUSDT',
    quantity=0.001,
    side='BUY',
    price=45000
)
print(f"Limit order placed: {order['order_id']}")

# Check open orders
open_orders = broker.get_open_orders('BTCUSDT')
print(f"Open orders: {len(open_orders)}")

# Cancel order
if open_orders:
    broker.cancel_order('BTCUSDT', open_orders[0]['order_id'])
    print("Order cancelled")
```

---

## Broker Types

### Paper Trading Broker

**Best for**: Testing strategies, learning, development

```python
broker = BrokerFactory.create_broker('paper', initial_capital=10000)
```

**Features**:
- No API keys required
- Instant order execution
- Tracks positions and P&L
- Perfect for backtesting

**Limitations**:
- No real market data (must provide prices)
- No slippage simulation
- No market impact

### Binance Broker

**Best for**: Live trading with cryptocurrency

```python
broker = BrokerFactory.create_broker(
    'binance',
    api_key='your_api_key',
    api_secret='your_secret',
    paper_trading=True  # Use testnet
)
```

**Features**:
- Real market execution
- Testnet for safe testing
- Spot trading support
- Multiple order types

**Requirements**:
- Binance API keys
- Funded account (testnet or production)

---

## API Reference

### BrokerFactory

#### `create_broker(broker_type, api_key, api_secret, paper_trading, **kwargs)`

Create a broker instance.

**Parameters**:
- `broker_type` (str): Broker type ('binance', 'paper')
- `api_key` (str, optional): API key
- `api_secret` (str, optional): API secret
- `paper_trading` (bool): Use paper trading mode
- `**kwargs`: Additional broker-specific parameters

**Returns**: BrokerInterface instance

### BrokerInterface (All Brokers)

#### `place_market_order(symbol, quantity, side, **kwargs)`

Place a market order for immediate execution.

**Parameters**:
- `symbol` (str): Trading symbol (e.g., 'BTCUSDT')
- `quantity` (float): Order quantity
- `side` (str): 'BUY' or 'SELL'
- `**kwargs`: Additional parameters (e.g., current_price for paper trading)

**Returns**: Dictionary with order details

```python
{
    'order_id': 'PAPER_1000',
    'symbol': 'BTCUSDT',
    'quantity': 0.1,
    'side': 'BUY',
    'type': 'MARKET',
    'status': 'FILLED',
    'filled_quantity': 0.1,
    'avg_price': 50000.0,
    'timestamp': '2024-01-01T12:00:00'
}
```

#### `place_limit_order(symbol, quantity, side, price, **kwargs)`

Place a limit order at a specific price.

**Parameters**:
- `symbol` (str): Trading symbol
- `quantity` (float): Order quantity
- `side` (str): 'BUY' or 'SELL'
- `price` (float): Limit price
- `**kwargs`: Additional parameters

**Returns**: Dictionary with order details

#### `cancel_order(symbol, order_id)`

Cancel an open order.

**Parameters**:
- `symbol` (str): Trading symbol
- `order_id` (str): Order ID to cancel

**Returns**: True if successful, False otherwise

#### `get_order_status(symbol, order_id)`

Get status of a specific order.

**Parameters**:
- `symbol` (str): Trading symbol
- `order_id` (str): Order ID

**Returns**: Dictionary with order status

#### `get_open_orders(symbol=None)`

Get all open orders.

**Parameters**:
- `symbol` (str, optional): Filter by symbol

**Returns**: List of open orders

#### `get_account_balance(asset=None)`

Get account balance.

**Parameters**:
- `asset` (str, optional): Asset symbol (e.g., 'USDT')

**Returns**: Dictionary with balance details

```python
{
    'free': 9500.0,      # Available balance
    'locked': 500.0,     # Locked in orders
    'total': 10000.0     # Total balance
}
```

#### `get_positions(symbol=None)`

Get open positions.

**Parameters**:
- `symbol` (str, optional): Filter by symbol

**Returns**: List of positions

```python
[
    {
        'symbol': 'BTCUSDT',
        'quantity': 0.1,
        'entry_price': 50000.0,
        'entry_time': '2024-01-01T12:00:00',
        'side': 'LONG'
    }
]
```

#### `close_position(symbol)`

Close an open position.

**Parameters**:
- `symbol` (str): Trading symbol

**Returns**: True if successful, False otherwise

---

## Integration with Strategies

### Using with Reversal-Trailing-Stop Strategy

```python
from broker_api import BrokerFactory
from strategy_core import ReversalTrailingStopStrategy
import pandas as pd

# Create broker
broker = BrokerFactory.create_broker('paper', initial_capital=10000)

# Create strategy
strategy = ReversalTrailingStopStrategy(
    initial_capital=10000,
    stop_loss_percent=2.0,
    take_profit_percent=4.0
)

# Get market data
df = pd.read_csv('market_data.csv')

# Process each candle
for i in range(len(df)):
    result = strategy.process_candle(df.iloc[i])
    
    if result['action'] == 'BUY':
        broker.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='BUY',
            current_price=result['price']
        )
        print(f"✓ Bought at ${result['price']:.2f}")
    
    elif result['action'] == 'SELL':
        broker.place_market_order(
            symbol='BTCUSDT',
            quantity=0.1,
            side='SELL',
            current_price=result['price']
        )
        print(f"✓ Sold at ${result['price']:.2f}")

# Get performance
positions = broker.get_positions()
balance = broker.get_account_balance('USDT')
print(f"\nFinal Balance: ${balance['total']:.2f}")
print(f"Open Positions: {len(positions)}")
```

### Using with Custom Strategy

```python
from broker_api import BrokerFactory

class MyStrategy:
    def __init__(self, broker):
        self.broker = broker
    
    def analyze(self, data):
        """Analyze market and return signal"""
        # Your strategy logic here
        if data['rsi'] < 30:
            return 'BUY'
        elif data['rsi'] > 70:
            return 'SELL'
        return 'HOLD'
    
    def execute(self, signal, price):
        """Execute trading signal"""
        if signal == 'BUY':
            # Check if we have capital
            balance = self.broker.get_account_balance('USDT')
            if balance['free'] > 1000:
                self.broker.place_market_order(
                    symbol='BTCUSDT',
                    quantity=0.01,
                    side='BUY',
                    current_price=price
                )
        
        elif signal == 'SELL':
            # Check if we have position
            positions = self.broker.get_positions('BTCUSDT')
            if positions:
                self.broker.close_position('BTCUSDT')

# Use strategy
broker = BrokerFactory.create_broker('paper', initial_capital=10000)
strategy = MyStrategy(broker)

# Run strategy
market_data = {'rsi': 25, 'price': 50000}
signal = strategy.analyze(market_data)
strategy.execute(signal, market_data['price'])
```

---

## Logging and Debugging

### Enable Detailed Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('broker_actions.log'),
        logging.StreamHandler()
    ]
)

# Create broker
broker = BrokerFactory.create_broker('paper', initial_capital=10000)

# All actions will be logged
broker.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000)
```

### Log Format

All broker actions are logged with the following format:

```
2024-01-01 12:00:00 - INFO - 🔄 BROKER ACTION: MARKET_ORDER_PLACED
2024-01-01 12:00:00 - INFO -   symbol: BTCUSDT
2024-01-01 12:00:00 - INFO -   side: BUY
2024-01-01 12:00:00 - INFO -   quantity: 0.1
2024-01-01 12:00:00 - INFO -   order_id: PAPER_1000
2024-01-01 12:00:00 - INFO -   status: FILLED
```

### Tracking Trade History

For paper trading:

```python
broker = BrokerFactory.create_broker('paper', initial_capital=10000)

# Execute some trades
broker.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000)
broker.place_market_order('BTCUSDT', 0.1, 'SELL', current_price=51000)

# Get trade history
trades = broker.trade_history
for trade in trades:
    print(f"{trade['timestamp']}: {trade['side']} {trade['quantity']} @ ${trade['price']}")
    if 'pnl' in trade:
        print(f"  P&L: ${trade['pnl']:.2f}")
```

---

## Best Practices

### 1. Always Start with Paper Trading

```python
# ✅ Good: Test first
broker = BrokerFactory.create_broker('paper', initial_capital=10000)
# Test your strategy...

# Then move to testnet
broker = BrokerFactory.create_broker(
    'binance',
    api_key=testnet_key,
    api_secret=testnet_secret,
    paper_trading=True
)
```

### 2. Use Try-Except for Error Handling

```python
try:
    order = broker.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000)
    print(f"Order placed: {order['order_id']}")
except ValueError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 3. Check Balances Before Trading

```python
def place_order_safely(broker, symbol, quantity, side, price):
    """Place order with balance check"""
    balance = broker.get_account_balance('USDT')
    
    if side == 'BUY':
        cost = quantity * price
        if balance['free'] < cost:
            print(f"Insufficient balance: ${balance['free']:.2f} < ${cost:.2f}")
            return None
    
    return broker.place_market_order(symbol, quantity, side, current_price=price)
```

### 4. Monitor Open Orders

```python
import time

def monitor_orders(broker, symbol):
    """Monitor and report open orders"""
    while True:
        orders = broker.get_open_orders(symbol)
        print(f"Open orders: {len(orders)}")
        
        for order in orders:
            print(f"  {order['order_id']}: {order['side']} {order['quantity']} @ ${order['price']}")
        
        time.sleep(10)  # Check every 10 seconds
```

### 5. Implement Position Sizing

```python
def calculate_position_size(balance, risk_percent, stop_loss_percent):
    """Calculate position size based on risk"""
    risk_amount = balance * risk_percent
    position_size = risk_amount / stop_loss_percent
    return position_size

# Example
balance = broker.get_account_balance('USDT')['total']
position_size = calculate_position_size(balance, 0.02, 0.05)  # 2% risk, 5% stop
```

---

## Examples

### Example 1: Simple Buy and Hold

```python
from broker_api import BrokerFactory
import time

# Create broker
broker = BrokerFactory.create_broker('paper', initial_capital=10000)

# Buy Bitcoin
print("Buying BTC...")
buy_order = broker.place_market_order(
    symbol='BTCUSDT',
    quantity=0.2,
    side='BUY',
    current_price=50000
)
print(f"✓ Bought 0.2 BTC at $50,000")

# Wait (simulated)
print("\nHolding position...")
time.sleep(2)

# Check position
positions = broker.get_positions()
print(f"Current positions: {len(positions)}")

# Sell at profit
print("\nSelling BTC...")
sell_order = broker.place_market_order(
    symbol='BTCUSDT',
    quantity=0.2,
    side='SELL',
    current_price=52000
)
print(f"✓ Sold 0.2 BTC at $52,000")

# Check profit
balance = broker.get_account_balance('USDT')
profit = balance['total'] - 10000
print(f"\nProfit: ${profit:.2f}")
```

### Example 2: Limit Order Strategy

```python
from broker_api import BrokerFactory
import time

broker = BrokerFactory.create_broker('paper', initial_capital=10000)

# Place multiple limit buy orders at different prices
buy_prices = [48000, 47000, 46000]

for price in buy_prices:
    order = broker.place_limit_order(
        symbol='BTCUSDT',
        quantity=0.05,
        side='BUY',
        price=price
    )
    print(f"✓ Limit buy order at ${price}")

# Check open orders
open_orders = broker.get_open_orders('BTCUSDT')
print(f"\nOpen orders: {len(open_orders)}")

# Cancel lowest price order
if open_orders:
    lowest_order = min(open_orders, key=lambda x: x['price'])
    broker.cancel_order('BTCUSDT', lowest_order['order_id'])
    print(f"✓ Cancelled order at ${lowest_order['price']}")
```

### Example 3: Multi-Asset Portfolio

```python
from broker_api import BrokerFactory

broker = BrokerFactory.create_broker('paper', initial_capital=10000)

# Buy multiple assets
assets = [
    ('BTCUSDT', 0.1, 50000),
    ('ETHUSDT', 1.0, 3000),
    ('BNBUSDT', 10.0, 400)
]

for symbol, quantity, price in assets:
    broker.place_market_order(
        symbol=symbol,
        quantity=quantity,
        side='BUY',
        current_price=price
    )
    print(f"✓ Bought {quantity} {symbol}")

# Check all positions
positions = broker.get_positions()
print(f"\nPortfolio: {len(positions)} positions")
for pos in positions:
    print(f"  {pos['symbol']}: {pos['quantity']}")

# Check balance
balance = broker.get_account_balance('USDT')
print(f"\nRemaining balance: ${balance['total']:.2f}")
```

---

## Troubleshooting

### Issue: Import Error

**Problem**: `ModuleNotFoundError: No module named 'broker_api'`

**Solution**:
```bash
# Make sure you're in the correct directory
cd /path/to/ai.traiding

# Verify file exists
ls -la broker_api.py
```

### Issue: API Key Error

**Problem**: `ValueError: API key and secret are required`

**Solution**:
1. Check your `.env` file exists
2. Verify API keys are set:
```python
import os
from dotenv import load_dotenv

load_dotenv()
print(f"API Key: {os.getenv('BINANCE_TESTNET_API_KEY')}")
```

### Issue: Insufficient Capital

**Problem**: `ValueError: Insufficient capital`

**Solution**:
```python
# Check balance before trading
balance = broker.get_account_balance('USDT')
print(f"Available: ${balance['free']:.2f}")

# Adjust quantity
cost = quantity * price
if cost > balance['free']:
    quantity = balance['free'] / price * 0.95  # Use 95% of available
```

### Issue: No Position to Sell

**Problem**: `ValueError: No position to sell`

**Solution**:
```python
# Always check position exists
positions = broker.get_positions('BTCUSDT')
if positions:
    broker.place_market_order('BTCUSDT', positions[0]['quantity'], 'SELL', current_price=price)
else:
    print("No position to sell")
```

### Issue: Rate Limiting

**Problem**: Too many API requests

**Solution**:
```python
import time

# Add delays between requests
broker.place_market_order(...)
time.sleep(0.5)  # Wait 500ms
broker.get_positions()
```

---

## Additional Resources

- **Binance API Documentation**: https://binance-docs.github.io/apidocs/spot/en/
- **Testnet**: https://testnet.binance.vision/
- **Strategy Core README**: [STRATEGY_CORE_README.md](STRATEGY_CORE_README.md)
- **Live Monitor Guide**: [LIVE_MARKET_MONITOR_GUIDE.md](LIVE_MARKET_MONITOR_GUIDE.md)

---

## Support

For issues, questions, or contributions:
- Check existing documentation
- Review example code
- Run tests: `python -m unittest test_broker_api`
- Check logs for detailed error messages

---

**⚠️ Important Disclaimer**:
- Always test with paper trading first
- Use testnet before production trading
- Never share your API keys
- Understand the risks of automated trading
- Start with small amounts in production

---

**Happy Trading! 📈**
