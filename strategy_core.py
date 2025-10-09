"""
strategy_core.py - Reversal-Trailing-Stop Strategy
====================================================
Implements a trading strategy with immediate entry, trailing stops,
and position reversal on stop-loss breach.

Strategy Logic:
1. IMMEDIATE ENTRY: Bot starts with a BUY order immediately
2. TRAILING STOPS: Once in profit, trailing stop-loss and take-profit follow price favorably
3. REVERSAL: When trailing stop-loss is breached, close position and immediately 
   open opposite position with same capital
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Represents a trading position"""
    direction: str  # 'LONG' or 'SHORT'
    entry_price: float
    quantity: float
    stop_loss: float
    take_profit: float
    highest_price: float  # For trailing stop (LONG)
    lowest_price: float   # For trailing stop (SHORT)
    

class ReversalTrailingStopStrategy:
    """
    Reversal-Trailing-Stop Trading Strategy
    
    This strategy implements an aggressive trading approach with:
    - Immediate market entry on initialization
    - Dynamic trailing stop-loss and take-profit
    - Automatic position reversal when stop-loss is hit
    
    The strategy maintains continuous market exposure by immediately 
    reversing positions when stopped out.
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        stop_loss_percent: float = 2.0,
        take_profit_percent: float = 4.0,
        trailing_stop_percent: float = 1.0,
        initial_direction: str = 'LONG',
        enable_dynamic_adjustment: bool = True
    ):
        """
        Initialize the Reversal-Trailing-Stop strategy
        
        Args:
            initial_capital: Starting capital for trading
            stop_loss_percent: Initial stop-loss percentage (e.g., 2.0 = 2%)
            take_profit_percent: Take-profit percentage (e.g., 4.0 = 4%)
            trailing_stop_percent: Trailing stop distance percentage (e.g., 1.0 = 1%)
            initial_direction: Initial position direction ('LONG' or 'SHORT')
            enable_dynamic_adjustment: Enable dynamic parameter adjustment based on volatility
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.stop_loss_percent = stop_loss_percent / 100.0
        self.take_profit_percent = take_profit_percent / 100.0
        self.trailing_stop_percent = trailing_stop_percent / 100.0
        self.initial_direction = initial_direction
        
        # Position tracking
        self.position: Optional[Position] = None
        self.needs_immediate_entry = True  # Flag for immediate entry
        
        # Trade history
        self.trades = []
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        # Dynamic adjustment parameters
        self.base_stop_loss_percent = self.stop_loss_percent
        self.base_take_profit_percent = self.take_profit_percent
        self.base_trailing_stop_percent = self.trailing_stop_percent
        self.enable_dynamic_adjustment = enable_dynamic_adjustment
        self.price_history = []  # Track recent prices for volatility calculation
        self.volatility_window = 20  # Number of candles for volatility calculation
        
        logger.info(f"✓ ReversalTrailingStopStrategy initialized")
        logger.info(f"  Initial Capital: ${initial_capital:,.2f}")
        logger.info(f"  Stop Loss: {stop_loss_percent}%")
        logger.info(f"  Take Profit: {take_profit_percent}%")
        logger.info(f"  Trailing Stop: {trailing_stop_percent}%")
        logger.info(f"  Initial Direction: {initial_direction}")
        logger.info(f"  Dynamic Adjustment: {'Enabled' if self.enable_dynamic_adjustment else 'Disabled'}")
    
    def process_candle(self, candle: pd.Series) -> Dict[str, Any]:
        """
        Process a new price candle and generate trading signals
        
        Args:
            candle: Price data with 'open', 'high', 'low', 'close', 'volume'
        
        Returns:
            Dictionary with action, position info, and trade details
        """
        current_price = candle['close']
        high_price = candle['high']
        low_price = candle['low']
        
        # Track price history for volatility calculation
        self.price_history.append(current_price)
        if len(self.price_history) > self.volatility_window:
            self.price_history.pop(0)  # Keep only recent history
        
        # Calculate and adjust based on volatility (if enabled)
        if len(self.price_history) >= 2:
            volatility = self._calculate_market_volatility()
            self._adjust_parameters_based_on_volatility(volatility)
        
        result = {
            'action': 'HOLD',
            'price': current_price,
            'position': None,
            'trade_info': None
        }
        
        # IMMEDIATE ENTRY: Enter position on first candle
        if self.needs_immediate_entry:
            self._open_position(self.initial_direction, current_price)
            result['action'] = 'BUY' if self.initial_direction == 'LONG' else 'SELL'
            result['position'] = self._get_position_info()
            self.needs_immediate_entry = False
            return result
        
        # If no position, something went wrong
        if self.position is None:
            logger.warning("No position found, re-entering market")
            self._open_position(self.initial_direction, current_price)
            result['action'] = 'BUY' if self.initial_direction == 'LONG' else 'SELL'
            result['position'] = self._get_position_info()
            return result
        
        # Update trailing stops if in profit
        self._update_trailing_stops(current_price, high_price, low_price)
        
        # Check if stop-loss or take-profit is hit
        trade_result = self._check_exit_conditions(current_price, high_price, low_price)
        
        if trade_result:
            # Record trade
            self._record_trade(trade_result)
            
            # REVERSAL LOGIC: Immediately open opposite position
            if trade_result['exit_reason'] == 'STOP_LOSS':
                # Reverse position
                new_direction = 'SHORT' if self.position.direction == 'LONG' else 'LONG'
                logger.info(f"🔄 REVERSAL: Switching from {self.position.direction} to {new_direction}")
                self._open_position(new_direction, current_price)
                result['action'] = 'REVERSE'
                result['trade_info'] = trade_result
                result['position'] = self._get_position_info()
            else:
                # Take-profit hit: Re-enter in same direction
                logger.info(f"✅ TAKE-PROFIT: Re-entering {self.position.direction} position")
                same_direction = self.position.direction
                self._open_position(same_direction, current_price)
                result['action'] = 'REENTER'
                result['trade_info'] = trade_result
                result['position'] = self._get_position_info()
        else:
            # Update position info
            result['position'] = self._get_position_info()
        
        return result
    
    def _open_position(self, direction: str, entry_price: float):
        """
        Open a new position
        
        Args:
            direction: 'LONG' or 'SHORT'
            entry_price: Entry price for the position
        """
        # Calculate position size based on available capital
        quantity = self.capital / entry_price
        
        # Calculate initial stop-loss and take-profit levels
        if direction == 'LONG':
            stop_loss = entry_price * (1 - self.stop_loss_percent)
            take_profit = entry_price * (1 + self.take_profit_percent)
            highest_price = entry_price
            lowest_price = entry_price
        else:  # SHORT
            stop_loss = entry_price * (1 + self.stop_loss_percent)
            take_profit = entry_price * (1 - self.take_profit_percent)
            highest_price = entry_price
            lowest_price = entry_price
        
        self.position = Position(
            direction=direction,
            entry_price=entry_price,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            highest_price=highest_price,
            lowest_price=lowest_price
        )
        
        logger.info(f"📈 {direction} Position Opened:")
        logger.info(f"  Entry Price: ${entry_price:.2f}")
        logger.info(f"  Quantity: {quantity:.6f}")
        logger.info(f"  Stop Loss: ${stop_loss:.2f}")
        logger.info(f"  Take Profit: ${take_profit:.2f}")
    
    def _update_trailing_stops(self, current_price: float, high_price: float, low_price: float):
        """
        Update trailing stop-loss based on favorable price movements
        
        Args:
            current_price: Current closing price
            high_price: Candle high
            low_price: Candle low
        """
        if self.position is None:
            return
        
        if self.position.direction == 'LONG':
            # Update highest price seen
            self.position.highest_price = max(self.position.highest_price, high_price)
            
            # Check if position is in profit
            if self.position.highest_price > self.position.entry_price:
                # Calculate trailing stop from highest price
                trailing_stop = self.position.highest_price * (1 - self.trailing_stop_percent)
                
                # Only move stop-loss up (never down)
                if trailing_stop > self.position.stop_loss:
                    old_stop = self.position.stop_loss
                    self.position.stop_loss = trailing_stop
                    logger.debug(f"📊 Trailing Stop Updated: ${old_stop:.2f} -> ${trailing_stop:.2f}")
        
        else:  # SHORT
            # Update lowest price seen
            self.position.lowest_price = min(self.position.lowest_price, low_price)
            
            # Check if position is in profit
            if self.position.lowest_price < self.position.entry_price:
                # Calculate trailing stop from lowest price
                trailing_stop = self.position.lowest_price * (1 + self.trailing_stop_percent)
                
                # Only move stop-loss down (never up)
                if trailing_stop < self.position.stop_loss:
                    old_stop = self.position.stop_loss
                    self.position.stop_loss = trailing_stop
                    logger.debug(f"📊 Trailing Stop Updated: ${old_stop:.2f} -> ${trailing_stop:.2f}")
    
    def _check_exit_conditions(
        self, 
        current_price: float, 
        high_price: float, 
        low_price: float
    ) -> Optional[Dict[str, Any]]:
        """
        Check if stop-loss or take-profit conditions are met
        
        Args:
            current_price: Current closing price
            high_price: Candle high
            low_price: Candle low
        
        Returns:
            Trade result dictionary if position should be closed, None otherwise
        """
        if self.position is None:
            return None
        
        if self.position.direction == 'LONG':
            # Check stop-loss (using low price for more realistic execution)
            if low_price <= self.position.stop_loss:
                exit_price = self.position.stop_loss
                pnl = (exit_price - self.position.entry_price) * self.position.quantity
                self.capital += pnl
                
                return {
                    'direction': self.position.direction,
                    'entry_price': self.position.entry_price,
                    'exit_price': exit_price,
                    'quantity': self.position.quantity,
                    'pnl': pnl,
                    'exit_reason': 'STOP_LOSS',
                    'capital_after': self.capital
                }
            
            # Check take-profit (using high price for more realistic execution)
            if high_price >= self.position.take_profit:
                exit_price = self.position.take_profit
                pnl = (exit_price - self.position.entry_price) * self.position.quantity
                self.capital += pnl
                
                return {
                    'direction': self.position.direction,
                    'entry_price': self.position.entry_price,
                    'exit_price': exit_price,
                    'quantity': self.position.quantity,
                    'pnl': pnl,
                    'exit_reason': 'TAKE_PROFIT',
                    'capital_after': self.capital
                }
        
        else:  # SHORT
            # Check stop-loss (using high price for more realistic execution)
            if high_price >= self.position.stop_loss:
                exit_price = self.position.stop_loss
                pnl = (self.position.entry_price - exit_price) * self.position.quantity
                self.capital += pnl
                
                return {
                    'direction': self.position.direction,
                    'entry_price': self.position.entry_price,
                    'exit_price': exit_price,
                    'quantity': self.position.quantity,
                    'pnl': pnl,
                    'exit_reason': 'STOP_LOSS',
                    'capital_after': self.capital
                }
            
            # Check take-profit (using low price for more realistic execution)
            if low_price <= self.position.take_profit:
                exit_price = self.position.take_profit
                pnl = (self.position.entry_price - exit_price) * self.position.quantity
                self.capital += pnl
                
                return {
                    'direction': self.position.direction,
                    'entry_price': self.position.entry_price,
                    'exit_price': exit_price,
                    'quantity': self.position.quantity,
                    'pnl': pnl,
                    'exit_reason': 'TAKE_PROFIT',
                    'capital_after': self.capital
                }
        
        return None
    
    def _record_trade(self, trade_result: Dict[str, Any]):
        """
        Record trade statistics
        
        Args:
            trade_result: Dictionary with trade information
        """
        self.trades.append(trade_result)
        self.total_trades += 1
        
        if trade_result['pnl'] > 0:
            self.winning_trades += 1
            emoji = "💰"
        else:
            self.losing_trades += 1
            emoji = "📉"
        
        logger.info(f"{emoji} Trade Closed:")
        logger.info(f"  Direction: {trade_result['direction']}")
        logger.info(f"  Entry: ${trade_result['entry_price']:.2f}")
        logger.info(f"  Exit: ${trade_result['exit_price']:.2f}")
        logger.info(f"  P&L: ${trade_result['pnl']:.2f}")
        logger.info(f"  Reason: {trade_result['exit_reason']}")
        logger.info(f"  Capital: ${trade_result['capital_after']:.2f}")
    
    def _get_position_info(self) -> Dict[str, Any]:
        """
        Get current position information
        
        Returns:
            Dictionary with position details
        """
        if self.position is None:
            return {
                'has_position': False,
                'capital': self.capital
            }
        
        return {
            'has_position': True,
            'direction': self.position.direction,
            'entry_price': self.position.entry_price,
            'quantity': self.position.quantity,
            'stop_loss': self.position.stop_loss,
            'take_profit': self.position.take_profit,
            'highest_price': self.position.highest_price,
            'lowest_price': self.position.lowest_price,
            'capital': self.capital
        }
    
    def _calculate_market_volatility(self) -> float:
        """
        Calculate recent market volatility using price history
        
        Returns:
            Volatility as a percentage (standard deviation of returns)
        """
        if len(self.price_history) < 2:
            return 0.0
        
        # Calculate returns
        returns = []
        for i in range(1, len(self.price_history)):
            ret = (self.price_history[i] - self.price_history[i-1]) / self.price_history[i-1]
            returns.append(ret)
        
        if not returns:
            return 0.0
        
        # Calculate standard deviation
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        volatility = (variance ** 0.5) * 100  # Convert to percentage
        
        return volatility
    
    def _adjust_parameters_based_on_volatility(self, volatility: float):
        """
        Dynamically adjust strategy parameters based on market volatility
        
        Args:
            volatility: Current market volatility (as percentage)
        
        Adjusts:
        - High volatility (>2%): Widen stops to avoid premature exits
        - Low volatility (<0.5%): Tighten stops to lock in profits faster
        """
        if not self.enable_dynamic_adjustment:
            return
        
        # Define volatility thresholds
        HIGH_VOLATILITY_THRESHOLD = 2.0  # 2% volatility
        LOW_VOLATILITY_THRESHOLD = 0.5   # 0.5% volatility
        
        # Adjustment factors
        if volatility > HIGH_VOLATILITY_THRESHOLD:
            # High volatility: Widen stops by 50%
            adjustment_factor = 1.5
            adjustment_type = "HIGH VOLATILITY"
        elif volatility < LOW_VOLATILITY_THRESHOLD:
            # Low volatility: Tighten stops by 25%
            adjustment_factor = 0.75
            adjustment_type = "LOW VOLATILITY"
        else:
            # Normal volatility: Use base parameters
            adjustment_factor = 1.0
            adjustment_type = "NORMAL VOLATILITY"
        
        # Calculate adjusted parameters
        new_stop_loss = self.base_stop_loss_percent * adjustment_factor
        new_take_profit = self.base_take_profit_percent * adjustment_factor
        new_trailing_stop = self.base_trailing_stop_percent * adjustment_factor
        
        # Update if parameters have changed significantly
        if abs(new_stop_loss - self.stop_loss_percent) > 0.001:
            logger.info(f"🔧 DYNAMIC ADJUSTMENT ({adjustment_type}):")
            logger.info(f"  Volatility: {volatility:.2f}%")
            logger.info(f"  Stop Loss: {self.stop_loss_percent*100:.2f}% → {new_stop_loss*100:.2f}%")
            logger.info(f"  Take Profit: {self.take_profit_percent*100:.2f}% → {new_take_profit*100:.2f}%")
            logger.info(f"  Trailing Stop: {self.trailing_stop_percent*100:.2f}% → {new_trailing_stop*100:.2f}%")
            
            self.stop_loss_percent = new_stop_loss
            self.take_profit_percent = new_take_profit
            self.trailing_stop_percent = new_trailing_stop
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get trading statistics
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'roi': 0.0,
                'capital': self.capital
            }
        
        total_pnl = sum(trade['pnl'] for trade in self.trades)
        roi = (total_pnl / self.initial_capital) * 100 if self.initial_capital > 0 else 0.0
        win_rate = (self.winning_trades / self.total_trades) * 100 if self.total_trades > 0 else 0.0
        
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0.0
        avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0.0
        
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'roi': roi,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'capital': self.capital,
            'initial_capital': self.initial_capital
        }
    
    def print_statistics(self):
        """Print detailed trading statistics"""
        stats = self.get_statistics()
        
        print("\n" + "=" * 70)
        print("📊 REVERSAL-TRAILING-STOP STRATEGY STATISTICS")
        print("=" * 70)
        print(f"\n💰 CAPITAL:")
        print(f"  Initial Capital:  ${stats['initial_capital']:,.2f}")
        print(f"  Final Capital:    ${stats['capital']:,.2f}")
        print(f"  Total P&L:        ${stats['total_pnl']:,.2f}")
        print(f"  ROI:              {stats['roi']:.2f}%")
        print(f"\n📈 TRADES:")
        print(f"  Total Trades:     {stats['total_trades']}")
        print(f"  Winning Trades:   {stats['winning_trades']}")
        print(f"  Losing Trades:    {stats['losing_trades']}")
        print(f"  Win Rate:         {stats['win_rate']:.2f}%")
        
        if stats['total_trades'] > 0:
            print(f"  Average Win:      ${stats['avg_win']:.2f}")
            print(f"  Average Loss:     ${stats['avg_loss']:.2f}")
        
        print("=" * 70 + "\n")


