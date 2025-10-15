"""
demo_advanced_circuit_breaker.py - Demo für erweiterte Circuit Breaker Logik
============================================================================
Zeigt die erweiterten Features des Circuit Breaker Systems:
- Multiple konfigurierbare Schwellenwerte
- Flexible Actions pro Schwellenwert
- Integration mit Alert-System
- Automatische Eskalation
"""
import logging
import sys
from typing import Dict, Any
from circuit_breaker import (
    CircuitBreakerManager,
    CircuitBreakerActions
)

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Helper zum Ausgeben von Abschnitten"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_basic_configuration():
    """Demo 1: Basis-Konfiguration mit mehreren Schwellenwerten"""
    print_section("Demo 1: Basis-Konfiguration mit mehreren Schwellenwerten")
    
    manager = CircuitBreakerManager()
    
    # Konfiguriere 3 Schwellenwerte
    print("Konfiguriere Circuit Breaker mit 3 Schwellenwerten:\n")
    
    manager.add_threshold(
        level=10.0,
        actions=[
            CircuitBreakerActions.create_log_action(
                "⚠️ WARNING: 10% Drawdown erreicht!",
                level="warning"
            )
        ],
        description="Warning Level"
    )
    print("  ✓ 10% Threshold: Warning + Log")
    
    manager.add_threshold(
        level=15.0,
        actions=[
            CircuitBreakerActions.create_log_action(
                "🔶 ALERT: 15% Drawdown - Erhöhte Aufmerksamkeit!",
                level="error"
            )
        ],
        description="Alert Level"
    )
    print("  ✓ 15% Threshold: Alert + Log")
    
    manager.add_threshold(
        level=20.0,
        actions=[
            CircuitBreakerActions.create_log_action(
                "🚨 CRITICAL: 20% Drawdown - Trading stoppen!",
                level="critical"
            )
        ],
        description="Critical Level"
    )
    print("  ✓ 20% Threshold: Critical + Trading Stop")
    
    # Zeige Status
    print("\nCircuit Breaker Status:")
    status = manager.get_status()
    print(f"  Enabled: {status['enabled']}")
    print(f"  Schwellenwerte konfiguriert: {len(status['thresholds'])}")
    for i, threshold in enumerate(status['thresholds'], 1):
        print(f"    {i}. {threshold['level']}% - {threshold['description']} ({threshold['num_actions']} Actions)")


def demo_progressive_escalation():
    """Demo 2: Progressive Eskalation bei steigendem Drawdown"""
    print_section("Demo 2: Progressive Eskalation bei steigendem Drawdown")
    
    manager = CircuitBreakerManager()
    actions_log = []
    
    # Konfiguriere mit Actions die wir tracken können
    manager.add_threshold(
        level=10.0,
        actions=[lambda: actions_log.append('10% - Warning')],
        description="Warning Level"
    )
    
    manager.add_threshold(
        level=15.0,
        actions=[lambda: actions_log.append('15% - Alert')],
        description="Alert Level"
    )
    
    manager.add_threshold(
        level=20.0,
        actions=[lambda: actions_log.append('20% - Critical')],
        description="Critical Level"
    )
    
    # Simuliere Trading mit progressivem Drawdown
    print("Simuliere Trading mit steigendem Drawdown:\n")
    equity_values = [10000, 10200, 9500, 9000, 8500, 8000]
    
    for i, equity in enumerate(equity_values):
        print(f"Iteration {i+1}: Equity = ${equity:,.2f}")
        triggered = manager.check(equity, is_dry_run=False)
        
        if triggered:
            drawdown = manager.calculate_current_drawdown()
            print(f"  → 🚨 Schwellenwert überschritten!")
            print(f"  → Drawdown: {drawdown:.2f}%")
            print(f"  → Action: {actions_log[-1]}")
        else:
            drawdown = manager.calculate_current_drawdown()
            print(f"  → Drawdown: {drawdown:.2f}%")
    
    # Zusammenfassung
    print(f"\n📊 Zusammenfassung:")
    print(f"  Ausgelöste Actions: {len(actions_log)}")
    for i, action in enumerate(actions_log, 1):
        print(f"    {i}. {action}")
    
    status = manager.get_status()
    print(f"\n  Final Drawdown: {status['current_drawdown']:.2f}%")
    print(f"  Höchster Level: {status['triggered_level']}%")


