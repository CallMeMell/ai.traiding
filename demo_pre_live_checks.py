"""
demo_pre_live_checks.py - Demo für Pre-Live Checks
=================================================
Demonstriert die automatisierten Pre-Live Checks mit verschiedenen Szenarien.
"""

import os
import sys
import tempfile
import shutil
from unittest.mock import patch
from automation.runner import AutomationRunner
from core.session_store import SessionStore


def demo_successful_checks():
    """Demo: Erfolgreiche Pre-Live Checks."""
    print("\n" + "=" * 80)
    print("DEMO 1: ERFOLGREICHE PRE-LIVE CHECKS")
    print("=" * 80)
    print("\nIn diesem Szenario bestehen alle Checks erfolgreich.\n")
    
    # Create temporary directory for session store
    test_dir = tempfile.mkdtemp()
    events_path = os.path.join(test_dir, "events.jsonl")
    summary_path = os.path.join(test_dir, "summary.json")
    
    try:
        # Create runner with custom session store
        store = SessionStore(events_path, summary_path)
        runner = AutomationRunner(
            data_phase_timeout=5,
            strategy_phase_timeout=5,
            api_phase_timeout=5,
            heartbeat_interval=2,
            enable_validation=False
        )
        runner.session_store = store
        
        # Run pre-live checks only
        result = runner._run_pre_live_checks()
        
        print("\n" + "=" * 80)
        print("ERGEBNIS:")
        print("=" * 80)
        print(f"Status: {result['status']}")
        print(f"Critical Failures: {len(result['critical_failures'])}")
        print(f"Warnings: {len(result['warnings'])}")
        
        if result['warnings']:
            print("\nWarnungen:")
            for warning in result['warnings']:
                print(f"  ⚠️  {warning}")
        
        print("\n✅ Workflow würde normal weiterlaufen.\n")
        
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def demo_critical_data_failure():
    """Demo: Kritischer Fehler bei Datenvalidierung."""
    print("\n" + "=" * 80)
    print("DEMO 2: KRITISCHER FEHLER - UNZUREICHENDE DATEN")
    print("=" * 80)
    print("\nIn diesem Szenario schlägt die Datenvalidierung fehl.\n")
    
    # Create temporary directory
    test_dir = tempfile.mkdtemp()
    events_path = os.path.join(test_dir, "events.jsonl")
    summary_path = os.path.join(test_dir, "summary.json")
    
    try:
        store = SessionStore(events_path, summary_path)
        runner = AutomationRunner(
            data_phase_timeout=5,
            strategy_phase_timeout=5,
            api_phase_timeout=5,
            heartbeat_interval=2,
            enable_validation=False
        )
        runner.session_store = store
        
        # Mock data validation to fail
        def mock_data_check():
            print("  ❌ Insufficient data: 50 records (min: 100)")
            return {
                'status': 'critical',
                'message': 'Insufficient data: 50 records (min: 100)',
                'details': {'record_count': 50}
            }
        
        with patch.object(runner, '_check_data_validation', side_effect=mock_data_check):
            result = runner._run_pre_live_checks()
        
        print("\n" + "=" * 80)
        print("ERGEBNIS:")
        print("=" * 80)
        print(f"Status: {result['status']}")
        print(f"Critical Failures: {len(result['critical_failures'])}")
        
        if result['critical_failures']:
            print("\n🚨 Kritische Fehler:")
            for i, failure in enumerate(result['critical_failures'], 1):
                print(f"  {i}. {failure}")
        
        print("\n🚫 Workflow würde ABGEBROCHEN werden.\n")
        
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def demo_strategy_warning():
    """Demo: Warnung bei Strategie-Validierung."""
    print("\n" + "=" * 80)
    print("DEMO 3: WARNUNG - HOHER DRAWDOWN")
    print("=" * 80)
    print("\nIn diesem Szenario gibt es eine Warnung bei der Strategie.\n")
    
    test_dir = tempfile.mkdtemp()
    events_path = os.path.join(test_dir, "events.jsonl")
    summary_path = os.path.join(test_dir, "summary.json")
    
    try:
        store = SessionStore(events_path, summary_path)
        runner = AutomationRunner(
            data_phase_timeout=5,
            strategy_phase_timeout=5,
            api_phase_timeout=5,
            heartbeat_interval=2,
            enable_validation=False
        )
        runner.session_store = store
        
        # Mock strategy validation to return warning
        def mock_strategy_check():
            print("  ⚠️  Strategy drawdown high: 22.0% (max: 25.0%)")
            return {
                'status': 'warning',
                'message': 'Strategy drawdown high: 22.0% (max: 25.0%)',
                'details': {'max_drawdown': 0.22}
            }
        
        with patch.object(runner, '_check_strategy_validation', side_effect=mock_strategy_check):
            result = runner._run_pre_live_checks()
        
        print("\n" + "=" * 80)
        print("ERGEBNIS:")
        print("=" * 80)
        print(f"Status: {result['status']}")
        print(f"Warnings: {len(result['warnings'])}")
        
        if result['warnings']:
            print("\n⚠️  Warnungen:")
            for warning in result['warnings']:
                print(f"  • {warning}")
        
        print("\n⚡ Workflow würde MIT VORSICHT weiterlaufen.\n")
        
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def demo_production_mode_api_check():
    """Demo: API-Check im Production-Modus."""
    print("\n" + "=" * 80)
    print("DEMO 4: PRODUCTION MODE - FEHLENDE API KEYS")
    print("=" * 80)
    print("\nIn diesem Szenario fehlen API Keys im Production-Modus.\n")
    
    test_dir = tempfile.mkdtemp()
    events_path = os.path.join(test_dir, "events.jsonl")
    summary_path = os.path.join(test_dir, "summary.json")
    
    try:
        # Set to production mode
        with patch.dict(os.environ, {'DRY_RUN': 'false'}, clear=False):
            store = SessionStore(events_path, summary_path)
            runner = AutomationRunner(
                data_phase_timeout=5,
                strategy_phase_timeout=5,
                api_phase_timeout=5,
                heartbeat_interval=2,
                enable_validation=False
            )
            runner.session_store = store
            
            # Mock API validation to fail
            def mock_validate():
                return {
                    'valid': False,
                    'missing': ['binance_api_key', 'binance_api_secret'],
                    'present': []
                }
            
            with patch('automation.runner.EnvHelper.validate_api_keys', side_effect=mock_validate):
                result = runner._run_pre_live_checks()
        
        print("\n" + "=" * 80)
        print("ERGEBNIS:")
        print("=" * 80)
        print(f"Status: {result['status']}")
        print(f"Critical Failures: {len(result['critical_failures'])}")
        
        if result['critical_failures']:
            print("\n🚨 Kritische Fehler:")
            for i, failure in enumerate(result['critical_failures'], 1):
                print(f"  {i}. {failure}")
        
        print("\n🚫 Workflow würde ABGEBROCHEN werden.")
        print("💡 Tipp: Im DRY_RUN Mode wäre dies nur eine Warnung.\n")
        
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def demo_workflow_abort():
    """Demo: Kompletter Workflow mit Abbruch."""
    print("\n" + "=" * 80)
    print("DEMO 5: VOLLSTÄNDIGER WORKFLOW-ABBRUCH")
    print("=" * 80)
    print("\nIn diesem Szenario wird der gesamte Workflow abgebrochen.\n")
    
    test_dir = tempfile.mkdtemp()
    events_path = os.path.join(test_dir, "events.jsonl")
    summary_path = os.path.join(test_dir, "summary.json")
    
    try:
        store = SessionStore(events_path, summary_path)
        runner = AutomationRunner(
            data_phase_timeout=5,
            strategy_phase_timeout=5,
            api_phase_timeout=5,
            heartbeat_interval=2,
            enable_validation=False
        )
        runner.session_store = store
        
        # Mock multiple checks to fail
        def mock_data_check():
            return {
                'status': 'critical',
                'message': 'Insufficient data: 30 records (min: 100)',
                'details': {}
            }
        
        def mock_strategy_check():
            return {
                'status': 'critical',
                'message': 'Strategy win rate too low: 35.0% (min: 40.0%)',
                'details': {}
            }
        
        with patch.object(runner, '_check_data_validation', side_effect=mock_data_check):
            with patch.object(runner, '_check_strategy_validation', side_effect=mock_strategy_check):
                result = runner.run()
        
        print("\n" + "=" * 80)
        print("WORKFLOW-ERGEBNIS:")
        print("=" * 80)
        print(f"Status: {result['status']}")
        print(f"Abort Reason: {result.get('abort_reason', 'N/A')}")
        
        if result.get('pre_live_checks'):
            checks = result['pre_live_checks']
            print(f"\nCritical Failures: {len(checks['critical_failures'])}")
            
            if checks['critical_failures']:
                print("\n🚨 Fehler:")
                for i, failure in enumerate(checks['critical_failures'], 1):
                    print(f"  {i}. {failure}")
        
        # Check that phases were NOT executed
        print(f"\nPhasen ausgeführt: {len(result.get('phases', {}))}")
        print("✅ Pre-Live Checks verhinderten fehlerhafte Ausführung!\n")
        
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("PRE-LIVE CHECKS DEMO")
    print("=" * 80)
    print("\nDiese Demo zeigt verschiedene Szenarien für Pre-Live Checks.")
    print("Die Checks laufen VOR dem eigentlichen Trading-Workflow.\n")
    
    demos = [
        ("1", "Erfolgreiche Checks", demo_successful_checks),
        ("2", "Kritischer Daten-Fehler", demo_critical_data_failure),
        ("3", "Strategie-Warnung", demo_strategy_warning),
        ("4", "Production Mode API-Check", demo_production_mode_api_check),
        ("5", "Workflow-Abbruch", demo_workflow_abort),
    ]
    
    print("Verfügbare Demos:")
    for num, desc, _ in demos:
        print(f"  {num}. {desc}")
    print("  0. Alle Demos ausführen")
    print()
    
    try:
        choice = input("Wähle Demo (0-5) oder Enter für alle: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nAbgebrochen.")
        return 0
    
    if not choice or choice == "0":
        # Run all demos
        for num, desc, demo_func in demos:
            input(f"\n>>> Drücke Enter um Demo {num} zu starten...")
            demo_func()
    else:
        # Run selected demo
        for num, desc, demo_func in demos:
            if choice == num:
                demo_func()
                break
        else:
            print(f"Ungültige Auswahl: {choice}")
            return 1
    
    print("\n" + "=" * 80)
    print("DEMO ABGESCHLOSSEN")
    print("=" * 80)
    print("\n💡 Weitere Informationen: PRE_LIVE_CHECKS_GUIDE.md")
    print("🧪 Tests ausführen: python test_pre_live_checks.py\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
