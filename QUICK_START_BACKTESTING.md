# Quick Start: Backtesting Environment

## 🚀 Get Started in 3 Minutes

### Option 1: Interactive Demo (Recommended for First-Time Users)

```bash
python demo_reversal_strategy.py
```

Then select:
- **[1]** for basic strategy example
- **[2]** for complete backtest with all metrics
- **[3]** for parameter comparison

### Option 2: Quick Backtest Script

```python
# Save as quick_backtest.py
from backtest_reversal import ReversalBacktester
from utils import generate_sample_data

# Create backtester
backtester = ReversalBacktester(
    initial_capital=10000.0,
    stop_loss_percent=2.0,
    take_profit_percent=4.0,
    trailing_stop_percent=1.0,
    initial_direction='LONG'
)

# Generate test data
data = generate_sample_data(n_bars=1000, start_price=30000)

# Run backtest
backtester.run(data)

# Save results
backtester.save_results()
```

Run it:
```bash
python quick_backtest.py
```

### Option 3: Command-Line Backtest

```bash
# Interactive mode
python backtest_reversal.py

# Then follow prompts:
# 1. Choose data source (1 for CSV, 2 for simulated)
# 2. Enter parameters (or press Enter for defaults)
# 3. Review results
# 4. Save if desired
```

## 📊 Understanding Your Results

After running a backtest, you'll see:

```
💰 CAPITAL:
  Initial Capital:  $10,000.00
  Final Capital:    $11,145.10
  ROI:              11.45%        ← Your profit percentage

📈 TRADES:
  Total Trades:     77
  Win Rate:         46.75%        ← Percentage of winning trades

📊 ADVANCED METRICS:
  Sharpe Ratio:     0.529         ← Risk-adjusted return (higher is better)
  Max Drawdown:     -6.34%        ← Worst loss from peak (lower is better)
```

### Quick Interpretation Guide

✅ **Good Results**:
- ROI > 5%
- Sharpe Ratio > 1.0
- Max Drawdown < 10%
- Win Rate > 45%

⚠️ **Warning Signs**:
- ROI < 0% (losing money)
- Sharpe Ratio < 0 (negative risk-adjusted return)
- Max Drawdown > 20% (high risk)
- Win Rate < 40% (too many losses)

## 🔧 Quick Parameter Tuning

Want to try different settings? Adjust these:

```python
# Conservative (Lower risk, lower return)
backtester = ReversalBacktester(
    stop_loss_percent=1.0,      # Tighter stop
    take_profit_percent=2.0,    # Smaller target
    trailing_stop_percent=0.5   # Closer trailing
)

# Moderate (Balanced)
backtester = ReversalBacktester(
    stop_loss_percent=2.0,
    take_profit_percent=4.0,
    trailing_stop_percent=1.0
)

# Aggressive (Higher risk, higher return potential)
backtester = ReversalBacktester(
    stop_loss_percent=3.0,      # Wider stop
    take_profit_percent=6.0,    # Bigger target
    trailing_stop_percent=1.5   # More room to breathe
)
```

## 📁 Using Your Own Data

Your CSV file should have these columns:

```csv
timestamp,open,high,low,close,volume
2024-01-01 00:00:00,30000,30100,29900,30050,1000000
2024-01-01 00:15:00,30050,30150,29950,30100,1100000
...
```

Then load it:

```python
data = backtester.load_data("path/to/your/data.csv")
backtester.run(data)
```

## 🧪 Running Tests

Verify everything works:

```bash
# Test system
python test_system.py

# Test strategy
python test_strategy_core.py

# Test metrics
python test_performance_metrics.py
```

All tests should show: ✅ OK

## 📚 Learn More

- **Detailed Guide**: See `BACKTESTING_GUIDE.md`
- **Results Analysis**: See `REVERSAL_STRATEGY_RESULTS.md`
- **Strategy Details**: See `STRATEGY_CORE_README.md`

## ❓ Common Questions

**Q: How long does a backtest take?**  
A: 1-2 seconds for 1000 candles

**Q: Can I backtest with real data?**  
A: Yes! Just load a CSV file with OHLCV data

**Q: What's a good ROI?**  
A: 5-15% is good for short-term strategies

**Q: What if my results are negative?**  
A: Try different parameters or test with different data

**Q: How do I know which parameters to use?**  
A: Run the demo's parameter comparison (option 3)

## 🆘 Troubleshooting

**Issue**: `ModuleNotFoundError`  
**Fix**: `pip install pandas numpy python-dotenv`

**Issue**: `FileNotFoundError`  
**Fix**: Check your CSV path is correct

**Issue**: `Invalid data` error  
**Fix**: Ensure CSV has required columns (open, high, low, close, volume)

**Issue**: Results don't make sense  
**Fix**: Check data quality and parameter values

## 🎯 Next Steps

1. ✅ Run the demo to see examples
2. ✅ Try a backtest with simulated data
3. ✅ Experiment with different parameters
4. ✅ Test with your own historical data
5. ✅ Review the detailed documentation
6. ✅ Ready for live testing? Use testnet first!

---

**Need Help?** Check the logs at `logs/backtest_reversal.log`

**Happy Backtesting! 📈**
