"""
demo_batch_backtest.py - Interactive Demo for Batch Backtesting
================================================================
Demonstrates the batch backtesting and visualization features
"""
import os
import sys

def print_header():
    """Print demo header"""
    print("\n" + "=" * 70)
    print("🚀 BATCH BACKTESTING & VISUALIZATION DEMO")
    print("=" * 70)
    print("\nThis demo showcases the new features:")
    print("  ✓ Batch testing multiple strategies")
    print("  ✓ Performance comparison and ranking")
    print("  ✓ Automatic visualization generation")
    print("  ✓ Interactive and static chart formats")
    print("=" * 70 + "\n")


def demo_basic_visualization():
    """Demo basic visualization functions"""
    print("\n📊 DEMO 1: Basic Visualization Functions")
    print("-" * 70)
    
    from utils import (
        generate_equity_curve_chart,
        generate_drawdown_chart,
        generate_pnl_distribution_chart
    )
    
    # Create sample data
    equity_curve = [
        {'timestamp': i, 'capital': 10000 + i * 100 - (i % 20) * 200}
        for i in range(100)
    ]
    
    trades = [
        {'pnl': 150.0 if i % 3 != 0 else -75.0}
        for i in range(30)
    ]
    
    output_dir = 'data/demo_charts'
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n1. Generating equity curve (PNG)...")
    result = generate_equity_curve_chart(
        equity_curve,
        f'{output_dir}/demo_equity.png',
        use_plotly=False,
        title='Demo - Equity Curve'
    )
    print(f"   ✓ Saved to: {result}")
    
    print("\n2. Generating drawdown chart (PNG)...")
    result = generate_drawdown_chart(
        equity_curve,
        f'{output_dir}/demo_drawdown.png',
        use_plotly=False,
        title='Demo - Drawdown'
    )
    print(f"   ✓ Saved to: {result}")
    
    print("\n3. Generating P&L distribution (HTML - Interactive)...")
    result = generate_pnl_distribution_chart(
        trades,
        f'{output_dir}/demo_pnl.html',
        use_plotly=True,
        title='Demo - P&L Distribution'
    )
    print(f"   ✓ Saved to: {result}")
    print(f"   ℹ️  Open {result} in a browser to see interactive chart")
    
    print("\n✓ Demo 1 completed!")


def demo_backtester_visualization():
    """Demo backtester with visualization"""
    print("\n📈 DEMO 2: Backtester with Visualization")
    print("-" * 70)
    
    from backtester import Backtester
    from utils import generate_sample_data
    
    print("\n1. Creating backtester and generating data...")
    backtester = Backtester(initial_capital=10000.0)
    data = generate_sample_data(n_bars=300, start_price=30000)
    print(f"   ✓ Generated {len(data)} bars of data")
    
    print("\n2. Running backtest...")
    backtester.run(data)
    
    print("\n3. Generating visualizations...")
    output_dir = 'data/demo_backtest'
    os.makedirs(output_dir, exist_ok=True)
    
    charts = backtester.visualize_results(
        output_dir=output_dir,
        use_plotly=False
    )
    
    print(f"\n   ✓ Generated {len(charts)} charts:")
    for chart_type, path in charts.items():
        size = os.path.getsize(path) / 1024  # KB
        print(f"     - {chart_type}: {path} ({size:.1f} KB)")
    
    print("\n✓ Demo 2 completed!")


def demo_batch_backtesting():
    """Demo batch backtesting"""
    print("\n🔄 DEMO 3: Batch Backtesting Multiple Strategies")
    print("-" * 70)
    
    from batch_backtester import BatchBacktester
    from utils import generate_sample_data
    from strategy import (
        MACrossoverStrategy,
        RSIStrategy,
        EMACrossoverStrategy
    )
    
    print("\n1. Creating batch backtester...")
    batch_tester = BatchBacktester(initial_capital=10000.0, trade_size=100.0)
    
    print("\n2. Adding strategies...")
    strategies = [
        ('MA Crossover (20/50)', MACrossoverStrategy({'short_window': 20, 'long_window': 50})),
        ('MA Crossover (10/30)', MACrossoverStrategy({'short_window': 10, 'long_window': 30})),
        ('RSI Mean Reversion', RSIStrategy({'window': 14, 'oversold_threshold': 35, 'overbought_threshold': 65})),
        ('EMA Crossover (9/21)', EMACrossoverStrategy({'short_window': 9, 'long_window': 21}))
    ]
    
    for name, strategy in strategies:
        batch_tester.add_strategy(name, strategy)
    
    print(f"   ✓ Added {len(strategies)} strategies")
    
    print("\n3. Generating sample data...")
    data = generate_sample_data(n_bars=400, start_price=30000)
    print(f"   ✓ Generated {len(data)} bars")
    
    print("\n4. Running batch backtest...")
    print("   (This may take 10-20 seconds...)\n")
    batch_tester.run_batch(data)
    
    print("\n5. Exporting results...")
    output_dir = 'data/demo_batch'
    os.makedirs(output_dir, exist_ok=True)
    batch_tester.export_results(output_dir=output_dir)
    
    print("\n6. Generating visualizations...")
    charts = batch_tester.visualize_results(
        output_dir=output_dir,
        use_plotly=False
    )
    
    print(f"\n   ✓ Generated visualizations for {len(charts)} strategies")
    for strategy_name, strategy_charts in charts.items():
        print(f"\n   {strategy_name}:")
        for chart_type, path in strategy_charts.items():
            print(f"     - {chart_type}: {os.path.basename(path)}")
    
    print("\n✓ Demo 3 completed!")


