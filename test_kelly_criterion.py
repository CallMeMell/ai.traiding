"""
test_kelly_criterion.py - Tests für Kelly Criterion Implementation
===================================================================
Unit tests für Kelly Criterion Position Sizing
"""

import unittest
import logging
from utils import (
    calculate_kelly_criterion,
    calculate_kelly_position_size,
    calculate_performance_metrics
)
from config import TradingConfig

# Setup logging für Tests
logging.basicConfig(level=logging.WARNING)


class TestKellyCriterion(unittest.TestCase):
    """Test cases für Kelly Criterion Berechnungen"""
    
    def test_kelly_criterion_positive_edge(self):
        """Test Kelly Criterion mit positivem Edge"""
        # 60% Gewinnrate, Win/Loss Ratio 1.5
        kelly = calculate_kelly_criterion(
            win_rate=0.6,
            avg_win=150,
            avg_loss=100,
            kelly_fraction=1.0
        )
        
        # Erwarteter Kelly: (0.6 * 1.5 - 0.4) / 1.5 = (0.9 - 0.4) / 1.5 = 0.333... = 33.33%
        self.assertAlmostEqual(kelly, 0.3333, places=2)
        self.assertGreater(kelly, 0)
        self.assertLessEqual(kelly, 1.0)
    
    def test_kelly_criterion_negative_edge(self):
        """Test Kelly Criterion mit negativem Edge (kein Trade)"""
        # 40% Gewinnrate, Win/Loss Ratio 1.0 -> negativer Kelly
        kelly = calculate_kelly_criterion(
            win_rate=0.4,
            avg_win=100,
            avg_loss=100,
            kelly_fraction=1.0
        )
        
        # Bei negativem Edge sollte Kelly 0 sein
        self.assertEqual(kelly, 0.0)
    
    def test_kelly_criterion_half_kelly(self):
        """Test Half Kelly (konservativerer Ansatz)"""
        # Voller Kelly
        full_kelly = calculate_kelly_criterion(
            win_rate=0.6,
            avg_win=150,
            avg_loss=100,
            kelly_fraction=1.0
        )
        
        # Half Kelly
        half_kelly = calculate_kelly_criterion(
            win_rate=0.6,
            avg_win=150,
            avg_loss=100,
            kelly_fraction=0.5
        )
        
        # Half Kelly sollte genau die Hälfte sein
        self.assertAlmostEqual(half_kelly, full_kelly * 0.5, places=4)
    
    def test_kelly_criterion_boundary_cases(self):
        """Test Grenzfälle"""
        # 100% Gewinnrate
        kelly_100 = calculate_kelly_criterion(
            win_rate=1.0,
            avg_win=100,
            avg_loss=1,
            kelly_fraction=1.0
        )
        self.assertGreater(kelly_100, 0)
        self.assertLessEqual(kelly_100, 1.0)
        
        # 0% Gewinnrate
        kelly_0 = calculate_kelly_criterion(
            win_rate=0.0,
            avg_win=100,
            avg_loss=100,
            kelly_fraction=1.0
        )
        self.assertEqual(kelly_0, 0.0)
        
        # 50% Gewinnrate, gleiche Wins/Losses
        kelly_50 = calculate_kelly_criterion(
            win_rate=0.5,
            avg_win=100,
            avg_loss=100,
            kelly_fraction=1.0
        )
        self.assertEqual(kelly_50, 0.0)
    
    def test_kelly_criterion_validation(self):
        """Test Validierung von Eingabeparametern"""
        # Ungültige win_rate
        kelly = calculate_kelly_criterion(
            win_rate=1.5,  # > 1.0
            avg_win=100,
            avg_loss=100,
            kelly_fraction=1.0
        )
        self.assertEqual(kelly, 0.0)
        
        # Ungültiger avg_win
        kelly = calculate_kelly_criterion(
            win_rate=0.6,
            avg_win=-100,  # negativ
            avg_loss=100,
            kelly_fraction=1.0
        )
        self.assertEqual(kelly, 0.0)
        
        # Ungültiger avg_loss
        kelly = calculate_kelly_criterion(
            win_rate=0.6,
            avg_win=100,
            avg_loss=0,  # null
            kelly_fraction=1.0
        )
        self.assertEqual(kelly, 0.0)
    
    def test_kelly_position_size(self):
        """Test konkrete Positionsgrößenberechnung"""
        capital = 10000.0
        position = calculate_kelly_position_size(
            capital=capital,
            win_rate=0.6,
            avg_win=150,
            avg_loss=100,
            kelly_fraction=0.5,
            max_position_pct=0.25
        )
        
        # Position sollte positiv sein
        self.assertGreater(position, 0)
        
        # Position sollte nicht das gesamte Kapital sein
        self.assertLess(position, capital)
        
        # Position sollte nicht mehr als max_position_pct sein
        self.assertLessEqual(position, capital * 0.25)
    
    def test_kelly_position_size_respects_maximum(self):
        """Test dass Maximum respektiert wird"""
        capital = 10000.0
        
        # Kelly würde 30% empfehlen (siehe test_kelly_criterion_positive_edge)
        # Aber wir limitieren auf 20%
        position = calculate_kelly_position_size(
            capital=capital,
            win_rate=0.6,
            avg_win=150,
            avg_loss=100,
            kelly_fraction=1.0,
            max_position_pct=0.20  # Max 20%
        )
        
        # Position sollte nicht mehr als 20% sein
        self.assertLessEqual(position, capital * 0.20)
    
    def test_kelly_position_size_zero_capital(self):
        """Test mit null Kapital"""
        position = calculate_kelly_position_size(
            capital=0,
            win_rate=0.6,
            avg_win=150,
            avg_loss=100
        )
        
        self.assertEqual(position, 0.0)
    
    def test_kelly_position_size_negative_capital(self):
        """Test mit negativem Kapital"""
        position = calculate_kelly_position_size(
            capital=-1000,
            win_rate=0.6,
            avg_win=150,
            avg_loss=100
        )
        
        self.assertEqual(position, 0.0)


