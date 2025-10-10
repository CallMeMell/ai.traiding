"""
live_switch.py - Live Trading Mode Switcher
===========================================
Sichere Umschaltung zwischen DRY_RUN und LIVE Modus.

SECURITY: 
- API-Keys werden validiert aber nicht angezeigt
- Explizite Bestätigung erforderlich
- Preflight-Checks werden durchgeführt

Usage:
    from automation.live_switch import switch_to_live, switch_to_dry_run
    
    # Zu Live-Modus wechseln (mit Bestätigung)
    switch_to_live()
    
    # Zu DRY_RUN wechseln
    switch_to_dry_run()
"""

import os
import sys
from typing import Tuple, Dict, Any, Optional


def check_api_key() -> Tuple[bool, str]:
    """
    Prüft ob API-Key und Secret vorhanden und gültig sind.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")
    
    if not api_key:
        return False, "BINANCE_API_KEY fehlt"
    
    if not api_secret:
        return False, "BINANCE_API_SECRET fehlt"
    
    # Validiere Länge (Binance API Keys sind typischerweise 64 Zeichen)
    if len(api_key) < 10:
        return False, "BINANCE_API_KEY erscheint ungültig (zu kurz)"
    
    if len(api_secret) < 10:
        return False, "BINANCE_API_SECRET erscheint ungültig (zu kurz)"
    
    return True, "API-Keys vorhanden und gültig"


def check_environment_ready() -> Tuple[bool, str]:
    """
    Prüft ob die Umgebung für Live-Trading bereit ist.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    # Prüfe API Keys
    api_valid, api_msg = check_api_key()
    if not api_valid:
        return False, f"API-Keys nicht gültig: {api_msg}"
    
    # Prüfe ob production endpoint konfiguriert ist
    base_url = os.getenv("BINANCE_BASE_URL", "")
    if base_url and not base_url.startswith("https://api.binance.com"):
        return False, f"BINANCE_BASE_URL muss Production-Endpoint sein (https://api.binance.com), aktuell: {base_url}"
    
    # Prüfe ob KILL_SWITCH aktiv ist
    kill_switch = os.getenv("KILL_SWITCH", "false").lower()
    if kill_switch == "true":
        return False, "KILL_SWITCH ist aktiv - Live-Trading blockiert"
    
    return True, "Umgebung bereit für Live-Trading"


def confirm_live_switch(force: bool = False) -> bool:
    """
    Bestätigungs-Dialog für Umschaltung zu Live-Modus.
    
    Args:
        force: Wenn True, wird keine Bestätigung angefordert
        
    Returns:
        bool: True wenn bestätigt, False sonst
    """
    if force:
        return True
    
    print("\n" + "="*60)
    print("⚠️  WARNUNG: Live-Trading Aktivierung")
    print("="*60)
    print("\nDu bist dabei, zu LIVE-TRADING zu wechseln!")
    print("\n⚠️  RISIKEN:")
    print("  • Trading mit ECHTEM Geld")
    print("  • Echte Verluste sind möglich")
    print("  • Keine Rücknahme von Transaktionen")
    print("\n✓  VORAUSSETZUNGEN:")
    print("  • API-Keys sind korrekt konfiguriert")
    print("  • Risk-Limits sind gesetzt")
    print("  • Monitoring ist aktiv")
    print("  • Du verstehst die Strategie")
    print("\nGib 'LIVE_TRADING_BESTÄTIGT' ein um fortzufahren:")
    print("(Jede andere Eingabe bricht ab)")
    print()
    
    try:
        user_input = input("> ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\n❌ Abgebrochen durch Benutzer")
        return False
    
    if user_input != "LIVE_TRADING_BESTÄTIGT":
        print("\n❌ Bestätigung fehlgeschlagen - Umschaltung abgebrochen")
        return False
    
    return True


