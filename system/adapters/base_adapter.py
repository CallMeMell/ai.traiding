"""
base_adapter.py - Base Broker Adapter Interface
==============================================
Abstract base class for broker API adapters.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime


class AdapterStatus(Enum):
    """Adapter connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class OrderType(Enum):
    """Order types."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Order side."""
    BUY = "buy"
    SELL = "sell"


class BaseAdapter(ABC):
    """
    Abstract base class for broker API adapters.
    
    All broker integrations must implement this interface.
    """
    
    def __init__(self, api_key: Optional[str] = None, 
                 api_secret: Optional[str] = None,
                 testnet: bool = True):
        """
        Initialize adapter.
        
        Args:
            api_key: API key (optional for testnet)
            api_secret: API secret (optional for testnet)
            testnet: Use testnet environment
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.status = AdapterStatus.DISCONNECTED
        self._connection = None
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to broker API.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from broker API.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_account_balance(self) -> Dict[str, Any]:
        """
        Get account balance.
        
        Returns:
            Dictionary with balance information
        """
        pass
    
    @abstractmethod
    def get_market_price(self, symbol: str) -> float:
        """
        Get current market price for symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            
        Returns:
            Current price
        """
        pass
    
    @abstractmethod
    def place_order(self, symbol: str, side: OrderSide, 
                   order_type: OrderType, quantity: float,
                   price: Optional[float] = None,
                   stop_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Place an order.
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            order_type: Order type
            quantity: Order quantity
            price: Limit price (for limit orders)
            stop_price: Stop price (for stop orders)
            
        Returns:
            Order result dictionary
        """
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get order status.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order status dictionary
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get open orders.
        
        Args:
            symbol: Filter by symbol (optional)
            
        Returns:
            List of open orders
        """
        pass
    
    @abstractmethod
    def get_historical_data(self, symbol: str, interval: str,
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None,
                          limit: int = 500) -> List[Dict[str, Any]]:
        """
        Get historical OHLCV data.
        
        Args:
            symbol: Trading symbol
            interval: Candle interval (e.g., '1h', '1d')
            start_time: Start time (optional)
            end_time: End time (optional)
            limit: Maximum number of candles
            
        Returns:
            List of OHLCV dictionaries
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if adapter is healthy and connected.
        
        Returns:
            True if healthy, False otherwise
        """
        pass
    
    def get_adapter_info(self) -> Dict[str, Any]:
        """
        Get adapter information.
        
        Returns:
            Adapter information dictionary
        """
        return {
            'name': self.__class__.__name__,
            'status': self.status.value,
            'testnet': self.testnet,
            'connected': self.status == AdapterStatus.CONNECTED
        }
