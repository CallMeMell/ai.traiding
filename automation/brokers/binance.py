"""
binance.py - Binance Testnet Adapter
===================================
Binance Testnet adapter for paper trading and testing.

Features:
- Testnet-only operations (safe for testing)
- Health check functionality
- Dry-run order simulation
- API key handling from environment variables
- No hardcoded credentials
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

# Import from system adapters
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from system.adapters.base_adapter import BaseAdapter, AdapterStatus, OrderSide, OrderType

try:
    from binance.client import Client
    from binance.exceptions import BinanceAPIException
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False
    Client = None
    BinanceAPIException = Exception

logger = logging.getLogger(__name__)


class BinanceTestnetClient(BaseAdapter):
    """
    Binance Testnet Adapter for Paper Trading
    
    This adapter connects to Binance Testnet for safe testing and development.
    All operations are performed on the testnet, no real money is involved.
    
    Features:
    - Testnet connection only
    - Health check functionality
    - Dry-run order placement
    - API key loading from environment
    """
    
    def __init__(self, api_key: Optional[str] = None, 
                 api_secret: Optional[str] = None,
                 testnet: bool = True):
        """
        Initialize Binance Testnet Client.
        
        Args:
            api_key: Binance API key (loaded from env if not provided)
            api_secret: Binance API secret (loaded from env if not provided)
            testnet: Always True for this adapter (safety feature)
        
        Note:
            API keys are loaded from environment variables:
            - BINANCE_API_KEY or BINANCE_TESTNET_API_KEY
            - BINANCE_SECRET_KEY or BINANCE_TESTNET_SECRET_KEY
        """
        # Force testnet mode for safety
        super().__init__(api_key, api_secret, testnet=True)
        
        if not BINANCE_AVAILABLE:
            raise ImportError(
                "python-binance not installed.\n"
                "Install with: pip install python-binance"
            )
        
        # Load API keys from environment if not provided
        self.api_key = api_key or os.getenv('BINANCE_TESTNET_API_KEY') or os.getenv('BINANCE_API_KEY')
        self.api_secret = api_secret or os.getenv('BINANCE_TESTNET_SECRET_KEY') or os.getenv('BINANCE_SECRET_KEY')
        
        # Client will be initialized on connect
        self._client: Optional[Client] = None
        
        logger.info("✓ BinanceTestnetClient initialized (testnet mode)")
    
    def connect(self) -> bool:
        """
        Connect to Binance Testnet.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.status = AdapterStatus.CONNECTING
            logger.info("Connecting to Binance Testnet...")
            
            # Initialize Binance client for testnet
            self._client = Client(
                api_key=self.api_key or '',
                api_secret=self.api_secret or '',
                testnet=True
            )
            
            # Test connection with ping
            self._client.ping()
            
            self.status = AdapterStatus.CONNECTED
            logger.info("✓ Connected to Binance Testnet")
            
            # If API keys provided, validate them
            if self.api_key and self.api_secret:
                try:
                    account = self._client.get_account()
                    logger.info(f"✓ API keys validated (Account type: {account.get('accountType', 'N/A')})")
                except BinanceAPIException as e:
                    logger.warning(f"⚠️ API key validation failed: {e}")
                    logger.info("Public API operations will still work")
            
            return True
            
        except Exception as e:
            self.status = AdapterStatus.ERROR
            logger.error(f"❌ Failed to connect to Binance Testnet: {e}")
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from Binance Testnet.
        
        Returns:
            True if disconnection successful
        """
        try:
            self._client = None
            self.status = AdapterStatus.DISCONNECTED
            logger.info("✓ Disconnected from Binance Testnet")
            return True
        except Exception as e:
            logger.error(f"❌ Error during disconnect: {e}")
            return False
    
    def health_check(self) -> bool:
        """
        Perform health check on Binance Testnet connection.
        
        This checks:
        - Connection status
        - API server availability (ping)
        - System status
        
        Returns:
            True if all checks pass, False otherwise
        """
        try:
            # Check if connected
            if self.status != AdapterStatus.CONNECTED or self._client is None:
                logger.warning("❌ Health check failed: Not connected")
                return False
            
            # Ping the server
            self._client.ping()
            logger.debug("✓ Health check: Ping successful")
            
            # Check system status
            status = self._client.get_system_status()
            if status.get('status') != 0:
                logger.warning(f"⚠️ Health check: System status abnormal: {status}")
                return False
            
            logger.info("✓ Health check passed")
            return True
            
        except BinanceAPIException as e:
            logger.error(f"❌ Health check failed (API error): {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    def get_account_balance(self) -> Dict[str, Any]:
        """
        Get account balance from Binance Testnet.
        
        Returns:
            Dictionary with balance information
        """
        try:
            if self.status != AdapterStatus.CONNECTED or self._client is None:
                raise RuntimeError("Not connected to Binance Testnet")
            
            account = self._client.get_account()
            balances = account.get('balances', [])
            
            # Calculate total balance in USDT equivalent (simplified)
            total_balance = 0.0
            available_balance = 0.0
            
            for balance in balances:
                free = float(balance.get('free', 0))
                locked = float(balance.get('locked', 0))
                
                if balance.get('asset') == 'USDT':
                    total_balance += free + locked
                    available_balance += free
            
            return {
                'total': total_balance,
                'available': available_balance,
                'currency': 'USDT',
                'balances': balances
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get account balance: {e}")
            return {'total': 0.0, 'available': 0.0, 'currency': 'USDT', 'error': str(e)}
    
    def get_market_price(self, symbol: str) -> float:
        """
        Get current market price for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            
        Returns:
            Current market price
        """
        try:
            if self.status != AdapterStatus.CONNECTED or self._client is None:
                raise RuntimeError("Not connected to Binance Testnet")
            
            ticker = self._client.get_symbol_ticker(symbol=symbol)
            price = float(ticker.get('price', 0))
            
            logger.debug(f"Current price for {symbol}: {price}")
            return price
            
        except Exception as e:
            logger.error(f"❌ Failed to get market price for {symbol}: {e}")
            return 0.0
    
    def place_order(self, symbol: str, side: OrderSide, 
                   order_type: OrderType, quantity: float,
                   price: Optional[float] = None,
                   stop_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Place a dry-run order (simulated).
        
        This method simulates order placement without actually executing
        the order on the exchange. Perfect for testing and development.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Order side (BUY or SELL)
            order_type: Order type (MARKET, LIMIT, etc.)
            quantity: Order quantity
            price: Limit price (for limit orders)
            stop_price: Stop price (for stop orders)
            
        Returns:
            Simulated order result
        """
        try:
            if self.status != AdapterStatus.CONNECTED or self._client is None:
                raise RuntimeError("Not connected to Binance Testnet")
            
            # DRY-RUN mode: Simulate order without executing
            dry_run_mode = os.getenv('DRY_RUN', 'true').lower() == 'true'
            
            if dry_run_mode:
                # Simulate order execution
                current_price = self.get_market_price(symbol)
                
                order_result = {
                    'order_id': f'DRY_RUN_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                    'symbol': symbol,
                    'side': side.value,
                    'type': order_type.value,
                    'quantity': quantity,
                    'price': price or current_price,
                    'status': 'filled',
                    'executed_qty': quantity,
                    'timestamp': datetime.now().isoformat(),
                    'dry_run': True
                }
                
                logger.info(f"✓ DRY-RUN order placed: {side.value} {quantity} {symbol} @ {price or current_price}")
                return order_result
            else:
                # Real order placement (not recommended for testnet adapter)
                logger.warning("⚠️ Real order placement not recommended with testnet adapter")
                raise RuntimeError("Real order placement disabled for testnet adapter. Use DRY_RUN=true")
            
        except Exception as e:
            logger.error(f"❌ Failed to place order: {e}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get order status (dry-run simulation).
        
        Args:
            order_id: Order ID
            
        Returns:
            Order status information
        """
        # For dry-run orders, return simulated status
        if order_id.startswith('DRY_RUN_'):
            return {
                'order_id': order_id,
                'status': 'filled',
                'dry_run': True
            }
        
        logger.warning(f"⚠️ Cannot query real order status in dry-run mode: {order_id}")
        return {'order_id': order_id, 'status': 'unknown', 'error': 'Dry-run mode'}
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel order (dry-run simulation).
        
        Args:
            order_id: Order ID
            
        Returns:
            True if successful
        """
        # For dry-run orders, simulate cancellation
        if order_id.startswith('DRY_RUN_'):
            logger.info(f"✓ DRY-RUN order cancelled: {order_id}")
            return True
        
        logger.warning(f"⚠️ Cannot cancel real order in dry-run mode: {order_id}")
        return False
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get open orders (dry-run returns empty list).
        
        Args:
            symbol: Filter by symbol (optional)
            
        Returns:
            List of open orders (empty in dry-run mode)
        """
        logger.debug("DRY-RUN mode: No real open orders")
        return []
    
    def get_historical_data(self, symbol: str, interval: str,
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None,
                          limit: int = 500) -> List[Dict[str, Any]]:
        """
        Get historical OHLCV data.
        
        Args:
            symbol: Trading symbol
            interval: Candle interval (e.g., '1h', '1d')
            start_time: Start time
            end_time: End time
            limit: Maximum number of candles
            
        Returns:
            List of OHLCV dictionaries
        """
        try:
            if self.status != AdapterStatus.CONNECTED or self._client is None:
                raise RuntimeError("Not connected to Binance Testnet")
            
            # Get klines data
            klines = self._client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            # Convert to standardized format
            historical_data = []
            for kline in klines:
                historical_data.append({
                    'timestamp': datetime.fromtimestamp(kline[0] / 1000),
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5])
                })
            
            logger.debug(f"✓ Retrieved {len(historical_data)} candles for {symbol}")
            return historical_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get historical data: {e}")
            return []
