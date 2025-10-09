"""
demo_live_monitor.py - Demo Script for Live Market Monitor
===========================================================
Demonstrates the Live Market Monitor with various use cases.

This script showcases:
1. Basic monitoring setup
2. Strategy integration
3. Alert handling
4. Custom callbacks
"""
import sys
import logging
import time
from datetime import datetime

from live_market_monitor import LiveMarketMonitor, Alert
from strategy import TradingStrategy
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def demo_basic_monitoring():
    """Demo 1: Basic market monitoring"""
    print_header("📊 DEMO 1: Basic Market Monitoring")
    
    print("\n1. Initialize Live Market Monitor")
    print("   - Symbols: BTCUSDT, ETHUSDT")
    print("   - Interval: 15 minutes")
    print("   - Update: Every 30 seconds")
    print("   - Environment: Testnet")
    
    try:
        monitor = LiveMarketMonitor(
            symbols=['BTCUSDT', 'ETHUSDT'],
            interval='15m',
            update_interval=30,
            testnet=True,
            price_alert_threshold=1.0  # 1% change threshold
        )
        
        print("\n✓ Monitor initialized successfully")
        
        print("\n2. Testing connection to Binance...")
        if monitor.test_connection():
            print("✓ Connection successful!")
        else:
            print("❌ Connection failed - using simulation mode")
            return
        
        print("\n3. Performing single monitoring cycle...")
        results = monitor.monitor_once()
        
        print(f"\n✓ Monitored {len(results)} symbols:")
        for symbol, data in results.items():
            price = data['current_price']
            change = data['price_metrics'].get('percent_change', 0)
            print(f"   {symbol}: ${price:,.2f} ({change:+.2f}%)")
        
        print("\n✓ Demo 1 complete!")
        
    except Exception as e:
        logger.error(f"Demo 1 error: {e}", exc_info=True)


def demo_strategy_integration():
    """Demo 2: Monitoring with strategy integration"""
    print_header("🎯 DEMO 2: Strategy Integration")
    
    print("\n1. Configure trading strategies")
    print(f"   Active strategies: {config.active_strategies}")
    print(f"   Cooperation logic: {config.cooperation_logic}")
    
    try:
        # Initialize monitor
        monitor = LiveMarketMonitor(
            symbols=['BTCUSDT'],
            interval='15m',
            update_interval=60,
            testnet=True,
            price_alert_threshold=1.5
        )
        
        print("\n2. Initialize trading strategy")
        strategy = TradingStrategy(config.to_dict())
        print(f"✓ Strategy initialized with {len(config.active_strategies)} strategies")
        
        print("\n3. Integrate strategy with monitor")
        monitor.integrate_strategy(strategy)
        print("✓ Strategy integrated - signals will trigger alerts")
        
        print("\n4. Test connection")
        if not monitor.test_connection():
            print("❌ Connection failed")
            return
        print("✓ Connected")
        
        print("\n5. Performing monitoring cycle with strategy analysis...")
        results = monitor.monitor_once()
        
        for symbol, data in results.items():
            print(f"\n{symbol}:")
            print(f"   Price: ${data['current_price']:,.2f}")
            
            if data['signal_info']:
                signal_text = data['signal_info']['signal_text']
                strategies = data['signal_info']['strategies']
                print(f"   Signal: {signal_text}")
                if strategies:
                    print(f"   Triggered by: {', '.join(strategies)}")
            else:
                print("   Signal: No strategy signals")
        
        print("\n✓ Demo 2 complete!")
        
    except Exception as e:
        logger.error(f"Demo 2 error: {e}", exc_info=True)


def demo_alert_handling():
    """Demo 3: Custom alert handling"""
    print_header("🔔 DEMO 3: Custom Alert Handling")
    
    print("\n1. Setup custom alert handlers")
    
    # Track alerts
    alert_counts = {
        'price': 0,
        'signal': 0,
        'volume': 0
    }
    
    def alert_counter(alert: Alert):
        """Count alerts by type"""
        if alert.alert_type.value == 'price_change':
            alert_counts['price'] += 1
        elif alert.alert_type.value == 'strategy_signal':
            alert_counts['signal'] += 1
        elif alert.alert_type.value == 'volume_spike':
            alert_counts['volume'] += 1
    
    def priority_handler(alert: Alert):
        """Handle high-priority alerts"""
        if alert.priority in ['high', 'critical']:
            print(f"\n⚠️  HIGH PRIORITY ALERT:")
            print(f"    Type: {alert.alert_type.value}")
            print(f"    Symbol: {alert.symbol}")
            print(f"    Message: {alert.message}")
    
    def telegram_simulator(alert: Alert):
        """Simulate sending to Telegram"""
        if alert.priority == 'critical':
            print(f"\n📱 [TELEGRAM] {alert.symbol}: {alert.message}")
    
    print("   ✓ alert_counter: Counts alerts by type")
    print("   ✓ priority_handler: Handles high-priority alerts")
    print("   ✓ telegram_simulator: Simulates Telegram notifications")
    
    try:
        print("\n2. Initialize monitor with low threshold for demo")
        monitor = LiveMarketMonitor(
            symbols=['BTCUSDT'],
            interval='15m',
            update_interval=30,
            testnet=True,
            price_alert_threshold=0.5  # Very low threshold for demo
        )
        
        print("\n3. Register alert callbacks")
        monitor.register_alert_callback(alert_counter)
        monitor.register_alert_callback(priority_handler)
        monitor.register_alert_callback(telegram_simulator)
        print("✓ 3 callbacks registered")
        
        print("\n4. Integrate strategy for signal alerts")
        strategy = TradingStrategy(config.to_dict())
        monitor.integrate_strategy(strategy)
        
        if not monitor.test_connection():
            print("❌ Connection failed")
            return
        
        print("\n5. Performing monitoring cycles (3 cycles)...")
        for i in range(3):
            print(f"\n   Cycle {i+1}/3...")
            results = monitor.monitor_once()
            time.sleep(5)  # Short delay between cycles
        
        print("\n6. Alert Summary:")
        print(f"   Price alerts: {alert_counts['price']}")
        print(f"   Signal alerts: {alert_counts['signal']}")
        print(f"   Volume alerts: {alert_counts['volume']}")
        print(f"   Total: {sum(alert_counts.values())}")
        
        recent_alerts = monitor.alert_system.get_recent_alerts(limit=5)
        if recent_alerts:
            print(f"\n   Recent alerts ({len(recent_alerts)}):")
            for alert in recent_alerts:
                print(f"   - {alert}")
        
        print("\n✓ Demo 3 complete!")
        
    except Exception as e:
        logger.error(f"Demo 3 error: {e}", exc_info=True)


