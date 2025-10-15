"""
circuit_breaker.py - Erweiterte Circuit Breaker Logik
======================================================
Flexible, konfigurierbare Circuit Breaker Implementation mit 
dynamischen Schwellenwerten und Actions.
"""
import logging
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CircuitBreakerThreshold:
    """
    Einzelner Circuit Breaker Schwellenwert mit zugehörigen Actions
    """
    level: float  # Drawdown-Schwellenwert in Prozent (z.B. 10.0 für 10%)
    actions: List[Callable[[], None]] = field(default_factory=list)
    triggered: bool = False
    description: str = ""


class CircuitBreakerManager:
    """
    Erweiterte Circuit Breaker Manager
    
    Features:
    - Dynamische, konfigurierbare Schwellenwerte
    - Flexible Actions pro Schwellenwert
    - Automatische Eskalation bei steigendem Drawdown
    - Integration mit Alert-System
    - Fehlerrobuste Implementierung
    
    Example:
        >>> manager = CircuitBreakerManager()
        >>> manager.add_threshold(
        ...     level=10.0,
        ...     actions=[lambda: send_alert("10% Drawdown!")],
        ...     description="Warning Level"
        ... )
        >>> manager.add_threshold(
        ...     level=20.0,
        ...     actions=[lambda: shutdown_trading()],
        ...     description="Critical Level"
        ... )
        >>> triggered = manager.check(equity_curve, is_dry_run=False)
    """
    
    def __init__(
        self,
        enabled: bool = True,
        only_production: bool = True
    ):
        """
        Initialisiere Circuit Breaker Manager
        
        Args:
            enabled: Circuit Breaker aktivieren
            only_production: Nur in Production-Modus aktiv (nicht DRY_RUN)
        """
        self.enabled = enabled
        self.only_production = only_production
        self.thresholds: List[CircuitBreakerThreshold] = []
        self.equity_curve: List[float] = []
        self.triggered = False
        self.triggered_level: Optional[float] = None
        
        logger.info("✓ Circuit Breaker Manager initialisiert")
    
    def add_threshold(
        self,
        level: float,
        actions: List[Callable[[], None]],
        description: str = ""
    ) -> None:
        """
        Füge Schwellenwert mit Actions hinzu
        
        Args:
            level: Drawdown-Schwellenwert in Prozent (z.B. 10.0 für 10%)
            actions: Liste von Actions (Callbacks) die ausgeführt werden
            description: Beschreibung des Schwellenwerts
        """
        if level <= 0:
            raise ValueError("Schwellenwert muss positiv sein")
        
        threshold = CircuitBreakerThreshold(
            level=level,
            actions=actions,
            description=description
        )
        
        self.thresholds.append(threshold)
        
        # Sortiere Schwellenwerte aufsteigend
        self.thresholds.sort(key=lambda t: t.level)
        
        logger.info(f"Circuit Breaker Schwellenwert hinzugefügt: {level}% - {description}")
    
    def configure_from_dict(self, config: Dict[float, Dict[str, Any]]) -> None:
        """
        Konfiguriere Circuit Breaker aus Dictionary
        
        Args:
            config: Dictionary mit Schwellenwerten und Actions
                   Format: {
                       10.0: {
                           'actions': [action1, action2],
                           'description': 'Warning Level'
                       },
                       20.0: {...}
                   }
        """
        for level, settings in config.items():
            actions = settings.get('actions', [])
            description = settings.get('description', '')
            self.add_threshold(level, actions, description)
    
    def update_equity(self, current_equity: float) -> None:
        """
        Update Equity Curve
        
        Args:
            current_equity: Aktueller Kapitalwert
        """
        self.equity_curve.append(current_equity)
    
    def calculate_current_drawdown(self) -> float:
        """
        Berechne aktuellen Drawdown
        
        Returns:
            Drawdown in Prozent (negative Zahl)
        """
        if len(self.equity_curve) < 2:
            return 0.0
        
        equity_array = np.array(self.equity_curve)
        peak_value = np.max(equity_array)
        current_value = equity_array[-1]
        
        if peak_value == 0:
            return 0.0
        
        drawdown_pct = ((current_value - peak_value) / peak_value) * 100
        return drawdown_pct
    
    def check(
        self,
        current_equity: Optional[float] = None,
        is_dry_run: bool = False
    ) -> bool:
        """
        Prüfe Circuit Breaker und führe Actions aus
        
        Args:
            current_equity: Aktuelles Kapital (optional, wenn bereits via update_equity aktualisiert)
            is_dry_run: Ist DRY_RUN Mode aktiv?
            
        Returns:
            True wenn ein Schwellenwert überschritten wurde
        """
        # Circuit Breaker deaktiviert
        if not self.enabled:
            return False
        
        # Circuit Breaker nur in Production-Modus
        if self.only_production and is_dry_run:
            return False
        
        # Keine Schwellenwerte konfiguriert
        if not self.thresholds:
            logger.warning("Keine Circuit Breaker Schwellenwerte konfiguriert")
            return False
        
        # Update equity curve falls Wert übergeben
        if current_equity is not None:
            self.update_equity(current_equity)
        
        # Berechne Drawdown
        current_drawdown = self.calculate_current_drawdown()
        
        # Prüfe jeden Schwellenwert
        any_triggered = False
        for threshold in self.thresholds:
            # Schwellenwert überschritten?
            if current_drawdown < -threshold.level and not threshold.triggered:
                any_triggered = True
                threshold.triggered = True
                self.triggered = True
                self.triggered_level = threshold.level
                
                logger.critical("=" * 70)
                logger.critical(f"🚨 CIRCUIT BREAKER THRESHOLD AUSGELÖST: {threshold.level}% 🚨")
                logger.critical("=" * 70)
                logger.critical(f"Beschreibung: {threshold.description}")
                logger.critical(f"Aktueller Drawdown: {current_drawdown:.2f}%")
                logger.critical(f"Schwellenwert: {threshold.level}%")
                logger.critical(f"Peak Value: ${np.max(self.equity_curve):,.2f}")
                logger.critical(f"Current Value: ${self.equity_curve[-1]:,.2f}")
                logger.critical(f"Verlust: ${self.equity_curve[-1] - np.max(self.equity_curve):,.2f}")
                logger.critical("=" * 70)
                
                # Führe Actions aus
                logger.info(f"Führe {len(threshold.actions)} Action(s) aus...")
                for i, action in enumerate(threshold.actions):
                    try:
                        logger.info(f"Action {i+1}/{len(threshold.actions)}: Ausführung...")
                        action()
                        logger.info(f"Action {i+1}/{len(threshold.actions)}: ✓ Erfolgreich")
                    except Exception as e:
                        logger.error(f"Action {i+1}/{len(threshold.actions)}: ✗ Fehler: {e}")
        
        return any_triggered
    
    def get_status(self) -> Dict[str, Any]:
        """
        Hole Circuit Breaker Status
        
        Returns:
            Status-Dictionary mit allen Informationen
        """
        return {
            'enabled': self.enabled,
            'only_production': self.only_production,
            'triggered': self.triggered,
            'triggered_level': self.triggered_level,
            'current_drawdown': self.calculate_current_drawdown() if self.equity_curve else 0.0,
            'thresholds': [
                {
                    'level': t.level,
                    'description': t.description,
                    'triggered': t.triggered,
                    'num_actions': len(t.actions)
                }
                for t in self.thresholds
            ],
            'equity_curve_length': len(self.equity_curve)
        }
    
    def reset(self) -> None:
        """
        Setze Circuit Breaker zurück
        """
        self.triggered = False
        self.triggered_level = None
        for threshold in self.thresholds:
            threshold.triggered = False
        
        logger.info("Circuit Breaker zurückgesetzt")
    
    def reset_equity_curve(self) -> None:
        """
        Setze Equity Curve zurück (z.B. für neue Trading-Session)
        """
        self.equity_curve = []
        logger.info("Equity Curve zurückgesetzt")


