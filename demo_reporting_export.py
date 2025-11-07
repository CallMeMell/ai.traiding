"""
demo_reporting_export.py - Demo für erweiterte Reporting & Export-Funktionen
=============================================================================
Demonstriert die neuen Features:
- ROI-Berechnung
- Umfassende Performance-Reports
- Export als CSV/JSON
- Detaillierte Trade-History
- ReportingModule für komplette Workflows
"""

import os
import sys
from datetime import datetime, timedelta
from utils import (
    TradeLogger,
    ReportingModule,
    generate_comprehensive_report,
    calculate_roi
)


def demo_basic_reporting():
    """Demonstriere Basis-Reporting mit ROI"""
    print("\n" + "="*70)
    print("📊 DEMO 1: Basis-Reporting mit ROI")
    print("="*70)
    
    # Erstelle Beispiel-Trades
    trades_file = "data/demo_reporting_trades.csv"
    logger = TradeLogger(trades_file)
    
    print("\n📝 Generiere Beispiel-Trades...")
    
    # Simuliere Trading-Session
    initial_capital = 10000.0
    capital = initial_capital
    
    trades_data = [
        ('BUY', 30000.0, 0.1, ['RSI', 'MACD'], 0.0),
        ('SELL', 31000.0, 0.1, ['MACD'], 100.0),
        ('BUY', 30800.0, 0.1, ['Bollinger'], 0.0),
        ('SELL', 31200.0, 0.1, ['RSI'], 40.0),
        ('BUY', 31500.0, 0.1, ['EMA_Cross'], 0.0),
        ('SELL', 31000.0, 0.1, ['MACD'], -50.0),
    ]
    
    for order_type, price, qty, strategies, pnl in trades_data:
        capital += pnl
        logger.log_trade(
            order_type=order_type,
            price=price,
            quantity=qty,
            strategies=strategies,
            capital=capital,
            pnl=pnl,
            is_real_money=False  # Dry-Run für Demo
        )
    
    final_capital = capital
    roi = calculate_roi(initial_capital, final_capital)
    
    print(f"\n💰 ERGEBNISSE:")
    print(f"  Start-Kapital:    ${initial_capital:,.2f}")
    print(f"  End-Kapital:      ${final_capital:,.2f}")
    print(f"  Gesamt P&L:       ${final_capital - initial_capital:,.2f}")
    print(f"  ROI:              {roi:.2f}%")
    print(f"  Trades-Datei:     {trades_file}")
    print("="*70)


def demo_comprehensive_reporting():
    """Demonstriere umfassendes Reporting mit allen Metriken"""
    print("\n" + "="*70)
    print("📈 DEMO 2: Umfassendes Performance-Reporting")
    print("="*70)
    
    trades_file = "data/demo_reporting_trades.csv"
    
    # Erstelle ReportingModule
    module = ReportingModule(trades_file)
    
    print("\n1️⃣  Lade Trades...")
    trades = module.load_trades()
    print(f"   ✓ {len(trades)} Trades geladen")
    
    print("\n2️⃣  Berechne Equity Curve...")
    equity_curve = module.calculate_equity_curve(initial_capital=10000.0)
    print(f"   ✓ {len(equity_curve)} Datenpunkte")
    
    print("\n3️⃣  Generiere umfassenden Report...")
    report = module.generate_report(initial_capital=10000.0)
    print(f"   ✓ Report mit {len(report)} Metriken erstellt")
    
    print("\n4️⃣  Report-Zusammenfassung:")
    module.print_report_summary()


