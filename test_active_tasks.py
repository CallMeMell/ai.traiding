#!/usr/bin/env python3
"""
test_active_tasks.py - Tests for Active Task Tracking Feature
==============================================================

Tests the active task tracking system for the trading bot dashboard.
"""

import unittest
import json
from datetime import datetime
from dashboard import (
    add_task, update_task, remove_task, _get_active_tasks,
    _active_tasks, _task_id_counter
)


class TestActiveTaskTracking(unittest.TestCase):
    """Test suite for active task tracking"""
    
    def setUp(self):
        """Set up test fixtures"""
        import dashboard
        # Clear active tasks before each test
        dashboard._active_tasks = []
        dashboard._task_id_counter = 0
    
    def test_add_task(self):
        """Test adding a new task"""
        task_id = add_task(
            task_name="Test Backtest",
            task_type="backtest",
            details="Testing BTC strategy"
        )
        
        self.assertIsNotNone(task_id)
        self.assertIsInstance(task_id, int)
        self.assertGreater(task_id, 0)
        
        # Verify task was added
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['name'], "Test Backtest")
        self.assertEqual(tasks[0]['type'], "backtest")
        self.assertEqual(tasks[0]['status'], "running")
        self.assertEqual(tasks[0]['progress'], 0)
    
    def test_update_task_progress(self):
        """Test updating task progress"""
        task_id = add_task("Test Task", "simulation")
        
        # Update progress
        result = update_task(task_id, progress=50)
        self.assertTrue(result)
        
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['progress'], 50)
        
        # Update to 100%
        update_task(task_id, progress=100)
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['progress'], 100)
    
    def test_update_task_status(self):
        """Test updating task status"""
        task_id = add_task("Test Task", "optimization")
        
        # Update status to completed
        result = update_task(task_id, status="completed")
        self.assertTrue(result)
        
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['status'], "completed")
        
        # Update status to failed
        update_task(task_id, status="failed")
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['status'], "failed")
    
    def test_update_task_details(self):
        """Test updating task details"""
        task_id = add_task("Test Task", "backtest")
        
        new_details = "Updated with new parameters"
        result = update_task(task_id, details=new_details)
        self.assertTrue(result)
        
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['details'], new_details)
    
    def test_update_nonexistent_task(self):
        """Test updating a task that doesn't exist"""
        result = update_task(9999, progress=50)
        self.assertFalse(result)
    
    def test_remove_task(self):
        """Test removing a task"""
        task_id = add_task("Test Task", "simulation")
        
        # Verify task exists
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), 1)
        
        # Remove task
        remove_task(task_id)
        
        # Verify task is removed
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), 0)
    
    def test_multiple_tasks(self):
        """Test managing multiple tasks"""
        task1 = add_task("Task 1", "backtest")
        task2 = add_task("Task 2", "simulation")
        task3 = add_task("Task 3", "optimization")
        
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), 3)
        
        # Update different tasks
        update_task(task1, progress=25)
        update_task(task2, progress=50)
        update_task(task3, progress=75)
        
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['progress'], 25)
        self.assertEqual(tasks[1]['progress'], 50)
        self.assertEqual(tasks[2]['progress'], 75)
        
        # Remove middle task
        remove_task(task2)
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), 2)
    
    def test_task_fields(self):
        """Test that all required fields are present"""
        task_id = add_task("Complete Task", "backtest", "Some details")
        
        tasks = _get_active_tasks()
        task = tasks[0]
        
        # Check required fields
        self.assertIn('id', task)
        self.assertIn('name', task)
        self.assertIn('type', task)
        self.assertIn('details', task)
        self.assertIn('status', task)
        self.assertIn('progress', task)
        self.assertIn('started_at', task)
        self.assertIn('updated_at', task)
        
        # Check field types
        self.assertIsInstance(task['id'], int)
        self.assertIsInstance(task['name'], str)
        self.assertIsInstance(task['type'], str)
        self.assertIsInstance(task['progress'], int)
    
    def test_progress_bounds(self):
        """Test that progress is bounded between 0 and 100"""
        task_id = add_task("Test Task", "backtest")
        
        # Test upper bound
        update_task(task_id, progress=150)
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['progress'], 100)
        
        # Test lower bound
        update_task(task_id, progress=-10)
        tasks = _get_active_tasks()
        self.assertEqual(tasks[0]['progress'], 0)
    
    def test_task_types(self):
        """Test different task types"""
        types = ["backtest", "simulation", "optimization", "live_trading"]
        
        for task_type in types:
            task_id = add_task(f"Test {task_type}", task_type)
            tasks = _get_active_tasks()
            self.assertTrue(any(t['type'] == task_type for t in tasks))
    
    def test_task_statuses(self):
        """Test different task statuses"""
        task_id = add_task("Test Task", "backtest")
        
        statuses = ["running", "completed", "failed", "queued"]
        for status in statuses:
            update_task(task_id, status=status)
            tasks = _get_active_tasks()
            self.assertEqual(tasks[0]['status'], status)


class TestTaskTrackingIntegration(unittest.TestCase):
    """Integration tests for task tracking"""
    
    def setUp(self):
        """Set up test fixtures"""
        import dashboard
        # Clear active tasks before each test
        dashboard._active_tasks = []
        dashboard._task_id_counter = 0
    
    def test_realistic_workflow(self):
        """Test a realistic task workflow"""
        # Start a backtest task
        task_id = add_task(
            task_name="Backtest Golden Cross",
            task_type="backtest",
            details="Testing on BTCUSDT 2023 data"
        )
        
        # Simulate progress updates
        for progress in [0, 25, 50, 75, 100]:
            update_task(task_id, progress=progress)
        
        # Mark as completed
        update_task(task_id, status="completed", details="Backtest completed successfully")
        
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['status'], "completed")
        self.assertEqual(tasks[0]['progress'], 100)
    
    def test_concurrent_tasks_workflow(self):
        """Test multiple concurrent tasks"""
        # Start multiple tasks
        task1 = add_task("Backtest Strategy A", "backtest")
        task2 = add_task("Optimize Parameters", "optimization")
        task3 = add_task("Simulate Trading", "simulation")
        
        # Update all tasks
        update_task(task1, progress=50)
        update_task(task2, progress=30)
        update_task(task3, progress=70)
        
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), 3)
        
        # Complete first task
        update_task(task1, status="completed")
        
        # Fail second task
        update_task(task2, status="failed", details="Parameter optimization failed")
        
        # Continue third task
        update_task(task3, progress=100)
        update_task(task3, status="completed")
        
        tasks = _get_active_tasks()
        self.assertEqual(len(tasks), 3)
        
        # Verify statuses
        statuses = [t['status'] for t in tasks]
        self.assertIn("completed", statuses)
        self.assertIn("failed", statuses)


def run_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  🧪 Running Active Task Tracking Tests")
    print("=" * 70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestActiveTaskTracking))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskTrackingIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("  ✅ All tests passed!")
    else:
        print("  ❌ Some tests failed")
    print("=" * 70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
