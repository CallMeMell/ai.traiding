# 🔬 Parameter Optimization Guide

## Overview

The Parameter Optimization module provides automated tools to find optimal parameters for your trading strategies. Instead of manually testing different parameter combinations, you can use systematic algorithms to explore the parameter space efficiently.

## Features

- **Multiple Optimization Algorithms:**
  - Grid Search: Exhaustive search over defined parameter grid
  - Random Search: Random sampling from parameter space
  - Genetic Algorithm: Evolutionary optimization using selection, crossover, and mutation

- **Comprehensive Performance Metrics:**
  - ROI (Return on Investment)
  - Sharpe Ratio (Risk-adjusted returns)
  - Maximum Drawdown
  - Win Rate
  - Profit Factor
  - Calmar Ratio

- **Automated Reporting:**
  - Best parameter combinations
  - Performance comparisons
  - CSV export of all results
  - Detailed text reports

## Quick Start

### 1. Basic Example - Grid Search

```python
from parameter_optimizer import ParameterOptimizer, ParameterRange
from backtest_reversal import ReversalBacktester
from utils import generate_sample_data

# Load or generate data
data = generate_sample_data(n_bars=500, start_price=30000)

# Define parameter ranges
parameter_ranges = [
    ParameterRange(
        name='initial_capital',
        min_value=10000.0,
        max_value=10000.0,
        type='float'
    ),
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
    ParameterRange(
        name='trailing_stop_percent',
        min_value=0.5,
        max_value=1.5,
        step=0.25,
        type='float'
    ),
    ParameterRange(
        name='initial_direction',
        type='categorical',
        values=['LONG', 'SHORT'],
        min_value=0,
        max_value=1
    )
]

# Initialize optimizer
optimizer = ParameterOptimizer(
    backtester_class=ReversalBacktester,
    data=data,
    parameter_ranges=parameter_ranges,
    optimization_metric='score'
)

# Run optimization
results = optimizer.grid_search()

# Get best parameters
best_params = optimizer.get_best_parameters()
print(f"Best parameters: {best_params}")

# Generate report
report = optimizer.generate_report(top_n=10)
print(report)

# Save results
optimizer.save_results_csv("optimization_results.csv")
```

### 2. Random Search Example

```python
# Use same setup as above, but run random search
optimizer = ParameterOptimizer(
    backtester_class=ReversalBacktester,
    data=data,
    parameter_ranges=parameter_ranges,
    optimization_metric='sharpe_ratio'  # Optimize for Sharpe Ratio
)

# Run random search with 50 iterations
results = optimizer.random_search(n_iterations=50, seed=42)

# Get best parameters
best_params = optimizer.get_best_parameters()
```

### 3. Genetic Algorithm Example

```python
# Run genetic algorithm optimization
optimizer = ParameterOptimizer(
    backtester_class=ReversalBacktester,
    data=data,
    parameter_ranges=parameter_ranges,
    optimization_metric='score'
)

results = optimizer.genetic_algorithm(
    population_size=20,
    n_generations=10,
    mutation_rate=0.1,
    crossover_rate=0.7,
    elite_size=2
)
```

## Parameter Range Types

### Float Parameters

For continuous numerical parameters (e.g., percentages):

```python
ParameterRange(
    name='stop_loss_percent',
    min_value=0.5,
    max_value=5.0,
    step=0.25,  # Optional: for grid search
    type='float'
)
```

### Integer Parameters

For discrete numerical parameters:

```python
ParameterRange(
    name='lookback_period',
    min_value=10,
    max_value=100,
    step=10,  # Optional: for grid search
    type='int'
)
```

### Categorical Parameters

For non-numerical options:

```python
ParameterRange(
    name='initial_direction',
    type='categorical',
    values=['LONG', 'SHORT', 'NEUTRAL'],
    min_value=0,  # Required but not used
    max_value=2   # Required but not used
)
```

## Optimization Metrics

You can optimize for different metrics:

- **`score`** (default): Combined score using weighted metrics
- **`roi`**: Return on Investment
- **`sharpe_ratio`**: Risk-adjusted returns
- **`win_rate`**: Percentage of winning trades
- **`profit_factor`**: Ratio of wins to losses
- **`calmar_ratio`**: ROI / Maximum Drawdown
- **`max_drawdown`**: Maximum peak-to-trough decline (lower is better)

