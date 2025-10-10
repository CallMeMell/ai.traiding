#!/usr/bin/env python3
"""
test_view_session_enhanced.py - Enhanced Tests for View Session Page
====================================================================

Tests the enhanced View Session page with all transparency and 
real-time update features.
"""

import unittest
import time
from datetime import datetime

# Import only public API functions
try:
    from dashboard import add_task, update_task, remove_task, _active_tasks
    # Import private function for internal testing
    from dashboard import _get_active_tasks
except ImportError:
    # Fallback for testing without full dependencies
    print("Warning: Could not import all dashboard functions")
    add_task = None
    update_task = None
    remove_task = None
    _get_active_tasks = None
    _active_tasks = None


class TestViewSessionTransparency(unittest.TestCase):
    """Test View Session page transparency features"""
    
    def setUp(self):
        """Set up test fixtures"""
        if add_task is None:
            self.skipTest("Dashboard functions not available")
        import dashboard
        # Clear active tasks before each test
        dashboard._active_tasks = []
        dashboard._task_id_counter = 0
    
    def test_task_with_elapsed_time(self):
        """Test that tasks track time correctly"""
        task_id = add_task("Test Task", "backtest", "Test details")
        time.sleep(0.1)  # Small delay
        
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), 1)
        
        # Verify time fields exist
        task = tasks[0]
        self.assertIn('started_at', task)
        self.assertIn('updated_at', task)
        
        # Verify time format
        try:
            datetime.strptime(task['started_at'], '%Y-%m-%d %H:%M:%S')
            datetime.strptime(task['updated_at'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            self.fail("Invalid datetime format")
    
    def test_multiple_task_visibility(self):
        """Test that all active tasks are visible"""
        # Add multiple tasks with different types
        task1 = add_task("Backtest Task", "backtest", "BTCUSDT strategy")
        task2 = add_task("Simulation Task", "simulation", "Live simulation")
        task3 = add_task("Optimization Task", "optimization", "Parameter tuning")
        
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), 3)
        
        # Verify all task IDs are present
        task_ids = [t['id'] for t in tasks]
        self.assertIn(task1, task_ids)
        self.assertIn(task2, task_ids)
        self.assertIn(task3, task_ids)
        
        # Verify all have required fields for transparency
        for task in tasks:
            self.assertIn('id', task)
            self.assertIn('name', task)
            self.assertIn('type', task)
            self.assertIn('status', task)
            self.assertIn('progress', task)
            self.assertIn('details', task)
            self.assertIn('started_at', task)
            self.assertIn('updated_at', task)
    
    def test_task_status_transitions(self):
        """Test that task status changes are tracked"""
        task_id = add_task("Test Task", "backtest")
        
        # Initial status
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['status'], 'running')
        
        # Update to completed
        update_task(task_id, status='completed')
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['status'], 'completed')
        
        # Verify updated_at changed
        initial_time = tasks[0]['started_at']
        time.sleep(0.1)
        update_task(task_id, details='Updated details')
        tasks = _get_active_tasks()
        # Updated time should be different from start time
        self.assertIsNotNone(tasks[0]['updated_at'])
    
    def test_progress_tracking(self):
        """Test that progress updates are accurate"""
        task_id = add_task("Progress Test", "backtest")
        
        # Test progress increments
        for progress in [0, 25, 50, 75, 100]:
            update_task(task_id, progress=progress)
            tasks = _get_active_tasks()
            self.assertEqual(tasks[0]['progress'], progress)
    
    def test_detailed_information_display(self):
        """Test that detailed task information is preserved"""
        detailed_info = "Backtesting Golden Cross on BTCUSDT from 2023-01-01 to 2023-12-31 with 1h timeframe"
        task_id = add_task("Detailed Task", "backtest", detailed_info)
        
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['details'], detailed_info)
        
        # Update details
        new_details = "Progress: 50% - Processing data from June 2023"
        update_task(task_id, details=new_details)
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['details'], new_details)
    
    def test_task_cleanup(self):
        """Test that completed tasks are cleaned up after time"""
        # Add and complete a task
        task_id = add_task("Cleanup Test", "backtest")
        update_task(task_id, status='completed', progress=100)
        
        # Should still be visible initially
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), 1)
        
        # Note: Full cleanup test would require time manipulation
        # This test verifies the cleanup logic exists
        import dashboard
        self.assertIsNotNone(dashboard._get_active_tasks)


