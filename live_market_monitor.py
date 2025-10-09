"""
live_market_monitor.py - Live-Market Monitoring Integration
============================================================

Comprehensive module for real-time market monitoring with:
- Live data fetching from multiple exchanges (Binance, Kraken)
- OHLCV data processing and validation
- Integration with existing trading strategies
- Alert system for price changes and trade signals
- Support for multiple trading pairs and timeframes

Key Features:
- Multi-exchange support (Binance primary, extensible for others)
- Real-time price monitoring with configurable intervals
- Strategy signal detection and alerts
- Price change alerts (absolute and percentage)
- Trade signal alerts based on active strategies
- Comprehensive logging and error handling
"""

import time
import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np

# Import existing components
try:
    from binance_integration import BinanceDataProvider
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False

logger = logging.getLogger(__name__)


class AlertType(Enum):
    """Types of alerts that can be triggered"""
    PRICE_CHANGE = "price_change"
    STRATEGY_SIGNAL = "strategy_signal"
    VOLUME_SPIKE = "volume_spike"
    VOLATILITY = "volatility"
    CUSTOM = "custom"


@dataclass
class Alert:
    """Represents a market alert"""
    alert_type: AlertType
    symbol: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"  # low, normal, high, critical
    
    def __str__(self):
        priority_emoji = {
            "low": "ℹ️",
            "normal": "📢",
            "high": "⚠️",
            "critical": "🚨"
        }
        emoji = priority_emoji.get(self.priority, "📢")
        return f"{emoji} [{self.alert_type.value.upper()}] {self.symbol}: {self.message}"


