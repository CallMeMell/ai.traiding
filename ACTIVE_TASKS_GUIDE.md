# Active Task Tracking - User Guide

## Overview

The Active Task Tracking feature provides real-time visibility of all ongoing operations in the trading bot dashboard. Tasks are displayed in the "View Session" page (Progress Monitor) with visual indicators showing their status and progress.

## Features

✅ **Real-time Monitoring**: Tasks update automatically every 5 seconds  
✅ **Visual Indicators**: Status badges (Running, Completed, Failed, Queued)  
✅ **Progress Bars**: Dynamic progress bars for running tasks (0-100%)  
✅ **Task Details**: View task type, details, start time, and status  
✅ **Auto-cleanup**: Completed/failed tasks auto-remove after 1 hour  

## Viewing Active Tasks

1. Open the dashboard at `http://localhost:5000`
2. Click on "Progress Monitor" in the navigation
3. The "Active Tasks" section appears at the top
4. Tasks automatically refresh every 5 seconds
5. Manually refresh by clicking the "Refresh" button

## Task Status Indicators

| Status | Badge Color | Icon | Description |
|--------|------------|------|-------------|
| **Running** | Blue | Spinning spinner | Task is actively executing |
| **Completed** | Green | Check circle | Task finished successfully |
| **Failed** | Red | X circle | Task encountered an error |
| **Queued** | Yellow | Clock | Task is waiting to start |

## Task Types

- **backtest**: Backtesting strategies with historical data
- **simulation**: Live simulated trading
- **optimization**: Parameter optimization and grid search
- **live_trading**: Real trading with live market data

## Integration Guide

### Adding Task Tracking to Your Module

```python
# Import the task tracking functions
from dashboard import add_task, update_task, remove_task

def run_backtest(strategy_name, data):
    """Example: Backtest with task tracking"""
    
    # 1. Add task when starting
    task_id = add_task(
        task_name=f"Backtest - {strategy_name}",
        task_type="backtest",
        details=f"Testing on {len(data)} candles"
    )
    
    try:
        # 2. Update progress as operation proceeds
        for i, candle in enumerate(data):
            # Process your data...
            process_candle(candle)
            
            # Update progress
            progress = int((i / len(data)) * 100)
            update_task(task_id, progress=progress)
            
            # Optional: Update details
            if i % 100 == 0:
                update_task(task_id, details=f"Processed {i}/{len(data)} candles")
        
        # 3. Mark as completed
        update_task(
            task_id, 
            status="completed",
            details=f"Backtest completed - Win rate: 65%"
        )
        
    except Exception as e:
        # 4. Mark as failed on error
        update_task(
            task_id,
            status="failed",
            details=f"Error: {str(e)}"
        )
```

### API Functions

#### `add_task(task_name, task_type, details="")`
Adds a new task to the active task list.

**Parameters:**
- `task_name` (str): Human-readable name for the task
- `task_type` (str): Type of task (backtest, simulation, optimization, live_trading)
- `details` (str, optional): Additional information about the task

**Returns:**
- `int`: Task ID for future updates

**Example:**
```python
task_id = add_task("Backtest Strategy A", "backtest", "Testing on BTCUSDT")
```

#### `update_task(task_id, progress=None, status=None, details=None)`
Updates an existing task's progress, status, or details.

**Parameters:**
- `task_id` (int): ID of the task to update
- `progress` (int, optional): Progress percentage (0-100)
- `status` (str, optional): New status (running, completed, failed, queued)
- `details` (str, optional): Updated details

**Returns:**
- `bool`: True if successful, False if task not found

**Example:**
```python
# Update progress
update_task(task_id, progress=50)

# Update status
update_task(task_id, status="completed")

# Update multiple fields
update_task(task_id, progress=100, status="completed", details="Success!")
```

#### `remove_task(task_id)`
Removes a task from the active task list.

**Parameters:**
- `task_id` (int): ID of the task to remove

**Example:**
```python
remove_task(task_id)
```

## REST API Endpoints

### GET `/api/active-tasks`
Retrieve all active tasks.

**Response:**
```json
{
    "tasks": [
        {
            "id": 1,
            "name": "Backtest - Golden Cross",
            "type": "backtest",
            "details": "Testing on BTCUSDT",
            "status": "running",
            "progress": 50,
            "started_at": "2025-10-10 01:05:29",
            "updated_at": "2025-10-10 01:05:45"
        }
    ],
    "count": 1,
    "last_update": "2025-10-10 01:05:50"
}
```

