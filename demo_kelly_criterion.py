"""
demo_kelly_criterion.py - Demonstration des Kelly Criterion Position Sizing
===========================================================================
Zeigt verschiedene Anwendungsfälle des Kelly Criterion für Position Sizing
"""

import logging
from utils import (
    calculate_kelly_criterion,
    calculate_kelly_position_size,
    setup_logging
)
from config import TradingConfig

# Setup logging
logger = setup_logging(log_level="INFO")


def demo_basic_kelly():
    """Demonstriere Basic Kelly Criterion Berechnung"""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Kelly Criterion")
    print("=" * 70)
    
    # Szenario: 60% Gewinnrate, durchschnittlicher Gewinn $150, durchschnittlicher Verlust $100
    win_rate = 0.6
    avg_win = 150.0
    avg_loss = 100.0
    
    print(f"\n📊 Trading-Statistiken:")
    print(f"   Gewinnrate: {win_rate*100:.1f}%")
    print(f"   Durchschnittlicher Gewinn: ${avg_win:.2f}")
    print(f"   Durchschnittlicher Verlust: ${avg_loss:.2f}")
    print(f"   Win/Loss Ratio: {avg_win/avg_loss:.2f}")
    
    # Full Kelly
    full_kelly = calculate_kelly_criterion(win_rate, avg_win, avg_loss, kelly_fraction=1.0)
    print(f"\n💯 Full Kelly empfiehlt: {full_kelly*100:.2f}% des Kapitals")
    
    # Half Kelly (konservativer)
    half_kelly = calculate_kelly_criterion(win_rate, avg_win, avg_loss, kelly_fraction=0.5)
    print(f"🔰 Half Kelly empfiehlt: {half_kelly*100:.2f}% des Kapitals (konservativer)")
    
    # Quarter Kelly (sehr konservativ)
    quarter_kelly = calculate_kelly_criterion(win_rate, avg_win, avg_loss, kelly_fraction=0.25)
    print(f"🛡️ Quarter Kelly empfiehlt: {quarter_kelly*100:.2f}% des Kapitals (sehr konservativ)")


def demo_position_sizing():
    """Demonstriere konkrete Positionsgrößenberechnung"""
    print("\n" + "=" * 70)
    print("DEMO 2: Position Sizing mit Kelly Criterion")
    print("=" * 70)
    
    capital = 10000.0
    win_rate = 0.6
    avg_win = 150.0
    avg_loss = 100.0
    
    print(f"\n💰 Verfügbares Kapital: ${capital:,.2f}")
    print(f"\n📊 Trading-Statistiken:")
    print(f"   Gewinnrate: {win_rate*100:.1f}%")
    print(f"   Avg Win: ${avg_win:.2f}")
    print(f"   Avg Loss: ${avg_loss:.2f}")
    
    # Half Kelly mit 25% Maximum
    position = calculate_kelly_position_size(
        capital=capital,
        win_rate=win_rate,
        avg_win=avg_win,
        avg_loss=avg_loss,
        kelly_fraction=0.5,
        max_position_pct=0.25
    )
    
    print(f"\n📏 Empfohlene Positionsgröße:")
    print(f"   ${position:,.2f} ({position/capital*100:.2f}% des Kapitals)")
    
    # Bei BTC-Preis von $50,000
    btc_price = 50000
    btc_quantity = position / btc_price
    print(f"\n₿ Bei BTC @ ${btc_price:,}:")
    print(f"   {btc_quantity:.6f} BTC")


def demo_scenarios():
    """Demonstriere verschiedene Trading-Szenarien"""
    print("\n" + "=" * 70)
    print("DEMO 3: Verschiedene Trading-Szenarien")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "Konservative Strategie",
            "win_rate": 0.55,
            "avg_win": 120,
            "avg_loss": 100,
            "description": "Hohe Gewinnrate, kleines Win/Loss Ratio"
        },
        {
            "name": "Aggressive Strategie",
            "win_rate": 0.40,
            "avg_win": 300,
            "avg_loss": 100,
            "description": "Niedrige Gewinnrate, großes Win/Loss Ratio"
        },
        {
            "name": "Breakeven Strategie",
            "win_rate": 0.50,
            "avg_win": 100,
            "avg_loss": 100,
            "description": "Weder Gewinn noch Verlust langfristig"
        },
        {
            "name": "Verlust-Strategie",
            "win_rate": 0.40,
            "avg_win": 100,
            "avg_loss": 120,
            "description": "Negativer Edge - nicht traden!"
        }
    ]
    
    capital = 10000.0
    
    for scenario in scenarios:
        print(f"\n{'─' * 70}")
        print(f"📋 {scenario['name']}")
        print(f"   {scenario['description']}")
        print(f"\n   Win Rate: {scenario['win_rate']*100:.1f}%")
        print(f"   Avg Win: ${scenario['avg_win']:.2f}")
        print(f"   Avg Loss: ${scenario['avg_loss']:.2f}")
        print(f"   Win/Loss Ratio: {scenario['avg_win']/scenario['avg_loss']:.2f}")
        
        kelly = calculate_kelly_criterion(
            win_rate=scenario['win_rate'],
            avg_win=scenario['avg_win'],
            avg_loss=scenario['avg_loss'],
            kelly_fraction=0.5
        )
        
        if kelly > 0:
            position = kelly * capital
            print(f"\n   ✅ Half Kelly: {kelly*100:.2f}%")
            print(f"   💵 Position Size: ${position:,.2f}")
        else:
            print(f"\n   ❌ Kelly: {kelly*100:.2f}% (Kein Trade empfohlen!)")


