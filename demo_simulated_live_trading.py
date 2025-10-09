"""
demo_simulated_live_trading.py - Demo of Simulated Live Trading Environment
===========================================================================

Demonstrates the simulated live-trading environment with realistic
trading conditions including slippage, fees, and execution delays.
"""

import logging
import time
from datetime import datetime
from simulated_live_trading import SimulatedLiveTradingEnvironment

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def print_separator(title: str = ""):
    """Print a separator line"""
    if title:
        print("\n" + "=" * 80)
        print(f" {title}")
        print("=" * 80)
    else:
        print("\n" + "-" * 80)


def print_metrics(metrics):
    """Print performance metrics"""
    print("\n📊 PERFORMANCE METRICS:")
    print(f"   Total Orders:        {metrics.total_orders}")
    print(f"   Filled Orders:       {metrics.filled_orders}")
    print(f"   Rejected Orders:     {metrics.rejected_orders}")
    print(f"   Total Volume Traded: ${metrics.total_volume_traded:,.2f}")
    print(f"   Total Fees Paid:     ${metrics.total_fees_paid:.2f}")
    print(f"   Total Slippage:      ${metrics.total_slippage:.2f}")
    print(f"   Avg Slippage:        {metrics.avg_slippage_percent:.4f}%")
    print(f"   Avg Exec Delay:      {metrics.avg_execution_delay_ms:.1f}ms")
    print(f"   Total P&L:           ${metrics.total_pnl:,.2f}")
    print(f"   Realized P&L:        ${metrics.realized_pnl:,.2f}")
    print(f"   Unrealized P&L:      ${metrics.unrealized_pnl:,.2f}")
    if metrics.sharpe_ratio != 0:
        print(f"   Sharpe Ratio:        {metrics.sharpe_ratio:.3f}")
    if metrics.max_drawdown_percent != 0:
        print(f"   Max Drawdown:        {metrics.max_drawdown_percent:.2f}%")


def demo_basic_trading():
    """Demo 1: Basic Trading with All Features Enabled"""
    print_separator("DEMO 1: Basic Trading with Realistic Conditions")
    
    # Create environment with all features enabled
    env = SimulatedLiveTradingEnvironment(
        initial_capital=10000.0,
        use_live_data=False,
        enable_slippage=True,
        enable_fees=True,
        enable_execution_delay=True,
        enable_market_impact=True
    )
    
    print("\n✅ Environment Initialized:")
    print(f"   Initial Capital: ${env.initial_capital:,.2f}")
    print(f"   Slippage: Enabled")
    print(f"   Fees: Enabled (0.075% maker/taker)")
    print(f"   Execution Delay: Enabled (50-200ms)")
    
    # Place some trades
    print_separator("Executing Trades")
    
    # Buy BTC
    print("\n📈 Buying BTC...")
    result = env.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
    print(f"   Order ID: {result.order_id}")
    print(f"   Status: {result.status}")
    print(f"   Execution Price: ${result.execution_price:.2f}")
    print(f"   Slippage: ${result.slippage:.2f} ({result.slippage_percent:.4f}%)")
    print(f"   Fees: ${result.fees:.2f}")
    print(f"   Execution Delay: {result.execution_delay_ms:.1f}ms")
    
    # Simulate price movement
    time.sleep(0.5)
    
    # Buy ETH
    print("\n📈 Buying ETH...")
    result = env.place_market_order('ETHUSDT', 1.5, 'BUY', current_price=3000.0)
    print(f"   Order ID: {result.order_id}")
    print(f"   Status: {result.status}")
    print(f"   Execution Price: ${result.execution_price:.2f}")
    print(f"   Slippage: ${result.slippage:.2f} ({result.slippage_percent:.4f}%)")
    print(f"   Fees: ${result.fees:.2f}")
    
    # Check positions
    print_separator("Current Positions")
    positions = env.get_positions()
    for symbol, pos in positions.items():
        print(f"\n{symbol}:")
        print(f"   Quantity: {pos['quantity']}")
        print(f"   Entry Price: ${pos['entry_price']:.2f}")
        print(f"   Current Price: ${pos['current_price']:.2f}")
        print(f"   Unrealized P&L: ${pos['unrealized_pnl']:.2f} ({pos['unrealized_pnl_percent']:.2f}%)")
    
    # Simulate profit and sell
    time.sleep(0.5)
    print_separator("Taking Profit")
    
    print("\n📉 Selling BTC at profit...")
    result = env.place_market_order('BTCUSDT', 0.1, 'SELL', current_price=51000.0)
    print(f"   Status: {result.status}")
    print(f"   Execution Price: ${result.execution_price:.2f}")
    print(f"   Slippage: ${result.slippage:.2f} ({result.slippage_percent:.4f}%)")
    
    # Get final metrics
    print_separator("Final Performance Metrics")
    metrics = env.get_performance_metrics()
    print_metrics(metrics)
    
    # Get account balance
    balance = env.get_account_balance()
    print("\n💰 ACCOUNT BALANCE:")
    print(f"   Available Capital:   ${balance['capital']:,.2f}")
    print(f"   Unrealized P&L:      ${balance['unrealized_pnl']:,.2f}")
    print(f"   Total Equity:        ${balance['total_equity']:,.2f}")
    print(f"   ROI:                 {((balance['total_equity'] / balance['initial_capital']) - 1) * 100:.2f}%")


