"""
test_runner_smoke.py - Automation Runner Smoke Tests
===================================================
Smoke tests to verify automation runner works end-to-end in DRY_RUN mode.
"""

import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from automation.runner import AutomationRunner
from core.session_store import SessionStore


class TestRunnerSmoke:
    """Smoke tests for automation runner."""
    
    @pytest.fixture
    def temp_session_dir(self):
        """Create temporary session directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_runner_initialization(self):
        """Test runner initializes successfully."""
        runner = AutomationRunner(
            data_phase_timeout=10,
            strategy_phase_timeout=10,
            api_phase_timeout=10,
            heartbeat_interval=2,
            enable_validation=True
        )
        
        assert runner is not None
        assert runner.session_id is not None
        assert runner.data_phase_timeout == 10
        assert runner.strategy_phase_timeout == 10
        assert runner.api_phase_timeout == 10
        assert runner.heartbeat_interval == 2
        assert runner.enable_validation is True
    
    def test_runner_smoke_dry_run(self, temp_session_dir):
        """Test runner executes successfully in dry-run mode."""
        # Set DRY_RUN environment
        os.environ['DRY_RUN'] = 'true'
        
        # Create runner with short timeouts for smoke test
        events_path = os.path.join(temp_session_dir, "events.jsonl")
        summary_path = os.path.join(temp_session_dir, "summary.json")
        store = SessionStore(events_path, summary_path)
        
        runner = AutomationRunner(
            data_phase_timeout=5,
            strategy_phase_timeout=5,
            api_phase_timeout=5,
            heartbeat_interval=1,
            enable_validation=True
        )
        runner.session_store = store
        
        # Run should complete without errors
        results = runner.run()
        
        assert results is not None
        assert 'status' in results
        assert 'phases' in results
    
    def test_runner_generates_events(self, temp_session_dir):
        """Test that runner generates events."""
        os.environ['DRY_RUN'] = 'true'
        
        events_path = os.path.join(temp_session_dir, "events.jsonl")
        summary_path = os.path.join(temp_session_dir, "summary.json")
        store = SessionStore(events_path, summary_path)
        
        runner = AutomationRunner(
            data_phase_timeout=5,
            strategy_phase_timeout=5,
            api_phase_timeout=5,
            heartbeat_interval=1,
            enable_validation=True
        )
        runner.session_store = store
        
        runner.run()
        
        # Check events were generated
        events = store.read_events()
        assert len(events) > 0
        
        # Verify essential event types
        event_types = [e.get('type') for e in events]
        assert 'runner_start' in event_types
        assert 'runner_end' in event_types
    
    def test_runner_generates_summary(self, temp_session_dir):
        """Test that runner generates summary."""
        os.environ['DRY_RUN'] = 'true'
        
        events_path = os.path.join(temp_session_dir, "events.jsonl")
        summary_path = os.path.join(temp_session_dir, "summary.json")
        store = SessionStore(events_path, summary_path)
        
        runner = AutomationRunner(
            data_phase_timeout=5,
            strategy_phase_timeout=5,
            api_phase_timeout=5,
            heartbeat_interval=1,
            enable_validation=True
        )
        runner.session_store = store
        
        runner.run()
        
        # Check summary was generated
        summary = store.read_summary()
        assert summary is not None
        assert 'session_id' in summary
        assert 'session_start' in summary
    
    def test_runner_no_secrets_required(self):
        """Test that runner works without API keys in DRY_RUN mode."""
        # Clear any API keys from environment
        for key in ['BINANCE_API_KEY', 'BINANCE_SECRET_KEY', 
                    'BINANCE_TESTNET_API_KEY', 'BINANCE_TESTNET_SECRET_KEY']:
            if key in os.environ:
                del os.environ[key]
        
        os.environ['DRY_RUN'] = 'true'
        
        # Should not raise any errors about missing API keys
        runner = AutomationRunner(
            data_phase_timeout=5,
            strategy_phase_timeout=5,
            api_phase_timeout=5,
            heartbeat_interval=1,
            enable_validation=True
        )
        
        assert runner is not None
        assert runner.session_id is not None
    
    def test_runner_session_id_unique(self):
        """Test that each runner instance has a unique session ID."""
        runner1 = AutomationRunner()
        runner2 = AutomationRunner()
        
        assert runner1.session_id != runner2.session_id
    
    def test_runner_with_validation_disabled(self):
        """Test runner can be initialized with validation disabled."""
        runner = AutomationRunner(
            data_phase_timeout=10,
            strategy_phase_timeout=10,
            api_phase_timeout=10,
            heartbeat_interval=2,
            enable_validation=False
        )
        
        assert runner.enable_validation is False
