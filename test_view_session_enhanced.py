"""
test_view_session_enhanced.py - Tests for Enhanced View Session
==============================================================
Test the enhanced view session app components.
"""

import unittest
import os
import tempfile
import shutil
import json
from datetime import datetime
from core.session_store import SessionStore
from tools.view_session_app import ViewSessionApp


class TestViewSessionEnhanced(unittest.TestCase):
    """Test enhanced view session functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.events_path = os.path.join(self.test_dir, "events.jsonl")
        self.summary_path = os.path.join(self.test_dir, "summary.json")
        self.store = SessionStore(self.events_path, self.summary_path)
        
        # Create test data
        self._create_test_data()
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _create_test_data(self):
        """Create test events and summary."""
        # Create test events
        events = [
            {
                'timestamp': datetime.now().isoformat(),
                'session_id': 'test-session',
                'type': 'runner_start',
                'phase': None,
                'level': 'info',
                'message': 'Runner started',
                'status': 'started'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'session_id': 'test-session',
                'type': 'phase_start',
                'phase': 'data_phase',
                'level': 'info',
                'message': 'Starting data phase',
                'status': 'started'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'session_id': 'test-session',
                'type': 'checkpoint',
                'phase': 'data_phase',
                'level': 'info',
                'message': 'Checkpoint: validation',
                'status': 'pass'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'session_id': 'test-session',
                'type': 'heartbeat',
                'phase': 'data_phase',
                'level': 'debug',
                'message': 'Heartbeat',
                'metrics': {
                    'equity': 10050.0,
                    'pnl': 50.0,
                    'trades': 5,
                    'wins': 3,
                    'losses': 2
                }
            },
            {
                'timestamp': datetime.now().isoformat(),
                'session_id': 'test-session',
                'type': 'phase_end',
                'phase': 'data_phase',
                'level': 'info',
                'message': 'Completed data phase',
                'status': 'success'
            }
        ]
        
        for event in events:
            self.store.append_event(event)
        
        # Create test summary
        summary = {
            'session_id': 'test-session',
            'session_start': datetime.now().isoformat(),
            'status': 'running',
            'phases_completed': 1,
            'phases_total': 3,
            'initial_capital': 10000.0,
            'current_equity': 10050.0,
            'totals': {
                'trades': 5,
                'wins': 3,
                'losses': 2
            },
            'roi': 0.5
        }
        
        self.store.write_summary(summary)
    
    def test_load_data(self):
        """Test loading data from store."""
        summary = self.store.read_summary()
        events = self.store.read_events()
        
        self.assertIsNotNone(summary)
        self.assertEqual(len(events), 5)
        self.assertEqual(summary['session_id'], 'test-session')
    
    def test_event_types(self):
        """Test different event types are present."""
        events = self.store.read_events()
        
        event_types = [e['type'] for e in events]
        self.assertIn('runner_start', event_types)
        self.assertIn('phase_start', event_types)
        self.assertIn('checkpoint', event_types)
        self.assertIn('heartbeat', event_types)
        self.assertIn('phase_end', event_types)
    
    def test_heartbeat_metrics(self):
        """Test heartbeat contains metrics."""
        events = self.store.read_events()
        
        heartbeat_events = [e for e in events if e['type'] == 'heartbeat']
        self.assertEqual(len(heartbeat_events), 1)
        
        heartbeat = heartbeat_events[0]
        self.assertIn('metrics', heartbeat)
        self.assertEqual(heartbeat['metrics']['equity'], 10050.0)
        self.assertEqual(heartbeat['metrics']['pnl'], 50.0)
    
    def test_checkpoint_status(self):
        """Test checkpoint has status."""
        events = self.store.read_events()
        
        checkpoint_events = [e for e in events if e['type'] == 'checkpoint']
        self.assertEqual(len(checkpoint_events), 1)
        
        checkpoint = checkpoint_events[0]
        self.assertEqual(checkpoint['status'], 'pass')
    
    def test_summary_totals(self):
        """Test summary has totals."""
        summary = self.store.read_summary()
        
        self.assertIn('totals', summary)
        self.assertEqual(summary['totals']['trades'], 5)
        self.assertEqual(summary['totals']['wins'], 3)
        self.assertEqual(summary['totals']['losses'], 2)
    
    def test_tail_reading(self):
        """Test tail reading of events."""
        events = self.store.read_events(tail=3)
        
        self.assertEqual(len(events), 3)
        # Should be the last 3 events
        self.assertEqual(events[-1]['type'], 'phase_end')


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestViewSessionEnhanced))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
