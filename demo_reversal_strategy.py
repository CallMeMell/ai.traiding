"""
demo_reversal_strategy.py - Demo Script for Reversal-Trailing-Stop Strategy
=============================================================================
Demonstrates the Reversal-Trailing-Stop strategy with sample data and
comprehensive performance metrics.

This script showcases:
1. Strategy initialization and configuration
2. Running backtest on sample data
3. Performance metrics (ROI, Sharpe Ratio, Maximum Drawdown)
4. Visual results summary
"""
import sys
from strategy_core import ReversalTrailingStopStrategy
from backtest_reversal import ReversalBacktester
from utils import generate_sample_data, format_currency, format_percentage
import logging

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


def demo_basic_strategy():
    """Demonstrate basic strategy usage"""
    print_header("📈 DEMO 1: Basic Strategy Usage")
    
    print("\n1. Initialize strategy with parameters:")
    print("   - Initial Capital: $10,000")
    print("   - Stop Loss: 2%")
    print("   - Take Profit: 4%")
    print("   - Trailing Stop: 1%")
    print("   - Initial Direction: LONG")
    
    strategy = ReversalTrailingStopStrategy(
        initial_capital=10000.0,
        stop_loss_percent=2.0,
        take_profit_percent=4.0,
        trailing_stop_percent=1.0,
        initial_direction='LONG'
    )
    
    print("\n✓ Strategy initialized successfully")
    
    print("\n2. Generate sample price data (100 candles)...")
    import pandas as pd
    import numpy as np
    
    np.random.seed(42)
    n_candles = 100
    start_price = 30000
    
    prices = [start_price]
    for _ in range(n_candles - 1):
        change = np.random.normal(0.0002, 0.005)
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)
    
    data = []
    for price in prices:
        volatility = price * 0.002
        open_price = price + np.random.uniform(-volatility, volatility)
        close_price = price
        high_price = max(open_price, close_price) + abs(np.random.uniform(0, volatility))
        low_price = min(open_price, close_price) - abs(np.random.uniform(0, volatility))
        
        data.append({
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': np.random.randint(1000000, 5000000)
        })
    
    df = pd.DataFrame(data)
    print(f"✓ Generated {len(df)} candles")
    print(f"  Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
    
    print("\n3. Process candles and track trades...")
    trade_count = 0
    for idx, candle in df.iterrows():
        result = strategy.process_candle(candle)
        if result['action'] in ['REVERSE', 'REENTER']:
            trade_count += 1
            print(f"  [Candle {idx}] {result['action']} @ ${result['price']:.2f}")
    
    print(f"\n✓ Processed all candles, {trade_count} trades executed")
    
    # Show statistics
    stats = strategy.get_statistics()
    print(f"\n4. Results:")
    print(f"   Final Capital: {format_currency(stats['capital'])}")
    print(f"   ROI: {format_percentage(stats['roi'])}")
    print(f"   Win Rate: {format_percentage(stats['win_rate'])}")


def demo_full_backtest():
    """Demonstrate full backtesting with all metrics"""
    print_header("📊 DEMO 2: Complete Backtest with All Metrics")
    
    print("\n1. Initialize backtester...")
    backtester = ReversalBacktester(
        initial_capital=10000.0,
        stop_loss_percent=2.0,
        take_profit_percent=4.0,
        trailing_stop_percent=1.0,
        initial_direction='LONG'
    )
    print("✓ Backtester initialized")
    
    print("\n2. Generate 1000 candles of sample data...")
    data = generate_sample_data(n_bars=1000, start_price=30000)
    print(f"✓ Generated {len(data)} candles")
    print(f"  Price range: ${data['low'].min():.2f} - ${data['high'].max():.2f}")
    
    print("\n3. Running backtest (this may take a moment)...")
    print("   Processing candles...")
    
    # Suppress detailed logs for cleaner demo
    logging.getLogger().setLevel(logging.WARNING)
    backtester.run(data)
    logging.getLogger().setLevel(logging.INFO)
    
    print("\n✓ Backtest completed!")
    
    # Get and display metrics
    stats = backtester.strategy.get_statistics()
    
    print("\n" + "=" * 70)
    print("  📊 PERFORMANCE METRICS")
    print("=" * 70)
    
    print(f"\n💰 CAPITAL:")
    print(f"  Initial Capital:      {format_currency(stats['initial_capital'])}")
    print(f"  Final Capital:        {format_currency(stats['capital'])}")
    print(f"  Total P&L:            {format_currency(stats['total_pnl'])}")
    print(f"  ROI:                  {format_percentage(stats['roi'])}")
    
    print(f"\n📈 TRADES:")
    print(f"  Total Trades:         {stats['total_trades']}")
    print(f"  Winning Trades:       {stats['winning_trades']}")
    print(f"  Losing Trades:        {stats['losing_trades']}")
    print(f"  Win Rate:             {format_percentage(stats['win_rate'])}")
    print(f"  Average Win:          {format_currency(stats['avg_win'])}")
    print(f"  Average Loss:         {format_currency(stats['avg_loss'])}")
    
    # Calculate advanced metrics
    from utils import calculate_sharpe_ratio, calculate_max_drawdown
    
    print(f"\n📊 ADVANCED METRICS:")
    
    if backtester.returns and len(backtester.returns) >= 2:
        sharpe = calculate_sharpe_ratio(backtester.returns)
        print(f"  Sharpe Ratio:         {sharpe:.3f}")
        
        if sharpe > 2.0:
            print(f"    → Excellent risk-adjusted returns! ✨")
        elif sharpe > 1.0:
            print(f"    → Good risk-adjusted returns ✓")
        elif sharpe > 0:
            print(f"    → Positive but suboptimal ⚠️")
        else:
            print(f"    → Poor risk-adjusted returns ❌")
    
    if backtester.equity_curve and len(backtester.equity_curve) >= 2:
        max_dd_percent, max_dd_value, peak, trough = calculate_max_drawdown(backtester.equity_curve)
        print(f"  Maximum Drawdown:     {format_percentage(max_dd_percent)}")
        print(f"    Drawdown Value:     {format_currency(max_dd_value)}")
        print(f"    Peak Capital:       {format_currency(peak)}")
        print(f"    Trough Capital:     {format_currency(trough)}")
        
        if abs(max_dd_percent) < 10:
            print(f"    → Low drawdown, stable strategy ✓")
        elif abs(max_dd_percent) < 20:
            print(f"    → Moderate drawdown ⚠️")
        else:
            print(f"    → High drawdown, risky strategy ❌")
    
    print("\n" + "=" * 70)


def demo_parameter_comparison():
    """Compare different parameter sets"""
    print_header("🔬 DEMO 3: Parameter Comparison")
    
    print("\nComparing three different parameter configurations:")
    print("  A) Conservative: 1% SL, 2% TP, 0.5% Trailing")
    print("  B) Moderate:     2% SL, 4% TP, 1.0% Trailing")
    print("  C) Aggressive:   3% SL, 6% TP, 1.5% Trailing")
    
    # Generate data once
    print("\nGenerating test data (500 candles)...")
    data = generate_sample_data(n_bars=500, start_price=30000)
    print(f"✓ Data generated: ${data['low'].min():.2f} - ${data['high'].max():.2f}")
    
    configs = [
        ("Conservative", 1.0, 2.0, 0.5),
        ("Moderate", 2.0, 4.0, 1.0),
        ("Aggressive", 3.0, 6.0, 1.5)
    ]
    
    results = []
    
    print("\nRunning backtests...")
    for name, sl, tp, ts in configs:
        print(f"\n  Testing {name}...")
        
        # Suppress logs
        logging.getLogger().setLevel(logging.ERROR)
        
        backtester = ReversalBacktester(
            initial_capital=10000.0,
            stop_loss_percent=sl,
            take_profit_percent=tp,
            trailing_stop_percent=ts,
            initial_direction='LONG'
        )
        
        backtester.run(data)
        stats = backtester.strategy.get_statistics()
        
        from utils import calculate_sharpe_ratio, calculate_max_drawdown
        
        sharpe = 0.0
        if backtester.returns and len(backtester.returns) >= 2:
            sharpe = calculate_sharpe_ratio(backtester.returns)
        
        max_dd = 0.0
        if backtester.equity_curve and len(backtester.equity_curve) >= 2:
            max_dd, _, _, _ = calculate_max_drawdown(backtester.equity_curve)
        
        results.append({
            'name': name,
            'roi': stats['roi'],
            'trades': stats['total_trades'],
            'win_rate': stats['win_rate'],
            'sharpe': sharpe,
            'max_dd': max_dd
        })
        
        print(f"    ✓ ROI: {format_percentage(stats['roi'])}, Sharpe: {sharpe:.2f}")
    
    # Re-enable logging
    logging.getLogger().setLevel(logging.INFO)
    
    # Display comparison table
    print("\n" + "=" * 70)
    print("  📊 COMPARISON RESULTS")
    print("=" * 70)
    print(f"\n{'Config':<15} {'ROI':<12} {'Trades':<10} {'Win Rate':<12} {'Sharpe':<10} {'Max DD':<10}")
    print("-" * 70)
    
    for r in results:
        print(f"{r['name']:<15} {format_percentage(r['roi']):<12} {r['trades']:<10} {format_percentage(r['win_rate']):<12} {r['sharpe']:<10.2f} {format_percentage(r['max_dd']):<10}")
    
    # Find best configuration
    best_sharpe = max(results, key=lambda x: x['sharpe'])
    best_roi = max(results, key=lambda x: x['roi'])
    
    print("\n💡 INSIGHTS:")
    print(f"  Best Risk-Adjusted Returns: {best_sharpe['name']} (Sharpe: {best_sharpe['sharpe']:.2f})")
    print(f"  Highest ROI: {best_roi['name']} (ROI: {format_percentage(best_roi['roi'])})")


def interactive_demo():
    """Interactive demo menu"""
    print("\n" + "=" * 70)
    print("  🚀 REVERSAL-TRAILING-STOP STRATEGY DEMO")
    print("=" * 70)
    print("\nThis demo showcases the Reversal-Trailing-Stop strategy with")
    print("comprehensive backtesting and performance metrics.")
    
    demos = [
        ("Basic Strategy Usage", demo_basic_strategy),
        ("Complete Backtest with All Metrics", demo_full_backtest),
        ("Parameter Comparison", demo_parameter_comparison),
    ]
    
    while True:
        print("\n📋 Choose a demo:")
        print("  [0] Run all demos")
        for i, (name, _) in enumerate(demos, 1):
            print(f"  [{i}] {name}")
        print("  [q] Exit")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'q':
            print("\n👋 Demo finished. Happy trading!")
            break
        
        elif choice == '0':
            print("\n🚀 Running all demos...")
            for name, demo_func in demos:
                demo_func()
                input("\nPress Enter to continue...")
            print("\n✅ All demos completed!")
        
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            idx = int(choice) - 1
            name, demo_func = demos[idx]
            demo_func()
            input("\nPress Enter to return to menu...")
        
        else:
            print("❌ Invalid choice. Please try again.")


def main():
    """Main entry point"""
    try:
        interactive_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
