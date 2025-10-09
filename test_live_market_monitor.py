"""
test_live_market_monitor.py - Tests for Live Market Monitor
============================================================
Comprehensive test suite for the live market monitoring module
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime

# Import components to test
from live_market_monitor import (
    MarketDataFetcher,
    DataProcessor,
    AlertSystem,
    LiveMarketMonitor,
    Alert,
    AlertType
)


class TestMarketDataFetcher(unittest.TestCase):
    """Test MarketDataFetcher class"""
    
    @patch('live_market_monitor.BinanceDataProvider')
    def test_initialization_binance(self, mock_binance):
        """Test initialization with Binance"""
        fetcher = MarketDataFetcher(exchange="binance", testnet=True)
        self.assertIsNotNone(fetcher.provider)
        self.assertEqual(fetcher.exchange, "binance")
        self.assertTrue(fetcher.testnet)
    
    def test_unsupported_exchange(self):
        """Test initialization with unsupported exchange"""
        with self.assertRaises(ValueError):
            MarketDataFetcher(exchange="unsupported")
    
    @patch('live_market_monitor.BinanceDataProvider')
    def test_fetch_current_price(self, mock_binance):
        """Test fetching current price"""
        # Setup mock
        mock_provider = MagicMock()
        mock_provider.get_current_price.return_value = 50000.0
        
        fetcher = MarketDataFetcher(exchange="binance")
        fetcher.provider = mock_provider
        
        price = fetcher.fetch_current_price('BTCUSDT')
        self.assertEqual(price, 50000.0)
        mock_provider.get_current_price.assert_called_once_with('BTCUSDT')
    
    @patch('live_market_monitor.BinanceDataProvider')
    def test_fetch_historical_data(self, mock_binance):
        """Test fetching historical data"""
        # Create sample DataFrame
        sample_df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='15min'),
            'open': np.random.uniform(49000, 51000, 100),
            'high': np.random.uniform(50000, 52000, 100),
            'low': np.random.uniform(48000, 50000, 100),
            'close': np.random.uniform(49000, 51000, 100),
            'volume': np.random.uniform(100, 1000, 100)
        })
        
        # Setup mock
        mock_provider = MagicMock()
        mock_provider.get_historical_klines.return_value = sample_df
        
        fetcher = MarketDataFetcher(exchange="binance")
        fetcher.provider = mock_provider
        
        df = fetcher.fetch_historical_data('BTCUSDT', interval='15m', limit=100)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 100)
        mock_provider.get_historical_klines.assert_called_once()


class TestDataProcessor(unittest.TestCase):
    """Test DataProcessor class"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.processor = DataProcessor()
        
        # Create valid sample data
        self.valid_df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='15min'),
            'open': np.random.uniform(49000, 51000, 100),
            'high': np.random.uniform(50000, 52000, 100),
            'low': np.random.uniform(48000, 50000, 100),
            'close': np.random.uniform(49000, 51000, 100),
            'volume': np.random.uniform(100, 1000, 100)
        })
        
        # Ensure high >= low, open, close
        self.valid_df['high'] = self.valid_df[['open', 'high', 'close']].max(axis=1) + 100
        self.valid_df['low'] = self.valid_df[['open', 'low', 'close']].min(axis=1) - 100
    
    def test_process_valid_ohlcv(self):
        """Test processing valid OHLCV data"""
        result = self.processor.process_ohlcv(self.valid_df, 'BTCUSDT')
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 100)
        self.assertIn('BTCUSDT', self.processor.data_cache)
    
    def test_process_empty_data(self):
        """Test processing empty data"""
        empty_df = pd.DataFrame()
        result = self.processor.process_ohlcv(empty_df, 'BTCUSDT')
        self.assertIsNone(result)
    
    def test_process_missing_columns(self):
        """Test processing data with missing columns"""
        invalid_df = pd.DataFrame({
            'open': [100, 101],
            'close': [102, 103]
            # Missing high, low, volume
        })
        result = self.processor.process_ohlcv(invalid_df, 'BTCUSDT')
        self.assertIsNone(result)
    
    def test_validate_ohlcv_with_nan(self):
        """Test validation with NaN values"""
        df_with_nan = self.valid_df.copy()
        df_with_nan.loc[0, 'close'] = np.nan
        self.assertFalse(self.processor._validate_ohlcv(df_with_nan))
    
    def test_validate_ohlcv_high_low_constraint(self):
        """Test validation of high >= low constraint"""
        invalid_df = self.valid_df.copy()
        invalid_df.loc[0, 'high'] = invalid_df.loc[0, 'low'] - 100
        self.assertFalse(self.processor._validate_ohlcv(invalid_df))
    
    def test_validate_ohlcv_negative_prices(self):
        """Test validation with negative prices"""
        invalid_df = self.valid_df.copy()
        invalid_df.loc[0, 'close'] = -100
        self.assertFalse(self.processor._validate_ohlcv(invalid_df))
    
    def test_calculate_price_change(self):
        """Test price change calculation"""
        changes = self.processor.calculate_price_change(self.valid_df)
        
        self.assertIn('current_price', changes)
        self.assertIn('previous_price', changes)
        self.assertIn('absolute_change', changes)
        self.assertIn('percent_change', changes)
        self.assertIn('total_change', changes)
        self.assertIn('total_percent', changes)
    
    def test_calculate_price_change_insufficient_data(self):
        """Test price change with insufficient data"""
        small_df = self.valid_df.iloc[:1]
        changes = self.processor.calculate_price_change(small_df)
        self.assertEqual(changes, {})
    
    def test_get_cached_data(self):
        """Test retrieving cached data"""
        self.processor.process_ohlcv(self.valid_df, 'BTCUSDT')
        cached = self.processor.get_cached_data('BTCUSDT')
        self.assertIsNotNone(cached)
        self.assertEqual(len(cached), 100)