def demo_export_functions():
    """Demonstriere Export-Funktionen (CSV/JSON)"""
    print("\n" + "="*70)
    print("💾 DEMO 3: Export-Funktionen (CSV/JSON)")
    print("="*70)
    
    trades_file = "data/demo_reporting_trades.csv"
    output_dir = "data/reports"
    
    # Erstelle ReportingModule
    module = ReportingModule(trades_file)
    
    print("\n📤 Exportiere alle Reports...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exported_files = module.export_all(output_dir=output_dir, prefix=f"demo_{timestamp}")
    
    print("\n✅ EXPORTIERTE DATEIEN:")
    for key, filepath in exported_files.items():
        if filepath and os.path.exists(filepath):
            size_kb = os.path.getsize(filepath) / 1024
            print(f"  {key:25} → {filepath} ({size_kb:.1f} KB)")
    
    print("\n📁 Alle Dateien in: " + os.path.abspath(output_dir))
    print("="*70)


def demo_detailed_trade_history():
    """Demonstriere detaillierte Trade-History mit kumulativen Metriken"""
    print("\n" + "="*70)
    print("📋 DEMO 4: Detaillierte Trade-History")
    print("="*70)
    
    from utils import load_trades_from_csv, export_trade_history_with_metrics
    
    trades_file = "data/demo_reporting_trades.csv"
    trades = load_trades_from_csv(trades_file)
    
    print(f"\n📊 Exportiere detaillierte Trade-History...")
    detail_file = "data/demo_trade_history_detailed.csv"
    result = export_trade_history_with_metrics(trades, detail_file)
    
    if result:
        print(f"   ✓ Detaillierte History exportiert: {detail_file}")
        
        # Zeige Vorschau
        import pandas as pd
        df = pd.read_csv(detail_file)
        
        print(f"\n📄 VORSCHAU (erste 5 Trades):")
        print(df.head().to_string(index=False))
        
        print(f"\n📊 ZUSAMMENFASSUNG:")
        print(f"  Total Trades:      {len(df)}")
        print(f"  Final Cum. P&L:    ${df['cumulative_pnl'].iloc[-1]:,.2f}")
    
    print("="*70)


def demo_json_export():
    """Demonstriere JSON-Export für API-Integration"""
    print("\n" + "="*70)
    print("🔌 DEMO 5: JSON-Export für API-Integration")
    print("="*70)
    
    from utils import load_trades_from_csv, export_trades_to_json
    import json
    
    trades_file = "data/demo_reporting_trades.csv"
    trades = load_trades_from_csv(trades_file)
    
    print(f"\n📤 Exportiere Trades als JSON...")
    json_file = "data/demo_trades_api.json"
    result = export_trades_to_json(trades, json_file, pretty=True)
    
    if result:
        print(f"   ✓ JSON exportiert: {json_file}")
        
        # Zeige Vorschau
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📄 JSON-STRUKTUR (erster Trade):")
        print(json.dumps(data[0], indent=2, ensure_ascii=False))
        
        print(f"\n✅ JSON-Datei bereit für:")
        print(f"  • REST API Integration")
        print(f"  • Web Dashboard")
        print(f"  • Externe Analytics Tools")
    
    print("="*70)


def demo_real_vs_dryrun_tracking():
    """Demonstriere Echtgeld vs. Dry-Run Tracking"""
    print("\n" + "="*70)
    print("💰 DEMO 6: Echtgeld vs. Dry-Run Tracking")
    print("="*70)
    
    # Erstelle Mixed Trades
    mixed_trades_file = "data/demo_mixed_trades.csv"
    logger = TradeLogger(mixed_trades_file)
    
    print("\n📝 Generiere gemischte Trades...")
    
    trades_data = [
        # Dry-Run Trades
        ('BUY', 30000.0, 0.1, ['RSI'], 0.0, False),
        ('SELL', 31000.0, 0.1, ['MACD'], 100.0, False),
        # Real-Money Trades
        ('BUY', 30500.0, 0.1, ['Bollinger'], 0.0, True),
        ('SELL', 31200.0, 0.1, ['RSI'], 70.0, True),
        # Dry-Run Trade
        ('BUY', 31500.0, 0.1, ['EMA'], 0.0, False),
        ('SELL', 31000.0, 0.1, ['MACD'], -50.0, False),
    ]
    
    capital = 10000.0
    for order_type, price, qty, strategies, pnl, is_real in trades_data:
        capital += pnl
        logger.log_trade(
            order_type=order_type,
            price=price,
            quantity=qty,
            strategies=strategies,
            capital=capital,
            pnl=pnl,
            is_real_money=is_real
        )
    
    # Generiere Report
    module = ReportingModule(mixed_trades_file)
    report = module.generate_report(initial_capital=10000.0)
    
    print(f"\n📊 STATISTIK:")
    print(f"  Gesamt Trades:        {report['total_trades']}")
    print(f"  💰 Echtgeld-Trades:   {report['total_real_money_trades']}")
    print(f"  🧪 Dry-Run Trades:    {report['total_dry_run_trades']}")
    print(f"  Gesamt P&L:           ${report['total_pnl']:,.2f}")
    print(f"  ROI:                  {report['roi']:.2f}%")
    
    print("\n⚠️  WICHTIG:")
    print("  • Echtgeld-Trades werden explizit markiert")
    print("  • Standard ist IMMER Dry-Run (Sicherheit!)")
    print("  • Report trennt beide Kategorien")
    
    print("="*70)


def main():
    """Hauptfunktion - führt alle Demos aus"""
    print("\n" + "="*70)
    print("🚀 ERWEITERTE REPORTING & EXPORT - DEMONSTRATION")
    print("="*70)
    print("\nDiese Demo zeigt die neuen Features:")
    print("  • ROI-Berechnung")
    print("  • Performance-Metriken (Sharpe, Profit Factor, etc.)")
    print("  • Export als CSV/JSON")
    print("  • Detaillierte Trade-History")
    print("  • Echtgeld vs. Dry-Run Tracking")
    print("="*70)
    
    # Führe alle Demos aus
    demo_basic_reporting()
    demo_comprehensive_reporting()
    demo_export_functions()
    demo_detailed_trade_history()
    demo_json_export()
    demo_real_vs_dryrun_tracking()
    
    print("\n" + "="*70)
    print("✅ ALLE DEMOS ABGESCHLOSSEN")
    print("="*70)
    print("\n💡 NÄCHSTE SCHRITTE:")
    print("  1. Prüfe die exportierten Dateien in data/reports/")
    print("  2. Integriere ReportingModule in deinen Trading-Bot")
    print("  3. Verwende JSON-Export für Web-Dashboard")
    print("  4. Nutze detaillierte Trade-History für Analyse")
    print("\n📚 WEITERE INFOS:")
    print("  • test_reporting_export.py - Unit- und Integration-Tests")
    print("  • utils.py - Alle Reporting-Funktionen")
    print("  • PERFORMANCE_METRICS_GUIDE.md - Dokumentation")
    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo abgebrochen")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