def demo_continuous_monitoring():
    """Demo 4: Continuous monitoring with time limit"""
    print_header("⏱️  DEMO 4: Continuous Monitoring")
    
    print("\n1. Setup continuous monitoring")
    print("   Duration: 2 minutes (120 seconds)")
    print("   Update interval: 15 seconds")
    
    try:
        monitor = LiveMarketMonitor(
            symbols=['BTCUSDT', 'ETHUSDT'],
            interval='5m',
            update_interval=15,
            testnet=True,
            price_alert_threshold=1.0
        )
        
        print("\n2. Integrate strategy")
        strategy = TradingStrategy(config.to_dict())
        monitor.integrate_strategy(strategy)
        
        print("\n3. Register alert callback")
        def simple_alert_logger(alert: Alert):
            print(f"🔔 {alert.timestamp.strftime('%H:%M:%S')}: {alert.message}")
        
        monitor.register_alert_callback(simple_alert_logger)
        
        if not monitor.test_connection():
            print("❌ Connection failed")
            return
        print("✓ Connected")
        
        print("\n4. Starting continuous monitoring...")
        print("   (Press Ctrl+C to stop early)")
        
        try:
            monitor.start_monitoring(duration=120)  # 2 minutes
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")
        
        print("\n✓ Demo 4 complete!")
        
    except Exception as e:
        logger.error(f"Demo 4 error: {e}", exc_info=True)


def interactive_menu():
    """Interactive demo menu"""
    print_header("🎮 Live Market Monitor - Interactive Demo")
    
    print("\nAvailable Demos:")
    print("  [1] Basic Market Monitoring")
    print("  [2] Strategy Integration")
    print("  [3] Custom Alert Handling")
    print("  [4] Continuous Monitoring (2 minutes)")
    print("  [5] Run All Demos")
    print("  [0] Exit")
    
    while True:
        try:
            choice = input("\nSelect demo (0-5): ").strip()
            
            if choice == '0':
                print("\n👋 Goodbye!")
                break
            elif choice == '1':
                demo_basic_monitoring()
            elif choice == '2':
                demo_strategy_integration()
            elif choice == '3':
                demo_alert_handling()
            elif choice == '4':
                demo_continuous_monitoring()
            elif choice == '5':
                print("\n🚀 Running all demos...")
                demo_basic_monitoring()
                demo_strategy_integration()
                demo_alert_handling()
                print("\nSkipping Demo 4 (continuous monitoring) in batch mode")
                print("Run it separately if desired.")
            else:
                print("❌ Invalid choice. Please select 0-5.")
            
            if choice in ['1', '2', '3', '4', '5']:
                input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Menu error: {e}")


def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("  🔍 Live Market Monitor - Demo Application")
    print("=" * 70)
    print("\nThis demo showcases the Live Market Monitoring capabilities:")
    print("- Real-time price monitoring")
    print("- Strategy signal detection")
    print("- Alert system with custom handlers")
    print("- Continuous monitoring")
    
    print("\nNote: This demo uses Binance TESTNET for safe testing.")
    print("No real money or live trading involved.")
    
    # Check if we should run specific demo
    if len(sys.argv) > 1:
        demo_arg = sys.argv[1]
        print(f"\nRunning demo: {demo_arg}")
        
        if demo_arg == '1' or demo_arg == 'basic':
            demo_basic_monitoring()
        elif demo_arg == '2' or demo_arg == 'strategy':
            demo_strategy_integration()
        elif demo_arg == '3' or demo_arg == 'alerts':
            demo_alert_handling()
        elif demo_arg == '4' or demo_arg == 'continuous':
            demo_continuous_monitoring()
        elif demo_arg == 'all':
            demo_basic_monitoring()
            demo_strategy_integration()
            demo_alert_handling()
        else:
            print(f"Unknown demo: {demo_arg}")
            print("Available: 1/basic, 2/strategy, 3/alerts, 4/continuous, all")
    else:
        # Interactive menu
        interactive_menu()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
