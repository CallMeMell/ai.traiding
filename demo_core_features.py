"""
Demo: Core Features Implementation
====================================
Demonstriert die neu implementierten Kernfunktionen:
- Alert System (Telegram & Email)
- Database Integration
- Circuit Breaker (bereits implementiert)
- Kelly Criterion (bereits implementiert)
"""
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_alert_system():
    """Demonstriere Alert System"""
    print("\n" + "="*70)
    print("📱 ALERT SYSTEM DEMO")
    print("="*70)
    
    from alerts import AlertManager
    
    # Initialize Alert Manager (reads from .env)
    alert_manager = AlertManager(
        enable_telegram=os.getenv('ENABLE_TELEGRAM_ALERTS', 'false').lower() == 'true',
        enable_email=os.getenv('ENABLE_EMAIL_ALERTS', 'false').lower() == 'true'
    )
    
    if not alert_manager.is_any_channel_active():
        print("⚠️ Keine Alert-Kanäle aktiviert")
        print("💡 Setze ENABLE_TELEGRAM_ALERTS=true oder ENABLE_EMAIL_ALERTS=true in .env")
        print("📚 Siehe ALERT_SYSTEM_GUIDE.md für Setup-Anleitung")
        return
    
    print("\n✅ Alert Manager initialisiert")
    print(f"   Telegram: {'✓' if alert_manager.telegram.enabled else '✗'}")
    print(f"   Email:    {'✓' if alert_manager.email.enabled else '✗'}")
    
    # Demo Trade Alert
    print("\n📊 Sende Demo Trade Alert...")
    results = alert_manager.send_trade_alert(
        order_type='BUY',
        symbol='BTC/USDT',
        price=50000.0,
        quantity=0.1,
        strategies=['Demo RSI', 'Demo EMA'],
        capital=10500.0,
        pnl=500.0
    )
    
    for channel, success in results.items():
        status = "✓" if success else "✗"
        print(f"   {status} {channel.capitalize()}: {'Erfolgreich' if success else 'Fehlgeschlagen'}")
    
    # Demo Performance Update
    print("\n📈 Sende Demo Performance Update...")
    results = alert_manager.send_performance_update(
        capital=10500.0,
        initial_capital=10000.0,
        total_trades=25,
        win_rate=65.0,
        profit_factor=1.8,
        sharpe_ratio=1.5
    )
    
    for channel, success in results.items():
        status = "✓" if success else "✗"
        print(f"   {status} {channel.capitalize()}: {'Erfolgreich' if success else 'Fehlgeschlagen'}")
    
    # Statistiken
    stats = alert_manager.get_statistics()
    print("\n📊 Alert Statistiken:")
    print(f"   Total Alerts:      {stats['total_alerts']}")
    print(f"   Telegram Sent:     {stats['telegram_sent']}")
    print(f"   Telegram Failed:   {stats['telegram_failed']}")
    print(f"   Email Sent:        {stats['email_sent']}")
    print(f"   Email Failed:      {stats['email_failed']}")


def demo_database():
    """Demonstriere Database Integration"""
    print("\n" + "="*70)
    print("💾 DATABASE INTEGRATION DEMO")
    print("="*70)
    
    from db import DatabaseManager
    import tempfile
    
    # Nutze temporäre Datenbank für Demo
    db_path = tempfile.mktemp(suffix='.db')
    
    try:
        with DatabaseManager(db_path) as db:
            print(f"\n✅ Database initialisiert: {db_path}")
            
            # Demo Trades einfügen
            print("\n📝 Füge Demo-Trades ein...")
            trades = [
                ('BUY', 50000.0, 0.1, ['RSI', 'EMA'], 10000.0, 0.0),
                ('SELL', 51000.0, 0.1, ['RSI', 'EMA'], 10100.0, 100.0),
                ('BUY', 51500.0, 0.1, ['Bollinger'], 10100.0, 0.0),
                ('SELL', 51200.0, 0.1, ['Bollinger'], 10070.0, -30.0),
            ]
            
            for order_type, price, quantity, strategies, capital, pnl in trades:
                trade_id = db.insert_trade(
                    symbol="BTC/USDT",
                    order_type=order_type,
                    price=price,
                    quantity=quantity,
                    strategies=strategies,
                    capital=capital,
                    pnl=pnl
                )
                print(f"   ✓ Trade #{trade_id}: {order_type} @ ${price:,.0f} (P&L: ${pnl:+,.0f})")
            
            # Statistiken abrufen
            print("\n📊 Trade-Statistiken:")
            stats = db.get_trade_statistics()
            print(f"   Total Trades:      {stats['total_trades']}")
            print(f"   Winning Trades:    {stats['winning_trades']}")
            print(f"   Losing Trades:     {stats['losing_trades']}")
            print(f"   Win Rate:          {stats['win_rate']:.2f}%")
            print(f"   Total P&L:         ${stats['total_pnl']:,.2f}")
            print(f"   Avg P&L:           ${stats['avg_pnl']:,.2f}")
            print(f"   Best Trade:        ${stats['best_trade']:,.2f}")
            print(f"   Worst Trade:       ${stats['worst_trade']:,.2f}")
            
            # Equity Curve einfügen
            print("\n📈 Füge Equity Curve Points ein...")
            equity_points = [
                (10000.0, 0.0),
                (10100.0, -1.0),
                (10070.0, -3.0),
            ]
            
            for equity, drawdown in equity_points:
                point_id = db.insert_equity_point(equity, drawdown)
                print(f"   ✓ Point #{point_id}: ${equity:,.0f} (Drawdown: {drawdown:.1f}%)")
            
            # Performance Metric einfügen
            print("\n💹 Füge Performance Metric ein...")
            metric_id = db.insert_performance_metric(
                capital=10070.0,
                total_pnl=70.0,
                roi_percent=0.7,
                total_trades=4,
                winning_trades=1,
                losing_trades=1,
                win_rate=50.0,
                profit_factor=3.33,
                sharpe_ratio=1.2,
                max_drawdown=-3.0
            )
            print(f"   ✓ Metric #{metric_id} gespeichert")
            
            # DataFrame Export
            print("\n📋 Export als DataFrame:")
            trades_df = db.get_trades_df()
            print(f"   ✓ {len(trades_df)} Trades exportiert")
            print(f"   Columns: {', '.join(trades_df.columns[:5])}...")
            
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"\n🗑️ Temporäre Datenbank gelöscht: {db_path}")


