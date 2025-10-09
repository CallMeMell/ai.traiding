# 📘 Strategy Integration Guide - Reversal-Trailing-Stop

## Quick Start

The **Reversal-Trailing-Stop** strategy has been implemented in `strategy_core.py` and is ready to be integrated with the existing backtesting system.

---

## Integration Steps

### Option 1: Direct Integration with Existing System

To add the Reversal-Trailing-Stop strategy to the existing `StrategyManager`:

#### Step 1: Update `strategy.py`

Add the import and register the strategy in the `STRATEGY_MAP`:

```python
# In strategy.py, around line 292 (after the LSOB import)

# Try to add Reversal-Trailing-Stop strategy
try:
    from strategy_core import ReversalTrailingStopStrategy
    self.STRATEGY_MAP['reversal_trailing'] = ReversalTrailingStopStrategy
    logger.debug("✓ Reversal-Trailing-Stop strategy loaded")
except ImportError as e:
    logger.debug(f"Reversal-Trailing-Stop strategy not available: {e}")
```

#### Step 2: Update `config.py`

Add strategy parameters to the default configuration:

```python
# In config.py, in the strategies dictionary (around line 62)

strategies: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
    # ... existing strategies ...
    "reversal_trailing": {
        "rsi_period": 14,
        "rsi_oversold": 30,
        "rsi_overbought": 70,
        "roc_period": 10,
        "roc_threshold": 2.0,
        "volume_mult": 1.2,
        "atr_period": 14,
        "trailing_stop_mult": 2.0,
        "initial_stop_mult": 3.0,
        "min_bars": 50
    }
})
```

#### Step 3: Activate the Strategy

In your configuration, add `"reversal_trailing"` to active strategies:

```python
active_strategies: list = field(default_factory=lambda: ["reversal_trailing"])
```

Or update the existing config:

```python
from config import config

config.active_strategies = ["reversal_trailing"]
# Or combine with other strategies
config.active_strategies = ["reversal_trailing", "rsi", "ema_crossover"]
```

---

### Option 2: Standalone Usage

The strategy can also be used standalone with the built-in backtesting wrapper:

```python
from strategy_core import ReversalTrailingStopBacktest
import pandas as pd

# Load your data
df = pd.read_csv('data/historical_data.csv')

# Or generate sample data
from utils import generate_sample_data
df = generate_sample_data(n_bars=1000)

# Create backtest instance
backtest = ReversalTrailingStopBacktest(
    initial_capital=10000.0,
    trade_size=100.0,
    params={
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'atr_period': 14,
        'trailing_stop_mult': 2.0
    }
)

# Run backtest
results = backtest.run_backtest(df)

# Results include:
# - initial_capital, final_capital, total_pnl, roi
# - total_trades, winning_trades, losing_trades, win_rate
# - avg_win, avg_loss, best_trade, worst_trade
```

---

## Strategy Parameters

### Core Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `rsi_period` | 14 | RSI calculation period |
| `rsi_oversold` | 30 | Oversold threshold for bullish reversal |
| `rsi_overbought` | 70 | Overbought threshold for bearish reversal |
| `roc_period` | 10 | Rate of Change period |
| `roc_threshold` | 2.0 | Minimum ROC percentage for momentum |
| `volume_mult` | 1.2 | Volume multiplier for confirmation |
| `atr_period` | 14 | ATR calculation period |
| `trailing_stop_mult` | 2.0 | Trailing stop distance (ATR multiplier) |
| `initial_stop_mult` | 3.0 | Initial stop-loss distance (ATR multiplier) |
| `min_bars` | 50 | Minimum bars needed for calculation |

### Parameter Tuning Guide

#### Conservative (Lower Risk, Lower Returns)
```python
params = {
    'rsi_oversold': 20,        # More extreme oversold
    'rsi_overbought': 80,      # More extreme overbought
    'roc_threshold': 3.0,      # Stronger momentum required
    'trailing_stop_mult': 2.5, # Wider trailing stop
    'initial_stop_mult': 4.0   # Wider initial stop
}
```

#### Balanced (Default)
```python
params = {
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    'roc_threshold': 2.0,
    'trailing_stop_mult': 2.0,
    'initial_stop_mult': 3.0
}
```

#### Aggressive (Higher Risk, Higher Returns)
```python
params = {
    'rsi_oversold': 40,        # Less extreme oversold
    'rsi_overbought': 60,      # Less extreme overbought
    'roc_threshold': 1.0,      # Weaker momentum required
    'trailing_stop_mult': 1.5, # Tighter trailing stop
    'initial_stop_mult': 2.0   # Tighter initial stop
}
```

---

## Example: Full Backtest with Existing System

```python
from config import config
from backtester import Backtester
from utils import generate_sample_data

# Step 1: Update configuration
config.active_strategies = ["reversal_trailing"]
config.cooperation_logic = "OR"
config.backtest_initial_capital = 10000.0

# Ensure strategy parameters are set
config.strategies["reversal_trailing"] = {
    "rsi_period": 14,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "roc_period": 10,
    "roc_threshold": 2.0,
    "volume_mult": 1.2,
    "atr_period": 14,
    "trailing_stop_mult": 2.0,
    "initial_stop_mult": 3.0,
    "min_bars": 50
}

# Step 2: Generate or load data
df = generate_sample_data(
    n_bars=1000,
    start_price=30000,
    volatility=0.02
)

# Step 3: Run backtest
backtester = Backtester(initial_capital=10000.0)
results = backtester.run(df)

# Results are printed to console and saved to files
```

---

## Example: Multi-Strategy Combination

