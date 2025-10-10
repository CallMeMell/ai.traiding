#!/usr/bin/env python3
"""
demo_automated_workflow.py - Demo of Automated Workflow System
==============================================================
Demonstrates the automated trading bot workflow preparation system
with simplified tasks for demonstration purposes.
"""
import os
import sys
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automated_workflow import (
    WorkflowManager,
    WorkflowTask,
    LiveViewSession,
    create_default_workflow
)
from utils import setup_logging


def print_separator(title: str):
    """Print a formatted separator"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_task_1(logger, live_view):
    """Demo Task 1: Quick data validation"""
    logger.info("Starting Demo Task 1: Data Validation")
    live_view.add_update('progress', "Validating data...")
    
    # Simulate some work
    steps = ["Loading data", "Checking format", "Validating values", "Computing stats"]
    
    for i, step in enumerate(steps, 1):
        logger.info(f"  Step {i}/{len(steps)}: {step}")
        live_view.update_task_status("Demo Task 1", step, i / len(steps) * 100)
        time.sleep(0.5)
    
    result = {
        "total_records": 5000,
        "data_quality": "excellent",
        "validation_time": 2.0
    }
    
    logger.info(f"✅ Demo Task 1 completed: {result}")
    live_view.add_update('success', "Data validation completed", result)
    
    return result


def demo_task_2(logger, live_view):
    """Demo Task 2: Strategy testing"""
    logger.info("Starting Demo Task 2: Strategy Testing")
    live_view.add_update('progress', "Testing strategy...")
    
    # Simulate strategy testing
    steps = ["Initializing strategy", "Running backtest", "Calculating metrics", "Validating results"]
    
    for i, step in enumerate(steps, 1):
        logger.info(f"  Step {i}/{len(steps)}: {step}")
        live_view.update_task_status("Demo Task 2", step, i / len(steps) * 100)
        time.sleep(0.5)
    
    result = {
        "roi": 12.5,
        "sharpe_ratio": 1.8,
        "total_trades": 150,
        "win_rate": 65.0
    }
    
    logger.info(f"✅ Demo Task 2 completed: {result}")
    live_view.add_update('success', "Strategy testing completed", result)
    
    return result


def demo_task_3(logger, live_view):
    """Demo Task 3: API check"""
    logger.info("Starting Demo Task 3: API Check")
    live_view.add_update('progress', "Checking API...")
    
    # Simulate API checking
    steps = ["Checking credentials", "Testing connection", "Validating permissions", "Preparing deployment"]
    
    for i, step in enumerate(steps, 1):
        logger.info(f"  Step {i}/{len(steps)}: {step}")
        live_view.update_task_status("Demo Task 3", step, i / len(steps) * 100)
        time.sleep(0.5)
    
    result = {
        "api_configured": True,
        "connection_status": "success",
        "ready_for_deployment": True
    }
    
    logger.info(f"✅ Demo Task 3 completed: {result}")
    live_view.add_update('success', "API check completed", result)
    
    return result


def demo_simple_workflow():
    """Demo: Simple workflow with 3 tasks"""
    print_separator("DEMO: Simple Workflow Execution")
    
    print("Creating workflow with 3 demo tasks...\n")
    
    manager = WorkflowManager(session_id=f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    # Add demo tasks (with very short time limits for demo)
    manager.add_task(WorkflowTask(
        name="Demo Task 1: Data Validation",
        description="Quick data validation check",
        time_limit_hours=0.05,  # 3 minutes
        execute_func=demo_task_1,
        pause_after_completion_minutes=0.5  # 30 seconds pause
    ))
    
    manager.add_task(WorkflowTask(
        name="Demo Task 2: Strategy Testing",
        description="Quick strategy backtest",
        time_limit_hours=0.05,  # 3 minutes
        execute_func=demo_task_2,
        pause_after_completion_minutes=0.5  # 30 seconds pause
    ))
    
    manager.add_task(WorkflowTask(
        name="Demo Task 3: API Check",
        description="Quick API connectivity check",
        time_limit_hours=0.05,  # 3 minutes
        execute_func=demo_task_3,
        pause_after_completion_minutes=0  # No pause after last task
    ))
    
    print(f"Session ID: {manager.session_id}")
    print(f"Total tasks: {len(manager.tasks)}")
    print(f"\nStarting workflow execution...\n")
    
    # Execute workflow
    success = manager.execute_workflow(auto_continue=True)
    
    print("\n" + "=" * 70)
    if success:
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
    else:
        print("⚠️  WORKFLOW COMPLETED WITH ERRORS")
    print("=" * 70)
    
    # Show results
    print("\n📊 Task Results:\n")
    for i, result in enumerate(manager.results, 1):
        status_icon = "✅" if result.success else "❌"
        print(f"{status_icon} Task {i}: {result.task_name}")
        print(f"   Duration: {result.duration_seconds:.1f}s")
        print(f"   Status: {result.status.value}")
        if result.data:
            print(f"   Data: {result.data}")
        print()
    
    # Show session info
    print("📁 Session Files:")
    print(f"   Log: logs/workflow_{manager.session_id}.log")
    print(f"   Session: data/workflow_sessions/{manager.session_id}.json")
    print(f"   Summary: data/workflow_sessions/{manager.session_id}_summary.json")


def demo_live_view_session():
    """Demo: Live view session features"""
    print_separator("DEMO: Live View Session")
    
    session = LiveViewSession("demo_session")
    
    print(f"Session ID: {session.session_id}")
    print(f"Start time: {session.start_time}\n")
    
    # Add various updates
    print("Adding progress updates...\n")
    
    session.add_update('info', "Workflow started")
    time.sleep(0.5)
    
    session.update_task_status("Data Analysis", "running", 25)
    time.sleep(0.5)
    
    session.update_task_status("Data Analysis", "running", 50)
    time.sleep(0.5)
    
    session.update_task_status("Data Analysis", "running", 75)
    time.sleep(0.5)
    
    session.update_task_status("Data Analysis", "completed", 100)
    time.sleep(0.5)
    
    session.add_update('success', "Task completed successfully", {
        'duration': 30.5,
        'records_processed': 5000
    })
    
    # Show status
    print("\n📊 Session Status:\n")
    status = session.get_status()
    for key, value in status.items():
        if key != 'latest_updates':
            print(f"   {key}: {value}")
    
    print("\n📝 Latest Updates:\n")
    for update in status['latest_updates']:
        print(f"   [{update['timestamp']}] {update['type']}: {update['message']}")


def demo_workflow_status():
    """Demo: Workflow status tracking"""
    print_separator("DEMO: Workflow Status Tracking")
    
    manager = WorkflowManager(session_id="demo_status")
    
    # Add tasks
    manager.add_task(WorkflowTask(
        name="Task 1",
        description="First task",
        time_limit_hours=1.0,
        execute_func=demo_task_1
    ))
    
    manager.add_task(WorkflowTask(
        name="Task 2",
        description="Second task",
        time_limit_hours=1.0,
        execute_func=demo_task_2
    ))
    
    # Show initial status
    print("Initial Workflow Status:\n")
    status = manager.get_workflow_status()
    for key, value in status.items():
        if key != 'live_view_status':
            print(f"   {key}: {value}")
    
    print("\n✓ Workflow configured and ready to execute")


def demo_full_workflow_info():
    """Demo: Show full default workflow information"""
    print_separator("DEMO: Default Workflow Configuration")
    
    manager = create_default_workflow()
    
    print(f"Session ID: {manager.session_id}")
    print(f"Total Tasks: {len(manager.tasks)}\n")
    
    total_time = 0
    
    for i, task in enumerate(manager.tasks, 1):
        print(f"Task {i}: {task.name}")
        print(f"   Description: {task.description}")
        print(f"   Time Limit: {task.time_limit_hours} hours")
        print(f"   Auto Retry: {task.auto_retry}")
        print(f"   Max Retries: {task.max_retries}")
        print(f"   Pause After: {task.pause_after_completion_minutes} minutes")
        print()
        total_time += task.time_limit_hours
    
    print(f"Total Estimated Time: {total_time} hours")
    print(f"Total Pause Time: {sum(t.pause_after_completion_minutes for t in manager.tasks)} minutes")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  🤖 AUTOMATED WORKFLOW SYSTEM - DEMO")
    print("=" * 70)
    
    demos = [
        ("Full Workflow Configuration", demo_full_workflow_info),
        ("Live View Session", demo_live_view_session),
        ("Workflow Status Tracking", demo_workflow_status),
        ("Simple Workflow Execution", demo_simple_workflow),
    ]
    
    print("\nAvailable Demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  {len(demos) + 1}. Run All Demos")
    print("  0. Exit")
    
    try:
        choice = input("\nSelect demo (0-{}): ".format(len(demos) + 1))
        choice = int(choice)
        
        if choice == 0:
            print("Exiting...")
            return
        elif choice == len(demos) + 1:
            # Run all demos
            for name, demo_func in demos:
                demo_func()
                input("\nPress Enter to continue to next demo...")
        elif 1 <= choice <= len(demos):
            # Run selected demo
            demos[choice - 1][1]()
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    print_separator("DEMO COMPLETED")
    print("✅ Demo completed successfully!")
    print("\n📖 Next Steps:")
    print("  1. Review the documentation: AUTOMATED_WORKFLOW_GUIDE.md")
    print("  2. Try the full workflow: python automated_workflow.py")
    print("  3. Integrate with your trading bot")
    print("  4. View workflow sessions in the web dashboard")


if __name__ == '__main__':
    main()
