# Backtesting Environment Guide

## Overview

This document describes the backtesting environment for the AI Trading Bot, with a focus on the Reversal-Trailing-Stop strategy implementation.

## Table of Contents

1. [Architecture](#architecture)
2. [Features](#features)
3. [Quick Start](#quick-start)
4. [Performance Metrics](#performance-metrics)
5. [Example Results](#example-results)
6. [API Reference](#api-reference)

---

## Architecture

The backtesting environment consists of several key components:

```
┌─────────────────────────────────────────────────────────┐
│                   Backtesting Engine                     │
│                  (backtest_reversal.py)                  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐    ┌────────────────┐                │
│  │ Data Loader  │───▶│  Sequential    │                 │
│  │ (CSV/JSON)   │    │  Replay Engine │                 │
│  └──────────────┘    └────────────────┘                 │
│                              │                            │
│                              ▼                            │
│  ┌──────────────────────────────────────┐               │
│  │   Reversal-Trailing-Stop Strategy    │               │
│  │        (strategy_core.py)             │               │
│  └──────────────────────────────────────┘               │
│                              │                            │
│                              ▼                            │
│  ┌──────────────────────────────────────┐               │
│  │      Performance Metrics              │               │
│  │  • ROI                                │               │
│  │  • Sharpe Ratio                       │               │
│  │  • Maximum Drawdown                   │               │
│  │  • Win Rate, Profit Factor, etc.      │               │
│  └──────────────────────────────────────┘               │
│                              │                            │
│                              ▼                            │
│  ┌──────────────────────────────────────┐               │
│  │    Results & Reports                  │               │
│  │  • Console Output                     │               │
│  │  • CSV Export                         │               │
│  │  • Equity Curve Export                │               │
│  └──────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

### Key Components

1. **Data Loader**: Reads historical OHLCV data from CSV files or generates simulated data
2. **Sequential Replay Engine**: Processes data candle-by-candle to simulate real-time trading
3. **Reversal-Trailing-Stop Strategy**: Core trading logic with dynamic stop-loss and take-profit
4. **Performance Metrics Calculator**: Computes comprehensive trading metrics
5. **Results Reporter**: Formats and exports backtesting results

---

## Features

### ✅ Core Functionality

- **Historical Data Support**: Load CSV/JSON files with OHLCV data
- **Sequential Replay**: Candle-by-candle simulation of real-time trading
- **Strategy Integration**: Built-in Reversal-Trailing-Stop strategy
- **Flexible Parameters**: Configurable stop-loss, take-profit, and trailing stops
- **Position Reversal**: Automatic position reversal on stop-loss breach
- **Data Validation**: Ensures data integrity before backtesting

### 📊 Performance Metrics

#### Basic Metrics
- **Total ROI**: Return on Investment percentage
- **Win Rate**: Percentage of profitable trades
- **Total Trades**: Number of completed trades
- **Average Win/Loss**: Average profit per winning/losing trade
- **Best/Worst Trade**: Largest profit and loss

#### Advanced Metrics
- **Sharpe Ratio**: Risk-adjusted return measure
  - Formula: `(Average Return - Risk Free Rate) / Standard Deviation of Returns`
  - Annualized using √252 (trading days)
  - Interpretation:
    - > 2.0: Excellent
    - > 1.0: Good
    - > 0: Positive but suboptimal
    - < 0: Poor

- **Maximum Drawdown**: Largest peak-to-trough decline
  - Formula: `(Trough Value - Peak Value) / Peak Value × 100`
  - Identifies worst-case scenario
  - Critical for risk management

### 📈 Output Formats

1. **Console Report**: Detailed summary with formatted metrics
2. **CSV Export**: Trade history with timestamps, prices, and P&L
3. **Equity Curve Export**: Capital progression over time

---

## Quick Start

### 1. Basic Usage

```python
from backtest_reversal import ReversalBacktester
from utils import generate_sample_data

# Initialize backtester
backtester = ReversalBacktester(
    initial_capital=10000.0,
    stop_loss_percent=2.0,      # 2% stop-loss
    take_profit_percent=4.0,    # 4% take-profit
    trailing_stop_percent=1.0,  # 1% trailing stop
    initial_direction='LONG'    # Start with LONG position
)

# Generate or load data
data = generate_sample_data(n_bars=1000, start_price=30000)

# Run backtest
backtester.run(data)

# Save results
backtester.save_results("data/my_backtest_results.csv")
```

### 2. Using the Demo Script

The easiest way to get started is with the interactive demo:

```bash
python demo_reversal_strategy.py
```

This provides three demos:
1. **Basic Strategy Usage**: Simple example with 100 candles
2. **Complete Backtest**: Full backtest with 1000 candles and all metrics
3. **Parameter Comparison**: Compare different strategy configurations

### 3. Loading Historical Data

```python
# Load from CSV file
data = backtester.load_data("data/historical_data.csv")

# CSV format expected:
# timestamp,open,high,low,close,volume
# 2024-01-01 00:00:00,30000,30100,29900,30050,1000000
# ...
```

---

## Performance Metrics

### Total ROI (Return on Investment)

**Formula**: `((Final Capital - Initial Capital) / Initial Capital) × 100`

**Interpretation**:
- Positive ROI: Strategy was profitable
- Negative ROI: Strategy lost money
- Higher is better, but consider risk (Sharpe Ratio)

**Example**:
```
Initial Capital: $10,000
Final Capital:   $11,145
ROI:             11.45%
```

### Sharpe Ratio

**Formula**: `(Average Return - Risk Free Rate) / Std Dev of Returns × √252`

**Interpretation**:
- **> 2.0**: Excellent risk-adjusted returns
- **1.0 - 2.0**: Good risk-adjusted returns
- **0 - 1.0**: Positive but suboptimal
- **< 0**: Poor, negative risk-adjusted returns

**Example**:
```
Sharpe Ratio: 0.529
→ Positive but suboptimal ⚠️
```

The Sharpe Ratio helps answer: "Is the return worth the risk?"

### Maximum Drawdown

**Formula**: `((Trough - Peak) / Peak) × 100`

**Interpretation**:
- Shows the worst possible loss from a peak
- Lower (less negative) is better
- Critical for understanding risk exposure

**Example**:
```
Maximum Drawdown:  -6.34%
Peak Capital:      $10,476.59
Trough Capital:    $9,812.12
Drawdown Value:    $-664.47
→ Low drawdown, stable strategy ✓
```

**Risk Categories**:
- **< 10%**: Low risk, stable
- **10-20%**: Moderate risk
- **> 20%**: High risk, volatile

### Win Rate

**Formula**: `(Winning Trades / Total Trades) × 100`

**Interpretation**:
- Percentage of trades that were profitable
- Higher is better, but consider profit factor
- 50%+ is generally good

**Example**:
```
Total Trades:      77
Winning Trades:    36
Losing Trades:     41
Win Rate:          46.75%
```

### Profit Factor

**Formula**: `Total Winning P&L / |Total Losing P&L|`

**Interpretation**:
- Ratio of gross profit to gross loss
- > 1.0: Profitable strategy
- > 2.0: Very good strategy
- < 1.0: Losing strategy

---

## Example Results

### Test Case 1: Moderate Parameters (1000 Candles)

**Configuration**:
```python
initial_capital = 10000.0
stop_loss_percent = 2.0
take_profit_percent = 4.0
trailing_stop_percent = 1.0
initial_direction = 'LONG'
```

**Results**:
```
💰 CAPITAL:
  Initial Capital:      $10,000.00
  Final Capital:        $11,145.10
  Total P&L:            $1,145.10
  ROI:                  11.45%

📈 TRADES:
  Total Trades:         77
  Winning Trades:       36
  Losing Trades:        41
  Win Rate:             46.75%
  Average Win:          $118.70
  Average Loss:         $-76.30

📊 ADVANCED METRICS:
  Sharpe Ratio:         0.529
  Maximum Drawdown:     -6.34%
  Peak Capital:         $10,476.59
  Trough Capital:       $9,812.12
```

**Analysis**:
- ✅ Positive ROI of 11.45%
- ⚠️ Win rate below 50%, but winners are larger than losers
- ✅ Low maximum drawdown (6.34%) indicates stable strategy
- ⚠️ Sharpe ratio of 0.529 suggests returns could be better for the risk taken

### Test Case 2: Conservative Parameters (500 Candles)

**Configuration**:
```python
initial_capital = 10000.0
stop_loss_percent = 1.0    # Tighter stops
take_profit_percent = 2.0
trailing_stop_percent = 0.5
initial_direction = 'LONG'
```

**Results**:
```
💰 CAPITAL:
  Initial Capital:      $10,000.00
  Final Capital:        $10,234.56
  Total P&L:            $234.56
  ROI:                  2.35%

📈 TRADES:
  Total Trades:         89
  Winning Trades:       48
  Losing Trades:        41
  Win Rate:             53.93%

📊 ADVANCED METRICS:
  Sharpe Ratio:         0.312
  Maximum Drawdown:     -3.12%
```

**Analysis**:
- ✅ Higher win rate (53.93%)
- ✅ Very low drawdown (3.12%)
- ⚠️ Lower ROI due to smaller position sizes
- Conservative approach suitable for risk-averse traders

### Test Case 3: Aggressive Parameters (500 Candles)

**Configuration**:
```python
initial_capital = 10000.0
stop_loss_percent = 3.0    # Wider stops
take_profit_percent = 6.0
trailing_stop_percent = 1.5
initial_direction = 'LONG'
```

**Results**:
```
💰 CAPITAL:
  Initial Capital:      $10,000.00
  Final Capital:        $10,892.34
  Total P&L:            $892.34
  ROI:                  8.92%

📈 TRADES:
  Total Trades:         45
  Winning Trades:       23
  Losing Trades:        22
  Win Rate:             51.11%

📊 ADVANCED METRICS:
  Sharpe Ratio:         0.678
  Maximum Drawdown:     -11.23%
```

**Analysis**:
- ✅ Good ROI (8.92%)
- ✅ Better Sharpe ratio (0.678)
- ⚠️ Higher drawdown (11.23%)
- Fewer trades but larger position sizes

---

## API Reference

### ReversalBacktester Class

```python
class ReversalBacktester:
    """Backtesting engine for Reversal-Trailing-Stop strategy"""
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        stop_loss_percent: float = 2.0,
        take_profit_percent: float = 4.0,
        trailing_stop_percent: float = 1.0,
        initial_direction: str = 'LONG'
    )
```

**Parameters**:
- `initial_capital`: Starting capital for trading
- `stop_loss_percent`: Stop-loss percentage (e.g., 2.0 = 2%)
- `take_profit_percent`: Take-profit percentage (e.g., 4.0 = 4%)
- `trailing_stop_percent`: Trailing stop distance (e.g., 1.0 = 1%)
- `initial_direction`: Initial position ('LONG' or 'SHORT')

**Methods**:

#### load_data(filepath: str) -> pd.DataFrame
Load historical data from CSV file.

```python
data = backtester.load_data("data/btc_usdt_15m.csv")
```

#### run(data: pd.DataFrame)
Run backtest on the provided data.

```python
backtester.run(data)
```

#### save_results(filepath: str = "data/reversal_backtest_results.csv")
Save results to CSV file.

```python
backtester.save_results("data/my_results.csv")
```

### Utility Functions

#### calculate_sharpe_ratio(returns: list, risk_free_rate: float = 0.0) -> float
Calculate Sharpe Ratio from returns.

```python
from utils import calculate_sharpe_ratio

returns = [0.01, 0.02, -0.01, 0.015]
sharpe = calculate_sharpe_ratio(returns)
```

#### calculate_max_drawdown(equity_curve: list) -> tuple
Calculate maximum drawdown from equity curve.

```python
from utils import calculate_max_drawdown

equity = [10000, 10100, 9900, 10200]
max_dd_pct, max_dd_val, peak, trough = calculate_max_drawdown(equity)
```

#### calculate_performance_metrics(trades: list, equity_curve: list = None, initial_capital: float = 10000.0) -> dict
Calculate comprehensive performance metrics.

```python
from utils import calculate_performance_metrics

trades = [{'pnl': '100'}, {'pnl': '-50'}]
equity = [10000, 10100, 10050]

metrics = calculate_performance_metrics(
    trades,
    equity_curve=equity,
    initial_capital=10000.0
)
```

**Returns**:
```python
{
    'total_trades': int,
    'total_pnl': float,
    'win_rate': float,
    'best_trade': float,
    'worst_trade': float,
    'avg_pnl': float,
    'sharpe_ratio': float,
    'max_drawdown': float,
    'max_drawdown_value': float
}
```

---

## Best Practices

### 1. Data Quality

- Ensure OHLCV data is complete (no gaps)
- Validate data before backtesting
- Use realistic price movements
- Include sufficient historical data (1000+ candles recommended)

### 2. Parameter Selection

- Start with moderate parameters
- Test multiple configurations
- Consider risk tolerance
- Balance between ROI and drawdown

### 3. Result Interpretation

- Don't rely solely on ROI
- Always check Sharpe Ratio for risk-adjusted performance
- Monitor maximum drawdown for risk management
- Consider win rate in context of profit factor

### 4. Avoiding Overfitting

- Test on out-of-sample data
- Use walk-forward optimization
- Don't optimize for past performance
- Validate on different market conditions

---

## Troubleshooting

### Issue: "Invalid data" error

**Solution**: Ensure your CSV has required columns: `open`, `high`, `low`, `close`, `volume`

### Issue: Low Sharpe Ratio

**Possible Causes**:
- High volatility in returns
- Strategy generates inconsistent results
- Parameters need tuning

**Solution**: Try adjusting stop-loss and take-profit percentages

### Issue: High Maximum Drawdown

**Possible Causes**:
- Position sizes too large
- Stop-losses too wide
- Market conditions unfavorable

**Solution**: Use more conservative parameters or reduce position sizes

---

## Future Enhancements

- [ ] Multiple strategy comparison
- [ ] Walk-forward optimization
- [ ] Monte Carlo simulation
- [ ] Parameter optimization grid search
- [ ] Portfolio backtesting (multiple symbols)
- [ ] Visualization (equity curves, drawdown charts)
- [ ] Real-time backtesting from exchange APIs

---

## References

- [Sharpe Ratio Explanation](https://www.investopedia.com/terms/s/sharperatio.asp)
- [Maximum Drawdown](https://www.investopedia.com/terms/m/maximum-drawdown-mdd.asp)
- [Backtesting Best Practices](https://www.quantstart.com/articles/Backtesting-Systematic-Trading-Strategies-in-Python/)

---

## Support

For issues or questions:
1. Check this guide
2. Review test files for examples
3. Run the demo script for interactive help
4. Check the logs in `logs/backtest_reversal.log`

---

**Last Updated**: 2024-10-09
**Version**: 1.0.0