class MarketDataFetcher:
    """
    Fetches live market data from various exchanges
    
    Primary: Binance (cryptocurrency)
    Future: Kraken, Coinbase, etc.
    """
    
    def __init__(self, exchange: str = "binance", api_key: Optional[str] = None,
                 api_secret: Optional[str] = None, testnet: bool = True):
        """
        Initialize market data fetcher
        
        Args:
            exchange: Exchange name (currently only 'binance' supported)
            api_key: API key for the exchange
            api_secret: API secret for the exchange
            testnet: Use testnet/sandbox environment
        """
        self.exchange = exchange.lower()
        self.testnet = testnet
        self.provider = None
        
        if self.exchange == "binance":
            if not BINANCE_AVAILABLE:
                raise ImportError("Binance integration not available. Install python-binance.")
            
            self.provider = BinanceDataProvider(
                api_key=api_key,
                api_secret=api_secret,
                testnet=testnet
            )
            logger.info(f"✓ MarketDataFetcher initialized with Binance ({'testnet' if testnet else 'live'})")
        else:
            raise ValueError(f"Unsupported exchange: {exchange}")
    
    def fetch_current_price(self, symbol: str) -> Optional[float]:
        """
        Fetch current price for a symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
        
        Returns:
            Current price or None if error
        """
        try:
            if self.provider:
                return self.provider.get_current_price(symbol)
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    def fetch_historical_data(self, symbol: str, interval: str = '15m',
                             limit: int = 500) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            interval: Timeframe (e.g., '1m', '5m', '15m', '1h', '1d')
            limit: Number of candles to fetch
        
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            if self.provider:
                return self.provider.get_historical_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test connection to exchange"""
        try:
            if self.provider:
                return self.provider.test_connection()
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


class DataProcessor:
    """
    Processes OHLCV data for strategy integration
    
    Features:
    - Data validation
    - Indicator calculation
    - Data normalization
    - Historical data management
    """
    
    def __init__(self):
        """Initialize data processor"""
        self.data_cache: Dict[str, pd.DataFrame] = {}
        logger.info("✓ DataProcessor initialized")
    
    def process_ohlcv(self, df: pd.DataFrame, symbol: str) -> Optional[pd.DataFrame]:
        """
        Process and validate OHLCV data
        
        Args:
            df: Raw OHLCV DataFrame
            symbol: Trading pair symbol
        
        Returns:
            Processed DataFrame or None if invalid
        """
        if df is None or df.empty:
            logger.warning(f"Empty data for {symbol}")
            return None
        
        # Validate required columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            logger.error(f"Missing required columns for {symbol}")
            return None
        
        # Validate data integrity
        if not self._validate_ohlcv(df):
            logger.error(f"Invalid OHLCV data for {symbol}")
            return None
        
        # Cache processed data
        self.data_cache[symbol] = df.copy()
        
        return df
    
    def _validate_ohlcv(self, df: pd.DataFrame) -> bool:
        """
        Validate OHLCV data integrity
        
        Args:
            df: OHLCV DataFrame
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check for NaN values
            if df[['open', 'high', 'low', 'close', 'volume']].isnull().any().any():
                logger.warning("Found NaN values in OHLCV data")
                return False
            
            # Check high >= low
            if not (df['high'] >= df['low']).all():
                logger.warning("High price less than low price detected")
                return False
            
            # Check high >= open, close
            if not ((df['high'] >= df['open']) & (df['high'] >= df['close'])).all():
                logger.warning("High price validation failed")
                return False
            
            # Check low <= open, close
            if not ((df['low'] <= df['open']) & (df['low'] <= df['close'])).all():
                logger.warning("Low price validation failed")
                return False
            
            # Check for negative prices
            if (df[['open', 'high', 'low', 'close']] <= 0).any().any():
                logger.warning("Negative or zero prices detected")
                return False
            
            # Check for negative volume
            if (df['volume'] < 0).any():
                logger.warning("Negative volume detected")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    def calculate_price_change(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate price change metrics
        
        Args:
            df: OHLCV DataFrame
        
        Returns:
            Dictionary with change metrics
        """
        if df is None or len(df) < 2:
            return {}
        
        current_price = df['close'].iloc[-1]
        previous_price = df['close'].iloc[-2]
        
        absolute_change = current_price - previous_price
        percent_change = (absolute_change / previous_price) * 100
        
        # Calculate from first to last
        first_price = df['close'].iloc[0]
        total_change = current_price - first_price
        total_percent = (total_change / first_price) * 100
        
        return {
            'current_price': current_price,
            'previous_price': previous_price,
            'absolute_change': absolute_change,
            'percent_change': percent_change,
            'first_price': first_price,
            'total_change': total_change,
            'total_percent': total_percent
        }
    
    def get_cached_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get cached data for symbol"""
        return self.data_cache.get(symbol)


class AlertSystem:
    """
    Alert system for price changes and trade signals
    
    Features:
    - Price change alerts (absolute and percentage)
    - Strategy signal alerts
    - Volume spike detection
    - Volatility alerts
    - Custom alert conditions
    - Alert history tracking
    """
    
    def __init__(self, price_change_threshold: float = 2.0,
                 volume_spike_multiplier: float = 2.0):
        """
        Initialize alert system
        
        Args:
            price_change_threshold: Percentage change threshold for alerts
            volume_spike_multiplier: Volume multiplier for spike detection
        """
        self.price_change_threshold = price_change_threshold
        self.volume_spike_multiplier = volume_spike_multiplier
        self.alert_history: List[Alert] = []
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        logger.info(f"✓ AlertSystem initialized (price threshold: {price_change_threshold}%)")
    
    def register_callback(self, callback: Callable[[Alert], None]):
        """
        Register a callback function for alerts
        
        Args:
            callback: Function to call when alert is triggered
        """
        self.alert_callbacks.append(callback)
        logger.info("Alert callback registered")
    
    def check_price_change(self, symbol: str, price_metrics: Dict[str, float]) -> Optional[Alert]:
        """
        Check for significant price changes
        
        Args:
            symbol: Trading pair
            price_metrics: Price change metrics from DataProcessor
        
        Returns:
            Alert if threshold exceeded, None otherwise
        """
        if not price_metrics:
            return None
        
        percent_change = price_metrics.get('percent_change', 0)
        
        if abs(percent_change) >= self.price_change_threshold:
            direction = "UP" if percent_change > 0 else "DOWN"
            priority = "high" if abs(percent_change) >= 5.0 else "normal"
            
            alert = Alert(
                alert_type=AlertType.PRICE_CHANGE,
                symbol=symbol,
                message=f"Price {direction} {abs(percent_change):.2f}% "
                       f"(${price_metrics['current_price']:.2f})",
                data=price_metrics,
                priority=priority
            )
            
            self._trigger_alert(alert)
            return alert
        
        return None
    
    def check_strategy_signal(self, symbol: str, signal: int,
                             strategies: List[str], current_price: float) -> Optional[Alert]:
        """
        Check for strategy trading signals
        
        Args:
            symbol: Trading pair
            signal: Signal value (1=BUY, -1=SELL, 0=HOLD)
            strategies: List of strategies that triggered the signal
            current_price: Current price
        
        Returns:
            Alert if signal detected, None otherwise
        """
        if signal == 0 or not strategies:
            return None
        
        signal_text = "BUY" if signal == 1 else "SELL"
        priority = "high" if len(strategies) > 1 else "normal"
        
        alert = Alert(
            alert_type=AlertType.STRATEGY_SIGNAL,
            symbol=symbol,
            message=f"{signal_text} signal from {len(strategies)} strateg{'y' if len(strategies) == 1 else 'ies'}: "
                   f"{', '.join(strategies)} at ${current_price:.2f}",
            data={
                'signal': signal,
                'signal_text': signal_text,
                'strategies': strategies,
                'price': current_price
            },
            priority=priority
        )
        
        self._trigger_alert(alert)
        return alert
    
    def check_volume_spike(self, symbol: str, df: pd.DataFrame) -> Optional[Alert]:
        """
        Check for volume spikes
        
        Args:
            symbol: Trading pair
            df: OHLCV DataFrame
        
        Returns:
            Alert if volume spike detected, None otherwise
        """
        if df is None or len(df) < 20:
            return None
        
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].iloc[-20:-1].mean()
        
        if current_volume > avg_volume * self.volume_spike_multiplier:
            volume_ratio = current_volume / avg_volume
            
            alert = Alert(
                alert_type=AlertType.VOLUME_SPIKE,
                symbol=symbol,
                message=f"Volume spike detected: {volume_ratio:.2f}x average "
                       f"(current: {current_volume:.0f}, avg: {avg_volume:.0f})",
                data={
                    'current_volume': current_volume,
                    'average_volume': avg_volume,
                    'ratio': volume_ratio
                },
                priority="normal"
            )
            
            self._trigger_alert(alert)
            return alert
        
        return None
    
    def _trigger_alert(self, alert: Alert):
        """
        Trigger an alert
        
        Args:
            alert: Alert to trigger
        """
        # Add to history
        self.alert_history.append(alert)
        
        # Log the alert
        if alert.priority == "critical":
            logger.critical(str(alert))
        elif alert.priority == "high":
            logger.warning(str(alert))
        else:
            logger.info(str(alert))
        
        # Call registered callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def get_recent_alerts(self, limit: int = 10) -> List[Alert]:
        """Get recent alerts"""
        return self.alert_history[-limit:]
    
    def clear_history(self):
        """Clear alert history"""
        self.alert_history.clear()
        logger.info("Alert history cleared")


