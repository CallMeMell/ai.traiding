"""
test_circuit_breaker.py - Tests für Circuit Breaker (Drawdown-Limit)
===================================================================
Unit tests for the circuit breaker functionality in live trading.
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import numpy as np

# Import functions to test
from utils import calculate_current_drawdown, calculate_max_drawdown
from automation.runner import AutomationRunner
from config import TradingConfig


class TestDrawdownCalculations(unittest.TestCase):
    """Tests für Drawdown-Berechnungen"""
    
    def test_calculate_current_drawdown_no_drawdown(self):
        """Test: Kein Drawdown bei steigenden Werten"""
        equity_curve = [10000, 10100, 10200, 10300]
        current_dd = calculate_current_drawdown(equity_curve)
        self.assertEqual(current_dd, 0.0)
    
    def test_calculate_current_drawdown_with_drawdown(self):
        """Test: Drawdown bei fallenden Werten"""
        equity_curve = [10000, 10500, 10000, 9000]
        current_dd = calculate_current_drawdown(equity_curve)
        # Peak is 10500, current is 9000
        # DD = (9000 - 10500) / 10500 * 100 = -14.29%
        expected_dd = ((9000 - 10500) / 10500) * 100
        self.assertAlmostEqual(current_dd, expected_dd, places=2)
    
    def test_calculate_current_drawdown_empty_curve(self):
        """Test: Leere Equity Curve"""
        equity_curve = []
        current_dd = calculate_current_drawdown(equity_curve)
        self.assertEqual(current_dd, 0.0)
    
    def test_calculate_current_drawdown_single_value(self):
        """Test: Einzelner Wert in Equity Curve"""
        equity_curve = [10000]
        current_dd = calculate_current_drawdown(equity_curve)
        self.assertEqual(current_dd, 0.0)
    
    def test_calculate_current_drawdown_20_percent(self):
        """Test: Genau 20% Drawdown"""
        equity_curve = [10000, 10000, 8000]
        current_dd = calculate_current_drawdown(equity_curve)
        # DD = (8000 - 10000) / 10000 * 100 = -20%
        self.assertAlmostEqual(current_dd, -20.0, places=2)
    
    def test_calculate_max_drawdown_basic(self):
        """Test: Maximum Drawdown Berechnung"""
        equity_curve = [10000, 11000, 9000, 10000]
        max_dd_pct, max_dd_val, peak_val, trough_val = calculate_max_drawdown(equity_curve)
        # Peak: 11000, Trough: 9000
        # Max DD = (9000 - 11000) / 11000 * 100 = -18.18%
        expected_dd_pct = ((9000 - 11000) / 11000) * 100
        self.assertAlmostEqual(max_dd_pct, expected_dd_pct, places=2)
        self.assertEqual(peak_val, 11000)
        self.assertEqual(trough_val, 9000)


class TestCircuitBreakerConfig(unittest.TestCase):
    """Tests für Circuit Breaker Konfiguration"""
    
    def test_config_has_drawdown_limit(self):
        """Test: Config hat max_drawdown_limit Parameter"""
        config = TradingConfig()
        self.assertTrue(hasattr(config, 'max_drawdown_limit'))
        self.assertIsInstance(config.max_drawdown_limit, float)
        self.assertGreater(config.max_drawdown_limit, 0.0)
        self.assertLessEqual(config.max_drawdown_limit, 1.0)
    
    def test_config_validation_drawdown_limit(self):
        """Test: Config Validierung für max_drawdown_limit"""
        config = TradingConfig()
        
        # Valid value
        config.max_drawdown_limit = 0.20
        is_valid, error = config.validate()
        self.assertTrue(is_valid)
        
        # Invalid value (negative)
        config.max_drawdown_limit = -0.1
        is_valid, error = config.validate()
        self.assertFalse(is_valid)
        self.assertIn('max_drawdown_limit', error)
        
        # Invalid value (> 1)
        config.max_drawdown_limit = 1.5
        is_valid, error = config.validate()
        self.assertFalse(is_valid)
        self.assertIn('max_drawdown_limit', error)


class TestCircuitBreakerAutomationRunner(unittest.TestCase):
    """Tests für Circuit Breaker in AutomationRunner"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.events_path = os.path.join(self.test_dir, "events.jsonl")
        self.summary_path = os.path.join(self.test_dir, "summary.json")
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_circuit_breaker_not_triggered_in_dry_run(self):
        """Test: Circuit Breaker wird in DRY_RUN nicht ausgelöst"""
        with patch.dict(os.environ, {'DRY_RUN': 'true'}):
            runner = AutomationRunner(
                data_phase_timeout=10,
                strategy_phase_timeout=10,
                api_phase_timeout=10,
                max_drawdown_limit=0.10  # 10% limit
            )
            
            # Simulate large drawdown
            self.assertFalse(runner.check_circuit_breaker(10000))
            self.assertFalse(runner.check_circuit_breaker(5000))  # 50% drawdown
            self.assertFalse(runner.circuit_breaker_triggered)
    
    def test_circuit_breaker_triggered_in_production(self):
        """Test: Circuit Breaker wird in Production ausgelöst"""
        with patch.dict(os.environ, {'DRY_RUN': 'false'}):
            runner = AutomationRunner(
                data_phase_timeout=10,
                strategy_phase_timeout=10,
                api_phase_timeout=10,
                max_drawdown_limit=0.20  # 20% limit
            )
            
            # Simulate equity progression with drawdown
            self.assertFalse(runner.check_circuit_breaker(10000))  # Initial
            self.assertFalse(runner.check_circuit_breaker(10500))  # +5%
            self.assertFalse(runner.check_circuit_breaker(9500))   # -9.5% from peak
            
            # Trigger circuit breaker with >20% drawdown
            triggered = runner.check_circuit_breaker(8000)  # -23.8% from peak
            self.assertTrue(triggered)
            self.assertTrue(runner.circuit_breaker_triggered)
    
    def test_circuit_breaker_threshold_exact(self):
        """Test: Circuit Breaker bei genauem Limit"""
        with patch.dict(os.environ, {'DRY_RUN': 'false'}):
            runner = AutomationRunner(
                data_phase_timeout=10,
                strategy_phase_timeout=10,
                api_phase_timeout=10,
                max_drawdown_limit=0.20  # 20% limit
            )
            
            # Build up to just over 20% drawdown
            runner.check_circuit_breaker(10000)  # Peak
            
            # Slightly more than 20% drawdown should trigger
            # -20.1% = 7990 from peak of 10000
            triggered = runner.check_circuit_breaker(7990)  # -20.1% from peak
            self.assertTrue(triggered)  # Should trigger at >-20%
            
            # Verify it's marked as triggered
            self.assertTrue(runner.circuit_breaker_triggered)
    
    def test_circuit_breaker_multiple_peaks(self):
        """Test: Circuit Breaker mit mehreren Peaks"""
        with patch.dict(os.environ, {'DRY_RUN': 'false'}):
            runner = AutomationRunner(
                data_phase_timeout=10,
                strategy_phase_timeout=10,
                api_phase_timeout=10,
                max_drawdown_limit=0.15  # 15% limit
            )
            
            # First peak
            runner.check_circuit_breaker(10000)
            runner.check_circuit_breaker(9000)  # -10%
            
            # New higher peak
            runner.check_circuit_breaker(11000)
            runner.check_circuit_breaker(10000)  # -9% from new peak
            
            # Trigger at >15% from highest peak
            triggered = runner.check_circuit_breaker(9300)  # -15.5% from 11000
            self.assertTrue(triggered)


