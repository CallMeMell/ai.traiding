# Batch Backtesting and Visualization Guide

## Overview

The batch backtesting system allows you to:
- Test multiple trading strategies simultaneously
- Compare performance metrics side-by-side
- Generate comprehensive visualizations
- Export results for further analysis

## Features

### 🚀 Batch Testing
- Test unlimited strategies with the same data
- Automatic performance comparison
- Ranking by ROI, Sharpe Ratio, and other metrics
- Error handling for problematic strategies

### 📊 Visualizations
- **Equity Curve**: Track capital growth over time
- **Drawdown Chart**: Visualize peak-to-trough declines
- **P&L Distribution**: Analyze profit/loss patterns
- Support for both Matplotlib (static) and Plotly (interactive)

### 📈 Performance Metrics
- Total ROI (Return on Investment)
- Win Rate
- Sharpe Ratio (risk-adjusted returns)
- Maximum Drawdown
- Best/Worst trades
- Average trade profit/loss

## Quick Start

### 1. Command Line Usage

```bash
# Run batch backtester interactively
python batch_backtester.py
```

Follow the prompts to:
1. Select data source
2. Configure capital and trade size
3. View results and rankings
4. Export CSV and visualizations

### 2. Programmatic Usage

```python
from batch_backtester import BatchBacktester
from utils import generate_sample_data
from strategy import MACrossoverStrategy, RSIStrategy

# Generate or load data
data = generate_sample_data(n_bars=1000, start_price=30000)

# Create batch backtester
batch_tester = BatchBacktester(
    initial_capital=10000.0,
    trade_size=100.0
)

# Add strategies to test
batch_tester.add_strategy(
    'MA Crossover (20/50)',
    MACrossoverStrategy({'short_window': 20, 'long_window': 50})
)

batch_tester.add_strategy(
    'RSI Mean Reversion',
    RSIStrategy({
        'window': 14,
        'oversold_threshold': 35,
        'overbought_threshold': 65
    })
)

# Run batch test
batch_tester.run_batch(data)

# Export results
batch_tester.export_results(output_dir='data')

# Generate visualizations
batch_tester.visualize_results(
    output_dir='data',
    use_plotly=False  # True for interactive HTML charts
)
```

## Visualization Examples

### Single Strategy Visualization

```python
from backtester import Backtester
from utils import generate_sample_data

# Run backtest
backtester = Backtester(initial_capital=10000.0)
data = generate_sample_data(n_bars=500)
backtester.run(data)

# Generate all visualizations
charts = backtester.visualize_results(
    output_dir='data/charts',
    use_plotly=True  # Interactive charts
)

print("Generated charts:")
for chart_type, path in charts.items():
    print(f"  {chart_type}: {path}")
```

### Standalone Visualization Functions

```python
from utils import (
    generate_equity_curve_chart,
    generate_drawdown_chart,
    generate_pnl_distribution_chart
)

# Equity curve
equity_curve = [
    {'timestamp': i, 'capital': 10000 + i * 50}
    for i in range(100)
]

generate_equity_curve_chart(
    equity_curve,
    'equity.png',
    use_plotly=False,
    title='My Strategy - Equity Curve'
)

# Drawdown
generate_drawdown_chart(
    equity_curve,
    'drawdown.html',
    use_plotly=True,
    title='My Strategy - Drawdown'
)

# P&L distribution
trades = [{'pnl': 50.0 if i % 2 == 0 else -25.0} for i in range(50)]

generate_pnl_distribution_chart(
    trades,
    'pnl_dist.png',
    use_plotly=False,
    title='Trade P&L Distribution'
)
```

## Output Files

### CSV Files

1. **batch_backtest_summary.csv**
   ```
   strategy_name,total_trades,total_pnl,roi,win_rate,best_trade,worst_trade,...
   MA Crossover,15,5430.20,54.30,60.0,1200.50,-450.30,...
   RSI Strategy,22,8750.45,87.50,72.7,2100.20,-320.10,...
   ```

2. **trades_<strategy_name>.csv**
   ```
   timestamp,type,price,quantity,capital_before,pnl
   2024-01-01 10:00,BUY,30000.0,100.0,10000.0,0
   2024-01-02 15:30,SELL,31000.0,100.0,10000.0,1000.0
   ```

