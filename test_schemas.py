"""
test_schemas.py - Tests for Event and Summary Schemas
====================================================
Unit tests for schema validation functionality.
"""

import unittest
from datetime import datetime
from pydantic import ValidationError

from automation.schemas import Event, Summary, validate_event, validate_summary, MetricsData, OrderData
from automation.validate import validate_event_lenient, validate_summary_lenient


class TestEventSchema(unittest.TestCase):
    """Test Event schema validation."""
    
    def test_minimal_event(self):
        """Test minimal valid event."""
        event_dict = {
            'timestamp': datetime.now().isoformat(),
            'type': 'test_event'
        }
        event = validate_event(event_dict)
        self.assertEqual(event.type, 'test_event')
        self.assertEqual(event.level, 'info')  # default
    
    def test_full_event(self):
        """Test event with all fields."""
        event_dict = {
            'timestamp': '2024-01-01T12:00:00',
            'session_id': 'test_session',
            'type': 'phase_start',
            'phase': 'data_phase',
            'level': 'info',
            'message': 'Starting data phase',
            'metrics': {
                'equity': 10000.0,
                'pnl': 150.0,
                'win_rate': 0.6,
                'trades': 10,
                'wins': 6,
                'losses': 4
            },
            'order': {
                'symbol': 'BTCUSDT',
                'side': 'BUY',
                'qty': 0.1,
                'price': 50000.0,
                'status': 'FILLED'
            },
            'details': {
                'extra': 'info'
            },
            'status': 'success'
        }
        event = validate_event(event_dict)
        self.assertEqual(event.type, 'phase_start')
        self.assertEqual(event.phase, 'data_phase')
        self.assertIsNotNone(event.metrics)
        self.assertEqual(event.metrics.equity, 10000.0)
        self.assertIsNotNone(event.order)
        self.assertEqual(event.order.symbol, 'BTCUSDT')
    
    def test_invalid_timestamp(self):
        """Test event with invalid timestamp."""
        event_dict = {
            'timestamp': 'invalid_timestamp',
            'type': 'test_event'
        }
        with self.assertRaises(ValidationError):
            validate_event(event_dict)
    
    def test_missing_required_fields(self):
        """Test event missing required fields."""
        event_dict = {
            'timestamp': datetime.now().isoformat()
            # Missing 'type'
        }
        with self.assertRaises(ValidationError):
            validate_event(event_dict)
    
    def test_invalid_level(self):
        """Test event with invalid level."""
        event_dict = {
            'timestamp': datetime.now().isoformat(),
            'type': 'test_event',
            'level': 'invalid_level'
        }
        with self.assertRaises(ValidationError):
            validate_event(event_dict)
    
    def test_lenient_validation(self):
        """Test lenient validation doesn't raise exception."""
        event_dict = {
            'timestamp': 'invalid',
            'type': 'test'
        }
        result = validate_event_lenient(event_dict)
        self.assertIsNone(result)


class TestSummarySchema(unittest.TestCase):
    """Test Summary schema validation."""
    
    def test_minimal_summary(self):
        """Test minimal valid summary."""
        summary_dict = {
            'session_start': datetime.now().isoformat()
        }
        summary = validate_summary(summary_dict)
        self.assertEqual(summary.status, 'running')  # default
        self.assertEqual(summary.phases_completed, 0)  # default
    
    def test_full_summary(self):
        """Test summary with all fields."""
        summary_dict = {
            'session_id': 'test_session',
            'session_start': '2024-01-01T12:00:00',
            'session_end': '2024-01-01T14:00:00',
            'started_at': '2024-01-01T12:00:00',
            'ended_at': '2024-01-01T14:00:00',
            'status': 'completed',
            'phases_completed': 3,
            'phases_total': 3,
            'initial_capital': 10000.0,
            'current_equity': 10500.0,
            'totals': {
                'trades': 20,
                'wins': 12,
                'losses': 8
            },
            'roi': 5.0,
            'max_drawdown': -2.5,
            'runtime_secs': 7200.0,
            'last_updated': '2024-01-01T14:00:00'
        }
        summary = validate_summary(summary_dict)
        self.assertEqual(summary.status, 'completed')
        self.assertEqual(summary.phases_completed, 3)
        self.assertEqual(summary.roi, 5.0)
        self.assertIsNotNone(summary.totals)
        self.assertEqual(summary.totals.trades, 20)
    
    def test_invalid_session_start(self):
        """Test summary with invalid session_start."""
        summary_dict = {
            'session_start': 'invalid_timestamp'
        }
        with self.assertRaises(ValidationError):
            validate_summary(summary_dict)
    
    def test_missing_session_start(self):
        """Test summary missing required session_start."""
        summary_dict = {
            'status': 'running'
        }
        with self.assertRaises(ValidationError):
            validate_summary(summary_dict)
    
    def test_lenient_validation(self):
        """Test lenient validation doesn't raise exception."""
        summary_dict = {
            'session_start': 'invalid'
        }
        result = validate_summary_lenient(summary_dict)
        self.assertIsNone(result)


class TestMetricsData(unittest.TestCase):
    """Test MetricsData model."""
    
    def test_metrics_optional_fields(self):
        """Test that all metrics fields are optional."""
        metrics = MetricsData()
        self.assertIsNone(metrics.equity)
        self.assertIsNone(metrics.pnl)
        
        metrics = MetricsData(equity=10000.0, pnl=500.0)
        self.assertEqual(metrics.equity, 10000.0)
        self.assertEqual(metrics.pnl, 500.0)


class TestOrderData(unittest.TestCase):
    """Test OrderData model."""
    
    def test_order_optional_fields(self):
        """Test that all order fields are optional."""
        order = OrderData()
        self.assertIsNone(order.symbol)
        self.assertIsNone(order.side)
        
        order = OrderData(symbol='BTCUSDT', side='BUY', qty=0.1)
        self.assertEqual(order.symbol, 'BTCUSDT')
        self.assertEqual(order.side, 'BUY')
        self.assertEqual(order.qty, 0.1)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestEventSchema))
    suite.addTests(loader.loadTestsFromTestCase(TestSummarySchema))
    suite.addTests(loader.loadTestsFromTestCase(TestMetricsData))
    suite.addTests(loader.loadTestsFromTestCase(TestOrderData))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