class LiveMarketMonitor:
    """
    Main live market monitoring class
    
    Orchestrates data fetching, processing, strategy analysis, and alerting.
    Integrates with existing trading strategies for signal detection.
    """
    
    def __init__(self, symbols: List[str], interval: str = '15m',
                 update_interval: int = 60, exchange: str = "binance",
                 api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 testnet: bool = True, price_alert_threshold: float = 2.0):
        """
        Initialize live market monitor
        
        Args:
            symbols: List of trading pairs to monitor (e.g., ['BTCUSDT', 'ETHUSDT'])
            interval: Timeframe for data (e.g., '1m', '5m', '15m', '1h')
            update_interval: Update frequency in seconds
            exchange: Exchange name (currently only 'binance')
            api_key: API key for exchange
            api_secret: API secret for exchange
            testnet: Use testnet environment
            price_alert_threshold: Percentage threshold for price alerts
        """
        self.symbols = symbols
        self.interval = interval
        self.update_interval = update_interval
        self.running = False
        
        # Initialize components
        self.data_fetcher = MarketDataFetcher(
            exchange=exchange,
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet
        )
        
        self.data_processor = DataProcessor()
        self.alert_system = AlertSystem(price_change_threshold=price_alert_threshold)
        
        # Strategy integration
        self.strategy = None
        
        logger.info(f"✓ LiveMarketMonitor initialized for {len(symbols)} symbols")
        logger.info(f"  Symbols: {', '.join(symbols)}")
        logger.info(f"  Interval: {interval}, Update: every {update_interval}s")
    
    def integrate_strategy(self, strategy):
        """
        Integrate a trading strategy for signal detection
        
        Args:
            strategy: TradingStrategy instance from strategy.py
        """
        self.strategy = strategy
        logger.info("✓ Trading strategy integrated with monitor")
    
    def register_alert_callback(self, callback: Callable[[Alert], None]):
        """
        Register callback for alert notifications
        
        Args:
            callback: Function to call when alerts are triggered
        """
        self.alert_system.register_callback(callback)
    
    def monitor_once(self) -> Dict[str, Any]:
        """
        Perform one monitoring cycle for all symbols
        
        Returns:
            Dictionary with monitoring results for each symbol
        """
        results = {}
        
        for symbol in self.symbols:
            try:
                # Fetch current price
                current_price = self.data_fetcher.fetch_current_price(symbol)
                if current_price is None:
                    logger.warning(f"Could not fetch price for {symbol}")
                    continue
                
                # Fetch historical data
                df = self.data_fetcher.fetch_historical_data(symbol, self.interval)
                if df is None or df.empty:
                    logger.warning(f"Could not fetch historical data for {symbol}")
                    continue
                
                # Process data
                processed_df = self.data_processor.process_ohlcv(df, symbol)
                if processed_df is None:
                    continue
                
                # Calculate price changes
                price_metrics = self.data_processor.calculate_price_change(processed_df)
                
                # Check price change alerts
                price_alert = self.alert_system.check_price_change(symbol, price_metrics)
                
                # Check volume spike
                volume_alert = self.alert_system.check_volume_spike(symbol, processed_df)
                
                # Check strategy signals if integrated
                strategy_alert = None
                signal_info = None
                if self.strategy:
                    try:
                        analysis = self.strategy.analyze(processed_df)
                        signal = analysis.get('signal', 0)
                        strategies = analysis.get('triggering_strategies', [])
                        
                        strategy_alert = self.alert_system.check_strategy_signal(
                            symbol, signal, strategies, current_price
                        )
                        
                        signal_info = {
                            'signal': signal,
                            'signal_text': analysis.get('signal_text', 'HOLD'),
                            'strategies': strategies
                        }
                    except Exception as e:
                        logger.error(f"Error analyzing strategy for {symbol}: {e}")
                
                # Compile results
                results[symbol] = {
                    'current_price': current_price,
                    'price_metrics': price_metrics,
                    'signal_info': signal_info,
                    'alerts': {
                        'price': price_alert,
                        'volume': volume_alert,
                        'strategy': strategy_alert
                    },
                    'timestamp': datetime.now()
                }
                
                logger.debug(f"{symbol}: ${current_price:.2f} "
                           f"({price_metrics.get('percent_change', 0):+.2f}%)")
                
            except Exception as e:
                logger.error(f"Error monitoring {symbol}: {e}")
                continue
        
        return results
    
    def start_monitoring(self, duration: Optional[int] = None):
        """
        Start continuous monitoring
        
        Args:
            duration: Monitoring duration in seconds (None for infinite)
        """
        self.running = True
        start_time = time.time()
        
        logger.info("=" * 70)
        logger.info("🔄 Live Market Monitoring Started")
        logger.info("=" * 70)
        logger.info(f"Monitoring {len(self.symbols)} symbols: {', '.join(self.symbols)}")
        logger.info(f"Update interval: {self.update_interval} seconds")
        if duration:
            logger.info(f"Duration: {duration} seconds")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 70)
        
        try:
            iteration = 0
            while self.running:
                iteration += 1
                
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    logger.info("Monitoring duration reached")
                    break
                
                logger.info(f"\n🔍 Monitoring cycle #{iteration}")
                
                # Perform monitoring
                results = self.monitor_once()
                
                # Summary
                logger.info(f"Monitored {len(results)}/{len(self.symbols)} symbols")
                
                # Wait for next update
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            logger.info("\n⏹️ Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}", exc_info=True)
        finally:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        logger.info("=" * 70)
        logger.info("📊 Monitoring Summary")
        logger.info("=" * 70)
        
        recent_alerts = self.alert_system.get_recent_alerts(limit=20)
        if recent_alerts:
            logger.info(f"Recent alerts ({len(recent_alerts)}):")
            for alert in recent_alerts[-5:]:  # Show last 5
                logger.info(f"  {alert}")
        else:
            logger.info("No alerts triggered")
        
        logger.info("=" * 70)
        logger.info("🛑 Live Market Monitoring Stopped")
        logger.info("=" * 70)
    
    def test_connection(self) -> bool:
        """Test connection to exchange"""
        return self.data_fetcher.test_connection()


