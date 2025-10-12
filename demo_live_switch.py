"""
demo_live_switch.py - Demonstration of Live Trading Mode Switcher
=================================================================
Zeigt die Verwendung der live_switch API.

Usage:
    python demo_live_switch.py
"""

import os
import sys
from automation.live_switch import (
    check_api_key,
    check_environment_ready,
    switch_to_live,
    switch_to_dry_run,
    get_current_mode
)


def demo_check_api_key():
    """Demonstriert API-Key Validierung."""
    print("\n" + "="*60)
    print("Demo 1: API-Key Validierung")
    print("="*60)
    
    # Setup test API keys
    os.environ["BINANCE_API_KEY"] = "demo_key_1234567890_abcdef"
    os.environ["BINANCE_API_SECRET"] = "demo_secret_1234567890_abcdef"
    
    success, message = check_api_key()
    print(f"\n✓  API-Key Check: {message}")
    print(f"   Status: {'✅ Erfolgreich' if success else '❌ Fehlgeschlagen'}")


def demo_environment_check():
    """Demonstriert Umgebungs-Validierung."""
    print("\n" + "="*60)
    print("Demo 2: Umgebungs-Validierung")
    print("="*60)
    
    # Test mit Production-Endpoint
    os.environ["BINANCE_BASE_URL"] = "https://api.binance.com"
    os.environ["KILL_SWITCH"] = "false"
    
    success, message = check_environment_ready()
    print(f"\n✓  Umgebungs-Check: {message}")
    print(f"   Status: {'✅ Erfolgreich' if success else '❌ Fehlgeschlagen'}")


def demo_get_status():
    """Demonstriert Status-Abfrage."""
    print("\n" + "="*60)
    print("Demo 3: Aktuellen Status abrufen")
    print("="*60)
    
    status = get_current_mode()
    print(f"\n📊 Aktueller Status:")
    print(f"   Modus: {status['mode']}")
    print(f"   DRY_RUN: {status['dry_run']}")
    print(f"   LIVE_TRADING: {status['live_trading']}")
    print(f"   BINANCE_BASE_URL: {status['base_url']}")
    print(f"   KILL_SWITCH: {status['kill_switch']}")
    print(f"   Sicherer Modus: {status['is_safe_mode']}")


def demo_switch_to_dry_run():
    """Demonstriert Umschaltung zu DRY_RUN."""
    print("\n" + "="*60)
    print("Demo 4: Umschaltung zu DRY_RUN")
    print("="*60)
    
    result = switch_to_dry_run()
    print(f"\n✅ Umschaltung erfolgreich!")
    print(f"   Neuer Modus: {result['mode']}")
    print(f"   DRY_RUN: {result['dry_run']}")
    print(f"   LIVE_TRADING: {result['live_trading']}")


def demo_switch_to_live_with_validation():
    """Demonstriert Umschaltung zu LIVE mit Validierung."""
    print("\n" + "="*60)
    print("Demo 5: Umschaltung zu LIVE (nur Validierung)")
    print("="*60)
    print("\n⚠️  Hinweis: Diese Demo führt KEINE echte Umschaltung durch,")
    print("   sondern zeigt nur die Validierungs-Schritte.")
    print()
    
    # Prüfe API-Keys
    print("1️⃣  Prüfe API-Keys...")
    api_valid, api_msg = check_api_key()
    if api_valid:
        print(f"   ✅ {api_msg}")
    else:
        print(f"   ❌ {api_msg}")
        return
    
    # Prüfe Umgebung
    print("\n2️⃣  Prüfe Umgebung...")
    env_valid, env_msg = check_environment_ready()
    if env_valid:
        print(f"   ✅ {env_msg}")
    else:
        print(f"   ❌ {env_msg}")
        return
    
    print("\n✅ Alle Voraussetzungen erfüllt!")
    print("   Um tatsächlich zu Live-Modus zu wechseln:")
    print("   1. Verwende: python -m automation.live_switch --live")
    print("   2. Oder: switch_to_live() (mit Bestätigung)")


def demo_programmatic_usage():
    """Demonstriert programmatische Verwendung."""
    print("\n" + "="*60)
    print("Demo 6: Programmatische Verwendung")
    print("="*60)
    print("\nBeispiel-Code für Trading-Bot Integration:\n")
    
    code = """
from automation.live_switch import switch_to_live, check_api_key

# Vor dem Trading-Start
if not check_api_key()[0]:
    raise Exception("API-Key fehlt oder ungültig")

# Wechsel zu Live-Modus (wenn vom Benutzer gewünscht)
user_wants_live = input("Live-Trading aktivieren? (ja/nein): ")
if user_wants_live.lower() == 'ja':
    try:
        result = switch_to_live()
        if result['success']:
            print("Live-Trading aktiviert!")
            # Starte Trading-Bot
            start_trading_bot()
        else:
            print(f"Fehler: {result.get('reason')}")
    except Exception as e:
        print(f"Fehler: {e}")
else:
    # Bleibe im DRY_RUN Modus
    print("Bleibe im sicheren DRY_RUN Modus")
    """
    
    print(code)


def main():
    """Hauptfunktion."""
    print("\n" + "="*70)
    print("🔄 Live Trading Mode Switcher - Demo")
    print("="*70)
    print("\nDiese Demo zeigt die Verwendung der live_switch API.")
    print("⚠️  Keine echten Umschaltungen werden durchgeführt (nur Demonstrationen).")
    
    try:
        # Setup demo environment
        os.environ["BINANCE_API_KEY"] = "demo_key_1234567890_abcdef"
        os.environ["BINANCE_API_SECRET"] = "demo_secret_1234567890_abcdef"
        os.environ["BINANCE_BASE_URL"] = "https://api.binance.com"
        os.environ["KILL_SWITCH"] = "false"
        os.environ["DRY_RUN"] = "true"
        os.environ["LIVE_TRADING"] = "false"
        
        # Run demos
        demo_check_api_key()
        demo_environment_check()
        demo_get_status()
        demo_switch_to_dry_run()
        demo_get_status()
        demo_switch_to_live_with_validation()
        demo_programmatic_usage()
        
        print("\n" + "="*70)
        print("✅ Demo abgeschlossen!")
        print("="*70)
        print("\n📚 Weitere Informationen:")
        print("   • README.md - Dokumentation")
        print("   • automation/live_switch.py - Quellcode")
        print("   • test_live_switch.py - Tests")
        print("\n💡 Verwendung:")
        print("   • CLI: python -m automation.live_switch --help")
        print("   • API: from automation.live_switch import switch_to_live")
        print()
        
    except KeyboardInterrupt:
        print("\n\n❌ Demo abgebrochen durch Benutzer")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fehler in Demo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