### Visualization Files

#### Matplotlib (PNG)
- Fast generation
- Small file size (50-150 KB typically)
- Print-ready quality
- Perfect for reports

#### Plotly (HTML)
- Interactive features (zoom, pan, hover)
- Larger file size (2-5 MB typically)
- Best for analysis and presentations
- Shareable web format

## Performance Comparison

The batch backtester automatically ranks strategies:

```
Rank  Strategy                           Trades    ROI         Win Rate    Sharpe    
-------------------------------------------------------------------------------------
🥇 #1  RSI Mean Reversion                 22         +87.50%       72.7%      8.45
🥈 #2  MA Crossover (20/50)               15         +54.30%       60.0%      5.23
🥉 #3  Bollinger Bands                    18         +42.10%       55.6%      4.12
```

Detailed metrics for top 3 performers include:
- Initial vs Final Capital
- Total P&L
- ROI (Return on Investment)
- Total number of trades
- Win Rate
- Best and Worst trades
- Average trade P&L
- Sharpe Ratio
- Maximum Drawdown

## Advanced Usage

### Custom Strategy Comparison

```python
from batch_backtester import BatchBacktester
from golden_cross_strategy import GoldenCrossStrategy

batch_tester = BatchBacktester(initial_capital=10000.0)

# Test multiple parameter combinations
for short, long in [(20, 50), (50, 200), (100, 300)]:
    batch_tester.add_strategy(
        f'Golden Cross ({short}/{long})',
        GoldenCrossStrategy({
            'short_window': short,
            'long_window': long,
            'confirmation_days': 3
        })
    )

batch_tester.run_batch(data)
```

### Exporting Only Specific Visualizations

```python
from utils import generate_equity_curve_chart

# Only generate equity curves
for name, result in batch_tester.results.items():
    if result['equity_curve']:
        safe_name = name.replace('/', '_').replace(' ', '_')
        generate_equity_curve_chart(
            result['equity_curve'],
            f'data/equity_{safe_name}.png',
            use_plotly=False,
            title=f'Equity Curve - {name}'
        )
```

## Testing

Run the comprehensive test suite:

```bash
python test_batch_backtesting.py
```

The test suite includes:
- Visualization function tests
- Backtester integration tests
- Batch backtester functionality tests
- Edge case handling tests

All 19 tests should pass successfully.

## Troubleshooting

### Matplotlib Not Available
```bash
pip install matplotlib>=3.7.0
```

### Plotly Not Available
```bash
pip install plotly>=5.18.0
```

### Charts Not Generated
- Check that `output_dir` exists or can be created
- Verify data is not empty
- Check logs for error messages

### Memory Issues with Large Datasets
- Use Matplotlib instead of Plotly (smaller memory footprint)
- Process strategies in batches
- Reduce dataset size for initial testing

## Best Practices

1. **Start Small**: Test with 500-1000 bars initially
2. **Validate Data**: Ensure OHLCV data is clean and complete
3. **Use Plotly for Analysis**: Interactive charts help identify patterns
4. **Use Matplotlib for Reports**: Faster and smaller for batch exports
5. **Save Results**: Always export CSV for post-analysis
6. **Compare Apples to Apples**: Use identical data for all strategies

## Performance Tips

- Batch testing is CPU-intensive; expect 1-2 seconds per strategy per 1000 bars
- Plotly charts take longer to generate than Matplotlib
- Consider parallel processing for many strategies (future enhancement)
- Use simulated data for quick testing, real data for final validation

## Dependencies

```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
plotly>=5.18.0
```

## Examples Directory

See the following files for more examples:
- `batch_backtester.py` - Full CLI implementation
- `test_batch_backtesting.py` - Unit tests with usage examples
- `BACKTESTING_GUIDE.md` - Comprehensive guide with more details

## Contributing

When adding new strategies:
1. Ensure they implement `generate_signal(df)` method
2. Test with batch backtester to validate
3. Add to standard strategy list in `batch_backtester.py`
4. Update documentation

## License

Same as parent project.

## Support

For issues or questions:
1. Check test files for working examples
2. Review logs in `logs/trading_bot.log`
3. Verify all dependencies are installed
4. Try with simulated data first

---

**Version**: 1.0.0
**Last Updated**: 2024-10-09
