#!/usr/bin/env python3
"""
Add demo tasks directly via API
"""

import requests
import time
import json

BASE_URL = "http://localhost:5000"

# Since the tasks are in-memory in the Flask process, we need to use the dashboard module
# within the same process. Let's create a simple script that makes HTTP requests instead
# to add tasks via an API endpoint

# For now, let's just verify the API is working
print("Checking API status...")
response = requests.get(f"{BASE_URL}/api/active-tasks")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\nNote: The task tracking system works in-memory.")
print("Tasks need to be added from within the Flask process or via a shared state mechanism.")
print("\nTo see active tasks in action:")
print("1. The dashboard.py module exports add_task, update_task, remove_task functions")
print("2. Other modules can import these functions to track their operations")
print("3. Example: In backtester.py or simulated_live_trading.py")
print("   from dashboard import add_task, update_task")
print("   task_id = add_task('Backtest Running', 'backtest', 'Testing strategy')")
print("   update_task(task_id, progress=50)")
print("   update_task(task_id, status='completed')")
