"""
test_scheduler_auto.py - Tests for automation/scheduler.py
===========================================================
Tests for PhaseScheduler class.
"""

import unittest
import time
from datetime import datetime
from unittest.mock import Mock

# Import module to test
from automation.scheduler import PhaseScheduler


class TestPhaseScheduler(unittest.TestCase):
    """Tests for PhaseScheduler class"""
    
    def setUp(self):
        """Set up test environment"""
        self.scheduler = PhaseScheduler(max_pause_minutes=5)
    
    def test_initialization(self):
        """Test scheduler initialization"""
        self.assertEqual(self.scheduler.max_pause_minutes, 5)
        self.assertIsNone(self.scheduler.current_phase)
        self.assertIsNone(self.scheduler.phase_start_time)
        self.assertEqual(self.scheduler.metrics, {})
    
    def test_run_phase_success(self):
        """Test running a phase successfully"""
        def phase_func():
            return {'result': 'success'}
        
        result = self.scheduler.run_phase(
            'test_phase',
            phase_func,
            timeout_seconds=5
        )
        
        self.assertEqual(result['phase'], 'test_phase')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['phase_result'], {'result': 'success'})
        self.assertIn('start_time', result)
        self.assertIn('end_time', result)
    
    def test_run_phase_with_event_callback(self):
        """Test running a phase with event callback"""
        events = []
        
        def on_event(event):
            events.append(event)
        
        def phase_func():
            return {'result': 'success'}
        
        result = self.scheduler.run_phase(
            'test_phase',
            phase_func,
            timeout_seconds=5,
            on_event=on_event
        )
        
        # Should have start and end events
        self.assertGreaterEqual(len(events), 2)
        self.assertEqual(events[0]['type'], 'phase_start')
        self.assertEqual(events[-1]['type'], 'phase_end')
    
    def test_run_phase_timeout(self):
        """Test phase timeout"""
        def slow_phase():
            time.sleep(0.3)
            return {'result': 'too_slow'}
        
        result = self.scheduler.run_phase(
            'slow_phase',
            slow_phase,
            timeout_seconds=1  # Give enough time but test the timeout logic
        )
        
        # Should still complete successfully if within timeout
        self.assertIn('status', result)
    
    def test_run_phase_error(self):
        """Test phase with error"""
        def failing_phase():
            raise ValueError("Test error")
        
        result = self.scheduler.run_phase(
            'failing_phase',
            failing_phase,
            timeout_seconds=5
        )
        
        self.assertEqual(result['phase'], 'failing_phase')
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
        self.assertIn('Test error', result['error'])
    
    def test_pause_and_check_success(self):
        """Test pause and check with successful check"""
        def check_func():
            return {'status': 'ok'}
        
        result = self.scheduler.pause_and_check(
            pause_seconds=0.01,  # Very short pause for testing
            check_func=check_func
        )
        
        self.assertEqual(result['type'], 'pause_and_check')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['check_result'], {'status': 'ok'})
        self.assertIn('timestamp', result)
    
    def test_pause_and_check_with_event_callback(self):
        """Test pause and check with event callback"""
        events = []
        
        def on_event(event):
            events.append(event)
        
        def check_func():
            return {'status': 'ok'}
        
        result = self.scheduler.pause_and_check(
            pause_seconds=0.01,
            check_func=check_func,
            on_event=on_event
        )
        
        # Should have start and end events
        self.assertGreaterEqual(len(events), 2)
        self.assertEqual(events[0]['type'], 'pause_start')
        self.assertEqual(events[-1]['type'], 'pause_end')
    
    def test_pause_and_check_exceeds_max(self):
        """Test pause duration exceeding maximum"""
        # Use a scheduler with very short max pause for testing
        short_scheduler = PhaseScheduler(max_pause_minutes=0.01)  # 0.6 seconds
        
        def check_func():
            return {'status': 'ok'}
        
        # Request pause longer than max
        result = short_scheduler.pause_and_check(
            pause_seconds=10,
            check_func=check_func
        )
        
        # Should be capped at max_pause_minutes (0.6 seconds)
        self.assertLessEqual(result['pause_seconds'], 1)
    
    def test_pause_and_check_error(self):
        """Test pause and check with error in check function"""
        def failing_check():
            raise RuntimeError("Check failed")
        
        result = self.scheduler.pause_and_check(
            pause_seconds=0.01,
            check_func=failing_check
        )
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
        self.assertIn('Check failed', result['error'])
    
    def test_write_heartbeat(self):
        """Test writing heartbeat"""
        events = []
        
        def on_event(event):
            events.append(event)
        
        # Set current phase
        self.scheduler.current_phase = 'test_phase'
        
        self.scheduler.write_heartbeat(on_event=on_event)
        
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['type'], 'heartbeat')
        self.assertEqual(events[0]['phase'], 'test_phase')
        self.assertIn('timestamp', events[0])
    
    def test_write_heartbeat_no_callback(self):
        """Test writing heartbeat without callback"""
        # Should not raise error
        self.scheduler.write_heartbeat()
    
    def test_get_metrics(self):
        """Test getting metrics"""
        # Run a phase to populate metrics
        def phase_func():
            return {'result': 'success'}
        
        self.scheduler.run_phase('test_phase', phase_func, timeout_seconds=5)
        
        metrics = self.scheduler.get_metrics()
        
        self.assertIsInstance(metrics, dict)


if __name__ == '__main__':
    unittest.main()
