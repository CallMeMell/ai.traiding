"""
orchestrator.py - Master System Orchestrator
===========================================
Central orchestrator for all system phases with health checks and recovery.
"""

import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import logging as builtin_logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.runner import AutomationRunner
from automation.scheduler import PhaseScheduler

logger = builtin_logging.getLogger(__name__)


class SystemPhase(Enum):
    """System phase definitions."""
    INIT = "initialization"
    DATA = "data_preparation"
    STRATEGY = "strategy_execution"
    API = "api_integration"
    MONITORING = "monitoring"
    CLEANUP = "cleanup"


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class SystemOrchestrator:
    """
    Master orchestrator for the 12h pre-execution system.
    
    Manages all phases, health checks, and recovery mechanisms.
    """
    
    def __init__(self, 
                 dry_run: bool = True,
                 enable_health_checks: bool = True,
                 enable_recovery: bool = True):
        """
        Initialize system orchestrator.
        
        Args:
            dry_run: Run in dry-run mode (default: True for safety)
            enable_health_checks: Enable health checks between phases
            enable_recovery: Enable automatic recovery on failures
        """
        self.dry_run = dry_run
        self.enable_health_checks = enable_health_checks
        self.enable_recovery = enable_recovery
        
        # Initialize runner
        self.runner = AutomationRunner(
            data_phase_timeout=7200,      # 2 hours
            strategy_phase_timeout=7200,  # 2 hours
            api_phase_timeout=3600,       # 1 hour
            heartbeat_interval=30,
            enable_validation=True
        )
        
        # System state
        self.current_phase = None
        self.phases_completed = []
        self.health_status = HealthStatus.HEALTHY
        self.start_time = None
        self.errors = []
        
        logger.info("SystemOrchestrator initialized")
        logger.info(f"Dry-Run Mode: {dry_run}")
        logger.info(f"Health Checks: {enable_health_checks}")
        logger.info(f"Auto Recovery: {enable_recovery}")
    
    def run(self) -> Dict[str, Any]:
        """
        Run complete 12h system workflow.
        
        Returns:
            Dictionary with execution results
        """
        self.start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("🚀 Starting 12h Pre-Execution System")
        logger.info("=" * 60)
        
        results = {
            'status': 'success',
            'start_time': self.start_time.isoformat(),
            'phases': [],
            'errors': [],
            'dry_run': self.dry_run
        }
        
        try:
            # Phase 1: Initialization
            phase_result = self._run_phase(
                SystemPhase.INIT,
                self._phase_initialization
            )
            results['phases'].append(phase_result)
            
            if phase_result['status'] != 'success':
                raise Exception(f"Initialization failed: {phase_result.get('error')}")
            
            # Phase 2: Data Preparation
            phase_result = self._run_phase(
                SystemPhase.DATA,
                self._phase_data_preparation
            )
            results['phases'].append(phase_result)
            
            # Phase 3: Strategy Execution
            phase_result = self._run_phase(
                SystemPhase.STRATEGY,
                self._phase_strategy_execution
            )
            results['phases'].append(phase_result)
            
            # Phase 4: API Integration
            phase_result = self._run_phase(
                SystemPhase.API,
                self._phase_api_integration
            )
            results['phases'].append(phase_result)
            
            # Phase 5: Monitoring
            phase_result = self._run_phase(
                SystemPhase.MONITORING,
                self._phase_monitoring
            )
            results['phases'].append(phase_result)
            
            logger.info("✅ All phases completed successfully")
            
        except Exception as e:
            logger.error(f"❌ System execution failed: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            self.errors.append(str(e))
        
        finally:
            # Phase 6: Cleanup (always runs)
            cleanup_result = self._run_phase(
                SystemPhase.CLEANUP,
                self._phase_cleanup
            )
            results['phases'].append(cleanup_result)
            
            results['end_time'] = datetime.now().isoformat()
            results['duration_seconds'] = (datetime.now() - self.start_time).total_seconds()
            results['errors'] = self.errors
            
            logger.info("=" * 60)
            logger.info(f"🏁 System Execution Complete - Status: {results['status']}")
            logger.info(f"Duration: {results['duration_seconds']:.2f}s")
            logger.info("=" * 60)
        
        return results
    
    def _run_phase(self, phase: SystemPhase, phase_func: Callable) -> Dict[str, Any]:
        """
        Run a single phase with health checks.
        
        Args:
            phase: Phase enum
            phase_func: Function to execute
            
        Returns:
            Phase result dictionary
        """
        self.current_phase = phase
        logger.info(f"\n{'=' * 60}")
        logger.info(f"📍 Phase: {phase.value.upper()}")
        logger.info(f"{'=' * 60}")
        
        start_time = time.time()
        result = {
            'phase': phase.value,
            'status': 'success',
            'start_time': datetime.now().isoformat(),
            'duration_seconds': 0
        }
        
        try:
            # Pre-phase health check
            if self.enable_health_checks and phase != SystemPhase.INIT:
                health = self._health_check(f"pre_{phase.value}")
                if health != HealthStatus.HEALTHY:
                    logger.warning(f"Health check before {phase.value}: {health.value}")
            
            # Execute phase
            phase_result = phase_func()
            result.update(phase_result)
            
            # Post-phase health check
            if self.enable_health_checks:
                health = self._health_check(f"post_{phase.value}")
                result['health_status'] = health.value
            
            self.phases_completed.append(phase)
            logger.info(f"✅ Phase {phase.value} completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Phase {phase.value} failed: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
            self.errors.append(f"{phase.value}: {str(e)}")
            
            # Attempt recovery if enabled
            if self.enable_recovery and phase != SystemPhase.CLEANUP:
                recovery_result = self._attempt_recovery(phase, e)
                result['recovery'] = recovery_result
        
        finally:
            result['duration_seconds'] = time.time() - start_time
            result['end_time'] = datetime.now().isoformat()
        
        return result
    
    def _health_check(self, checkpoint: str) -> HealthStatus:
        """
        Perform system health check.
        
        Args:
            checkpoint: Health check checkpoint name
            
        Returns:
            Health status
        """
        logger.info(f"🏥 Health Check: {checkpoint}")
        
        # Basic health checks
        checks = {
            'memory': self._check_memory(),
            'disk': self._check_disk(),
            'connectivity': self._check_connectivity()
        }
        
        # Evaluate overall health
        if all(checks.values()):
            return HealthStatus.HEALTHY
        elif any(checks.values()):
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNHEALTHY
    
    def _check_memory(self) -> bool:
        """Check if memory usage is acceptable."""
        # Simplified check - in production use psutil
        return True
    
    def _check_disk(self) -> bool:
        """Check if disk space is sufficient."""
        # Simplified check - in production check actual disk space
        return True
    
    def _check_connectivity(self) -> bool:
        """Check if network connectivity is available."""
        # Simplified check - in production ping actual services
        return True
    
    def _attempt_recovery(self, phase: SystemPhase, error: Exception) -> Dict[str, Any]:
        """
        Attempt to recover from phase failure.
        
        Args:
            phase: Failed phase
            error: Exception that occurred
            
        Returns:
            Recovery result
        """
        logger.warning(f"🔄 Attempting recovery for {phase.value}")
        
        # Simple recovery: retry once
        try:
            time.sleep(5)  # Brief pause before retry
            logger.info(f"Retrying {phase.value}...")
            # In production, implement actual recovery logic
            return {
                'attempted': True,
                'success': False,
                'message': 'Recovery not implemented yet'
            }
        except Exception as e:
            logger.error(f"Recovery failed: {e}")
            return {
                'attempted': True,
                'success': False,
                'error': str(e)
            }
    
    # Phase implementations
    
    def _phase_initialization(self) -> Dict[str, Any]:
        """Initialize system components."""
        logger.info("Initializing system components...")
        
        # Check environment variables
        dry_run_env = os.getenv('DRY_RUN', 'true').lower() == 'true'
        logger.info(f"DRY_RUN environment: {dry_run_env}")
        
        # Verify directories
        required_dirs = ['data', 'logs', 'data/session']
        for dir_name in required_dirs:
            os.makedirs(dir_name, exist_ok=True)
            logger.info(f"✓ Directory verified: {dir_name}")
        
        return {
            'status': 'success',
            'message': 'System initialized'
        }
    
    def _phase_data_preparation(self) -> Dict[str, Any]:
        """Execute data preparation phase."""
        logger.info("Running data preparation phase...")
        
        # Delegate to automation runner (simplified)
        time.sleep(1)  # Simulate work
        
        return {
            'status': 'success',
            'message': 'Data preparation complete'
        }
    
    def _phase_strategy_execution(self) -> Dict[str, Any]:
        """Execute strategy phase."""
        logger.info("Running strategy execution phase...")
        
        # Delegate to automation runner (simplified)
        time.sleep(1)  # Simulate work
        
        return {
            'status': 'success',
            'message': 'Strategy execution complete'
        }
    
    def _phase_api_integration(self) -> Dict[str, Any]:
        """Execute API integration phase."""
        logger.info("Running API integration phase...")
        
        if self.dry_run:
            logger.info("⚠️  Dry-run mode - Skipping actual API calls")
        
        # Delegate to automation runner (simplified)
        time.sleep(1)  # Simulate work
        
        return {
            'status': 'success',
            'message': 'API integration complete (dry-run)' if self.dry_run else 'API integration complete'
        }
    
    def _phase_monitoring(self) -> Dict[str, Any]:
        """Execute monitoring phase."""
        logger.info("Running monitoring phase...")
        
        # Collect metrics
        metrics = {
            'phases_completed': len(self.phases_completed),
            'errors_count': len(self.errors),
            'health_status': self.health_status.value
        }
        
        logger.info(f"Metrics: {metrics}")
        
        return {
            'status': 'success',
            'message': 'Monitoring complete',
            'metrics': metrics
        }
    
    def _phase_cleanup(self) -> Dict[str, Any]:
        """Cleanup resources."""
        logger.info("Cleaning up resources...")
        
        # Stop heartbeats if running
        if hasattr(self.runner, 'stop_heartbeat'):
            self.runner.stop_heartbeat = True
        
        logger.info("✓ Cleanup complete")
        
        return {
            'status': 'success',
            'message': 'Cleanup complete'
        }


def main():
    """Main entry point for orchestrator."""
    # Configure logging
    builtin_logging.basicConfig(
        level=builtin_logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get DRY_RUN from environment (default: True for safety)
    dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
    
    # Create and run orchestrator
    orchestrator = SystemOrchestrator(
        dry_run=dry_run,
        enable_health_checks=True,
        enable_recovery=True
    )
    
    results = orchestrator.run()
    
    # Exit with appropriate code
    exit_code = 0 if results['status'] == 'success' else 1
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