def demo_comparison_example():
    """Demo comparing strategy variations"""
    print("\n🎯 DEMO 4: Comparing Strategy Variations")
    print("-" * 70)
    
    from batch_backtester import BatchBacktester
    from utils import generate_sample_data
    from strategy import MACrossoverStrategy
    
    print("\n1. Testing MA Crossover with different parameters...")
    batch_tester = BatchBacktester(initial_capital=10000.0, trade_size=100.0)
    
    # Test different window combinations
    window_combos = [
        (10, 30),
        (20, 50),
        (30, 100),
        (50, 200)
    ]
    
    for short, long in window_combos:
        batch_tester.add_strategy(
            f'MA ({short}/{long})',
            MACrossoverStrategy({'short_window': short, 'long_window': long})
        )
    
    print(f"   ✓ Added {len(window_combos)} parameter variations")
    
    print("\n2. Running comparison...")
    data = generate_sample_data(n_bars=500, start_price=30000)
    batch_tester.run_batch(data)
    
    print("\n3. Finding best parameters...")
    best_strategy = None
    best_roi = float('-inf')
    
    for name, result in batch_tester.results.items():
        roi = result['metrics']['roi']
        if roi > best_roi:
            best_roi = roi
            best_strategy = name
    
    print(f"\n   🥇 Best performing: {best_strategy}")
    print(f"   📊 ROI: {best_roi:+.2f}%")
    
    print("\n✓ Demo 4 completed!")


def show_results_summary():
    """Show summary of generated files"""
    print("\n📁 FILES GENERATED")
    print("-" * 70)
    
    demo_dirs = [
        'data/demo_charts',
        'data/demo_backtest',
        'data/demo_batch'
    ]
    
    total_files = 0
    for demo_dir in demo_dirs:
        if os.path.exists(demo_dir):
            files = os.listdir(demo_dir)
            if files:
                print(f"\n{demo_dir}:")
                for f in sorted(files):
                    path = os.path.join(demo_dir, f)
                    size = os.path.getsize(path) / 1024
                    print(f"  ✓ {f} ({size:.1f} KB)")
                    total_files += 1
    
    print(f"\n📊 Total files generated: {total_files}")


def main():
    """Run all demos"""
    print_header()
    
    print("This demo will run 4 demonstrations:")
    print("  1. Basic visualization functions")
    print("  2. Backtester with visualization")
    print("  3. Batch backtesting multiple strategies")
    print("  4. Comparing strategy parameter variations")
    print()
    
    choice = input("Run all demos? (y/n): ").strip().lower()
    
    if choice != 'y':
        print("\nDemo cancelled.")
        return
    
    try:
        # Run demos
        demo_basic_visualization()
        input("\nPress Enter to continue to Demo 2...")
        
        demo_backtester_visualization()
        input("\nPress Enter to continue to Demo 3...")
        
        demo_batch_backtesting()
        input("\nPress Enter to continue to Demo 4...")
        
        demo_comparison_example()
        
        # Show summary
        show_results_summary()
        
        print("\n" + "=" * 70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Review generated files in data/demo_*/ directories")
        print("  2. Open HTML files in a browser for interactive charts")
        print("  3. Check BATCH_BACKTESTING_README.md for detailed documentation")
        print("  4. Run 'python batch_backtester.py' for interactive CLI")
        print("  5. Run 'python test_batch_backtesting.py' to verify installation")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