### POST `/api/active-tasks/add`
Add a new task (for testing/demo purposes).

**Request Body:**
```json
{
    "name": "My Task",
    "type": "backtest",
    "details": "Task details here"
}
```

**Response:**
```json
{
    "success": true,
    "task_id": 1,
    "message": "Task added successfully"
}
```

### POST `/api/active-tasks/<task_id>/update`
Update an existing task.

**Request Body:**
```json
{
    "progress": 75,
    "status": "running",
    "details": "Updated details"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Task updated successfully"
}
```

## Demo Scripts

### Run Demo Tasks
```bash
# Run all demos
python demo_active_tasks.py 0

# Run specific demo
python demo_active_tasks.py 1  # Single task
python demo_active_tasks.py 2  # Multiple tasks
python demo_active_tasks.py 3  # Failed task
python demo_active_tasks.py 4  # Queued tasks
python demo_active_tasks.py 5  # Continuous monitoring (20 seconds)
```

### Test Suite
```bash
# Run all tests
python test_active_tasks.py

# Expected output: All 13 tests pass
```

## Best Practices

1. **Always add tasks before operations start**
   ```python
   task_id = add_task("Operation Name", "type", "details")
   ```

2. **Update progress regularly (but not too frequently)**
   ```python
   # Update every 10-100 iterations, not every single one
   if i % 10 == 0:
       update_task(task_id, progress=int(i/total*100))
   ```

3. **Always mark completion or failure**
   ```python
   try:
       # Do work...
       update_task(task_id, status="completed")
   except Exception as e:
       update_task(task_id, status="failed", details=str(e))
   ```

4. **Provide meaningful details**
   ```python
   # Good
   update_task(task_id, details="Processed 500/1000 trades")
   
   # Bad
   update_task(task_id, details="Working...")
   ```

5. **Use appropriate task types**
   - `backtest`: Historical data testing
   - `simulation`: Paper trading / simulated live
   - `optimization`: Parameter tuning
   - `live_trading`: Real trading operations

## Troubleshooting

### Tasks not appearing in UI
- Ensure tasks are added from within the Flask process
- Check that the dashboard is running
- Verify the API endpoint returns tasks: `curl http://localhost:5000/api/active-tasks`

### Tasks disappearing too quickly
- Completed/failed tasks auto-clean after 1 hour
- Running tasks remain visible indefinitely
- Adjust cleanup time in `_get_active_tasks()` if needed

### Auto-refresh not working
- Check browser console for errors
- Verify the modal is open (refresh only works when View Session is visible)
- Check that the interval is running: Look for auto-refresh logs

## UI Customization

Task status colors can be customized in `static/css/features.css`:

```css
.status-running {
    background: rgba(102, 126, 234, 0.1);  /* Blue */
    color: var(--primary-color);
}

.status-completed {
    background: rgba(46, 204, 113, 0.1);  /* Green */
    color: var(--success-color);
}

.status-failed {
    background: rgba(231, 76, 60, 0.1);  /* Red */
    color: var(--danger-color);
}

.status-queued {
    background: rgba(241, 196, 15, 0.1);  /* Yellow */
    color: #f1c40f;
}
```

## Technical Details

- **Storage**: In-memory (resets when Flask restarts)
- **Refresh Rate**: 5 seconds automatic refresh
- **Cleanup**: Auto-removes tasks completed/failed > 1 hour ago
- **Thread Safety**: Basic thread safety via Python globals
- **Performance**: Minimal overhead, suitable for 100+ concurrent tasks

## Future Enhancements

- [ ] Persistent storage (database or file)
- [ ] WebSocket support for instant updates
- [ ] Task history and logs
- [ ] Task cancellation/pause functionality
- [ ] Task priority queuing
- [ ] Email/notification on task completion/failure
- [ ] Task execution time tracking
- [ ] Resource usage monitoring per task

## Support

For issues or questions:
1. Check the test suite: `python test_active_tasks.py`
2. Review demo scripts: `python demo_active_tasks.py`
3. Check API health: `curl http://localhost:5000/api/active-tasks`
4. Review implementation in `dashboard.py` (lines 31-698)

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Status**: ✅ Production Ready
