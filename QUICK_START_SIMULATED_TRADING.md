# Quick Start: Simulated Live-Trading

## 🚀 Get Started in 2 Minutes

### Installation
```bash
# All dependencies should already be installed
# If not:
pip install pandas numpy python-dotenv
```

### Option 1: Direct Usage

```python
from simulated_live_trading import SimulatedLiveTradingEnvironment

# Create environment
env = SimulatedLiveTradingEnvironment(initial_capital=10000.0)

# Buy
buy = env.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
print(f"Bought at ${buy.execution_price:.2f}")
print(f"Slippage: {buy.slippage_percent:.3f}%")
print(f"Fees: ${buy.fees:.2f}")

# Sell
sell = env.place_market_order('BTCUSDT', 0.1, 'SELL', current_price=51000.0)
print(f"Sold at ${sell.execution_price:.2f}")

# Check metrics
metrics = env.get_performance_metrics()
print(f"Total P&L: ${metrics.total_pnl:.2f}")
```

### Option 2: Via Broker API (Recommended)

```python
from broker_api import BrokerFactory

# Create simulated broker
broker = BrokerFactory.create_broker('simulated', initial_capital=10000.0)

# Place order
order = broker.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
print(f"Order: {order['status']}")
print(f"Price: ${order['avg_price']:.2f}")
print(f"Slippage: {order['slippage_percent']:.3f}%")
print(f"Fees: ${order['fees']:.2f}")

# Get balance
balance = broker.get_account_balance()
print(f"Equity: ${balance['total']:,.2f}")

# Get positions
positions = broker.get_positions()
for pos in positions:
    print(f"{pos['symbol']}: {pos['quantity']} @ ${pos['entry_price']:.2f}")
```

### Option 3: In Your Trading Bot

```python
# In your trading bot initialization
class MyTradingBot:
    def __init__(self, paper_trading=True, realistic_simulation=True):
        if realistic_simulation and paper_trading:
            # Use realistic simulation
            self.broker = BrokerFactory.create_broker(
                'simulated',
                initial_capital=10000.0,
                enable_slippage=True,
                enable_fees=True
            )
        elif paper_trading:
            # Use basic paper trading
            self.broker = BrokerFactory.create_broker('paper')
        else:
            # Use live trading
            self.broker = BrokerFactory.create_broker('binance')
```

## 📊 Run Examples

### Demo Script
```bash
python demo_simulated_live_trading.py
```

Shows:
- Basic trading with all features
- Comparison with/without slippage & fees  
- High-frequency trading simulation
- Session logging

### Run Tests
```bash
python test_simulated_live_trading.py
```

Runs 25+ comprehensive tests

## ⚙️ Configuration

### Enable/Disable Features

```python
env = SimulatedLiveTradingEnvironment(
    initial_capital=10000.0,
    enable_slippage=True,        # Price slippage (0.01-0.1%)
    enable_fees=True,            # Transaction fees (0.075%)
    enable_execution_delay=True, # Order delays (50-200ms)
    enable_market_impact=True    # Market impact on large orders
)
```

### Global Settings (config.py)

```python
# Slippage range
slippage_min_percent = 0.01  # 0.01%
slippage_max_percent = 0.1   # 0.1%

# Execution delay
execution_delay_min_ms = 50   # 50ms
execution_delay_max_ms = 200  # 200ms

# Fees
maker_fee_percent = 0.075     # 0.075%
taker_fee_percent = 0.075     # 0.075%
```

## 📈 Key Features

| Feature | Description | Impact |
|---------|-------------|--------|
| **Slippage** | Price moves against you | 0.01-0.1% per order |
| **Fees** | Transaction costs | 0.075% maker/taker |
| **Delays** | Execution latency | 50-200ms per order |
| **Market Impact** | Large orders affect price | Scales with order size |

## 🎯 Common Scenarios

### Scenario 1: Test a Strategy
```python
env = SimulatedLiveTradingEnvironment(initial_capital=10000.0)

for signal in strategy_signals:
    if signal == 'BUY':
        env.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=price)
    elif signal == 'SELL':
        if 'BTCUSDT' in env.positions:
            qty = env.positions['BTCUSDT']['quantity']
            env.place_market_order('BTCUSDT', qty, 'SELL', current_price=price)

metrics = env.get_performance_metrics()
print(f"Sharpe Ratio: {metrics.sharpe_ratio:.3f}")
print(f"Max Drawdown: {metrics.max_drawdown_percent:.2f}%")
```

### Scenario 2: Compare Ideal vs Reality
```python
def test_strategy(enable_costs):
    env = SimulatedLiveTradingEnvironment(
        initial_capital=10000.0,
        enable_slippage=enable_costs,
        enable_fees=enable_costs
    )
    # ... execute trades ...
    return env.get_performance_metrics().total_pnl

ideal_pnl = test_strategy(False)
real_pnl = test_strategy(True)
print(f"Cost of Reality: ${ideal_pnl - real_pnl:.2f}")
```

### Scenario 3: Save Trading Session
```python
env = SimulatedLiveTradingEnvironment(initial_capital=10000.0)
# ... execute trades ...

# Save detailed log
env.save_session_log("logs/my_strategy_test.log")

# Log includes:
# - All order executions
# - Slippage and fees breakdown
# - Performance metrics
# - Complete equity curve
```

## 📝 Performance Metrics

```python
metrics = env.get_performance_metrics()

print(f"Orders: {metrics.total_orders}")
print(f"Filled: {metrics.filled_orders}")
print(f"Volume: ${metrics.total_volume_traded:,.2f}")
print(f"Fees Paid: ${metrics.total_fees_paid:.2f}")
print(f"Avg Slippage: {metrics.avg_slippage_percent:.4f}%")
print(f"Avg Delay: {metrics.avg_execution_delay_ms:.1f}ms")
print(f"Total P&L: ${metrics.total_pnl:.2f}")
print(f"Sharpe: {metrics.sharpe_ratio:.3f}")
print(f"Max DD: {metrics.max_drawdown_percent:.2f}%")
```

## 🔧 Troubleshooting

### Orders Rejected?
```python
# Check capital before ordering
balance = env.get_account_balance()
print(f"Available: ${balance['capital']:.2f}")

# Order smaller amounts or use position sizing
max_order = balance['capital'] * 0.95 / current_price
```

### Too Slow?
```python
# Disable execution delay for faster simulation
env = SimulatedLiveTradingEnvironment(
    enable_execution_delay=False  # Much faster
)
```

### No Metrics?
```python
# Need enough trades for statistics
if metrics.total_orders < 10:
    print("Need more trades for metrics")
```

## 📚 Documentation

- **Full Guide**: `SIMULATED_LIVE_TRADING_GUIDE.md`
- **Broker API**: `BROKER_API_GUIDE.md`
- **Examples**: `demo_simulated_live_trading.py`
- **Tests**: `test_simulated_live_trading.py`

## 🎓 Next Steps

1. ✅ Run demo: `python demo_simulated_live_trading.py`
2. ✅ Run tests: `python test_simulated_live_trading.py`
3. ✅ Integrate with your strategy
4. ✅ Test different market conditions
5. ✅ Compare with/without costs
6. ✅ Analyze session logs
7. ✅ Ready for live trading!

---

**Questions?** Check the full guide in `SIMULATED_LIVE_TRADING_GUIDE.md`