def demo_custom_actions():
    """Demo 3: Custom Actions und Rebalancing"""
    print_section("Demo 3: Custom Actions und Rebalancing")
    
    manager = CircuitBreakerManager()
    
    # Tracking für Actions
    action_history = []
    
    # Mock Portfolio Manager
    class MockPortfolioManager:
        def __init__(self):
            self.rebalanced = False
        
        def rebalance(self):
            self.rebalanced = True
            action_history.append("Portfolio rebalanced")
            logger.info("📊 Portfolio wurde rebalanciert")
    
    # Mock Trading Bot
    class MockBot:
        def __init__(self):
            self.paused = False
            self.circuit_breaker_triggered = False
        
        def pause(self):
            self.paused = True
            action_history.append("Trading paused")
            logger.info("⏸️ Trading wurde pausiert")
    
    portfolio = MockPortfolioManager()
    bot = MockBot()
    
    # Konfiguriere erweiterte Actions
    print("Konfiguriere Circuit Breaker mit Custom Actions:\n")
    
    manager.add_threshold(
        level=10.0,
        actions=[
            CircuitBreakerActions.create_log_action(
                "10% Drawdown - Warnung",
                level="warning"
            ),
            CircuitBreakerActions.create_custom_action(
                lambda: action_history.append("Risk assessment triggered"),
                description="Risk Assessment"
            )
        ],
        description="Warning + Risk Assessment"
    )
    print("  ✓ 10%: Warning + Risk Assessment")
    
    manager.add_threshold(
        level=15.0,
        actions=[
            CircuitBreakerActions.create_pause_trading_action(bot),
            CircuitBreakerActions.create_log_action(
                "15% Drawdown - Trading pausiert",
                level="error"
            )
        ],
        description="Pause Trading"
    )
    print("  ✓ 15%: Pause Trading")
    
    manager.add_threshold(
        level=20.0,
        actions=[
            CircuitBreakerActions.create_rebalance_action(portfolio),
            CircuitBreakerActions.create_shutdown_action(bot),
            CircuitBreakerActions.create_log_action(
                "20% Drawdown - Emergency Rebalance + Shutdown",
                level="critical"
            )
        ],
        description="Emergency: Rebalance + Shutdown"
    )
    print("  ✓ 20%: Rebalance + Shutdown")
    
    # Simuliere Drawdown
    print("\nSimuliere Drawdown:\n")
    manager.check(10000, is_dry_run=False)
    manager.check(8500, is_dry_run=False)  # -15%
    manager.check(7800, is_dry_run=False)  # -22%
    
    # Ergebnisse
    print("\n📋 Ausgeführte Actions:")
    for i, action in enumerate(action_history, 1):
        print(f"  {i}. {action}")
    
    print("\n📊 Status:")
    print(f"  Trading pausiert: {bot.paused}")
    print(f"  Portfolio rebalanciert: {portfolio.rebalanced}")
    print(f"  Circuit Breaker aktiv: {bot.circuit_breaker_triggered}")


def demo_configuration_from_dict():
    """Demo 4: Konfiguration aus Dictionary (wie in config.py)"""
    print_section("Demo 4: Konfiguration aus Dictionary")
    
    manager = CircuitBreakerManager()
    
    # Konfiguration wie in config.py
    config_dict = {
        10.0: {
            'actions': [
                CircuitBreakerActions.create_log_action("10% Warning", "warning")
            ],
            'description': 'Warning Level'
        },
        15.0: {
            'actions': [
                CircuitBreakerActions.create_log_action("15% Alert", "error")
            ],
            'description': 'Alert Level'
        },
        20.0: {
            'actions': [
                CircuitBreakerActions.create_log_action("20% Critical", "critical")
            ],
            'description': 'Critical Level'
        }
    }
    
    print("Konfiguriere aus Dictionary:\n")
    print("config = {")
    for level, settings in config_dict.items():
        print(f"    {level}%: {settings['description']}")
    print("}\n")
    
    manager.configure_from_dict(config_dict)
    
    print("✓ Konfiguration erfolgreich geladen\n")
    
    status = manager.get_status()
    print(f"Schwellenwerte: {len(status['thresholds'])}")
    for threshold in status['thresholds']:
        print(f"  - {threshold['level']}%: {threshold['description']}")


