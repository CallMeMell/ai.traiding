"""
demo_circuit_breaker.py - Circuit Breaker Demo
==============================================
Demonstrates how the Circuit Breaker (Drawdown-Limit) works
in live trading scenarios.
"""

import os
import sys
from utils import calculate_current_drawdown, calculate_max_drawdown

def demo_basic_drawdown():
    """Demo: Grundlegende Drawdown-Berechnung"""
    print("=" * 70)
    print("📊 Demo 1: Grundlegende Drawdown-Berechnung")
    print("=" * 70)
    
    equity_curve = [10000, 10500, 11000, 9500, 9000, 10000]
    
    print(f"\nEquity Curve: {equity_curve}")
    print(f"Initial Capital: ${equity_curve[0]:,.2f}")
    print(f"Peak Value: ${max(equity_curve):,.2f}")
    print(f"Current Value: ${equity_curve[-1]:,.2f}")
    
    # Calculate current drawdown
    current_dd = calculate_current_drawdown(equity_curve)
    print(f"\nCurrent Drawdown: {current_dd:.2f}%")
    
    # Calculate maximum drawdown
    max_dd_pct, max_dd_val, peak_val, trough_val = calculate_max_drawdown(equity_curve)
    print(f"Maximum Drawdown: {max_dd_pct:.2f}%")
    print(f"  Peak: ${peak_val:,.2f}")
    print(f"  Trough: ${trough_val:,.2f}")
    print(f"  Loss: ${max_dd_val:,.2f}")


def demo_circuit_breaker_trigger():
    """Demo: Circuit Breaker Auslösung"""
    print("\n" + "=" * 70)
    print("🚨 Demo 2: Circuit Breaker Auslösung")
    print("=" * 70)
    
    initial_capital = 10000
    drawdown_limit = 0.20  # 20%
    
    print(f"\nStartkapital: ${initial_capital:,.2f}")
    print(f"Drawdown-Limit: {drawdown_limit * 100:.0f}%")
    print(f"Trigger bei Kapital < ${initial_capital * (1 - drawdown_limit):,.2f}")
    
    # Simulate trading with losses
    equity_values = [
        (10000, "Start"),
        (10500, "Nach gutem Trade (+5%)"),
        (10200, "Nach kleinem Verlust (-2.9%)"),
        (9500, "Nach größerem Verlust (-9.5% vom Peak)"),
        (8500, "Nach weiterem Verlust (-19.0% vom Peak)"),
        (7900, "Circuit Breaker! (-24.8% vom Peak)")
    ]
    
    equity_curve = []
    
    print("\n" + "-" * 70)
    print("Equity Progression:")
    print("-" * 70)
    
    for equity, description in equity_values:
        equity_curve.append(equity)
        current_dd = calculate_current_drawdown(equity_curve)
        
        status = "✅ OK"
        if current_dd < -drawdown_limit * 100:
            status = "🚨 CIRCUIT BREAKER AUSGELÖST!"
        
        print(f"${equity:>8,.2f} | DD: {current_dd:>7.2f}% | {status} | {description}")
        
        if current_dd < -drawdown_limit * 100:
            print("\n⚠️ Trading wurde gestoppt!")
            print(f"Verlust: ${equity_curve[0] - equity:,.2f}")
            print(f"Verbleibend: {(equity / equity_curve[0]) * 100:.1f}% des Startkapitals")
            break


def demo_dry_run_vs_production():
    """Demo: DRY_RUN vs Production Mode"""
    print("\n" + "=" * 70)
    print("⚙️  Demo 3: DRY_RUN vs Production Mode")
    print("=" * 70)
    
    print("\n📝 DRY_RUN Mode (Standard):")
    print("  - Circuit Breaker ist INAKTIV")
    print("  - Kein automatischer Stop bei Verlusten")
    print("  - Nur für Testing und Simulation")
    print("  - Gesetzt via: DRY_RUN=true (default)")
    
    print("\n💰 Production Mode:")
    print("  - Circuit Breaker ist AKTIV")
    print("  - Automatischer Stop bei Drawdown-Limit")
    print("  - Für echtes Trading mit echtem Geld")
    print("  - Gesetzt via: DRY_RUN=false")
    
    print("\n⚠️  WICHTIG:")
    print("  Circuit Breaker schützt nur in Production Mode!")
    print("  Immer zuerst im DRY_RUN Mode testen!")


def demo_recommended_limits():
    """Demo: Empfohlene Drawdown-Limits"""
    print("\n" + "=" * 70)
    print("📋 Demo 4: Empfohlene Drawdown-Limits")
    print("=" * 70)
    
    initial_capital = 10000
    
    limits = [
        (0.10, "Konservativ", "Für Anfänger und geringe Risikotoleranz"),
        (0.20, "Moderat (Standard)", "Ausgewogenes Risk/Reward Verhältnis"),
        (0.30, "Aggressiv", "Für erfahrene Trader mit hoher Risikotoleranz"),
    ]
    
    print(f"\nStartkapital: ${initial_capital:,.2f}")
    print("\n" + "-" * 70)
    print(f"{'Limit':<10} | {'Trigger bei':<15} | {'Verbleibend':<15} | Beschreibung")
    print("-" * 70)
    
    for limit, name, description in limits:
        trigger_value = initial_capital * (1 - limit)
        remaining = trigger_value
        
        print(f"{limit * 100:>3.0f}% {name:<20} | ${trigger_value:>8,.2f} | ${remaining:>8,.2f} | {description}")


def main():
    """Main demo function"""
    print("\n🚨 CIRCUIT BREAKER (DRAWDOWN-LIMIT) DEMO")
    print("=" * 70)
    print("Zeigt wie der automatische Circuit Breaker funktioniert")
    print("=" * 70)
    
    # Run demos
    demo_basic_drawdown()
    demo_circuit_breaker_trigger()
    demo_dry_run_vs_production()
    demo_recommended_limits()
    
    print("\n" + "=" * 70)
    print("✅ Demo abgeschlossen!")
    print("=" * 70)
    print("\n📚 Weitere Informationen:")
    print("  - README.md: Risk Management Sektion")
    print("  - LIVE_TRADING_SETUP_GUIDE.md: Circuit Breaker Sektion")
    print("  - test_circuit_breaker.py: Unit Tests")
    print("\n💡 Tipp: Starte mit einem konservativen Limit (10-20%)")
    print("         und teste ausführlich im DRY_RUN Mode!\n")


if __name__ == '__main__':
    main()
