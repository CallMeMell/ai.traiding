"""
demo_parameter_optimization.py - Parameter Optimization Demo
============================================================
Demonstrates automated parameter optimization for trading strategies
using Grid Search, Random Search, and Genetic Algorithms.
"""

import sys
import logging
from parameter_optimizer import ParameterOptimizer, ParameterRange
from backtest_reversal import ReversalBacktester
from utils import generate_sample_data, setup_logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def demo_grid_search():
    """Demonstrate Grid Search optimization"""
    print_header("🔍 DEMO 1: Grid Search Optimization")
    
    print("\nGrid Search systematically tests all parameter combinations")
    print("in a defined grid. Best for small parameter spaces.\n")
    
    # Generate sample data
    print("Generating sample data (300 candles)...")
    data = generate_sample_data(n_bars=300, start_price=30000)
    print(f"✓ Data generated: ${data['low'].min():.2f} - ${data['high'].max():.2f}\n")
    
    # Define parameter ranges for Reversal-Trailing-Stop strategy
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
    
    print("Parameter ranges:")
    print("  Stop Loss:       1.0% - 3.0% (step: 0.5%)")
    print("  Take Profit:     2.0% - 6.0% (step: 1.0%)")
    print("  Trailing Stop:   0.5% - 1.5% (step: 0.25%)")
    print("  Direction:       LONG, SHORT")
    
    # Initialize optimizer
    optimizer = ParameterOptimizer(
        backtester_class=ReversalBacktester,
        data=data,
        parameter_ranges=parameter_ranges,
        optimization_metric='score'
    )
    
    # Run grid search
    print("\nStarting Grid Search...")
    results = optimizer.grid_search()
    
    # Generate and display report
    report = optimizer.generate_report(top_n=5, output_file="data/grid_search_report.txt")
    print("\n" + report)
    
    # Save results
    optimizer.save_results_csv("data/grid_search_results.csv")
    
    print("\n💡 INSIGHTS:")
    if optimizer.best_result:
        best = optimizer.best_result
        print(f"  Best configuration found with {best.roi:.2f}% ROI")
        print(f"  Optimal Stop Loss: {best.parameters['stop_loss_percent']:.2f}%")
        print(f"  Optimal Take Profit: {best.parameters['take_profit_percent']:.2f}%")
        print(f"  Optimal Trailing Stop: {best.parameters['trailing_stop_percent']:.2f}%")
        print(f"  Optimal Direction: {best.parameters['initial_direction']}")


