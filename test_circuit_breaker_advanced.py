"""
test_circuit_breaker_advanced.py - Tests für erweiterte Circuit Breaker Logik
==============================================================================
Unit and integration tests for the advanced circuit breaker functionality.
"""

import unittest
import logging
from unittest.mock import MagicMock, patch, call
import numpy as np

# Import classes to test
from circuit_breaker import (
    CircuitBreakerManager,
    CircuitBreakerThreshold,
    CircuitBreakerActions
)


class TestCircuitBreakerThreshold(unittest.TestCase):
    """Tests für CircuitBreakerThreshold Dataclass"""
    
    def test_threshold_creation(self):
        """Test: Threshold erstellen"""
        threshold = CircuitBreakerThreshold(
            level=10.0,
            actions=[lambda: None],
            description="Test Threshold"
        )
        
        self.assertEqual(threshold.level, 10.0)
        self.assertEqual(len(threshold.actions), 1)
        self.assertEqual(threshold.description, "Test Threshold")
        self.assertFalse(threshold.triggered)


class TestCircuitBreakerManager(unittest.TestCase):
    """Tests für CircuitBreakerManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = CircuitBreakerManager()
    
    def test_initialization(self):
        """Test: Manager Initialisierung"""
        self.assertTrue(self.manager.enabled)
        self.assertTrue(self.manager.only_production)
        self.assertEqual(len(self.manager.thresholds), 0)
        self.assertFalse(self.manager.triggered)
        self.assertIsNone(self.manager.triggered_level)
    
    def test_add_threshold(self):
        """Test: Schwellenwert hinzufügen"""
        action = lambda: None
        self.manager.add_threshold(
            level=10.0,
            actions=[action],
            description="Test"
        )
        
        self.assertEqual(len(self.manager.thresholds), 1)
        self.assertEqual(self.manager.thresholds[0].level, 10.0)
        self.assertEqual(self.manager.thresholds[0].description, "Test")
    
    def test_add_threshold_invalid_level(self):
        """Test: Ungültiger Schwellenwert (negativ)"""
        with self.assertRaises(ValueError):
            self.manager.add_threshold(
                level=-10.0,
                actions=[lambda: None]
            )
    
    def test_thresholds_sorted(self):
        """Test: Schwellenwerte werden sortiert"""
        self.manager.add_threshold(level=20.0, actions=[lambda: None])
        self.manager.add_threshold(level=10.0, actions=[lambda: None])
        self.manager.add_threshold(level=15.0, actions=[lambda: None])
        
        levels = [t.level for t in self.manager.thresholds]
        self.assertEqual(levels, [10.0, 15.0, 20.0])
    
    def test_configure_from_dict(self):
        """Test: Konfiguration aus Dictionary"""
        config = {
            10.0: {
                'actions': [lambda: None],
                'description': 'Level 1'
            },
            20.0: {
                'actions': [lambda: None, lambda: None],
                'description': 'Level 2'
            }
        }
        
        self.manager.configure_from_dict(config)
        
        self.assertEqual(len(self.manager.thresholds), 2)
        self.assertEqual(self.manager.thresholds[0].level, 10.0)
        self.assertEqual(self.manager.thresholds[1].level, 20.0)
        self.assertEqual(len(self.manager.thresholds[1].actions), 2)
    
    def test_update_equity(self):
        """Test: Equity Curve Update"""
        self.manager.update_equity(10000)
        self.manager.update_equity(10500)
        
        self.assertEqual(len(self.manager.equity_curve), 2)
        self.assertEqual(self.manager.equity_curve[0], 10000)
        self.assertEqual(self.manager.equity_curve[1], 10500)
    
    def test_calculate_current_drawdown_no_drawdown(self):
        """Test: Kein Drawdown bei steigenden Werten"""
        self.manager.equity_curve = [10000, 10500, 11000]
        drawdown = self.manager.calculate_current_drawdown()
        self.assertEqual(drawdown, 0.0)
    
    def test_calculate_current_drawdown_with_drawdown(self):
        """Test: Drawdown berechnen"""
        self.manager.equity_curve = [10000, 11000, 9000]
        drawdown = self.manager.calculate_current_drawdown()
        # Peak: 11000, Current: 9000
        # DD = (9000 - 11000) / 11000 * 100 = -18.18%
        expected_dd = ((9000 - 11000) / 11000) * 100
        self.assertAlmostEqual(drawdown, expected_dd, places=2)
    
    def test_calculate_current_drawdown_empty_curve(self):
        """Test: Leere Equity Curve"""
        drawdown = self.manager.calculate_current_drawdown()
        self.assertEqual(drawdown, 0.0)
    
    def test_check_disabled(self):
        """Test: Circuit Breaker deaktiviert"""
        self.manager.enabled = False
        self.manager.add_threshold(level=10.0, actions=[lambda: None])
        
        triggered = self.manager.check(current_equity=8000, is_dry_run=False)
        self.assertFalse(triggered)
    
    def test_check_dry_run(self):
        """Test: Circuit Breaker in DRY_RUN nicht aktiv"""
        self.manager.add_threshold(level=10.0, actions=[lambda: None])
        self.manager.equity_curve = [10000]
        
        triggered = self.manager.check(current_equity=8000, is_dry_run=True)
        self.assertFalse(triggered)
    
    def test_check_no_thresholds(self):
        """Test: Keine Schwellenwerte konfiguriert"""
        triggered = self.manager.check(current_equity=8000, is_dry_run=False)
        self.assertFalse(triggered)
    
    def test_check_threshold_not_exceeded(self):
        """Test: Schwellenwert nicht überschritten"""
        self.manager.add_threshold(level=20.0, actions=[lambda: None])
        self.manager.equity_curve = [10000]
        
        triggered = self.manager.check(current_equity=9500, is_dry_run=False)
        self.assertFalse(triggered)
    
    def test_check_threshold_exceeded(self):
        """Test: Schwellenwert überschritten"""
        action_called = []
        
        def test_action():
            action_called.append(True)
        
        self.manager.add_threshold(level=10.0, actions=[test_action])
        self.manager.equity_curve = [10000]
        
        triggered = self.manager.check(current_equity=8500, is_dry_run=False)
        
        self.assertTrue(triggered)
        self.assertTrue(self.manager.triggered)
        self.assertEqual(self.manager.triggered_level, 10.0)
        self.assertEqual(len(action_called), 1)
    
    def test_check_multiple_thresholds(self):
        """Test: Mehrere Schwellenwerte"""
        actions_called = []
        
        self.manager.add_threshold(
            level=10.0,
            actions=[lambda: actions_called.append('10%')]
        )
        self.manager.add_threshold(
            level=20.0,
            actions=[lambda: actions_called.append('20%')]
        )
        
        # Ersten Schwellenwert überschreiten
        self.manager.check(current_equity=10000, is_dry_run=False)
        self.manager.check(current_equity=8500, is_dry_run=False)
        
        self.assertEqual(len(actions_called), 1)
        self.assertEqual(actions_called[0], '10%')
        
        # Zweiten Schwellenwert überschreiten
        self.manager.check(current_equity=7500, is_dry_run=False)
        
        self.assertEqual(len(actions_called), 2)
        self.assertEqual(actions_called[1], '20%')
    
    def test_check_action_error_handling(self):
        """Test: Fehlerbehandlung bei Action-Ausführung"""
        def failing_action():
            raise Exception("Test Error")
        
        self.manager.add_threshold(level=10.0, actions=[failing_action])
        self.manager.equity_curve = [10000]
        
        # Sollte nicht abstürzen, sondern Fehler loggen
        triggered = self.manager.check(current_equity=8000, is_dry_run=False)
        self.assertTrue(triggered)
    
    def test_get_status(self):
        """Test: Status abrufen"""
        self.manager.add_threshold(level=10.0, actions=[lambda: None])
        self.manager.equity_curve = [10000, 9000]
        
        status = self.manager.get_status()
        
        self.assertIn('enabled', status)
        self.assertIn('only_production', status)
        self.assertIn('triggered', status)
        self.assertIn('triggered_level', status)
        self.assertIn('current_drawdown', status)
        self.assertIn('thresholds', status)
        self.assertIn('equity_curve_length', status)
        
        self.assertTrue(status['enabled'])
        self.assertEqual(status['equity_curve_length'], 2)
    
    def test_reset(self):
        """Test: Reset Circuit Breaker"""
        self.manager.add_threshold(level=10.0, actions=[lambda: None])
        self.manager.equity_curve = [10000]
        self.manager.check(current_equity=8000, is_dry_run=False)
        
        self.assertTrue(self.manager.triggered)
        
        self.manager.reset()
        
        self.assertFalse(self.manager.triggered)
        self.assertIsNone(self.manager.triggered_level)
        for threshold in self.manager.thresholds:
            self.assertFalse(threshold.triggered)
    
    def test_reset_equity_curve(self):
        """Test: Reset Equity Curve"""
        self.manager.equity_curve = [10000, 9000, 8000]
        self.assertEqual(len(self.manager.equity_curve), 3)
        
        self.manager.reset_equity_curve()
        
        self.assertEqual(len(self.manager.equity_curve), 0)


class TestCircuitBreakerActions(unittest.TestCase):
    """Tests für CircuitBreakerActions Factory"""
    
    def test_create_log_action(self):
        """Test: Log-Action erstellen"""
        action = CircuitBreakerActions.create_log_action(
            message="Test Log",
            level="info"
        )
        
        self.assertTrue(callable(action))
        # Action sollte ohne Fehler ausführbar sein
        action()
    
    def test_create_alert_action(self):
        """Test: Alert-Action erstellen"""
        mock_alert_manager = MagicMock()
        
        action = CircuitBreakerActions.create_alert_action(
            alert_manager=mock_alert_manager,
            drawdown=-15.0,
            limit=10.0,
            capital=8500.0,
            initial_capital=10000.0
        )
        
        action()
        
        mock_alert_manager.send_circuit_breaker_alert.assert_called_once_with(
            drawdown=-15.0,
            limit=10.0,
            capital=8500.0,
            initial_capital=10000.0
        )
    
    def test_create_pause_trading_action(self):
        """Test: Pause-Trading-Action erstellen"""
        mock_bot = MagicMock()
        mock_bot.pause = MagicMock()
        
        action = CircuitBreakerActions.create_pause_trading_action(mock_bot)
        action()
        
        mock_bot.pause.assert_called_once()
    
    def test_create_pause_trading_action_fallback(self):
        """Test: Pause-Trading-Action Fallback (circuit_breaker_triggered Flag)"""
        mock_bot = MagicMock()
        mock_bot.circuit_breaker_triggered = False
        del mock_bot.pause  # Entferne pause Methode
        
        action = CircuitBreakerActions.create_pause_trading_action(mock_bot)
        action()
        
        self.assertTrue(mock_bot.circuit_breaker_triggered)
    
    def test_create_shutdown_action(self):
        """Test: Shutdown-Action erstellen"""
        mock_bot = MagicMock()
        mock_bot.shutdown = MagicMock()
        mock_bot.circuit_breaker_triggered = False
        
        action = CircuitBreakerActions.create_shutdown_action(mock_bot)
        action()
        
        self.assertTrue(mock_bot.circuit_breaker_triggered)
    
    def test_create_rebalance_action(self):
        """Test: Rebalance-Action erstellen"""
        mock_portfolio = MagicMock()
        mock_portfolio.rebalance = MagicMock()
        
        action = CircuitBreakerActions.create_rebalance_action(mock_portfolio)
        action()
        
        mock_portfolio.rebalance.assert_called_once()
    
    def test_create_rebalance_action_no_manager(self):
        """Test: Rebalance-Action ohne Portfolio Manager"""
        action = CircuitBreakerActions.create_rebalance_action(None)
        # Sollte ohne Fehler ausführbar sein
        action()
    
    def test_create_custom_action(self):
        """Test: Custom-Action erstellen"""
        custom_called = []
        
        def custom_func():
            custom_called.append(True)
        
        action = CircuitBreakerActions.create_custom_action(
            func=custom_func,
            description="Test Custom Action"
        )
        
        action()
        
        self.assertEqual(len(custom_called), 1)


class TestCircuitBreakerIntegration(unittest.TestCase):
    """Integration Tests für Circuit Breaker"""
    
    def test_full_workflow(self):
        """Test: Kompletter Workflow mit mehreren Schwellenwerten"""
        manager = CircuitBreakerManager()
        
        actions_log = []
        
        # Konfiguriere Schwellenwerte
        manager.add_threshold(
            level=10.0,
            actions=[lambda: actions_log.append('warning')],
            description="Warning"
        )
        manager.add_threshold(
            level=20.0,
            actions=[lambda: actions_log.append('critical')],
            description="Critical"
        )
        
        # Simuliere Trading mit Drawdown
        equity_values = [10000, 10500, 9500, 8800, 8000]
        
        for equity in equity_values:
            manager.check(equity, is_dry_run=False)
        
        # Beide Schwellenwerte sollten ausgelöst worden sein
        self.assertEqual(len(actions_log), 2)
        self.assertIn('warning', actions_log)
        self.assertIn('critical', actions_log)
        
        # Status prüfen
        status = manager.get_status()
        self.assertTrue(status['triggered'])
        self.assertEqual(status['triggered_level'], 20.0)
        self.assertLess(status['current_drawdown'], -20.0)
    
    def test_with_alert_manager_integration(self):
        """Test: Integration mit AlertManager"""
        manager = CircuitBreakerManager()
        mock_alert_manager = MagicMock()
        
        # Konfiguriere mit Alert-Action
        manager.add_threshold(
            level=15.0,
            actions=[
                CircuitBreakerActions.create_alert_action(
                    alert_manager=mock_alert_manager,
                    drawdown=-15.5,
                    limit=15.0,
                    capital=8450.0,
                    initial_capital=10000.0
                )
            ]
        )
        
        # Simuliere Drawdown
        manager.check(10000, is_dry_run=False)
        manager.check(8450, is_dry_run=False)
        
        # Alert sollte gesendet worden sein
        mock_alert_manager.send_circuit_breaker_alert.assert_called()


def run_tests():
    """Run all advanced circuit breaker tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Lade alle Test-Klassen
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerThreshold))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerManager))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerActions))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerIntegration))
    
    # Führe Tests aus
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.CRITICAL)  # Suppress logs during tests
    success = run_tests()
    sys.exit(0 if success else 1)
