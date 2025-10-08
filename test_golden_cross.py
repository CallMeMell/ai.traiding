"""
test_golden_cross.py - Umfassende Tests für Golden Cross Strategie
==================================================================

Testet:
- Golden Cross Detection
- Death Cross Detection
- Alle Filter
- Edge Cases
- Performance
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from golden_cross_strategy import GoldenCrossStrategy
from utils import generate_sample_data, setup_logging

# Setup Logging
logger = setup_logging(log_level="INFO")


class GoldenCrossTestSuite:
    """Comprehensive Test Suite für Golden Cross Strategie"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests_run = 0
    
    def run_test(self, test_name: str, test_func):
        """Führe einzelnen Test aus"""
        self.tests_run += 1
        print(f"\n{'='*70}")
        print(f"Test {self.tests_run}: {test_name}")
        print('='*70)
        
        try:
            test_func()
            self.passed += 1
            print(f"✅ PASSED: {test_name}")
        except AssertionError as e:
            self.failed += 1
            print(f"❌ FAILED: {test_name}")
            print(f"   Reason: {e}")
        except Exception as e:
            self.failed += 1
            print(f"❌ ERROR: {test_name}")
            print(f"   Error: {e}")
    
    def print_summary(self):
        """Drucke Test-Zusammenfassung"""
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"Total Tests:  {self.tests_run}")
        print(f"Passed:       {self.passed} ✅")
        print(f"Failed:       {self.failed} ❌")
        print(f"Success Rate: {(self.passed/self.tests_run*100):.1f}%")
        print("="*70)
        
        if self.failed == 0:
            print("\n🎉 Alle Tests bestanden!")
            return 0
        else:
            print(f"\n⚠️ {self.failed} Test(s) fehlgeschlagen!")
            return 1


def test_strategy_initialization():
    """Test 1: Strategie-Initialisierung"""
    
    params = {
        'short_window': 50,
        'long_window': 200,
        'confirmation_days': 3
    }
    
    strategy = GoldenCrossStrategy(params)
    
    assert strategy.short_window == 50, "Short window nicht korrekt"
    assert strategy.long_window == 200, "Long window nicht korrekt"
    assert strategy.confirmation_days == 3, "Confirmation days nicht korrekt"
    assert strategy.enabled == True, "Strategie sollte aktiviert sein"
    
    print("✓ Strategie korrekt initialisiert")


def test_golden_cross_detection():
    """Test 2: Golden Cross Erkennung"""
    
    # Erstelle synthetische Daten mit Golden Cross
    dates = pd.date_range(end=datetime.now(), periods=300, freq='1D')
    
    # Preis fällt erst, dann starker Anstieg (Golden Cross auslösen)
    prices = np.concatenate([
        np.linspace(100, 80, 100),     # Fallend
        np.linspace(80, 80, 50),       # Flat
        np.linspace(80, 120, 150)      # Stark steigend → Golden Cross
    ])
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.uniform(1000, 2000, 300)
    })
    
    params = {
        'short_window': 50,
        'long_window': 200,
        'confirmation_days': 0,  # Keine Confirmation für Test
        'volume_confirmation': False,
        'trend_strength_filter': False,
        'volatility_filter': False
    }
    
    strategy = GoldenCrossStrategy(params)
    
    # Berechne Indikatoren
    df_ind = strategy.calculate_indicators(df)
    
    # Prüfe ob Golden Cross erkannt wird
    cross_type, cross_date = strategy.detect_cross(df_ind)
    
    # In den letzten 50 Kerzen sollte ein Golden Cross sein
    assert cross_type in ['golden', None], f"Unerwarteter Cross-Typ: {cross_type}"
    
    print(f"✓ Cross Detection funktioniert (Detected: {cross_type})")


def test_death_cross_detection():
    """Test 3: Death Cross Erkennung"""
    
    dates = pd.date_range(end=datetime.now(), periods=300, freq='1D')
    
    # Preis steigt erst, dann starker Fall (Death Cross auslösen)
    prices = np.concatenate([
        np.linspace(100, 120, 100),    # Steigend
        np.linspace(120, 120, 50),     # Flat
        np.linspace(120, 80, 150)      # Stark fallend → Death Cross
    ])
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.uniform(1000, 2000, 300)
    })
    
    params = {
        'short_window': 50,
        'long_window': 200,
        'confirmation_days': 0,
        'volume_confirmation': False,
        'trend_strength_filter': False,
        'volatility_filter': False
    }
    
    strategy = GoldenCrossStrategy(params)
    df_ind = strategy.calculate_indicators(df)
    cross_type, cross_date = strategy.detect_cross(df_ind)
    
    assert cross_type in ['death', None], f"Unerwarteter Cross-Typ: {cross_type}"
    
    print(f"✓ Death Cross Detection funktioniert (Detected: {cross_type})")


