"""
test_base_strategy.py - Tests for Enhanced Base Strategy Framework
==================================================================
Unit tests for the enhanced base strategy implementation.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import tempfile
import json

from base_strategy import (
    EnhancedBaseStrategy,
    VideoBasedStrategy,
    StrategyState,
    DataFeed,
    create_strategy_from_video,
    log_strategy_performance
)
from utils import generate_sample_data


class TestStrategyState:
    """Tests for StrategyState dataclass"""
    
    def test_initialization(self):
        """Test state initialization with defaults"""
        state = StrategyState()
        
        assert state.last_signal == 0
        assert state.last_signal_time is None
        assert state.position_open == False
        assert state.position_entry_price == 0.0
        assert state.trades_count == 0
        assert state.wins_count == 0
        assert state.losses_count == 0
        assert state.total_profit == 0.0
        assert isinstance(state.custom_data, dict)
    
    def test_custom_data(self):
        """Test custom data storage"""
        state = StrategyState()
        state.custom_data['my_indicator'] = 42.5
        state.custom_data['last_alert'] = datetime.now()
        
        assert state.custom_data['my_indicator'] == 42.5
        assert isinstance(state.custom_data['last_alert'], datetime)


class TestDataFeed:
    """Tests for DataFeed dataclass"""
    
    def test_initialization(self):
        """Test data feed initialization"""
        df = generate_sample_data(n_bars=100)
        feed = DataFeed(
            symbol='BTC/USDT',
            timeframe='1h',
            data=df
        )
        
        assert feed.symbol == 'BTC/USDT'
        assert feed.timeframe == '1h'
        assert len(feed.data) == 100
    
    def test_validation_valid_data(self):
        """Test validation with valid data"""
        df = generate_sample_data(n_bars=100)
        feed = DataFeed('BTC/USDT', '1h', df)
        
        assert feed.validate() == True
    
    def test_validation_missing_columns(self):
        """Test validation with missing columns"""
        df = pd.DataFrame({'price': [100, 101, 102]})
        feed = DataFeed('BTC/USDT', '1h', df)
        
        assert feed.validate() == False
    
    def test_validation_insufficient_data(self):
        """Test validation with insufficient data"""
        df = pd.DataFrame({
            'open': [100],
            'high': [101],
            'low': [99],
            'close': [100.5],
            'volume': [1000]
        })
        feed = DataFeed('BTC/USDT', '1h', df)
        
        assert feed.validate() == False
    
    def test_is_stale(self):
        """Test staleness detection"""
        df = generate_sample_data(n_bars=100)
        
        # Fresh feed
        feed = DataFeed('BTC/USDT', '1h', df, last_update=datetime.now())
        assert feed.is_stale(max_age_seconds=300) == False
        
        # Stale feed
        old_time = datetime.now() - timedelta(seconds=400)
        feed_stale = DataFeed('BTC/USDT', '1h', df, last_update=old_time)
        assert feed_stale.is_stale(max_age_seconds=300) == True
        
        # No update time
        feed_no_update = DataFeed('BTC/USDT', '1h', df)
        assert feed_no_update.is_stale() == True


class TestVideoBasedStrategy:
    """Tests for VideoBasedStrategy implementation"""
    
    def test_initialization(self):
        """Test strategy initialization"""
        params = {
            'ma_short': 10,
            'ma_long': 50,
            'rsi_period': 14
        }
        
        strategy = VideoBasedStrategy(params)
        
        assert strategy.name == "VideoBasedStrategy"
        assert strategy.enabled == True
        assert strategy.ma_short == 10
        assert strategy.ma_long == 50
        assert strategy.rsi_period == 14
    
    def test_initialization_with_defaults(self):
        """Test initialization with default parameters"""
        strategy = VideoBasedStrategy({})
        
        assert strategy.ma_short == 10  # Default value
        assert strategy.ma_long == 50
        assert strategy.rsi_period == 14
    
    def test_signal_generation_insufficient_data(self):
        """Test signal generation with insufficient data"""
        strategy = VideoBasedStrategy({})
        
        # Not enough data
        df = generate_sample_data(n_bars=10)
        signal = strategy.generate_signal(df)
        
        assert signal == 0  # HOLD
    
    def test_signal_generation_sufficient_data(self):
        """Test signal generation with sufficient data"""
        strategy = VideoBasedStrategy({
            'ma_short': 10,
            'ma_long': 20,
            'rsi_period': 14
        })
        
        df = generate_sample_data(n_bars=100, start_price=50000)
        signal = strategy.generate_signal(df)
        
        # Should generate valid signal
        assert signal in [-1, 0, 1]
    
    def test_signal_generation_buy_signal(self):
        """Test buy signal generation"""
        strategy = VideoBasedStrategy({
            'ma_short': 5,
            'ma_long': 10,
            'rsi_period': 14,
            'rsi_overbought': 70
        })
        
        # Create uptrend data
        dates = pd.date_range(start='2024-01-01', periods=50, freq='1h')
        prices = np.linspace(45000, 55000, 50)  # Strong uptrend
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': prices * 1.01,
            'low': prices * 0.99,
            'close': prices,
            'volume': np.random.uniform(100, 1000, 50)
        })
        
        signal = strategy.generate_signal(df)
        # May generate BUY or HOLD depending on RSI
        assert signal in [0, 1]
    
    def test_disabled_strategy(self):
        """Test that disabled strategy returns HOLD"""
        strategy = VideoBasedStrategy({})
        strategy.enabled = False
        
        df = generate_sample_data(n_bars=100)
        signal = strategy.generate_signal(df)
        
        assert signal == 0  # HOLD


class TestEnhancedBaseStrategy:
    """Tests for EnhancedBaseStrategy base class"""
    
    def test_data_validation_valid(self):
        """Test data validation with valid data"""
        strategy = VideoBasedStrategy({})
        df = generate_sample_data(n_bars=100)
        
        assert strategy.validate_data(df) == True
    
    def test_data_validation_missing_column(self):
        """Test data validation with missing column"""
        strategy = VideoBasedStrategy({})
        df = pd.DataFrame({'close': [100, 101, 102]})
        
        assert strategy.validate_data(df) == False
    
    def test_data_validation_insufficient_rows(self):
        """Test data validation with insufficient rows"""
        strategy = VideoBasedStrategy({})
        df = pd.DataFrame({
            'open': [100],
            'high': [101],
            'low': [99],
            'close': [100],
            'volume': [1000]
        })
        
        assert strategy.validate_data(df) == False
    
    def test_data_validation_invalid_ohlc(self):
        """Test data validation with invalid OHLC"""
        strategy = VideoBasedStrategy({})
        df = pd.DataFrame({
            'open': [100, 100],
            'high': [99, 99],  # High < Low (invalid)
            'low': [101, 101],
            'close': [100, 100],
            'volume': [1000, 1000]
        })
        
        assert strategy.validate_data(df) == False
    
    def test_add_data_feed(self):
        """Test adding data feeds"""
        strategy = VideoBasedStrategy({})
        
        df_1h = generate_sample_data(n_bars=100)
        df_4h = generate_sample_data(n_bars=100)
        
        # Add feeds
        result1 = strategy.add_data_feed('BTC/USDT', '1h', df_1h)
        result2 = strategy.add_data_feed('BTC/USDT', '4h', df_4h)
        
        assert result1 == True
        assert result2 == True
        assert len(strategy.data_feeds) == 2
    
    def test_get_data_feed(self):
        """Test retrieving data feeds"""
        strategy = VideoBasedStrategy({})
        
        df = generate_sample_data(n_bars=100)
        strategy.add_data_feed('BTC/USDT', '1h', df)
        
        # Retrieve existing feed
        retrieved = strategy.get_data_feed('BTC/USDT', '1h')
        assert retrieved is not None
        assert len(retrieved) == 100
        
        # Try non-existent feed
        missing = strategy.get_data_feed('ETH/USDT', '1d')
        assert missing is None
    
    def test_update_state(self):
        """Test state updates"""
        strategy = VideoBasedStrategy({})
        
        # Update standard fields
        strategy.update_state(
            trades_count=5,
            wins_count=3,
            total_profit=150.0
        )
        
        assert strategy.state.trades_count == 5
        assert strategy.state.wins_count == 3
        assert strategy.state.total_profit == 150.0
        
        # Update custom fields
        strategy.update_state(
            my_indicator=42.5,
            last_alert='test'
        )
        
        assert strategy.state.custom_data['my_indicator'] == 42.5
        assert strategy.state.custom_data['last_alert'] == 'test'
    
    def test_on_position_opened(self):
        """Test position opened callback"""
        strategy = VideoBasedStrategy({})
        
        strategy.on_position_opened(
            entry_price=50000.0,
            quantity=0.01,
            side='long'
        )
        
        assert strategy.state.position_open == True
        assert strategy.state.position_entry_price == 50000.0
        assert strategy.state.trades_count == 1
        assert strategy.state.position_entry_time is not None
    
    def test_on_position_closed(self):
        """Test position closed callback"""
        strategy = VideoBasedStrategy({})
        
        # Open position first
        strategy.on_position_opened(50000.0, 0.01, 'long')
        
        # Close with profit
        strategy.on_position_closed(51000.0, 10.0, 'long')
        
        assert strategy.state.position_open == False
        assert strategy.state.total_profit == 10.0
        assert strategy.state.wins_count == 1
        assert strategy.state.losses_count == 0
        
        # Open and close with loss
        strategy.on_position_opened(50000.0, 0.01, 'short')
        strategy.on_position_closed(51000.0, -10.0, 'short')
        
        assert strategy.state.total_profit == 0.0
        assert strategy.state.wins_count == 1
        assert strategy.state.losses_count == 1
    
    def test_generate_signal_with_context(self):
        """Test signal generation with context"""
        strategy = VideoBasedStrategy({})
        df = generate_sample_data(n_bars=100)
        
        signal, context = strategy.generate_signal_with_context(df)
        
        # Check signal
        assert signal in [-1, 0, 1]
        
        # Check context
        assert 'signal' in context
        assert 'signal_text' in context
        assert 'timestamp' in context
        assert 'current_price' in context
        assert 'strategy_state' in context
        assert 'confidence' in context
        
        # Check signal text
        assert context['signal_text'] in ['BUY', 'SELL', 'HOLD']
    
    def test_performance_tracking(self):
        """Test performance metrics tracking"""
        strategy = VideoBasedStrategy({})
        df = generate_sample_data(n_bars=100)
        
        # Generate multiple signals with context (which tracks performance)
        for _ in range(5):
            strategy.generate_signal_with_context(df)
        
        metrics = strategy.performance_metrics
        
        assert metrics['signals_generated'] == 5
        assert metrics['buy_signals'] + metrics['sell_signals'] + metrics['hold_signals'] == 5
        assert metrics['avg_execution_time_ms'] >= 0
    
    def test_update_params(self):
        """Test parameter updates"""
        params = {'ma_short': 10, 'ma_long': 50}
        strategy = VideoBasedStrategy(params)
        
        assert strategy.params['ma_short'] == 10
        
        # Update parameters
        strategy.update_params({'ma_short': 20})
        
        assert strategy.params['ma_short'] == 20
        assert strategy.params['ma_long'] == 50  # Unchanged
    
    def test_get_info(self):
        """Test getting strategy info"""
        strategy = VideoBasedStrategy({
            'ma_short': 10,
            'ma_long': 50
        })
        
        info = strategy.get_info()
        
        assert 'name' in info
        assert 'enabled' in info
        assert 'params' in info
        assert 'state' in info
        assert 'performance' in info
        assert 'data_feeds' in info
        
        assert info['name'] == "VideoBasedStrategy"
        assert info['enabled'] == True
    
    def test_reset_state(self):
        """Test state reset"""
        strategy = VideoBasedStrategy({})
        
        # Modify state
        strategy.state.trades_count = 10
        strategy.state.wins_count = 5
        strategy.state.total_profit = 100.0
        
        # Reset
        strategy.reset_state()
        
        assert strategy.state.trades_count == 0
        assert strategy.state.wins_count == 0
        assert strategy.state.total_profit == 0.0
    
    def test_export_import_state(self):
        """Test state export and import"""
        strategy = VideoBasedStrategy({'ma_short': 10})
        
        # Set some state
        strategy.state.trades_count = 10
        strategy.state.wins_count = 6
        strategy.state.losses_count = 4
        strategy.state.total_profit = 150.0
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            strategy.export_state(filepath)
            
            # Verify file exists and has content
            assert os.path.exists(filepath)
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            assert 'name' in data
            assert 'state' in data
            assert data['state']['trades_count'] == 10
            
            # Create new strategy and import
            new_strategy = VideoBasedStrategy({'ma_short': 10})
            new_strategy.import_state(filepath)
            
            assert new_strategy.state.trades_count == 10
            assert new_strategy.state.wins_count == 6
            assert new_strategy.state.total_profit == 150.0
            
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)


class TestUtilityFunctions:
    """Tests for utility functions"""
    
    def test_create_strategy_from_video(self):
        """Test strategy factory function"""
        params = {'ma_short': 10}
        
        strategy = create_strategy_from_video(
            video_id='FDmV1bIub_s',
            strategy_name='TestStrategy',
            params=params
        )
        
        assert strategy is not None
        assert isinstance(strategy, VideoBasedStrategy)
    
    def test_log_strategy_performance(self):
        """Test performance logging"""
        strategy = VideoBasedStrategy({})
        df = generate_sample_data(n_bars=100)
        
        # Generate some signals
        for _ in range(3):
            strategy.generate_signal(df)
        
        # Should not raise exception
        log_strategy_performance(strategy)
        log_strategy_performance(strategy, detailed=True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
