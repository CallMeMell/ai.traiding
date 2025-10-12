"""
test_validation_integration.py - Integration Tests for Schema Validation
========================================================================
Tests to verify that validation is properly integrated into the workflow.
"""

import unittest
import os
import tempfile
import shutil
import json
from datetime import datetime

from core.session_store import SessionStore
from automation.runner import AutomationRunner
from automation.validate import validate_event_lenient, validate_summary_lenient


class TestValidationIntegration(unittest.TestCase):
    """Test that validation is properly integrated."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.events_path = os.path.join(self.test_dir, "events.jsonl")
        self.summary_path = os.path.join(self.test_dir, "summary.json")
        self.store = SessionStore(self.events_path, self.summary_path)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_validation_enabled_by_default_in_runner(self):
        """Test that AutomationRunner has validation enabled by default."""
        runner = AutomationRunner()
        self.assertTrue(runner.enable_validation, 
                       "Validation should be enabled by default in AutomationRunner")
    
    def test_session_store_validates_by_default(self):
        """Test that SessionStore validates events by default."""
        # Try to append an invalid event
        invalid_event = {
            'type': 'test_event'
            # Missing required 'timestamp' field
        }
        
        # Should add timestamp automatically, then validate
        self.store.append_event(invalid_event)  # Should use default validate=True
        
        # Event should be written (lenient validation warns but doesn't fail)
        events = self.store.read_events()
        self.assertEqual(len(events), 1)
        self.assertIn('timestamp', events[0])
    
    def test_invalid_events_are_logged(self):
        """Test that invalid events generate warnings but are still written."""
        # Write a completely invalid event with explicit validation
        invalid_event = {
            'timestamp': 'not-a-valid-timestamp',
            'type': 'test_event'
        }
        
        # With lenient validation, this should warn but still write
        self.store.append_event(invalid_event, validate=True)
        
        events = self.store.read_events()
        self.assertEqual(len(events), 1)
    
    def test_valid_events_pass_validation(self):
        """Test that valid events pass validation."""
        valid_event = {
            'timestamp': datetime.now().isoformat(),
            'type': 'test_event',
            'level': 'info',
            'message': 'Test message'
        }
        
        self.store.append_event(valid_event, validate=True)
        
        events = self.store.read_events()
        self.assertEqual(len(events), 1)
        
        # Verify event validates
        validated = validate_event_lenient(events[0])
        self.assertIsNotNone(validated)
    
    def test_summary_validation_integration(self):
        """Test that summary validation works correctly."""
        valid_summary = {
            'session_start': datetime.now().isoformat(),
            'status': 'running',
            'phases_completed': 1,
            'initial_capital': 10000.0,
            'current_equity': 10100.0
        }
        
        self.store.write_summary(valid_summary, validate=True)
        
        summary = self.store.read_summary()
        self.assertIsNotNone(summary)
        
        # Verify summary validates
        validated = validate_summary_lenient(summary)
        self.assertIsNotNone(validated)
    
    def test_runner_with_validation_completes_successfully(self):
        """Test that runner completes successfully with validation enabled."""
        runner = AutomationRunner(
            data_phase_timeout=5,
            strategy_phase_timeout=5,
            api_phase_timeout=5,
            heartbeat_interval=1,
            enable_validation=True  # Explicitly enable (though it's default now)
        )
        runner.session_store = self.store
        
        result = runner.run()
        
        self.assertEqual(result['status'], 'success')
        
        # All events should be valid
        events = self.store.read_events()
        valid_count = 0
        for event in events:
            if validate_event_lenient(event):
                valid_count += 1
        
        # All events should validate
        self.assertEqual(valid_count, len(events),
                        "All generated events should pass validation")
    
    def test_erroneous_entries_excluded_by_lenient_validator(self):
        """Test that truly erroneous entries are excluded by lenient validator."""
        # Create an event that will definitely fail validation
        bad_event = {
            'timestamp': 'completely-invalid-timestamp-format',
            'type': 'test'
        }
        
        validated = validate_event_lenient(bad_event)
        self.assertIsNone(validated, 
                         "Lenient validator should return None for invalid data")
    
    def test_mixed_valid_invalid_events(self):
        """Test handling of mixed valid and invalid events."""
        # Write some valid and invalid events
        valid_event = {
            'timestamp': datetime.now().isoformat(),
            'type': 'valid_event'
        }
        
        self.store.append_event(valid_event)
        
        # Manually add an invalid event to the file
        with open(self.events_path, 'a') as f:
            f.write('{"timestamp": "invalid", "type": "bad_event"}\n')
        
        # Read all events
        events = self.store.read_events()
        self.assertEqual(len(events), 2)
        
        # Filter with lenient validation
        valid_events = [e for e in events if validate_event_lenient(e)]
        
        # Only the valid event should pass
        self.assertEqual(len(valid_events), 1)
        self.assertEqual(valid_events[0]['type'], 'valid_event')


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestValidationIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
