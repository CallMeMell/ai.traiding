"""
test_schema_validators.py - Schema Validation Tests
=================================================
Unit tests for event and summary schema validation.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from pydantic import ValidationError

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from automation.schemas import (
    Event, Summary, MetricsData, OrderData, SummaryTotals,
    validate_event, validate_summary
)
from automation.validate import (
    validate_event_lenient, validate_summary_lenient,
    validate_event_strict, validate_summary_strict
)


class TestEventSchema:
    """Test Event schema validation."""
    
    def test_event_minimal_valid(self):
        """Test minimal valid event."""
        event_dict = {
            'timestamp': datetime.now().isoformat(),
            'type': 'session_start'
        }
        
        event = validate_event(event_dict)
        
        assert event.timestamp is not None
        assert event.type == 'session_start'
        assert event.level == 'info'  # Default value
    
    def test_event_full_valid(self):
        """Test fully populated valid event."""
        event_dict = {
            'timestamp': datetime.now().isoformat(),
            'session_id': 'TEST123',
            'type': 'checkpoint',
            'phase': 'data_phase',
            'level': 'info',
            'message': 'Test checkpoint',
            'metrics': {
                'equity': 10100.0,
                'pnl': 100.0,
                'win_rate': 60.0,
                'trades': 5,
                'wins': 3,
                'losses': 2
            },
            'status': 'success',
            'duration_seconds': 120.5
        }
        
        event = validate_event(event_dict)
        
        assert event.type == 'checkpoint'
        assert event.phase == 'data_phase'
        assert event.metrics.equity == 10100.0
        assert event.metrics.pnl == 100.0
        assert event.duration_seconds == 120.5
    
    def test_event_with_order_data(self):
        """Test event with order data."""
        event_dict = {
            'timestamp': datetime.now().isoformat(),
            'type': 'order_placed',
            'order': {
                'symbol': 'BTCUSDT',
                'side': 'BUY',
                'qty': 0.001,
                'price': 50000.0,
                'status': 'filled'
            }
        }
        
        event = validate_event(event_dict)
        
        assert event.order is not None
        assert event.order.symbol == 'BTCUSDT'
        assert event.order.side == 'BUY'
        assert event.order.qty == 0.001
    
    def test_event_invalid_timestamp(self):
        """Test event with invalid timestamp fails validation."""
        event_dict = {
            'timestamp': 'invalid-timestamp',
            'type': 'test'
        }
        
        with pytest.raises(ValidationError):
            validate_event(event_dict)
    
    def test_event_invalid_level(self):
        """Test event with invalid log level fails validation."""
        event_dict = {
            'timestamp': datetime.now().isoformat(),
            'type': 'test',
            'level': 'invalid_level'
        }
        
        with pytest.raises(ValidationError):
            validate_event(event_dict)
    
    def test_event_missing_required_fields(self):
        """Test event missing required fields fails validation."""
        event_dict = {
            'timestamp': datetime.now().isoformat()
            # Missing 'type' field
        }
        
        with pytest.raises(ValidationError):
            validate_event(event_dict)


class TestSummarySchema:
    """Test Summary schema validation."""
    
    def test_summary_minimal_valid(self):
        """Test minimal valid summary."""
        summary_dict = {
            'session_start': datetime.now().isoformat()
        }
        
        summary = validate_summary(summary_dict)
        
        assert summary.session_start is not None
        assert summary.status == 'running'  # Default value
        assert summary.phases_completed == 0  # Default value
        assert summary.initial_capital == 10000.0  # Default value
    
    def test_summary_full_valid(self):
        """Test fully populated valid summary."""
        summary_dict = {
            'session_id': 'TEST123',
            'session_start': datetime.now().isoformat(),
            'session_end': datetime.now().isoformat(),
            'status': 'completed',
            'phases_completed': 3,
            'phases_total': 3,
            'initial_capital': 10000.0,
            'current_equity': 10500.0,
            'totals': {
                'trades': 10,
                'wins': 6,
                'losses': 4
            },
            'roi': 5.0,
            'max_drawdown': 2.5,
            'runtime_secs': 3600.0,
            'last_updated': datetime.now().isoformat()
        }
        
        summary = validate_summary(summary_dict)
        
        assert summary.session_id == 'TEST123'
        assert summary.status == 'completed'
        assert summary.phases_completed == 3
        assert summary.current_equity == 10500.0
        assert summary.totals.trades == 10
        assert summary.roi == 5.0
    
    def test_summary_invalid_timestamp(self):
        """Test summary with invalid timestamp fails validation."""
        summary_dict = {
            'session_start': 'invalid-timestamp'
        }
        
        with pytest.raises(ValidationError):
            validate_summary(summary_dict)
    
    def test_summary_negative_capital(self):
        """Test summary accepts negative capital (for losses)."""
        summary_dict = {
            'session_start': datetime.now().isoformat(),
            'initial_capital': 10000.0,
            'current_equity': -500.0  # Significant loss
        }
        
        summary = validate_summary(summary_dict)
        
        assert summary.current_equity == -500.0


class TestValidationHelpers:
    """Test validation helper functions."""
    
    def test_validate_event_lenient_valid(self):
        """Test lenient validation with valid event."""
        event_dict = {
            'timestamp': datetime.now().isoformat(),
            'type': 'test'
        }
        
        event = validate_event_lenient(event_dict)
        
        assert event is not None
        assert event.type == 'test'
    
    def test_validate_event_lenient_invalid(self):
        """Test lenient validation with invalid event returns None."""
        event_dict = {
            'timestamp': 'invalid',
            'type': 'test'
        }
        
        event = validate_event_lenient(event_dict)
        
        assert event is None
    
    def test_validate_event_strict_valid(self):
        """Test strict validation with valid event."""
        event_dict = {
            'timestamp': datetime.now().isoformat(),
            'type': 'test'
        }
        
        event = validate_event_strict(event_dict)
        
        assert event is not None
        assert event.type == 'test'
    
    def test_validate_event_strict_invalid(self):
        """Test strict validation with invalid event raises exception."""
        event_dict = {
            'timestamp': 'invalid',
            'type': 'test'
        }
        
        with pytest.raises(ValidationError):
            validate_event_strict(event_dict)
    
    def test_validate_summary_lenient_valid(self):
        """Test lenient summary validation with valid data."""
        summary_dict = {
            'session_start': datetime.now().isoformat()
        }
        
        summary = validate_summary_lenient(summary_dict)
        
        assert summary is not None
        assert summary.status == 'running'
    
    def test_validate_summary_lenient_invalid(self):
        """Test lenient summary validation with invalid data returns None."""
        summary_dict = {
            'session_start': 'invalid'
        }
        
        summary = validate_summary_lenient(summary_dict)
        
        assert summary is None
    
    def test_validate_summary_strict_valid(self):
        """Test strict summary validation with valid data."""
        summary_dict = {
            'session_start': datetime.now().isoformat()
        }
        
        summary = validate_summary_strict(summary_dict)
        
        assert summary is not None
        assert summary.status == 'running'
    
    def test_validate_summary_strict_invalid(self):
        """Test strict summary validation with invalid data raises exception."""
        summary_dict = {
            'session_start': 'invalid'
        }
        
        with pytest.raises(ValidationError):
            validate_summary_strict(summary_dict)


class TestMetricsData:
    """Test MetricsData schema."""
    
    def test_metrics_data_all_fields(self):
        """Test metrics data with all fields."""
        metrics = MetricsData(
            equity=10000.0,
            pnl=100.0,
            win_rate=60.0,
            trades=10,
            wins=6,
            losses=4
        )
        
        assert metrics.equity == 10000.0
        assert metrics.pnl == 100.0
        assert metrics.win_rate == 60.0
        assert metrics.trades == 10
    
    def test_metrics_data_partial_fields(self):
        """Test metrics data with partial fields."""
        metrics = MetricsData(
            equity=10000.0,
            pnl=100.0
        )
        
        assert metrics.equity == 10000.0
        assert metrics.pnl == 100.0
        assert metrics.win_rate is None


class TestOrderData:
    """Test OrderData schema."""
    
    def test_order_data_all_fields(self):
        """Test order data with all fields."""
        order = OrderData(
            symbol='BTCUSDT',
            side='BUY',
            qty=0.001,
            price=50000.0,
            status='filled'
        )
        
        assert order.symbol == 'BTCUSDT'
        assert order.side == 'BUY'
        assert order.qty == 0.001
        assert order.price == 50000.0
    
    def test_order_data_partial_fields(self):
        """Test order data with partial fields."""
        order = OrderData(
            symbol='BTCUSDT',
            side='BUY'
        )
        
        assert order.symbol == 'BTCUSDT'
        assert order.side == 'BUY'
        assert order.qty is None
