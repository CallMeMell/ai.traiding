"""
broker_api.py - Unified Broker API Integration
===============================================

Provides a unified interface for interacting with different broker APIs
(Binance, Interactive Brokers, Alpaca, etc.) for automated trading.

Features:
- Standardized interface for all broker operations
- Support for market and limit orders
- Order cancellation and tracking
- Account balance and position management
- Comprehensive logging for all actions
- Support for paper trading and live trading

Usage:
    from broker_api import BrokerFactory
    
    # Create broker instance
    broker = BrokerFactory.create_broker('binance', paper_trading=True)
    
    # Place order
    order = broker.place_market_order('BTCUSDT', 0.01, 'BUY')
    
    # Get account balance
    balance = broker.get_account_balance()
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"


class OrderSide(Enum):
    """Order side enumeration"""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    """Order status enumeration"""
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    PENDING_CANCEL = "PENDING_CANCEL"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class BrokerInterface(ABC):
    """
    Abstract base class for broker integration
    
    All broker implementations must inherit from this class and implement
    the required methods to ensure consistency across different brokers.
    """
    
    def __init__(self, api_key: Optional[str] = None, 
                 api_secret: Optional[str] = None,
                 paper_trading: bool = True):
        """
        Initialize broker interface
        
        Args:
            api_key: API key for broker
            api_secret: API secret for broker
            paper_trading: True for paper trading, False for live trading
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.paper_trading = paper_trading
        self._initialized = False
        
    @abstractmethod
    def place_market_order(self, symbol: str, quantity: float, 
                          side: str, **kwargs) -> Dict[str, Any]:
        """
        Place a market order
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT', 'AAPL')
            quantity: Order quantity
            side: Order side ('BUY' or 'SELL')
            **kwargs: Additional broker-specific parameters
        
        Returns:
            Dictionary with order details including:
            - order_id: Unique order identifier
            - symbol: Trading symbol
            - quantity: Order quantity
            - side: Order side
            - status: Order status
            - filled_quantity: Quantity filled
            - avg_price: Average fill price
            - timestamp: Order timestamp
        """
        pass
    
    @abstractmethod
    def place_limit_order(self, symbol: str, quantity: float, 
                         side: str, price: float, **kwargs) -> Dict[str, Any]:
        """
        Place a limit order
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: Order side ('BUY' or 'SELL')
            price: Limit price
            **kwargs: Additional broker-specific parameters
        
        Returns:
            Dictionary with order details (same format as place_market_order)
        """
        pass
    
    @abstractmethod
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """
        Cancel an open order
        
        Args:
            symbol: Trading symbol
            order_id: Order ID to cancel
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """
        Get order status
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
        
        Returns:
            Dictionary with order details
        """
        pass
    
    @abstractmethod
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open orders
        
        Args:
            symbol: Trading symbol (optional, if None returns all open orders)
        
        Returns:
            List of open orders
        """
        pass
    
    @abstractmethod
    def get_account_balance(self, asset: Optional[str] = None) -> Dict[str, float]:
        """
        Get account balance
        
        Args:
            asset: Asset symbol (e.g., 'USDT', 'BTC'). If None, returns all balances
        
        Returns:
            Dictionary with asset balances:
            - For single asset: {'free': float, 'locked': float, 'total': float}
            - For all assets: {asset: {'free': float, 'locked': float, 'total': float}}
        """
        pass
    
    @abstractmethod
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get open positions
        
        Args:
            symbol: Trading symbol (optional)
        
        Returns:
            List of positions with details:
            - symbol: Trading symbol
            - quantity: Position size
            - entry_price: Average entry price
            - current_price: Current market price
            - unrealized_pnl: Unrealized profit/loss
            - side: Position side ('LONG' or 'SHORT')
        """
        pass
    
    @abstractmethod
    def close_position(self, symbol: str) -> bool:
        """
        Close an open position
        
        Args:
            symbol: Trading symbol
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def log_action(self, action: str, details: Dict[str, Any]):
        """
        Log broker action
        
        Args:
            action: Action description
            details: Action details
        """
        logger.info(f"🔄 BROKER ACTION: {action}")
        for key, value in details.items():
            logger.info(f"  {key}: {value}")