def demo_circuit_breaker():
    """Demonstriere Circuit Breaker (bereits implementiert)"""
    print("\n" + "="*70)
    print("🚨 CIRCUIT BREAKER DEMO")
    print("="*70)
    
    from utils import calculate_current_drawdown
    
    print("\n✅ Circuit Breaker ist bereits implementiert!")
    print("   Location: main.py, utils.py, config.py")
    print("   Status: ACTIVE in Production Mode (DRY_RUN=false)")
    
    # Demo Drawdown Calculation
    print("\n📊 Drawdown-Berechnung Demo:")
    equity_curves = [
        [10000, 11000, 10500, 9000, 9500],   # -18.2% Drawdown
        [10000, 12000, 11000, 8000, 9000],   # -33.3% Drawdown
    ]
    
    for i, equity_curve in enumerate(equity_curves, 1):
        drawdown = calculate_current_drawdown(equity_curve)
        print(f"\n   Equity Curve #{i}: {equity_curve}")
        print(f"   Max Equity:  ${max(equity_curve):,.0f}")
        print(f"   Current:     ${equity_curve[-1]:,.0f}")
        print(f"   Drawdown:    {drawdown:.2f}%")
        
        if drawdown < -20:
            print(f"   🚨 Circuit Breaker würde auslösen! (Limit: -20%)")
        else:
            print(f"   ✓ OK (Limit: -20%)")


def demo_kelly_criterion():
    """Demonstriere Kelly Criterion (bereits implementiert)"""
    print("\n" + "="*70)
    print("🎯 KELLY CRITERION DEMO")
    print("="*70)
    
    from utils import calculate_kelly_criterion, calculate_kelly_position_size
    
    print("\n✅ Kelly Criterion ist bereits implementiert!")
    print("   Location: utils.py, lsob_strategy.py, config.py")
    print("   Status: Konfigurierbar (enable_kelly_criterion)")
    
    # Demo Kelly Berechnung
    print("\n📊 Kelly Criterion Berechnung Demo:")
    scenarios = [
        {'win_rate': 0.60, 'avg_win': 150.0, 'avg_loss': 100.0},
        {'win_rate': 0.55, 'avg_win': 200.0, 'avg_loss': 150.0},
        {'win_rate': 0.70, 'avg_win': 100.0, 'avg_loss': 100.0},
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        kelly_pct = calculate_kelly_criterion(
            win_rate=scenario['win_rate'],
            avg_win=scenario['avg_win'],
            avg_loss=scenario['avg_loss']
        )
        
        position_size = calculate_kelly_position_size(
            capital=10000.0,
            win_rate=scenario['win_rate'],
            avg_win=scenario['avg_win'],
            avg_loss=scenario['avg_loss'],
            kelly_fraction=0.5,  # Half Kelly (konservativ)
            max_position_pct=0.25
        )
        
        print(f"\n   Scenario #{i}:")
        print(f"   Win Rate:      {scenario['win_rate']*100:.0f}%")
        print(f"   Avg Win:       ${scenario['avg_win']:.0f}")
        print(f"   Avg Loss:      ${scenario['avg_loss']:.0f}")
        print(f"   Kelly %:       {kelly_pct*100:.2f}%")
        print(f"   Half Kelly %:  {kelly_pct*50:.2f}%")
        print(f"   Position Size: ${position_size:,.0f}")


def main():
    """Hauptfunktion"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🚀 CORE FEATURES IMPLEMENTATION - DEMO".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    print("\nDieses Demo-Skript zeigt alle implementierten Kernfunktionen:")
    print("  1. 📱 Alert System (Telegram & Email)")
    print("  2. 💾 Database Integration")
    print("  3. 🚨 Circuit Breaker (bereits implementiert)")
    print("  4. 🎯 Kelly Criterion (bereits implementiert)")
    
    try:
        # Demo Alert System
        demo_alert_system()
        
        # Demo Database
        demo_database()
        
        # Demo Circuit Breaker
        demo_circuit_breaker()
        
        # Demo Kelly Criterion
        demo_kelly_criterion()
        
        print("\n" + "="*70)
        print("✅ DEMO ABGESCHLOSSEN")
        print("="*70)
        print("\n📚 Weitere Informationen:")
        print("   - ALERT_SYSTEM_GUIDE.md")
        print("   - DATABASE_INTEGRATION_GUIDE.md")
        print("   - CORE_FEATURES_IMPLEMENTATION_SUMMARY.md")
        print("   - CIRCUIT_BREAKER_IMPLEMENTATION_SUMMARY.md")
        print("   - KELLY_CRITERION_GUIDE.md")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo abgebrochen durch Benutzer")
    except Exception as e:
        print(f"\n\n❌ Fehler während Demo: {e}")
        logger.exception("Demo error")


if __name__ == "__main__":
    main()
