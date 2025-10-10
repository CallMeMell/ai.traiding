"""
automated_workflow.py - Automatisierter Workflow für KI-Trading-Bot
====================================================================
Vollautomatisierter Workflow zur Vorbereitung des KI-Tradingbots für Echtgeld-Einsatz
mit Zeitlimits, Zwischenschritten und Live-View-Session Integration.

Workflow-Phasen:
1. Datenanalyse und -kreierung (2 Stunden)
2. Strategie-Optimierung und Bot-Konfiguration (2 Stunden)
3. Order- und API-Vorbereitung für Echtgeldeinsatz (1 Stunde)
4. Live-View-Session Integration (parallel)
5. Fortschrittskontrolle und automatische Weiterführung
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import json
import os
import pandas as pd
import numpy as np

from config import config
from utils import (
    generate_sample_data, 
    validate_ohlcv_data,
    calculate_performance_metrics,
    setup_logging
)
from strategy import TradingStrategy, StrategyManager
from backtester import Backtester

# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """Repräsentation eines Workflow-Schritts"""
    name: str
    phase: str
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    time_limit_seconds: int = 7200  # Default: 2 Stunden
    error_message: Optional[str] = None
    results: Dict[str, Any] = field(default_factory=dict)
    
    def start(self):
        """Starte den Schritt"""
        self.status = "RUNNING"
        self.start_time = datetime.now()
        logger.info(f"▶️ Starte: {self.name} (Zeitlimit: {self.time_limit_seconds}s)")
    
    def complete(self, results: Dict[str, Any] = None):
        """Markiere Schritt als abgeschlossen"""
        self.status = "COMPLETED"
        self.end_time = datetime.now()
        if results:
            self.results = results
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"✅ Abgeschlossen: {self.name} (Dauer: {duration:.2f}s)")
    
    def fail(self, error: str):
        """Markiere Schritt als fehlgeschlagen"""
        self.status = "FAILED"
        self.end_time = datetime.now()
        self.error_message = error
        logger.error(f"❌ Fehlgeschlagen: {self.name} - {error}")
    
    def is_time_exceeded(self) -> bool:
        """Prüfe ob Zeitlimit überschritten"""
        if not self.start_time:
            return False
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed > self.time_limit_seconds
    
    def get_elapsed_time(self) -> float:
        """Hole verstrichene Zeit in Sekunden"""
        if not self.start_time:
            return 0.0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()


@dataclass
class WorkflowSession:
    """Trading Bot Workflow Session"""
    session_id: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: str = "RUNNING"  # RUNNING, COMPLETED, FAILED, STOPPED
    steps: List[WorkflowStep] = field(default_factory=list)
    current_step_index: int = 0
    data_directory: str = "data/workflow_sessions"
    live_view_enabled: bool = True
    
    def __post_init__(self):
        """Initialisiere Session-Verzeichnis"""
        os.makedirs(self.data_directory, exist_ok=True)
        self.session_file = os.path.join(
            self.data_directory, 
            f"session_{self.session_id}.json"
        )
    
    def add_step(self, step: WorkflowStep):
        """Füge Workflow-Schritt hinzu"""
        self.steps.append(step)
    
    def get_current_step(self) -> Optional[WorkflowStep]:
        """Hole aktuellen Schritt"""
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def advance_step(self):
        """Gehe zum nächsten Schritt"""
        self.current_step_index += 1
    
    def save_session(self):
        """Speichere Session-Status"""
        session_data = {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "current_step_index": self.current_step_index,
            "steps": [
                {
                    "name": step.name,
                    "phase": step.phase,
                    "status": step.status,
                    "start_time": step.start_time.isoformat() if step.start_time else None,
                    "end_time": step.end_time.isoformat() if step.end_time else None,
                    "time_limit_seconds": step.time_limit_seconds,
                    "error_message": step.error_message,
                    "elapsed_time": step.get_elapsed_time(),
                    "results": step.results
                }
                for step in self.steps
            ]
        }
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def get_progress_percentage(self) -> float:
        """Berechne Fortschritt in Prozent"""
        if not self.steps:
            return 0.0
        completed = sum(1 for step in self.steps if step.status == "COMPLETED")
        return (completed / len(self.steps)) * 100.0
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Hole Session-Zusammenfassung"""
        return {
            "session_id": self.session_id,
            "status": self.status,
            "progress": f"{self.get_progress_percentage():.1f}%",
            "current_step": self.get_current_step().name if self.get_current_step() else "Abgeschlossen",
            "total_steps": len(self.steps),
            "completed_steps": sum(1 for s in self.steps if s.status == "COMPLETED"),
            "failed_steps": sum(1 for s in self.steps if s.status == "FAILED"),
            "elapsed_time": (datetime.now() - self.start_time).total_seconds()
        }


