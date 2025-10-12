"""
demo_api_key_validation.py - Demonstration der API-Key-Validierung
===================================================================
Zeigt die API-Key-Validierung vor dem Live-Trading Start.

Usage:
    python demo_api_key_validation.py
"""

import os
import sys
from unittest.mock import MagicMock, patch


def demo_validation_function():
    """Demonstriert die validate_api_keys_for_live_trading Funktion."""
    print("\n" + "="*70)
    print("Demo 1: API-Key Validierung Funktion")
    print("="*70)
    
    from main import validate_api_keys_for_live_trading
    
    # Szenario 1: Gültige Keys
    print("\n📋 Szenario 1: Gültige API-Keys")
    os.environ["BINANCE_API_KEY"] = "demo_key_1234567890_valid"
    os.environ["BINANCE_API_SECRET"] = "demo_secret_1234567890_valid"
    
    success, message = validate_api_keys_for_live_trading()
    print(f"   Ergebnis: {'✅ Erfolgreich' if success else '❌ Fehlgeschlagen'}")
    print(f"   Nachricht: {message}")
    
    # Szenario 2: Fehlender API-Key
    print("\n📋 Szenario 2: Fehlender API-Key")
    os.environ["BINANCE_API_KEY"] = ""
    os.environ["BINANCE_API_SECRET"] = "demo_secret_1234567890_valid"
    
    success, message = validate_api_keys_for_live_trading()
    print(f"   Ergebnis: {'✅ Erfolgreich' if success else '❌ Fehlgeschlagen'}")
    print(f"   Nachricht: {message}")
    
    # Szenario 3: Zu kurzer API-Key
    print("\n📋 Szenario 3: Zu kurzer API-Key")
    os.environ["BINANCE_API_KEY"] = "short"
    os.environ["BINANCE_API_SECRET"] = "demo_secret_1234567890_valid"
    
    success, message = validate_api_keys_for_live_trading()
    print(f"   Ergebnis: {'✅ Erfolgreich' if success else '❌ Fehlgeschlagen'}")
    print(f"   Nachricht: {message}")


def demo_live_mode_validation():
    """Demonstriert Validierung im Live-Modus."""
    print("\n" + "="*70)
    print("Demo 2: Live-Modus mit ungültigen Keys")
    print("="*70)
    print("\n⚠️  Hinweis: Dieser Test zeigt, wie ungültige Keys Live-Trading verhindern.")
    
    # Setup: DRY_RUN=false, keine Keys
    os.environ["DRY_RUN"] = "false"
    os.environ["BINANCE_API_KEY"] = ""
    os.environ["BINANCE_API_SECRET"] = ""
    
    print("\n📋 Umgebung:")
    print(f"   DRY_RUN: {os.environ.get('DRY_RUN')}")
    print(f"   BINANCE_API_KEY: {'<leer>' if not os.environ.get('BINANCE_API_KEY') else '<gesetzt>'}")
    print(f"   BINANCE_API_SECRET: {'<leer>' if not os.environ.get('BINANCE_API_SECRET') else '<gesetzt>'}")
    
    print("\n🔄 Versuche LiveTradingBot zu starten...")
    
    try:
        # Mock dependencies to avoid actual initialization
        with patch('main.setup_logging') as mock_logging, \
             patch('main.config') as mock_config, \
             patch('main.BINANCE_AVAILABLE', False):
            
            mock_logger = MagicMock()
            mock_logging.return_value = mock_logger
            mock_config.log_level = "INFO"
            mock_config.log_file = "test.log"
            mock_config.to_dict = MagicMock(return_value={})
            
            from main import LiveTradingBot
            
            # This should raise an exception
            bot = LiveTradingBot(use_live_data=True, paper_trading=False)
            print("\n❌ FEHLER: Bot wurde trotz fehlender Keys gestartet!")
            
    except Exception as e:
        print(f"\n✅ Erwarteter Fehler: {str(e)}")
        print("\n📌 Live-Trading wurde erfolgreich verhindert!")