def demo_config_integration():
    """Demonstriere Integration mit TradingConfig"""
    print("\n" + "=" * 70)
    print("DEMO 4: Integration mit TradingConfig")
    print("=" * 70)
    
    # Lade Standard-Config
    config = TradingConfig()
    
    print(f"\n⚙️ Aktuelle Konfiguration:")
    print(f"   Kelly Criterion aktiviert: {config.enable_kelly_criterion}")
    print(f"   Kelly Fraction: {config.kelly_fraction} ({'Half Kelly' if config.kelly_fraction == 0.5 else 'Full Kelly' if config.kelly_fraction == 1.0 else 'Custom'})")
    print(f"   Max Position: {config.kelly_max_position_pct*100:.0f}%")
    print(f"   Lookback Trades: {config.kelly_lookback_trades}")
    
    # Aktiviere Kelly
    print(f"\n🔧 Aktiviere Kelly Criterion...")
    config.enable_kelly_criterion = True
    
    # Validiere
    is_valid, error = config.validate()
    if is_valid:
        print(f"   ✅ Konfiguration ist valid")
    else:
        print(f"   ❌ Fehler: {error}")
    
    print(f"\n💡 Empfehlung:")
    print(f"   - Starte mit Half Kelly (kelly_fraction=0.5)")
    print(f"   - Begrenze Position auf 25% (kelly_max_position_pct=0.25)")
    print(f"   - Nutze mindestens 20 vergangene Trades (kelly_lookback_trades=20)")
    print(f"   - Teste im DRY_RUN Modus bevor du live gehst!")


def demo_calculation_example():
    """Demonstriere Schritt-für-Schritt Kelly Berechnung"""
    print("\n" + "=" * 70)
    print("DEMO 5: Schritt-für-Schritt Kelly Berechnung")
    print("=" * 70)
    
    print("\n📝 Kelly-Formel: f* = (p * b - q) / b")
    print("   wobei:")
    print("   - p = Gewinnwahrscheinlichkeit (win_rate)")
    print("   - q = Verlustwahrscheinlichkeit (1 - win_rate)")
    print("   - b = Win/Loss Ratio (avg_win / avg_loss)")
    print("   - f* = Optimaler Kapitalanteil für Trade")
    
    # Beispiel
    win_rate = 0.6
    avg_win = 150.0
    avg_loss = 100.0
    
    print(f"\n📊 Beispiel:")
    print(f"   p = {win_rate} (60% Gewinnrate)")
    print(f"   q = {1-win_rate} (40% Verlustrate)")
    print(f"   b = {avg_win}/{avg_loss} = {avg_win/avg_loss:.2f}")
    
    # Berechnung
    win_loss_ratio = avg_win / avg_loss
    loss_rate = 1 - win_rate
    kelly = (win_rate * win_loss_ratio - loss_rate) / win_loss_ratio
    
    print(f"\n🧮 Berechnung:")
    print(f"   f* = ({win_rate} * {win_loss_ratio:.2f} - {loss_rate}) / {win_loss_ratio:.2f}")
    print(f"   f* = ({win_rate * win_loss_ratio:.2f} - {loss_rate}) / {win_loss_ratio:.2f}")
    print(f"   f* = {win_rate * win_loss_ratio - loss_rate:.2f} / {win_loss_ratio:.2f}")
    print(f"   f* = {kelly:.4f} = {kelly*100:.2f}%")
    
    print(f"\n💡 Interpretation:")
    print(f"   Full Kelly empfiehlt {kelly*100:.2f}% des Kapitals pro Trade")
    print(f"   Half Kelly (konservativer): {kelly*50:.2f}%")
    print(f"   Bei $10,000 Kapital: ${10000*kelly:.2f} (Full) oder ${10000*kelly*0.5:.2f} (Half)")


def main():
    """Hauptfunktion"""
    print("=" * 70)
    print("KELLY CRITERION POSITION SIZING - DEMONSTRATION")
    print("=" * 70)
    print("\nDas Kelly Criterion hilft, die optimale Positionsgröße zu berechnen")
    print("basierend auf historischer Performance und Win/Loss Ratio.")
    print("\n⚠️ WICHTIG:")
    print("   - Kelly ist aggressiv - nutze Half Kelly (0.5) für mehr Sicherheit")
    print("   - Benötigt mindestens 20 Trades für verlässliche Statistiken")
    print("   - Teste immer im DRY_RUN Modus!")
    
    # Run demos
    demo_basic_kelly()
    demo_position_sizing()
    demo_scenarios()
    demo_calculation_example()
    demo_config_integration()
    
    print("\n" + "=" * 70)
    print("✓ Demo abgeschlossen!")
    print("=" * 70)
    print("\n📚 Weitere Informationen:")
    print("   - Wikipedia: Kelly Criterion")
    print("   - Teste mit test_kelly_criterion.py")
    print("   - Siehe config.py für Konfigurationsoptionen")
    print("   - Siehe lsob_strategy.py für Beispiel-Integration")


if __name__ == "__main__":
    main()