### Custom Scoring Weights

Customize how the combined score is calculated:

```python
optimizer = ParameterOptimizer(
    backtester_class=ReversalBacktester,
    data=data,
    parameter_ranges=parameter_ranges,
    optimization_metric='score',
    scoring_weights={
        'roi': 0.4,           # 40% weight on ROI
        'sharpe_ratio': 0.3,  # 30% weight on Sharpe
        'win_rate': 0.1,      # 10% weight on win rate
        'profit_factor': 0.1, # 10% weight on profit factor
        'calmar_ratio': 0.1   # 10% weight on Calmar
    }
)
```

## Algorithm Comparison

### Grid Search

**Pros:**
- Exhaustive: Tests all combinations
- Reproducible results
- Good for small parameter spaces

**Cons:**
- Computationally expensive for large spaces
- Exponential growth with number of parameters

**Best for:**
- 2-4 parameters
- When you need certainty you found the global optimum
- Small to medium parameter ranges

### Random Search

**Pros:**
- Faster than grid search for large spaces
- Can find good solutions quickly
- Scalable to many parameters

**Cons:**
- No guarantee of finding global optimum
- May need many iterations

**Best for:**
- 4+ parameters
- Large parameter ranges
- When speed is important

### Genetic Algorithm

**Pros:**
- Inspired by natural selection
- Good at exploring complex spaces
- Can escape local optima

**Cons:**
- More complex to tune
- Slower convergence
- Requires more iterations

**Best for:**
- Complex, high-dimensional spaces
- Non-linear relationships
- When other methods struggle

## Performance Tips

### 1. Start Small
Begin with a subset of data and fewer iterations to validate your setup:

```python
# Use small data for initial testing
test_data = data.iloc[:200]  # First 200 candles

# Use fewer iterations
results = optimizer.random_search(n_iterations=10)
```

### 2. Use Walk-Forward Analysis
Prevent overfitting by testing on out-of-sample data:

```python
# Split data
train_data = data.iloc[:int(len(data) * 0.7)]
test_data = data.iloc[int(len(data) * 0.7):]

# Optimize on training data
optimizer_train = ParameterOptimizer(
    backtester_class=ReversalBacktester,
    data=train_data,
    parameter_ranges=parameter_ranges
)
results = optimizer_train.grid_search()
best_params = optimizer_train.get_best_parameters()

# Validate on test data
backtester = ReversalBacktester(**best_params)
backtester.run(test_data)
```

### 3. Parallelize (Future Enhancement)
For grid search and random search, backtests can be run in parallel to speed up optimization.

### 4. Cache Results
Save optimization results to avoid re-running:

```python
optimizer.save_results_csv("optimization_results.csv")

# Later, you can load and analyze without re-optimizing
import pandas as pd
results_df = pd.read_csv("optimization_results.csv")
best_row = results_df.nlargest(1, 'score')
```

## Demo Script

Run the interactive demo to see all features:

```bash
python demo_parameter_optimization.py
```

The demo includes:
1. Grid Search optimization
2. Random Search optimization
3. Genetic Algorithm optimization
4. Comparison of all methods

## Interpreting Results

### Understanding the Report

```
📊 PARAMETER OPTIMIZATION REPORT
================================================================================
Generated: 2024-10-09 12:00:00
Total combinations tested: 135
Optimization metric: score
================================================================================

🏆 BEST PARAMETERS FOUND:
--------------------------------------------------------------------------------
  initial_capital................ 10000.0000
  stop_loss_percent.............. 1.5000
  take_profit_percent............ 4.0000
  trailing_stop_percent.......... 0.7500
  initial_direction.............. LONG

📈 BEST PERFORMANCE METRICS:
--------------------------------------------------------------------------------
  Combined Score:........... 0.5234
  ROI:...................... 15.50%
  Sharpe Ratio:............. 1.850
  Maximum Drawdown:......... -8.30%
  Total Trades:............. 45
  Win Rate:................. 62.22%
  Profit Factor:............ 2.15
  Calmar Ratio:............. 1.867
```

### Key Metrics Interpretation

