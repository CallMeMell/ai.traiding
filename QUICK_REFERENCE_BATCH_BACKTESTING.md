# Quick Reference - Batch Backtesting & Visualization

## 🚀 Quick Start (30 seconds)

### Run Interactive Demo
```bash
python demo_batch_backtest.py
```

### Run Batch Backtester
```bash
python batch_backtester.py
```

### Run Tests
```bash
python test_batch_backtesting.py
```

## 📋 Common Use Cases

### 1. Compare Multiple Strategies
```python
from batch_backtester import BatchBacktester
from strategy import MACrossoverStrategy, RSIStrategy
from utils import generate_sample_data

# Setup
data = generate_sample_data(n_bars=1000, start_price=30000)
batch = BatchBacktester(initial_capital=10000.0)

# Add strategies
batch.add_strategy('MA 20/50', MACrossoverStrategy({'short_window': 20, 'long_window': 50}))
batch.add_strategy('RSI', RSIStrategy({'window': 14}))

# Run and visualize
batch.run_batch(data)
batch.export_results('data')
batch.visualize_results('data', use_plotly=True)
```

### 2. Single Strategy with Visualizations
```python
from backtester import Backtester
from utils import generate_sample_data

# Run backtest
backtester = Backtester(initial_capital=10000.0)
data = generate_sample_data(n_bars=500)
backtester.run(data)

# Generate charts
charts = backtester.visualize_results('data/charts', use_plotly=False)
```

### 3. Standalone Visualizations
```python
from utils import generate_equity_curve_chart, generate_drawdown_chart

# Equity curve
equity = [{'timestamp': i, 'capital': 10000 + i*50} for i in range(100)]
generate_equity_curve_chart(equity, 'equity.png')

# Drawdown
generate_drawdown_chart(equity, 'drawdown.html', use_plotly=True)
```

## 📊 Visualization Functions

| Function | Purpose | Output |
|----------|---------|--------|
| `generate_equity_curve_chart()` | Capital growth over time | PNG or HTML |
| `generate_drawdown_chart()` | Peak-to-trough declines | PNG or HTML |
| `generate_pnl_distribution_chart()` | Trade P&L histogram | PNG or HTML |

**Parameters**:
- `equity_curve`: List of dicts or values
- `output_file`: Path to save (optional)
- `use_plotly`: True for HTML, False for PNG
- `title`: Chart title

## 🎯 BatchBacktester API

### Initialization
```python
BatchBacktester(initial_capital=10000.0, trade_size=100.0)
```

### Methods
| Method | Description |
|--------|-------------|
| `add_strategy(name, strategy)` | Add strategy to test |
| `run_batch(data)` | Execute batch backtest |
| `export_results(output_dir)` | Save CSV results |
| `visualize_results(output_dir, use_plotly)` | Generate charts |

### Results Structure
```python
batch.results = {
    'Strategy Name': {
        'metrics': {
            'strategy_name': str,
            'total_trades': int,
            'roi': float,
            'win_rate': float,
            'sharpe_ratio': float,
            'max_drawdown': float,
            ...
        },
        'trades': [...],
        'equity_curve': [...]
    }
}
```

## 📈 Output Files

### CSV Files
- `batch_backtest_summary.csv` - All strategies compared
- `trades_<strategy>.csv` - Individual trade history

### Visualization Files
- **PNG** (Matplotlib): `equity_<strategy>.png`, `drawdown_<strategy>.png`, `pnl_<strategy>.png`
- **HTML** (Plotly): `equity_<strategy>.html`, `drawdown_<strategy>.html`, `pnl_<strategy>.html`

## 🔧 Configuration

### Matplotlib (Static)
- Fast generation
- Small file size (50-150 KB)
- Print-ready quality
- Use: `use_plotly=False`

### Plotly (Interactive)
- Zoom, pan, hover
- Larger files (2-5 MB)
- Web-based
- Use: `use_plotly=True`

## ⚡ Performance Tips

1. **Start small**: Test with 500-1000 bars initially
2. **Use Matplotlib for batch**: Faster generation
3. **Use Plotly for analysis**: Better for detailed review
4. **Validate data first**: Ensure clean OHLCV data

## 🐛 Troubleshooting

### Matplotlib not available
```bash
pip install matplotlib>=3.7.0
```

### Plotly not available
```bash
pip install plotly>=5.18.0
```

### No charts generated
- Check output directory exists
- Verify data is not empty
- Check logs: `logs/trading_bot.log`

### Memory issues
- Use Matplotlib instead of Plotly
- Reduce dataset size
- Process strategies separately

## 📚 Documentation

| File | Content |
|------|---------|
| `BATCH_BACKTESTING_README.md` | Comprehensive guide |
| `BACKTESTING_GUIDE.md` | Full backtesting documentation |
| `FEATURE_SUMMARY.md` | Implementation details |
| `demo_batch_backtest.py` | Working examples |

## 🧪 Testing

Run comprehensive test suite:
```bash
python test_batch_backtesting.py
```

Expected output:
```
Ran 19 tests in ~6s
OK
```

## 📊 Example Output

### Comparison Table
```
Rank  Strategy                 Trades    ROI      Win Rate   Sharpe
-----------------------------------------------------------------------
🥇 #1  RSI Mean Reversion      22        +87.5%   72.7%      8.45
🥈 #2  MA Crossover (20/50)    15        +54.3%   60.0%      5.23
🥉 #3  Bollinger Bands         18        +42.1%   55.6%      4.12
```

### Metrics Available
- Total ROI (%)
- Win Rate (%)
- Total Trades
- Best/Worst Trade ($)
- Average Trade ($)
- Sharpe Ratio
- Maximum Drawdown (%)
- Final Capital ($)

## 💡 Best Practices

1. **Use identical data** for all strategies in batch test
2. **Save results** before closing to preserve analysis
3. **Start with demo** to understand output format
4. **Run tests** to verify installation
5. **Check documentation** for advanced features

## 🎯 Common Patterns

### Parameter Optimization
```python
# Test different MA windows
for short, long in [(10,30), (20,50), (50,200)]:
    batch.add_strategy(
        f'MA {short}/{long}',
        MACrossoverStrategy({'short_window': short, 'long_window': long})
    )
```

### Strategy Comparison
```python
# Compare different strategy types
strategies = [
    ('MA', MACrossoverStrategy(...)),
    ('RSI', RSIStrategy(...)),
    ('BB', BollingerBandsStrategy(...))
]
for name, strat in strategies:
    batch.add_strategy(name, strat)
```

### Export and Analyze
```python
# Run and save everything
batch.run_batch(data)
batch.export_results('results')
charts = batch.visualize_results('results', use_plotly=True)

# Load results later
import pandas as pd
summary = pd.read_csv('results/batch_backtest_summary.csv')
print(summary.sort_values('roi', ascending=False))
```

## 🔗 Quick Links

- **Main Documentation**: `BATCH_BACKTESTING_README.md`
- **Backtest Guide**: `BACKTESTING_GUIDE.md`
- **Test File**: `test_batch_backtesting.py`
- **Demo Script**: `demo_batch_backtest.py`
- **Implementation Details**: `FEATURE_SUMMARY.md`

## ✨ Key Commands

```bash
# Run batch backtester interactively
python batch_backtester.py

# Run demo (generates example outputs)
python demo_batch_backtest.py

# Run all tests
python test_batch_backtesting.py

# Run system tests
python test_system.py
```

---

**Quick Help**: For detailed information, see `BATCH_BACKTESTING_README.md`
