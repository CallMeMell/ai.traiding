"""
test_slo_monitor.py - Tests for Automation SLO Monitor
=====================================================
Tests for SLO monitoring with needs-review event generation.
"""

import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from automation.slo_monitor import SLOMonitor
from core.session_store import SessionStore
from system.monitoring.slo import SLOStatus


class TestSLOMonitor:
    """Test automation SLO monitor."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for session store."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def session_store(self, temp_dir):
        """Create session store in temp directory."""
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        store = SessionStore()
        yield store
        os.chdir(original_dir)
    
    def test_initialization(self, session_store):
        """Test SLO monitor initialization."""
        monitor = SLOMonitor(session_store=session_store)
        
        assert monitor.error_rate_threshold == 0.01
        assert monitor.render_time_threshold_ms == 500.0
        assert monitor.session_store == session_store
    
    def test_custom_thresholds(self, session_store):
        """Test initialization with custom thresholds."""
        monitor = SLOMonitor(
            error_rate_threshold=0.05,
            render_time_threshold_ms=1000.0,
            session_store=session_store
        )
        
        assert monitor.error_rate_threshold == 0.05
        assert monitor.render_time_threshold_ms == 1000.0
    
    def test_set_error_rate_threshold(self, session_store):
        """Test setting error rate threshold."""
        monitor = SLOMonitor(session_store=session_store)
        
        monitor.error_rate_threshold = 0.05
        assert monitor.error_rate_threshold == 0.05
    
    def test_invalid_error_rate_threshold(self, session_store):
        """Test invalid error rate threshold."""
        monitor = SLOMonitor(session_store=session_store)
        
        with pytest.raises(ValueError):
            monitor.error_rate_threshold = 1.5
        
        with pytest.raises(ValueError):
            monitor.error_rate_threshold = -0.1
    
    def test_set_render_time_threshold(self, session_store):
        """Test setting render time threshold."""
        monitor = SLOMonitor(session_store=session_store)
        
        monitor.render_time_threshold_ms = 1000.0
        assert monitor.render_time_threshold_ms == 1000.0
    
    def test_invalid_render_time_threshold(self, session_store):
        """Test invalid render time threshold."""
        monitor = SLOMonitor(session_store=session_store)
        
        with pytest.raises(ValueError):
            monitor.render_time_threshold_ms = -100
    
    def test_add_error_measurement(self, session_store):
        """Test adding error measurements."""
        monitor = SLOMonitor(session_store=session_store)
        
        monitor.add_error_measurement(success=True)
        monitor.add_error_measurement(success=False)
        
        # Verify measurements were added to base monitor
        measurements = monitor.base_monitor.measurements['error_rate']
        assert len(measurements) == 2
    
    def test_add_render_time_measurement(self, session_store):
        """Test adding render time measurements."""
        monitor = SLOMonitor(session_store=session_store)
        
        # Add measurement under threshold (success)
        monitor.add_render_time_measurement(300.0)
        
        # Add measurement over threshold (failure)
        monitor.add_render_time_measurement(800.0)
        
        # Verify measurements were added
        measurements = monitor.base_monitor.measurements['api_response_time']
        assert len(measurements) == 2
        assert measurements[0]['success'] is True
        assert measurements[1]['success'] is False
    
    def test_check_error_rate_compliant(self, session_store):
        """Test error rate check when compliant."""
        monitor = SLOMonitor(session_store=session_store)
        
        # Add measurements that meet SLO (100% success)
        for _ in range(100):
            monitor.add_error_measurement(success=True)
        
        status = monitor.check_error_rate()
        
        assert status['status'] == SLOStatus.COMPLIANT.value
        assert status['current_percentage'] == 100.0
    
    def test_check_error_rate_breached(self, temp_dir, session_store):
        """Test error rate check when breached."""
        monitor = SLOMonitor(session_store=session_store)
        
        # Add measurements that breach SLO (only 90% success)
        for _ in range(90):
            monitor.add_error_measurement(success=True)
        for _ in range(10):
            monitor.add_error_measurement(success=False)
        
        status = monitor.check_error_rate()
        
        # Should be breached or at risk since 90% < 99% target
        assert status['status'] in [SLOStatus.AT_RISK.value, SLOStatus.BREACHED.value]
        assert status['current_percentage'] == 90.0
        
        # Verify needs-review event was generated
        events = session_store.read_events()
        needs_review_events = [e for e in events if e.get('type') == 'needs-review']
        assert len(needs_review_events) > 0
        
        # Check event details
        event = needs_review_events[0]
        assert event['details']['slo_name'] == 'error_rate'
        assert event['details']['status'] in [SLOStatus.AT_RISK.value, SLOStatus.BREACHED.value]
    
    def test_check_render_time_compliant(self, session_store):
        """Test render time check when compliant."""
        monitor = SLOMonitor(session_store=session_store)
        
        # Add measurements under threshold (all successful)
        for _ in range(100):
            monitor.add_render_time_measurement(300.0)
        
        status = monitor.check_render_time()
        
        assert status['status'] == SLOStatus.COMPLIANT.value
        assert status['current_percentage'] == 100.0
    
    def test_check_render_time_breached(self, temp_dir, session_store):
        """Test render time check when breached."""
        monitor = SLOMonitor(session_store=session_store)
        
        # Add measurements that breach SLO (many over threshold)
        for _ in range(90):
            monitor.add_render_time_measurement(300.0)  # Under threshold
        for _ in range(10):
            monitor.add_render_time_measurement(1000.0)  # Over threshold
        
        status = monitor.check_render_time()
        
        # Should be at risk or breached since 90% < 95% target
        assert status['status'] in [SLOStatus.AT_RISK.value, SLOStatus.BREACHED.value]
        
        # Verify needs-review event was generated
        events = session_store.read_events()
        needs_review_events = [e for e in events if e.get('type') == 'needs-review']
        assert len(needs_review_events) > 0
        
        # Check event details
        event = needs_review_events[0]
        assert event['details']['slo_name'] == 'render_time'
    
    def test_get_all_status(self, session_store):
        """Test getting all SLO status."""
        monitor = SLOMonitor(session_store=session_store)
        
        # Add some measurements
        monitor.add_error_measurement(success=True)
        monitor.add_render_time_measurement(300.0)
        
        all_status = monitor.get_all_status()
        
        assert 'error_rate' in all_status
        assert 'render_time' in all_status
        assert all_status['error_rate']['status'] == SLOStatus.COMPLIANT.value
        assert all_status['render_time']['status'] == SLOStatus.COMPLIANT.value
    
    def test_multiple_needs_review_events(self, temp_dir, session_store):
        """Test generating multiple needs-review events."""
        monitor = SLOMonitor(session_store=session_store)
        
        # Breach both SLOs
        for _ in range(85):
            monitor.add_error_measurement(success=True)
            monitor.add_render_time_measurement(300.0)
        for _ in range(15):
            monitor.add_error_measurement(success=False)
            monitor.add_render_time_measurement(1000.0)
        
        # Check both
        monitor.check_error_rate()
        monitor.check_render_time()
        
        # Verify both events were generated
        events = session_store.read_events()
        needs_review_events = [e for e in events if e.get('type') == 'needs-review']
        assert len(needs_review_events) >= 2
        
        slo_names = [e['details']['slo_name'] for e in needs_review_events]
        assert 'error_rate' in slo_names
        assert 'render_time' in slo_names