class BinanceOrderExecutor(BrokerInterface):
    """
    Binance Order Executor for Live Trading
    
    Implements real order execution on Binance exchange using Binance API.
    Supports both testnet (paper trading) and production trading.
    """
    
    def __init__(self, api_key: Optional[str] = None, 
                 api_secret: Optional[str] = None,
                 paper_trading: bool = True):
        """
        Initialize Binance Order Executor
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            paper_trading: True for testnet, False for production
        """
        super().__init__(api_key, api_secret, paper_trading)
        
        try:
            from binance.client import Client
            from binance.exceptions import BinanceAPIException
            self.Client = Client
            self.BinanceAPIException = BinanceAPIException
        except ImportError:
            raise ImportError(
                "python-binance not installed.\n"
                "Install with: pip install python-binance"
            )
        
        if not api_key or not api_secret:
            raise ValueError("API key and secret are required for Binance order execution")
        
        # Initialize Binance client
        self.client = Client(
            api_key=api_key,
            api_secret=api_secret,
            testnet=paper_trading
        )
        
        mode = "TESTNET (Paper Trading)" if paper_trading else "PRODUCTION (Live Trading)"
        logger.info(f"✓ Binance Order Executor initialized: {mode}")
        self.log_action("INITIALIZED", {
            "broker": "Binance",
            "mode": mode,
            "timestamp": datetime.now().isoformat()
        })
        
        self._initialized = True
    
    def place_market_order(self, symbol: str, quantity: float, 
                          side: str, **kwargs) -> Dict[str, Any]:
        """Place a market order on Binance"""
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        try:
            # Place order
            order = self.client.create_order(
                symbol=symbol,
                side=side.upper(),
                type='MARKET',
                quantity=quantity,
                **kwargs
            )
            
            # Extract order details
            result = {
                'order_id': order['orderId'],
                'symbol': order['symbol'],
                'quantity': float(order['origQty']),
                'side': order['side'],
                'type': order['type'],
                'status': order['status'],
                'filled_quantity': float(order.get('executedQty', 0)),
                'avg_price': float(order.get('price', 0)) if order.get('price') else 0,
                'timestamp': datetime.fromtimestamp(order['transactTime'] / 1000).isoformat(),
                'raw_response': order
            }
            
            self.log_action("MARKET_ORDER_PLACED", {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "order_id": result['order_id'],
                "status": result['status']
            })
            
            logger.info(f"✓ Market order placed: {side} {quantity} {symbol}")
            return result
            
        except self.BinanceAPIException as e:
            logger.error(f"❌ Binance API error placing market order: {e}")
            self.log_action("MARKET_ORDER_FAILED", {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "error": str(e)
            })
            raise
        except Exception as e:
            logger.error(f"❌ Error placing market order: {e}")
            raise
    
    def place_limit_order(self, symbol: str, quantity: float, 
                         side: str, price: float, **kwargs) -> Dict[str, Any]:
        """Place a limit order on Binance"""
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        try:
            # Place order
            order = self.client.create_order(
                symbol=symbol,
                side=side.upper(),
                type='LIMIT',
                quantity=quantity,
                price=price,
                timeInForce=kwargs.get('timeInForce', 'GTC'),
                **{k: v for k, v in kwargs.items() if k != 'timeInForce'}
            )
            
            # Extract order details
            result = {
                'order_id': order['orderId'],
                'symbol': order['symbol'],
                'quantity': float(order['origQty']),
                'side': order['side'],
                'type': order['type'],
                'price': float(order['price']),
                'status': order['status'],
                'filled_quantity': float(order.get('executedQty', 0)),
                'avg_price': float(order.get('price', 0)) if order.get('price') else 0,
                'timestamp': datetime.fromtimestamp(order['transactTime'] / 1000).isoformat(),
                'raw_response': order
            }
            
            self.log_action("LIMIT_ORDER_PLACED", {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "price": price,
                "order_id": result['order_id'],
                "status": result['status']
            })
            
            logger.info(f"✓ Limit order placed: {side} {quantity} {symbol} @ ${price}")
            return result
            
        except self.BinanceAPIException as e:
            logger.error(f"❌ Binance API error placing limit order: {e}")
            self.log_action("LIMIT_ORDER_FAILED", {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "price": price,
                "error": str(e)
            })
            raise
        except Exception as e:
            logger.error(f"❌ Error placing limit order: {e}")
            raise
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an order on Binance"""
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        try:
            self.client.cancel_order(symbol=symbol, orderId=order_id)
            
            self.log_action("ORDER_CANCELED", {
                "symbol": symbol,
                "order_id": order_id,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"✓ Order canceled: {order_id}")
            return True
            
        except self.BinanceAPIException as e:
            logger.error(f"❌ Error canceling order: {e}")
            self.log_action("ORDER_CANCEL_FAILED", {
                "symbol": symbol,
                "order_id": order_id,
                "error": str(e)
            })
            return False
        except Exception as e:
            logger.error(f"❌ Error canceling order: {e}")
            return False
    
    def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Get order status from Binance"""
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        try:
            order = self.client.get_order(symbol=symbol, orderId=order_id)
            
            return {
                'order_id': order['orderId'],
                'symbol': order['symbol'],
                'quantity': float(order['origQty']),
                'side': order['side'],
                'type': order['type'],
                'price': float(order.get('price', 0)),
                'status': order['status'],
                'filled_quantity': float(order.get('executedQty', 0)),
                'avg_price': float(order.get('price', 0)) if order.get('price') else 0,
                'timestamp': datetime.fromtimestamp(order['time'] / 1000).isoformat()
            }
            
        except self.BinanceAPIException as e:
            logger.error(f"❌ Error getting order status: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error getting order status: {e}")
            raise
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get open orders from Binance"""
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        try:
            if symbol:
                orders = self.client.get_open_orders(symbol=symbol)
            else:
                orders = self.client.get_open_orders()
            
            return [
                {
                    'order_id': order['orderId'],
                    'symbol': order['symbol'],
                    'quantity': float(order['origQty']),
                    'side': order['side'],
                    'type': order['type'],
                    'price': float(order.get('price', 0)),
                    'status': order['status'],
                    'filled_quantity': float(order.get('executedQty', 0))
                }
                for order in orders
            ]
            
        except self.BinanceAPIException as e:
            logger.error(f"❌ Error getting open orders: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting open orders: {e}")
            return []
    
    def get_account_balance(self, asset: Optional[str] = None) -> Dict[str, float]:
        """Get account balance from Binance"""
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        try:
            account = self.client.get_account()
            
            if asset:
                # Return balance for specific asset
                for balance in account['balances']:
                    if balance['asset'] == asset:
                        return {
                            'free': float(balance['free']),
                            'locked': float(balance['locked']),
                            'total': float(balance['free']) + float(balance['locked'])
                        }
                return {'free': 0.0, 'locked': 0.0, 'total': 0.0}
            else:
                # Return all balances
                result = {}
                for balance in account['balances']:
                    total = float(balance['free']) + float(balance['locked'])
                    if total > 0:  # Only include non-zero balances
                        result[balance['asset']] = {
                            'free': float(balance['free']),
                            'locked': float(balance['locked']),
                            'total': total
                        }
                return result
                
        except self.BinanceAPIException as e:
            logger.error(f"❌ Error getting account balance: {e}")
            return {}
        except Exception as e:
            logger.error(f"❌ Error getting account balance: {e}")
            return {}
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get open positions from Binance
        
        Note: Binance Spot doesn't have positions in the traditional sense.
        This returns current holdings as positions.
        """
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        try:
            account = self.client.get_account()
            positions = []
            
            for balance in account['balances']:
                qty = float(balance['free']) + float(balance['locked'])
                if qty > 0:
                    asset = balance['asset']
                    
                    # Skip if symbol filter is specified and doesn't match
                    if symbol and not asset in symbol:
                        continue
                    
                    positions.append({
                        'symbol': asset,
                        'quantity': qty,
                        'free': float(balance['free']),
                        'locked': float(balance['locked'])
                    })
            
            return positions
            
        except self.BinanceAPIException as e:
            logger.error(f"❌ Error getting positions: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting positions: {e}")
            return []
    
    def close_position(self, symbol: str) -> bool:
        """
        Close a position by selling all holdings
        
        For Binance Spot, this means selling all of the base asset.
        """
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        try:
            # Get current balance of the asset
            positions = self.get_positions(symbol=symbol)
            
            if not positions:
                logger.warning(f"No position found for {symbol}")
                return False
            
            # For spot trading, sell all of the base asset
            for position in positions:
                if position['free'] > 0:
                    # Place market sell order
                    self.place_market_order(
                        symbol=symbol,
                        quantity=position['free'],
                        side='SELL'
                    )
            
            self.log_action("POSITION_CLOSED", {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"✓ Position closed: {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error closing position: {e}")
            return False


class EnhancedPaperTradingExecutor(BrokerInterface):
    """
    Enhanced Paper Trading Executor with full broker interface
    
    Simulates trading without real money, implementing all broker
    interface methods for testing and development.
    """
    
    def __init__(self, initial_capital: float = 10000.0,
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 paper_trading: bool = True):
        """
        Initialize Enhanced Paper Trading Executor
        
        Args:
            initial_capital: Starting capital in base currency (USDT)
            api_key: Placeholder (not used for paper trading)
            api_secret: Placeholder (not used for paper trading)
            paper_trading: Always True for paper trading
        """
        super().__init__(api_key, api_secret, True)
        
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.trade_history: List[Dict[str, Any]] = []
        self.next_order_id = 1000
        
        logger.info(f"✓ Paper Trading Executor initialized")
        logger.info(f"  Initial Capital: ${initial_capital:,.2f}")
        
        self.log_action("INITIALIZED", {
            "broker": "Paper Trading",
            "initial_capital": f"${initial_capital:,.2f}",
            "timestamp": datetime.now().isoformat()
        })
        
        self._initialized = True
    
    def _generate_order_id(self) -> str:
        """Generate unique order ID"""
        order_id = f"PAPER_{self.next_order_id}"
        self.next_order_id += 1
        return order_id
    
    def place_market_order(self, symbol: str, quantity: float, 
                          side: str, **kwargs) -> Dict[str, Any]:
        """Simulate market order execution"""
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        # For paper trading, we need a price - use kwargs or simulate
        price = kwargs.get('current_price', 50000.0)  # Default price if not provided
        
        cost = quantity * price
        
        # Check capital for BUY orders
        if side.upper() == 'BUY' and cost > self.capital:
            logger.error(f"❌ Insufficient capital: Need ${cost:.2f}, Have ${self.capital:.2f}")
            raise ValueError(f"Insufficient capital: {self.capital:.2f} < {cost:.2f}")
        
        # Generate order
        order_id = self._generate_order_id()
        
        # Execute order
        if side.upper() == 'BUY':
            self.capital -= cost
            self.positions[symbol] = {
                'quantity': quantity,
                'entry_price': price,
                'entry_time': datetime.now()
            }
        elif side.upper() == 'SELL':
            if symbol not in self.positions:
                raise ValueError(f"No position to sell for {symbol}")
            
            position = self.positions[symbol]
            revenue = quantity * price
            self.capital += revenue
            
            # Record trade
            pnl = revenue - (position['entry_price'] * quantity)
            self.trade_history.append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'side': 'SELL',
                'quantity': quantity,
                'price': price,
                'pnl': pnl
            })
            
            del self.positions[symbol]
        
        result = {
            'order_id': order_id,
            'symbol': symbol,
            'quantity': quantity,
            'side': side.upper(),
            'type': 'MARKET',
            'status': 'FILLED',
            'filled_quantity': quantity,
            'avg_price': price,
            'timestamp': datetime.now().isoformat()
        }
        
        self.orders[order_id] = result
        
        self.log_action("MARKET_ORDER_EXECUTED", {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": f"${price:.2f}",
            "capital_after": f"${self.capital:.2f}"
        })
        
        logger.info(f"✓ Paper market order: {side} {quantity} {symbol} @ ${price:.2f}")
        return result
    
    def place_limit_order(self, symbol: str, quantity: float, 
                         side: str, price: float, **kwargs) -> Dict[str, Any]:
        """Simulate limit order placement"""
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        order_id = self._generate_order_id()
        
        result = {
            'order_id': order_id,
            'symbol': symbol,
            'quantity': quantity,
            'side': side.upper(),
            'type': 'LIMIT',
            'price': price,
            'status': 'NEW',
            'filled_quantity': 0,
            'avg_price': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        self.orders[order_id] = result
        
        self.log_action("LIMIT_ORDER_PLACED", {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": f"${price:.2f}"
        })
        
        logger.info(f"✓ Paper limit order: {side} {quantity} {symbol} @ ${price:.2f}")
        return result
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an order"""
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        if order_id not in self.orders:
            logger.warning(f"Order {order_id} not found")
            return False
        
        order = self.orders[order_id]
        if order['status'] in ['FILLED', 'CANCELED']:
            logger.warning(f"Order {order_id} already {order['status']}")
            return False
        
        order['status'] = 'CANCELED'
        
        self.log_action("ORDER_CANCELED", {
            "order_id": order_id,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"✓ Paper order canceled: {order_id}")
        return True
    
    def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Get order status"""
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        if order_id not in self.orders:
            raise ValueError(f"Order {order_id} not found")
        
        return self.orders[order_id]
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get open orders"""
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        open_orders = [
            order for order in self.orders.values()
            if order['status'] in ['NEW', 'PARTIALLY_FILLED']
        ]
        
        if symbol:
            open_orders = [o for o in open_orders if o['symbol'] == symbol]
        
        return open_orders
    
    def get_account_balance(self, asset: Optional[str] = None) -> Dict[str, float]:
        """Get account balance"""
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        if asset == 'USDT' or asset is None:
            return {
                'free': self.capital,
                'locked': 0.0,
                'total': self.capital
            }
        
        return {'free': 0.0, 'locked': 0.0, 'total': 0.0}
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get open positions"""
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        positions = []
        for sym, pos in self.positions.items():
            if symbol is None or sym == symbol:
                positions.append({
                    'symbol': sym,
                    'quantity': pos['quantity'],
                    'entry_price': pos['entry_price'],
                    'entry_time': pos['entry_time'].isoformat(),
                    'side': 'LONG'
                })
        
        return positions
    
    def close_position(self, symbol: str) -> bool:
        """Close a position"""
        if not self._initialized:
            raise RuntimeError("Broker not initialized")
        
        if symbol not in self.positions:
            logger.warning(f"No position for {symbol}")
            return False
        
        position = self.positions[symbol]
        
        # Simulate market sell at current price
        # In real scenario, we'd get current market price
        current_price = position['entry_price'] * 1.01  # Simulate 1% gain
        
        self.place_market_order(
            symbol=symbol,
            quantity=position['quantity'],
            side='SELL',
            current_price=current_price
        )
        
        self.log_action("POSITION_CLOSED", {
            "symbol": symbol,
            "quantity": position['quantity'],
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"✓ Paper position closed: {symbol}")
        return True


class BrokerFactory:
    """
    Factory class for creating broker instances
    
    Simplifies broker initialization with support for different
    broker types and configurations.
    """
    
    @staticmethod
    def create_broker(broker_type: str, api_key: Optional[str] = None,
                     api_secret: Optional[str] = None,
                     paper_trading: bool = True,
                     **kwargs) -> BrokerInterface:
        """
        Create a broker instance
        
        Args:
            broker_type: Type of broker ('binance', 'paper', etc.)
            api_key: API key for broker
            api_secret: API secret for broker
            paper_trading: True for paper trading, False for live trading
            **kwargs: Additional broker-specific parameters
        
        Returns:
            BrokerInterface instance
        """
        broker_type = broker_type.lower()
        
        if broker_type == 'binance':
            return BinanceOrderExecutor(
                api_key=api_key,
                api_secret=api_secret,
                paper_trading=paper_trading
            )
        elif broker_type == 'paper':
            initial_capital = kwargs.get('initial_capital', 10000.0)
            return EnhancedPaperTradingExecutor(
                initial_capital=initial_capital,
                api_key=api_key,
                api_secret=api_secret,
                paper_trading=True
            )
        else:
            raise ValueError(f"Unsupported broker type: {broker_type}")


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("  Broker API Integration - Example")
    print("=" * 70)
    
    # Example 1: Paper Trading
    print("\n1. Paper Trading Example...")
    paper_broker = BrokerFactory.create_broker('paper', initial_capital=10000)
    
    # Get balance
    balance = paper_broker.get_account_balance('USDT')
    print(f"Balance: ${balance['total']:.2f}")
    
    # Place order
    order = paper_broker.place_market_order('BTCUSDT', 0.1, 'BUY', current_price=50000)
    print(f"Order placed: {order['order_id']}")
    
    # Get positions
    positions = paper_broker.get_positions()
    print(f"Positions: {len(positions)}")
    
    print("\n✓ Example completed!")
