"""
test_orchestrator_recovery.py - Test orchestrator recovery logic
===============================================================
Tests for recovery/retry functionality in system orchestrator.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from system.orchestrator import SystemOrchestrator, SystemPhase


class TestOrchestratorRecovery(unittest.TestCase):
    """Test orchestrator recovery logic."""
    
    def setUp(self):
        """Set up test environment."""
        self.orchestrator = SystemOrchestrator(
            dry_run=True,
            enable_health_checks=False,
            enable_recovery=True
        )
    
    def test_recovery_has_retry_logic(self):
        """Test that recovery attempts retry with backoff."""
        # Simulate a failed phase
        error = Exception("Simulated phase failure")
        result = self.orchestrator._attempt_recovery(SystemPhase.DATA, error)
        
        # Verify recovery was attempted
        self.assertTrue(result['attempted'])
        self.assertIn('attempts', result)
        self.assertIsInstance(result['attempts'], list)
        
        # Should have made multiple attempts (up to max_retries=3)
        self.assertGreater(len(result['attempts']), 0)
        self.assertLessEqual(len(result['attempts']), 3)
    
    def test_recovery_logs_each_attempt(self):
        """Test that each recovery attempt is logged."""
        error = Exception("Test error")
        result = self.orchestrator._attempt_recovery(SystemPhase.STRATEGY, error)
        
        # Check that attempts have required fields
        for attempt in result['attempts']:
            self.assertIn('attempt', attempt)
            self.assertIn('delay', attempt)
            self.assertIn('status', attempt)
    
    def test_recovery_exponential_backoff(self):
        """Test that delays increase exponentially."""
        error = Exception("Test error")
        result = self.orchestrator._attempt_recovery(SystemPhase.API, error)
        
        # Check delays increase (base_delay=2, so 2, 4, 8...)
        attempts = result['attempts']
        if len(attempts) > 1:
            # Verify delays are increasing
            delays = [a['delay'] for a in attempts]
            for i in range(len(delays) - 1):
                # Each delay should be at least as large as previous (exponential)
                self.assertGreaterEqual(delays[i + 1], delays[i])
    
    def test_recovery_respects_max_delay(self):
        """Test that delay doesn't exceed maximum."""
        error = Exception("Test error")
        result = self.orchestrator._attempt_recovery(SystemPhase.MONITORING, error)
        
        # Check that no delay exceeds max_delay (30 seconds)
        for attempt in result['attempts']:
            self.assertLessEqual(attempt['delay'], 30)
    
    def test_recovery_includes_error_info(self):
        """Test that recovery result includes error information."""
        error = Exception("Original error message")
        result = self.orchestrator._attempt_recovery(SystemPhase.INIT, error)
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], "Original error message")


def run_tests():
    """Run all tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOrchestratorRecovery)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
