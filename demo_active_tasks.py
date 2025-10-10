#!/usr/bin/env python3
"""
demo_active_tasks.py - Demonstration of Active Task Tracking
==============================================================

This demo shows how to use the active task tracking feature
to monitor ongoing operations in the trading bot dashboard.
"""

import time
import logging
from datetime import datetime
from dashboard import add_task, update_task, remove_task

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_single_task():
    """Demo 1: Single task with progress updates"""
    print("\n" + "=" * 70)
    print("  📊 DEMO 1: Single Task with Progress Updates")
    print("=" * 70)
    
    # Add a task
    task_id = add_task(
        task_name="Running Backtest - Golden Cross Strategy",
        task_type="backtest",
        details="Testing on BTCUSDT from 2023-01-01 to 2023-12-31"
    )
    print(f"\n✓ Task created with ID: {task_id}")
    
    # Simulate progress updates
    for progress in [0, 25, 50, 75, 100]:
        print(f"  Progress: {progress}%")
        update_task(task_id, progress=progress)
        time.sleep(1)
    
    # Mark as completed
    update_task(task_id, status="completed", details="Backtest completed successfully")
    print("✓ Task completed!")
    
    # Keep completed task visible for a moment
    time.sleep(2)


def demo_multiple_tasks():
    """Demo 2: Multiple concurrent tasks"""
    print("\n" + "=" * 70)
    print("  📊 DEMO 2: Multiple Concurrent Tasks")
    print("=" * 70)
    
    # Start multiple tasks
    task_ids = []
    
    print("\n✓ Starting multiple tasks...")
    task1 = add_task(
        task_name="Backtest - Strategy A",
        task_type="backtest",
        details="Testing RSI strategy on ETHUSDT"
    )
    task_ids.append(task1)
    
    task2 = add_task(
        task_name="Parameter Optimization",
        task_type="optimization",
        details="Optimizing MA periods for Golden Cross"
    )
    task_ids.append(task2)
    
    task3 = add_task(
        task_name="Simulated Trading",
        task_type="simulation",
        details="Running live simulation on testnet"
    )
    task_ids.append(task3)
    
    print(f"  Created {len(task_ids)} tasks")
    
    # Update tasks at different rates
    for i in range(10):
        update_task(task1, progress=min(100, (i + 1) * 10))
        update_task(task2, progress=min(100, (i + 1) * 8))
        update_task(task3, progress=min(100, (i + 1) * 12))
        print(f"  Iteration {i + 1}: Tasks progressing...")
        time.sleep(1)
    
    # Complete tasks
    update_task(task1, status="completed")
    print("  ✓ Task 1 completed")
    time.sleep(0.5)
    
    update_task(task2, status="completed")
    print("  ✓ Task 2 completed")
    time.sleep(0.5)
    
    update_task(task3, status="completed")
    print("  ✓ Task 3 completed")
    
    print("\n✓ All tasks completed!")
    time.sleep(2)


def demo_failed_task():
    """Demo 3: Task that fails"""
    print("\n" + "=" * 70)
    print("  📊 DEMO 3: Task Failure Handling")
    print("=" * 70)
    
    task_id = add_task(
        task_name="Live Trading - High Risk Strategy",
        task_type="live_trading",
        details="Attempting connection to broker"
    )
    print(f"\n✓ Task created with ID: {task_id}")
    
    # Simulate progress
    for progress in [0, 20, 40]:
        print(f"  Progress: {progress}%")
        update_task(task_id, progress=progress)
        time.sleep(1)
    
    # Simulate failure
    print("  ❌ Task failed!")
    update_task(
        task_id, 
        status="failed", 
        details="Connection to broker failed - API key invalid"
    )
    
    time.sleep(2)


def demo_queued_tasks():
    """Demo 4: Queued tasks"""
    print("\n" + "=" * 70)
    print("  📊 DEMO 4: Queued Tasks")
    print("=" * 70)
    
    # Add queued tasks
    print("\n✓ Adding tasks to queue...")
    task1 = add_task(
        task_name="Batch Backtest - Strategy 1",
        task_type="backtest",
        details="Queued for execution"
    )
    update_task(task1, status="queued")
    
    task2 = add_task(
        task_name="Batch Backtest - Strategy 2",
        task_type="backtest",
        details="Queued for execution"
    )
    update_task(task2, status="queued")
    
    task3 = add_task(
        task_name="Batch Backtest - Strategy 3",
        task_type="backtest",
        details="Queued for execution"
    )
    update_task(task3, status="queued")
    
    print("  Created 3 queued tasks")
    time.sleep(2)
    
    # Process queue
    for i, task_id in enumerate([task1, task2, task3], 1):
        print(f"\n  Processing task {i}...")
        update_task(task_id, status="running", details=f"Now executing strategy {i}")
        
        for progress in range(0, 101, 20):
            update_task(task_id, progress=progress)
            time.sleep(0.5)
        
        update_task(task_id, status="completed")
        print(f"  ✓ Task {i} completed")
    
    print("\n✓ All queued tasks processed!")
    time.sleep(2)