class TestAlertSystem(unittest.TestCase):
    """Test AlertSystem class"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.alert_system = AlertSystem(
            price_change_threshold=2.0,
            volume_spike_multiplier=2.0
        )
    
    def test_initialization(self):
        """Test alert system initialization"""
        self.assertEqual(self.alert_system.price_change_threshold, 2.0)
        self.assertEqual(self.alert_system.volume_spike_multiplier, 2.0)
        self.assertEqual(len(self.alert_system.alert_history), 0)
    
    def test_register_callback(self):
        """Test registering alert callback"""
        def dummy_callback(alert):
            pass
        
        self.alert_system.register_callback(dummy_callback)
        self.assertEqual(len(self.alert_system.alert_callbacks), 1)
    
    def test_check_price_change_above_threshold(self):
        """Test price change alert when threshold exceeded"""
        price_metrics = {
            'current_price': 51000.0,
            'previous_price': 50000.0,
            'percent_change': 2.5,
            'absolute_change': 1000.0
        }
        
        alert = self.alert_system.check_price_change('BTCUSDT', price_metrics)
        self.assertIsNotNone(alert)
        self.assertEqual(alert.alert_type, AlertType.PRICE_CHANGE)
        self.assertEqual(alert.symbol, 'BTCUSDT')
        self.assertIn('UP', alert.message)
    
    def test_check_price_change_below_threshold(self):
        """Test no alert when below threshold"""
        price_metrics = {
            'current_price': 50500.0,
            'previous_price': 50000.0,
            'percent_change': 1.0,
            'absolute_change': 500.0
        }
        
        alert = self.alert_system.check_price_change('BTCUSDT', price_metrics)
        self.assertIsNone(alert)
    
    def test_check_price_change_negative(self):
        """Test price change alert for negative change"""
        price_metrics = {
            'current_price': 48500.0,
            'previous_price': 50000.0,
            'percent_change': -3.0,
            'absolute_change': -1500.0
        }
        
        alert = self.alert_system.check_price_change('BTCUSDT', price_metrics)
        self.assertIsNotNone(alert)
        self.assertIn('DOWN', alert.message)
    
    def test_check_strategy_signal_buy(self):
        """Test strategy signal alert for BUY"""
        alert = self.alert_system.check_strategy_signal(
            symbol='BTCUSDT',
            signal=1,
            strategies=['RSI', 'EMA_Crossover'],
            current_price=50000.0
        )
        
        self.assertIsNotNone(alert)
        self.assertEqual(alert.alert_type, AlertType.STRATEGY_SIGNAL)
        self.assertIn('BUY', alert.message)
        self.assertIn('RSI', alert.message)
    
    def test_check_strategy_signal_sell(self):
        """Test strategy signal alert for SELL"""
        alert = self.alert_system.check_strategy_signal(
            symbol='BTCUSDT',
            signal=-1,
            strategies=['MA_Crossover'],
            current_price=50000.0
        )
        
        self.assertIsNotNone(alert)
        self.assertIn('SELL', alert.message)
    
    def test_check_strategy_signal_hold(self):
        """Test no alert for HOLD signal"""
        alert = self.alert_system.check_strategy_signal(
            symbol='BTCUSDT',
            signal=0,
            strategies=[],
            current_price=50000.0
        )
        
        self.assertIsNone(alert)
    
    def test_check_volume_spike(self):
        """Test volume spike detection"""
        df = pd.DataFrame({
            'volume': [100] * 19 + [300]  # Last volume is 3x average
        })
        
        alert = self.alert_system.check_volume_spike('BTCUSDT', df)
        self.assertIsNotNone(alert)
        self.assertEqual(alert.alert_type, AlertType.VOLUME_SPIKE)
        self.assertIn('spike', alert.message.lower())
    
    def test_check_volume_spike_insufficient_data(self):
        """Test volume spike with insufficient data"""
        df = pd.DataFrame({
            'volume': [100] * 10
        })
        
        alert = self.alert_system.check_volume_spike('BTCUSDT', df)
        self.assertIsNone(alert)
    
    def test_get_recent_alerts(self):
        """Test getting recent alerts"""
        # Trigger some alerts
        for i in range(15):
            price_metrics = {
                'current_price': 50000.0 + i * 100,
                'previous_price': 50000.0,
                'percent_change': 2.5,
                'absolute_change': i * 100
            }
            self.alert_system.check_price_change('BTCUSDT', price_metrics)
        
        recent = self.alert_system.get_recent_alerts(limit=5)
        self.assertEqual(len(recent), 5)
    
    def test_clear_history(self):
        """Test clearing alert history"""
        # Add some alerts
        price_metrics = {
            'current_price': 51000.0,
            'previous_price': 50000.0,
            'percent_change': 2.5,
            'absolute_change': 1000.0
        }
        self.alert_system.check_price_change('BTCUSDT', price_metrics)
        
        self.assertGreater(len(self.alert_system.alert_history), 0)
        
        self.alert_system.clear_history()
        self.assertEqual(len(self.alert_system.alert_history), 0)
    
    def test_alert_callback_execution(self):
        """Test that alert callbacks are executed"""
        callback_called = {'count': 0}
        
        def callback(alert):
            callback_called['count'] += 1
        
        self.alert_system.register_callback(callback)
        
        price_metrics = {
            'current_price': 51000.0,
            'previous_price': 50000.0,
            'percent_change': 2.5,
            'absolute_change': 1000.0
        }
        self.alert_system.check_price_change('BTCUSDT', price_metrics)
        
        self.assertEqual(callback_called['count'], 1)


class TestLiveMarketMonitor(unittest.TestCase):
    """Test LiveMarketMonitor class"""
    
    @patch('live_market_monitor.MarketDataFetcher')
    def test_initialization(self, mock_fetcher):
        """Test monitor initialization"""
        monitor = LiveMarketMonitor(
            symbols=['BTCUSDT', 'ETHUSDT'],
            interval='15m',
            update_interval=60
        )
        
        self.assertEqual(len(monitor.symbols), 2)
        self.assertEqual(monitor.interval, '15m')
        self.assertEqual(monitor.update_interval, 60)
        self.assertFalse(monitor.running)
    
    @patch('live_market_monitor.MarketDataFetcher')
    def test_integrate_strategy(self, mock_fetcher):
        """Test strategy integration"""
        monitor = LiveMarketMonitor(symbols=['BTCUSDT'])
        
        mock_strategy = Mock()
        monitor.integrate_strategy(mock_strategy)
        
        self.assertIsNotNone(monitor.strategy)
        self.assertEqual(monitor.strategy, mock_strategy)
    
    @patch('live_market_monitor.MarketDataFetcher')
    def test_register_alert_callback(self, mock_fetcher):
        """Test registering alert callback"""
        monitor = LiveMarketMonitor(symbols=['BTCUSDT'])
        
        def dummy_callback(alert):
            pass
        
        monitor.register_alert_callback(dummy_callback)
        self.assertEqual(len(monitor.alert_system.alert_callbacks), 1)
    
    @patch('live_market_monitor.MarketDataFetcher')
    def test_monitor_once_success(self, mock_fetcher_class):
        """Test single monitoring cycle"""
        # Setup mock data fetcher
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_current_price.return_value = 50000.0
        
        # Create valid sample DataFrame
        sample_df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='15min'),
            'open': np.random.uniform(49000, 51000, 100),
            'high': np.random.uniform(50000, 52000, 100),
            'low': np.random.uniform(48000, 50000, 100),
            'close': np.random.uniform(49000, 51000, 100),
            'volume': np.random.uniform(100, 1000, 100)
        })
        # Fix OHLCV constraints
        sample_df['high'] = sample_df[['open', 'high', 'close']].max(axis=1) + 100
        sample_df['low'] = sample_df[['open', 'low', 'close']].min(axis=1) - 100
        
        mock_fetcher.fetch_historical_data.return_value = sample_df
        
        monitor = LiveMarketMonitor(symbols=['BTCUSDT'])
        monitor.data_fetcher = mock_fetcher
        
        results = monitor.monitor_once()
        
        self.assertIn('BTCUSDT', results)
        self.assertIn('current_price', results['BTCUSDT'])
        self.assertEqual(results['BTCUSDT']['current_price'], 50000.0)
    
    @patch('live_market_monitor.MarketDataFetcher')
    def test_monitor_once_with_strategy(self, mock_fetcher_class):
        """Test monitoring with strategy integration"""
        # Setup mock data fetcher
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_current_price.return_value = 50000.0
        
        sample_df = pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='15min'),
            'open': np.random.uniform(49000, 51000, 100),
            'high': np.random.uniform(50000, 52000, 100),
            'low': np.random.uniform(48000, 50000, 100),
            'close': np.random.uniform(49000, 51000, 100),
            'volume': np.random.uniform(100, 1000, 100)
        })
        sample_df['high'] = sample_df[['open', 'high', 'close']].max(axis=1) + 100
        sample_df['low'] = sample_df[['open', 'low', 'close']].min(axis=1) - 100
        
        mock_fetcher.fetch_historical_data.return_value = sample_df
        
        # Setup mock strategy
        mock_strategy = Mock()
        mock_strategy.analyze.return_value = {
            'signal': 1,
            'signal_text': 'BUY',
            'triggering_strategies': ['RSI', 'EMA'],
            'current_price': 50000.0
        }
        
        monitor = LiveMarketMonitor(symbols=['BTCUSDT'])
        monitor.data_fetcher = mock_fetcher
        monitor.integrate_strategy(mock_strategy)
        
        results = monitor.monitor_once()
        
        self.assertIn('BTCUSDT', results)
        self.assertIsNotNone(results['BTCUSDT']['signal_info'])
        self.assertEqual(results['BTCUSDT']['signal_info']['signal'], 1)


class TestAlert(unittest.TestCase):
    """Test Alert class"""
    
    def test_alert_creation(self):
        """Test creating an alert"""
        alert = Alert(
            alert_type=AlertType.PRICE_CHANGE,
            symbol='BTCUSDT',
            message='Test alert',
            priority='high'
        )
        
        self.assertEqual(alert.alert_type, AlertType.PRICE_CHANGE)
        self.assertEqual(alert.symbol, 'BTCUSDT')
        self.assertEqual(alert.message, 'Test alert')
        self.assertEqual(alert.priority, 'high')
        self.assertIsInstance(alert.timestamp, datetime)
    
    def test_alert_string_representation(self):
        """Test alert string representation"""
        alert = Alert(
            alert_type=AlertType.STRATEGY_SIGNAL,
            symbol='ETHUSDT',
            message='BUY signal',
            priority='critical'
        )
        
        alert_str = str(alert)
        self.assertIn('STRATEGY_SIGNAL', alert_str)
        self.assertIn('ETHUSDT', alert_str)
        self.assertIn('BUY signal', alert_str)


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("  Live Market Monitor - Test Suite")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMarketDataFetcher))
    suite.addTests(loader.loadTestsFromTestCase(TestDataProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestAlertSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestLiveMarketMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestAlert))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("  Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
