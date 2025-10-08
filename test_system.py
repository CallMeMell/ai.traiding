"""
test_system.py - Systemtest für die Master-Version
===================================================
Überprüft alle Komponenten auf Funktionalität
"""
import sys
import os

def test_imports():
    """Teste ob alle Module importierbar sind"""
    print("🔍 Teste Imports...")
    
    try:
        from config import config
        print("  ✅ config.py importiert")
    except Exception as e:
        print(f"  ❌ config.py: {e}")
        return False
    
    try:
        from strategy import TradingStrategy, StrategyManager
        print("  ✅ strategy.py importiert")
    except Exception as e:
        print(f"  ❌ strategy.py: {e}")
        return False
    
    try:
        from utils import setup_logging, TradeLogger, generate_sample_data
        print("  ✅ utils.py importiert")
    except Exception as e:
        print(f"  ❌ utils.py: {e}")
        return False
    
    return True


def test_config():
    """Teste Konfiguration"""
    print("\n⚙️ Teste Konfiguration...")
    
    try:
        from config import config
        
        # Validierung
        is_valid, error = config.validate()
        if is_valid:
            print("  ✅ Konfiguration ist valid")
        else:
            print(f"  ❌ Konfiguration: {error}")
            return False
        
        # Teste to_dict()
        config_dict = config.to_dict()
        print(f"  ✅ Config dict erstellt ({len(config_dict)} keys)")
        
        return True
    except Exception as e:
        print(f"  ❌ Config Test: {e}")
        return False


def test_strategies():
    """Teste Strategie-System"""
    print("\n📊 Teste Strategien...")
    
    try:
        from strategy import TradingStrategy, StrategyManager
        from config import config
        from utils import generate_sample_data
        
        # Erstelle Sample-Daten
        df = generate_sample_data(n_bars=200)
        print(f"  ✅ Sample-Daten generiert ({len(df)} Zeilen)")
        
        # Initialisiere Strategy
        strategy = TradingStrategy(config.to_dict())
        print("  ✅ TradingStrategy initialisiert")
        
        # Teste Signal-Generierung
        analysis = strategy.analyze(df)
        signal = analysis['signal']
        signal_text = analysis['signal_text']
        
        print(f"  ✅ Signal generiert: {signal_text} (Signal: {signal})")
        print(f"     Triggering strategies: {analysis['triggering_strategies']}")
        
        return True
    except Exception as e:
        print(f"  ❌ Strategy Test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utils():
    """Teste Utility-Funktionen"""
    print("\n🛠️ Teste Utilities...")
    
    try:
        from utils import (
            generate_sample_data, 
            validate_ohlcv_data,
            calculate_performance_metrics,
            format_currency,
            format_percentage
        )
        
        # Sample Data
        df = generate_sample_data(n_bars=100)
        print(f"  ✅ generate_sample_data: {len(df)} Zeilen")
        
        # Validierung
        is_valid, error = validate_ohlcv_data(df)
        if is_valid:
            print("  ✅ validate_ohlcv_data: Daten sind valid")
        else:
            print(f"  ❌ validate_ohlcv_data: {error}")
            return False
        
        # Performance Metrics
        fake_trades = [
            {'pnl': '100.50'},
            {'pnl': '-50.25'},
            {'pnl': '75.00'}
        ]
        metrics = calculate_performance_metrics(fake_trades)
        print(f"  ✅ calculate_performance_metrics: {metrics['total_trades']} trades")
        
        # Formatting
        print(f"  ✅ format_currency: {format_currency(1234.56)}")
        print(f"  ✅ format_percentage: {format_percentage(12.34)}")
        
        return True
    except Exception as e:
        print(f"  ❌ Utils Test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_logging():
    """Teste Logging-System"""
    print("\n📝 Teste Logging...")
    
    try:
        from utils import setup_logging
        import logging
        
        logger = setup_logging(
            log_level="INFO",
            log_file="logs/test.log"
        )
        print("  ✅ Logger erstellt")
        
        logger.info("Test Info Message")
        logger.warning("Test Warning Message")
        print("  ✅ Log-Nachrichten geschrieben")
        
        # Prüfe ob Log-Datei existiert
        if os.path.exists("logs/test.log"):
            print("  ✅ Log-Datei wurde erstellt")
            return True
        else:
            print("  ❌ Log-Datei nicht gefunden")
            return False
        
    except Exception as e:
        print(f"  ❌ Logging Test: {e}")
        return False


def test_directories():
    """Teste ob Verzeichnisse erstellt werden können"""
    print("\n📁 Teste Verzeichnisse...")
    
    try:
        # Erstelle test Verzeichnisse
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs("config", exist_ok=True)
        
        print("  ✅ data/ erstellt")
        print("  ✅ logs/ erstellt")
        print("  ✅ config/ erstellt")
        
        return True
    except Exception as e:
        print(f"  ❌ Directory Test: {e}")
        return False


def run_all_tests():
    """Führe alle Tests aus"""
    print("=" * 60)
    print("🧪 SYSTEM TEST - Master Version")
    print("=" * 60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Directories", test_directories),
        ("Configuration", test_config),
        ("Strategies", test_strategies),
        ("Utilities", test_utils),
        ("Logging", test_logging),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ {test_name} Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print()
    print(f"Ergebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n🎉 Alle Tests erfolgreich! System ist einsatzbereit.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} Test(s) fehlgeschlagen. Bitte Fehler beheben.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
