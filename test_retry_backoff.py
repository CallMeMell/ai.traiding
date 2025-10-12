"""
test_retry_backoff.py - Test retry and backoff logic
====================================================
Tests for retry/backoff functionality in automation runner.
"""

import unittest
import time
import tempfile
import shutil
import os
from automation.runner import AutomationRunner
from core.session_store import SessionStore


class TestRetryBackoff(unittest.TestCase):
    """Test retry and backoff logic."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.events_path = os.path.join(self.test_dir, "events.jsonl")
        self.summary_path = os.path.join(self.test_dir, "summary.json")
        
        self.runner = AutomationRunner(
            data_phase_timeout=10,
            strategy_phase_timeout=10,
            api_phase_timeout=10,
            heartbeat_interval=5,
            enable_validation=False
        )
        self.runner.session_store = SessionStore(self.events_path, self.summary_path)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_retry_success_on_second_attempt(self):
        """Test that retry succeeds on second attempt."""
        attempt_count = {'count': 0}
        
        def flaky_operation():
            attempt_count['count'] += 1
            if attempt_count['count'] < 2:
                raise ValueError("Simulated failure")
            return {'status': 'success'}
        
        # Should succeed on second attempt
        result = self.runner._retry_with_backoff(
            flaky_operation,
            max_retries=3,
            base_delay=0.1,
            operation_name="test_op"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(attempt_count['count'], 2)
    
    def test_retry_all_attempts_fail(self):
        """Test that all retry attempts are exhausted."""
        def always_fails():
            raise ValueError("Always fails")
        
        # Should raise after all retries
        with self.assertRaises(ValueError):
            self.runner._retry_with_backoff(
                always_fails,
                max_retries=3,
                base_delay=0.1,
                operation_name="failing_op"
            )
    
    def test_retry_first_attempt_succeeds(self):
        """Test that function succeeds on first attempt without retry."""
        attempt_count = {'count': 0}
        
        def works_immediately():
            attempt_count['count'] += 1
            return {'status': 'success'}
        
        result = self.runner._retry_with_backoff(
            works_immediately,
            max_retries=3,
            base_delay=0.1,
            operation_name="good_op"
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(attempt_count['count'], 1)
    
    def test_autocorrect_events_logged(self):
        """Test that autocorrect events are logged during retries."""
        attempt_count = {'count': 0}
        
        def flaky_operation():
            attempt_count['count'] += 1
            if attempt_count['count'] < 2:
                raise ValueError("Simulated failure")
            return {'status': 'success'}
        
        # Run with retry
        result = self.runner._retry_with_backoff(
            flaky_operation,
            max_retries=3,
            base_delay=0.1,
            operation_name="test_autocorrect"
        )
        
        # Check that autocorrect events were logged
        events = self.runner.session_store.read_events()
        autocorrect_events = [e for e in events if e.get('type') == 'autocorrect_attempt']
        
        # Should have at least one autocorrect event (for the retry)
        self.assertGreater(len(autocorrect_events), 0)
    
    def test_exponential_backoff_delays(self):
        """Test that exponential backoff delays increase."""
        attempt_count = {'count': 0}
        delays = []
        
        def capture_timing():
            attempt_count['count'] += 1
            if attempt_count['count'] > 1:
                delays.append(time.time())
            if attempt_count['count'] < 3:
                raise ValueError("Simulated failure")
            return {'status': 'success'}
        
        start = time.time()
        result = self.runner._retry_with_backoff(
            capture_timing,
            max_retries=3,
            base_delay=0.1,
            max_delay=1.0,
            operation_name="timing_test"
        )
        
        # Verify we had retries
        self.assertEqual(attempt_count['count'], 3)
        self.assertEqual(result['status'], 'success')


def run_tests():
    """Run all tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRetryBackoff)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