# ========== EXAMPLE USAGE ==========

def example_live_monitoring():
    """Example of using the live market monitor"""
    import logging
    from strategy import TradingStrategy
    from config import config
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("  Live Market Monitor - Example")
    print("=" * 70)
    
    # Initialize monitor
    monitor = LiveMarketMonitor(
        symbols=['BTCUSDT', 'ETHUSDT'],
        interval='15m',
        update_interval=30,  # 30 seconds
        testnet=True,
        price_alert_threshold=1.0  # 1% change threshold
    )
    
    # Test connection
    print("\n1. Testing connection...")
    if not monitor.test_connection():
        print("❌ Connection failed!")
        return
    print("✓ Connection successful")
    
    # Integrate strategy
    print("\n2. Integrating trading strategy...")
    strategy = TradingStrategy(config.to_dict())
    monitor.integrate_strategy(strategy)
    print("✓ Strategy integrated")
    
    # Register alert callback
    def alert_handler(alert: Alert):
        print(f"\n🔔 ALERT: {alert}")
    
    monitor.register_alert_callback(alert_handler)
    
    # Start monitoring for 2 minutes
    print("\n3. Starting monitoring (2 minutes)...")
    monitor.start_monitoring(duration=120)
    
    print("\n✓ Example complete!")


if __name__ == "__main__":
    example_live_monitoring()
