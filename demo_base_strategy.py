"""
demo_base_strategy.py - Demo for Enhanced Base Strategy Framework
================================================================
Demonstrates the usage of the enhanced base strategy framework
for implementing video-based trading strategies.
"""
from base_strategy import (
    VideoBasedStrategy,
    EnhancedBaseStrategy,
    log_strategy_performance,
    create_strategy_from_video
)
from utils import generate_sample_data, setup_logging
import logging

# Setup logging
logger = setup_logging(log_level="INFO")


def demo_video_based_strategy():
    """Demo 1: Using the VideoBasedStrategy template"""
    print("\n" + "="*60)
    print("Demo 1: Video-Based Strategy Template")
    print("="*60)
    
    # Create strategy with custom parameters
    params = {
        'ma_short': 10,
        'ma_long': 50,
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_overbought': 70
    }
    
    strategy = VideoBasedStrategy(params)
    print(f"\n✓ Strategy created: {strategy.name}")
    print(f"  Parameters: {strategy.params}")
    
    # Generate sample data
    df = generate_sample_data(n_bars=100, start_price=50000)
    print(f"\n✓ Generated sample data: {len(df)} bars")
    print(f"  Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    
    # Generate signal
    signal = strategy.generate_signal(df)
    signal_text = "BUY" if signal == 1 else "SELL" if signal == -1 else "HOLD"
    print(f"\n✓ Signal generated: {signal_text}")
    
    # Generate signal with context
    signal2, context = strategy.generate_signal_with_context(df)
    print(f"\n✓ Signal with context:")
    print(f"  Signal: {context['signal_text']}")
    print(f"  Confidence: {context['confidence']:.2f}")
    print(f"  Current Price: ${context['current_price']:.2f}")
    print(f"  Timestamp: {context['timestamp']}")


def demo_multi_timeframe():
    """Demo 2: Multi-timeframe analysis"""
    print("\n" + "="*60)
    print("Demo 2: Multi-Timeframe Data Feeds")
    print("="*60)
    
    strategy = VideoBasedStrategy({})
    
    # Add multiple timeframe data
    df_15m = generate_sample_data(n_bars=100, start_price=50000)
    df_1h = generate_sample_data(n_bars=100, start_price=50000)
    df_4h = generate_sample_data(n_bars=100, start_price=50000)
    
    strategy.add_data_feed('BTC/USDT', '15m', df_15m)
    strategy.add_data_feed('BTC/USDT', '1h', df_1h)
    strategy.add_data_feed('BTC/USDT', '4h', df_4h)
    
    print(f"\n✓ Added {len(strategy.data_feeds)} data feeds:")
    for key in strategy.data_feeds.keys():
        print(f"  - {key}")
    
    # Retrieve specific feed
    retrieved = strategy.get_data_feed('BTC/USDT', '1h')
    if retrieved is not None:
        print(f"\n✓ Retrieved 1h feed: {len(retrieved)} bars")
        print(f"  Latest close: ${retrieved['close'].iloc[-1]:.2f}")


def demo_state_management():
    """Demo 3: State management and persistence"""
    print("\n" + "="*60)
    print("Demo 3: State Management")
    print("="*60)
    
    strategy = VideoBasedStrategy({})
    
    # Update state
    strategy.update_state(
        trades_count=10,
        wins_count=6,
        losses_count=4,
        total_profit=150.0
    )
    
    print("\n✓ State updated:")
    info = strategy.get_info()
    state = info['state']
    print(f"  Trades: {state['trades_count']}")
    print(f"  Wins: {state['wins_count']}")
    print(f"  Losses: {state['losses_count']}")
    print(f"  Win Rate: {state['win_rate']:.2%}")
    print(f"  Total P&L: ${state['total_profit']:.2f}")
    
    # Position lifecycle
    print("\n✓ Testing position lifecycle:")
    strategy.on_position_opened(entry_price=50000.0, quantity=0.01, side='long')
    print(f"  Position opened at $50,000")
    
    strategy.on_position_closed(exit_price=51000.0, profit=10.0, side='long')
    print(f"  Position closed at $51,000 (P&L: $10.00)")
    
    # Export state
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        state_file = f.name
    
    try:
        strategy.export_state(state_file)
        print(f"\n✓ State exported to: {state_file}")
        
        # Import in new strategy
        new_strategy = VideoBasedStrategy({})
        new_strategy.import_state(state_file)
        print(f"✓ State imported successfully")
        print(f"  Restored trades: {new_strategy.state.trades_count}")
    finally:
        if os.path.exists(state_file):
            os.remove(state_file)


def demo_performance_tracking():
    """Demo 4: Performance tracking"""
    print("\n" + "="*60)
    print("Demo 4: Performance Tracking")
    print("="*60)
    
    strategy = VideoBasedStrategy({
        'ma_short': 5,
        'ma_long': 20,
        'rsi_period': 14
    })
    
    df = generate_sample_data(n_bars=100, start_price=50000)
    
    # Generate multiple signals
    print("\n✓ Generating signals...")
    for i in range(10):
        signal, context = strategy.generate_signal_with_context(df)
        if i == 0:
            print(f"  First signal: {context['signal_text']}")
    
    # Show performance metrics
    print("\n✓ Performance Metrics:")
    metrics = strategy.performance_metrics
    print(f"  Total Signals: {metrics['signals_generated']}")
    print(f"  Buy Signals: {metrics['buy_signals']}")
    print(f"  Sell Signals: {metrics['sell_signals']}")
    print(f"  Hold Signals: {metrics['hold_signals']}")
    print(f"  Avg Execution Time: {metrics['avg_execution_time_ms']:.2f}ms")
    
    # Use logging utility
    print("\n✓ Detailed performance log:")
    log_strategy_performance(strategy, detailed=True)


def demo_integration_with_manager():
    """Demo 5: Integration with StrategyManager"""
    print("\n" + "="*60)
    print("Demo 5: Integration with Strategy Manager")
    print("="*60)
    
    from strategy import StrategyManager
    
    # Create config with video-based strategy
    config = {
        'active_strategies': ['video_based', 'rsi'],
        'cooperation_logic': 'OR',
        'strategies': {
            'video_based': {
                'ma_short': 10,
                'ma_long': 50,
                'rsi_period': 14
            },
            'rsi': {
                'window': 14,
                'oversold_threshold': 30,
                'overbought_threshold': 70
            }
        }
    }
    
    manager = StrategyManager(config)
    print(f"\n✓ StrategyManager created")
    print(f"  Active strategies: {list(manager.strategies.keys())}")
    
    # Generate signal
    df = generate_sample_data(n_bars=100, start_price=50000)
    signal, strategies = manager.get_aggregated_signal(df)
    
    signal_text = "BUY" if signal == 1 else "SELL" if signal == -1 else "HOLD"
    print(f"\n✓ Aggregated signal: {signal_text}")
    print(f"  Triggering strategies: {strategies if strategies else 'None'}")


def demo_factory_function():
    """Demo 6: Strategy factory function"""
    print("\n" + "="*60)
    print("Demo 6: Strategy Factory Function")
    print("="*60)
    
    # Create strategy from video reference
    strategy = create_strategy_from_video(
        video_id='FDmV1bIub_s',
        strategy_name='YouTubeStrategy',
        params={
            'ma_short': 12,
            'ma_long': 26,
            'rsi_period': 14
        }
    )
    
    print(f"\n✓ Strategy created from video ID: FDmV1bIub_s")
    print(f"  Strategy name: {strategy.name}")
    print(f"  Parameters: {strategy.params}")
    
    # Test it
    df = generate_sample_data(n_bars=100, start_price=50000)
    signal = strategy.generate_signal(df)
    signal_text = "BUY" if signal == 1 else "SELL" if signal == -1 else "HOLD"
    print(f"\n✓ Generated signal: {signal_text}")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("Enhanced Base Strategy Framework - Demo")
    print("="*60)
    print("\nThis demo showcases the new enhanced base strategy framework")
    print("for implementing video-based and custom trading strategies.")
    
    try:
        demo_video_based_strategy()
        demo_multi_timeframe()
        demo_state_management()
        demo_performance_tracking()
        demo_integration_with_manager()
        demo_factory_function()
        
        print("\n" + "="*60)
        print("✓ All demos completed successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Read docs/BASE_STRATEGY_GUIDE.md for detailed documentation")
        print("2. Implement your own strategy by extending EnhancedBaseStrategy")
        print("3. Test with backtesting before live trading")
        print("4. Always use DRY_RUN=true initially")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Demo failed: {e}")


if __name__ == '__main__':
    main()
