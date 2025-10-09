"""
strategy_broker_integration.py - Strategy + Broker Integration
===============================================================

Integrates trading strategies with broker API for automated trading.
Provides a bridge between strategy signals and broker execution.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from broker_api import BrokerInterface, BrokerFactory
from strategy_core import ReversalTrailingStopStrategy

logger = logging.getLogger(__name__)


class StrategyBrokerExecutor:
    """
    Executes trading strategy with real broker integration
    
    Manages the connection between strategy signals and broker orders,
    handling position tracking, order execution, and risk management.
    """
    
    def __init__(
        self,
        strategy: ReversalTrailingStopStrategy,
        broker: BrokerInterface,
        symbol: str,
        trade_quantity: float = 0.1
    ):
        """
        Initialize strategy-broker executor
        
        Args:
            strategy: Trading strategy instance
            broker: Broker interface instance
            symbol: Trading symbol (e.g., 'BTCUSDT')
            trade_quantity: Fixed quantity to trade
        """
        self.strategy = strategy
        self.broker = broker
        self.symbol = symbol
        self.trade_quantity = trade_quantity
        
        # Track broker orders
        self.active_order_id: Optional[str] = None
        self.last_action: Optional[str] = None
        
        logger.info("✓ Strategy-Broker Executor initialized")
        logger.info(f"  Strategy: {strategy.__class__.__name__}")
        logger.info(f"  Broker: {broker.__class__.__name__}")
        logger.info(f"  Symbol: {symbol}")
        logger.info(f"  Trade Quantity: {trade_quantity}")
    
    def process_candle(self, candle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a candle with strategy and execute trades
        
        Args:
            candle_data: Dictionary with OHLCV data
                {
                    'open': float,
                    'high': float,
                    'low': float,
                    'close': float,
                    'volume': float
                }
        
        Returns:
            Dictionary with execution results
        """
        # Get strategy signal
        strategy_result = self.strategy.process_candle(candle_data)
        
        action = strategy_result['action']
        current_price = strategy_result['price']
        
        # Execute trades based on strategy action
        execution_result = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'price': current_price,
            'strategy_result': strategy_result,
            'broker_order': None,
            'error': None
        }
        
        try:
            if action == 'BUY':
                # Execute buy order
                order = self._execute_buy(current_price)
                execution_result['broker_order'] = order
                
            elif action == 'SELL':
                # Execute sell order
                order = self._execute_sell(current_price)
                execution_result['broker_order'] = order
                
            elif action == 'REVERSE':
                # Close current position and open opposite
                close_order = self._execute_sell(current_price)
                # Immediately open opposite position
                new_order = self._execute_buy(current_price)
                execution_result['broker_order'] = {
                    'close_order': close_order,
                    'new_order': new_order
                }
                
            elif action == 'REENTER':
                # Re-enter position (same direction)
                order = self._execute_buy(current_price)
                execution_result['broker_order'] = order
                
            # Update last action
            if action != 'HOLD':
                self.last_action = action
                
        except Exception as e:
            logger.error(f"Error executing broker order: {e}")
            execution_result['error'] = str(e)
        
        return execution_result
    
    def _execute_buy(self, price: float) -> Dict[str, Any]:
        """Execute buy order"""
        logger.info(f"📈 Executing BUY order: {self.trade_quantity} {self.symbol} @ ${price:.2f}")
        
        order = self.broker.place_market_order(
            symbol=self.symbol,
            quantity=self.trade_quantity,
            side='BUY',
            current_price=price  # For paper trading
        )
        
        self.active_order_id = order['order_id']
        
        logger.info(f"✓ BUY order executed: {order['order_id']}")
        return order
    
    def _execute_sell(self, price: float) -> Dict[str, Any]:
        """Execute sell order"""
        logger.info(f"📉 Executing SELL order: {self.trade_quantity} {self.symbol} @ ${price:.2f}")
        
        order = self.broker.place_market_order(
            symbol=self.symbol,
            quantity=self.trade_quantity,
            side='SELL',
            current_price=price  # For paper trading
        )
        
        self.active_order_id = None
        
        logger.info(f"✓ SELL order executed: {order['order_id']}")
        return order
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get combined performance summary from strategy and broker"""
        # Get strategy statistics
        strategy_stats = self.strategy.get_statistics()
        
        # Get broker balance
        balance = self.broker.get_account_balance('USDT')
        
        # Get open positions
        positions = self.broker.get_positions(self.symbol)
        
        return {
            'strategy_stats': strategy_stats,
            'broker_balance': balance,
            'open_positions': positions,
            'active_order_id': self.active_order_id,
            'last_action': self.last_action
        }
    
    def close_all_positions(self):
        """Close all open positions"""
        logger.info("Closing all positions...")
        
        positions = self.broker.get_positions(self.symbol)
        
        if positions:
            for pos in positions:
                self.broker.close_position(pos['symbol'])
                logger.info(f"✓ Closed position: {pos['symbol']}")
        else:
            logger.info("No positions to close")


# Example usage
if __name__ == "__main__":
    import pandas as pd
    from utils import setup_logging, generate_sample_data
    
    # Setup logging
    logger = setup_logging(log_level="INFO")
    
    print("=" * 70)
    print("STRATEGY-BROKER INTEGRATION EXAMPLE")
    print("=" * 70)
    
    # Create broker (paper trading)
    print("\n1. Creating paper trading broker...")
    broker = BrokerFactory.create_broker('paper', initial_capital=10000)
    print("✓ Broker created")
    
    # Create strategy
    print("\n2. Creating Reversal-Trailing-Stop strategy...")
    strategy = ReversalTrailingStopStrategy(
        initial_capital=10000,
        stop_loss_percent=2.0,
        take_profit_percent=4.0,
        trailing_stop_percent=1.0,
        initial_direction='LONG'
    )
    print("✓ Strategy created")
    
    # Create executor
    print("\n3. Creating strategy-broker executor...")
    executor = StrategyBrokerExecutor(
        strategy=strategy,
        broker=broker,
        symbol='BTCUSDT',
        trade_quantity=0.1
    )
    print("✓ Executor created")
    
    # Generate sample market data
    print("\n4. Generating sample market data...")
    df = generate_sample_data(n_bars=100, start_price=50000)
    print(f"✓ Generated {len(df)} candles")
    
    # Run strategy with broker integration
    print("\n5. Running strategy with broker execution...")
    print("-" * 70)
    
    trades_executed = 0
    
    for i in range(len(df)):
        candle = {
            'open': df.iloc[i]['open'],
            'high': df.iloc[i]['high'],
            'low': df.iloc[i]['low'],
            'close': df.iloc[i]['close'],
            'volume': df.iloc[i]['volume']
        }
        
        result = executor.process_candle(candle)
        
        if result['action'] != 'HOLD':
            trades_executed += 1
            print(f"\nCandle {i+1}: {result['action']}")
            print(f"  Price: ${result['price']:.2f}")
            
            if result['broker_order']:
                if isinstance(result['broker_order'], dict) and 'close_order' in result['broker_order']:
                    print(f"  Close Order: {result['broker_order']['close_order']['order_id']}")
                    print(f"  New Order: {result['broker_order']['new_order']['order_id']}")
                else:
                    print(f"  Order ID: {result['broker_order']['order_id']}")
            
            if result['error']:
                print(f"  ⚠️ Error: {result['error']}")
    
    print("\n" + "-" * 70)
    print(f"\n6. Performance Summary:")
    print("-" * 70)
    
    # Get performance summary
    summary = executor.get_performance_summary()
    
    # Strategy stats
    stats = summary['strategy_stats']
    print(f"\n📊 Strategy Performance:")
    print(f"  Total Trades: {stats['total_trades']}")
    print(f"  Winning Trades: {stats['winning_trades']}")
    print(f"  Win Rate: {stats['win_rate']:.2f}%")
    print(f"  Total P&L: ${stats['total_pnl']:.2f}")
    print(f"  ROI: {stats['roi']:.2f}%")
    
    # Broker stats
    balance = summary['broker_balance']
    print(f"\n💰 Broker Balance:")
    print(f"  Total: ${balance['total']:,.2f}")
    print(f"  Free: ${balance['free']:,.2f}")
    
    # Positions
    positions = summary['open_positions']
    print(f"\n📋 Open Positions: {len(positions)}")
    for pos in positions:
        print(f"  • {pos['symbol']}: {pos['quantity']}")
    
    print(f"\n📈 Trades Executed: {trades_executed}")
    
    # Close any open positions
    print("\n7. Closing all positions...")
    executor.close_all_positions()
    
    print("\n" + "=" * 70)
    print("✅ EXAMPLE COMPLETED")
    print("=" * 70)
