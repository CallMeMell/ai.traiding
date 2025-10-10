"""
demo_automated_workflow.py - Demo für Automatisierten Workflow
===============================================================
Demonstriert den vollautomatischen Workflow zur Vorbereitung
des Trading-Bots für Echtgeld-Einsatz.
"""

import sys
import logging
from automated_workflow import AutomatedWorkflow
from config import config
from utils import setup_logging


def main():
    """
    Hauptfunktion für Demo
    """
    print("=" * 70)
    print("🚀 AUTOMATISIERTER TRADING-BOT WORKFLOW - DEMO")
    print("=" * 70)
    print()
    print("Dieser Workflow bereitet den Trading-Bot automatisch vor:")
    print("  1. Datenanalyse und -kreierung (Zeitlimit: 2 Stunden)")
    print("  2. Strategie-Optimierung (Zeitlimit: 2 Stunden)")
    print("  3. API-Vorbereitung (Zeitlimit: 1 Stunde)")
    print("  4. Live-View Session Integration")
    print("  5. Finale Validierung")
    print()
    print("Alle Schritte laufen vollautomatisch mit:")
    print("  ✓ Zeitlimit-Überwachung")
    print("  ✓ Automatischer Fehlerkorrektur")
    print("  ✓ Zwischenschritt-Validierung")
    print("  ✓ Live-View Visualisierung")
    print()
    print("=" * 70)
    print()
    
    # Frage Benutzer
    response = input("Möchten Sie den Workflow starten? (j/n): ").lower()
    
    if response != 'j':
        print("\n❌ Workflow abgebrochen")
        return
    
    print("\n🚀 Starte Workflow...\n")
    
    # Setup Logging
    setup_logging(config.log_level, config.log_file)
    
    try:
        # Erstelle Workflow
        workflow = AutomatedWorkflow()
        
        # Führe Workflow aus
        results = workflow.run_workflow(auto_continue=True)
        
        # Zeige Zusammenfassung
        print("\n" + "=" * 70)
        print("✅ WORKFLOW ABGESCHLOSSEN")
        print("=" * 70)
        print(f"Session ID: {results['session_id']}")
        print(f"Status: {results['status']}")
        print(f"Fortschritt: {results['progress']}")
        print(f"Abgeschlossene Schritte: {results['completed_steps']}/{results['total_steps']}")
        print(f"Fehlgeschlagene Schritte: {results['failed_steps']}")
        print(f"Gesamtdauer: {results['elapsed_time']:.2f}s")
        print("=" * 70)
        print()
        print(f"📁 Session-Datei: {workflow.session.session_file}")
        print(f"📊 Live-View: /view-session/{workflow.session_id}")
        print()
        
        # Empfehlungen
        if results['status'] == 'COMPLETED' and results['failed_steps'] == 0:
            print("✅ ALLE SCHRITTE ERFOLGREICH!")
            print()
            print("🎯 Nächste Schritte:")
            print("  1. Überprüfe Session-Details im Live-View")
            print("  2. Teste Bot im Paper-Trading Modus")
            print("  3. Führe weitere Tests auf Binance Testnet durch")
            print("  4. Erst nach erfolgreichen Tests: Echtgeld erwägen")
            print()
            print("⚠️  WARNUNG: Echtgeld-Trading birgt erhebliche Risiken!")
        else:
            print("⚠️  WORKFLOW MIT FEHLERN ABGESCHLOSSEN")
            print()
            print("🔧 Empfohlene Aktionen:")
            print("  1. Überprüfe Log-Datei für Details")
            print("  2. Korrigiere Fehler und führe Workflow erneut aus")
            print("  3. Kontaktiere Support bei persistenten Problemen")
        
        print()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Workflow manuell abgebrochen")
        print("Session-Datei wurde gespeichert für spätere Analyse")
    
    except Exception as e:
        print(f"\n\n❌ Kritischer Fehler: {e}")
        print("Siehe Log-Datei für Details")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
