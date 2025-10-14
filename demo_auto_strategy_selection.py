"""
demo_auto_strategy_selection.py - Demo der automatischen Strategie-Auswahl
==========================================================================

Demonstriert verschiedene Modi und Features der automatischen Strategie-Auswahl
"""

import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategy_selector import StrategySelector
from utils import generate_sample_data


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_basic_usage():
    """Demo: Grundlegende Verwendung"""
    print_section("Demo 1: Grundlegende Verwendung")
    
    print("Generiere Testdaten...")
    data = generate_sample_data(n_bars=500, start_price=30000)
    print(f"✓ {len(data)} Datenpunkte generiert\n")
    
    print("Erstelle Strategie-Selector...")
    selector = StrategySelector(
        initial_capital=10000.0,
        trade_size=100.0,
        min_trades=5
    )
    print("✓ Selector initialisiert\n")
    
    print("Führe automatische Strategie-Auswahl durch...")
    best_name, best_score = selector.run_selection(data)
    
    print(f"\n🏆 ERGEBNIS:")
    print(f"   Beste Strategie: {best_name}")
    print(f"   Score: {best_score.score:.2f}/100")
    print(f"   ROI: {best_score.roi:+.2f}%")
    print(f"   Win Rate: {best_score.win_rate:.1f}%")


def demo_custom_weights():
    """Demo: Benutzerdefinierte Gewichtung"""
    print_section("Demo 2: Konservative Strategie-Auswahl")
    
    print("Verwende konservative Gewichtung (Fokus auf Sharpe & Drawdown)...\n")
    
    # Konservative Gewichtung: mehr Fokus auf Risikomanagement
    conservative_weights = {
        'roi': 0.20,           # Weniger Fokus auf ROI
        'sharpe_ratio': 0.35,  # Mehr Fokus auf Sharpe
        'calmar_ratio': 0.25,  # Mehr Fokus auf Calmar
        'win_rate': 0.10,
        'max_drawdown': 0.10   # Risikominimierung
    }
    
    data = generate_sample_data(n_bars=500, start_price=30000)
    
    selector = StrategySelector(
        initial_capital=10000.0,
        trade_size=100.0,
        min_trades=5,
        weights=conservative_weights
    )
    
    print("Führe Auswahl mit konservativer Gewichtung durch...")
    best_name, best_score = selector.run_selection(data)
    
    print(f"\n🏆 ERGEBNIS (Konservativ):")
    print(f"   Beste Strategie: {best_name}")
    print(f"   Score: {best_score.score:.2f}/100")
    print(f"   Sharpe Ratio: {best_score.sharpe_ratio:.2f}")
    print(f"   Max Drawdown: {best_score.max_drawdown:.2f}%")


def demo_high_capital():
    """Demo: Größeres Kapital"""
    print_section("Demo 3: Strategie-Auswahl mit größerem Kapital")
    
    print("Simuliere Auswahl mit $100,000 Startkapital...\n")
    
    data = generate_sample_data(n_bars=500, start_price=30000)
    
    selector = StrategySelector(
        initial_capital=100000.0,  # Größeres Kapital
        trade_size=1000.0,         # Größere Positionsgrößen
        min_trades=10
    )
    
    print("Führe Auswahl mit großem Kapital durch...")
    best_name, best_score = selector.run_selection(data)
    
    print(f"\n🏆 ERGEBNIS (Großes Kapital):")
    print(f"   Beste Strategie: {best_name}")
    print(f"   Score: {best_score.score:.2f}/100")
    print(f"   Final Capital: ${best_score.final_capital:,.2f}")
    print(f"   Avg Trade: ${best_score.avg_trade:+,.2f}")


def demo_export_and_compare():
    """Demo: Export und Vergleich"""
    print_section("Demo 4: Ranking Export und Vergleich")
    
    print("Führe Auswahl durch und exportiere Ranking...\n")
    
    data = generate_sample_data(n_bars=500, start_price=30000)
    
    selector = StrategySelector(
        initial_capital=10000.0,
        trade_size=100.0,
        min_trades=5
    )
    
    best_name, best_score = selector.run_selection(data)
    
    # Export zu temporärer Datei
    import tempfile
    export_path = os.path.join(tempfile.gettempdir(), "demo_strategy_ranking.csv")
    selector.export_ranking(export_path)
    
    print(f"\n✓ Ranking exportiert: {export_path}")
    print(f"\n📊 Top 3 Strategien:")
    
    # Sortiere und zeige Top 3
    sorted_results = sorted(
        selector.results.items(),
        key=lambda x: x[1].score,
        reverse=True
    )[:3]
    
    for rank, (name, score) in enumerate(sorted_results, 1):
        emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        print(f"\n{emoji} #{rank}: {name}")
        print(f"   Score: {score.score:.2f}")
        print(f"   ROI: {score.roi:+.2f}%")
        print(f"   Sharpe: {score.sharpe_ratio:.2f}")
        print(f"   Win Rate: {score.win_rate:.1f}%")


def demo_robustness_filter():
    """Demo: Robustheit-Filter"""
    print_section("Demo 5: Robustheit-Filter (Hohe Mindestanzahl Trades)")
    
    print("Verwende hohen min_trades Threshold für robuste Strategien...\n")
    
    data = generate_sample_data(n_bars=1000, start_price=30000)  # Mehr Daten
    
    selector = StrategySelector(
        initial_capital=10000.0,
        trade_size=100.0,
        min_trades=20  # Hoher Threshold
    )
    
    try:
        print("Führe Auswahl mit min_trades=20 durch...")
        best_name, best_score = selector.run_selection(data)
        
        print(f"\n🏆 ERGEBNIS (Robust):")
        print(f"   Beste Strategie: {best_name}")
        print(f"   Total Trades: {best_score.total_trades} (≥ 20)")
        print(f"   Score: {best_score.score:.2f}/100")
        
    except ValueError as e:
        print(f"\n⚠️  {e}")
        print("   → Keine Strategie erfüllte die Mindestanforderungen")
        print("   → Reduziere min_trades oder erhöhe Datenmenge")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  🎯 DEMO: AUTOMATISCHE STRATEGIE-AUSWAHL")
    print("=" * 70)
    print("\nDiese Demo zeigt verschiedene Modi der automatischen Strategie-Auswahl:")
    print("  1. Grundlegende Verwendung")
    print("  2. Konservative Gewichtung")
    print("  3. Großes Kapital")
    print("  4. Ranking Export")
    print("  5. Robustheit-Filter")
    print("\n" + "=" * 70)
    
    try:
        # Demo 1
        demo_basic_usage()
        input("\n[Drücke Enter für nächste Demo...]")
        
        # Demo 2
        demo_custom_weights()
        input("\n[Drücke Enter für nächste Demo...]")
        
        # Demo 3
        demo_high_capital()
        input("\n[Drücke Enter für nächste Demo...]")
        
        # Demo 4
        demo_export_and_compare()
        input("\n[Drücke Enter für nächste Demo...]")
        
        # Demo 5
        demo_robustness_filter()
        
        # Summary
        print_section("DEMO ABGESCHLOSSEN")
        print("✅ Alle Demos erfolgreich durchgeführt!")
        print("\n📚 Weitere Informationen:")
        print("   - AUTO_STRATEGY_SELECTION_GUIDE.md")
        print("   - STRATEGY_SELECTION_GUIDE.md")
        print("   - python scripts/auto_select_strategy.py --help")
        print("\n" + "=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo abgebrochen")
        return 1
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
