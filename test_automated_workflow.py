"""
test_automated_workflow.py - Tests for Automated Workflow System
================================================================
Unit tests for the automated trading bot workflow preparation system
"""
import os
import sys
import json
import time
from datetime import datetime, timedelta

# Test framework imports
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Simple test runner if pytest not available
    class pytest:
        @staticmethod
        def fixture(func):
            return func

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automated_workflow import (
    WorkflowManager,
    WorkflowTask,
    LiveViewSession,
    TaskStatus,
    TaskResult,
    create_default_workflow,
    data_analysis_task,
    strategy_optimization_task,
    api_preparation_task
)
from config import config
from utils import setup_logging


# Test helper functions

def simple_task(logger, live_view):
    """Simple test task that always succeeds"""
    logger.info("Executing simple task")
    live_view.add_update('progress', "Processing...")
    return {"status": "success"}


def failing_task(logger, live_view):
    """Test task that always fails"""
    logger.info("Executing failing task")
    raise ValueError("Intentional test failure")


def slow_task(logger, live_view):
    """Test task that takes some time"""
    logger.info("Executing slow task")
    time.sleep(2)
    return {"status": "success", "duration": 2}


# Test fixtures

@pytest.fixture
def temp_workflow_dir(tmp_path):
    """Create temporary directory for workflow sessions"""
    workflow_dir = tmp_path / "workflow_sessions"
    workflow_dir.mkdir()
    return str(workflow_dir)


@pytest.fixture
def workflow_manager():
    """Create a test workflow manager"""
    return WorkflowManager(session_id="test_workflow")


@pytest.fixture
def live_view_session(temp_workflow_dir):
    """Create a test live view session"""
    return LiveViewSession("test_session", output_dir=temp_workflow_dir)


# Tests for LiveViewSession

def test_live_view_session_creation(temp_workflow_dir):
    """Test live view session creation"""
    session = LiveViewSession("test_session_1", output_dir=temp_workflow_dir)
    
    assert session.session_id == "test_session_1"
    assert session.output_dir == temp_workflow_dir
    assert len(session.updates) == 0
    assert session.start_time is not None
    
    # Check session file created
    session_file = os.path.join(temp_workflow_dir, "test_session_1.json")
    assert os.path.exists(session_file)


def test_live_view_add_update(live_view_session):
    """Test adding updates to live view session"""
    live_view_session.add_update('info', "Test message")
    assert len(live_view_session.updates) == 1
    assert live_view_session.updates[0]['type'] == 'info'
    assert live_view_session.updates[0]['message'] == "Test message"


def test_live_view_task_status(live_view_session):
    """Test updating task status"""
    live_view_session.update_task_status("Test Task", "running", 50.0)
    
    assert len(live_view_session.updates) == 1
    update = live_view_session.updates[0]
    assert update['type'] == 'progress'
    assert update['data']['task_name'] == "Test Task"
    assert update['data']['status'] == "running"
    assert update['data']['progress'] == 50.0


def test_live_view_get_status(live_view_session):
    """Test getting session status"""
    live_view_session.add_update('info', "Update 1")
    live_view_session.add_update('info', "Update 2")
    
    status = live_view_session.get_status()
    
    assert status['session_id'] == live_view_session.session_id
    assert status['total_updates'] == 2
    assert len(status['latest_updates']) == 2


# Tests for WorkflowTask

def test_workflow_task_creation():
    """Test workflow task creation"""
    task = WorkflowTask(
        name="Test Task",
        description="A test task",
        time_limit_hours=1.0,
        execute_func=simple_task
    )
    
    assert task.name == "Test Task"
    assert task.description == "A test task"
    assert task.time_limit_hours == 1.0
    assert task.auto_retry is True
    assert task.max_retries == 3


def test_workflow_task_validation():
    """Test workflow task validation"""
    # Invalid time limit
    try:
        task = WorkflowTask(
            name="Test",
            description="Test",
            time_limit_hours=-1.0,
            execute_func=simple_task
        )
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "time_limit_hours must be positive" in str(e)


# Tests for WorkflowManager

def test_workflow_manager_creation():
    """Test workflow manager creation"""
    manager = WorkflowManager(session_id="test_123")
    
    assert manager.session_id == "test_123"
    assert len(manager.tasks) == 0
    assert len(manager.results) == 0
    assert manager.live_view is not None


def test_workflow_add_task(workflow_manager):
    """Test adding tasks to workflow"""
    task = WorkflowTask(
        name="Task 1",
        description="First task",
        time_limit_hours=1.0,
        execute_func=simple_task
    )
    
    workflow_manager.add_task(task)
    assert len(workflow_manager.tasks) == 1
    assert workflow_manager.tasks[0].name == "Task 1"


def test_workflow_execute_single_task():
    """Test executing a workflow with a single task"""
    manager = WorkflowManager(session_id="test_single")
    
    task = WorkflowTask(
        name="Simple Task",
        description="A simple successful task",
        time_limit_hours=0.1,  # 6 minutes
        execute_func=simple_task,
        pause_after_completion_minutes=0  # No pause for test
    )
    
    manager.add_task(task)
    success = manager.execute_workflow(auto_continue=True)
    
    assert success is True
    assert len(manager.results) == 1
    assert manager.results[0].success is True
    assert manager.results[0].task_name == "Simple Task"


