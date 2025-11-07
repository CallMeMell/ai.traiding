"""
example_reporting_usage.py - Praktisches Beispiel für Reporting & Export
==========================================================================
Zeigt typische Anwendungsfälle für das erweiterte Reporting-System.
"""

from datetime import datetime
from utils import ReportingModule, TradeLogger


def example_1_daily_report():
    """Beispiel 1: Täglicher Performance-Report"""
    print("\n" + "="*70)
    print("📊 Beispiel 1: Täglicher Performance-Report")
    print("="*70)
    
    # Am Ende des Trading-Tages
    module = ReportingModule("data/trades.csv")
    
    # Generiere Report
    report = module.generate_report(initial_capital=10000.0)
    
    # Zeige wichtigste Metriken
    print(f"\n📈 Performance heute:")
    print(f"  ROI:           {report['roi']:.2f}%")
    print(f"  Win Rate:      {report['win_rate']:.2f}%")
    print(f"  Sharpe Ratio:  {report['sharpe_ratio']:.4f}")
    print(f"  Max Drawdown:  {report['max_drawdown']:.2f}%")
    
    # Speichere Report für Historie
    timestamp = datetime.now().strftime("%Y%m%d")
    module.export_all(prefix=f"daily_{timestamp}")
    
    print(f"\n✅ Täglicher Report exportiert")


def example_2_weekly_analysis():
    """Beispiel 2: Wöchentliche Analyse mit vollständigem Export"""
    print("\n" + "="*70)
    print("📊 Beispiel 2: Wöchentliche Analyse")
    print("="*70)
    
    # Am Ende der Woche
    module = ReportingModule("data/trades.csv")
    
    # Voller Report mit Console-Ausgabe
    print("\n📄 Vollständiger Wochen-Report:")
    module.print_report_summary()
    
    # Export für Archive
    week_num = datetime.now().strftime("%Y_W%W")
    exported_files = module.export_all(
        output_dir="data/reports/weekly",
        prefix=f"week_{week_num}"
    )
    
    print(f"\n✅ {len(exported_files)} Dateien exportiert für Woche {week_num}")


def example_3_performance_monitoring():
    """Beispiel 3: Performance-Überwachung mit Schwellenwerten"""
    print("\n" + "="*70)
    print("📊 Beispiel 3: Performance-Überwachung")
    print("="*70)
    
    module = ReportingModule("data/trades.csv")
    report = module.generate_report(initial_capital=10000.0)
    
    print("\n🔍 Prüfe Performance-Schwellenwerte...")
    
    warnings = []
    
    # Prüfe Sharpe Ratio
    if report['sharpe_ratio'] < 0.5:
        warnings.append("⚠️  Niedrige Sharpe Ratio (< 0.5)")
    
    # Prüfe Max Drawdown
    if report['max_drawdown'] < -20.0:
        warnings.append("⚠️  Hoher Drawdown (< -20%)")
    
    # Prüfe Win Rate
    if report['win_rate'] < 40.0:
        warnings.append("⚠️  Niedrige Win Rate (< 40%)")
    
    # Prüfe Profit Factor
    if report['profit_factor'] < 1.0:
        warnings.append("⚠️  Profit Factor unter 1.0 (Verluste)")
    
    if warnings:
        print("\n❌ WARNUNGEN:")
        for warning in warnings:
            print(f"  {warning}")
        print("\n💡 Empfehlung: Strategie überprüfen!")
    else:
        print("\n✅ Alle Performance-Metriken im grünen Bereich")


def example_4_json_api_export():
    """Beispiel 4: JSON-Export für Web-Dashboard"""
    print("\n" + "="*70)
    print("📊 Beispiel 4: JSON-Export für Web-Dashboard")
    print("="*70)
    
    from utils import export_report_to_json, export_trades_to_json
    
    module = ReportingModule("data/trades.csv")
    report = module.generate_report(initial_capital=10000.0)
    trades = module.trades
    
    # Export für API
    print("\n📤 Exportiere für Web-Dashboard...")
    
    export_report_to_json(
        report,
        filepath="data/api/performance.json",
        pretty=True
    )
    
    export_trades_to_json(
        trades,
        filepath="data/api/trades.json",
        pretty=True
    )
    
    print("✅ JSON-Dateien bereit für:")
    print("  • REST API: GET /api/performance")
    print("  • REST API: GET /api/trades")
    print("  • Web Dashboard Visualisierung")