def demo_no_slippage_comparison():
    """Demo 2: Comparison with and without slippage"""
    print_separator("DEMO 2: Impact of Slippage and Fees")
    
    # Trading with all features
    print("\n🔵 Scenario A: With Slippage & Fees")
    env_with = SimulatedLiveTradingEnvironment(
        initial_capital=10000.0,
        enable_slippage=True,
        enable_fees=True,
        enable_execution_delay=False  # Disable to speed up demo
    )
    
    # Execute same trade
    buy_result = env_with.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
    sell_result = env_with.place_market_order('BTCUSDT', 0.1, 'SELL', current_price=51000.0)
    
    metrics_with = env_with.get_performance_metrics()
    balance_with = env_with.get_account_balance()
    
    print(f"   Buy Price:  ${buy_result.execution_price:.2f}")
    print(f"   Sell Price: ${sell_result.execution_price:.2f}")
    print(f"   Total Fees: ${metrics_with.total_fees_paid:.2f}")
    print(f"   Total Slippage: ${metrics_with.total_slippage:.2f}")
    print(f"   Final Equity: ${balance_with['total_equity']:,.2f}")
    print(f"   Net P&L: ${balance_with['total_equity'] - 10000:.2f}")
    
    # Trading without features
    print("\n🟢 Scenario B: Without Slippage & Fees")
    env_without = SimulatedLiveTradingEnvironment(
        initial_capital=10000.0,
        enable_slippage=False,
        enable_fees=False,
        enable_execution_delay=False
    )
    
    buy_result = env_without.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
    sell_result = env_without.place_market_order('BTCUSDT', 0.1, 'SELL', current_price=51000.0)
    
    metrics_without = env_without.get_performance_metrics()
    balance_without = env_without.get_account_balance()
    
    print(f"   Buy Price:  ${buy_result.execution_price:.2f}")
    print(f"   Sell Price: ${sell_result.execution_price:.2f}")
    print(f"   Total Fees: ${metrics_without.total_fees_paid:.2f}")
    print(f"   Total Slippage: ${metrics_without.total_slippage:.2f}")
    print(f"   Final Equity: ${balance_without['total_equity']:,.2f}")
    print(f"   Net P&L: ${balance_without['total_equity'] - 10000:.2f}")
    
    # Calculate impact
    print("\n📊 IMPACT ANALYSIS:")
    pnl_diff = balance_without['total_equity'] - balance_with['total_equity']
    print(f"   Cost of Slippage & Fees: ${pnl_diff:.2f}")
    print(f"   Percentage Impact: {(pnl_diff / 100) * 100:.2f}% of potential profit")


