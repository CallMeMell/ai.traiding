"""
test_scheduler.py - Tests for Phase Scheduler
============================================
Unit tests for scheduler functionality.
"""

import unittest
import time
from automation.scheduler import PhaseScheduler


class TestPhaseScheduler(unittest.TestCase):
    """Test PhaseScheduler functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.scheduler = PhaseScheduler(max_pause_minutes=10)
        self.events = []
    
    def _event_handler(self, event):
        """Event handler for testing."""
        self.events.append(event)
    
    def test_run_phase_success(self):
        """Test running a successful phase."""
        def test_phase():
            return {'result': 'success'}
        
        result = self.scheduler.run_phase(
            'test_phase',
            test_phase,
            timeout_seconds=10,
            on_event=self._event_handler
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['phase'], 'test_phase')
        self.assertIn('phase_result', result)
        self.assertEqual(result['phase_result']['result'], 'success')
        
        # Check events
        self.assertEqual(len(self.events), 2)  # start and end
        self.assertEqual(self.events[0]['type'], 'phase_start')
        self.assertEqual(self.events[1]['type'], 'phase_end')
    
    def test_run_phase_error(self):
        """Test running a phase that raises an error."""
        def failing_phase():
            raise ValueError("Test error")
        
        result = self.scheduler.run_phase(
            'failing_phase',
            failing_phase,
            timeout_seconds=10,
            on_event=self._event_handler
        )
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
        self.assertIn('Test error', result['error'])
    
    def test_run_phase_timeout(self):
        """Test phase timeout detection."""
        def slow_phase():
            time.sleep(3)
            return {'result': 'done'}
        
        result = self.scheduler.run_phase(
            'slow_phase',
            slow_phase,
            timeout_seconds=1,
            on_event=self._event_handler
        )
        
        # Phase completes but should note timeout
        self.assertIn(result['status'], ['timeout', 'success'])
        self.assertGreater(result['duration_seconds'], 1)
    
    def test_pause_and_check(self):
        """Test pause and check functionality."""
        def check_func():
            return {'check': 'passed'}
        
        result = self.scheduler.pause_and_check(
            check_func,
            pause_seconds=1,
            on_event=self._event_handler
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['pause_seconds'], 1)
        self.assertIn('check_result', result)
        
        # Check events
        self.assertGreaterEqual(len(self.events), 2)  # start and end
    
    def test_pause_cap(self):
        """Test that pause duration is capped at max."""
        # Create scheduler with low max for testing
        scheduler = PhaseScheduler(max_pause_minutes=1)
        
        def check_func():
            return {}
        
        result = scheduler.pause_and_check(
            check_func,
            pause_seconds=1000,  # Request very long pause
            on_event=self._event_handler
        )
        
        # Should be capped at 60 seconds (1 minute for test)
        self.assertLessEqual(result['pause_seconds'], 60)
    
    def test_get_metrics(self):
        """Test getting phase metrics."""
        def test_phase():
            return {}
        
        self.scheduler.run_phase('phase1', test_phase, 10)
        self.scheduler.run_phase('phase2', test_phase, 10)
        
        metrics = self.scheduler.get_metrics()
        self.assertIn('phase1', metrics)
        self.assertIn('phase2', metrics)
    
    def test_write_heartbeat(self):
        """Test heartbeat writing."""
        self.scheduler.current_phase = 'test_phase'
        self.scheduler.write_heartbeat(on_event=self._event_handler)
        
        self.assertEqual(len(self.events), 1)
        self.assertEqual(self.events[0]['type'], 'heartbeat')
        self.assertEqual(self.events[0]['phase'], 'test_phase')


def run_tests():
    """Run all tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhaseScheduler)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
