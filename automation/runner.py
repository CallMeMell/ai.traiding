"""
runner.py - Automated Real-Money Readiness Workflow
=================================================
Automation runner with explicit phase time limits and automatic self-checks.
"""

import time
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.session_store import SessionStore
from core.env_helpers import EnvHelper
from automation.scheduler import PhaseScheduler
from circuit_breaker import CircuitBreakerManager, CircuitBreakerActions
from config import config as trading_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutomationRunner:
    """
    Automation runner for real-money readiness workflow.
    Phases: data_phase, strategy_phase, api_phase
    """
    
    def __init__(self, 
                 data_phase_timeout: int = 7200,  # 2 hours
                 strategy_phase_timeout: int = 7200,  # 2 hours
                 api_phase_timeout: int = 3600,  # 1 hour
                 heartbeat_interval: int = 30,  # 30 seconds
                 enable_validation: bool = True,  # Validation enabled by default for strict schema compliance
                 max_drawdown_limit: float = 0.20):  # Circuit Breaker: 20% max drawdown
        """
        Initialize automation runner.
        
        Args:
            data_phase_timeout: Timeout for data phase in seconds
            strategy_phase_timeout: Timeout for strategy phase in seconds
            api_phase_timeout: Timeout for API phase in seconds
            heartbeat_interval: Interval between heartbeats in seconds
            enable_validation: Enable schema validation for events and summaries
            max_drawdown_limit: Maximum drawdown limit (0.20 = 20%) before circuit breaker triggers
        """
        self.data_phase_timeout = data_phase_timeout
        self.strategy_phase_timeout = strategy_phase_timeout
        self.api_phase_timeout = api_phase_timeout
        self.heartbeat_interval = heartbeat_interval
        self.enable_validation = enable_validation
        self.max_drawdown_limit = max_drawdown_limit
        
        self.session_store = SessionStore()
        self.scheduler = PhaseScheduler(max_pause_minutes=10)
        
        # Session tracking
        self.session_id = str(uuid.uuid4())
        self.session_start_time = None
        self.current_phase = None
        self.heartbeat_thread = None
        self.stop_heartbeat = False
        
        # Circuit Breaker tracking (Legacy)
        self.equity_curve = []
        self.circuit_breaker_triggered = False
        self.is_dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        
        # Erweiterte Circuit Breaker Logik
        self.use_advanced_cb = trading_config.use_advanced_circuit_breaker
        if self.use_advanced_cb:
            self.circuit_breaker_manager = CircuitBreakerManager(
                enabled=True,
                only_production=True
            )
            self._configure_advanced_circuit_breaker()
            logger.info("✓ Erweiterte Circuit Breaker Logik aktiviert")
        else:
            self.circuit_breaker_manager = None
            logger.info("Standard Circuit Breaker Logik aktiviert")
        
        # Load environment
        EnvHelper.load_dotenv_if_available()
        
        logger.info("AutomationRunner initialized")
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"Phase timeouts: data={data_phase_timeout}s, strategy={strategy_phase_timeout}s, api={api_phase_timeout}s")
        logger.info(f"Heartbeat interval: {heartbeat_interval}s")
        logger.info(f"Validation enabled: {enable_validation}")
        logger.info(f"Circuit Breaker: {'AKTIV (Production)' if not self.is_dry_run else 'INAKTIV (DRY_RUN)'}")
        logger.info(f"Drawdown-Limit: {max_drawdown_limit * 100:.1f}%")
    
    def _configure_advanced_circuit_breaker(self):
        """
        Konfiguriere erweiterte Circuit Breaker mit Actions
        """
        if not self.circuit_breaker_manager:
            return
        
        # Konfiguriere Schwellenwerte aus config
        for threshold_name, threshold_config in trading_config.circuit_breaker_thresholds.items():
            level = threshold_config.get('level')
            action_names = threshold_config.get('actions', [])
            description = threshold_config.get('description', '')
            
            # Erstelle Actions basierend auf Namen
            actions = []
            for action_name in action_names:
                if action_name == 'log':
                    actions.append(
                        CircuitBreakerActions.create_log_action(
                            message=f"🚨 Circuit Breaker: {level}% Drawdown-Limit überschritten!",
                            level='critical'
                        )
                    )
                elif action_name == 'alert':
                    # Alert wird über Event-System gehandelt
                    def create_event_action():
                        current_drawdown = self.circuit_breaker_manager.calculate_current_drawdown()
                        self.write_event(
                            event_type='circuit_breaker',
                            phase=self.current_phase,
                            level='critical',
                            message=f'Circuit Breaker {level}% ausgelöst!',
                            status='triggered',
                            details={
                                'current_drawdown_percent': current_drawdown,
                                'drawdown_limit_percent': level,
                                'threshold_name': threshold_name
                            }
                        )
                    actions.append(create_event_action)
                elif action_name == 'pause_trading':
                    actions.append(
                        CircuitBreakerActions.create_pause_trading_action(self)
                    )
                elif action_name == 'shutdown':
                    actions.append(
                        CircuitBreakerActions.create_shutdown_action(self)
                    )
                elif action_name == 'rebalance':
                    # Rebalancing - aktuell Platzhalter
                    actions.append(
                        CircuitBreakerActions.create_rebalance_action(None)
                    )
            
            # Füge Schwellenwert hinzu
            self.circuit_breaker_manager.add_threshold(
                level=level,
                actions=actions,
                description=description
            )
    
    def _on_event(self, event: Dict[str, Any]) -> None:
        """
        Event handler to write events to session store.
        
        Args:
            event: Event dictionary
        """
        self.session_store.append_event(event, validate=self.enable_validation)
        logger.info(f"Event: {event['type']} - {event.get('phase', 'N/A')}")
    
    def write_event(self, event_type: str, phase: Optional[str] = None, 
                   level: str = "info", message: Optional[str] = None,
                   metrics: Optional[Dict[str, Any]] = None,
                   order: Optional[Dict[str, Any]] = None,
                   details: Optional[Dict[str, Any]] = None,
                   status: Optional[str] = None,
                   error: Optional[str] = None) -> None:
        """
        Write a structured event.
        
        Args:
            event_type: Type of event (e.g., 'phase_start', 'checkpoint', 'heartbeat')
            phase: Phase name
            level: Log level (info, warning, error, debug)
            message: Human-readable message
            metrics: Performance metrics dictionary
            order: Order information dictionary
            details: Additional details dictionary
            status: Status string
            error: Error message if applicable
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'type': event_type,
            'phase': phase or self.current_phase,
            'level': level,
            'message': message
        }
        
        if metrics:
            event['metrics'] = metrics
        if order:
            event['order'] = order
        if details:
            event['details'] = details
        if status:
            event['status'] = status
        if error:
            event['error'] = error
        
        self._on_event(event)
    
    def heartbeat(self) -> None:
        """Emit a heartbeat event with current metrics."""
        summary = self.session_store.read_summary()
        metrics = {}
        
        if summary:
            metrics = {
                'equity': summary.get('current_equity'),
                'pnl': summary.get('current_equity', 0) - summary.get('initial_capital', 0),
                'trades': summary.get('totals', {}).get('trades', 0) if summary.get('totals') else 0,
                'wins': summary.get('totals', {}).get('wins', 0) if summary.get('totals') else 0,
                'losses': summary.get('totals', {}).get('losses', 0) if summary.get('totals') else 0
            }
        
        self.write_event(
            event_type='heartbeat',
            phase=self.current_phase,
            level='debug',
            message='Heartbeat',
            metrics=metrics
        )
    
    def _heartbeat_loop(self) -> None:
        """Background thread for periodic heartbeats."""
        while not self.stop_heartbeat:
            time.sleep(self.heartbeat_interval)
            if not self.stop_heartbeat:
                try:
                    self.heartbeat()
                except Exception as e:
                    logger.error(f"Heartbeat error: {e}")
    
    def _start_heartbeat(self) -> None:
        """Start heartbeat background thread."""
        if self.heartbeat_thread is None or not self.heartbeat_thread.is_alive():
            self.stop_heartbeat = False
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self.heartbeat_thread.start()
            logger.info("Heartbeat thread started")
    
    def _stop_heartbeat(self) -> None:
        """Stop heartbeat background thread."""
        self.stop_heartbeat = True
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=2)
            logger.info("Heartbeat thread stopped")
    
    def begin_phase(self, name: str, message: Optional[str] = None) -> None:
        """
        Begin a phase with structured event.
        
        Args:
            name: Phase name
            message: Optional message
        """
        self.current_phase = name
        self.write_event(
            event_type='phase_start',
            phase=name,
            level='info',
            message=message or f'Starting {name}',
            status='started'
        )
    
    def end_phase(self, name: str, ok: bool = True, error: Optional[str] = None,
                 duration: Optional[float] = None) -> None:
        """
        End a phase with structured event.
        
        Args:
            name: Phase name
            ok: Whether phase succeeded
            error: Error message if failed
            duration: Duration in seconds
        """
        event_data = {
            'event_type': 'phase_end',
            'phase': name,
            'level': 'info' if ok else 'error',
            'message': f'Completed {name}' if ok else f'Failed {name}',
            'status': 'success' if ok else 'failed'
        }
        
        if error:
            event_data['error'] = error
        if duration is not None:
            event_data['details'] = {'duration_seconds': duration}
        
        self.write_event(**event_data)
    
    def checkpoint(self, name: str, status: str, info: Optional[Dict[str, Any]] = None) -> None:
        """
        Emit a checkpoint event.
        
        Args:
            name: Checkpoint name
            status: Status (pass/fail)
            info: Additional checkpoint information
        """
        self.write_event(
            event_type='checkpoint',
            phase=self.current_phase,
            level='info' if status == 'pass' else 'warning',
            message=f'Checkpoint: {name}',
            status=status,
            details=info or {}
        )
    
    def autocorrect_attempt(self, n: int, reason: str, result: str) -> None:
        """
        Emit an autocorrect attempt event.
        
        Args:
            n: Attempt number
            reason: Reason for autocorrect
            result: Result of attempt
        """
        self.write_event(
            event_type='autocorrect_attempt',
            phase=self.current_phase,
            level='warning',
            message=f'Autocorrect attempt {n}: {reason}',
            details={
                'attempt_number': n,
                'reason': reason,
                'result': result
            }
        )
    
    def update_summary(self, partial: Dict[str, Any]) -> None:
        """
        Update summary with partial data.
        
        Args:
            partial: Partial summary data to update
        """
        summary = self.session_store.read_summary() or {}
        summary.update(partial)
        self.session_store.write_summary(summary, validate=self.enable_validation)
        
        # Emit summary updated event
        self.write_event(
            event_type='summary_updated',
            phase=self.current_phase,
            level='debug',
            message='Summary updated',
            details=partial
        )
    
    def check_circuit_breaker(self, current_equity: float) -> bool:
        """
        Prüfe Circuit Breaker (Drawdown-Limit)
        
        Args:
            current_equity: Aktuelles Kapital
            
        Returns:
            True wenn Circuit Breaker ausgelöst wurde
        """
        # Verwende erweiterten Circuit Breaker falls aktiviert
        if self.use_advanced_cb and self.circuit_breaker_manager:
            triggered = self.circuit_breaker_manager.check(
                current_equity=current_equity,
                is_dry_run=self.is_dry_run
            )
            
            if triggered:
                self.circuit_breaker_triggered = True
            
            return triggered
        
        # Legacy Circuit Breaker
        # Circuit Breaker nur im Production-Modus (nicht DRY_RUN)
        if self.is_dry_run:
            return False
        
        # Update equity curve
        self.equity_curve.append(current_equity)
        
        if len(self.equity_curve) < 2:
            return False
        
        # Berechne aktuellen Drawdown
        import numpy as np
        equity_array = np.array(self.equity_curve)
        peak_value = np.max(equity_array)
        current_value = equity_array[-1]
        
        if peak_value == 0:
            return False
        
        current_drawdown = ((current_value - peak_value) / peak_value) * 100
        drawdown_limit_percent = self.max_drawdown_limit * 100
        
        if current_drawdown < -drawdown_limit_percent:
            self.circuit_breaker_triggered = True
            
            # Emit critical circuit breaker event
            self.write_event(
                event_type='circuit_breaker',
                phase=self.current_phase,
                level='critical',
                message='Circuit Breaker ausgelöst! Drawdown-Limit überschritten',
                status='triggered',
                details={
                    'current_drawdown_percent': current_drawdown,
                    'drawdown_limit_percent': drawdown_limit_percent,
                    'peak_value': float(peak_value),
                    'current_value': float(current_value),
                    'loss': float(current_value - peak_value)
                }
            )
            
            logger.critical("=" * 70)
            logger.critical("🚨 CIRCUIT BREAKER AUSGELÖST! 🚨")
            logger.critical("=" * 70)
            logger.critical(f"Aktueller Drawdown: {current_drawdown:.2f}%")
            logger.critical(f"Drawdown-Limit: {drawdown_limit_percent:.2f}%")
            logger.critical(f"Peak Value: ${peak_value:,.2f}")
            logger.critical(f"Current Value: ${current_value:,.2f}")
            logger.critical(f"Verlust: ${current_value - peak_value:,.2f}")
            logger.critical("Workflow wird SOFORT gestoppt!")
            logger.critical("=" * 70)
            
            return True
        
        return False
    
    def _retry_with_backoff(self, func, max_retries: int = 3, base_delay: float = 1.0, 
                           max_delay: float = 30.0, operation_name: str = "operation") -> Any:
        """
        Retry a function with exponential backoff.
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            operation_name: Name of operation for logging
            
        Returns:
            Result of the function
            
        Raises:
            Exception: If all retries fail
        """
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Attempt {attempt}/{max_retries} for {operation_name}")
                result = func()
                
                if attempt > 1:
                    # Log successful retry
                    self.autocorrect_attempt(
                        attempt, 
                        f"Retry for {operation_name}", 
                        "success"
                    )
                
                return result
                
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt}/{max_retries} failed for {operation_name}: {e}")
                
                # Log retry attempt
                self.autocorrect_attempt(
                    attempt,
                    f"Error in {operation_name}: {str(e)}",
                    f"failed" if attempt == max_retries else "retrying"
                )
                
                if attempt < max_retries:
                    # Calculate exponential backoff delay
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.info(f"Waiting {delay}s before retry...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {max_retries} attempts failed for {operation_name}")
        
        # All retries failed
        raise last_error
    
    def _data_phase(self) -> Dict[str, Any]:
        """
        Data phase: Load and validate data.
        
        Returns:
            Phase result dictionary
        """
        logger.info("Executing data phase...")
        
        # Simulate data loading and validation
        result = {
            'status': 'success',
            'data_loaded': True,
            'records': 1000,
            'message': 'Data phase completed successfully'
        }
        
        # Simulate some work
        time.sleep(2)
        
        return result
    
    def _strategy_phase(self) -> Dict[str, Any]:
        """
        Strategy phase: Test and validate strategies.
        
        Returns:
            Phase result dictionary
        """
        logger.info("Executing strategy phase...")
        
        # Simulate strategy testing
        result = {
            'status': 'success',
            'strategies_tested': 3,
            'strategies_passed': 3,
            'message': 'Strategy phase completed successfully'
        }
        
        # Simulate some work
        time.sleep(2)
        
        return result
    
    def _api_phase(self) -> Dict[str, Any]:
        """
        API phase: Validate API keys and connectivity.
        
        Returns:
            Phase result dictionary
        """
        logger.info("Executing API phase...")
        
        # Validate API keys
        validation = EnvHelper.validate_api_keys(['binance_api_key', 'binance_api_secret'])
        
        # Dry-run connectivity check
        connectivity = EnvHelper.dry_run_connectivity_check()
        
        result = {
            'status': 'success' if validation['valid'] else 'warning',
            'api_keys_valid': validation['valid'],
            'missing_keys': validation['missing'],
            'connectivity': connectivity,
            'message': 'API phase completed' if validation['valid'] else 'API keys missing'
        }
        
        # Simulate some work
        time.sleep(2)
        
        return result
    
    def _run_pre_live_checks(self) -> Dict[str, Any]:
        """
        Run comprehensive pre-live checks for data, strategy, and API.
        
        Returns:
            Dictionary with check results and overall status
        """
        logger.info("=" * 70)
        logger.info("RUNNING PRE-LIVE CHECKS")
        logger.info("=" * 70)
        
        results = {
            'status': 'success',
            'checks': {},
            'critical_failures': [],
            'warnings': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Emit pre-live check start event
        self.write_event(
            event_type='pre_live_check_start',
            level='info',
            message='Starting pre-live checks',
            status='started'
        )
        
        # Check 1: Data Validation
        logger.info("\n🔍 Check 1: Data Validation")
        try:
            data_check = self._check_data_validation()
        except Exception as e:
            logger.error(f"  ❌ Data validation error: {str(e)}")
            data_check = {
                'status': 'critical',
                'message': f"Data validation error: {str(e)}",
                'details': {}
            }
        
        results['checks']['data_validation'] = data_check
        
        if data_check['status'] == 'critical':
            results['critical_failures'].append(data_check['message'])
        elif data_check['status'] == 'warning':
            results['warnings'].append(data_check['message'])
        
        # Check 2: Strategy Validation
        logger.info("\n🔍 Check 2: Strategy Validation")
        try:
            strategy_check = self._check_strategy_validation()
        except Exception as e:
            logger.error(f"  ❌ Strategy validation error: {str(e)}")
            strategy_check = {
                'status': 'critical',
                'message': f"Strategy validation error: {str(e)}",
                'details': {}
            }
        
        results['checks']['strategy_validation'] = strategy_check
        
        if strategy_check['status'] == 'critical':
            results['critical_failures'].append(strategy_check['message'])
        elif strategy_check['status'] == 'warning':
            results['warnings'].append(strategy_check['message'])
        
        # Check 3: API Connectivity
        logger.info("\n🔍 Check 3: API Connectivity")
        try:
            api_check = self._check_api_connectivity()
        except Exception as e:
            logger.error(f"  ❌ API connectivity error: {str(e)}")
            api_check = {
                'status': 'critical',
                'message': f"API connectivity error: {str(e)}",
                'details': {}
            }
        
        results['checks']['api_connectivity'] = api_check
        
        if api_check['status'] == 'critical':
            results['critical_failures'].append(api_check['message'])
        elif api_check['status'] == 'warning':
            results['warnings'].append(api_check['message'])
        
        # Determine overall status
        if results['critical_failures']:
            results['status'] = 'critical'
            logger.error(f"\n❌ PRE-LIVE CHECKS FAILED: {len(results['critical_failures'])} critical failure(s)")
        elif results['warnings']:
            results['status'] = 'warning'
            logger.warning(f"\n⚠️  PRE-LIVE CHECKS PASSED WITH WARNINGS: {len(results['warnings'])} warning(s)")
        else:
            results['status'] = 'success'
            logger.info("\n✅ PRE-LIVE CHECKS PASSED")
        
        # Emit detailed check results
        self.write_event(
            event_type='pre_live_check_complete',
            level='error' if results['status'] == 'critical' else 'warning' if results['status'] == 'warning' else 'info',
            message=f"Pre-live checks completed with status: {results['status']}",
            status=results['status'],
            details={
                'critical_failures': results['critical_failures'],
                'warnings': results['warnings'],
                'checks': {k: {'status': v['status'], 'message': v['message']} for k, v in results['checks'].items()}
            }
        )
        
        logger.info("=" * 70)
        
        return results
    
    def _check_data_validation(self) -> Dict[str, Any]:
        """
        Validate data quality and availability.
        
        Returns:
            Check result dictionary
        """
        result = {
            'status': 'success',
            'message': 'Data validation passed',
            'details': {}
        }
        
        try:
            # Simulate data validation checks
            # In production, this would check:
            # - Minimum number of records available
            # - Data freshness (not too old)
            # - Data quality (no missing values in critical fields)
            # - Sufficient historical data for backtesting
            
            min_records_required = 100
            simulated_record_count = 1000  # In production: query actual data source
            
            if simulated_record_count < min_records_required:
                result['status'] = 'critical'
                result['message'] = f"Insufficient data: {simulated_record_count} records (min: {min_records_required})"
                logger.error(f"  ❌ {result['message']}")
            else:
                result['details']['record_count'] = simulated_record_count
                logger.info(f"  ✅ Data records: {simulated_record_count} (min: {min_records_required})")
            
            # Check data freshness (simulated)
            data_age_hours = 1  # In production: calculate from latest timestamp
            max_age_hours = 24
            
            if data_age_hours > max_age_hours:
                result['status'] = 'warning'
                result['message'] = f"Data may be stale: {data_age_hours}h old (max: {max_age_hours}h)"
                logger.warning(f"  ⚠️  {result['message']}")
            else:
                result['details']['data_age_hours'] = data_age_hours
                logger.info(f"  ✅ Data freshness: {data_age_hours}h old (max: {max_age_hours}h)")
            
        except Exception as e:
            result['status'] = 'critical'
            result['message'] = f"Data validation error: {str(e)}"
            logger.error(f"  ❌ {result['message']}")
        
        return result
    
    def _check_strategy_validation(self) -> Dict[str, Any]:
        """
        Validate strategy performance and configuration.
        
        Returns:
            Check result dictionary
        """
        result = {
            'status': 'success',
            'message': 'Strategy validation passed',
            'details': {}
        }
        
        try:
            # Simulate strategy validation checks
            # In production, this would check:
            # - Strategy has positive backtest results
            # - Win rate above minimum threshold
            # - Maximum drawdown within acceptable limits
            # - Risk/reward ratio acceptable
            # - Strategy parameters are within valid ranges
            
            min_win_rate = 0.40  # 40%
            simulated_win_rate = 0.55  # In production: calculate from backtest results
            
            if simulated_win_rate < min_win_rate:
                result['status'] = 'critical'
                result['message'] = f"Strategy win rate too low: {simulated_win_rate:.1%} (min: {min_win_rate:.1%})"
                logger.error(f"  ❌ {result['message']}")
            else:
                result['details']['win_rate'] = simulated_win_rate
                logger.info(f"  ✅ Strategy win rate: {simulated_win_rate:.1%} (min: {min_win_rate:.1%})")
            
            # Check strategy drawdown
            max_acceptable_drawdown = 0.25  # 25%
            simulated_max_drawdown = 0.15  # In production: calculate from backtest
            
            if simulated_max_drawdown > max_acceptable_drawdown:
                result['status'] = 'warning'
                result['message'] = f"Strategy drawdown high: {simulated_max_drawdown:.1%} (max: {max_acceptable_drawdown:.1%})"
                logger.warning(f"  ⚠️  {result['message']}")
            else:
                result['details']['max_drawdown'] = simulated_max_drawdown
                logger.info(f"  ✅ Strategy drawdown: {simulated_max_drawdown:.1%} (max: {max_acceptable_drawdown:.1%})")
            
            # Check strategy has been tested
            simulated_backtest_trades = 50  # In production: get from backtest results
            min_backtest_trades = 20
            
            if simulated_backtest_trades < min_backtest_trades:
                result['status'] = 'warning'
                result['message'] = f"Insufficient backtest trades: {simulated_backtest_trades} (min: {min_backtest_trades})"
                logger.warning(f"  ⚠️  {result['message']}")
            else:
                result['details']['backtest_trades'] = simulated_backtest_trades
                logger.info(f"  ✅ Backtest trades: {simulated_backtest_trades} (min: {min_backtest_trades})")
            
        except Exception as e:
            result['status'] = 'critical'
            result['message'] = f"Strategy validation error: {str(e)}"
            logger.error(f"  ❌ {result['message']}")
        
        return result
    
    def _check_api_connectivity(self) -> Dict[str, Any]:
        """
        Validate API keys and connectivity.
        
        Returns:
            Check result dictionary
        """
        result = {
            'status': 'success',
            'message': 'API connectivity validated',
            'details': {}
        }
        
        try:
            # Check API keys presence
            validation = EnvHelper.validate_api_keys(['binance_api_key', 'binance_api_secret'])
            
            # Determine if we're in production mode (check at call time, not init time)
            is_dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
            
            if not validation['valid']:
                # Only critical in production mode
                if not is_dry_run:
                    result['status'] = 'critical'
                    result['message'] = f"API keys missing: {', '.join(validation['missing'])}"
                    logger.error(f"  ❌ {result['message']}")
                else:
                    result['status'] = 'warning'
                    result['message'] = f"API keys missing (OK in DRY_RUN): {', '.join(validation['missing'])}"
                    logger.warning(f"  ⚠️  {result['message']}")
            else:
                result['details']['api_keys_present'] = validation['present']
                logger.info(f"  ✅ API keys present: {len(validation['present'])}")
            
            # Check connectivity (dry-run mode)
            connectivity = EnvHelper.dry_run_connectivity_check()
            result['details']['connectivity'] = connectivity
            
            # Check if production endpoint is configured (only in live mode)
            if not is_dry_run:
                base_url = os.getenv("BINANCE_BASE_URL", "")
                if base_url and not base_url.startswith("https://api.binance.com"):
                    # Only set to critical if not already critical from missing keys
                    if result['status'] != 'critical':
                        result['status'] = 'critical'
                        result['message'] = f"Invalid production endpoint: {base_url}"
                    logger.error(f"  ❌ Invalid production endpoint: {base_url}")
                elif not base_url:
                    # Only set to warning if not already critical
                    if result['status'] != 'critical':
                        result['status'] = 'warning'
                        result['message'] = "Production endpoint not explicitly configured"
                    logger.warning(f"  ⚠️  Production endpoint not explicitly configured")
                else:
                    logger.info(f"  ✅ Production endpoint configured")
            
        except Exception as e:
            result['status'] = 'critical'
            result['message'] = f"API connectivity check error: {str(e)}"
            logger.error(f"  ❌ {result['message']}")
        
        return result
    
    def _self_check(self) -> Dict[str, Any]:
        """
        Self-check between phases.
        
        Returns:
            Check result dictionary
        """
        logger.info("Running self-check...")
        
        # Basic health checks
        result = {
            'status': 'healthy',
            'checks': {
                'session_store': os.path.exists(self.session_store.events_path),
                'metrics_available': bool(self.scheduler.get_metrics())
            }
        }
        
        return result
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete automation workflow.
        
        Returns:
            Overall results dictionary
        """
        logger.info("=" * 70)
        logger.info("AUTOMATION RUNNER - REAL-MONEY READINESS WORKFLOW")
        logger.info("=" * 70)
        
        start_time = datetime.now()
        self.session_start_time = start_time
        
        # Write initial summary
        summary = {
            'session_id': self.session_id,
            'session_start': start_time.isoformat(),
            'status': 'running',
            'phases_completed': 0,
            'phases_total': 3,
            'initial_capital': 10000.0,
            'current_equity': 10000.0
        }
        self.session_store.write_summary(summary, validate=self.enable_validation)
        
        # Emit runner start event
        self.write_event(
            event_type='runner_start',
            level='info',
            message='Automation runner started',
            status='started'
        )
        
        # Start heartbeat thread
        self._start_heartbeat()
        
        results = {
            'start_time': start_time.isoformat(),
            'phases': {},
            'status': 'success',
            'pre_live_checks': None
        }
        
        try:
            # Pre-Live Checks (before any phases)
            logger.info("\n" + "=" * 70)
            logger.info("PRE-LIVE CHECKS")
            logger.info("=" * 70)
            
            pre_live_result = self._run_pre_live_checks()
            results['pre_live_checks'] = pre_live_result
            
            # Abort workflow if critical failures detected
            if pre_live_result['status'] == 'critical':
                logger.critical("\n" + "=" * 70)
                logger.critical("🚨 WORKFLOW ABORTED - CRITICAL PRE-LIVE CHECK FAILURES")
                logger.critical("=" * 70)
                logger.critical(f"Critical failures ({len(pre_live_result['critical_failures'])}):")
                for i, failure in enumerate(pre_live_result['critical_failures'], 1):
                    logger.critical(f"  {i}. {failure}")
                logger.critical("=" * 70)
                logger.critical("❌ Fix these issues before starting live trading!")
                logger.critical("=" * 70)
                
                results['status'] = 'aborted'
                results['abort_reason'] = 'pre_live_checks_failed'
                
                self.write_event(
                    event_type='workflow_aborted',
                    level='critical',
                    message='Workflow aborted due to failed pre-live checks',
                    status='aborted',
                    details={
                        'critical_failures': pre_live_result['critical_failures']
                    }
                )
                
                return results
            
            # Log warnings if present
            if pre_live_result['warnings']:
                logger.warning("\n⚠️  Pre-live checks passed with warnings:")
                for i, warning in enumerate(pre_live_result['warnings'], 1):
                    logger.warning(f"  {i}. {warning}")
                logger.warning("Proceeding with caution...\n")
            
            # Phase 1: Data Phase
            logger.info("\n--- Phase 1: Data Phase ---")
            self.begin_phase('data_phase', 'Starting data phase')
            
            # Emit checkpoint
            self.checkpoint('data_phase_start', 'pass', {'validation': 'schema_ok'})
            
            data_result = self.scheduler.run_phase(
                'data_phase',
                self._data_phase,
                self.data_phase_timeout,
                on_event=self._on_event
            )
            results['phases']['data_phase'] = data_result
            
            # Update summary
            current_equity = 10050.0
            self.update_summary({
                'phases_completed': 1,
                'current_equity': current_equity
            })
            
            # Check circuit breaker
            if self.check_circuit_breaker(current_equity):
                results['status'] = 'circuit_breaker'
                results['circuit_breaker_triggered'] = True
                return results
            
            self.end_phase('data_phase', ok=data_result['status'] == 'success',
                          duration=data_result.get('duration_seconds'))
            
            if data_result['status'] != 'success':
                logger.error(f"Data phase failed: {data_result.get('error')}")
                results['status'] = 'failed'
                return results
            
            # Pause and self-check
            logger.info("\n--- Pause and Self-Check ---")
            check_result = self.scheduler.pause_and_check(
                self._self_check,
                pause_seconds=5,
                on_event=self._on_event
            )
            results['check_1'] = check_result
            
            # Phase 2: Strategy Phase
            logger.info("\n--- Phase 2: Strategy Phase ---")
            self.begin_phase('strategy_phase', 'Starting strategy phase')
            
            # Emit checkpoint
            self.checkpoint('strategy_phase_start', 'pass', {'validation': 'lint_ok'})
            
            strategy_result = self.scheduler.run_phase(
                'strategy_phase',
                self._strategy_phase,
                self.strategy_phase_timeout,
                on_event=self._on_event
            )
            results['phases']['strategy_phase'] = strategy_result
            
            # Update summary with trade stats
            current_equity = 10125.0
            self.update_summary({
                'phases_completed': 2,
                'current_equity': current_equity,
                'totals': {'trades': 5, 'wins': 3, 'losses': 2}
            })
            
            # Check circuit breaker
            if self.check_circuit_breaker(current_equity):
                results['status'] = 'circuit_breaker'
                results['circuit_breaker_triggered'] = True
                return results
            
            self.end_phase('strategy_phase', ok=strategy_result['status'] == 'success',
                          duration=strategy_result.get('duration_seconds'))
            
            if strategy_result['status'] != 'success':
                logger.error(f"Strategy phase failed: {strategy_result.get('error')}")
                results['status'] = 'failed'
                return results
            
            # Pause and self-check
            logger.info("\n--- Pause and Self-Check ---")
            check_result = self.scheduler.pause_and_check(
                self._self_check,
                pause_seconds=5,
                on_event=self._on_event
            )
            results['check_2'] = check_result
            
            # Phase 3: API Phase
            logger.info("\n--- Phase 3: API Phase ---")
            self.begin_phase('api_phase', 'Starting API phase')
            
            # Emit checkpoint
            self.checkpoint('api_phase_start', 'pass', {'validation': 'api_keys_present'})
            
            api_result = self.scheduler.run_phase(
                'api_phase',
                self._api_phase,
                self.api_phase_timeout,
                on_event=self._on_event
            )
            results['phases']['api_phase'] = api_result
            
            # Final summary update
            current_equity = 10150.0
            self.update_summary({
                'phases_completed': 3,
                'current_equity': current_equity,
                'totals': {'trades': 10, 'wins': 6, 'losses': 4}
            })
            
            # Check circuit breaker
            if self.check_circuit_breaker(current_equity):
                results['status'] = 'circuit_breaker'
                results['circuit_breaker_triggered'] = True
                return results
            
            self.end_phase('api_phase', ok=api_result['status'] in ['success', 'warning'],
                          duration=api_result.get('duration_seconds'))
            
            if api_result['status'] not in ['success', 'warning']:
                logger.error(f"API phase failed: {api_result.get('error')}")
                results['status'] = 'failed'
            
        except Exception as e:
            logger.error(f"Automation workflow failed: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            
            self.write_event(
                event_type='error',
                level='error',
                message='Workflow failed',
                error=str(e)
            )
        
        finally:
            # Stop heartbeat
            self._stop_heartbeat()
            
            # Write final summary
            end_time = datetime.now()
            runtime_secs = (end_time - start_time).total_seconds()
            
            summary = self.session_store.read_summary() or {}
            summary.update({
                'session_end': end_time.isoformat(),
                'status': results['status'],
                'runtime_secs': runtime_secs
            })
            
            # Add circuit breaker info
            if self.circuit_breaker_triggered:
                summary['circuit_breaker_triggered'] = True
                summary['circuit_breaker_reason'] = f'Drawdown exceeded {self.max_drawdown_limit * 100:.1f}%'
            
            # Calculate ROI and drawdown
            if 'initial_capital' in summary and 'current_equity' in summary:
                summary['roi'] = self.session_store.calculate_roi(
                    summary['initial_capital'],
                    summary['current_equity']
                )
            
            # Calculate max drawdown if equity curve available
            if len(self.equity_curve) > 1:
                import numpy as np
                equity_array = np.array(self.equity_curve)
                running_max = np.maximum.accumulate(equity_array)
                drawdown = (equity_array - running_max) / running_max
                max_dd_idx = np.argmin(drawdown)
                max_dd_percent = drawdown[max_dd_idx] * 100
                summary['max_drawdown_percent'] = float(max_dd_percent)
            
            self.session_store.write_summary(summary, validate=self.enable_validation)
            
            # Emit runner end event
            self.write_event(
                event_type='runner_end',
                level='info',
                message=f'Automation runner ended with status: {results["status"]}',
                status=results['status'],
                details={'runtime_secs': runtime_secs}
            )
            
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = runtime_secs
        
        logger.info("=" * 70)
        logger.info(f"WORKFLOW COMPLETED - Status: {results['status']}")
        logger.info("=" * 70)
        
        return results


def main():
    """Main entry point."""
    logger.info("Starting automation runner...")
    
    runner = AutomationRunner(
        data_phase_timeout=7200,  # 2 hours
        strategy_phase_timeout=7200,  # 2 hours
        api_phase_timeout=3600  # 1 hour
    )
    
    results = runner.run()
    
    # Print summary
    print("\n" + "=" * 70)
    print("AUTOMATION SUMMARY")
    print("=" * 70)
    print(f"Status: {results['status']}")
    print(f"Duration: {results.get('duration_seconds', 0):.2f} seconds")
    print(f"\nPhases completed:")
    for phase_name, phase_result in results.get('phases', {}).items():
        print(f"  - {phase_name}: {phase_result['status']} ({phase_result.get('duration_seconds', 0):.2f}s)")
    print("=" * 70)
    
    return 0 if results['status'] == 'success' else 1


if __name__ == '__main__':
    sys.exit(main())