def demo_high_frequency_trading():
    """Demo 3: High-frequency trading scenario"""
    print_separator("DEMO 3: High-Frequency Trading Simulation")
    
    env = SimulatedLiveTradingEnvironment(
        initial_capital=10000.0,
        enable_slippage=True,
        enable_fees=True,
        enable_execution_delay=True
    )
    
    print("\n🔄 Executing 20 rapid trades...")
    print("   (Simulating algorithmic trading strategy)")
    
    start_time = time.time()
    
    # Simulate rapid trading
    base_price = 50000.0
    for i in range(10):
        # Buy
        price = base_price + (i * 100) + ((-1) ** i * 50)  # Some price variation
        env.place_market_order('BTCUSDT', 0.01, 'BUY', current_price=price)
        
        # Sell
        sell_price = price + 100  # Small profit target
        env.place_market_order('BTCUSDT', 0.01, 'SELL', current_price=sell_price)
    
    elapsed_time = time.time() - start_time
    
    print(f"\n✅ Completed 20 orders in {elapsed_time:.3f} seconds")
    
    # Get metrics
    metrics = env.get_performance_metrics()
    balance = env.get_account_balance()
    
    print_separator("High-Frequency Trading Results")
    print_metrics(metrics)
    
    print(f"\n💰 Final Equity: ${balance['total_equity']:,.2f}")
    print(f"💰 Net P&L: ${balance['total_equity'] - 10000:.2f}")
    
    # Calculate costs
    print("\n📊 COST BREAKDOWN:")
    print(f"   Total Trading Fees: ${metrics.total_fees_paid:.2f}")
    print(f"   Total Slippage Cost: ${metrics.total_slippage:.2f}")
    print(f"   Combined Costs: ${metrics.total_fees_paid + metrics.total_slippage:.2f}")
    print(f"   Avg Cost per Trade: ${(metrics.total_fees_paid + metrics.total_slippage) / metrics.filled_orders:.2f}")


def demo_save_session_log():
    """Demo 4: Save comprehensive session log"""
    print_separator("DEMO 4: Session Logging")
    
    env = SimulatedLiveTradingEnvironment(initial_capital=10000.0)
    
    print("\n📝 Executing sample trades...")
    
    # Execute some trades
    env.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000.0)
    env.place_market_order('ETHUSDT', 1.0, 'BUY', current_price=3000.0)
    env.place_market_order('BTCUSDT', 0.05, 'SELL', current_price=51000.0)
    
    # Save session log
    print("\n💾 Saving session log...")
    log_file = "logs/demo_session.log"
    env.save_session_log(log_file)
    
    print(f"   ✅ Session log saved to: {log_file}")
    print(f"   📄 Contains:")
    print(f"      - Performance metrics")
    print(f"      - Complete execution history")
    print(f"      - Detailed order information")
    print(f"      - Slippage and fee breakdown")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print(" SIMULATED LIVE TRADING ENVIRONMENT - DEMONSTRATION")
    print("=" * 80)
    print("\nThis demo showcases realistic live-trading simulation with:")
    print("  ✓ Order execution delays (50-200ms)")
    print("  ✓ Price slippage (0.01-0.1%)")
    print("  ✓ Transaction fees (0.075% maker/taker)")
    print("  ✓ Market impact simulation")
    print("  ✓ Comprehensive performance metrics")
    print("  ✓ Detailed execution logging")
    
    try:
        # Run demos
        demo_basic_trading()
        time.sleep(1)
        
        demo_no_slippage_comparison()
        time.sleep(1)
        
        demo_high_frequency_trading()
        time.sleep(1)
        
        demo_save_session_log()
        
        print_separator("DEMO COMPLETE")
        print("\n✅ All demonstrations completed successfully!")
        print("\nNext Steps:")
        print("  1. Review the session log in logs/demo_session.log")
        print("  2. Run tests: python test_simulated_live_trading.py")
        print("  3. Integrate with your trading strategies")
        print("  4. See SIMULATED_LIVE_TRADING_GUIDE.md for full documentation")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
