"""
test_integration_workflow.py - Integration test for complete workflow
====================================================================
Integration test demonstrating phase engine, heartbeats, retry/backoff, and summary.
"""

import unittest
import tempfile
import shutil
import os
import json
from automation.runner import AutomationRunner
from core.session_store import SessionStore


class TestIntegrationWorkflow(unittest.TestCase):
    """Integration test for complete automation workflow."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.events_path = os.path.join(self.test_dir, "events.jsonl")
        self.summary_path = os.path.join(self.test_dir, "summary.json")
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_complete_workflow_with_all_features(self):
        """Test complete workflow demonstrating all features."""
        # Create runner with short intervals for testing
        runner = AutomationRunner(
            data_phase_timeout=10,
            strategy_phase_timeout=10,
            api_phase_timeout=10,
            heartbeat_interval=2,
            enable_validation=False
        )
        runner.session_store = SessionStore(self.events_path, self.summary_path)
        
        # Run the complete workflow
        result = runner.run()
        
        # Verify workflow completed successfully
        self.assertEqual(result['status'], 'success')
        self.assertIn('duration_seconds', result)
        self.assertGreater(result['duration_seconds'], 0)
        
        # Verify all phases completed
        self.assertIn('phases', result)
        phases = result['phases']
        self.assertIn('data_phase', phases)
        self.assertIn('strategy_phase', phases)
        self.assertIn('api_phase', phases)
        
        # Verify each phase succeeded
        for phase_name, phase_result in phases.items():
            self.assertEqual(phase_result['status'], 'success', 
                           f"{phase_name} did not succeed")
        
        # Read and verify events
        events = runner.session_store.read_events()
        self.assertGreater(len(events), 0, "No events were logged")
        
        # Verify essential event types
        event_types = [e.get('type') for e in events]
        
        # Check for phase events
        self.assertIn('runner_start', event_types, "Missing runner_start event")
        self.assertIn('runner_end', event_types, "Missing runner_end event")
        self.assertIn('phase_start', event_types, "Missing phase_start events")
        self.assertIn('phase_end', event_types, "Missing phase_end events")
        self.assertIn('checkpoint', event_types, "Missing checkpoint events")
        
        # Check for heartbeat events
        heartbeat_events = [e for e in events if e.get('type') == 'heartbeat']
        self.assertGreater(len(heartbeat_events), 0, "No heartbeat events found")
        
        print(f"✓ Found {len(heartbeat_events)} heartbeat events")
        
        # Verify heartbeat events have proper structure
        for hb in heartbeat_events:
            self.assertIn('timestamp', hb)
            self.assertIn('session_id', hb)
            self.assertIn('phase', hb)
            # Heartbeats should have metrics
            if 'metrics' in hb:
                metrics = hb['metrics']
                # Verify metrics structure
                self.assertIsInstance(metrics, dict)
        
        # Read and verify summary
        summary = runner.session_store.read_summary()
        self.assertIsNotNone(summary, "Summary was not created")
        
        # Verify summary contains required fields
        required_fields = [
            'session_id', 'session_start', 'session_end',
            'status', 'runtime_secs', 'phases_completed',
            'initial_capital', 'current_equity', 'roi'
        ]
        
        for field in required_fields:
            self.assertIn(field, summary, f"Summary missing required field: {field}")
        
        # Verify summary values
        self.assertEqual(summary['status'], 'success')
        self.assertEqual(summary['phases_completed'], 3)
        self.assertGreater(summary['runtime_secs'], 0)
        self.assertIsNotNone(summary['roi'])
        
        print(f"✓ Summary: {summary['phases_completed']} phases, "
              f"{summary['runtime_secs']:.2f}s runtime, "
              f"{summary['roi']:.2%} ROI")
        
        # Verify events file exists and is valid JSON Lines format
        self.assertTrue(os.path.exists(self.events_path), "events.jsonl not created")
        
        with open(self.events_path, 'r') as f:
            lines = f.readlines()
            self.assertGreater(len(lines), 0, "events.jsonl is empty")
            
            # Verify each line is valid JSON
            for i, line in enumerate(lines):
                try:
                    json.loads(line)
                except json.JSONDecodeError as e:
                    self.fail(f"Line {i+1} in events.jsonl is invalid JSON: {e}")
        
        print(f"✓ events.jsonl has {len(lines)} valid JSON lines")
        
        # Verify summary file exists and is valid JSON
        self.assertTrue(os.path.exists(self.summary_path), "summary.json not created")
        
        with open(self.summary_path, 'r') as f:
            try:
                summary_data = json.load(f)
                self.assertIsInstance(summary_data, dict)
            except json.JSONDecodeError as e:
                self.fail(f"summary.json is invalid JSON: {e}")
        
        print(f"✓ summary.json is valid JSON with {len(summary_data)} fields")
        
        # Verify phase progression (note: each phase has 2 phase_start events - one from runner, one from scheduler)
        phase_start_events = [e for e in events if e.get('type') == 'phase_start']
        phase_names = [e.get('phase') for e in phase_start_events 
                      if e.get('phase') in ['data_phase', 'strategy_phase', 'api_phase']]
        
        # Get unique phases in order
        unique_phases = []
        for phase in phase_names:
            if not unique_phases or unique_phases[-1] != phase:
                unique_phases.append(phase)
        
        expected_order = ['data_phase', 'strategy_phase', 'api_phase']
        self.assertEqual(unique_phases, expected_order, 
                        f"Phases executed in wrong order: {unique_phases}")
        
        print(f"✓ Phases executed in correct order: {' -> '.join(unique_phases)}")
        
        print("\n✅ All integration tests passed!")
        print(f"   - Total events: {len(events)}")
        print(f"   - Heartbeats: {len(heartbeat_events)}")
        print(f"   - Phases: {summary['phases_completed']}")
        print(f"   - Runtime: {summary['runtime_secs']:.2f}s")
        print(f"   - Status: {summary['status']}")


def run_tests():
    """Run all tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegrationWorkflow)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
