# 🔬 Parameter Optimization Module - Quick Reference

## Overview

The Parameter Optimization module automatically finds the best parameters for your trading strategies using three powerful algorithms:

- **Grid Search** - Exhaustive testing of all combinations
- **Random Search** - Efficient random sampling
- **Genetic Algorithm** - Evolutionary optimization

## Quick Start (60 seconds)

### 1. Run the Example

```bash
python optimize_strategy_example.py
```

This will:
- Test 20 different parameter combinations
- Show the best parameters found
- Generate a report and save results
- Complete in about 10-15 seconds

### 2. Try the Interactive Demo

```bash
python demo_parameter_optimization.py
```

Choose from:
1. Grid Search optimization
2. Random Search optimization
3. Genetic Algorithm optimization
4. Compare all methods

## When to Use Each Algorithm

| Algorithm | Use When | Speed | Quality |
|-----------|----------|-------|---------|
| **Grid Search** | 2-4 parameters, need certainty | Slow | Exact |
| **Random Search** | 4+ parameters, need speed | Fast | Good |
| **Genetic Algorithm** | Complex spaces, have time | Medium | Excellent |

## Basic Usage

```python
from parameter_optimizer import ParameterOptimizer, ParameterRange
from backtest_reversal import ReversalBacktester
from utils import generate_sample_data

# Step 1: Get data
data = generate_sample_data(n_bars=300)

# Step 2: Define parameters to optimize
parameters = [
    ParameterRange(
        name='stop_loss_percent',
        min_value=1.0,
        max_value=3.0,
        step=0.5,
        type='float'
    ),
    ParameterRange(
        name='take_profit_percent',
        min_value=2.0,
        max_value=6.0,
        step=1.0,
        type='float'
    ),
]

# Step 3: Initialize optimizer
optimizer = ParameterOptimizer(
    backtester_class=ReversalBacktester,
    data=data,
    parameter_ranges=parameters
)

# Step 4: Run optimization
results = optimizer.random_search(n_iterations=30)

# Step 5: Get results
best = optimizer.get_best_parameters()
print(f"Best parameters: {best}")

# Step 6: Generate report
optimizer.generate_report(top_n=10, output_file="report.txt")
```

## What Gets Optimized?

The optimizer finds parameters that maximize:

- **ROI** - Total return percentage
- **Sharpe Ratio** - Risk-adjusted returns
- **Win Rate** - Percentage of winning trades
- **Profit Factor** - Profit/Loss ratio
- **Calmar Ratio** - Return/Drawdown ratio
- **Combined Score** - Weighted combination

## Output Files

After optimization, you get:

1. **CSV Results** - All tested combinations with metrics
2. **Text Report** - Best parameters and performance summary
3. **Best Parameters** - Ready to use in your strategy

## Performance Metrics Explained

```
ROI:              15.50%     ← Total return
Sharpe Ratio:     1.850      ← Risk-adjusted (>1 is good, >2 excellent)
Win Rate:         62.22%     ← % of winning trades
Total Trades:     45         ← Number of trades executed
Profit Factor:    2.15       ← Gross profit / Gross loss (>1 profitable)
Max Drawdown:     -8.30%     ← Worst decline from peak
Calmar Ratio:     1.867      ← ROI / Max Drawdown (higher better)
```

## Common Use Cases

### 1. Finding Best Stop Loss and Take Profit

```python
parameters = [
    ParameterRange(name='stop_loss_percent', min_value=0.5, max_value=5.0),
    ParameterRange(name='take_profit_percent', min_value=1.0, max_value=10.0),
]
```

### 2. Optimizing Multiple Parameters

```python
parameters = [
    ParameterRange(name='stop_loss_percent', min_value=1.0, max_value=3.0),
    ParameterRange(name='take_profit_percent', min_value=2.0, max_value=6.0),
    ParameterRange(name='trailing_stop_percent', min_value=0.5, max_value=1.5),
    ParameterRange(name='initial_direction', type='categorical', 
                   values=['LONG', 'SHORT'], min_value=0, max_value=1),
]
```

### 3. Different Optimization Goals

```python
# Optimize for maximum ROI
optimizer = ParameterOptimizer(..., optimization_metric='roi')

# Optimize for best Sharpe Ratio
optimizer = ParameterOptimizer(..., optimization_metric='sharpe_ratio')

# Optimize for highest Win Rate
optimizer = ParameterOptimizer(..., optimization_metric='win_rate')
```