def demo_random_search():
    """Demonstrate Random Search optimization"""
    print_header("🎲 DEMO 2: Random Search Optimization")
    
    print("\nRandom Search samples random parameter combinations.")
    print("More efficient than Grid Search for large parameter spaces.\n")
    
    # Generate sample data
    print("Generating sample data (300 candles)...")
    data = generate_sample_data(n_bars=300, start_price=30000)
    print(f"✓ Data generated: ${data['low'].min():.2f} - ${data['high'].max():.2f}\n")
    
    # Define parameter ranges with continuous ranges
    parameter_ranges = [
        ParameterRange(
            name='initial_capital',
            min_value=10000.0,
            max_value=10000.0,
            type='float'
        ),
        ParameterRange(
            name='stop_loss_percent',
            min_value=0.5,
            max_value=5.0,
            type='float'
        ),
        ParameterRange(
            name='take_profit_percent',
            min_value=1.0,
            max_value=10.0,
            type='float'
        ),
        ParameterRange(
            name='trailing_stop_percent',
            min_value=0.25,
            max_value=2.0,
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
    
    print("Parameter ranges (continuous):")
    print("  Stop Loss:       0.5% - 5.0%")
    print("  Take Profit:     1.0% - 10.0%")
    print("  Trailing Stop:   0.25% - 2.0%")
    print("  Direction:       LONG, SHORT")
    
    # Initialize optimizer
    optimizer = ParameterOptimizer(
        backtester_class=ReversalBacktester,
        data=data,
        parameter_ranges=parameter_ranges,
        optimization_metric='score'
    )
    
    # Run random search
    print("\nStarting Random Search (30 iterations)...")
    results = optimizer.random_search(n_iterations=30, seed=42)
    
    # Generate and display report
    report = optimizer.generate_report(top_n=5, output_file="data/random_search_report.txt")
    print("\n" + report)
    
    # Save results
    optimizer.save_results_csv("data/random_search_results.csv")
    
    print("\n💡 INSIGHTS:")
    if optimizer.best_result:
        best = optimizer.best_result
        print(f"  Random Search found {best.roi:.2f}% ROI configuration")
        print(f"  This is more efficient than exhaustive grid search")
        print(f"  Optimal parameters:")
        for param, value in best.parameters.items():
            if param != 'initial_capital':
                if isinstance(value, float):
                    print(f"    {param}: {value:.3f}")
                else:
                    print(f"    {param}: {value}")


def demo_genetic_algorithm():
    """Demonstrate Genetic Algorithm optimization"""
    print_header("🧬 DEMO 3: Genetic Algorithm Optimization")
    
    print("\nGenetic Algorithm uses evolutionary principles to find")
    print("optimal parameters through selection, crossover, and mutation.\n")
    
    # Generate sample data
    print("Generating sample data (300 candles)...")
    data = generate_sample_data(n_bars=300, start_price=30000)
    print(f"✓ Data generated: ${data['low'].min():.2f} - ${data['high'].max():.2f}\n")
    
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
            min_value=0.5,
            max_value=5.0,
            type='float'
        ),
        ParameterRange(
            name='take_profit_percent',
            min_value=1.0,
            max_value=10.0,
            type='float'
        ),
        ParameterRange(
            name='trailing_stop_percent',
            min_value=0.25,
            max_value=2.0,
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
    
    print("Parameter ranges:")
    print("  Stop Loss:       0.5% - 5.0%")
    print("  Take Profit:     1.0% - 10.0%")
    print("  Trailing Stop:   0.25% - 2.0%")
    print("  Direction:       LONG, SHORT")
    
    # Initialize optimizer
    optimizer = ParameterOptimizer(
        backtester_class=ReversalBacktester,
        data=data,
        parameter_ranges=parameter_ranges,
        optimization_metric='score'
    )
    
    # Run genetic algorithm
    print("\nStarting Genetic Algorithm...")
    print("  Population: 10, Generations: 5")
    results = optimizer.genetic_algorithm(
        population_size=10,
        n_generations=5,
        mutation_rate=0.15,
        crossover_rate=0.7,
        elite_size=2
    )
    
    # Generate and display report
    report = optimizer.generate_report(top_n=5, output_file="data/genetic_algorithm_report.txt")
    print("\n" + report)
    
    # Save results
    optimizer.save_results_csv("data/genetic_algorithm_results.csv")
    
    print("\n💡 INSIGHTS:")
    if optimizer.best_result:
        best = optimizer.best_result
        print(f"  Genetic Algorithm evolved to {best.roi:.2f}% ROI")
        print(f"  The algorithm converged to optimal parameters through evolution")
        print(f"  Final best parameters:")
        for param, value in best.parameters.items():
            if param != 'initial_capital':
                if isinstance(value, float):
                    print(f"    {param}: {value:.3f}")
                else:
                    print(f"    {param}: {value}")


def demo_comparison():
    """Compare all three optimization methods"""
    print_header("📊 DEMO 4: Method Comparison")
    
    print("\nComparing Grid Search vs Random Search vs Genetic Algorithm")
    print("on the same data and parameter ranges.\n")
    
    # Generate sample data once
    print("Generating sample data (250 candles)...")
    data = generate_sample_data(n_bars=250, start_price=30000)
    print(f"✓ Data generated: ${data['low'].min():.2f} - ${data['high'].max():.2f}\n")
    
    # Define parameter ranges (smaller for faster demo)
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
            step=1.0,
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
            values=['LONG'],
            min_value=0,
            max_value=0
        )
    ]
    
    methods = []
    
    # Grid Search
    print("\n1. Running Grid Search...")
    opt_grid = ParameterOptimizer(
        backtester_class=ReversalBacktester,
        data=data,
        parameter_ranges=parameter_ranges,
        optimization_metric='score'
    )
    opt_grid.grid_search()
    methods.append(("Grid Search", opt_grid))
    
    # Random Search
    print("\n2. Running Random Search...")
    opt_random = ParameterOptimizer(
        backtester_class=ReversalBacktester,
        data=data,
        parameter_ranges=parameter_ranges,
        optimization_metric='score'
    )
    opt_random.random_search(n_iterations=15, seed=42)
    methods.append(("Random Search", opt_random))
    
    # Genetic Algorithm
    print("\n3. Running Genetic Algorithm...")
    opt_genetic = ParameterOptimizer(
        backtester_class=ReversalBacktester,
        data=data,
        parameter_ranges=parameter_ranges,
        optimization_metric='score'
    )
    opt_genetic.genetic_algorithm(
        population_size=8,
        n_generations=3,
        mutation_rate=0.2
    )
    methods.append(("Genetic Algorithm", opt_genetic))
    
    # Compare results
    print("\n" + "=" * 70)
    print("📊 COMPARISON RESULTS")
    print("=" * 70)
    
    print(f"\n{'Method':<20} {'Tests':<10} {'Best ROI':<12} {'Best Sharpe':<12} {'Score':<10}")
    print("-" * 70)
    
    for method_name, optimizer in methods:
        best = optimizer.best_result
        if best:
            print(f"{method_name:<20} {len(optimizer.results):<10} "
                  f"{best.roi:<12.2f} {best.sharpe_ratio:<12.3f} {best.score:<10.4f}")
    
    print("\n💡 INSIGHTS:")
    print("  • Grid Search: Exhaustive but can be slow for large spaces")
    print("  • Random Search: Fast and often finds good solutions")
    print("  • Genetic Algorithm: Evolves toward optimal, great for complex spaces")
    print("  • Choice depends on: parameter space size, time budget, and complexity")


def interactive_demo():
    """Interactive demo menu"""
    print("\n" + "=" * 70)
    print("  🚀 PARAMETER OPTIMIZATION DEMO")
    print("=" * 70)
    print("\nThis demo showcases automated parameter optimization for")
    print("trading strategies using various search algorithms.")
    
    demos = [
        ("Grid Search Optimization", demo_grid_search),
        ("Random Search Optimization", demo_random_search),
        ("Genetic Algorithm Optimization", demo_genetic_algorithm),
        ("Compare All Methods", demo_comparison),
    ]
    
    while True:
        print("\n📋 Choose a demo:")
        print("  [0] Run all demos")
        for i, (name, _) in enumerate(demos, 1):
            print(f"  [{i}] {name}")
        print("  [q] Exit")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'q':
            print("\n👋 Demo finished. Happy optimizing!")
            break
        
        elif choice == '0':
            print("\n🚀 Running all demos sequentially...\n")
            for name, demo_func in demos:
                demo_func()
                input("\nPress Enter to continue to next demo...")
            print("\n✓ All demos completed!")
        
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            demos[int(choice) - 1][1]()
        
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        interactive_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
