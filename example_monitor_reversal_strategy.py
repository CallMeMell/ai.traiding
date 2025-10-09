"""
example_monitor_reversal_strategy.py - Live Monitoring with Reversal Strategy
==============================================================================
Example demonstrating integration of Live Market Monitor with the 
Reversal-Trailing-Stop strategy.

This example shows:
1. Setting up live monitoring for crypto markets
2. Integrating the Reversal-Trailing-Stop strategy
3. Receiving alerts for trade signals
4. Monitoring position changes and performance
"""
import logging
from datetime import datetime

from live_market_monitor import LiveMarketMonitor, Alert
from strategy_core import ReversalTrailingStopStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReversalStrategyMonitor:
    """
    Wrapper class that adapts ReversalTrailingStopStrategy to work with
    the LiveMarketMonitor's strategy integration interface.
    """
    
    def __init__(self, reversal_strategy: ReversalTrailingStopStrategy):
        """
        Initialize the adapter
        
        Args:
            reversal_strategy: ReversalTrailingStopStrategy instance
        """
        self.reversal_strategy = reversal_strategy
        self.last_signal = 0
        logger.info("✓ ReversalStrategyMonitor initialized")
    
    def analyze(self, df):
        """
        Analyze market data and generate signals compatible with LiveMarketMonitor
        
        Args:
            df: OHLCV DataFrame
        
        Returns:
            Dictionary with signal, price, and strategy info
        """
        if df is None or len(df) < 2:
            return {
                'signal': 0,
                'signal_text': 'HOLD',
                'triggering_strategies': [],
                'current_price': 0,
                'timestamp': None
            }
        
        current_price = df['close'].iloc[-1]
        
        # Process the latest candle with the reversal strategy
        candle = {
            'open': df['open'].iloc[-1],
            'high': df['high'].iloc[-1],
            'low': df['low'].iloc[-1],
            'close': df['close'].iloc[-1],
            'volume': df['volume'].iloc[-1]
        }
        
        # Update strategy
        action = self.reversal_strategy.update(candle)
        
        # Convert action to signal
        signal = 0
        signal_text = 'HOLD'
        strategies = []
        
        if action and 'action' in action:
            if action['action'] in ['BUY', 'ENTER_LONG']:
                signal = 1
                signal_text = 'BUY'
                strategies = ['Reversal-Trailing-Stop']
            elif action['action'] in ['SELL', 'ENTER_SHORT', 'CLOSE_LONG']:
                signal = -1
                signal_text = 'SELL'
                strategies = ['Reversal-Trailing-Stop']
        
        # Get strategy state for additional info
        state = self.reversal_strategy.get_state()
        
        return {
            'signal': signal,
            'signal_text': signal_text,
            'triggering_strategies': strategies,
            'current_price': current_price,
            'timestamp': df['timestamp'].iloc[-1] if 'timestamp' in df.columns else None,
            'position': state['position'],
            'capital': state['capital'],
            'total_pnl': state['total_pnl'],
            'roi': state['roi']
        }


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def example_basic_integration():
    """Example 1: Basic integration with monitoring"""
    print_header("📊 Example 1: Basic Reversal Strategy Monitoring")
    
    print("\n1. Initialize Reversal-Trailing-Stop Strategy")
    print("   - Initial Capital: $10,000")
    print("   - Stop Loss: 2%")
    print("   - Take Profit: 4%")
    print("   - Trailing Stop: 1%")
    
    reversal_strategy = ReversalTrailingStopStrategy(
        initial_capital=10000.0,
        stop_loss_percent=2.0,
        take_profit_percent=4.0,
        trailing_stop_percent=1.0,
        initial_direction='LONG'
    )
    
    print("\n2. Wrap strategy for monitor integration")
    strategy_adapter = ReversalStrategyMonitor(reversal_strategy)
    
    print("\n3. Initialize Live Market Monitor")
    monitor = LiveMarketMonitor(
        symbols=['BTCUSDT'],
        interval='15m',
        update_interval=60,
        testnet=True,
        price_alert_threshold=1.5
    )
    
    print("\n4. Integrate strategy with monitor")
    monitor.integrate_strategy(strategy_adapter)
    
    print("\n5. Test connection")
    if not monitor.test_connection():
        print("❌ Connection failed - check API keys and network")
        return
    print("✓ Connection successful")
    
    print("\n6. Perform single monitoring cycle")
    results = monitor.monitor_once()
    
    for symbol, data in results.items():
        print(f"\n{symbol} Status:")
        print(f"   Current Price: ${data['current_price']:,.2f}")
        
        if data['signal_info']:
            info = data['signal_info']
            print(f"   Signal: {info['signal_text']}")
            if info.get('position'):
                pos = info['position']
                print(f"   Position: {pos['direction']} @ ${pos['entry_price']:,.2f}")
                print(f"   Stop Loss: ${pos['stop_loss']:,.2f}")
                print(f"   Take Profit: ${pos['take_profit']:,.2f}")
            print(f"   Capital: ${info.get('capital', 0):,.2f}")
            print(f"   Total P&L: ${info.get('total_pnl', 0):,.2f}")
            print(f"   ROI: {info.get('roi', 0):.2f}%")
    
    print("\n✓ Example 1 complete!")