Combine Reversal-Trailing-Stop with other strategies:

```python
from config import config

# Use OR logic: Trade when ANY strategy gives signal
config.active_strategies = ["reversal_trailing", "rsi", "ema_crossover"]
config.cooperation_logic = "OR"

# Or use AND logic: Trade only when ALL strategies agree (more conservative)
config.active_strategies = ["reversal_trailing", "rsi"]
config.cooperation_logic = "AND"
```

---

## Monitoring Strategy Performance

### Check Position Info

```python
from strategy_core import ReversalTrailingStopStrategy

strategy = ReversalTrailingStopStrategy()

# After generating signals...
position_info = strategy.get_position_info()

print(f"Position Type: {position_info['position_type']}")
print(f"Entry Price: ${position_info['entry_price']:.2f}")
print(f"Stop Loss: ${position_info['stop_loss']:.2f}")
```

### View Strategy Description

```python
from strategy_core import ReversalTrailingStopStrategy

strategy = ReversalTrailingStopStrategy()
print(strategy.get_strategy_description())
```

---

## Testing

### Unit Test Example

```python
import pytest
from strategy_core import ReversalTrailingStopStrategy
import pandas as pd
import numpy as np

def test_reversal_trailing_stop_signal():
    """Test strategy generates valid signals"""
    strategy = ReversalTrailingStopStrategy()
    
    # Create test data
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='15min'),
        'open': np.random.uniform(29900, 30100, 100),
        'high': np.random.uniform(30000, 30200, 100),
        'low': np.random.uniform(29800, 30000, 100),
        'close': np.random.uniform(29900, 30100, 100),
        'volume': np.random.uniform(100, 200, 100)
    })
    
    signal = strategy.generate_signal(df)
    
    # Signal should be -1, 0, or 1
    assert signal in [-1, 0, 1]

def test_reversal_trailing_stop_indicators():
    """Test indicator calculations"""
    strategy = ReversalTrailingStopStrategy()
    
    df = pd.DataFrame({
        'close': [100, 102, 101, 103, 105, 104, 106, 108, 107, 109],
        'high': [101, 103, 102, 104, 106, 105, 107, 109, 108, 110],
        'low': [99, 101, 100, 102, 104, 103, 105, 107, 106, 108],
        'volume': [100] * 10
    })
    
    rsi = strategy.calculate_rsi(df, period=5)
    atr = strategy.calculate_atr(df, period=5)
    
    # RSI should be between 0 and 100
    assert rsi.iloc[-1] >= 0 and rsi.iloc[-1] <= 100
    
    # ATR should be positive
    assert atr.iloc[-1] > 0
```

---

## Troubleshooting

### Strategy Not Generating Signals

**Problem:** Strategy returns 0 (HOLD) for all bars

**Solutions:**
1. Check if data has enough bars (`min_bars` = 50 by default)
2. Verify OHLCV data is valid (use `validate_ohlcv_data()`)
3. Try more aggressive parameters (lower RSI thresholds)
4. Check if market conditions match strategy (needs reversals)

### Stop-Loss Not Triggering

**Problem:** Positions not closing when expected

**Solutions:**
1. Verify ATR is being calculated correctly
2. Check if `trailing_stop_mult` is too wide
3. Ensure price data includes high/low (not just close)

### Poor Backtest Performance

**Problem:** Low win rate or negative returns

**Solutions:**
1. **Market Mismatch:** Strategy works best in volatile, mean-reverting markets
2. **Parameter Tuning:** Try different combinations (see Parameter Tuning Guide)
3. **Timeframe:** Test on different timeframes (15m, 1H, 4H)
4. **Combine Strategies:** Use with other strategies (AND/OR logic)
5. **Data Quality:** Ensure historical data is clean and accurate

---

## Best Practices

### 1. Parameter Optimization
- Use walk-forward analysis (train on period 1, test on period 2)
- Test on out-of-sample data to avoid overfitting
- Document which parameters work for which market conditions

### 2. Risk Management
- Never risk more than 1-2% per trade
- Use the built-in stop-loss mechanism
- Monitor drawdown continuously
- Consider portfolio-level risk limits

### 3. Market Conditions
- **Best For:** Volatile markets with clear reversals
- **Good For:** Cryptocurrency 15m-4H timeframes
- **Avoid:** Very low volatility or strongly trending markets

### 4. Backtesting
- Use at least 1-2 years of historical data
- Include transaction costs (0.1-0.25% per trade)
- Model realistic slippage
- Paper trade for 30+ days before live

---

## Additional Resources

### Documentation
- See `IMPLEMENTATION_PLAN.md` for overall system architecture
- See `ADDITIONAL_STRATEGIES.md` for 20 other strategy ideas
- See `ROADMAP.md` for project development phases

### Code Examples
- `strategy_core.py` - Strategy implementation with inline documentation
- `backtester.py` - Existing backtesting framework
- `strategy.py` - Strategy manager and base classes

### Support
- Review FAQ.md for common questions
- Check logs in `logs/trading_bot.log` for debugging
- Use demo mode first: `python demo.py`

---

## Next Steps

1. **Test Standalone:** Run `python strategy_core.py` to see demo
2. **Integrate:** Follow Option 1 steps to add to existing system
3. **Backtest:** Run extensive backtests on historical data
4. **Optimize:** Tune parameters for your specific market
5. **Paper Trade:** Test with real-time data but no real money
6. **Go Live:** Only after 30+ days successful paper trading

---

**Version:** 1.0  
**Last Updated:** October 2024  
**Status:** Ready for Integration and Testing
