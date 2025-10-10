"""
test_smoke_automation.py - Smoke Test for Automation Runner
==========================================================
Smoke test to verify the automation runner works end-to-end.
"""

import unittest
import os
import tempfile
import shutil
from automation.runner import AutomationRunner
from core.session_store import SessionStore
from automation.validate import validate_event_lenient, validate_summary_lenient


class TestSmokeAutomation(unittest.TestCase):
    """Smoke test for automation runner."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.events_path = os.path.join(self.test_dir, "events.jsonl")
        self.summary_path = os.path.join(self.test_dir, "summary.json")
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_runner_dry_run(self):
        """Test runner executes successfully in dry-run mode."""
        # Create runner with short timeouts
        store = SessionStore(self.events_path, self.summary_path)
        runner = AutomationRunner(
            data_phase_timeout=10,
            strategy_phase_timeout=10,
            api_phase_timeout=10,
            heartbeat_interval=2,
            enable_validation=True
        )
        runner.session_store = store
        
        # Run
        result = runner.run()
        
        # Verify result
        self.assertEqual(result['status'], 'success')
        self.assertIn('duration_seconds', result)
        self.assertGreater(result['duration_seconds'], 0)
    
    def test_events_generated(self):
        """Test that events are generated."""
        # Create runner
        store = SessionStore(self.events_path, self.summary_path)
        runner = AutomationRunner(
            data_phase_timeout=10,
            strategy_phase_timeout=10,
            api_phase_timeout=10,
            heartbeat_interval=2,
            enable_validation=True
        )
        runner.session_store = store
        
        # Run
        runner.run()
        
        # Read events
        events = store.read_events()
        
        # Verify events exist and are not empty
        self.assertGreater(len(events), 0)
        
        # Verify essential event types exist
        event_types = [e.get('type') for e in events]
        self.assertIn('runner_start', event_types)
        self.assertIn('runner_end', event_types)
        self.assertIn('phase_start', event_types)
        self.assertIn('phase_end', event_types)
        self.assertIn('heartbeat', event_types)
    
    def test_summary_generated(self):
        """Test that summary is generated."""
        # Create runner
        store = SessionStore(self.events_path, self.summary_path)
        runner = AutomationRunner(
            data_phase_timeout=10,
            strategy_phase_timeout=10,
            api_phase_timeout=10,
            heartbeat_interval=2,
            enable_validation=True
        )
        runner.session_store = store
        
        # Run
        runner.run()
        
        # Read summary
        summary = store.read_summary()
        
        # Verify summary exists and is not empty
        self.assertIsNotNone(summary)
        self.assertIn('session_start', summary)
        self.assertIn('session_end', summary)
        self.assertIn('status', summary)
        self.assertEqual(summary['status'], 'success')
        self.assertIn('roi', summary)
    
    def test_events_validate(self):
        """Test that events pass validation."""
        # Create runner
        store = SessionStore(self.events_path, self.summary_path)
        runner = AutomationRunner(
            data_phase_timeout=10,
            strategy_phase_timeout=10,
            api_phase_timeout=10,
            heartbeat_interval=2,
            enable_validation=True
        )
        runner.session_store = store
        
        # Run
        runner.run()
        
        # Read and validate events
        events = store.read_events()
        
        valid_count = 0
        for event in events:
            validated = validate_event_lenient(event)
            if validated:
                valid_count += 1
        
        # At least 80% of events should validate
        self.assertGreater(valid_count / len(events), 0.8)
    
    def test_summary_validates(self):
        """Test that summary passes validation."""
        # Create runner
        store = SessionStore(self.events_path, self.summary_path)
        runner = AutomationRunner(
            data_phase_timeout=10,
            strategy_phase_timeout=10,
            api_phase_timeout=10,
            heartbeat_interval=2,
            enable_validation=True
        )
        runner.session_store = store
        
        # Run
        runner.run()
        
        # Read and validate summary
        summary = store.read_summary()
        validated = validate_summary_lenient(summary)
        
        self.assertIsNotNone(validated)
    
    def test_no_secrets_required(self):
        """Test that runner works without API keys (DRY_RUN mode)."""
        # Create runner without setting API keys
        store = SessionStore(self.events_path, self.summary_path)
        runner = AutomationRunner(
            data_phase_timeout=10,
            strategy_phase_timeout=10,
            api_phase_timeout=10,
            heartbeat_interval=2,
            enable_validation=False
        )
        runner.session_store = store
        
        # Run should complete successfully without secrets
        result = runner.run()
        
        # Runner should complete (may have warnings about missing keys, but not fail)
        self.assertIn(result['status'], ['success', 'warning'])


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestSmokeAutomation))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
