"""
test_integration.py - Integration Tests
=====================================
End-to-end integration tests for the complete system.
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from system.orchestrator import SystemOrchestrator
from system.config.manager import ConfigManager
from system.monitoring.slo import SLOMonitor
from system.monitoring.metrics import MetricsCollector


class TestSystemIntegration:
    """Integration tests for complete system."""
    
    def test_full_system_run(self, test_env, temp_dir):
        """Test complete system orchestration."""
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create orchestrator
            orchestrator = SystemOrchestrator(
                dry_run=True,
                enable_health_checks=True,
                enable_recovery=True
            )
            
            # Run system
            results = orchestrator.run()
            
            # Verify results
            assert results['status'] == 'success'
            assert results['dry_run'] is True
            assert len(results['phases']) >= 6
            assert len(results['errors']) == 0
            
            # Verify all phases completed
            phase_names = [p['phase'] for p in results['phases']]
            assert 'initialization' in phase_names
            assert 'data_preparation' in phase_names
            assert 'strategy_execution' in phase_names
            assert 'api_integration' in phase_names
            assert 'monitoring' in phase_names
            assert 'cleanup' in phase_names
            
            # Verify directories created
            assert os.path.exists('data')
            assert os.path.exists('logs')
            assert os.path.exists('data/session')
            
        finally:
            os.chdir(original_dir)
    
    def test_config_with_orchestrator(self, test_env, temp_dir):
        """Test configuration manager with orchestrator."""
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create config manager
            config = ConfigManager()
            
            # Verify default config
            assert config.get('DRY_RUN') is True
            assert config.validate() is True
            
            # Create orchestrator with config
            orchestrator = SystemOrchestrator(
                dry_run=config.get('DRY_RUN')
            )
            
            results = orchestrator.run()
            assert results['status'] == 'success'
            
        finally:
            os.chdir(original_dir)
    
    def test_monitoring_with_orchestrator(self, test_env, temp_dir):
        """Test monitoring system with orchestrator."""
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create monitors
            slo_monitor = SLOMonitor()
            metrics_collector = MetricsCollector()
            
            # Run orchestrator
            orchestrator = SystemOrchestrator(dry_run=True)
            results = orchestrator.run()
            
            # Record SLO measurements
            success = results['status'] == 'success'
            slo_monitor.add_measurement('system_uptime', success=success)
            
            # Record metrics
            metrics_collector.record('execution_time', results['duration_seconds'])
            
            # Verify SLO status
            slo_status = slo_monitor.get_slo_status('system_uptime')
            assert slo_status['status'] in ['compliant', 'at_risk', 'breached']
            
            # Verify metrics
            metrics = metrics_collector.get_stats('execution_time')
            assert metrics['count'] == 1
            assert metrics['mean'] > 0
            
        finally:
            os.chdir(original_dir)
    
    def test_error_recovery(self, test_env, temp_dir):
        """Test error recovery mechanism."""
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            orchestrator = SystemOrchestrator(
                dry_run=True,
                enable_recovery=True
            )
            
            # System should handle errors gracefully
            results = orchestrator.run()
            
            # Even with potential errors, cleanup should run
            phase_names = [p['phase'] for p in results['phases']]
            assert 'cleanup' in phase_names
            
        finally:
            os.chdir(original_dir)


class TestComponentIntegration:
    """Test integration between components."""
    
    def test_adapter_with_config(self, mock_adapter):
        """Test adapter with configuration."""
        config = ConfigManager()
        
        # Create adapter with config values
        adapter = mock_adapter
        adapter.testnet = config.get('DRY_RUN', True)
        
        # Connect and test
        assert adapter.connect() is True
        assert adapter.health_check() is True
    
    def test_logging_with_config(self, test_env):
        """Test logging system with configuration."""
        from system.log_system.logger import configure_logging, get_logger, LogLevel
        
        config = ConfigManager()
        
        # Configure logging from config
        configure_logging(
            log_dir=config.get('LOG_DIR', 'logs'),
            level=LogLevel[config.get('LOG_LEVEL', 'INFO')],
            max_bytes=config.get('MAX_LOG_SIZE_MB', 10) * 1024 * 1024,
            backup_count=config.get('LOG_BACKUP_COUNT', 5)
        )
        
        # Test logging
        logger = get_logger(__name__)
        logger.info("Test log message")
        
        assert logger is not None
    
    def test_metrics_with_slo(self):
        """Test metrics collector with SLO monitor."""
        metrics = MetricsCollector()
        slo = SLOMonitor()
        
        # Record metrics
        for i in range(100):
            response_time = 100 + i
            metrics.record('api_response_time', response_time)
            
            # Check against SLO threshold
            success = response_time < 500  # 500ms threshold
            slo.add_measurement('api_response_time', success=success)
        
        # Verify both systems tracked correctly
        stats = metrics.get_stats('api_response_time')
        assert stats['count'] == 100
        
        slo_status = slo.get_slo_status('api_response_time')
        assert slo_status['total_measurements'] == 100


def test_end_to_end_scenario(test_env, temp_dir):
    """Test complete end-to-end scenario."""
    original_dir = os.getcwd()
    os.chdir(temp_dir)
    
    try:
        # 1. Initialize configuration
        config = ConfigManager()
        assert config.validate() is True
        
        # 2. Initialize monitoring
        slo_monitor = SLOMonitor()
        metrics = MetricsCollector()
        
        # 3. Run orchestrator
        orchestrator = SystemOrchestrator(
            dry_run=config.get('DRY_RUN'),
            enable_health_checks=True,
            enable_recovery=True
        )
        
        results = orchestrator.run()
        
        # 4. Record results in monitoring
        slo_monitor.add_measurement('system_uptime', success=results['status'] == 'success')
        metrics.record('total_duration', results['duration_seconds'])
        
        # 5. Generate summary
        slo_summary = slo_monitor.get_summary()
        metrics_summary = metrics.get_all_metrics()
        
        # Verify complete flow
        assert results['status'] == 'success'
        assert slo_summary['total_slos'] == 4
        assert 'total_duration' in metrics_summary
        
    finally:
        os.chdir(original_dir)