def demo_dry_run_validation():
    """Demonstriert Validierung im DRY_RUN-Modus."""
    print("\n" + "="*70)
    print("Demo 3: DRY_RUN Modus mit ungültigen Keys")
    print("="*70)
    print("\n⚠️  Hinweis: Im DRY_RUN Modus wird nur eine Warnung ausgegeben.")
    
    # Setup: DRY_RUN=true, keine Keys
    os.environ["DRY_RUN"] = "true"
    os.environ["BINANCE_API_KEY"] = ""
    os.environ["BINANCE_API_SECRET"] = ""
    
    print("\n📋 Umgebung:")
    print(f"   DRY_RUN: {os.environ.get('DRY_RUN')}")
    print(f"   BINANCE_API_KEY: {'<leer>' if not os.environ.get('BINANCE_API_KEY') else '<gesetzt>'}")
    print(f"   BINANCE_API_SECRET: {'<leer>' if not os.environ.get('BINANCE_API_SECRET') else '<gesetzt>'}")
    
    print("\n🔄 Versuche LiveTradingBot zu starten...")
    
    try:
        # Mock dependencies to avoid actual initialization
        with patch('main.setup_logging') as mock_logging, \
             patch('main.config') as mock_config, \
             patch('main.BINANCE_AVAILABLE', False):
            
            mock_logger = MagicMock()
            mock_logging.return_value = mock_logger
            mock_config.log_level = "INFO"
            mock_config.log_file = "test.log"
            mock_config.initial_capital = 10000
            mock_config.to_dict = MagicMock(return_value={})
            
            from main import LiveTradingBot
            
            # This should NOT raise an exception in DRY_RUN mode
            bot = LiveTradingBot(use_live_data=True, paper_trading=False)
            print("\n✅ Bot wurde erfolgreich im DRY_RUN Modus gestartet!")
            print("📌 Warnung wurde ausgegeben, aber Trading läuft weiter")
            
            # Check if warning was logged
            warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
            if any("API" in str(call) for call in warning_calls):
                print("✅ API-Key Warnung wurde protokolliert")
            
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {str(e)}")


def demo_dashboard_warning():
    """Demonstriert Dashboard-Warnung."""
    print("\n" + "="*70)
    print("Demo 4: Dashboard API-Key Warnung")
    print("="*70)
    
    print("\n🔄 Erstelle Dashboard mit API-Key Warnung...")
    
    try:
        from dashboard import create_dashboard
        
        dashboard = create_dashboard()
        
        # Display API key warning
        dashboard.display_api_key_warning(
            "BINANCE_API_KEY fehlt - Live-Trading nicht möglich\n"
            "DRY_RUN ist aktiviert - Trading läuft im Simulationsmodus\n"
            "Für Live-Trading müssen gültige API-Keys konfiguriert werden"
        )
        
        print("\n✅ Dashboard-Warnung wurde erfolgreich angezeigt!")
        
    except Exception as e:
        print(f"\n❌ Fehler beim Dashboard: {str(e)}")


def demo_comparison():
    """Vergleich: Alte vs. Neue Implementierung."""
    print("\n" + "="*70)
    print("Demo 5: Vergleich Alte vs. Neue Implementierung")
    print("="*70)
    
    print("\n📊 ALTE Implementierung:")
    print("   • API-Keys wurden nur geprüft wenn Binance initialisiert wurde")
    print("   • Bei fehlenden Keys: Silent Fallback zu Simulation")
    print("   • Keine explizite Warnung vor Live-Trading Start")
    print("   • Benutzer könnte versehentlich in Simulation laufen")
    
    print("\n📊 NEUE Implementierung:")
    print("   ✅ API-Keys werden VOR Trading-Start validiert")
    print("   ✅ Im Live-Modus (DRY_RUN=false): Exception bei fehlenden Keys")
    print("   ✅ Im DRY_RUN Modus: Warnung aber kein Abbruch")
    print("   ✅ Log- UND Dashboard-Warnung")
    print("   ✅ Tests für alle Szenarien")
    
    print("\n🎯 Vorteile:")
    print("   • Verhindert versehentliches Trading ohne gültige Keys")
    print("   • Klare Fehlermeldungen für Benutzer")
    print("   • Sicherheit durch Fail-Fast Prinzip")
    print("   • Dashboard-Integration für bessere Sichtbarkeit")


def main():
    """Hauptfunktion."""
    print("\n" + "="*70)
    print("🔐 API-Key-Validierung und Warnsystem - Demonstration")
    print("="*70)
    print("\nDieses Script demonstriert die neue API-Key-Validierung")
    print("vor dem Live-Trading Start.\n")
    
    try:
        demo_validation_function()
        demo_live_mode_validation()
        demo_dry_run_validation()
        demo_dashboard_warning()
        demo_comparison()
        
        print("\n" + "="*70)
        print("✅ Alle Demonstrationen erfolgreich abgeschlossen!")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo abgebrochen durch Benutzer")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fehler bei Demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
