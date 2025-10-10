# Retry & Backoff Guide

## Overview

The automation system includes robust retry and backoff mechanisms to handle transient failures gracefully. This guide explains how these mechanisms work and how to configure them.

## Features

### 1. Exponential Backoff

Both the `AutomationRunner` and `SystemOrchestrator` implement exponential backoff for retry attempts:

- **Initial Delay**: 1-2 seconds (configurable)
- **Growth Factor**: 2x (doubles with each attempt)
- **Max Delay**: 30 seconds (prevents excessive wait times)
- **Max Retries**: 3 attempts by default

### 2. Retry Logic Locations

#### AutomationRunner (`automation/runner.py`)

The runner provides a `_retry_with_backoff()` method for retrying operations with exponential backoff:

```python
result = runner._retry_with_backoff(
    func=operation_function,
    max_retries=3,
    base_delay=1.0,
    max_delay=30.0,
    operation_name="data_load"
)
```

Features:
- Logs each retry attempt
- Emits `autocorrect_attempt` events for monitoring
- Raises exception if all retries fail

#### SystemOrchestrator (`system/orchestrator.py`)

The orchestrator implements phase-level recovery with automatic retries:

```python
recovery_result = orchestrator._attempt_recovery(phase, error)
```

Features:
- Automatically retries failed phases up to 3 times
- Uses exponential backoff (2s, 4s, 8s, capped at 30s)
- Logs all recovery attempts with detailed information
- Returns structured recovery result

## Usage Examples

### Example 1: Retry in AutomationRunner

```python
from automation.runner import AutomationRunner

runner = AutomationRunner()

def load_data():
    # May fail due to network issues
    return fetch_market_data()

# Will retry up to 3 times with exponential backoff
result = runner._retry_with_backoff(
    load_data,
    max_retries=3,
    operation_name="market_data_fetch"
)
```

### Example 2: Phase Recovery in Orchestrator

```python
from system.orchestrator import SystemOrchestrator

orchestrator = SystemOrchestrator(
    dry_run=True,
    enable_recovery=True  # Enable automatic recovery
)

# If a phase fails, it will automatically retry
results = orchestrator.run()

# Check recovery attempts
for phase_result in results['phases']:
    if 'recovery' in phase_result:
        print(f"Phase recovered after {len(phase_result['recovery']['attempts'])} attempts")
```

## Event Logging

### Autocorrect Events

When retries occur, `autocorrect_attempt` events are logged to `events.jsonl`:

```json
{
  "timestamp": "2025-10-10T19:11:43.482629",
  "session_id": "4786a9a2-c5bf-41ca-a26e-e1ae5d01f41c",
  "type": "autocorrect_attempt",
  "phase": "data_phase",
  "level": "warning",
  "message": "Autocorrect attempt 1: Error in data_load: Connection timeout",
  "details": {
    "attempt_number": 1,
    "reason": "Error in data_load: Connection timeout",
    "result": "retrying"
  }
}
```

### Recovery Events

Phase recovery attempts are logged in phase results:

```json
{
  "phase": "data_preparation",
  "status": "success",
  "recovery": {
    "attempted": true,
    "success": true,
    "message": "Recovery successful on attempt 2",
    "attempts": [
      {
        "attempt": 1,
        "delay": 2,
        "status": "error",
        "error": "Connection refused"
      },
      {
        "attempt": 2,
        "delay": 4,
        "status": "success",
        "result": {"status": "success"}
      }
    ]
  }
}
```

## Configuration

### Retry Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_retries` | 3 | Maximum number of retry attempts |
| `base_delay` | 1.0-2.0s | Initial delay before first retry |
| `max_delay` | 30s | Maximum delay between retries |

### Backoff Calculation

The delay between retries is calculated as:

```python
delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
```

For `base_delay=2s`:
- Attempt 1: 2 seconds
- Attempt 2: 4 seconds
- Attempt 3: 8 seconds
- Attempt 4+: 30 seconds (capped)

## Best Practices

### 1. Use Appropriate Operation Names

Always provide descriptive operation names for better debugging:

```python
# Good
runner._retry_with_backoff(func, operation_name="binance_api_connect")

# Bad
runner._retry_with_backoff(func, operation_name="op1")
```

### 2. Handle Non-Retryable Errors

Not all errors should be retried. Consider catching and handling specific errors:

```python
def operation():
    try:
        return risky_operation()
    except ConfigurationError:
        # Don't retry configuration errors
        raise
    except TemporaryError:
        # Allow retry for temporary errors
        raise
```

### 3. Monitor Autocorrect Events

Check `events.jsonl` for `autocorrect_attempt` events to identify patterns:

```bash
# Count retry attempts
grep '"type": "autocorrect_attempt"' data/session/events.jsonl | wc -l

# View failed operations
grep '"type": "autocorrect_attempt"' data/session/events.jsonl | grep '"result": "failed"'
```

### 4. Adjust Retry Configuration

For operations that consistently need more retries:

```python
# Increase retries for unreliable operations
result = runner._retry_with_backoff(
    flaky_operation,
    max_retries=5,  # More attempts
    base_delay=0.5,  # Faster initial retry
    max_delay=60.0   # Allow longer delays
)
```

## Testing

### Test Retry Logic

```python
def test_retry_with_simulated_failure():
    attempt_count = {'count': 0}
    
    def flaky_operation():
        attempt_count['count'] += 1
        if attempt_count['count'] < 2:
            raise ValueError("Simulated failure")
        return {'status': 'success'}
    
    # Should succeed on second attempt
    result = runner._retry_with_backoff(
        flaky_operation,
        max_retries=3,
        base_delay=0.1  # Short delay for testing
    )
    
    assert result['status'] == 'success'
    assert attempt_count['count'] == 2
```

See `test_retry_backoff.py` and `test_orchestrator_recovery.py` for comprehensive examples.

## Troubleshooting

### Problem: All Retries Failing

**Check:**
1. Is the error persistent (not transient)?
2. Are retry limits too low?
3. Is the base delay too short for the operation?

**Solution:**
- Increase `max_retries` for operations that need more attempts
- Increase `base_delay` if the service needs more time to recover
- Check logs for the specific error causing failures

### Problem: Too Many Retries

**Check:**
1. Are operations failing unnecessarily?
2. Is the service consistently unavailable?

**Solution:**
- Fix underlying service issues first
- Add specific error handling to avoid retrying non-transient errors
- Consider circuit breaker pattern for persistent failures

## Related Files

- `automation/runner.py` - Runner retry implementation
- `system/orchestrator.py` - Orchestrator recovery implementation
- `test_retry_backoff.py` - Runner retry tests
- `test_orchestrator_recovery.py` - Orchestrator recovery tests
- `test_integration_workflow.py` - Full workflow integration test

## Summary

The retry/backoff system provides:
- ✅ Automatic retry with exponential backoff
- ✅ Detailed logging of all retry attempts
- ✅ Configurable retry parameters
- ✅ Event-based monitoring
- ✅ Phase-level recovery in orchestrator
- ✅ Operation-level retry in runner

This ensures the system is resilient to transient failures while maintaining observability.