def example_with_custom_alerts():
    """Example 2: Monitoring with custom alert handling"""
    print_header("🔔 Example 2: Monitoring with Custom Alerts")
    
    print("\n1. Setup strategy and monitor")
    
    reversal_strategy = ReversalTrailingStopStrategy(
        initial_capital=10000.0,
        stop_loss_percent=2.0,
        take_profit_percent=4.0,
        trailing_stop_percent=1.0,
        initial_direction='LONG'
    )
    
    strategy_adapter = ReversalStrategyMonitor(reversal_strategy)
    
    monitor = LiveMarketMonitor(
        symbols=['BTCUSDT'],
        interval='5m',
        update_interval=30,
        testnet=True,
        price_alert_threshold=1.0
    )
    
    monitor.integrate_strategy(strategy_adapter)
    
    print("\n2. Register custom alert handlers")
    
    # Track trades
    trade_log = []
    
    def trade_alert_handler(alert: Alert):
        """Log trade signals"""
        if alert.alert_type.value == 'strategy_signal':
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            trade_log.append({
                'timestamp': timestamp,
                'symbol': alert.symbol,
                'signal': alert.data.get('signal_text', 'UNKNOWN'),
                'price': alert.data.get('price', 0)
            })
            
            print(f"\n📋 Trade Signal Logged:")
            print(f"   Time: {timestamp}")
            print(f"   Symbol: {alert.symbol}")
            print(f"   Action: {alert.data.get('signal_text', 'UNKNOWN')}")
            print(f"   Price: ${alert.data.get('price', 0):,.2f}")
    
    def performance_tracker(alert: Alert):
        """Track performance metrics"""
        if alert.alert_type.value == 'strategy_signal':
            state = reversal_strategy.get_state()
            if state['total_trades'] > 0:
                win_rate = (state['winning_trades'] / state['total_trades']) * 100
                print(f"\n📊 Performance Update:")
                print(f"   Total Trades: {state['total_trades']}")
                print(f"   Win Rate: {win_rate:.1f}%")
                print(f"   Total P&L: ${state['total_pnl']:,.2f}")
                print(f"   ROI: {state['roi']:.2f}%")
    
    monitor.register_alert_callback(trade_alert_handler)
    monitor.register_alert_callback(performance_tracker)
    
    if not monitor.test_connection():
        print("❌ Connection failed")
        return
    print("✓ Connected")
    
    print("\n3. Running monitoring cycles (5 cycles)...")
    for i in range(5):
        print(f"\n--- Cycle {i+1}/5 ---")
        results = monitor.monitor_once()
        
        import time
        time.sleep(3)  # Short delay between cycles
    
    print("\n4. Trade Summary:")
    if trade_log:
        print(f"   Trades logged: {len(trade_log)}")
        for trade in trade_log[-3:]:  # Show last 3 trades
            print(f"   - {trade['timestamp']}: {trade['signal']} {trade['symbol']} @ ${trade['price']:,.2f}")
    else:
        print("   No trades logged")
    
    print("\n✓ Example 2 complete!")


