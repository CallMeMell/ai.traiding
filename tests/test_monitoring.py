"""
test_monitoring.py - Monitoring System Tests
==========================================
Tests for SLO monitoring and metrics collection.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from system.monitoring.slo import SLOMonitor, SLODefinition, SLOStatus
from system.monitoring.metrics import MetricsCollector


class TestSLOMonitor:
    """Test SLO monitoring."""
    
    def test_slo_monitor_initialization(self):
        """Test SLO monitor initialization."""
        monitor = SLOMonitor()
        
        assert len(monitor.slos) == 4  # 4 standard SLOs
        assert 'system_uptime' in monitor.slos
        assert 'api_response_time' in monitor.slos
        assert 'trade_execution_time' in monitor.slos
        assert 'error_rate' in monitor.slos
    
    def test_add_measurement(self):
        """Test adding measurements."""
        monitor = SLOMonitor()
        
        # Add successful measurement
        monitor.add_measurement('system_uptime', success=True)
        
        measurements = monitor.measurements['system_uptime']
        assert len(measurements) == 1
        assert measurements[0]['success'] is True
    
    def test_get_slo_status_no_measurements(self):
        """Test SLO status with no measurements."""
        monitor = SLOMonitor()
        
        status = monitor.get_slo_status('system_uptime')
        
        assert status['status'] == SLOStatus.COMPLIANT.value
        assert status['total_measurements'] == 0
    
    def test_get_slo_status_compliant(self):
        """Test SLO status when compliant."""
        monitor = SLOMonitor()
        
        # Add measurements that meet SLO
        for _ in range(100):
            monitor.add_measurement('system_uptime', success=True)
        
        status = monitor.get_slo_status('system_uptime')
        
        assert status['status'] == SLOStatus.COMPLIANT.value
        assert status['current_percentage'] == 100.0
        assert status['total_measurements'] == 100
    
    def test_get_slo_status_breached(self):
        """Test SLO status when breached."""
        monitor = SLOMonitor()
        
        # Add measurements that breach SLO (only 90% success)
        for _ in range(90):
            monitor.add_measurement('system_uptime', success=True)
        for _ in range(10):
            monitor.add_measurement('system_uptime', success=False)
        
        status = monitor.get_slo_status('system_uptime')
        
        # Should be breached since 90% < 99.5% target
        assert status['status'] in [SLOStatus.AT_RISK.value, SLOStatus.BREACHED.value]
        assert status['current_percentage'] == 90.0
    
    def test_get_all_slo_status(self):
        """Test getting all SLO statuses."""
        monitor = SLOMonitor()
        
        all_status = monitor.get_all_slo_status()
        
        assert len(all_status) == 4
        assert all(isinstance(s, dict) for s in all_status)
    
    def test_get_summary(self):
        """Test getting SLO summary."""
        monitor = SLOMonitor()
        
        summary = monitor.get_summary()
        
        assert 'total_slos' in summary
        assert 'compliant' in summary
        assert 'at_risk' in summary
        assert 'breached' in summary
        assert 'overall_health' in summary
        assert summary['total_slos'] == 4
    
    def test_slo_definition(self):
        """Test SLO definition."""
        slo = SLODefinition(
            name="test_slo",
            description="Test SLO",
            target_percentage=99.0,
            window_days=7,
            error_budget_percentage=1.0
        )
        
        assert slo.name == "test_slo"
        assert slo.target_percentage == 99.0
        assert slo.window_days == 7


class TestMetricsCollector:
    """Test metrics collector."""
    
    def test_collector_initialization(self):
        """Test collector initialization."""
        collector = MetricsCollector()
        
        assert len(collector.metrics) == 0
    
    def test_record_metric(self):
        """Test recording a metric."""
        collector = MetricsCollector()
        
        collector.record('response_time', 100.5)
        
        assert 'response_time' in collector.metrics
        assert len(collector.metrics['response_time']) == 1
        assert collector.metrics['response_time'][0]['value'] == 100.5
    
    def test_record_with_tags(self):
        """Test recording with tags."""
        collector = MetricsCollector()
        
        collector.record('response_time', 100.5, tags={'endpoint': '/api/v1'})
        
        metric = collector.metrics['response_time'][0]
        assert metric['tags']['endpoint'] == '/api/v1'
    
    def test_get_stats(self):
        """Test getting statistics."""
        collector = MetricsCollector()
        
        # Record multiple values
        for value in [10, 20, 30, 40, 50]:
            collector.record('response_time', value)
        
        stats = collector.get_stats('response_time')
        
        assert stats['count'] == 5
        assert stats['mean'] == 30.0
        assert stats['min'] == 10
        assert stats['max'] == 50
        assert stats['p50'] == 30
    
    def test_get_stats_no_data(self):
        """Test getting stats for non-existent metric."""
        collector = MetricsCollector()
        
        stats = collector.get_stats('nonexistent')
        
        assert stats['count'] == 0
        assert stats['mean'] == 0
    
    def test_get_all_metrics(self):
        """Test getting all metrics."""
        collector = MetricsCollector()
        
        collector.record('metric1', 100)
        collector.record('metric2', 200)
        
        all_metrics = collector.get_all_metrics()
        
        assert 'metric1' in all_metrics
        assert 'metric2' in all_metrics
    
    def test_clear_specific_metric(self):
        """Test clearing a specific metric."""
        collector = MetricsCollector()
        
        collector.record('metric1', 100)
        collector.record('metric2', 200)
        
        collector.clear('metric1')
        
        assert len(collector.metrics['metric1']) == 0
        assert len(collector.metrics['metric2']) == 1
    
    def test_clear_all_metrics(self):
        """Test clearing all metrics."""
        collector = MetricsCollector()
        
        collector.record('metric1', 100)
        collector.record('metric2', 200)
        
        collector.clear()
        
        assert len(collector.metrics) == 0
