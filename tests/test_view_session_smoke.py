"""
test_view_session_smoke.py - View Session Smoke Tests
====================================================
Smoke tests to verify session viewing functionality works.
"""

import pytest
import sys
import os
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.session_store import SessionStore


class TestViewSessionSmoke:
    """Smoke tests for view session functionality."""
    
    @pytest.fixture
    def temp_session_dir(self):
        """Create temporary session directory with test data."""
        temp_dir = tempfile.mkdtemp()
        
        # Create test session data
        events_path = os.path.join(temp_dir, "events.jsonl")
        summary_path = os.path.join(temp_dir, "summary.json")
        
        store = SessionStore(events_path, summary_path)
        
        # Add test events
        test_events = [
            {
                'timestamp': datetime.now().isoformat(),
                'type': 'session_start',
                'session_id': 'TEST123',
                'level': 'info',
                'message': 'Session started'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'type': 'phase_start',
                'phase': 'data_phase',
                'session_id': 'TEST123',
                'level': 'info',
                'message': 'Data phase started'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'type': 'checkpoint',
                'phase': 'data_phase',
                'session_id': 'TEST123',
                'level': 'info',
                'message': 'Data collected',
                'metrics': {'equity': 10100.0, 'pnl': 100.0}
            },
        ]
        
        for event in test_events:
            store.append_event(event)
        
        # Add test summary
        test_summary = {
            'session_id': 'TEST123',
            'session_start': datetime.now().isoformat(),
            'initial_capital': 10000.0,
            'current_equity': 10100.0,
            'total_trades': 5,
            'winning_trades': 3,
            'losing_trades': 2
        }
        store.write_summary(test_summary)
        
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_view_session_initialization(self, temp_session_dir):
        """Test session view can be initialized."""
        events_path = os.path.join(temp_session_dir, "events.jsonl")
        summary_path = os.path.join(temp_session_dir, "summary.json")
        
        store = SessionStore(events_path, summary_path)
        
        assert store is not None
        assert os.path.exists(events_path)
        assert os.path.exists(summary_path)
    
    def test_view_session_reads_events(self, temp_session_dir):
        """Test session view can read events."""
        events_path = os.path.join(temp_session_dir, "events.jsonl")
        summary_path = os.path.join(temp_session_dir, "summary.json")
        
        store = SessionStore(events_path, summary_path)
        events = store.read_events()
        
        assert len(events) > 0
        assert events[0]['type'] == 'session_start'
        assert events[0]['session_id'] == 'TEST123'
    
    def test_view_session_reads_summary(self, temp_session_dir):
        """Test session view can read summary."""
        events_path = os.path.join(temp_session_dir, "events.jsonl")
        summary_path = os.path.join(temp_session_dir, "summary.json")
        
        store = SessionStore(events_path, summary_path)
        summary = store.read_summary()
        
        assert summary is not None
        assert summary['session_id'] == 'TEST123'
        assert summary['initial_capital'] == 10000.0
        assert summary['current_equity'] == 10100.0
    
    def test_view_session_calculates_metrics(self, temp_session_dir):
        """Test session view can calculate metrics."""
        events_path = os.path.join(temp_session_dir, "events.jsonl")
        summary_path = os.path.join(temp_session_dir, "summary.json")
        
        store = SessionStore(events_path, summary_path)
        summary = store.read_summary()
        
        # Verify metrics calculations
        assert summary['total_trades'] == 5
        assert summary['winning_trades'] == 3
        assert summary['losing_trades'] == 2
        
        # Calculate win rate
        win_rate = (summary['winning_trades'] / summary['total_trades']) * 100
        assert win_rate == 60.0
    
    def test_view_session_renders_without_error(self, temp_session_dir):
        """Test session view renders data without errors."""
        events_path = os.path.join(temp_session_dir, "events.jsonl")
        summary_path = os.path.join(temp_session_dir, "summary.json")
        
        store = SessionStore(events_path, summary_path)
        
        # Simulate rendering by reading data
        events = store.read_events()
        summary = store.read_summary()
        
        # Verify we can access key fields for rendering
        assert len(events) > 0
        assert summary is not None
        
        # Verify event fields are accessible
        for event in events:
            assert 'timestamp' in event
            assert 'type' in event
        
        # Verify summary fields are accessible
        assert 'session_id' in summary
        assert 'session_start' in summary
    
    def test_view_session_filters_by_type(self, temp_session_dir):
        """Test session view can filter events by type."""
        events_path = os.path.join(temp_session_dir, "events.jsonl")
        summary_path = os.path.join(temp_session_dir, "summary.json")
        
        store = SessionStore(events_path, summary_path)
        events = store.read_events()
        
        # Filter by type
        session_start_events = [e for e in events if e['type'] == 'session_start']
        phase_start_events = [e for e in events if e['type'] == 'phase_start']
        
        assert len(session_start_events) == 1
        assert len(phase_start_events) == 1
    
    def test_view_session_filters_by_phase(self, temp_session_dir):
        """Test session view can filter events by phase."""
        events_path = os.path.join(temp_session_dir, "events.jsonl")
        summary_path = os.path.join(temp_session_dir, "summary.json")
        
        store = SessionStore(events_path, summary_path)
        events = store.read_events()
        
        # Filter by phase
        data_phase_events = [e for e in events if e.get('phase') == 'data_phase']
        
        assert len(data_phase_events) == 2
    
    def test_view_session_roi_calculation(self):
        """Test ROI calculation for session view."""
        store = SessionStore()
        
        initial_capital = 10000.0
        current_equity = 10500.0
        
        roi = store.calculate_roi(initial_capital, current_equity)
        
        # ROI should be 5%
        assert abs(roi - 5.0) < 0.01
    
    def test_view_session_empty_data_handling(self):
        """Test session view handles empty data gracefully."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            events_path = os.path.join(temp_dir, "empty_events.jsonl")
            summary_path = os.path.join(temp_dir, "empty_summary.json")
            
            store = SessionStore(events_path, summary_path)
            
            # Should not crash when reading empty data
            events = store.read_events()
            summary = store.read_summary()
            
            assert events == []
            assert summary is None
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
