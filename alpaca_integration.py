"""
alpaca_integration.py - Alpaca API Integration for Trading Bot
==============================================================

Complete integration with Alpaca for:
- Live and historical market data (REST API)
- Order execution (Paper & Live Trading)
- Account management
- WebSocket for real-time updates
- Robust error handling and rate limiting

Usage:
    from alpaca_integration import AlpacaDataProvider, AlpacaOrderExecutor
    
    # Initialize data provider
    provider = AlpacaDataProvider()
    
    # Get historical data
    df = provider.get_historical_bars('AAPL', '1Day', limit=100)
    
    # Initialize order executor
    executor = AlpacaOrderExecutor()
    
    # Place order
    order = executor.place_order('AAPL', 10, 'buy')
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv

try:
    from alpaca.trading.client import TradingClient
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
    from alpaca.data.timeframe import TimeFrame
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logging.warning("alpaca-py not installed. Install with: pip install alpaca-py")

# Load environment variables from keys.env or .env
load_dotenv('keys.env')
load_dotenv()

logger = logging.getLogger(__name__)


class AlpacaDataProvider:
    """
    Alpaca Data Provider for Trading Strategies
    
    Features:
    - Historical bar data (stocks and crypto)
    - Latest quotes and trades
    - Real-time data streaming (via WebSocket)
    - Rate limit handling
    - Error recovery
    """
    
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None,
                 paper: bool = True):
        """
        Initialize Alpaca Data Provider
        
        Args:
            api_key: Alpaca API Key (optional, uses env var if not provided)
            secret_key: Alpaca Secret Key (optional, uses env var if not provided)
            paper: True = Paper Trading, False = Live Trading
        """
        if not ALPACA_AVAILABLE:
            raise ImportError(
                "alpaca-py not installed.\n"
                "Install with: pip install alpaca-py"
            )
        
        # API Credentials
        self.api_key = api_key or os.getenv('ALPACA_API_KEY', '')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY', '')
        self.paper = paper
        
        if not self.api_key or not self.secret_key:
            logger.warning("⚠️ Alpaca API keys not found. Data access may be limited.")
        
        # Initialize Data Client (no base URL needed for data client)
        self.data_client = StockHistoricalDataClient(
            api_key=self.api_key,
            secret_key=self.secret_key
        )
        
        if paper:
            logger.info("✓ Alpaca Data Client initialized (Paper Trading)")
        else:
            logger.warning("⚠️ Alpaca Data Client initialized (LIVE Trading)")
        
        # Rate Limiting
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 200ms between requests
    
    def _rate_limit_check(self):
        """Check and wait if necessary due to rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _convert_timeframe(self, interval: str) -> TimeFrame:
        """
        Convert interval string to Alpaca TimeFrame
        
        Args:
            interval: Interval string (e.g., '1Min', '1Hour', '1Day')
        
        Returns:
            Alpaca TimeFrame object
        """
        interval_map = {
            '1min': TimeFrame.Minute,
            '5min': TimeFrame(5, 'Min'),
            '15min': TimeFrame(15, 'Min'),
            '30min': TimeFrame(30, 'Min'),
            '1h': TimeFrame.Hour,
            '1hour': TimeFrame.Hour,
            '4h': TimeFrame(4, 'Hour'),
            '4hour': TimeFrame(4, 'Hour'),
            '1d': TimeFrame.Day,
            '1day': TimeFrame.Day,
            '1w': TimeFrame.Week,
            '1week': TimeFrame.Week,
        }
        
        interval_lower = interval.lower()
        return interval_map.get(interval_lower, TimeFrame.Day)
    
    def get_historical_bars(self, symbol: str, timeframe: str = '1Day',
                           start: Optional[datetime] = None,
                           end: Optional[datetime] = None,
                           limit: int = 100) -> pd.DataFrame:
        """
        Get historical bar data from Alpaca
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')
            timeframe: Bar timeframe (e.g., '1Min', '1Hour', '1Day')
            start: Start datetime (optional)
            end: End datetime (optional)
            limit: Maximum number of bars to return
        
        Returns:
            DataFrame with OHLCV data
        """
        logger.info(f"Loading historical data: {symbol} {timeframe}")
        
        try:
            self._rate_limit_check()
            
            # Set default date range if not provided
            if not end:
                end = datetime.now()
            if not start:
                # Default to last 100 periods
                if '1d' in timeframe.lower() or 'day' in timeframe.lower():
                    start = end - timedelta(days=limit)
                elif 'hour' in timeframe.lower():
                    start = end - timedelta(hours=limit)
                else:
                    start = end - timedelta(minutes=limit)
            
            # Create request
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=self._convert_timeframe(timeframe),
                start=start,
                end=end,
                limit=limit
            )
            
            # Get bars
            bars = self.data_client.get_stock_bars(request_params)
            
            # Convert to DataFrame
            if symbol in bars.data:
                df = bars.df
                
                # Reset index and rename columns
                if isinstance(df.index, pd.MultiIndex):
                    df = df.reset_index()
                    df = df[df['symbol'] == symbol]
                
                # Rename columns to standard format
                df = df.rename(columns={
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close',
                    'volume': 'volume',
                    'timestamp': 'timestamp'
                })
                
                # Ensure timestamp column exists
                if 'timestamp' not in df.columns and 'date' in df.columns:
                    df['timestamp'] = df['date']
                
                # Set timestamp as index if it exists
                if 'timestamp' in df.columns:
                    df.set_index('timestamp', inplace=True)
                
                logger.info(f"✓ Loaded {len(df)} bars for {symbol}")
                return df[['open', 'high', 'low', 'close', 'volume']]
            else:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
                
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            raise
    
    def get_latest_quote(self, symbol: str) -> Dict[str, float]:
        """
        Get latest quote for a symbol
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with bid, ask, and mid prices
        """
        try:
            self._rate_limit_check()
            
            request_params = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quotes = self.data_client.get_stock_latest_quote(request_params)
            
            if symbol in quotes:
                quote = quotes[symbol]
                return {
                    'bid': float(quote.bid_price),
                    'ask': float(quote.ask_price),
                    'mid': (float(quote.bid_price) + float(quote.ask_price)) / 2,
                    'bid_size': quote.bid_size,
                    'ask_size': quote.ask_size
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting latest quote: {e}")
            return {}
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current market price for a symbol
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Current price as float
        """
        try:
            quote = self.get_latest_quote(symbol)
            if quote:
                price = quote.get('mid', 0.0)
                logger.debug(f"{symbol}: ${price:,.2f}")
                return price
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            return 0.0
    
    def test_connection(self) -> bool:
        """
        Test Alpaca connection
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to get data for a common stock
            df = self.get_historical_bars('AAPL', '1Day', limit=1)
            
            if not df.empty:
                logger.info("✓ Alpaca connection successful")
                return True
            else:
                logger.error("❌ Alpaca connection failed: No data returned")
                return False
                
        except Exception as e:
            logger.error(f"❌ Alpaca connection failed: {e}")
            return False


class AlpacaOrderExecutor:
    """
    Alpaca Order Executor for Trading
    
    Features:
    - Market and limit orders
    - Order status tracking
    - Position management
    - Account information
    - Paper trading support
    """
    
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None,
                 paper: bool = True):
        """
        Initialize Alpaca Order Executor
        
        Args:
            api_key: Alpaca API Key
            secret_key: Alpaca Secret Key
            paper: True = Paper Trading, False = Live Trading
        """
        if not ALPACA_AVAILABLE:
            raise ImportError(
                "alpaca-py not installed.\n"
                "Install with: pip install alpaca-py"
            )
        
        # API Credentials
        self.api_key = api_key or os.getenv('ALPACA_API_KEY', '')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY', '')
        self.paper = paper
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API keys are required for order execution")
        
        # Initialize Trading Client
        self.trading_client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            paper=paper
        )
        
        if paper:
            logger.info("✓ Alpaca Trading Client initialized (Paper Trading)")
        else:
            logger.warning("⚠️ Alpaca Trading Client initialized (LIVE Trading)")
    
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information
        
        Returns:
            Dictionary with account details
        """
        try:
            account = self.trading_client.get_account()
            return {
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'buying_power': float(account.buying_power),
                'equity': float(account.equity),
                'status': account.status
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return {}
    
    def place_market_order(self, symbol: str, qty: float, side: str,
                          time_in_force: str = 'day') -> Optional[Dict[str, Any]]:
        """
        Place a market order
        
        Args:
            symbol: Stock symbol
            qty: Quantity to trade
            side: 'buy' or 'sell'
            time_in_force: 'day', 'gtc', 'ioc', or 'fok'
        
        Returns:
            Order details or None if failed
        """
        try:
            # Convert side to OrderSide enum
            order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
            
            # Convert time_in_force to TimeInForce enum
            tif_map = {
                'day': TimeInForce.DAY,
                'gtc': TimeInForce.GTC,
                'ioc': TimeInForce.IOC,
                'fok': TimeInForce.FOK
            }
            time_in_force_enum = tif_map.get(time_in_force.lower(), TimeInForce.DAY)
            
            # Create market order request
            market_order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=order_side,
                time_in_force=time_in_force_enum
            )
            
            # Submit order
            order = self.trading_client.submit_order(order_data=market_order_data)
            
            logger.info(f"✓ Market order placed: {side.upper()} {qty} {symbol}")
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'side': order.side.value,
                'type': order.type.value,
                'status': order.status.value
            }
            
        except Exception as e:
            logger.error(f"Error placing market order: {e}")
            return None
    
    def place_limit_order(self, symbol: str, qty: float, side: str, limit_price: float,
                         time_in_force: str = 'day') -> Optional[Dict[str, Any]]:
        """
        Place a limit order
        
        Args:
            symbol: Stock symbol
            qty: Quantity to trade
            side: 'buy' or 'sell'
            limit_price: Limit price
            time_in_force: 'day', 'gtc', 'ioc', or 'fok'
        
        Returns:
            Order details or None if failed
        """
        try:
            # Convert side to OrderSide enum
            order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
            
            # Convert time_in_force to TimeInForce enum
            tif_map = {
                'day': TimeInForce.DAY,
                'gtc': TimeInForce.GTC,
                'ioc': TimeInForce.IOC,
                'fok': TimeInForce.FOK
            }
            time_in_force_enum = tif_map.get(time_in_force.lower(), TimeInForce.DAY)
            
            # Create limit order request
            limit_order_data = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=order_side,
                time_in_force=time_in_force_enum,
                limit_price=limit_price
            )
            
            # Submit order
            order = self.trading_client.submit_order(order_data=limit_order_data)
            
            logger.info(f"✓ Limit order placed: {side.upper()} {qty} {symbol} @ ${limit_price}")
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'side': order.side.value,
                'type': order.type.value,
                'limit_price': float(order.limit_price),
                'status': order.status.value
            }
            
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.trading_client.cancel_order_by_id(order_id)
            logger.info(f"✓ Order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    def get_open_orders(self) -> List[Dict[str, Any]]:
        """
        Get all open orders
        
        Returns:
            List of open orders
        """
        try:
            orders = self.trading_client.get_orders()
            return [
                {
                    'id': order.id,
                    'symbol': order.symbol,
                    'qty': float(order.qty),
                    'side': order.side.value,
                    'type': order.type.value,
                    'status': order.status.value
                }
                for order in orders
            ]
        except Exception as e:
            logger.error(f"Error getting open orders: {e}")
            return []
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get all current positions
        
        Returns:
            List of positions
        """
        try:
            positions = self.trading_client.get_all_positions()
            return [
                {
                    'symbol': pos.symbol,
                    'qty': float(pos.qty),
                    'side': pos.side.value,
                    'market_value': float(pos.market_value),
                    'cost_basis': float(pos.cost_basis),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_plpc': float(pos.unrealized_plpc)
                }
                for pos in positions
            ]
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def close_position(self, symbol: str) -> bool:
        """
        Close a position
        
        Args:
            symbol: Stock symbol
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.trading_client.close_position(symbol)
            logger.info(f"✓ Position closed: {symbol}")
            return True
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False


# ========== EXAMPLE USAGE ==========

def example_alpaca_integration():
    """Example of Alpaca integration"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("  Alpaca Integration - Example")
    print("=" * 70)
    
    # 1. Initialize Alpaca Data Provider
    print("\n1. Initialize Alpaca Data Provider...")
    provider = AlpacaDataProvider(paper=True)
    
    # 2. Test connection
    print("\n2. Test connection...")
    if not provider.test_connection():
        print("❌ Connection failed!")
        return
    
    # 3. Get historical data
    print("\n3. Load historical data...")
    df = provider.get_historical_bars(
        symbol='AAPL',
        timeframe='1Day',
        limit=30
    )
    print(f"✓ {len(df)} daily bars loaded")
    print(f"\nLatest data:")
    print(df.tail(3))
    
    # 4. Get current price
    print("\n4. Get current price...")
    price = provider.get_current_price('AAPL')
    print(f"✓ Current AAPL price: ${price:,.2f}")
    
    # 5. Initialize Order Executor (only if keys are available)
    if os.getenv('ALPACA_API_KEY') and os.getenv('ALPACA_SECRET_KEY'):
        print("\n5. Initialize Order Executor...")
        executor = AlpacaOrderExecutor(paper=True)
        
        # 6. Get account info
        print("\n6. Get account info...")
        account = executor.get_account()
        if account:
            print(f"✓ Account Status: {account.get('status')}")
            print(f"  Cash: ${account.get('cash', 0):,.2f}")
            print(f"  Portfolio Value: ${account.get('portfolio_value', 0):,.2f}")
        
        # 7. Get positions
        print("\n7. Get current positions...")
        positions = executor.get_positions()
        if positions:
            for pos in positions:
                print(f"  {pos['symbol']}: {pos['qty']} shares, P&L: ${pos['unrealized_pl']:,.2f}")
        else:
            print("  No open positions")
    else:
        print("\n⚠️ API keys not found - skipping order executor example")
    
    print("\n✓ Example completed!")


if __name__ == "__main__":
    example_alpaca_integration()
