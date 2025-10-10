"""
test_session_store.py - Tests for Session Store
==============================================
Unit tests for session store functionality.
"""

import unittest
import os
import tempfile
import shutil
import json
from core.session_store import SessionStore


class TestSessionStore(unittest.TestCase):
    """Test SessionStore functionality."""
    
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
    
    def test_append_event(self):
        """Test appending events."""
        event = {
            'type': 'test_event',
            'phase': 'test_phase',
            'data': 'test_data'
        }
        
        self.store.append_event(event)
        
        # Verify file exists
        self.assertTrue(os.path.exists(self.events_path))
        
        # Read and verify
        events = self.store.read_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['type'], 'test_event')
        self.assertIn('timestamp', events[0])
    
    def test_append_multiple_events(self):
        """Test appending multiple events."""
        for i in range(5):
            event = {'type': f'event_{i}', 'data': i}
            self.store.append_event(event)
        
        events = self.store.read_events()
        self.assertEqual(len(events), 5)
    
    def test_read_events_empty(self):
        """Test reading events when file doesn't exist."""
        events = self.store.read_events()
        self.assertEqual(len(events), 0)
    
    def test_write_summary(self):
        """Test writing summary."""
        summary = {
            'session_start': '2024-01-01T12:00:00',
            'initial_capital': 10000.0,
            'current_equity': 10150.0
        }
        
        self.store.write_summary(summary)
        
        # Verify file exists
        self.assertTrue(os.path.exists(self.summary_path))
        
        # Read and verify
        loaded = self.store.read_summary()
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded['initial_capital'], 10000.0)
        self.assertIn('last_updated', loaded)
    
    def test_read_summary_empty(self):
        """Test reading summary when file doesn't exist."""
        summary = self.store.read_summary()
        self.assertIsNone(summary)
    
    def test_calculate_roi(self):
        """Test ROI calculation."""
        roi = self.store.calculate_roi(10000.0, 10500.0)
        self.assertAlmostEqual(roi, 5.0, places=2)
        
        roi = self.store.calculate_roi(10000.0, 9500.0)
        self.assertAlmostEqual(roi, -5.0, places=2)
        
        roi = self.store.calculate_roi(0, 100)
        self.assertEqual(roi, 0.0)
    
    def test_clear_events(self):
        """Test clearing events."""
        self.store.append_event({'type': 'test'})
        self.assertTrue(os.path.exists(self.events_path))
        
        self.store.clear_events()
        self.assertFalse(os.path.exists(self.events_path))
    
    def test_clear_summary(self):
        """Test clearing summary."""
        self.store.write_summary({'test': 'data'})
        self.assertTrue(os.path.exists(self.summary_path))
        
        self.store.clear_summary()
        self.assertFalse(os.path.exists(self.summary_path))


def run_tests():
    """Run all tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSessionStore)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