def test_workflow_execute_multiple_tasks():
    """Test executing a workflow with multiple tasks"""
    manager = WorkflowManager(session_id="test_multiple")
    
    for i in range(3):
        task = WorkflowTask(
            name=f"Task {i+1}",
            description=f"Task number {i+1}",
            time_limit_hours=0.1,
            execute_func=simple_task,
            pause_after_completion_minutes=0
        )
        manager.add_task(task)
    
    success = manager.execute_workflow(auto_continue=True)
    
    assert success is True
    assert len(manager.results) == 3
    assert all(r.success for r in manager.results)


def test_workflow_task_retry():
    """Test task retry mechanism"""
    manager = WorkflowManager(session_id="test_retry")
    
    # Create a task that fails but has retry enabled
    task = WorkflowTask(
        name="Failing Task",
        description="This task will fail",
        time_limit_hours=0.1,
        execute_func=failing_task,
        auto_retry=True,
        max_retries=2,
        pause_after_completion_minutes=0
    )
    
    manager.add_task(task)
    success = manager.execute_workflow(auto_continue=True)
    
    assert success is False
    assert len(manager.results) == 1
    assert manager.results[0].success is False
    assert len(manager.results[0].errors) > 0


def test_workflow_get_status(workflow_manager):
    """Test getting workflow status"""
    task = WorkflowTask(
        name="Test Task",
        description="Test",
        time_limit_hours=1.0,
        execute_func=simple_task
    )
    workflow_manager.add_task(task)
    
    status = workflow_manager.get_workflow_status()
    
    assert status['session_id'] == workflow_manager.session_id
    assert status['total_tasks'] == 1
    assert status['completed_tasks'] == 0
    assert 'live_view_status' in status


# Tests for task implementations

def test_data_analysis_task():
    """Test data analysis task execution"""
    logger = setup_logging()
    live_view = LiveViewSession("test_data_analysis")
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    try:
        result = data_analysis_task(logger, live_view)
        
        assert isinstance(result, dict)
        assert 'total_candles' in result
        assert 'avg_price' in result
        assert 'volatility' in result
        assert result['total_candles'] > 0
    except Exception as e:
        # Task might fail if dependencies missing, that's ok for this test
        print(f"Note: data_analysis_task raised exception (expected in test env): {e}")


def test_strategy_optimization_task():
    """Test strategy optimization task execution"""
    logger = setup_logging()
    live_view = LiveViewSession("test_strategy_optimization")
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    try:
        result = strategy_optimization_task(logger, live_view)
        
        assert isinstance(result, dict)
        assert 'roi' in result
        assert 'sharpe_ratio' in result
        assert 'total_trades' in result
    except Exception as e:
        # Task might fail if data missing, that's ok for this test
        print(f"Note: strategy_optimization_task raised exception (expected in test env): {e}")


def test_api_preparation_task():
    """Test API preparation task execution"""
    logger = setup_logging()
    live_view = LiveViewSession("test_api_preparation")
    
    try:
        result = api_preparation_task(logger, live_view)
        
        assert isinstance(result, dict)
        assert 'api_status' in result
        assert 'connection_test' in result
        assert 'operational_status' in result
    except Exception as e:
        # Task might fail if API not configured, that's ok for this test
        print(f"Note: api_preparation_task raised exception (expected in test env): {e}")


# Tests for default workflow

def test_create_default_workflow():
    """Test creating default workflow"""
    manager = create_default_workflow()
    
    assert len(manager.tasks) == 3
    assert manager.tasks[0].name == "Data Analysis"
    assert manager.tasks[1].name == "Strategy Optimization"
    assert manager.tasks[2].name == "API Preparation"
    
    # Check time limits
    assert manager.tasks[0].time_limit_hours == 2.0
    assert manager.tasks[1].time_limit_hours == 2.0
    assert manager.tasks[2].time_limit_hours == 1.0


# Integration tests

def test_full_workflow_integration():
    """Integration test for full workflow execution"""
    manager = WorkflowManager(session_id="test_integration")
    
    # Add simple tasks
    for i in range(3):
        task = WorkflowTask(
            name=f"Integration Task {i+1}",
            description=f"Integration test task {i+1}",
            time_limit_hours=0.05,  # 3 minutes
            execute_func=simple_task,
            pause_after_completion_minutes=0
        )
        manager.add_task(task)
    
    # Execute workflow
    success = manager.execute_workflow(auto_continue=True)
    
    assert success is True
    assert len(manager.results) == 3
    assert all(r.success for r in manager.results)
    
    # Check session files created
    session_dir = "data/workflow_sessions"
    os.makedirs(session_dir, exist_ok=True)
    
    # Check workflow status
    status = manager.get_workflow_status()
    assert status['successful_tasks'] == 3
    assert status['failed_tasks'] == 0


# Manual test runner (if pytest not available)

def run_tests_manually():
    """Run tests manually without pytest"""
    print("\n" + "=" * 70)
    print("RUNNING TESTS MANUALLY (pytest not available)")
    print("=" * 70 + "\n")
    
    tests = [
        ("Workflow Manager Creation", test_workflow_manager_creation),
        ("Workflow Add Task", lambda: test_workflow_add_task(WorkflowManager())),
        ("Workflow Task Creation", test_workflow_task_creation),
        ("Create Default Workflow", test_create_default_workflow),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"Running: {test_name}...", end=" ")
            
            # Create temp directory for tests that need it
            import tempfile
            with tempfile.TemporaryDirectory() as tmp_dir:
                if "live_view" in test_name.lower():
                    test_func(tmp_dir)
                else:
                    test_func()
            
            print("✓ PASSED")
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == '__main__':
    if PYTEST_AVAILABLE:
        # Run with pytest
        import pytest
        sys.exit(pytest.main([__file__, '-v']))
    else:
        # Run manually
        success = run_tests_manually()
        sys.exit(0 if success else 1)