def run_preflight_checks() -> Tuple[bool, str]:
    """
    Führt Preflight-Checks aus bevor Live-Trading aktiviert wird.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    # Importiere preflight module
    try:
        # Add scripts directory to path
        scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        
        import live_preflight
        
        # Führe einzelne Checks aus
        checks = [
            ("Environment", live_preflight.check_environment),
            ("Credentials", live_preflight.check_credentials),
            ("Time Sync", live_preflight.check_time_sync),
        ]
        
        all_passed = True
        failed_checks = []
        
        for check_name, check_func in checks:
            try:
                success, message = check_func()
                if not success:
                    all_passed = False
                    failed_checks.append(f"{check_name}: {message}")
            except Exception as e:
                all_passed = False
                failed_checks.append(f"{check_name}: {str(e)}")
        
        if not all_passed:
            return False, f"Preflight-Checks fehlgeschlagen: {', '.join(failed_checks)}"
        
        return True, "Alle Preflight-Checks erfolgreich"
        
    except ImportError as e:
        return False, f"Konnte Preflight-Modul nicht laden: {str(e)}"
    except Exception as e:
        return False, f"Fehler bei Preflight-Checks: {str(e)}"


def switch_to_live(force: bool = False, skip_preflight: bool = False) -> Dict[str, Any]:
    """
    Wechselt zu Live-Trading Modus.
    
    Args:
        force: Wenn True, wird keine Bestätigung angefordert
        skip_preflight: Wenn True, werden Preflight-Checks übersprungen (nicht empfohlen!)
        
    Returns:
        Dict mit Status und Details
        
    Raises:
        Exception: Wenn API-Key oder Secret fehlen oder ungültig sind
    """
    print("\n🔄 Starte Umschaltung zu LIVE-Modus...\n")
    
    # Schritt 1: Prüfe API-Keys
    print("1️⃣  Prüfe API-Keys...")
    api_valid, api_msg = check_api_key()
    if not api_valid:
        raise Exception(f"API-Key fehlt oder ungültig: {api_msg}")
    print(f"   ✅ {api_msg}\n")
    
    # Schritt 2: Prüfe Umgebung
    print("2️⃣  Prüfe Umgebung...")
    env_valid, env_msg = check_environment_ready()
    if not env_valid:
        raise Exception(f"Umgebung nicht bereit: {env_msg}")
    print(f"   ✅ {env_msg}\n")
    
    # Schritt 3: Bestätigung
    print("3️⃣  Anforderung Bestätigung...")
    if not confirm_live_switch(force=force):
        return {
            "success": False,
            "mode": "DRY_RUN",
            "reason": "Bestätigung verweigert",
            "live_ack_required": True
        }
    print("   ✅ Bestätigung erhalten\n")
    
    # Schritt 4: Preflight-Checks (optional)
    if not skip_preflight:
        print("4️⃣  Führe Preflight-Checks aus...")
        preflight_valid, preflight_msg = run_preflight_checks()
        if not preflight_valid:
            raise Exception(f"Preflight-Checks fehlgeschlagen: {preflight_msg}")
        print(f"   ✅ {preflight_msg}\n")
    else:
        print("4️⃣  Preflight-Checks übersprungen (nicht empfohlen!)\n")
    
    # Schritt 5: Setze Environment-Variablen
    print("5️⃣  Setze Live-Trading Flags...")
    os.environ["DRY_RUN"] = "false"
    os.environ["LIVE_TRADING"] = "true"
    os.environ["BINANCE_BASE_URL"] = "https://api.binance.com"
    print("   ✅ DRY_RUN=false")
    print("   ✅ LIVE_TRADING=true")
    print("   ✅ BINANCE_BASE_URL=https://api.binance.com\n")
    
    print("="*60)
    print("✅ ERFOLGREICH: Live-Trading aktiviert!")
    print("="*60)
    print("\n⚠️  WICHTIG:")
    print("  • Überwache deine Positionen kontinuierlich")
    print("  • Setze Stop-Loss Orders")
    print("  • Habe einen Notfall-Plan (KILL_SWITCH)")
    print("  • Prüfe regelmäßig dein Account-Balance")
    print()
    
    return {
        "success": True,
        "mode": "LIVE",
        "dry_run": False,
        "live_trading": True,
        "base_url": "https://api.binance.com"
    }


def switch_to_dry_run() -> Dict[str, Any]:
    """
    Wechselt zu DRY_RUN Modus (sicherer Modus).
    
    Returns:
        Dict mit Status und Details
    """
    print("\n🔄 Wechsle zu DRY_RUN Modus (sicherer Modus)...\n")
    
    # Setze Environment-Variablen
    os.environ["DRY_RUN"] = "true"
    os.environ["LIVE_TRADING"] = "false"
    
    # Optional: Wechsel zu Testnet endpoint
    testnet_url = "https://testnet.binance.vision"
    os.environ["BINANCE_BASE_URL"] = testnet_url
    
    print("✅ DRY_RUN aktiviert")
    print("   • DRY_RUN=true")
    print("   • LIVE_TRADING=false")
    print(f"   • BINANCE_BASE_URL={testnet_url}")
    print("\n✓  Sicherer Modus: Keine echten Trades werden ausgeführt")
    print()
    
    return {
        "success": True,
        "mode": "DRY_RUN",
        "dry_run": True,
        "live_trading": False,
        "base_url": testnet_url
    }


def get_current_mode() -> Dict[str, Any]:
    """
    Gibt den aktuellen Trading-Modus zurück.
    
    Returns:
        Dict mit aktuellem Status
    """
    dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
    live_trading = os.getenv("LIVE_TRADING", "false").lower() == "true"
    base_url = os.getenv("BINANCE_BASE_URL", "")
    kill_switch = os.getenv("KILL_SWITCH", "false").lower() == "true"
    live_ack = os.getenv("LIVE_ACK", "")
    
    mode = "DRY_RUN" if dry_run else "LIVE"
    
    return {
        "mode": mode,
        "dry_run": dry_run,
        "live_trading": live_trading,
        "base_url": base_url,
        "kill_switch": kill_switch,
        "live_ack": live_ack,
        "is_safe_mode": dry_run or kill_switch
    }


def main():
    """CLI Einstiegspunkt für live_switch."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Live Trading Mode Switcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Wechsel zu Live-Modus (mit Bestätigung)
  python -m automation.live_switch --live
  
  # Wechsel zu Live-Modus (erzwungen, ohne Bestätigung - NUR FÜR TESTS!)
  python -m automation.live_switch --live --force
  
  # Wechsel zu DRY_RUN Modus
  python -m automation.live_switch --dry-run
  
  # Zeige aktuellen Modus
  python -m automation.live_switch --status
        """
    )
    
    parser.add_argument(
        '--live',
        action='store_true',
        help='Wechsel zu Live-Trading Modus'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Wechsel zu DRY_RUN Modus'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Zeige aktuellen Modus'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Erzwinge Umschaltung ohne Bestätigung (GEFÄHRLICH!)'
    )
    
    parser.add_argument(
        '--skip-preflight',
        action='store_true',
        help='Überspringe Preflight-Checks (NICHT EMPFOHLEN!)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.status:
            status = get_current_mode()
            print("\n📊 Aktueller Status:")
            print(f"   Modus: {status['mode']}")
            print(f"   DRY_RUN: {status['dry_run']}")
            print(f"   LIVE_TRADING: {status['live_trading']}")
            print(f"   BINANCE_BASE_URL: {status['base_url']}")
            print(f"   KILL_SWITCH: {status['kill_switch']}")
            print(f"   LIVE_ACK: {status['live_ack']}")
            print(f"   Sicherer Modus: {status['is_safe_mode']}")
            print()
            
        elif args.live:
            result = switch_to_live(force=args.force, skip_preflight=args.skip_preflight)
            if not result["success"]:
                print(f"\n❌ Fehler: {result.get('reason', 'Unbekannter Fehler')}")
                sys.exit(1)
                
        elif args.dry_run:
            switch_to_dry_run()
            
        else:
            parser.print_help()
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ FEHLER: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