class TestKellyConfig(unittest.TestCase):
    """Test cases für Kelly Criterion Konfiguration"""
    
    def test_kelly_config_disabled_by_default(self):
        """Test dass Kelly standardmäßig deaktiviert ist"""
        config = TradingConfig()
        self.assertFalse(config.enable_kelly_criterion)
    
    def test_kelly_config_default_values(self):
        """Test Default-Werte für Kelly Parameter"""
        config = TradingConfig()
        self.assertEqual(config.kelly_fraction, 0.5)  # Half Kelly
        self.assertEqual(config.kelly_max_position_pct, 0.25)  # 25% max
        self.assertEqual(config.kelly_lookback_trades, 20)
    
    def test_kelly_config_validation_enabled(self):
        """Test Validierung bei aktiviertem Kelly"""
        # Valide Konfiguration
        config = TradingConfig()
        config.enable_kelly_criterion = True
        is_valid, error = config.validate()
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Ungültiger kelly_fraction
        config.kelly_fraction = 1.5
        is_valid, error = config.validate()
        self.assertFalse(is_valid)
        self.assertIn("kelly_fraction", error)
        
        # Ungültiger kelly_max_position_pct
        config.kelly_fraction = 0.5
        config.kelly_max_position_pct = -0.1
        is_valid, error = config.validate()
        self.assertFalse(is_valid)
        self.assertIn("kelly_max_position_pct", error)
        
        # Ungültiger kelly_lookback_trades
        config.kelly_max_position_pct = 0.25
        config.kelly_lookback_trades = 2
        is_valid, error = config.validate()
        self.assertFalse(is_valid)
        self.assertIn("kelly_lookback_trades", error)


class TestKellyScenarios(unittest.TestCase):
    """Test verschiedene Trading-Szenarien mit Kelly Criterion"""
    
    def test_scenario_high_winrate_small_wins(self):
        """Scenario: Hohe Gewinnrate aber kleine Gewinne"""
        # 70% Gewinnrate, aber Wins nur 50% größer als Losses
        kelly = calculate_kelly_criterion(
            win_rate=0.7,
            avg_win=75,
            avg_loss=50,
            kelly_fraction=1.0
        )
        
        # Kelly sollte positiv aber moderat sein
        self.assertGreater(kelly, 0.2)
        self.assertLess(kelly, 0.5)
    
    def test_scenario_low_winrate_big_wins(self):
        """Scenario: Niedrige Gewinnrate aber große Gewinne"""
        # 40% Gewinnrate, aber Wins 3x größer als Losses
        kelly = calculate_kelly_criterion(
            win_rate=0.4,
            avg_win=300,
            avg_loss=100,
            kelly_fraction=1.0
        )
        
        # Kelly sollte positiv sein (gutes Win/Loss Ratio kompensiert)
        self.assertGreater(kelly, 0)
    
    def test_scenario_breakeven_strategy(self):
        """Scenario: Break-even Strategie"""
        # 50% Gewinnrate, gleiche Wins/Losses
        kelly = calculate_kelly_criterion(
            win_rate=0.5,
            avg_win=100,
            avg_loss=100,
            kelly_fraction=1.0
        )
        
        # Kelly sollte 0 sein (kein Edge)
        self.assertEqual(kelly, 0.0)
    
    def test_scenario_realistic_trading(self):
        """Scenario: Realistisches Trading-Szenario"""
        # 55% Gewinnrate, Win/Loss Ratio 1.2
        capital = 10000.0
        position = calculate_kelly_position_size(
            capital=capital,
            win_rate=0.55,
            avg_win=120,
            avg_loss=100,
            kelly_fraction=0.5,  # Half Kelly für Sicherheit
            max_position_pct=0.25
        )
        
        # Position sollte zwischen 2% und 10% des Kapitals sein
        self.assertGreater(position, capital * 0.02)
        self.assertLess(position, capital * 0.10)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestKellyCriterion))
    suite.addTests(loader.loadTestsFromTestCase(TestKellyConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestKellyScenarios))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("=" * 70)
    print("KELLY CRITERION TESTS")
    print("=" * 70)
    result = run_tests()
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    
    exit(0 if result.wasSuccessful() else 1)