def demo_status_and_reset():
    """Demo 5: Status-Abfrage und Reset"""
    print_section("Demo 5: Status-Abfrage und Reset")
    
    manager = CircuitBreakerManager()
    
    # Konfiguriere
    manager.add_threshold(
        level=10.0,
        actions=[CircuitBreakerActions.create_log_action("10%", "warning")],
        description="Warning"
    )
    
    # Simuliere Trigger
    print("Initial Status:")
    status = manager.get_status()
    print(f"  Triggered: {status['triggered']}")
    print(f"  Triggered Level: {status['triggered_level']}")
    
    print("\nSimuliere Drawdown...")
    manager.check(10000, is_dry_run=False)
    manager.check(8500, is_dry_run=False)
    
    print("\nStatus nach Trigger:")
    status = manager.get_status()
    print(f"  Triggered: {status['triggered']}")
    print(f"  Triggered Level: {status['triggered_level']}%")
    print(f"  Current Drawdown: {status['current_drawdown']:.2f}%")
    
    print("\nReset Circuit Breaker...")
    manager.reset()
    
    print("\nStatus nach Reset:")
    status = manager.get_status()
    print(f"  Triggered: {status['triggered']}")
    print(f"  Triggered Level: {status['triggered_level']}")
    
    # Equity curve reset
    print("\nReset Equity Curve...")
    print(f"  Vorher: {len(manager.equity_curve)} Datenpunkte")
    manager.reset_equity_curve()
    print(f"  Nachher: {len(manager.equity_curve)} Datenpunkte")


def main():
    """Hauptfunktion - Führe alle Demos aus"""
    print("\n" + "=" * 70)
    print("  🚨 ERWEITERTE CIRCUIT BREAKER LOGIK - DEMO")
    print("=" * 70)
    print("\nDieses Demo zeigt die erweiterten Features des Circuit Breaker Systems:")
    print("  • Multiple konfigurierbare Schwellenwerte")
    print("  • Flexible Actions pro Schwellenwert")
    print("  • Progressive Eskalation")
    print("  • Custom Actions und Rebalancing")
    print("  • Dictionary-basierte Konfiguration")
    print("  • Status-Management und Reset")
    
    try:
        # Demo 1
        demo_basic_configuration()
        input("\nDrücke Enter für nächste Demo...")
        
        # Demo 2
        demo_progressive_escalation()
        input("\nDrücke Enter für nächste Demo...")
        
        # Demo 3
        demo_custom_actions()
        input("\nDrücke Enter für nächste Demo...")
        
        # Demo 4
        demo_configuration_from_dict()
        input("\nDrücke Enter für nächste Demo...")
        
        # Demo 5
        demo_status_and_reset()
        
        print_section("✓ ALLE DEMOS ERFOLGREICH ABGESCHLOSSEN")
        
        print("\n📚 Weitere Informationen:")
        print("  • Siehe circuit_breaker.py für API-Dokumentation")
        print("  • Siehe test_circuit_breaker_advanced.py für Tests")
        print("  • Siehe config.py für Konfigurationsbeispiele")
        print("  • Siehe CIRCUIT_BREAKER_GUIDE.md für vollständige Dokumentation")
        
    except KeyboardInterrupt:
        print("\n\n❌ Demo durch Benutzer abgebrochen")
        sys.exit(0)


if __name__ == "__main__":
    main()
