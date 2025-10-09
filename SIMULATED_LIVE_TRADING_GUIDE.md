# Simulated Live-Trading Environment Guide

## Overview

The Simulated Live-Trading Environment provides a realistic sandbox for testing trading strategies in near real-time conditions without risking real money. It accurately simulates the challenges of live trading including order execution delays, price slippage, transaction fees, and market impact.

## Table of Contents

1. [Features](#features)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Performance Metrics](#performance-metrics)
7. [Best Practices](#best-practices)
8. [Integration Guide](#integration-guide)
9. [Troubleshooting](#troubleshooting)

---

## Features

### ✅ Realistic Trading Conditions

- **Order Execution Delays**: Simulates 50-200ms delays typical of real exchanges
- **Price Slippage**: 0.01-0.1% slippage based on order size and market volatility
- **Transaction Fees**: Maker/taker fee model (default 0.075% each)
- **Market Impact**: Larger orders experience higher slippage
- **Partial Fills**: Large orders may be partially filled (configurable)

### ✅ Comprehensive Performance Tracking

- Total orders (filled, rejected, partially filled)
- Trading volume and fees paid
- Slippage costs and execution delays
- Realized and unrealized P&L
- Sharpe ratio and maximum drawdown
- Complete equity curve tracking

### ✅ Flexible Configuration

- Enable/disable individual features (slippage, fees, delays)
- Adjustable slippage ranges
- Configurable execution delay bounds
- Custom fee structures
- Live data integration support

### ✅ Production-Ready Logging

- Detailed order execution logs
- Session-based log files
- Performance metrics export
- Execution history tracking

---

## Quick Start

### Installation

No additional dependencies required beyond the base trading bot:

```bash
pip install pandas numpy python-dotenv
```

### Basic Usage

```python
from simulated_live_trading import SimulatedLiveTradingEnvironment

# Create environment with default settings
env = SimulatedLiveTradingEnvironment(
    initial_capital=10000.0,
    use_live_data=False,
    enable_slippage=True,
    enable_fees=True,
    enable_execution_delay=True
)

# Place a market buy order
result = env.place_market_order(
    symbol='BTCUSDT',
    quantity=0.1,
    side='BUY',
    current_price=50000.0
)

# Check result
print(f"Order Status: {result.status}")
print(f"Execution Price: ${result.execution_price:.2f}")
print(f"Slippage: {result.slippage_percent:.3f}%")
print(f"Fees: ${result.fees:.2f}")

# Get account balance
balance = env.get_account_balance()
print(f"Total Equity: ${balance['total_equity']:,.2f}")

# Get performance metrics
metrics = env.get_performance_metrics()
print(f"Total P&L: ${metrics.total_pnl:.2f}")
```

### Run Demo

```bash
python demo_simulated_live_trading.py
```

### Run Tests

```bash
python test_simulated_live_trading.py
```

---

## Architecture

### Core Components

```
SimulatedLiveTradingEnvironment
├── Order Execution Engine
│   ├── Slippage Calculator
│   ├── Fee Calculator
│   ├── Delay Simulator
│   └── Market Impact Model
├── Position Manager
│   ├── Position Tracking
│   ├── P&L Calculation
│   └── Equity Curve Updates
├── Performance Metrics Engine
│   ├── Sharpe Ratio Calculator
│   ├── Drawdown Analyzer
│   └── Trade Statistics
└── Data Provider Interface
    ├── Live Data Integration (optional)
    └── Simulated Price Feed
```

### Data Flow

```
1. Strategy generates signal
2. Order placed → SimulatedLiveTradingEnvironment
3. Execution delay simulated
4. Current price fetched (live or simulated)
5. Slippage calculated
6. Execution price determined
7. Fees calculated
8. Capital/position updated
9. Metrics updated
10. Order result returned
```

---

## Configuration

### Global Configuration (config.py)

```python
# Slippage Settings
enable_slippage: bool = True
slippage_min_percent: float = 0.01      # 0.01%
slippage_max_percent: float = 0.1       # 0.1%
slippage_volatility_factor: float = 1.5

# Execution Delay Settings
enable_execution_delay: bool = True
execution_delay_min_ms: int = 50        # 50ms
execution_delay_max_ms: int = 200       # 200ms

# Fee Settings
enable_transaction_fees: bool = True
maker_fee_percent: float = 0.075        # 0.075%
taker_fee_percent: float = 0.075        # 0.075%

# Market Impact Settings
enable_market_impact: bool = True
market_impact_factor: float = 0.001     # 0.1% per 1% of daily volume

# Partial Fills
simulate_partial_fills: bool = True
min_fill_percent: float = 90.0          # 90% minimum fill
```

### Per-Environment Configuration

```python
env = SimulatedLiveTradingEnvironment(
    initial_capital=10000.0,
    use_live_data=False,              # Use simulated data
    enable_slippage=True,              # Enable slippage
    enable_fees=True,                  # Enable fees
    enable_execution_delay=True,       # Enable delays
    enable_market_impact=True,         # Enable market impact
    data_provider=None                 # Optional data provider
)
```

---

## Usage Examples

### Example 1: Basic Buy and Sell

```python
env = SimulatedLiveTradingEnvironment(initial_capital=10000.0)

# Buy BTC
buy_result = env.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
print(f"Bought at ${buy_result.execution_price:.2f}")

# Sell BTC at profit
sell_result = env.place_market_order('BTCUSDT', 0.1, 'SELL', current_price=51000.0)
print(f"Sold at ${sell_result.execution_price:.2f}")

# Check P&L
metrics = env.get_performance_metrics()
print(f"Realized P&L: ${metrics.realized_pnl:.2f}")
```

### Example 2: Multiple Position Management

```python
env = SimulatedLiveTradingEnvironment(initial_capital=50000.0)

# Open multiple positions
env.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
env.place_market_order('ETHUSDT', 2.0, 'BUY', current_price=3000.0)
env.place_market_order('BNBUSDT', 10.0, 'BUY', current_price=400.0)

# Check all positions
positions = env.get_positions()
for symbol, pos in positions.items():
    print(f"{symbol}:")
    print(f"  Quantity: {pos['quantity']}")
    print(f"  Entry: ${pos['entry_price']:.2f}")
    print(f"  Current: ${pos['current_price']:.2f}")
    print(f"  P&L: ${pos['unrealized_pnl']:.2f}")

# Close all positions
env.close_all_positions()
```

### Example 3: Strategy Backtesting with Realistic Conditions

```python
from strategy import TradingStrategy

env = SimulatedLiveTradingEnvironment(initial_capital=10000.0)
strategy = TradingStrategy()

# Simulate trading over historical data
for candle in historical_data:
    # Get strategy signal
    signal = strategy.analyze(candle)
    
    if signal == 'BUY' and len(env.positions) == 0:
        env.place_market_order(
            'BTCUSDT', 
            0.1, 
            'BUY', 
            current_price=candle['close']
        )
    elif signal == 'SELL' and 'BTCUSDT' in env.positions:
        env.place_market_order(
            'BTCUSDT',
            env.positions['BTCUSDT']['quantity'],
            'SELL',
            current_price=candle['close']
        )

# Get final metrics
metrics = env.get_performance_metrics()
print(f"Final Equity: ${metrics.equity_curve[-1]:,.2f}")
print(f"Sharpe Ratio: {metrics.sharpe_ratio:.3f}")
print(f"Max Drawdown: {metrics.max_drawdown_percent:.2f}%")
```

### Example 4: Comparing Scenarios

```python
def test_strategy(enable_slippage, enable_fees):
    env = SimulatedLiveTradingEnvironment(
        initial_capital=10000.0,
        enable_slippage=enable_slippage,
        enable_fees=enable_fees
    )
    
    # Execute trades
    for _ in range(10):
        env.place_market_order('BTCUSDT', 0.01, 'BUY', current_price=50000.0)
        env.place_market_order('BTCUSDT', 0.01, 'SELL', current_price=50500.0)
    
    metrics = env.get_performance_metrics()
    return metrics.total_pnl

# Compare scenarios
pnl_ideal = test_strategy(False, False)
pnl_realistic = test_strategy(True, True)

print(f"Ideal P&L: ${pnl_ideal:.2f}")
print(f"Realistic P&L: ${pnl_realistic:.2f}")
print(f"Cost of Reality: ${pnl_ideal - pnl_realistic:.2f}")
```

### Example 5: Session Logging

```python
env = SimulatedLiveTradingEnvironment(initial_capital=10000.0)

# Execute trades
env.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
env.place_market_order('ETHUSDT', 1.0, 'BUY', current_price=3000.0)
env.place_market_order('BTCUSDT', 0.05, 'SELL', current_price=51000.0)

# Save comprehensive session log
env.save_session_log("logs/my_session.log")
```

---

## Performance Metrics

### Available Metrics

| Metric | Description | Formula/Notes |
|--------|-------------|---------------|
| `total_orders` | Total number of orders placed | - |
| `filled_orders` | Orders successfully filled | - |
| `rejected_orders` | Orders rejected (insufficient capital, etc.) | - |
| `total_volume_traded` | Total USD value traded | Sum of all filled order values |
| `total_fees_paid` | Total transaction fees | Sum of all fees |
| `total_slippage` | Total slippage cost | Sum of absolute slippage amounts |
| `avg_slippage_percent` | Average slippage percentage | Mean of all slippage percentages |
| `avg_execution_delay_ms` | Average execution delay | Mean delay in milliseconds |
| `total_pnl` | Total profit/loss | Realized + Unrealized P&L |
| `realized_pnl` | P&L from closed positions | Actual gains/losses |
| `unrealized_pnl` | P&L from open positions | Mark-to-market value |
| `sharpe_ratio` | Risk-adjusted return | Mean return / Std dev of returns * √252 |
| `max_drawdown_percent` | Maximum portfolio decline | Max peak-to-trough decline |
| `equity_curve` | Portfolio value over time | List of equity values |

### Accessing Metrics

```python
metrics = env.get_performance_metrics()

# Access individual metrics
print(f"Total Orders: {metrics.total_orders}")
print(f"Fill Rate: {metrics.filled_orders / metrics.total_orders * 100:.1f}%")
print(f"Total Fees: ${metrics.total_fees_paid:.2f}")
print(f"Avg Slippage: {metrics.avg_slippage_percent:.4f}%")
print(f"Sharpe Ratio: {metrics.sharpe_ratio:.3f}")
print(f"Max Drawdown: {metrics.max_drawdown_percent:.2f}%")

# Export metrics
metrics_dict = metrics.to_dict()
```

---

## Best Practices

### 1. Start with Realistic Settings

```python
# Recommended for crypto markets
env = SimulatedLiveTradingEnvironment(
    initial_capital=10000.0,
    enable_slippage=True,      # Crypto has slippage
    enable_fees=True,          # Fees are significant
    enable_execution_delay=True # Delays affect HFT
)
```

### 2. Test with Different Conditions

```python
# Test best case
env_ideal = SimulatedLiveTradingEnvironment(
    enable_slippage=False,
    enable_fees=False
)

# Test realistic case
env_realistic = SimulatedLiveTradingEnvironment(
    enable_slippage=True,
    enable_fees=True
)

# Test worst case
env_worst = SimulatedLiveTradingEnvironment(
    enable_slippage=True,
    enable_fees=True,
    slippage_max_percent=0.2  # Higher slippage
)
```

### 3. Monitor Execution Quality

```python
for order in env.metrics.execution_history:
    if order.slippage_percent > 0.1:
        print(f"High slippage on {order.order_id}: {order.slippage_percent:.3f}%")
```

### 4. Account for Costs in Strategy

```python
# Calculate net profit target after costs
target_gross_profit = 1.0  # 1% target
expected_costs = 0.15  # ~0.15% slippage + fees
required_gross_profit = target_gross_profit + expected_costs

print(f"Need {required_gross_profit:.2f}% move for {target_gross_profit:.2f}% net profit")
```

### 5. Save Sessions for Analysis

```python
# Save after each trading session
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
env.save_session_log(f"logs/session_{timestamp}.log")
```

---

## Integration Guide

### With Existing Trading Bot

```python
# In main.py
from simulated_live_trading import SimulatedLiveTradingEnvironment

class LiveTradingBot:
    def __init__(self, paper_trading=True):
        if paper_trading:
            # Use simulated environment
            self.executor = SimulatedLiveTradingEnvironment(
                initial_capital=config.initial_capital,
                enable_slippage=True,
                enable_fees=True
            )
        else:
            # Use real broker
            self.executor = BrokerFactory.create_broker('binance')
    
    def execute_trade(self, signal, symbol, quantity):
        result = self.executor.place_market_order(
            symbol=symbol,
            quantity=quantity,
            side=signal,
            current_price=self.get_current_price(symbol)
        )
        return result
```

### With Live Data Feed

```python
from binance_integration import BinanceDataProvider

# Create data provider
data_provider = BinanceDataProvider(
    api_key=config.BINANCE_API_KEY,
    api_secret=config.BINANCE_SECRET_KEY,
    testnet=True
)

# Create environment with live data
env = SimulatedLiveTradingEnvironment(
    initial_capital=10000.0,
    use_live_data=True,
    data_provider=data_provider
)

# Orders will use real market prices
result = env.place_market_order('BTCUSDT', 0.1, 'BUY')
```

### With Custom Strategy

```python
from strategy_core import ReversalTrailingStopStrategy

strategy = ReversalTrailingStopStrategy(
    initial_capital=10000.0,
    stop_loss_percent=2.0,
    take_profit_percent=4.0
)

env = SimulatedLiveTradingEnvironment(initial_capital=10000.0)

# Connect strategy to environment
for signal in strategy.generate_signals(data):
    if signal['action'] == 'BUY':
        env.place_market_order(
            signal['symbol'],
            signal['quantity'],
            'BUY',
            current_price=signal['price']
        )
```

---

## Troubleshooting

### Orders Being Rejected

**Problem**: Orders fail with insufficient capital

**Solution**:
```python
# Check available capital before ordering
balance = env.get_account_balance()
max_order_value = balance['capital'] * 0.95  # Use 95% to account for fees/slippage

quantity = max_order_value / current_price
result = env.place_market_order(symbol, quantity, 'BUY', current_price)
```

### High Slippage

**Problem**: Slippage is unexpectedly high

**Solution**:
```python
# Check slippage settings in config.py
# Reduce slippage range if too aggressive
slippage_min_percent = 0.005  # 0.005% instead of 0.01%
slippage_max_percent = 0.05   # 0.05% instead of 0.1%

# Or reduce order sizes to minimize market impact
```

### Slow Execution

**Problem**: Orders take too long to execute

**Solution**:
```python
# Disable execution delay for faster simulation
env = SimulatedLiveTradingEnvironment(
    enable_execution_delay=False  # Speeds up simulation
)
```

### Missing Performance Metrics

**Problem**: Sharpe ratio or drawdown showing as 0

**Solution**:
```python
# Need sufficient trading history
# Ensure at least 10+ completed trades
metrics = env.get_performance_metrics()

if len(metrics.equity_curve) < 10:
    print("Insufficient data for advanced metrics")
else:
    print(f"Sharpe Ratio: {metrics.sharpe_ratio:.3f}")
```

---

## Advanced Features

### Custom Slippage Model

```python
# Override slippage calculation for custom behavior
class CustomSimulatedEnvironment(SimulatedLiveTradingEnvironment):
    def _calculate_slippage(self, symbol, side, quantity, base_price):
        # Custom slippage based on time of day, volatility, etc.
        hour = datetime.now().hour
        if 9 <= hour <= 16:  # Market hours
            base_slippage = 0.05  # 0.05% during market hours
        else:
            base_slippage = 0.15  # 0.15% after hours
        
        slippage_amount = base_price * (base_slippage / 100.0)
        if side.upper() == 'BUY':
            slippage_amount = abs(slippage_amount)
        else:
            slippage_amount = -abs(slippage_amount)
        
        return slippage_amount, base_slippage
```

### Real-time Strategy Testing

```python
import time

env = SimulatedLiveTradingEnvironment(initial_capital=10000.0)

while trading_active:
    # Get latest market data
    current_price = get_latest_price('BTCUSDT')
    
    # Apply strategy
    signal = strategy.analyze(current_price)
    
    # Execute in simulation
    if signal:
        result = env.place_market_order(
            'BTCUSDT',
            calculate_position_size(),
            signal,
            current_price=current_price
        )
        
        print(f"Order executed: {result.status}")
    
    time.sleep(60)  # Check every minute
```

---

## FAQ

**Q: Can I use this for algorithmic trading?**

A: Yes! This is designed specifically for testing algorithms in realistic conditions before deploying to live markets.

**Q: Does it support limit orders?**

A: Currently market orders only. Limit order support is planned for a future release.

**Q: How accurate is the slippage simulation?**

A: Slippage is based on typical crypto exchange conditions (0.01-0.1%). Actual slippage varies by exchange, market conditions, and order size.

**Q: Can I integrate with my own data feed?**

A: Yes! Pass a `data_provider` object that implements `get_current_price(symbol)` method.

**Q: Is this suitable for high-frequency trading?**

A: Yes, but be aware that execution delays (50-200ms) are simulated. You can disable delays for testing pure HFT logic.

---

## Next Steps

1. ✅ Run the demo: `python demo_simulated_live_trading.py`
2. ✅ Run the tests: `python test_simulated_live_trading.py`
3. ✅ Integrate with your strategy
4. ✅ Test with different market conditions
5. ✅ Analyze session logs for insights
6. ✅ Validate performance before going live

---

## Support

For issues, questions, or contributions:
- Review test files for usage examples
- Check demo script for common patterns
- See `broker_api.py` for integration examples
- Refer to `config.py` for all configuration options

---

**Happy Simulated Trading! 🚀**
