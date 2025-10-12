"""
demo_extended_tradelogger.py - Demo für erweiterten TradeLogger
===============================================================
Demonstriert die neuen Features:
- Echtgeld-Flag (is_real_money)
- Erweiterte Metriken (profit_factor, win_rate, sharpe_ratio)
"""
import os
import sys
from datetime import datetime

from utils import TradeLogger, load_trades_from_csv
from dashboard import create_dashboard


def demo_extended_logger():
    """Demonstriere erweiterten TradeLogger"""
    print("\n" + "="*70)
    print("🚀 DEMO: Erweiterter TradeLogger mit Echtgeld-Flag & Metriken")
    print("="*70)
    
    # Erstelle TradeLogger
    trades_file = "data/demo_extended_trades.csv"
    logger = TradeLogger(trades_file)
    
    print("\n📝 Beispiel-Trades werden protokolliert...\n")
    
    # Beispiel 1: Dry-Run Trade (Standardverhalten - sicher!)
    print("1. 🧪 DRY-RUN Trade (Standard):")
    logger.log_trade(
        order_type='BUY',
        price=30000.0,
        quantity=0.1,
        strategies=['RSI', 'MACD'],
        capital=10000.0,
        pnl=0.0,
        symbol='BTC/USDT'
    )
    print("   ✓ Dry-Run BUY @ $30,000")
    
    # Beispiel 2: Erfolgreiches Real-Money Trade
    print("\n2. 💰 ECHTGELD Trade (Gewinn):")
    logger.log_trade(
        order_type='SELL',
        price=31500.0,
        quantity=0.1,
        strategies=['RSI', 'Bollinger'],
        capital=10650.0,
        pnl=650.0,
        symbol='BTC/USDT',
        is_real_money=True,  # ⚠️ ECHTGELD!
        profit_factor=2.5,
        win_rate=75.0,
        sharpe_ratio=1.8
    )
    print("   ✓ Real-Money SELL @ $31,500 (Gewinn: $650)")
    
    # Beispiel 3: Dry-Run mit Verlust
    print("\n3. 🧪 DRY-RUN Trade (Verlust):")
    logger.log_trade(
        order_type='BUY',
        price=31000.0,
        quantity=0.1,
        strategies=['EMA_Cross'],
        capital=10650.0,
        pnl=0.0,
        symbol='BTC/USDT',
        is_real_money=False
    )
    logger.log_trade(
        order_type='SELL',
        price=30500.0,
        quantity=0.1,
        strategies=['MACD'],
        capital=10600.0,
        pnl=-50.0,
        symbol='BTC/USDT',
        is_real_money=False,
        profit_factor=2.0,
        win_rate=66.67,
        sharpe_ratio=1.5
    )
    print("   ✓ Dry-Run SELL @ $30,500 (Verlust: -$50)")
    
    # Beispiel 4: Real-Money Trade mit Metriken
    print("\n4. 💰 ECHTGELD Trade (mit erweiterten Metriken):")
    logger.log_trade(
        order_type='BUY',
        price=30800.0,
        quantity=0.15,
        strategies=['RSI', 'MACD', 'Volume_Spike'],
        capital=10600.0,
        pnl=0.0,
        symbol='BTC/USDT',
        is_real_money=True,  # ⚠️ ECHTGELD!
        profit_factor=1.8,
        win_rate=70.0,
        sharpe_ratio=1.6
    )
    print("   ✓ Real-Money BUY @ $30,800")
    print("   📊 Metriken: PF=1.8, WR=70%, SR=1.6")
    
    # Zeige alle Trades
    print("\n" + "="*70)
    print("📊 ALLE PROTOKOLLIERTEN TRADES")
    print("="*70)
    
    trades = load_trades_from_csv(trades_file)
    print(f"\nGesamt: {len(trades)} Trades\n")
    
    for i, trade in enumerate(trades, 1):
        real_money = trade.get('is_real_money', False)
        if isinstance(real_money, str):
            real_money = real_money.lower() in ('true', '1', 'yes')
        
        status = "💰 ECHTGELD" if real_money else "🧪 DRY-RUN"
        pnl = float(trade.get('pnl', 0))
        pnl_str = f"+${pnl:.2f}" if pnl > 0 else f"${pnl:.2f}"
        
        print(f"Trade {i}: {status}")
        print(f"  {trade['order_type']:4} @ ${float(trade['price']):,.2f} | "
              f"P&L: {pnl_str:>10} | "
              f"Kapital: ${float(trade['capital']):,.2f}")
        print(f"  Strategien: {trade.get('triggering_strategies', 'N/A')}")
        
        if trade.get('profit_factor') and float(trade['profit_factor']) > 0:
            print(f"  Metriken: PF={trade.get('profit_factor')}, "
                  f"WR={trade.get('win_rate')}%, "
                  f"SR={trade.get('sharpe_ratio')}")
        print()
    
    # Statistiken
    real_money_count = sum(1 for t in trades if str(t.get('is_real_money', False)).lower() in ('true', '1', 'yes'))
    dry_run_count = len(trades) - real_money_count
    
    print("="*70)
    print("📈 ZUSAMMENFASSUNG")
    print("="*70)
    print(f"Gesamt Trades:        {len(trades)}")
    print(f"💰 Echtgeld-Trades:   {real_money_count}")
    print(f"🧪 Dry-Run Trades:    {dry_run_count}")
    print(f"📁 Datei:             {trades_file}")
    print("="*70)
    
    return trades_file


def demo_extended_dashboard(trades_file):
    """Demonstriere erweiterte Dashboard-Anzeige"""
    print("\n" + "="*70)
    print("📊 DEMO: Dashboard mit erweiterten Metriken")
    print("="*70)
    
    from dashboard import VisualDashboard
    
    # Erstelle Dashboard
    config_file = "data/demo_extended_config.json"
    dashboard = VisualDashboard(trades_file, config_file)
    
    print("\n1. Metriken im Dashboard:")
    print("-" * 70)
    dashboard.display_metrics_console()
    
    print("\n2. HTML-Dashboard exportieren:")
    print("-" * 70)
    html_file = "data/demo_extended_dashboard.html"
    dashboard.export_dashboard_html(html_file)
    
    if os.path.exists(html_file):
        size_kb = os.path.getsize(html_file) / 1024
        print(f"   ✅ Dashboard exportiert: {html_file}")
        print(f"   📄 Dateigröße: {size_kb:.1f} KB")
        print(f"   🌐 Öffne die Datei im Browser zur Ansicht")
    
    print("\n" + "="*70)
    print("✅ Demo abgeschlossen!")
    print("="*70)
    print("\n💡 WICHTIGE HINWEISE:")
    print("   • Das Echtgeld-Flag ist standardmäßig FALSE (sicher!)")
    print("   • Nur explizit als is_real_money=True markierte Trades sind Echtgeld")
    print("   • Erweiterte Metriken helfen bei der Performance-Analyse")
    print("   • Dashboard zeigt alle Metriken übersichtlich an")
    print("="*70 + "\n")


if __name__ == '__main__':
    # Demo ausführen
    trades_file = demo_extended_logger()
    demo_extended_dashboard(trades_file)