def example_continuous_monitoring():
    """Example 3: Continuous monitoring with reversal strategy"""
    print_header("⏱️  Example 3: Continuous Monitoring")
    
    print("\n1. Setup strategy and monitor for continuous operation")
    
    reversal_strategy = ReversalTrailingStopStrategy(
        initial_capital=10000.0,
        stop_loss_percent=2.0,
        take_profit_percent=4.0,
        trailing_stop_percent=1.0,
        initial_direction='LONG',
        enable_dynamic_adjustment=True  # Enable dynamic adjustment
    )
    
    strategy_adapter = ReversalStrategyMonitor(reversal_strategy)
    
    monitor = LiveMarketMonitor(
        symbols=['BTCUSDT'],
        interval='5m',
        update_interval=30,
        testnet=True,
        price_alert_threshold=1.0
    )
    
    monitor.integrate_strategy(strategy_adapter)
    
    print("\n2. Register comprehensive alert handlers")
    
    def comprehensive_alert_handler(alert: Alert):
        """Handle all types of alerts"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if alert.priority in ['high', 'critical']:
            print(f"\n⚠️  [{timestamp}] {alert}")
            
            # Additional info for strategy signals
            if alert.alert_type.value == 'strategy_signal':
                state = reversal_strategy.get_state()
                if state['position']:
                    pos = state['position']
                    print(f"   Position: {pos['direction']} @ ${pos['entry_price']:,.2f}")
                    
                    # Calculate unrealized P&L
                    current_price = alert.data.get('price', 0)
                    if pos['direction'] == 'LONG':
                        pnl = (current_price - pos['entry_price']) * pos['quantity']
                    else:
                        pnl = (pos['entry_price'] - current_price) * pos['quantity']
                    
                    print(f"   Unrealized P&L: ${pnl:,.2f}")
    
    monitor.register_alert_callback(comprehensive_alert_handler)
    
    if not monitor.test_connection():
        print("❌ Connection failed")
        return
    print("✓ Connected")
    
    print("\n3. Starting continuous monitoring (2 minutes)")
    print("   Press Ctrl+C to stop early")
    
    try:
        monitor.start_monitoring(duration=120)  # 2 minutes
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")
    
    # Final performance report
    state = reversal_strategy.get_state()
    
    print("\n" + "=" * 70)
    print("  📊 Final Performance Report")
    print("=" * 70)
    print(f"Initial Capital:  ${reversal_strategy.initial_capital:,.2f}")
    print(f"Current Capital:  ${state['capital']:,.2f}")
    print(f"Total P&L:        ${state['total_pnl']:,.2f}")
    print(f"ROI:              {state['roi']:.2f}%")
    print(f"Total Trades:     {state['total_trades']}")
    print(f"Winning Trades:   {state['winning_trades']}")
    print(f"Losing Trades:    {state['losing_trades']}")
    if state['total_trades'] > 0:
        win_rate = (state['winning_trades'] / state['total_trades']) * 100
        print(f"Win Rate:         {win_rate:.1f}%")
    print("=" * 70)
    
    print("\n✓ Example 3 complete!")


def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("  Live Market Monitor with Reversal-Trailing-Stop Strategy")
    print("=" * 70)
    print("\nThis example demonstrates integrating the Reversal-Trailing-Stop")
    print("strategy with live market monitoring for real-time trading signals.")
    print("\nNote: Uses Binance TESTNET for safe testing.")
    
    import sys
    
    if len(sys.argv) > 1:
        example = sys.argv[1]
        if example == '1' or example == 'basic':
            example_basic_integration()
        elif example == '2' or example == 'alerts':
            example_with_custom_alerts()
        elif example == '3' or example == 'continuous':
            example_continuous_monitoring()
        else:
            print(f"\nUnknown example: {example}")
            print("Available: 1/basic, 2/alerts, 3/continuous")
    else:
        # Interactive menu
        print("\nAvailable Examples:")
        print("  [1] Basic Integration")
        print("  [2] Custom Alert Handling")
        print("  [3] Continuous Monitoring")
        
        choice = input("\nSelect example (1-3): ").strip()
        
        if choice == '1':
            example_basic_integration()
        elif choice == '2':
            example_with_custom_alerts()
        elif choice == '3':
            example_continuous_monitoring()
        else:
            print("Invalid choice")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