- **Combined Score**: Higher is better (0-1 range typically)
- **ROI**: Total return percentage
- **Sharpe Ratio**: Risk-adjusted return (>1 is good, >2 is excellent)
- **Max Drawdown**: Worst decline from peak (smaller absolute value is better)
- **Win Rate**: Percentage of profitable trades (>50% is positive)
- **Profit Factor**: Ratio of gross profit to gross loss (>1 is profitable, >2 is good)
- **Calmar Ratio**: ROI divided by Max Drawdown (higher is better)

## Best Practices

### 1. Define Reasonable Parameter Ranges
Don't make ranges too wide:

```python
# Too wide - will take forever
ParameterRange(name='stop_loss_percent', min_value=0.1, max_value=50.0)

# Better - reasonable trading range
ParameterRange(name='stop_loss_percent', min_value=0.5, max_value=5.0)
```

### 2. Consider Market Conditions
Optimize separately for different market regimes:
- Trending markets
- Ranging markets
- High volatility periods
- Low volatility periods

### 3. Avoid Overfitting
- Use walk-forward analysis
- Test on out-of-sample data
- Don't optimize on too little data
- Consider parameter stability over time

### 4. Document Your Results
Always save optimization results and parameters:

```python
# Save results
optimizer.save_results_csv(f"optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

# Save report
report = optimizer.generate_report(
    top_n=20,
    output_file=f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
)
```

## Advanced Usage

### Multi-Objective Optimization

You can run multiple optimizations with different metrics and compare:

```python
# Optimize for ROI
opt_roi = ParameterOptimizer(..., optimization_metric='roi')
opt_roi.random_search(n_iterations=50)

# Optimize for Sharpe Ratio
opt_sharpe = ParameterOptimizer(..., optimization_metric='sharpe_ratio')
opt_sharpe.random_search(n_iterations=50)

# Compare results
print(f"Best ROI params: {opt_roi.get_best_parameters()}")
print(f"Best Sharpe params: {opt_sharpe.get_best_parameters()}")
```

### Parameter Sensitivity Analysis

Analyze how sensitive performance is to each parameter:

```python
# Run optimization
optimizer.grid_search()

# Save results
optimizer.save_results_csv("sensitivity_results.csv")

# Analyze with pandas
import pandas as pd
df = pd.read_csv("sensitivity_results.csv")

# See correlation between parameters and score
correlations = df.corr()['score'].sort_values(ascending=False)
print(correlations)
```

## Troubleshooting

### Problem: Optimization takes too long

**Solutions:**
1. Reduce parameter space (fewer parameters or smaller ranges)
2. Use Random Search instead of Grid Search
3. Reduce data size for initial testing
4. Use fewer iterations/generations

### Problem: No good parameters found

**Solutions:**
1. Expand parameter ranges
2. Try different optimization metrics
3. Check if strategy is suitable for the data
4. Use more iterations (especially for Random Search and Genetic Algorithm)

### Problem: Results not reproducible

**Solutions:**
1. Set random seed: `optimizer.random_search(seed=42)`
2. Save all results immediately
3. Document data source and date range

## FAQ

### Q: How many iterations should I use for Random Search?
**A:** Start with 30-50 iterations. Increase if results are still improving significantly. Diminishing returns typically occur after 100-200 iterations.

### Q: Which algorithm should I use?
**A:** 
- Start with Random Search (fastest, good results)
- Use Grid Search if you have 2-3 parameters and want exhaustive search
- Try Genetic Algorithm for complex, multi-dimensional spaces

### Q: How do I prevent overfitting?
**A:**
1. Use walk-forward analysis (train/test split)
2. Test on out-of-sample data
3. Don't over-optimize (stop when improvements are marginal)
4. Validate parameters on different time periods

### Q: Can I optimize multiple strategies at once?
**A:** Currently, the optimizer works with one strategy at a time. To optimize multiple strategies, run separate optimizations for each.

### Q: How do I choose parameter ranges?
**A:** Start with ranges used in literature or common practice. Gradually expand if optimal values are at boundaries.

## Further Resources

- See `demo_parameter_optimization.py` for working examples
- Check `test_parameter_optimization.py` for implementation details
- Review `PERFORMANCE_METRICS_GUIDE.md` for metric explanations
- See `FAQ.md` for additional strategy optimization tips

## Contributing

To add new optimization algorithms or features:
1. Extend the `ParameterOptimizer` class
2. Add tests in `test_parameter_optimization.py`
3. Update this guide with usage examples

---

**Happy Optimizing! 🚀**
