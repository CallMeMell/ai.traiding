"""
demo_strategy_selection.py - Demo der automatischen Strategie-Auswahl
=====================================================================

Zeigt die Funktionsweise der automatischen Strategie-Auswahl
mit simulierten Daten.
"""

from strategy_selector import StrategySelector
from utils import generate_sample_data, setup_logging

logger = setup_logging(log_level="INFO")


def main():
    """Demo der Strategie-Auswahl"""
    
    print("\n" + "=" * 70)
    print("  🎯 DEMO: AUTOMATISCHE STRATEGIE-AUSWAHL")
    print("=" * 70)
    print()
    print("Dieses Demo zeigt wie die automatische Strategie-Auswahl funktioniert.")
    print("Es analysiert alle verfügbaren Strategien und empfiehlt die beste.")
    print()
    print("=" * 70)
    
    # Generiere Demo-Daten
    print("\n📊 Generiere historische Marktdaten...")
    data = generate_sample_data(n_bars=1000, start_price=30000)
    print(f"✓ {len(data)} Kerzen generiert")
    print(f"  Zeitraum: {data['timestamp'].iloc[0]} bis {data['timestamp'].iloc[-1]}")
    
    # Erstelle Selector
    print("\n🔧 Erstelle Strategy Selector...")
    selector = StrategySelector(
        initial_capital=10000.0,
        trade_size=100.0,
        min_trades=8
    )
    print("✓ Selector erstellt")
    print(f"  Initial Capital: ${selector.initial_capital:,.2f}")
    print(f"  Trade Size: {selector.trade_size}")
    print(f"  Min Trades: {selector.min_trades}")
    
    # Zeige Gewichtung
    print("\n📈 Bewertungs-Gewichtung:")
    for metric, weight in selector.weights.items():
        print(f"  {metric:20s}: {weight*100:>5.1f}%")
    
    # Führe Auswahl durch
    print("\n⏳ Führe Strategie-Auswahl durch...")
    print("   (Dies kann einige Minuten dauern)")
    print()
    
    best_name, best_score = selector.run_selection(data)
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("📊 ZUSAMMENFASSUNG")
    print("=" * 70)
    print(f"Analysierte Strategien: {len(selector.results)}")
    print(f"Empfohlene Strategie:   {best_name}")
    print(f"Score:                  {best_score.score:.2f}/100")
    print()
    print("Metriken der empfohlenen Strategie:")
    print(f"  ROI:           {best_score.roi:+.2f}%")
    print(f"  Sharpe Ratio:  {best_score.sharpe_ratio:.2f}")
    print(f"  Calmar Ratio:  {best_score.calmar_ratio:.2f}")
    print(f"  Max Drawdown:  {best_score.max_drawdown:.2f}%")
    print(f"  Win Rate:      {best_score.win_rate:.1f}%")
    print(f"  Total Trades:  {best_score.total_trades}")
    print(f"  Avg P&L:       ${best_score.avg_trade:+.2f}")
    print(f"  Final Capital: ${best_score.final_capital:,.2f}")
    print("=" * 70)
    
    # Export
    print("\n💾 Exportiere Ranking...")
    selector.export_ranking("data/demo_strategy_ranking.csv")
    
    print("\n✅ Demo abgeschlossen!")
    print()
    print("Nächste Schritte:")
    print("  1. Prüfe data/demo_strategy_ranking.csv für vollständiges Ranking")
    print("  2. Führe setup_live.py aus um Strategie für Live-Trading zu konfigurieren")
    print("  3. Lies STRATEGY_SELECTION_GUIDE.md für weitere Details")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo abgebrochen")
    except Exception as e:
        logger.error(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
