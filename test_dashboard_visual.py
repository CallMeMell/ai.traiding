#!/usr/bin/env python3
"""
test_dashboard_visual.py - Visual Test for Dashboard
====================================================

Starts the dashboard and adds demo tasks for visual verification.
"""

import time
import threading
from dashboard import add_task, update_task, start_web_dashboard
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate_demo_tasks():
    """Populate dashboard with demo tasks"""
    # Wait for dashboard to start
    time.sleep(3)
    
    logger.info("Adding demo tasks...")
    
    # Add a completed task
    task1 = add_task(
        "Historical Backtest - Golden Cross",
        "backtest",
        "Completed backtest on BTCUSDT 2023"
    )
    for i in range(0, 101, 25):
        update_task(task1, progress=i)
        time.sleep(0.1)
    update_task(task1, status='completed', details="Backtest completed - Win rate: 68%")
    logger.info(f"Task {task1} completed")
    
    # Add running tasks with different progress levels
    task2 = add_task(
        "Parameter Optimization",
        "optimization",
        "Testing 100 parameter combinations"
    )
    update_task(task2, progress=35, details="Testing combination 35/100")
    logger.info(f"Task {task2} at 35%")
    
    task3 = add_task(
        "Live Paper Trading",
        "simulation",
        "Simulating trades on 3 trading pairs"
    )
    update_task(task3, progress=62, details="Monitoring BTCUSDT, ETHUSDT, BNBUSDT")
    logger.info(f"Task {task3} at 62%")
    
    task4 = add_task(
        "Strategy Validation",
        "backtest",
        "Validating on out-of-sample data"
    )
    update_task(task4, progress=18, details="Loading validation dataset")
    logger.info(f"Task {task4} at 18%")
    
    # Add a failed task
    task5 = add_task(
        "Market Data Download",
        "backtest",
        "Downloading SOLUSDT historical data"
    )
    update_task(task5, progress=45, details="Downloaded 450MB / 1GB")
    time.sleep(0.5)
    update_task(task5, status='failed', details="Error: API rate limit exceeded")
    logger.info(f"Task {task5} failed")
    
    # Add a queued task
    task6 = add_task(
        "Scheduled Backtest",
        "backtest",
        "Waiting for previous tasks to complete"
    )
    update_task(task6, status='queued', progress=0)
    logger.info(f"Task {task6} queued")
    
    logger.info("Demo tasks added successfully!")
    logger.info("Open http://localhost:5000 and click 'Progress Monitor' to see tasks")
    
    # Keep some tasks updating
    for i in range(10):
        time.sleep(5)
        # Update running tasks
        if task2:
            prog = min(100, 35 + (i * 6))
            update_task(task2, progress=prog, details=f"Testing combination {35 + (i * 6)}/100")
        if task3:
            prog = min(100, 62 + (i * 3))
            update_task(task3, progress=prog, details=f"Monitored {62 + (i * 30)} trades")
        if task4:
            prog = min(100, 18 + (i * 8))
            update_task(task4, progress=prog, details=f"Validating epoch {i+1}/10")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  🚀 Starting Dashboard with Demo Tasks")
    print("=" * 70)
    print("\nThis will:")
    print("  1. Start the web dashboard on http://localhost:5000")
    print("  2. Add demo tasks with various states")
    print("  3. Keep some tasks updating to show real-time features")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 70 + "\n")
    
    # Start task population in background
    task_thread = threading.Thread(target=populate_demo_tasks, daemon=True)
    task_thread.start()
    
    # Start dashboard (this will block)
    try:
        start_web_dashboard(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