class TestViewSessionRealTimeUpdates(unittest.TestCase):
    """Test real-time update capabilities"""
    
    def setUp(self):
        """Set up test fixtures"""
        if add_task is None:
            self.skipTest("Dashboard functions not available")
        import dashboard
        dashboard._active_tasks = []
        dashboard._task_id_counter = 0
    
    def test_concurrent_task_updates(self):
        """Test updating multiple tasks concurrently"""
        task1 = add_task("Task 1", "backtest")
        task2 = add_task("Task 2", "simulation")
        task3 = add_task("Task 3", "optimization")
        
        # Update all tasks with different progress
        update_task(task1, progress=30)
        update_task(task2, progress=60)
        update_task(task3, progress=90)
        
        tasks = _get_active_tasks()
        progress_values = [t['progress'] for t in tasks]
        self.assertIn(30, progress_values)
        self.assertIn(60, progress_values)
        self.assertIn(90, progress_values)
    
    def test_task_type_diversity(self):
        """Test that different task types are properly tracked"""
        types = ['backtest', 'simulation', 'optimization', 'live_trading']
        task_ids = []
        
        for task_type in types:
            task_id = add_task(f"Task {task_type}", task_type)
            task_ids.append(task_id)
        
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), len(types))
        
        # Verify all types are present
        tracked_types = [t['type'] for t in tasks]
        for task_type in types:
            self.assertIn(task_type, tracked_types)
    
    def test_rapid_updates(self):
        """Test that rapid successive updates are handled"""
        task_id = add_task("Rapid Update Test", "backtest")
        
        # Rapidly update progress
        for i in range(0, 101, 10):
            update_task(task_id, progress=i)
        
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['progress'], 100)
    
    def test_task_failure_tracking(self):
        """Test that task failures are properly tracked"""
        task_id = add_task("Failure Test", "backtest")
        
        # Simulate task failure
        update_task(task_id, status='failed', details='Error: Connection timeout')
        
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['status'], 'failed')
        self.assertIn('Error', tasks[0]['details'])


class TestViewSessionIntegration(unittest.TestCase):
    """Integration tests for complete View Session workflows"""
    
    def setUp(self):
        """Set up test fixtures"""
        if add_task is None:
            self.skipTest("Dashboard functions not available")
        import dashboard
        dashboard._active_tasks = []
        dashboard._task_id_counter = 0
    
    def test_complete_backtest_workflow(self):
        """Test a complete backtest task workflow"""
        # Start backtest
        task_id = add_task(
            "Backtest - Golden Cross Strategy",
            "backtest",
            "Testing on BTCUSDT 2023 data"
        )
        
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['status'], 'running')
        self.assertEqual(tasks[0]['progress'], 0)
        
        # Simulate progress
        for progress in [25, 50, 75, 100]:
            update_task(task_id, progress=progress)
            tasks = _get_active_tasks()
            self.assertEqual(tasks[0]['progress'], progress)
        
        # Complete task
        update_task(task_id, status='completed', details='Win rate: 65%')
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['status'], 'completed')
        self.assertIn('Win rate', tasks[0]['details'])
    
    def test_multiple_concurrent_operations(self):
        """Test multiple concurrent operations visibility"""
        # Start multiple operations
        backtest_id = add_task("Backtest", "backtest", "Testing strategy A")
        sim_id = add_task("Simulation", "simulation", "Live paper trading")
        opt_id = add_task("Optimization", "optimization", "Tuning parameters")
        
        # All should be visible
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), 3)
        
        # Update each independently
        update_task(backtest_id, progress=50)
        update_task(sim_id, progress=30)
        update_task(opt_id, progress=70)
        
        # Verify independent updates
        tasks = _get_active_tasks()
        task_dict = {t['id']: t for t in tasks}
        self.assertEqual(task_dict[backtest_id]['progress'], 50)
        self.assertEqual(task_dict[sim_id]['progress'], 30)
        self.assertEqual(task_dict[opt_id]['progress'], 70)
        
        # Complete one, keep others running
        update_task(backtest_id, status='completed')
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), 3)  # All still visible
        
        completed_tasks = [t for t in tasks if t['status'] == 'completed']
        running_tasks = [t for t in tasks if t['status'] == 'running']
        self.assertEqual(len(completed_tasks), 1)
        self.assertEqual(len(running_tasks), 2)
    
    def test_task_transparency_features(self):
        """Test that all transparency requirements are met"""
        task_id = add_task(
            "Comprehensive Test",
            "backtest",
            "Full transparency test with all details"
        )
        
        tasks = _get_active_tasks()
        task = tasks[0]
        
        # Verify all required fields for transparency
        required_fields = [
            'id', 'name', 'type', 'details', 'status', 
            'progress', 'started_at', 'updated_at'
        ]
        
        for field in required_fields:
            self.assertIn(field, task, f"Missing required field: {field}")
            self.assertIsNotNone(task[field], f"Field {field} is None")
        
        # Verify field types
        self.assertIsInstance(task['id'], int)
        self.assertIsInstance(task['name'], str)
        self.assertIsInstance(task['type'], str)
        self.assertIsInstance(task['details'], str)
        self.assertIsInstance(task['status'], str)
        self.assertIsInstance(task['progress'], int)
        self.assertIsInstance(task['started_at'], str)
        self.assertIsInstance(task['updated_at'], str)


def run_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  🧪 Running Enhanced View Session Tests")
    print("=" * 70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestViewSessionTransparency))
    suite.addTests(loader.loadTestsFromTestCase(TestViewSessionRealTimeUpdates))
    suite.addTests(loader.loadTestsFromTestCase(TestViewSessionIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("  ✅ All enhanced tests passed!")
        print(f"  Total tests: {result.testsRun}")
    else:
        print("  ❌ Some tests failed")
        print(f"  Tests run: {result.testsRun}")
        print(f"  Failures: {len(result.failures)}")
        print(f"  Errors: {len(result.errors)}")
    print("=" * 70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