def example_5_trading_integration():
    """Beispiel 5: Integration in Trading-Bot"""
    print("\n" + "="*70)
    print("📊 Beispiel 5: Integration in Trading-Bot")
    print("="*70)
    
    # Simuliere Trading-Session
    trades_file = "data/example_bot_trades.csv"
    logger = TradeLogger(trades_file)
    
    print("\n🤖 Trading-Bot Session gestartet...")
    print("📝 Protokolliere Trades...")
    
    # Simuliere einige Trades
    capital = 10000.0
    
    # Trade 1
    logger.log_trade(
        order_type='BUY',
        price=30000.0,
        quantity=0.1,
        strategies=['RSI', 'MACD'],
        capital=capital,
        pnl=0.0,
        is_real_money=False  # DRY_RUN default!
    )
    
    # Trade 2 - Profit
    capital += 150.0
    logger.log_trade(
        order_type='SELL',
        price=31500.0,
        quantity=0.1,
        strategies=['MACD'],
        capital=capital,
        pnl=150.0,
        is_real_money=False
    )
    
    print("✅ Trades protokolliert")
    
    # Am Ende der Session: Report
    print("\n📊 Session-Report:")
    module = ReportingModule(trades_file)
    report = module.generate_report(initial_capital=10000.0)
    
    print(f"  Trades:     {report['total_trades']}")
    print(f"  P&L:        ${report['total_pnl']:,.2f}")
    print(f"  ROI:        {report['roi']:.2f}%")
    
    # Export Session-Report
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    module.export_all(prefix=f"session_{session_id}")
    
    print(f"\n✅ Session-Report exportiert: session_{session_id}")


def example_6_csv_for_excel():
    """Beispiel 6: CSV-Export für Excel-Analyse"""
    print("\n" + "="*70)
    print("📊 Beispiel 6: CSV-Export für Excel-Analyse")
    print("="*70)
    
    from utils import export_trade_history_with_metrics
    
    module = ReportingModule("data/trades.csv")
    trades = module.load_trades()
    
    print("\n📤 Exportiere detaillierte Trade-History für Excel...")
    
    # Export mit allen Details und kumulativen Metriken
    export_trade_history_with_metrics(
        trades,
        filepath="data/excel_export/trade_history_detailed.csv"
    )
    
    print("✅ CSV exportiert mit:")
    print("  • Trade Number")
    print("  • Timestamp")
    print("  • Symbol, Type, Price, Quantity")
    print("  • P&L (einzeln)")
    print("  • Cumulative P&L")
    print("  • Capital nach Trade")
    print("  • Performance-Metriken")
    print("\n💡 Öffne in Excel für Pivot-Tables und Charts!")


def main():
    """Führe alle Beispiele aus"""
    print("\n" + "="*70)
    print("📚 REPORTING & EXPORT - PRAKTISCHE BEISPIELE")
    print("="*70)
    print("\nDiese Beispiele zeigen typische Anwendungsfälle:")
    print("  1. Täglicher Performance-Report")
    print("  2. Wöchentliche Analyse")
    print("  3. Performance-Überwachung")
    print("  4. JSON-Export für Web-Dashboard")
    print("  5. Integration in Trading-Bot")
    print("  6. CSV-Export für Excel-Analyse")
    print("="*70)
    
    # Nur Beispiel 3 und 5 ausführen (die anderen benötigen existierende Trades)
    try:
        example_3_performance_monitoring()
        example_5_trading_integration()
        
        print("\n" + "="*70)
        print("✅ BEISPIELE ABGESCHLOSSEN")
        print("="*70)
        print("\n💡 Tipp: Passe die Beispiele an deine Bedürfnisse an!")
        print("📚 Siehe REPORTING_AND_EXPORT_GUIDE.md für Details")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n⚠️  Hinweis: {e}")
        print("💡 Führe zuerst demo_reporting_export.py aus, um Testdaten zu erstellen")


if __name__ == '__main__':
    main()