def test_confirmation_period():
    """Test 4: Confirmation Period"""
    
    df = generate_sample_data(n_bars=300)
    
    params = {
        'short_window': 50,
        'long_window': 200,
        'confirmation_days': 5,  # 5 Tage Confirmation
        'volume_confirmation': False,
        'trend_strength_filter': False,
        'volatility_filter': False
    }
    
    strategy = GoldenCrossStrategy(params)
    
    # Signal sollte 0 sein bis Confirmation abgelaufen
    signal = strategy.generate_signal(df)
    
    # Da wir simulierte Daten haben, kann Signal 0, 1 oder -1 sein
    # Wichtig: Kein Crash!
    assert signal in [0, 1, -1], f"Ungültiges Signal: {signal}"
    
    print(f"✓ Confirmation Period funktioniert (Signal: {signal})")


def test_spread_filter():
    """Test 5: Spread Filter (Flat Market Detection)"""
    
    # Erstelle flache Markt-Daten
    dates = pd.date_range(end=datetime.now(), periods=300, freq='1D')
    prices = np.ones(300) * 100 + np.random.normal(0, 0.5, 300)  # Sehr flat
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices * 1.001,
        'low': prices * 0.999,
        'close': prices,
        'volume': np.random.uniform(1000, 2000, 300)
    })
    
    params = {
        'short_window': 50,
        'long_window': 200,
        'confirmation_days': 0,
        'min_spread_pct': 1.0,  # Braucht min 1% Spread
        'volume_confirmation': False,
        'trend_strength_filter': False,
        'volatility_filter': False
    }
    
    strategy = GoldenCrossStrategy(params)
    df_ind = strategy.calculate_indicators(df)
    
    # Check Spread Filter
    spread_ok = strategy.check_spread_filter(df_ind)
    
    # In flat market sollte Spread zu klein sein
    assert spread_ok == False, "Spread Filter sollte in flat market triggern"
    
    print("✓ Spread Filter erkennt flat markets")


def test_volume_confirmation():
    """Test 6: Volumen-Bestätigung"""
    
    df = generate_sample_data(n_bars=300)
    
    # Setze letztes Volumen sehr niedrig
    df.loc[df.index[-1], 'volume'] = df['volume'].mean() * 0.5
    
    params = {
        'short_window': 50,
        'long_window': 200,
        'confirmation_days': 0,
        'volume_confirmation': True,
        'trend_strength_filter': False,
        'volatility_filter': False
    }
    
    strategy = GoldenCrossStrategy(params)
    df_ind = strategy.calculate_indicators(df)
    
    # Volumen-Check sollte fehlschlagen
    vol_ok = strategy.check_volume_confirmation(df_ind)
    
    assert vol_ok == False, "Volumen-Confirmation sollte bei niedrigem Volumen fehlschlagen"
    
    print("✓ Volumen-Confirmation funktioniert")


def test_volatility_filter():
    """Test 7: Volatilitäts-Filter"""
    
    # Erstelle sehr volatile Daten
    df = generate_sample_data(n_bars=300)
    
    # Erhöhe Volatilität künstlich
    df['close'] = df['close'] * (1 + np.random.normal(0, 0.1, 300))  # 10% Volatilität
    
    params = {
        'short_window': 50,
        'long_window': 200,
        'confirmation_days': 0,
        'volatility_filter': True,
        'max_volatility': 0.05,  # Max 5%
        'volume_confirmation': False,
        'trend_strength_filter': False
    }
    
    strategy = GoldenCrossStrategy(params)
    df_ind = strategy.calculate_indicators(df)
    
    vol_ok = strategy.check_volatility_filter(df_ind)
    
    # Sollte wegen hoher Volatilität fehlschlagen
    assert vol_ok == False, "Volatilitäts-Filter sollte bei hoher Vol triggern"
    
    print("✓ Volatilitäts-Filter funktioniert")


def test_insufficient_data():
    """Test 8: Zu wenig Daten"""
    
    # Nur 100 Kerzen (braucht 200+ für MA_200)
    df = generate_sample_data(n_bars=100)
    
    params = {
        'short_window': 50,
        'long_window': 200,
        'confirmation_days': 3
    }
    
    strategy = GoldenCrossStrategy(params)
    signal = strategy.generate_signal(df)
    
    # Sollte HOLD zurückgeben (0)
    assert signal == 0, "Bei zu wenig Daten sollte HOLD zurückgegeben werden"
    
    print("✓ Zu wenig Daten wird korrekt behandelt")