# Vordefinierte Action Factories
class CircuitBreakerActions:
    """
    Factory für häufig verwendete Circuit Breaker Actions
    """
    
    @staticmethod
    def create_log_action(message: str, level: str = "critical") -> Callable[[], None]:
        """
        Erstelle Log-Action
        
        Args:
            message: Log-Nachricht
            level: Log-Level (info, warning, error, critical)
            
        Returns:
            Action Callable
        """
        def log_action():
            log_func = getattr(logger, level, logger.info)
            log_func(message)
        
        return log_action
    
    @staticmethod
    def create_alert_action(
        alert_manager,
        drawdown: float,
        limit: float,
        capital: float,
        initial_capital: float
    ) -> Callable[[], None]:
        """
        Erstelle Alert-Action
        
        Args:
            alert_manager: AlertManager Instanz
            drawdown: Aktueller Drawdown
            limit: Drawdown-Limit
            capital: Aktuelles Kapital
            initial_capital: Start-Kapital
            
        Returns:
            Action Callable
        """
        def alert_action():
            if alert_manager:
                alert_manager.send_circuit_breaker_alert(
                    drawdown=drawdown,
                    limit=limit,
                    capital=capital,
                    initial_capital=initial_capital
                )
        
        return alert_action
    
    @staticmethod
    def create_pause_trading_action(bot) -> Callable[[], None]:
        """
        Erstelle Pause-Trading-Action
        
        Args:
            bot: Trading Bot Instanz mit pause() Methode
            
        Returns:
            Action Callable
        """
        def pause_action():
            if hasattr(bot, 'pause'):
                bot.pause()
                logger.info("Trading pausiert via Circuit Breaker")
            elif hasattr(bot, 'circuit_breaker_triggered'):
                bot.circuit_breaker_triggered = True
                logger.info("Circuit Breaker Flag gesetzt")
        
        return pause_action
    
    @staticmethod
    def create_shutdown_action(bot) -> Callable[[], None]:
        """
        Erstelle Shutdown-Action
        
        Args:
            bot: Trading Bot Instanz mit shutdown() oder stop() Methode
            
        Returns:
            Action Callable
        """
        def shutdown_action():
            if hasattr(bot, 'shutdown'):
                logger.critical("Trading wird heruntergefahren via Circuit Breaker")
                # Setze Flag statt direkten Shutdown
                bot.circuit_breaker_triggered = True
            elif hasattr(bot, 'stop'):
                bot.stop()
        
        return shutdown_action
    
    @staticmethod
    def create_rebalance_action(portfolio_manager=None) -> Callable[[], None]:
        """
        Erstelle Rebalance-Action
        
        Args:
            portfolio_manager: Portfolio Manager Instanz (optional)
            
        Returns:
            Action Callable
        """
        def rebalance_action():
            if portfolio_manager and hasattr(portfolio_manager, 'rebalance'):
                logger.info("Portfolio Rebalancing via Circuit Breaker")
                portfolio_manager.rebalance()
            else:
                logger.info("⚠️ Rebalancing Action - Portfolio Manager nicht verfügbar")
        
        return rebalance_action
    
    @staticmethod
    def create_custom_action(func: Callable[[], None], description: str = "") -> Callable[[], None]:
        """
        Erstelle Custom-Action
        
        Args:
            func: Custom Function
            description: Beschreibung
            
        Returns:
            Action Callable
        """
        def custom_action():
            logger.info(f"Custom Action: {description}")
            func()
        
        return custom_action


