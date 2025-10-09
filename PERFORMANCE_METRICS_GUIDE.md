# Performance Metrics and Dynamic Adjustments Guide

## Overview

This guide documents the enhanced performance metrics and dynamic adjustment features added to the trading system.

## Enhanced Performance Metrics

The backtesting engine now includes comprehensive performance metrics to better evaluate trading strategies.

### New Metrics

#### 1. Calmar Ratio
- **Definition**: Measures risk-adjusted return by comparing annual return to maximum drawdown
- **Formula**: `Calmar Ratio = Annual Return / Absolute Maximum Drawdown`
- **Interpretation**:
  - Higher values indicate better risk-adjusted performance
  - A ratio > 1.0 suggests good performance relative to risk
  - A ratio > 3.0 indicates excellent performance

#### 2. Volatility
- **Definition**: Measures the variability of returns over time
- **Formula**: Standard deviation of returns (annualized)
- **Interpretation**:
  - Lower volatility indicates more stable returns
  - Higher volatility suggests more unpredictable performance
  - Typically shown as an annualized percentage

#### 3. Average Trade Duration
- **Definition**: Average time a position is held before exit
- **Formula**: Sum of all trade durations / Number of trades
- **Interpretation**:
  - Helps understand typical holding periods
  - Can inform strategy optimization
  - Measured in hours

#### 4. Profit Factor
- **Definition**: Ratio of gross profits to gross losses
- **Formula**: `Profit Factor = Total Gross Profit / Total Gross Loss`
- **Interpretation**:
  - A ratio > 1.0 indicates profitability
  - A ratio of 2.0 means profits are twice the losses
  - Higher values indicate better performance

### Existing Metrics (Enhanced)

- **Total Trades**: Number of completed trades
- **Win Rate**: Percentage of profitable trades
- **Best/Worst Trade**: Largest profit and loss
- **Average P&L**: Mean profit/loss per trade
- **Sharpe Ratio**: Risk-adjusted return measure
- **Maximum Drawdown**: Largest peak-to-trough decline

## Usage

### In Backtesting

All metrics are automatically calculated and displayed in backtest reports:

```python
from backtester import Backtester

backtester = Backtester(initial_capital=10000.0)
data = backtester.load_data('data/historical_data.csv')
backtester.run(data)

# Metrics are automatically displayed in the report
```

Output example:
```
📊 BACKTEST REPORT
==================================================

💰 KAPITAL:
  Initial Capital:  $10,000.00
  Final Capital:    $11,250.00
  Total P&L:        $1,250.00
  ROI:              12.50%

📈 TRADES:
  Total Trades:     45
  Win Rate:         55.56%
  Best Trade:       $350.00
  Worst Trade:      $-180.00
  Average P&L:      $27.78
  Profit Factor:    1.89

📊 ERWEITERTE METRIKEN:
  Sharpe Ratio:     1.45
  Max Drawdown:     -8.50%
  Calmar Ratio:     1.47
  Volatility:       18.50%
  Avg Trade Duration: 4.25 hours
```

### Programmatic Access

You can also access metrics programmatically:

```python
from utils import calculate_performance_metrics

# Calculate metrics from trades and equity curve
metrics = calculate_performance_metrics(
    trades=trade_list,
    equity_curve=equity_values,
    initial_capital=10000.0
)

print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Calmar Ratio: {metrics['calmar_ratio']:.2f}")
print(f"Volatility: {metrics['volatility']*100:.2f}%")
print(f"Profit Factor: {metrics['profit_factor']:.2f}")
print(f"Avg Trade Duration: {metrics['avg_trade_duration']/3600:.2f} hours")
```

## Dynamic Parameter Adjustment

The Reversal-Trailing-Stop strategy now includes dynamic parameter adjustment based on market volatility.

### How It Works

1. **Volatility Monitoring**: The strategy continuously monitors market volatility using recent price history (default: 20 candles)

2. **Automatic Adjustment**: Parameters are automatically adjusted based on detected volatility:
   - **High Volatility (>2%)**: Widens stops by 50% to avoid premature exits
   - **Low Volatility (<0.5%)**: Tightens stops by 25% to lock in profits faster
   - **Normal Volatility**: Uses base parameters

3. **Affected Parameters**:
   - Stop Loss percentage
   - Take Profit percentage
   - Trailing Stop percentage

### Configuration

Dynamic adjustment can be enabled or disabled during initialization:

```python
from strategy_core import ReversalTrailingStopStrategy

# Enable dynamic adjustment (default)
strategy = ReversalTrailingStopStrategy(
    initial_capital=10000.0,
    stop_loss_percent=2.0,
    take_profit_percent=4.0,
    trailing_stop_percent=1.0,
    enable_dynamic_adjustment=True
)

# Disable dynamic adjustment
strategy_static = ReversalTrailingStopStrategy(
    initial_capital=10000.0,
    stop_loss_percent=2.0,
    take_profit_percent=4.0,
    trailing_stop_percent=1.0,
    enable_dynamic_adjustment=False
)
```

### Monitoring Adjustments

When dynamic adjustments occur, they are logged:

```
🔧 DYNAMIC ADJUSTMENT (HIGH VOLATILITY):
  Volatility: 2.45%
  Stop Loss: 2.00% → 3.00%
  Take Profit: 4.00% → 6.00%
  Trailing Stop: 1.00% → 1.50%
```

### Benefits

1. **Adaptability**: Strategy automatically adapts to changing market conditions
2. **Risk Management**: Wider stops in volatile markets prevent whipsaws
3. **Profit Optimization**: Tighter stops in stable markets maximize gains
4. **No Manual Intervention**: Adjustments happen automatically

### Customization

You can customize the adjustment behavior by modifying:

```python
# In strategy_core.py
HIGH_VOLATILITY_THRESHOLD = 2.0  # Default: 2%
LOW_VOLATILITY_THRESHOLD = 0.5   # Default: 0.5%
```

Or adjust the volatility calculation window:

```python
strategy.volatility_window = 30  # Use 30 candles instead of 20
```

## Best Practices

1. **Always Review Metrics Together**: No single metric tells the full story. Review all metrics holistically.

2. **Compare Against Benchmarks**: Compare your strategy's metrics against:
   - Buy-and-hold returns
   - Market indices
   - Other strategies

3. **Consider Market Conditions**: Dynamic adjustment works best in:
   - Markets with varying volatility
   - Medium to long-term trading
   - Strategies with clear volatility sensitivity

4. **Test Both Modes**: Test your strategy with dynamic adjustment both enabled and disabled to understand its impact.

5. **Monitor Volatility Patterns**: Log and analyze when adjustments occur to understand your strategy's behavior.

## Examples

### Example 1: High Volatility Market

```python
# Market with high volatility
strategy = ReversalTrailingStopStrategy(
    initial_capital=10000.0,
    stop_loss_percent=2.0,
    enable_dynamic_adjustment=True
)

# Strategy will widen stops to 3% when volatility exceeds 2%
# This prevents premature stop-outs during volatile swings
```

### Example 2: Stable Market

```python
# Market with low volatility
strategy = ReversalTrailingStopStrategy(
    initial_capital=10000.0,
    stop_loss_percent=2.0,
    enable_dynamic_adjustment=True
)

# Strategy will tighten stops to 1.5% when volatility drops below 0.5%
# This locks in profits more aggressively during stable trends
```

### Example 3: Comparative Analysis

```python
from backtest_reversal import ReversalBacktester

# Test with dynamic adjustment
backtester1 = ReversalBacktester(
    initial_capital=10000.0,
    stop_loss_percent=2.0
)
backtester1.strategy.enable_dynamic_adjustment = True

# Test without dynamic adjustment
backtester2 = ReversalBacktester(
    initial_capital=10000.0,
    stop_loss_percent=2.0
)
backtester2.strategy.enable_dynamic_adjustment = False

# Compare metrics from both runs
```

## Technical Implementation

### Volatility Calculation

```python
def _calculate_market_volatility(self) -> float:
    """
    Calculate recent market volatility using price history
    
    Returns:
        Volatility as a percentage (standard deviation of returns)
    """
    # Calculate returns from price history
    returns = [(price[i] - price[i-1]) / price[i-1] 
               for i in range(1, len(price_history))]
    
    # Standard deviation as volatility
    volatility = std_dev(returns) * 100
    
    return volatility
```

### Parameter Adjustment Logic

```python
def _adjust_parameters_based_on_volatility(self, volatility: float):
    """
    Dynamically adjust strategy parameters based on market volatility
    
    High volatility (>2%): Widen stops by 50%
    Low volatility (<0.5%): Tighten stops by 25%
    Normal volatility: Use base parameters
    """
    if volatility > 2.0:
        adjustment_factor = 1.5
    elif volatility < 0.5:
        adjustment_factor = 0.75
    else:
        adjustment_factor = 1.0
    
    # Apply adjustment
    self.stop_loss_percent = self.base_stop_loss_percent * adjustment_factor
    # ... (same for other parameters)
```

## Testing

Run the test suite to verify functionality:

```bash
# Test performance metrics
python test_performance_metrics.py

# Test dynamic adjustment
python test_dynamic_adjustment.py

# Test strategy core
python test_strategy_core.py
```

## Troubleshooting

### Issue: Metrics showing as 0.0

**Cause**: Insufficient data or no completed trades

**Solution**: Ensure you have:
- At least 2 data points in equity curve
- Completed trades (both entry and exit)
- Valid timestamps in trade data

### Issue: Dynamic adjustment not working

**Cause**: Feature might be disabled or insufficient price history

**Solution**: 
- Verify `enable_dynamic_adjustment=True`
- Ensure at least 2 candles have been processed
- Check logs for adjustment messages

### Issue: Extreme adjustment values

**Cause**: Very high or low calculated volatility

**Solution**:
- Review the volatility calculation window size
- Check for data quality issues (outliers, gaps)
- Consider adjusting thresholds

## Further Reading

- [Sharpe Ratio Explained](https://www.investopedia.com/terms/s/sharperatio.asp)
- [Calmar Ratio Guide](https://www.investopedia.com/terms/c/calmarratio.asp)
- [Maximum Drawdown](https://www.investopedia.com/terms/m/maximum-drawdown-mdd.asp)
- [Volatility in Trading](https://www.investopedia.com/terms/v/volatility.asp)