## Tips for Best Results

### ✅ DO:
- Start with small data samples for testing
- Use reasonable parameter ranges (not too wide)
- Run walk-forward analysis to avoid overfitting
- Save all results for later analysis
- Test optimal parameters on different time periods

### ❌ DON'T:
- Over-optimize on limited data
- Use parameters that are at range boundaries
- Trust results from too few trades (<30)
- Forget to test on out-of-sample data
- Make ranges too wide (slow and unreliable)

## Avoiding Overfitting

```python
# Split data: 70% train, 30% test
train_data = data.iloc[:int(len(data) * 0.7)]
test_data = data.iloc[int(len(data) * 0.7):]

# Optimize on training data
optimizer = ParameterOptimizer(..., data=train_data)
results = optimizer.random_search(n_iterations=50)
best_params = optimizer.get_best_parameters()

# Validate on test data
backtester = ReversalBacktester(**best_params)
backtester.run(test_data)
```

## Files and Documentation

- **`parameter_optimizer.py`** - Core optimization engine
- **`optimize_strategy_example.py`** - Simple example script
- **`demo_parameter_optimization.py`** - Interactive demo with all methods
- **`test_parameter_optimization.py`** - 16 unit tests (all passing)
- **`PARAMETER_OPTIMIZATION_GUIDE.md`** - Complete detailed guide
- **`FAQ.md`** - Updated with optimization tips
- **`START_HERE.md`** - Updated with optimization workflow

## Troubleshooting

### Problem: Takes too long

**Solution:** 
- Use Random Search instead of Grid Search
- Reduce parameter ranges
- Use smaller data sample
- Reduce iterations

### Problem: No good parameters found

**Solution:**
- Expand parameter ranges
- Try different optimization metric
- Use more iterations
- Check if strategy fits the data

### Problem: Results differ each time

**Solution:**
- Set random seed: `optimizer.random_search(seed=42)`
- Save results immediately
- Use Grid Search for reproducibility

## Need More Help?

1. **Quick Start:** Run `python optimize_strategy_example.py`
2. **Interactive Demo:** Run `python demo_parameter_optimization.py`
3. **Full Guide:** Read `PARAMETER_OPTIMIZATION_GUIDE.md`
4. **Tests:** Check `test_parameter_optimization.py` for examples
5. **FAQ:** See updated `FAQ.md` for common questions

## Algorithm Comparison Example

```python
# Compare all three methods on same data
data = generate_sample_data(n_bars=250)

# Grid Search
opt1 = ParameterOptimizer(..., data=data)
opt1.grid_search()

# Random Search  
opt2 = ParameterOptimizer(..., data=data)
opt2.random_search(n_iterations=30)

# Genetic Algorithm
opt3 = ParameterOptimizer(..., data=data)
opt3.genetic_algorithm(population_size=15, n_generations=5)

# Compare
print(f"Grid Search best: {opt1.best_result.roi:.2f}%")
print(f"Random Search best: {opt2.best_result.roi:.2f}%")
print(f"Genetic Algorithm best: {opt3.best_result.roi:.2f}%")
```

## Performance

- **Grid Search:** Tests 27 combinations in ~3 seconds
- **Random Search:** Tests 30 combinations in ~3 seconds
- **Genetic Algorithm:** Tests 50 combinations in ~5 seconds

*(Timing with 300 candles, Intel i5 processor)*

## Integration with Existing Code

The optimizer works seamlessly with:
- ✅ `backtest_reversal.py` - Reversal-Trailing-Stop Strategy
- ✅ `backtester.py` - Main backtester
- ✅ All existing performance metrics
- ✅ Existing data loading and validation

No changes needed to your existing strategies!

## Summary

| Feature | Status |
|---------|--------|
| Grid Search | ✅ Working |
| Random Search | ✅ Working |
| Genetic Algorithm | ✅ Working |
| Report Generation | ✅ Working |
| CSV Export | ✅ Working |
| Tests | ✅ 16/16 Passing |
| Documentation | ✅ Complete |
| Examples | ✅ 2 Scripts |
| Integration | ✅ Seamless |

---

**Ready to optimize your trading strategy? Start with:**

```bash
python optimize_strategy_example.py
```

**Happy Trading! 🚀📈**
