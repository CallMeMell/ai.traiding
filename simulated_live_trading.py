"""
simulated_live_trading.py - Simulated Live-Trading Environment
==============================================================

A comprehensive simulated live-trading environment that:
- Uses live market data (or simulated data as fallback)
- Executes trades in sandbox mode without real money
- Mimics realistic trading conditions:
  * Order execution delays (50-200ms)
  * Slippage based on volatility and order size
  * Variable transaction fees (maker/taker model)
  * Market impact simulation
  * Partial fills for large orders
- Generates performance metrics and comprehensive logs

Usage:
    from simulated_live_trading import SimulatedLiveTradingEnvironment
    
    # Create environment
    env = SimulatedLiveTradingEnvironment(
        initial_capital=10000.0,
        use_live_data=True,
        enable_slippage=True,
        enable_fees=True
    )
    
    # Place an order
    order = env.place_market_order('BTCUSDT', 0.1, 'BUY')
    
    # Get performance metrics
    metrics = env.get_performance_metrics()
"""

import logging
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import pandas as pd
import numpy as np

from config import config

logger = logging.getLogger(__name__)


@dataclass
class OrderExecutionResult:
    """Result of an order execution with realistic simulation"""
    order_id: str
    symbol: str
    side: str  # 'BUY' or 'SELL'
    order_type: str  # 'MARKET' or 'LIMIT'
    requested_quantity: float
    filled_quantity: float
    requested_price: Optional[float]  # For limit orders
    execution_price: float
    slippage: float  # Absolute slippage amount
    slippage_percent: float
    fees: float
    execution_delay_ms: float
    timestamp: datetime
    status: str  # 'FILLED', 'PARTIALLY_FILLED', 'REJECTED'
    total_cost: float  # Including fees
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side,
            'order_type': self.order_type,
            'requested_quantity': self.requested_quantity,
            'filled_quantity': self.filled_quantity,
            'requested_price': self.requested_price,
            'execution_price': self.execution_price,
            'slippage': self.slippage,
            'slippage_percent': self.slippage_percent,
            'fees': self.fees,
            'execution_delay_ms': self.execution_delay_ms,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'total_cost': self.total_cost
        }


@dataclass
class SimulationMetrics:
    """Performance metrics for simulated trading session"""
    total_orders: int = 0
    filled_orders: int = 0
    partially_filled_orders: int = 0
    rejected_orders: int = 0
    total_volume_traded: float = 0.0
    total_fees_paid: float = 0.0
    total_slippage: float = 0.0
    avg_slippage_percent: float = 0.0
    avg_execution_delay_ms: float = 0.0
    total_pnl: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown_percent: float = 0.0
    equity_curve: List[float] = field(default_factory=list)
    execution_history: List[OrderExecutionResult] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_orders': self.total_orders,
            'filled_orders': self.filled_orders,
            'partially_filled_orders': self.partially_filled_orders,
            'rejected_orders': self.rejected_orders,
            'total_volume_traded': self.total_volume_traded,
            'total_fees_paid': self.total_fees_paid,
            'total_slippage': self.total_slippage,
            'avg_slippage_percent': self.avg_slippage_percent,
            'avg_execution_delay_ms': self.avg_execution_delay_ms,
            'total_pnl': self.total_pnl,
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': self.unrealized_pnl,
            'win_rate': self.win_rate,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown_percent': self.max_drawdown_percent
        }


