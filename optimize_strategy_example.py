"""
optimize_strategy_example.py - Simple Parameter Optimization Example
====================================================================
Quick example showing how to optimize trading strategy parameters.
"""

from parameter_optimizer import ParameterOptimizer, ParameterRange
from backtest_reversal import ReversalBacktester
from utils import generate_sample_data
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    print("=" * 70)
    print("🔬 STRATEGY PARAMETER OPTIMIZATION - QUICK EXAMPLE")
    print("=" * 70)
    print()
    
    # Step 1: Generate or load data
    print("Step 1: Loading data...")
    data = generate_sample_data(n_bars=300, start_price=30000)
    print(f"✓ Loaded {len(data)} candles")
    print(f"  Price range: ${data['low'].min():.2f} - ${data['high'].max():.2f}")
    print()
    
    # Step 2: Define parameter ranges
    print("Step 2: Defining parameter ranges...")
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
            step=2.0,
            type='float'
        ),
        ParameterRange(
            name='trailing_stop_percent',
            min_value=0.5,
            max_value=1.5,
            step=0.5,
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
    print("✓ Parameters to optimize:")
    print("  - Stop Loss: 1.0% - 3.0%")
    print("  - Take Profit: 2.0% - 6.0%")
    print("  - Trailing Stop: 0.5% - 1.5%")
    print("  - Direction: LONG, SHORT")
    print()
    
    # Step 3: Initialize optimizer
    print("Step 3: Initializing optimizer...")
    optimizer = ParameterOptimizer(
        backtester_class=ReversalBacktester,
        data=data,
        parameter_ranges=parameter_ranges,
        optimization_metric='score'  # Optimize combined score
    )
    print("✓ Optimizer ready")
    print()
    
    # Step 4: Run optimization
    print("Step 4: Running Random Search optimization...")
    print("  (This will test 20 random parameter combinations)")
    print()
    
    results = optimizer.random_search(n_iterations=20, seed=42)
    
    print()
    print("✓ Optimization complete!")
    print()
    
    # Step 5: Display results
    print("=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    
    best = optimizer.best_result
    if best:
        print()
        print("🏆 BEST PARAMETERS FOUND:")
        print("-" * 70)
        print(f"  Stop Loss:        {best.parameters['stop_loss_percent']:.2f}%")
        print(f"  Take Profit:      {best.parameters['take_profit_percent']:.2f}%")
        print(f"  Trailing Stop:    {best.parameters['trailing_stop_percent']:.2f}%")
        print(f"  Direction:        {best.parameters['initial_direction']}")
        print()
        print("📈 PERFORMANCE METRICS:")
        print("-" * 70)
        print(f"  ROI:              {best.roi:.2f}%")
        print(f"  Sharpe Ratio:     {best.sharpe_ratio:.3f}")
        print(f"  Win Rate:         {best.win_rate:.2f}%")
        print(f"  Total Trades:     {best.total_trades}")
        print(f"  Profit Factor:    {best.profit_factor:.2f}")
        print(f"  Max Drawdown:     {best.max_drawdown:.2f}%")
        print()
        
        # Interpretation
        print("💡 INTERPRETATION:")
        print("-" * 70)
        if best.roi > 0:
            print(f"  ✅ Strategy was profitable with {best.roi:.2f}% return")
        else:
            print(f"  ❌ Strategy lost {abs(best.roi):.2f}%")
        
        if best.sharpe_ratio > 1.5:
            print(f"  ✅ Excellent risk-adjusted returns (Sharpe: {best.sharpe_ratio:.2f})")
        elif best.sharpe_ratio > 1.0:
            print(f"  ✅ Good risk-adjusted returns (Sharpe: {best.sharpe_ratio:.2f})")
        elif best.sharpe_ratio > 0:
            print(f"  ⚠️  Positive but modest risk-adjusted returns")
        else:
            print(f"  ❌ Poor risk-adjusted returns")
        
        if best.win_rate > 60:
            print(f"  ✅ High win rate: {best.win_rate:.1f}%")
        elif best.win_rate > 50:
            print(f"  ✓  Positive win rate: {best.win_rate:.1f}%")
        print()
    
    # Step 6: Save results
    print("Step 6: Saving results...")
    optimizer.save_results_csv("data/optimization_example_results.csv")
    report = optimizer.generate_report(
        top_n=5,
        output_file="data/optimization_example_report.txt"
    )
    print("✓ Results saved:")
    print("  - data/optimization_example_results.csv")
    print("  - data/optimization_example_report.txt")
    print()
    
    # Next steps
    print("=" * 70)
    print("🚀 NEXT STEPS")
    print("=" * 70)
    print()
    print("1. Review the full report: data/optimization_example_report.txt")
    print("2. Test best parameters on different data")
    print("3. Try Grid Search for exhaustive testing:")
    print("   results = optimizer.grid_search()")
    print("4. Try Genetic Algorithm for advanced optimization:")
    print("   results = optimizer.genetic_algorithm(population_size=20, n_generations=10)")
    print()
    print("For more details, see: PARAMETER_OPTIMIZATION_GUIDE.md")
    print()
    print("=" * 70)
    print("✓ Example complete!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Optimization interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