class TestCircuitBreakerIntegration(unittest.TestCase):
    """Integration tests für Circuit Breaker"""
    
    def test_circuit_breaker_logs_critical_event(self):
        """Test: Circuit Breaker loggt kritisches Event"""
        with patch.dict(os.environ, {'DRY_RUN': 'false'}):
            runner = AutomationRunner(
                data_phase_timeout=10,
                strategy_phase_timeout=10,
                api_phase_timeout=10,
                max_drawdown_limit=0.20
            )
            
            # Simulate drawdown - only trigger once
            triggered_first = runner.check_circuit_breaker(10000)
            self.assertFalse(triggered_first)  # Should not trigger on first value
            
            triggered_second = runner.check_circuit_breaker(7500)  # -25% drawdown
            self.assertTrue(triggered_second)  # Should trigger on large drawdown
            
            # Verify event was logged
            events = runner.session_store.read_events()
            circuit_breaker_events = [e for e in events if e.get('type') == 'circuit_breaker']
            self.assertGreaterEqual(len(circuit_breaker_events), 1)  # At least one event
            
            # Check the first circuit breaker event
            event = circuit_breaker_events[0]
            self.assertEqual(event['level'], 'critical')
            self.assertEqual(event['status'], 'triggered')
            self.assertIn('current_drawdown_percent', event['details'])
            self.assertIn('drawdown_limit_percent', event['details'])


def run_tests():
    """Run all circuit breaker tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDrawdownCalculations))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerAutomationRunner))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