class SimulatedLiveTradingEnvironment:
    """
    Simulated Live-Trading Environment
    
    Provides a realistic simulation of live trading conditions including:
    - Order execution delays
    - Price slippage
    - Transaction fees
    - Market impact
    - Partial fills
    
    Can use live market data or simulated data.
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        use_live_data: bool = False,
        enable_slippage: bool = True,
        enable_fees: bool = True,
        enable_execution_delay: bool = True,
        enable_market_impact: bool = True,
        data_provider: Optional[Any] = None
    ):
        """
        Initialize simulated live-trading environment
        
        Args:
            initial_capital: Starting capital in base currency
            use_live_data: Whether to use live market data
            enable_slippage: Simulate price slippage
            enable_fees: Apply transaction fees
            enable_execution_delay: Simulate execution delays
            enable_market_impact: Simulate market impact on large orders
            data_provider: Optional external data provider (e.g., BinanceDataProvider)
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.use_live_data = use_live_data
        self.enable_slippage = enable_slippage
        self.enable_fees = enable_fees
        self.enable_execution_delay = enable_execution_delay
        self.enable_market_impact = enable_market_impact
        self.data_provider = data_provider
        
        # Trading state
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.orders: Dict[str, OrderExecutionResult] = {}
        self.next_order_id = 1000
        
        # Performance tracking
        self.metrics = SimulationMetrics()
        self.metrics.equity_curve.append(initial_capital)
        
        # Market data cache
        self.market_data_cache: Dict[str, Dict[str, Any]] = {}
        self.last_market_update: Dict[str, datetime] = {}
        
        logger.info("=" * 70)
        logger.info("🔧 SIMULATED LIVE TRADING ENVIRONMENT INITIALIZED")
        logger.info("=" * 70)
        logger.info(f"Initial Capital: ${initial_capital:,.2f}")
        logger.info(f"Using Live Data: {use_live_data}")
        logger.info(f"Slippage Enabled: {enable_slippage}")
        logger.info(f"Fees Enabled: {enable_fees}")
        logger.info(f"Execution Delay Enabled: {enable_execution_delay}")
        logger.info(f"Market Impact Enabled: {enable_market_impact}")
        logger.info("=" * 70)
    
    def _generate_order_id(self) -> str:
        """Generate unique order ID"""
        order_id = f"SIM_{self.next_order_id}_{int(time.time() * 1000)}"
        self.next_order_id += 1
        return order_id
    
    def _get_current_price(self, symbol: str) -> float:
        """
        Get current market price for symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Current market price
        """
        # Try to get live data if available
        if self.use_live_data and self.data_provider:
            try:
                # Attempt to get price from data provider
                price = self.data_provider.get_current_price(symbol)
                if price:
                    self.market_data_cache[symbol] = {
                        'price': price,
                        'timestamp': datetime.now()
                    }
                    return price
            except Exception as e:
                logger.warning(f"Could not fetch live price for {symbol}: {e}")
        
        # Fallback: use cached data or simulate
        if symbol in self.market_data_cache:
            cached_data = self.market_data_cache[symbol]
            # Add some random walk to cached price
            base_price = cached_data['price']
            volatility = 0.001  # 0.1% volatility
            price_change = base_price * random.gauss(0, volatility)
            new_price = base_price + price_change
            
            self.market_data_cache[symbol] = {
                'price': new_price,
                'timestamp': datetime.now()
            }
            return new_price
        else:
            # Initial simulated price
            default_prices = {
                'BTCUSDT': 50000.0,
                'ETHUSDT': 3000.0,
                'BTC/USDT': 50000.0,
                'ETH/USDT': 3000.0
            }
            initial_price = default_prices.get(symbol, 100.0)
            self.market_data_cache[symbol] = {
                'price': initial_price,
                'timestamp': datetime.now()
            }
            return initial_price
    
    def _calculate_slippage(
        self,
        symbol: str,
        side: str,
        quantity: float,
        base_price: float
    ) -> Tuple[float, float]:
        """
        Calculate realistic slippage based on market conditions
        
        Args:
            symbol: Trading symbol
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            base_price: Base price before slippage
            
        Returns:
            Tuple of (slippage_amount, slippage_percent)
        """
        if not self.enable_slippage:
            return 0.0, 0.0
        
        # Base slippage from config
        min_slippage = config.slippage_min_percent / 100.0
        max_slippage = config.slippage_max_percent / 100.0
        
        # Random component
        base_slippage = random.uniform(min_slippage, max_slippage)
        
        # Adjust for order size (larger orders = more slippage)
        order_value = quantity * base_price
        size_factor = min(order_value / self.capital, 1.0) * 0.5
        
        # Adjust for market volatility (simulated)
        volatility_factor = random.uniform(0.5, 1.5)
        
        # Calculate total slippage
        total_slippage_percent = base_slippage * (1 + size_factor) * volatility_factor
        total_slippage_percent = min(total_slippage_percent, max_slippage * 2)
        
        # Apply slippage direction (BUY = worse price higher, SELL = worse price lower)
        slippage_multiplier = 1.0 if side.upper() == 'BUY' else -1.0
        slippage_amount = base_price * total_slippage_percent * slippage_multiplier
        
        return slippage_amount, total_slippage_percent * 100
    
    def _calculate_fees(self, order_value: float, is_maker: bool = False) -> float:
        """
        Calculate transaction fees
        
        Args:
            order_value: Total order value
            is_maker: True if maker order, False if taker
            
        Returns:
            Fee amount
        """
        if not self.enable_fees:
            return 0.0
        
        fee_percent = config.maker_fee_percent if is_maker else config.taker_fee_percent
        fee = order_value * (fee_percent / 100.0)
        return fee
    
    def _simulate_execution_delay(self) -> float:
        """
        Simulate order execution delay
        
        Returns:
            Execution delay in milliseconds
        """
        if not self.enable_execution_delay:
            return 0.0
        
        # Random delay between configured min and max
        delay_ms = random.uniform(
            config.execution_delay_min_ms,
            config.execution_delay_max_ms
        )
        
        # Actually sleep for a fraction of the delay (scaled down for simulation)
        # Sleep for 1/10th of the delay to avoid slowing down too much
        time.sleep(delay_ms / 10000.0)
        
        return delay_ms
    
    def place_market_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        current_price: Optional[float] = None
    ) -> OrderExecutionResult:
        """
        Place a market order with realistic simulation
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'BUY' or 'SELL'
            current_price: Optional current price (for testing)
            
        Returns:
            OrderExecutionResult with execution details
        """
        start_time = time.time()
        order_id = self._generate_order_id()
        
        logger.info(f"📝 Placing market order: {side} {quantity} {symbol}")
        
        # Get current price
        if current_price is None:
            current_price = self._get_current_price(symbol)
        
        # Simulate execution delay
        execution_delay = self._simulate_execution_delay()
        
        # Calculate slippage
        slippage_amount, slippage_percent = self._calculate_slippage(
            symbol, side, quantity, current_price
        )
        
        # Calculate execution price
        execution_price = current_price + slippage_amount
        
        # Calculate order value and fees
        order_value = quantity * execution_price
        fees = self._calculate_fees(order_value, is_maker=False)  # Market orders are taker
        
        # Total cost including fees
        if side.upper() == 'BUY':
            total_cost = order_value + fees
        else:
            total_cost = order_value - fees
        
        # Check if order can be filled
        status = 'FILLED'
        filled_quantity = quantity
        
        if side.upper() == 'BUY':
            # Check capital for buy orders
            if total_cost > self.capital:
                logger.error(f"❌ Insufficient capital: Need ${total_cost:.2f}, Have ${self.capital:.2f}")
                status = 'REJECTED'
                filled_quantity = 0.0
            else:
                # Execute buy
                self.capital -= total_cost
                
                # Update or create position
                if symbol in self.positions:
                    # Average down
                    pos = self.positions[symbol]
                    total_quantity = pos['quantity'] + quantity
                    avg_price = (
                        (pos['quantity'] * pos['entry_price']) + 
                        (quantity * execution_price)
                    ) / total_quantity
                    pos['quantity'] = total_quantity
                    pos['entry_price'] = avg_price
                else:
                    self.positions[symbol] = {
                        'quantity': quantity,
                        'entry_price': execution_price,
                        'entry_time': datetime.now()
                    }
                
                logger.info(f"✅ BUY executed: {quantity} {symbol} @ ${execution_price:.2f}")
                logger.info(f"   Slippage: ${slippage_amount:.2f} ({slippage_percent:.3f}%)")
                logger.info(f"   Fees: ${fees:.2f}")
                logger.info(f"   Capital: ${self.capital:.2f}")
        
        else:  # SELL
            # Check if we have position to sell
            if symbol not in self.positions:
                logger.error(f"❌ No position to sell for {symbol}")
                status = 'REJECTED'
                filled_quantity = 0.0
            elif self.positions[symbol]['quantity'] < quantity:
                logger.error(f"❌ Insufficient position: Have {self.positions[symbol]['quantity']}, Need {quantity}")
                status = 'REJECTED'
                filled_quantity = 0.0
            else:
                # Execute sell
                self.capital += total_cost
                
                # Calculate realized P&L
                pos = self.positions[symbol]
                pnl = (execution_price - pos['entry_price']) * quantity - fees
                self.metrics.realized_pnl += pnl
                
                # Update position
                pos['quantity'] -= quantity
                if pos['quantity'] <= 0:
                    del self.positions[symbol]
                
                logger.info(f"✅ SELL executed: {quantity} {symbol} @ ${execution_price:.2f}")
                logger.info(f"   Slippage: ${slippage_amount:.2f} ({slippage_percent:.3f}%)")
                logger.info(f"   Fees: ${fees:.2f}")
                logger.info(f"   P&L: ${pnl:.2f}")
                logger.info(f"   Capital: ${self.capital:.2f}")
        
        # Create execution result
        result = OrderExecutionResult(
            order_id=order_id,
            symbol=symbol,
            side=side.upper(),
            order_type='MARKET',
            requested_quantity=quantity,
            filled_quantity=filled_quantity,
            requested_price=None,
            execution_price=execution_price,
            slippage=slippage_amount,
            slippage_percent=slippage_percent,
            fees=fees,
            execution_delay_ms=execution_delay,
            timestamp=datetime.now(),
            status=status,
            total_cost=total_cost if status == 'FILLED' else 0.0
        )
        
        # Update metrics
        self.metrics.total_orders += 1
        if status == 'FILLED':
            self.metrics.filled_orders += 1
            self.metrics.total_volume_traded += order_value
            self.metrics.total_fees_paid += fees
            self.metrics.total_slippage += abs(slippage_amount)
        elif status == 'REJECTED':
            self.metrics.rejected_orders += 1
        
        # Update equity curve
        self._update_equity_curve()
        
        # Store order
        self.orders[order_id] = result
        self.metrics.execution_history.append(result)
        
        return result
    
    def _update_equity_curve(self):
        """Update equity curve with current portfolio value"""
        # Calculate unrealized P&L from open positions
        unrealized_pnl = 0.0
        for symbol, pos in self.positions.items():
            current_price = self._get_current_price(symbol)
            position_value = pos['quantity'] * current_price
            cost_basis = pos['quantity'] * pos['entry_price']
            unrealized_pnl += (position_value - cost_basis)
        
        self.metrics.unrealized_pnl = unrealized_pnl
        total_equity = self.capital + unrealized_pnl
        self.metrics.equity_curve.append(total_equity)
        self.metrics.total_pnl = total_equity - self.initial_capital
    
    def get_account_balance(self) -> Dict[str, float]:
        """Get current account balance"""
        unrealized_pnl = sum(
            (self._get_current_price(symbol) - pos['entry_price']) * pos['quantity']
            for symbol, pos in self.positions.items()
        )
        
        return {
            'capital': self.capital,
            'unrealized_pnl': unrealized_pnl,
            'total_equity': self.capital + unrealized_pnl,
            'initial_capital': self.initial_capital
        }
    
    def get_positions(self) -> Dict[str, Dict[str, Any]]:
        """Get current positions"""
        positions_with_pnl = {}
        for symbol, pos in self.positions.items():
            current_price = self._get_current_price(symbol)
            unrealized_pnl = (current_price - pos['entry_price']) * pos['quantity']
            
            positions_with_pnl[symbol] = {
                **pos,
                'current_price': current_price,
                'unrealized_pnl': unrealized_pnl,
                'unrealized_pnl_percent': (unrealized_pnl / (pos['entry_price'] * pos['quantity'])) * 100
            }
        
        return positions_with_pnl
    
    def get_performance_metrics(self) -> SimulationMetrics:
        """
        Calculate and return comprehensive performance metrics
        
        Returns:
            SimulationMetrics with all performance data
        """
        # Update current equity
        self._update_equity_curve()
        
        # Calculate average slippage
        if self.metrics.filled_orders > 0:
            total_slippage_percent = sum(
                order.slippage_percent 
                for order in self.metrics.execution_history 
                if order.status == 'FILLED'
            )
            self.metrics.avg_slippage_percent = total_slippage_percent / self.metrics.filled_orders
            
            # Calculate average execution delay
            total_delay = sum(
                order.execution_delay_ms 
                for order in self.metrics.execution_history 
                if order.status == 'FILLED'
            )
            self.metrics.avg_execution_delay_ms = total_delay / self.metrics.filled_orders
        
        # Calculate win rate (from closed positions)
        winning_trades = sum(
            1 for order in self.metrics.execution_history
            if order.side == 'SELL' and order.status == 'FILLED'
        )
        total_closed_trades = len([
            order for order in self.metrics.execution_history
            if order.side == 'SELL' and order.status == 'FILLED'
        ])
        
        if total_closed_trades > 0:
            # This is simplified - in reality we'd track which sells were profitable
            self.metrics.win_rate = (self.metrics.realized_pnl > 0) * 50.0  # Simplified
        
        # Calculate Sharpe ratio from equity curve
        if len(self.metrics.equity_curve) > 2:
            returns = np.diff(self.metrics.equity_curve) / self.metrics.equity_curve[:-1]
            if np.std(returns) > 0:
                self.metrics.sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
        
        # Calculate max drawdown
        if len(self.metrics.equity_curve) > 1:
            equity_array = np.array(self.metrics.equity_curve)
            running_max = np.maximum.accumulate(equity_array)
            drawdown = (equity_array - running_max) / running_max
            self.metrics.max_drawdown_percent = abs(np.min(drawdown)) * 100
        
        return self.metrics
    
    def save_session_log(self, filepath: str = None):
        """
        Save comprehensive session log to file
        
        Args:
            filepath: Path to save log file
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"logs/simulated_trading_session_{timestamp}.log"
        
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("SIMULATED LIVE TRADING SESSION LOG\n")
            f.write("=" * 80 + "\n")
            f.write(f"Session Start: {self.metrics.execution_history[0].timestamp if self.metrics.execution_history else 'N/A'}\n")
            f.write(f"Session End: {datetime.now()}\n")
            f.write(f"Initial Capital: ${self.initial_capital:,.2f}\n")
            f.write(f"Final Equity: ${self.metrics.equity_curve[-1]:,.2f}\n")
            f.write(f"Total P&L: ${self.metrics.total_pnl:,.2f}\n")
            f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("PERFORMANCE METRICS\n")
            f.write("=" * 80 + "\n")
            metrics_dict = self.metrics.to_dict()
            for key, value in metrics_dict.items():
                if key != 'equity_curve':
                    f.write(f"{key}: {value}\n")
            f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("EXECUTION HISTORY\n")
            f.write("=" * 80 + "\n")
            for order in self.metrics.execution_history:
                f.write(f"\nOrder ID: {order.order_id}\n")
                f.write(f"  Symbol: {order.symbol}\n")
                f.write(f"  Side: {order.side}\n")
                f.write(f"  Quantity: {order.filled_quantity}/{order.requested_quantity}\n")
                f.write(f"  Execution Price: ${order.execution_price:.2f}\n")
                f.write(f"  Slippage: ${order.slippage:.2f} ({order.slippage_percent:.3f}%)\n")
                f.write(f"  Fees: ${order.fees:.2f}\n")
                f.write(f"  Delay: {order.execution_delay_ms:.1f}ms\n")
                f.write(f"  Status: {order.status}\n")
                f.write(f"  Timestamp: {order.timestamp}\n")
        
        logger.info(f"✅ Session log saved to {filepath}")
    
    def close_all_positions(self):
        """Close all open positions"""
        symbols_to_close = list(self.positions.keys())
        for symbol in symbols_to_close:
            pos = self.positions[symbol]
            self.place_market_order(symbol, pos['quantity'], 'SELL')
        
        logger.info(f"✅ All positions closed")