def demo_continuous_monitoring():
    """Demo 5: Continuous monitoring simulation"""
    print("\n" + "=" * 70)
    print("  📊 DEMO 5: Continuous Monitoring (20 seconds)")
    print("=" * 70)
    
    print("\nThis demo will run for 20 seconds.")
    print("Open the dashboard in your browser to see tasks update in real-time!")
    print("Dashboard URL: http://localhost:5000")
    print("\nStarting tasks...\n")
    
    # Long-running task
    monitor_task = add_task(
        task_name="Live Market Monitoring",
        task_type="simulation",
        details="Monitoring BTCUSDT, ETHUSDT for trading signals"
    )
    
    # Periodic task
    optimization_task = add_task(
        task_name="Strategy Optimization",
        task_type="optimization",
        details="Running parameter grid search"
    )
    
    # Update tasks over 20 seconds
    for i in range(20):
        # Update monitoring task (slower progress)
        monitor_progress = min(100, (i + 1) * 5)
        update_task(
            monitor_task, 
            progress=monitor_progress,
            details=f"Monitoring - {i + 1} updates processed"
        )
        
        # Update optimization task (faster progress)
        opt_progress = min(100, (i + 1) * 10)
        update_task(
            optimization_task,
            progress=opt_progress,
            details=f"Testing parameter set {i + 1}/20"
        )
        
        print(f"  Tick {i + 1}/20 - Monitor: {monitor_progress}%, Optimization: {opt_progress}%")
        time.sleep(1)
    
    # Complete tasks
    update_task(monitor_task, status="completed", details="Monitoring session completed")
    update_task(optimization_task, status="completed", details="Found optimal parameters")
    
    print("\n✓ Continuous monitoring demo completed!")
    print("  Tasks will remain visible in dashboard for 1 hour")


def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("  🚀 Active Task Tracking - Demo Application")
    print("=" * 70)
    print("\nThis demo showcases the Active Task Tracking feature:")
    print("- Add tasks to track ongoing operations")
    print("- Update task progress in real-time")
    print("- Mark tasks as completed, failed, or queued")
    print("- View tasks in the Dashboard View Session page")
    
    print("\n📋 Available Demos:")
    print("  1. Single task with progress updates")
    print("  2. Multiple concurrent tasks")
    print("  3. Task failure handling")
    print("  4. Queued tasks")
    print("  5. Continuous monitoring (20 seconds)")
    print("  0. Run all demos")
    
    # Check if we should run specific demo
    import sys
    if len(sys.argv) > 1:
        demo_arg = sys.argv[1]
        
        if demo_arg == '1':
            demo_single_task()
        elif demo_arg == '2':
            demo_multiple_tasks()
        elif demo_arg == '3':
            demo_failed_task()
        elif demo_arg == '4':
            demo_queued_tasks()
        elif demo_arg == '5':
            demo_continuous_monitoring()
        elif demo_arg == '0':
            demo_single_task()
            demo_multiple_tasks()
            demo_failed_task()
            demo_queued_tasks()
            demo_continuous_monitoring()
        else:
            print(f"\nInvalid demo selection: {demo_arg}")
            print("Usage: python demo_active_tasks.py [1-5|0]")
            return
    else:
        # Interactive mode
        try:
            choice = input("\nSelect demo (0-5): ").strip()
            
            if choice == '1':
                demo_single_task()
            elif choice == '2':
                demo_multiple_tasks()
            elif choice == '3':
                demo_failed_task()
            elif choice == '4':
                demo_queued_tasks()
            elif choice == '5':
                demo_continuous_monitoring()
            elif choice == '0':
                demo_single_task()
                demo_multiple_tasks()
                demo_failed_task()
                demo_queued_tasks()
                demo_continuous_monitoring()
            else:
                print("Invalid selection")
        except KeyboardInterrupt:
            print("\n\nDemo interrupted by user")
    
    print("\n" + "=" * 70)
    print("  ✨ Demo Complete!")
    print("=" * 70)
    print("\nTo use task tracking in your own code:")
    print("  from dashboard import add_task, update_task, remove_task")
    print("  task_id = add_task('My Task', 'backtest', 'Details here')")
    print("  update_task(task_id, progress=50)")
    print("  update_task(task_id, status='completed')")


if __name__ == "__main__":
    main()