def run_strategy_example():
    """
    Example usage of the Reversal-Trailing-Stop strategy
    Demonstrates how to use the strategy with sample data
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("🚀 REVERSAL-TRAILING-STOP STRATEGY DEMO")
    print("=" * 70)
    print()
    
    # Generate sample price data
    np.random.seed(42)
    n_candles = 500
    start_price = 30000
    
    # Generate realistic price movement with trend and noise
    prices = [start_price]
    for i in range(n_candles - 1):
        # Add trend (slight upward bias) and random noise
        trend = 0.0002  # Slight upward trend
        noise = np.random.normal(0, 0.005)  # 0.5% volatility
        change = trend + noise
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)
    
    # Create OHLCV dataframe
    data = []
    for i in range(len(prices)):
        price = prices[i]
        volatility = price * 0.002  # 0.2% intra-candle volatility
        
        open_price = price + np.random.uniform(-volatility, volatility)
        close_price = price
        high_price = max(open_price, close_price) + abs(np.random.uniform(0, volatility))
        low_price = min(open_price, close_price) - abs(np.random.uniform(0, volatility))
        volume = np.random.randint(1000000, 5000000)
        
        data.append({
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    
    print(f"Generated {len(df)} price candles")
    print(f"Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
    print()
    
    # Initialize strategy
    strategy = ReversalTrailingStopStrategy(
        initial_capital=10000.0,
        stop_loss_percent=2.0,      # 2% stop-loss
        take_profit_percent=4.0,     # 4% take-profit
        trailing_stop_percent=1.0,   # 1% trailing stop
        initial_direction='LONG'     # Start with LONG position
    )
    
    print("\n🔄 Running backtest...")
    print()
    
    # Process each candle
    for idx, candle in df.iterrows():
        result = strategy.process_candle(candle)
        
        # Log significant actions
        if result['action'] in ['BUY', 'SELL', 'REVERSE', 'REENTER']:
            print(f"[Candle {idx}] {result['action']} @ ${result['price']:.2f}")
            if result['trade_info']:
                trade = result['trade_info']
                pnl_emoji = "💰" if trade['pnl'] > 0 else "📉"
                print(f"  {pnl_emoji} P&L: ${trade['pnl']:.2f} ({trade['exit_reason']})")
    
    # Print final statistics
    strategy.print_statistics()


if __name__ == "__main__":
    run_strategy_example()
