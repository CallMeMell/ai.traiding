"""
test_orchestrator.py - System Orchestrator Tests
==============================================
Tests for the master system orchestrator.
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from system.orchestrator import SystemOrchestrator, SystemPhase, HealthStatus


class TestSystemOrchestrator:
    """Test SystemOrchestrator class."""
    
    def test_orchestrator_initialization(self, test_env):
        """Test orchestrator initialization."""
        orchestrator = SystemOrchestrator(
            dry_run=True,
            enable_health_checks=True,
            enable_recovery=True
        )
        
        assert orchestrator.dry_run is True
        assert orchestrator.enable_health_checks is True
        assert orchestrator.enable_recovery is True
        assert orchestrator.current_phase is None
        assert len(orchestrator.phases_completed) == 0
        assert orchestrator.health_status == HealthStatus.HEALTHY
    
    def test_orchestrator_run_success(self, test_env, temp_dir):
        """Test successful orchestrator run."""
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            orchestrator = SystemOrchestrator(dry_run=True)
            results = orchestrator.run()
            
            assert results['status'] == 'success'
            assert results['dry_run'] is True
            assert len(results['phases']) >= 6  # All phases including cleanup
            assert 'start_time' in results
            assert 'end_time' in results
            assert 'duration_seconds' in results
        finally:
            os.chdir(original_dir)
    
    def test_health_check(self, test_env):
        """Test health check functionality."""
        orchestrator = SystemOrchestrator(dry_run=True)
        
        health = orchestrator._health_check('test')
        assert health in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]
    
    def test_phase_initialization(self, test_env, temp_dir):
        """Test initialization phase."""
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            orchestrator = SystemOrchestrator(dry_run=True)
            result = orchestrator._phase_initialization()
            
            assert result['status'] == 'success'
            assert 'message' in result
            
            # Check directories created
            assert os.path.exists('data')
            assert os.path.exists('logs')
        finally:
            os.chdir(original_dir)
    
    def test_dry_run_mode(self, test_env):
        """Test that dry-run mode is respected."""
        orchestrator = SystemOrchestrator(dry_run=True)
        
        result = orchestrator._phase_api_integration()
        assert result['status'] == 'success'
        assert 'dry-run' in result['message'].lower()
    
    def test_phase_enum(self):
        """Test SystemPhase enum."""
        assert SystemPhase.INIT.value == "initialization"
        assert SystemPhase.DATA.value == "data_preparation"
        assert SystemPhase.STRATEGY.value == "strategy_execution"
        assert SystemPhase.API.value == "api_integration"
        assert SystemPhase.MONITORING.value == "monitoring"
        assert SystemPhase.CLEANUP.value == "cleanup"
    
    def test_health_status_enum(self):
        """Test HealthStatus enum."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"


class TestPhasesExecution:
    """Test individual phase executions."""
    
    def test_data_preparation_phase(self, test_env):
        """Test data preparation phase."""
        orchestrator = SystemOrchestrator(dry_run=True)
        result = orchestrator._phase_data_preparation()
        
        assert result['status'] == 'success'
        assert 'message' in result
    
    def test_strategy_execution_phase(self, test_env):
        """Test strategy execution phase."""
        orchestrator = SystemOrchestrator(dry_run=True)
        result = orchestrator._phase_strategy_execution()
        
        assert result['status'] == 'success'
        assert 'message' in result
    
    def test_monitoring_phase(self, test_env):
        """Test monitoring phase."""
        orchestrator = SystemOrchestrator(dry_run=True)
        result = orchestrator._phase_monitoring()
        
        assert result['status'] == 'success'
        assert 'metrics' in result
        assert 'phases_completed' in result['metrics']
        assert 'errors_count' in result['metrics']
    
    def test_cleanup_phase(self, test_env):
        """Test cleanup phase."""
        orchestrator = SystemOrchestrator(dry_run=True)
        result = orchestrator._phase_cleanup()
        
        assert result['status'] == 'success'
        assert 'message' in result


def test_orchestrator_main(test_env, temp_dir):
    """Test orchestrator main entry point."""
    original_dir = os.getcwd()
    os.chdir(temp_dir)
    
    try:
        from system.orchestrator import SystemOrchestrator
        
        orchestrator = SystemOrchestrator(dry_run=True)
        results = orchestrator.run()
        
        assert results['status'] == 'success'
    finally:
        os.chdir(original_dir)