# Demo
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("🚨 Circuit Breaker Manager - Demo")
    print("=" * 70)
    
    # Erstelle Circuit Breaker Manager
    cb_manager = CircuitBreakerManager()
    
    # Konfiguriere Schwellenwerte
    print("\n1. Konfiguriere Schwellenwerte:")
    
    cb_manager.add_threshold(
        level=10.0,
        actions=[
            CircuitBreakerActions.create_log_action(
                "⚠️ WARNING: 10% Drawdown erreicht!",
                level="warning"
            )
        ],
        description="Warning Level - Erste Warnung"
    )
    
    cb_manager.add_threshold(
        level=15.0,
        actions=[
            CircuitBreakerActions.create_log_action(
                "🔶 ALERT: 15% Drawdown - Erhöhte Aufmerksamkeit!",
                level="error"
            )
        ],
        description="Alert Level - Erhöhte Warnstufe"
    )
    
    cb_manager.add_threshold(
        level=20.0,
        actions=[
            CircuitBreakerActions.create_log_action(
                "🚨 CRITICAL: 20% Drawdown - Trading stoppen!",
                level="critical"
            )
        ],
        description="Critical Level - Trading wird gestoppt"
    )
    
    # Simuliere Drawdown
    print("\n2. Simuliere Drawdown:")
    equity_values = [10000, 10200, 9500, 9000, 8500, 8000]
    
    for i, equity in enumerate(equity_values):
        print(f"\nIteration {i+1}: Equity = ${equity:,.2f}")
        triggered = cb_manager.check(equity, is_dry_run=False)
        
        if triggered:
            status = cb_manager.get_status()
            print(f"  → Drawdown: {status['current_drawdown']:.2f}%")
            print(f"  → Triggered Level: {status['triggered_level']}%")
    
    # Zeige Status
    print("\n3. Final Status:")
    status = cb_manager.get_status()
    print(f"  Triggered: {status['triggered']}")
    print(f"  Triggered Level: {status['triggered_level']}%")
    print(f"  Current Drawdown: {status['current_drawdown']:.2f}%")
    print(f"  Anzahl Schwellenwerte: {len(status['thresholds'])}")
    
    print("\n" + "=" * 70)
    print("✓ Demo abgeschlossen")
    print("=" * 70)