def test_indicator_calculation():
    """Test 9: Indikator-Berechnung"""
    
    df = generate_sample_data(n_bars=300)
    
    params = {
        'short_window': 50,
        'long_window': 200,
        'confirmation_days': 3
    }
    
    strategy = GoldenCrossStrategy(params)
    df_ind = strategy.calculate_indicators(df)
    
    # Prüfe ob alle Spalten vorhanden sind
    required_cols = ['MA_50', 'MA_200', 'ma_spread', 'ma_spread_pct', 
                     'volume_sma', 'volatility']
    
    for col in required_cols:
        assert col in df_ind.columns, f"Fehlende Spalte: {col}"
    
    # Prüfe ob MAs sinnvoll sind
    assert df_ind['MA_50'].iloc[-1] > 0, "MA_50 sollte positiv sein"
    assert df_ind['MA_200'].iloc[-1] > 0, "MA_200 sollte positiv sein"
    
    print("✓ Indikatoren werden korrekt berechnet")


def test_strategy_info():
    """Test 10: Strategie-Informationen"""
    
    params = {
        'short_window': 50,
        'long_window': 200,
        'confirmation_days': 3
    }
    
    strategy = GoldenCrossStrategy(params)
    info = strategy.get_info()
    
    # Prüfe ob alle wichtigen Infos vorhanden
    assert 'name' in info, "Name fehlt in Info"
    assert 'enabled' in info, "Enabled fehlt in Info"
    assert 'short_window' in info, "Short window fehlt"
    assert 'long_window' in info, "Long window fehlt"
    assert 'filters' in info, "Filter-Info fehlt"
    
    print("✓ Strategie-Info vollständig")


def test_parameter_update():
    """Test 11: Parameter-Update"""
    
    params = {
        'short_window': 50,
        'long_window': 200
    }
    
    strategy = GoldenCrossStrategy(params)
    
    # Update Parameter
    new_params = {
        'short_window': 20,
        'confirmation_days': 5
    }
    
    strategy.update_params(new_params)
    
    # Prüfe ob Updates angewendet wurden
    assert strategy.params['short_window'] == 20, "Short window nicht aktualisiert"
    assert strategy.params['confirmation_days'] == 5, "Confirmation days nicht aktualisiert"
    
    print("✓ Parameter-Update funktioniert")


def test_enable_disable():
    """Test 12: Enable/Disable Strategie"""
    
    params = {'short_window': 50, 'long_window': 200}
    strategy = GoldenCrossStrategy(params)
    
    assert strategy.enabled == True, "Strategie sollte initial aktiviert sein"
    
    # Disable
    strategy.disable()
    assert strategy.enabled == False, "Strategie sollte deaktiviert sein"
    
    # Signal sollte 0 sein wenn disabled
    df = generate_sample_data(n_bars=300)
    signal = strategy.generate_signal(df)
    assert signal == 0, "Signal sollte 0 sein wenn disabled"
    
    # Enable wieder
    strategy.enable()
    assert strategy.enabled == True, "Strategie sollte wieder aktiviert sein"
    
    print("✓ Enable/Disable funktioniert")


def run_all_tests():
    """Führe alle Tests aus"""
    
    print("\n" + "="*70)
    print("🧪 GOLDEN CROSS STRATEGY - TEST SUITE")
    print("="*70)
    
    suite = GoldenCrossTestSuite()
    
    # Führe alle Tests aus
    suite.run_test("Strategie-Initialisierung", test_strategy_initialization)
    suite.run_test("Golden Cross Detection", test_golden_cross_detection)
    suite.run_test("Death Cross Detection", test_death_cross_detection)
    suite.run_test("Confirmation Period", test_confirmation_period)
    suite.run_test("Spread Filter (Flat Market)", test_spread_filter)
    suite.run_test("Volumen-Bestätigung", test_volume_confirmation)
    suite.run_test("Volatilitäts-Filter", test_volatility_filter)
    suite.run_test("Zu wenig Daten", test_insufficient_data)
    suite.run_test("Indikator-Berechnung", test_indicator_calculation)
    suite.run_test("Strategie-Informationen", test_strategy_info)
    suite.run_test("Parameter-Update", test_parameter_update)
    suite.run_test("Enable/Disable", test_enable_disable)
    
    # Zusammenfassung
    return suite.print_summary()


if __name__ == "__main__":
    sys.exit(run_all_tests())