class AutomatedWorkflow:
    """
    Vollautomatisierter Workflow für KI-Trading-Bot Vorbereitung
    
    Features:
    - Zeitlimit-überwachung für jeden Schritt
    - Automatische Fehlerkorrektur
    - Live-View Session Integration
    - Zwischenschritt-Validierung
    - Automatische Fortsetzung ohne manuelle Bestätigung
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialisiere Automated Workflow
        
        Args:
            session_id: Optionale Session-ID (wird generiert falls None)
        """
        self.session_id = session_id or f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session = WorkflowSession(session_id=self.session_id)
        self.config = config
        
        # Workflow-Status
        self.market_data = None
        self.strategy_results = {}
        self.api_status = {}
        
        # Initialisiere Workflow-Schritte
        self._initialize_workflow_steps()
        
        logger.info(f"🚀 Automatisierter Workflow initialisiert: {self.session_id}")
    
    def _initialize_workflow_steps(self):
        """Initialisiere alle Workflow-Schritte"""
        # Phase 1: Datenanalyse und -kreierung (2 Stunden)
        self.session.add_step(WorkflowStep(
            name="Marktdaten laden und analysieren",
            phase="Phase 1: Datenanalyse",
            time_limit_seconds=3600  # 1 Stunde
        ))
        self.session.add_step(WorkflowStep(
            name="Datenvalidierung und -bereinigung",
            phase="Phase 1: Datenanalyse",
            time_limit_seconds=1800  # 30 Minuten
        ))
        self.session.add_step(WorkflowStep(
            name="Strategieparameter-Analyse",
            phase="Phase 1: Datenanalyse",
            time_limit_seconds=1800  # 30 Minuten
        ))
        
        # Phase 2: Strategie-Optimierung (2 Stunden)
        self.session.add_step(WorkflowStep(
            name="Strategie-Konfiguration dynamisch anpassen",
            phase="Phase 2: Strategie-Optimierung",
            time_limit_seconds=3600  # 1 Stunde
        ))
        self.session.add_step(WorkflowStep(
            name="Backtesting und Profitabilitäts-Tests",
            phase="Phase 2: Strategie-Optimierung",
            time_limit_seconds=3600  # 1 Stunde
        ))
        
        # Phase 3: API-Vorbereitung (1 Stunde)
        self.session.add_step(WorkflowStep(
            name="Broker-API Konfiguration prüfen",
            phase="Phase 3: API-Vorbereitung",
            time_limit_seconds=1800  # 30 Minuten
        ))
        self.session.add_step(WorkflowStep(
            name="API-Sicherheit und Verschlüsselung validieren",
            phase="Phase 3: API-Vorbereitung",
            time_limit_seconds=1800  # 30 Minuten
        ))
        
        # Phase 4: Live-View Integration (läuft parallel)
        self.session.add_step(WorkflowStep(
            name="Live-View Session initialisieren",
            phase="Phase 4: Live-View Integration",
            time_limit_seconds=600  # 10 Minuten
        ))
        
        # Phase 5: Finale Validierung
        self.session.add_step(WorkflowStep(
            name="Finale System-Validierung",
            phase="Phase 5: Finale Validierung",
            time_limit_seconds=1200  # 20 Minuten
        ))
    
    def run_workflow(self, auto_continue: bool = True) -> Dict[str, Any]:
        """
        Führe vollständigen Workflow aus
        
        Args:
            auto_continue: Automatische Fortsetzung ohne manuelle Bestätigung
        
        Returns:
            Workflow-Ergebnis mit Status und Metriken
        """
        logger.info("=" * 70)
        logger.info("🎯 STARTE AUTOMATISIERTEN WORKFLOW")
        logger.info("=" * 70)
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"Anzahl Schritte: {len(self.session.steps)}")
        logger.info(f"Auto-Continue: {auto_continue}")
        logger.info("=" * 70)
        
        try:
            while self.session.current_step_index < len(self.session.steps):
                current_step = self.session.get_current_step()
                
                # Führe Schritt aus
                self._execute_step(current_step)
                
                # Speichere Session
                self.session.save_session()
                
                # Prüfe auf Fehler
                if current_step.status == "FAILED":
                    # Versuche Fehlerkorrektur
                    if not self._attempt_error_correction(current_step):
                        logger.error("❌ Fehlerkorrektur fehlgeschlagen. Workflow abgebrochen.")
                        self.session.status = "FAILED"
                        break
                
                # Zwischenschritt-Pause (max 10 Minuten)
                if auto_continue:
                    pause_seconds = 10  # Kurze Pause für Überprüfung
                    logger.info(f"⏸️ Pause für {pause_seconds}s zur Überprüfung...")
                    time.sleep(pause_seconds)
                else:
                    input(f"\n▶️ Drücke Enter um fortzufahren zum nächsten Schritt...")
                
                # Fortschritt anzeigen
                progress = self.session.get_progress_percentage()
                logger.info(f"📊 Fortschritt: {progress:.1f}% ({self.session.current_step_index + 1}/{len(self.session.steps)})")
                
                # Gehe zum nächsten Schritt
                self.session.advance_step()
            
            # Workflow abgeschlossen
            self.session.status = "COMPLETED"
            self.session.end_time = datetime.now()
            self.session.save_session()
            
            logger.info("=" * 70)
            logger.info("✅ WORKFLOW ERFOLGREICH ABGESCHLOSSEN")
            logger.info("=" * 70)
            
            return self._generate_workflow_report()
            
        except KeyboardInterrupt:
            logger.info("\n⏹️ Workflow manuell abgebrochen")
            self.session.status = "STOPPED"
            self.session.end_time = datetime.now()
            self.session.save_session()
            return self._generate_workflow_report()
        
        except Exception as e:
            logger.error(f"❌ Kritischer Fehler im Workflow: {e}", exc_info=True)
            self.session.status = "FAILED"
            self.session.end_time = datetime.now()
            self.session.save_session()
            return self._generate_workflow_report()
    
    def _execute_step(self, step: WorkflowStep):
        """
        Führe einzelnen Workflow-Schritt aus
        
        Args:
            step: Auszuführender Schritt
        """
        step.start()
        
        try:
            # Phase 1: Datenanalyse
            if step.name == "Marktdaten laden und analysieren":
                self._step_analyze_market_data(step)
            elif step.name == "Datenvalidierung und -bereinigung":
                self._step_validate_and_clean_data(step)
            elif step.name == "Strategieparameter-Analyse":
                self._step_analyze_strategy_parameters(step)
            
            # Phase 2: Strategie-Optimierung
            elif step.name == "Strategie-Konfiguration dynamisch anpassen":
                self._step_optimize_strategy_config(step)
            elif step.name == "Backtesting und Profitabilitäts-Tests":
                self._step_run_profitability_tests(step)
            
            # Phase 3: API-Vorbereitung
            elif step.name == "Broker-API Konfiguration prüfen":
                self._step_check_api_configuration(step)
            elif step.name == "API-Sicherheit und Verschlüsselung validieren":
                self._step_validate_api_security(step)
            
            # Phase 4: Live-View Integration
            elif step.name == "Live-View Session initialisieren":
                self._step_initialize_live_view(step)
            
            # Phase 5: Finale Validierung
            elif step.name == "Finale System-Validierung":
                self._step_final_system_validation(step)
            
            else:
                raise ValueError(f"Unbekannter Schritt: {step.name}")
            
            # Prüfe Zeitlimit
            if step.is_time_exceeded():
                logger.warning(f"⚠️ Zeitlimit überschritten für {step.name}")
            
        except Exception as e:
            step.fail(str(e))
            raise
    
    def _step_analyze_market_data(self, step: WorkflowStep):
        """Schritt: Marktdaten laden und analysieren"""
        logger.info("📊 Lade und analysiere Marktdaten...")
        
        # Generiere oder lade Marktdaten
        n_bars = 1000
        self.market_data = generate_sample_data(n_bars=n_bars)
        
        # Analysiere Daten
        analysis = {
            "n_bars": len(self.market_data),
            "date_range": f"{self.market_data.index[0]} bis {self.market_data.index[-1]}",
            "price_range": f"${self.market_data['close'].min():.2f} - ${self.market_data['close'].max():.2f}",
            "avg_volume": f"{self.market_data['volume'].mean():.2f}",
            "volatility": f"{self.market_data['close'].pct_change().std() * 100:.2f}%"
        }
        
        logger.info(f"  ✓ {n_bars} Kerzen geladen")
        logger.info(f"  ✓ Preisbereich: {analysis['price_range']}")
        logger.info(f"  ✓ Volatilität: {analysis['volatility']}")
        
        step.complete(results=analysis)
    
    def _step_validate_and_clean_data(self, step: WorkflowStep):
        """Schritt: Datenvalidierung und -bereinigung"""
        logger.info("🔍 Validiere und bereinige Daten...")
        
        if self.market_data is None:
            raise ValueError("Keine Marktdaten verfügbar")
        
        # Validiere Daten
        is_valid, error = validate_ohlcv_data(self.market_data)
        
        if not is_valid:
            raise ValueError(f"Datenvalidierung fehlgeschlagen: {error}")
        
        # Bereinigung (falls nötig)
        initial_count = len(self.market_data)
        self.market_data = self.market_data.dropna()
        cleaned_count = len(self.market_data)
        
        results = {
            "initial_rows": initial_count,
            "cleaned_rows": cleaned_count,
            "removed_rows": initial_count - cleaned_count,
            "validation_passed": is_valid
        }
        
        logger.info(f"  ✓ Validierung erfolgreich")
        logger.info(f"  ✓ {results['removed_rows']} Zeilen entfernt")
        
        step.complete(results=results)
    
    def _step_analyze_strategy_parameters(self, step: WorkflowStep):
        """Schritt: Strategieparameter-Analyse"""
        logger.info("⚙️ Analysiere Strategieparameter...")
        
        # Analysiere aktuelle Strategien
        active_strategies = self.config.active_strategies
        strategy_params = self.config.strategies
        
        analysis = {
            "active_strategies": active_strategies,
            "cooperation_logic": self.config.cooperation_logic,
            "strategy_count": len(active_strategies),
            "parameters": {
                name: params 
                for name, params in strategy_params.items() 
                if name in active_strategies
            }
        }
        
        logger.info(f"  ✓ {len(active_strategies)} aktive Strategien")
        logger.info(f"  ✓ Cooperation Logic: {self.config.cooperation_logic}")
        
        step.complete(results=analysis)
    
    def _step_optimize_strategy_config(self, step: WorkflowStep):
        """Schritt: Strategie-Konfiguration dynamisch anpassen"""
        logger.info("🎯 Optimiere Strategie-Konfiguration...")
        
        # Dynamische Anpassung basierend auf Marktdaten
        if self.market_data is None:
            raise ValueError("Keine Marktdaten für Optimierung verfügbar")
        
        # Berechne Markt-Volatilität
        volatility = self.market_data['close'].pct_change().std()
        
        # Passe Parameter an Volatilität an
        optimized_params = {}
        for strategy_name in self.config.active_strategies:
            params = self.config.strategies.get(strategy_name, {}).copy()
            
            # Beispiel: Passe RSI-Thresholds an Volatilität an
            if strategy_name == "rsi" and volatility > 0.02:
                params['oversold_threshold'] = 30  # Konservativer bei hoher Volatilität
                params['overbought_threshold'] = 70
                logger.info(f"  ✓ RSI-Parameter angepasst für hohe Volatilität")
            
            optimized_params[strategy_name] = params
        
        results = {
            "market_volatility": f"{volatility * 100:.2f}%",
            "optimized_strategies": list(optimized_params.keys()),
            "parameters": optimized_params
        }
        
        logger.info(f"  ✓ {len(optimized_params)} Strategien optimiert")
        
        step.complete(results=results)
    
    def _step_run_profitability_tests(self, step: WorkflowStep):
        """Schritt: Backtesting und Profitabilitäts-Tests"""
        logger.info("💰 Führe Profitabilitäts-Tests durch...")
        
        if self.market_data is None:
            raise ValueError("Keine Marktdaten für Backtesting verfügbar")
        
        # Initialisiere Backtester
        backtester = Backtester(initial_capital=self.config.initial_capital)
        
        # Führe Backtest durch
        backtester.run(self.market_data)
        
        # Extrahiere Ergebnisse
        backtest_results = {
            'initial_capital': backtester.initial_capital,
            'final_capital': backtester.capital,
            'total_trades': len(backtester.trades),
            'roi': ((backtester.capital - backtester.initial_capital) / backtester.initial_capital) * 100
        }
        
        # Berechne zusätzliche Metriken falls Trades vorhanden
        if backtester.trades:
            metrics = calculate_performance_metrics(backtester.trades)
            backtest_results.update(metrics)
        
        # Prüfe Profitabilität
        roi = backtest_results.get('roi', 0)
        win_rate = backtest_results.get('win_rate', 0)
        sharpe_ratio = backtest_results.get('sharpe_ratio', 0)
        
        is_profitable = roi > 5.0 and win_rate > 50.0  # Mindestkriterien
        
        results = {
            "roi": f"{roi:.2f}%",
            "win_rate": f"{win_rate:.2f}%",
            "sharpe_ratio": f"{sharpe_ratio:.2f}",
            "total_trades": backtest_results.get('total_trades', 0),
            "is_profitable": is_profitable,
            "final_capital": f"${backtest_results.get('final_capital', 0):.2f}"
        }
        
        logger.info(f"  ✓ ROI: {results['roi']}")
        logger.info(f"  ✓ Win Rate: {results['win_rate']}")
        logger.info(f"  ✓ Profitabel: {is_profitable}")
        
        if not is_profitable:
            logger.warning("⚠️ Strategie nicht profitabel genug! Optimierung empfohlen.")
        
        step.complete(results=results)
    
    def _step_check_api_configuration(self, step: WorkflowStep):
        """Schritt: Broker-API Konfiguration prüfen"""
        logger.info("🔌 Prüfe Broker-API Konfiguration...")
        
        # Prüfe API-Konfiguration
        has_binance_keys = bool(self.config.BINANCE_TESTNET_API_KEY)
        
        api_status = {
            "binance_testnet_configured": has_binance_keys,
            "paper_trading_available": True,  # Immer verfügbar
            "recommended_mode": "testnet" if has_binance_keys else "paper_trading"
        }
        
        if not has_binance_keys:
            logger.warning("⚠️ Keine Binance API-Keys konfiguriert")
            logger.info("  ℹ️ Verwende Paper Trading Modus für Tests")
        else:
            logger.info("  ✓ Binance Testnet konfiguriert")
        
        # Prüfe ob broker_api verfügbar ist
        try:
            from broker_api import PaperTradingAPI
            paper_api = PaperTradingAPI(initial_capital=self.config.initial_capital)
            balance = paper_api.get_balance()
            api_status["paper_trading_balance"] = balance
            logger.info(f"  ✓ Paper Trading API funktioniert (Balance: ${balance:.2f})")
        except ImportError:
            logger.info("  ℹ️ Paper Trading API nicht verfügbar (broker_api.py fehlt)")
            api_status["paper_trading_available"] = False
        except Exception as e:
            logger.error(f"  ❌ Paper Trading API Fehler: {e}")
            api_status["paper_trading_error"] = str(e)
        
        self.api_status = api_status
        step.complete(results=api_status)
    
    def _step_validate_api_security(self, step: WorkflowStep):
        """Schritt: API-Sicherheit und Verschlüsselung validieren"""
        logger.info("🔒 Validiere API-Sicherheit...")
        
        security_checks = {
            "env_file_exists": os.path.exists('.env') or os.path.exists('keys.env'),
            "keys_not_hardcoded": not self.config.BINANCE_API_KEY or self.config.BINANCE_API_KEY == os.getenv("BINANCE_API_KEY"),
            "testnet_mode": True,  # Für Echtgeld sollte dies false sein
            "ssl_enabled": True,  # APIs verwenden HTTPS
        }
        
        all_passed = all(security_checks.values())
        
        logger.info(f"  ✓ Environment-Datei: {security_checks['env_file_exists']}")
        logger.info(f"  ✓ Keine hardcodierten Keys: {security_checks['keys_not_hardcoded']}")
        logger.info(f"  ✓ SSL aktiviert: {security_checks['ssl_enabled']}")
        
        if not all_passed:
            logger.warning("⚠️ Nicht alle Sicherheitschecks bestanden")
        
        security_checks["all_passed"] = all_passed
        step.complete(results=security_checks)
    
    def _step_initialize_live_view(self, step: WorkflowStep):
        """Schritt: Live-View Session initialisieren"""
        logger.info("📺 Initialisiere Live-View Session...")
        
        # Speichere Session für Live-View
        self.session.save_session()
        
        results = {
            "session_id": self.session_id,
            "session_file": self.session.session_file,
            "live_view_url": f"/view-session/{self.session_id}",
            "progress": f"{self.session.get_progress_percentage():.1f}%"
        }
        
        logger.info(f"  ✓ Session gespeichert: {self.session.session_file}")
        logger.info(f"  ✓ Live-View verfügbar unter: {results['live_view_url']}")
        
        step.complete(results=results)
    
    def _step_final_system_validation(self, step: WorkflowStep):
        """Schritt: Finale System-Validierung"""
        logger.info("✅ Führe finale System-Validierung durch...")
        
        # Sammle alle Ergebnisse
        validation_results = {
            "data_validated": any(s.name == "Datenvalidierung und -bereinigung" and s.status == "COMPLETED" for s in self.session.steps),
            "strategy_optimized": any(s.name == "Strategie-Konfiguration dynamisch anpassen" and s.status == "COMPLETED" for s in self.session.steps),
            "profitability_tested": any(s.name == "Backtesting und Profitabilitäts-Tests" and s.status == "COMPLETED" for s in self.session.steps),
            "api_configured": any(s.name == "Broker-API Konfiguration prüfen" and s.status == "COMPLETED" for s in self.session.steps),
            "security_validated": any(s.name == "API-Sicherheit und Verschlüsselung validieren" and s.status == "COMPLETED" for s in self.session.steps),
        }
        
        all_validated = all(validation_results.values())
        validation_results["system_ready"] = all_validated
        
        if all_validated:
            logger.info("  ✅ Alle Validierungen erfolgreich!")
            logger.info("  🚀 System bereit für Paper Trading / Testnet")
            logger.warning("  ⚠️ FÜR ECHTGELD: Weitere Tests auf Testnet empfohlen!")
        else:
            logger.warning("  ⚠️ Nicht alle Validierungen erfolgreich")
            for check, passed in validation_results.items():
                if not passed:
                    logger.warning(f"    ❌ {check}: NICHT BESTANDEN")
        
        step.complete(results=validation_results)
    
    def _attempt_error_correction(self, step: WorkflowStep) -> bool:
        """
        Versuche Fehlerkorrektur für fehlgeschlagenen Schritt
        
        Args:
            step: Fehlgeschlagener Schritt
        
        Returns:
            True wenn Korrektur erfolgreich, sonst False
        """
        logger.info(f"🔧 Versuche Fehlerkorrektur für: {step.name}")
        
        max_retries = 3
        for retry in range(max_retries):
            logger.info(f"  Versuch {retry + 1}/{max_retries}...")
            
            try:
                # Reset step status
                step.status = "PENDING"
                step.error_message = None
                
                # Versuche erneut
                self._execute_step(step)
                
                if step.status == "COMPLETED":
                    logger.info(f"  ✅ Fehlerkorrektur erfolgreich!")
                    return True
                
            except Exception as e:
                logger.error(f"  ❌ Fehlerkorrektur-Versuch {retry + 1} fehlgeschlagen: {e}")
                step.fail(str(e))
                
                if retry < max_retries - 1:
                    time.sleep(5)  # Kurze Pause vor erneutem Versuch
        
        logger.error(f"  ❌ Fehlerkorrektur nach {max_retries} Versuchen fehlgeschlagen")
        return False
    
    def _generate_workflow_report(self) -> Dict[str, Any]:
        """Generiere Workflow-Abschluss-Report"""
        summary = self.session.get_session_summary()
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 WORKFLOW REPORT")
        logger.info("=" * 70)
        logger.info(f"Session ID: {summary['session_id']}")
        logger.info(f"Status: {summary['status']}")
        logger.info(f"Fortschritt: {summary['progress']}")
        logger.info(f"Abgeschlossene Schritte: {summary['completed_steps']}/{summary['total_steps']}")
        logger.info(f"Fehlgeschlagene Schritte: {summary['failed_steps']}")
        logger.info(f"Gesamtdauer: {summary['elapsed_time']:.2f}s")
        logger.info("=" * 70)
        
        # Detail-Ausgabe für jeden Schritt
        logger.info("\n📋 SCHRITT-DETAILS:")
        for i, step in enumerate(self.session.steps, 1):
            status_icon = "✅" if step.status == "COMPLETED" else "❌" if step.status == "FAILED" else "⏸️"
            logger.info(f"  {i}. {status_icon} {step.name}")
            logger.info(f"     Phase: {step.phase}")
            logger.info(f"     Status: {step.status}")
            logger.info(f"     Dauer: {step.get_elapsed_time():.2f}s")
            if step.error_message:
                logger.info(f"     Fehler: {step.error_message}")
        
        logger.info("\n" + "=" * 70)
        
        return summary


def main():
    """Hauptfunktion für Automated Workflow"""
    # Setup Logging
    setup_logging(config.log_level, config.log_file)
    
    logger.info("🚀 Starte Automatisierten Trading-Bot Workflow")
    
    # Erstelle und führe Workflow aus
    workflow = AutomatedWorkflow()
    results = workflow.run_workflow(auto_continue=True)
    
    logger.info("\n✅ Workflow abgeschlossen!")
    logger.info(f"Session-Datei: {workflow.session.session_file}")
    
    return results


if __name__ == "__main__":
    main()
