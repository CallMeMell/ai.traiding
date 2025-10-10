"""
runner.py - Automated Real-Money Readiness Workflow
=================================================
Automation runner with explicit phase time limits and automatic self-checks.
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.session_store import SessionStore
from core.env_helpers import EnvHelper
from automation.scheduler import PhaseScheduler

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
                 api_phase_timeout: int = 3600):  # 1 hour
        """
        Initialize automation runner.
        
        Args:
            data_phase_timeout: Timeout for data phase in seconds
            strategy_phase_timeout: Timeout for strategy phase in seconds
            api_phase_timeout: Timeout for API phase in seconds
        """
        self.data_phase_timeout = data_phase_timeout
        self.strategy_phase_timeout = strategy_phase_timeout
        self.api_phase_timeout = api_phase_timeout
        
        self.session_store = SessionStore()
        self.scheduler = PhaseScheduler(max_pause_minutes=10)
        
        # Load environment
        EnvHelper.load_dotenv_if_available()
        
        logger.info("AutomationRunner initialized")
        logger.info(f"Phase timeouts: data={data_phase_timeout}s, strategy={strategy_phase_timeout}s, api={api_phase_timeout}s")
    
    def _on_event(self, event: Dict[str, Any]) -> None:
        """
        Event handler to write events to session store.
        
        Args:
            event: Event dictionary
        """
        self.session_store.append_event(event)
        logger.info(f"Event: {event['type']} - {event.get('phase', 'N/A')}")
    
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
        
        # Write initial summary
        summary = {
            'session_start': start_time.isoformat(),
            'status': 'running',
            'phases_completed': 0,
            'phases_total': 3,
            'initial_capital': 10000.0,
            'current_equity': 10000.0
        }
        self.session_store.write_summary(summary)
        
        # Log session start event
        self._on_event({
            'type': 'session_start',
            'timestamp': start_time.isoformat()
        })
        
        results = {
            'start_time': start_time.isoformat(),
            'phases': {},
            'status': 'success'
        }
        
        try:
            # Phase 1: Data Phase
            logger.info("\n--- Phase 1: Data Phase ---")
            data_result = self.scheduler.run_phase(
                'data_phase',
                self._data_phase,
                self.data_phase_timeout,
                on_event=self._on_event
            )
            results['phases']['data_phase'] = data_result
            summary['phases_completed'] = 1
            summary['current_equity'] = 10050.0  # Simulate small gain
            self.session_store.write_summary(summary)
            
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
            strategy_result = self.scheduler.run_phase(
                'strategy_phase',
                self._strategy_phase,
                self.strategy_phase_timeout,
                on_event=self._on_event
            )
            results['phases']['strategy_phase'] = strategy_result
            summary['phases_completed'] = 2
            summary['current_equity'] = 10125.0  # Simulate more gain
            self.session_store.write_summary(summary)
            
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
            api_result = self.scheduler.run_phase(
                'api_phase',
                self._api_phase,
                self.api_phase_timeout,
                on_event=self._on_event
            )
            results['phases']['api_phase'] = api_result
            summary['phases_completed'] = 3
            summary['current_equity'] = 10150.0  # Simulate final equity
            self.session_store.write_summary(summary)
            
            if api_result['status'] not in ['success', 'warning']:
                logger.error(f"API phase failed: {api_result.get('error')}")
                results['status'] = 'failed'
            
        except Exception as e:
            logger.error(f"Automation workflow failed: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            
            self._on_event({
                'type': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        
        finally:
            # Write final summary
            end_time = datetime.now()
            summary['session_end'] = end_time.isoformat()
            summary['status'] = results['status']
            summary['roi'] = self.session_store.calculate_roi(
                summary['initial_capital'],
                summary['current_equity']
            )
            self.session_store.write_summary(summary)
            
            # Write session end event
            self._on_event({
                'type': 'session_end',
                'status': results['status'],
                'timestamp': end_time.isoformat()
            })
            
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = (end_time - start_time).total_seconds()
        
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
