"""
test_session_store_core.py - Tests for core/session_store.py
=============================================================
Tests for SessionStore class.
"""

import unittest
import os
import tempfile
import shutil
import json
from datetime import datetime

# Import module to test
from core.session_store import SessionStore


class TestSessionStore(unittest.TestCase):
    """Tests for SessionStore class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.events_path = os.path.join(self.test_dir, "events.jsonl")
        self.summary_path = os.path.join(self.test_dir, "summary.json")
        self.store = SessionStore(
            events_path=self.events_path,
            summary_path=self.summary_path
        )
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test SessionStore initialization"""
        self.assertIsInstance(self.store, SessionStore)
        self.assertTrue(os.path.exists(os.path.dirname(self.events_path)))
        self.assertTrue(os.path.exists(os.path.dirname(self.summary_path)))
    
    def test_append_event_with_timestamp(self):
        """Test appending event with timestamp"""
        event = {
            'timestamp': '2023-01-01T00:00:00',
            'type': 'test_event',
            'data': {'value': 100}
        }
        
        self.store.append_event(event, validate=False)
        
        self.assertTrue(os.path.exists(self.events_path))
        
        # Read and verify
        events = self.store.read_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['type'], 'test_event')
        self.assertEqual(events[0]['timestamp'], '2023-01-01T00:00:00')
    
    def test_append_event_without_timestamp(self):
        """Test appending event without timestamp (should add one)"""
        event = {
            'type': 'test_event',
            'data': {'value': 100}
        }
        
        self.store.append_event(event, validate=False)
        
        events = self.store.read_events()
        self.assertEqual(len(events), 1)
        self.assertIn('timestamp', events[0])
    
    def test_append_event_with_validation(self):
        """Test appending event with validation enabled"""
        event = {
            'timestamp': '2023-01-01T00:00:00',
            'type': 'test_event',
            'data': {'value': 100}
        }
        
        # Should not raise error even if validation fails
        self.store.append_event(event, validate=True)
        
        events = self.store.read_events()
        self.assertEqual(len(events), 1)
    
    def test_append_multiple_events(self):
        """Test appending multiple events"""
        for i in range(5):
            event = {
                'type': f'event_{i}',
                'data': {'index': i}
            }
            self.store.append_event(event, validate=False)
        
        events = self.store.read_events()
        self.assertEqual(len(events), 5)
    
    def test_read_events_empty_file(self):
        """Test reading events from non-existent file"""
        events = self.store.read_events()
        
        self.assertEqual(events, [])
    
    def test_read_events_with_tail(self):
        """Test reading last N events"""
        for i in range(10):
            event = {
                'type': f'event_{i}',
                'data': {'index': i}
            }
            self.store.append_event(event, validate=False)
        
        events = self.store.read_events(tail=3)
        
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0]['data']['index'], 7)
        self.assertEqual(events[2]['data']['index'], 9)
    
    def test_read_events_with_invalid_json(self):
        """Test reading events with invalid JSON lines"""
        # Write some invalid JSON
        with open(self.events_path, 'w') as f:
            f.write('{"valid": true}\n')
            f.write('invalid json line\n')
            f.write('{"also_valid": true}\n')
        
        events = self.store.read_events()
        
        # Should skip invalid line
        self.assertEqual(len(events), 2)
        self.assertTrue(events[0]['valid'])
        self.assertTrue(events[1]['also_valid'])
    
    def test_read_events_with_empty_lines(self):
        """Test reading events with empty lines"""
        with open(self.events_path, 'w') as f:
            f.write('{"event": 1}\n')
            f.write('\n')
            f.write('{"event": 2}\n')
        
        events = self.store.read_events()
        
        self.assertEqual(len(events), 2)
    
    def test_write_summary(self):
        """Test writing summary"""
        summary = {
            'session_id': 'test123',
            'total_trades': 10,
            'win_rate': 0.6
        }
        
        self.store.write_summary(summary, validate=False)
        
        self.assertTrue(os.path.exists(self.summary_path))
        
        # Verify content
        with open(self.summary_path, 'r') as f:
            loaded = json.load(f)
            self.assertEqual(loaded['session_id'], 'test123')
            self.assertEqual(loaded['total_trades'], 10)
    
    def test_write_summary_with_validation(self):
        """Test writing summary with validation enabled"""
        summary = {
            'session_id': 'test123',
            'total_trades': 10
        }
        
        # Should not raise error even if validation fails
        self.store.write_summary(summary, validate=True)
        
        loaded_summary = self.store.read_summary()
        self.assertIsNotNone(loaded_summary)
        self.assertEqual(loaded_summary['session_id'], 'test123')
    
    def test_read_summary_empty(self):
        """Test reading summary from non-existent file"""
        summary = self.store.read_summary()
        
        self.assertIsNone(summary)
    
    def test_read_summary_with_invalid_json(self):
        """Test reading summary with invalid JSON"""
        with open(self.summary_path, 'w') as f:
            f.write('invalid json')
        
        summary = self.store.read_summary()
        
        self.assertIsNone(summary)
    
    def test_calculate_roi_positive(self):
        """Test ROI calculation with profit"""
        initial = 10000.0
        current = 12000.0
        
        roi = self.store.calculate_roi(initial, current)
        
        self.assertAlmostEqual(roi, 20.0, places=2)
    
    def test_calculate_roi_negative(self):
        """Test ROI calculation with loss"""
        initial = 10000.0
        current = 8000.0
        
        roi = self.store.calculate_roi(initial, current)
        
        self.assertAlmostEqual(roi, -20.0, places=2)
    
    def test_calculate_roi_zero_initial_capital(self):
        """Test ROI calculation with zero initial capital"""
        roi = self.store.calculate_roi(0, 1000)
        
        self.assertEqual(roi, 0.0)
    
    def test_calculate_roi_negative_initial_capital(self):
        """Test ROI calculation with negative initial capital"""
        roi = self.store.calculate_roi(-100, 1000)
        
        self.assertEqual(roi, 0.0)
    
    def test_clear_events(self):
        """Test clearing events"""
        # Add some events
        for i in range(3):
            event = {'type': f'event_{i}'}
            self.store.append_event(event, validate=False)
        
        self.assertTrue(os.path.exists(self.events_path))
        
        # Clear events
        self.store.clear_events()
        
        self.assertFalse(os.path.exists(self.events_path))
    
    def test_clear_events_nonexistent(self):
        """Test clearing events when file doesn't exist"""
        # Should not raise error
        self.store.clear_events()
        
        self.assertFalse(os.path.exists(self.events_path))
    
    def test_clear_summary(self):
        """Test clearing summary"""
        # Write summary
        summary = {'session_id': 'test'}
        self.store.write_summary(summary, validate=False)
        
        self.assertTrue(os.path.exists(self.summary_path))
        
        # Clear summary
        self.store.clear_summary()
        
        self.assertFalse(os.path.exists(self.summary_path))
    
    def test_clear_summary_nonexistent(self):
        """Test clearing summary when file doesn't exist"""
        # Should not raise error
        self.store.clear_summary()
        
        self.assertFalse(os.path.exists(self.summary_path))


if __name__ == '__main__':
    unittest.main()
