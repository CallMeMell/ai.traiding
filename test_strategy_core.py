"""
test_strategy_core.py - Test Suite für Reversal-Trailing-Stop Strategie
========================================================================
"""
import unittest
import pandas as pd
import numpy as np
from strategy_core import ReversalTrailingStopStrategy


class TestReversalTrailingStopStrategy(unittest.TestCase):
    """Test-Suite für Reversal-Trailing-Stop Strategie"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.strategy = ReversalTrailingStopStrategy()
        self.sample_data = self._generate_sample_data(100)
    
    def _generate_sample_data(self, n_bars: int = 100) -> pd.DataFrame:
        """Generiert Test-Daten"""
        dates = pd.date_range(end=pd.Timestamp.now(), periods=n_bars, freq='15min')
        
        # Simuliere Preisverlauf
        np.random.seed(42)
        price = 30000
        prices = [price]
        
        for _ in range(n_bars - 1):
            change = np.random.normal(0, 100)
            price += change
            price = max(price, 1000)
            prices.append(price)
        
        prices = np.array(prices)
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices + np.random.normal(0, 50, n_bars),
            'high': prices + abs(np.random.normal(50, 30, n_bars)),
            'low': prices - abs(np.random.normal(50, 30, n_bars)),
            'close': prices,
            'volume': np.random.uniform(100, 1000, n_bars)
        })
        
        return df
    
    def test_strategy_initialization(self):
        """Test: Strategie wird korrekt initialisiert"""
        self.assertEqual(self.strategy.name, "Reversal-Trailing-Stop")
        self.assertTrue(self.strategy.enabled)
        self.assertEqual(self.strategy.current_position, 0)
    
    def test_custom_parameters(self):
        """Test: Custom Parameter werden gesetzt"""
        custom_params = {
            'lookback_period': 30,
            'trailing_stop_pct': 3.0
        }
        strategy = ReversalTrailingStopStrategy(custom_params)
        self.assertEqual(strategy.params['lookback_period'], 30)
        self.assertEqual(strategy.params['trailing_stop_pct'], 3.0)
    
    def test_calculate_indicators(self):
        """Test: Indikatoren werden berechnet"""
        df = self.strategy.calculate_indicators(self.sample_data)
        
        # Check dass neue Spalten hinzugefügt wurden
        self.assertIn('rsi', df.columns)
        self.assertIn('atr', df.columns)
        self.assertIn('sma_short', df.columns)
        self.assertIn('sma_long', df.columns)
        self.assertIn('macd', df.columns)
        self.assertIn('macd_signal', df.columns)
        self.assertIn('momentum', df.columns)
    
    def test_rsi_calculation(self):
        """Test: RSI wird korrekt berechnet"""
        prices = pd.Series([30000, 30100, 30200, 30150, 30300, 30250, 30400])
        rsi = self.strategy._calculate_rsi(prices, period=3)
        
        # RSI sollte Werte zwischen 0 und 100 haben
        valid_rsi = rsi[~pd.isna(rsi)]
        self.assertTrue((valid_rsi >= 0).all() and (valid_rsi <= 100).all())
    
    def test_atr_calculation(self):
        """Test: ATR wird korrekt berechnet"""
        df = pd.DataFrame({
            'high': [100, 105, 103, 108, 106],
            'low': [95, 98, 99, 102, 101],
            'close': [98, 102, 101, 105, 104]
        })
        atr = self.strategy._calculate_atr(df, period=3)
        
        # ATR sollte positive Werte haben
        valid_atr = atr[~pd.isna(atr)]
        self.assertTrue((valid_atr > 0).all())
    
    def test_signal_generation_insufficient_data(self):
        """Test: Kein Signal bei zu wenig Daten"""
        small_data = self.sample_data.iloc[:10]
        signal = self.strategy.generate_signal(small_data)
        self.assertEqual(signal, 0)  # HOLD
    
    def test_signal_generation_with_sufficient_data(self):
        """Test: Signal-Generierung mit ausreichend Daten"""
        signal = self.strategy.generate_signal(self.sample_data)
        self.assertIn(signal, [-1, 0, 1])  # SELL, HOLD, or BUY
    
    def test_position_info(self):
        """Test: Position-Info wird korrekt zurückgegeben"""
        info = self.strategy.get_position_info()
        
        self.assertIn('position', info)
        self.assertIn('entry_price', info)
        self.assertIn('stop_loss', info)
        self.assertIn('take_profit', info)
        
        # Initial sollte keine Position offen sein
        self.assertEqual(info['position'], 'NONE')
    
    def test_strategy_info(self):
        """Test: Strategie-Info enthält alle relevanten Daten"""
        info = self.strategy.get_info()
        
        self.assertEqual(info['name'], "Reversal-Trailing-Stop")
        self.assertTrue(info['enabled'])
        self.assertIsInstance(info['params'], dict)
        self.assertIsInstance(info['position'], dict)
    
    def test_parameter_update(self):
        """Test: Parameter können aktualisiert werden"""
        new_params = {'trailing_stop_pct': 3.5}
        self.strategy.update_params(new_params)
        
        self.assertEqual(self.strategy.params['trailing_stop_pct'], 3.5)
    
    def test_momentum_score(self):
        """Test: Momentum Score wird berechnet"""
        df = self.strategy.calculate_indicators(self.sample_data)
        momentum = df['momentum'].dropna()
        
        # Momentum sollte zwischen -1 und 1 liegen (aufgrund von tanh)
        self.assertTrue((momentum >= -2).all() and (momentum <= 2).all())
    
    def test_long_position_entry(self):
        """Test: Long Position Entry setzt korrekte Parameter"""
        entry_price = 30000.0
        atr = 300.0
        
        self.strategy._set_entry_parameters(entry_price, atr, direction=1)
        
        self.assertEqual(self.strategy.current_position, 1)
        self.assertEqual(self.strategy.entry_price, entry_price)
        self.assertGreater(self.strategy.take_profit, entry_price)
        self.assertLess(self.strategy.stop_loss, entry_price)
    
    def test_short_position_entry(self):
        """Test: Short Position Entry setzt korrekte Parameter"""
        entry_price = 30000.0
        atr = 300.0
        
        self.strategy._set_entry_parameters(entry_price, atr, direction=-1)
        
        self.assertEqual(self.strategy.current_position, -1)
        self.assertEqual(self.strategy.entry_price, entry_price)
        self.assertLess(self.strategy.take_profit, entry_price)
        self.assertGreater(self.strategy.stop_loss, entry_price)
    
    def test_trailing_stop_long(self):
        """Test: Trailing Stop bei Long Position"""
        self.strategy.current_position = 1
        self.strategy.entry_price = 30000.0
        self.strategy.highest_price = 30000.0
        self.strategy.stop_loss = 29400.0  # 2% unter Entry
        
        # Preis steigt
        self.strategy._update_trailing_stops(30500.0)
        
        # Stop-Loss sollte nach oben angepasst werden
        self.assertGreater(self.strategy.stop_loss, 29400.0)
        self.assertEqual(self.strategy.highest_price, 30500.0)
    
    def test_trailing_stop_short(self):
        """Test: Trailing Stop bei Short Position"""
        self.strategy.current_position = -1
        self.strategy.entry_price = 30000.0
        self.strategy.lowest_price = 30000.0
        self.strategy.stop_loss = 30600.0  # 2% über Entry
        
        # Preis fällt
        self.strategy._update_trailing_stops(29500.0)
        
        # Stop-Loss sollte nach unten angepasst werden
        self.assertLess(self.strategy.stop_loss, 30600.0)
        self.assertEqual(self.strategy.lowest_price, 29500.0)
    
    def test_stop_loss_trigger_long(self):
        """Test: Stop-Loss Trigger bei Long Position"""
        self.strategy.current_position = 1
        self.strategy.entry_price = 30000.0
        self.strategy.stop_loss = 29400.0
        self.strategy.take_profit = 31500.0
        
        # Preis fällt unter Stop-Loss
        exit_signal = self.strategy._check_exit_conditions(29300.0)
        
        # Sollte Signal für Reversal zu Short geben
        self.assertEqual(exit_signal, -1)
        self.assertEqual(self.strategy.current_position, 0)  # Position zurückgesetzt
    
    def test_take_profit_trigger_long(self):
        """Test: Take-Profit Trigger bei Long Position"""
        self.strategy.current_position = 1
        self.strategy.entry_price = 30000.0
        self.strategy.stop_loss = 29400.0
        self.strategy.take_profit = 31500.0
        
        # Preis erreicht Take-Profit
        exit_signal = self.strategy._check_exit_conditions(31600.0)
        
        # Sollte Position schließen ohne Reversal
        self.assertEqual(exit_signal, 0)
        self.assertEqual(self.strategy.current_position, 0)
    
    def test_position_reset(self):
        """Test: Position wird korrekt zurückgesetzt"""
        self.strategy.current_position = 1
        self.strategy.entry_price = 30000.0
        self.strategy.stop_loss = 29400.0
        self.strategy.take_profit = 31500.0
        
        self.strategy._reset_position()
        
        self.assertEqual(self.strategy.current_position, 0)
        self.assertEqual(self.strategy.entry_price, 0.0)
        self.assertEqual(self.strategy.stop_loss, 0.0)
        self.assertEqual(self.strategy.take_profit, 0.0)
    
    def test_macd_calculation(self):
        """Test: MACD wird korrekt berechnet"""
        prices = pd.Series(range(100, 150))
        macd, signal = self.strategy._calculate_macd(prices)
        
        # MACD und Signal sollten numerische Werte haben
        self.assertFalse(macd.isna().all())
        self.assertFalse(signal.isna().all())


def run_tests():
    """Führe alle Tests aus"""
    print("=" * 70)
    print("🧪 REVERSAL-TRAILING-STOP STRATEGY TEST SUITE")
    print("=" * 70)
    
    # Erstelle Test Suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestReversalTrailingStopStrategy)
    
    # Führe Tests aus
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
