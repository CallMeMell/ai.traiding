"""
scheduler.py - Phase Scheduler with Time Limits
==============================================
Scheduler for automation phases with wall-clock timeouts and pause support.
"""

import time
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PhaseScheduler:
    """
    Scheduler for automation phases with timeouts and pause support.
    """
    
    def __init__(self, max_pause_minutes: int = 10):
        """
        Initialize scheduler.
        
        Args:
            max_pause_minutes: Maximum pause duration in minutes
        """
        self.max_pause_minutes = max_pause_minutes
        self.current_phase = None
        self.phase_start_time = None
        self.metrics = {}
    
    def run_phase(self, phase_name: str, phase_func: Callable, 
                  timeout_seconds: int, on_event: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Run a phase with timeout.
        
        Args:
            phase_name: Name of the phase
            phase_func: Function to execute
            timeout_seconds: Maximum execution time in seconds
            on_event: Optional callback for events
            
        Returns:
            Dictionary with phase results
        """
        self.current_phase = phase_name
        self.phase_start_time = datetime.now()
        
        result = {
            'phase': phase_name,
            'status': 'success',
            'start_time': self.phase_start_time.isoformat(),
            'timeout_seconds': timeout_seconds,
            'error': None,
            'duration_seconds': 0
        }
        
        if on_event:
            on_event({
                'type': 'phase_start',
                'phase': phase_name,
                'timestamp': self.phase_start_time.isoformat()
            })
        
        try:
            # Execute phase with timeout monitoring
            start = time.time()
            end_time = start + timeout_seconds
            
            # Call the phase function
            phase_result = phase_func()
            
            elapsed = time.time() - start
            result['duration_seconds'] = elapsed
            
            # Check if we exceeded timeout
            if time.time() > end_time:
                result['status'] = 'timeout'
                result['error'] = f'Phase exceeded timeout of {timeout_seconds}s'
                logger.warning(f"Phase {phase_name} exceeded timeout")
            else:
                result['status'] = 'success'
                result['phase_result'] = phase_result
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            logger.error(f"Phase {phase_name} failed: {e}")
        
        finally:
            result['end_time'] = datetime.now().isoformat()
            
            if on_event:
                on_event({
                    'type': 'phase_end',
                    'phase': phase_name,
                    'status': result['status'],
                    'duration_seconds': result['duration_seconds'],
                    'timestamp': result['end_time']
                })
        
        self.metrics[phase_name] = result
        return result
    
    def pause_and_check(self, check_func: Callable, pause_seconds: int = 60,
                       on_event: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Pause and run self-check.
        
        Args:
            check_func: Function to run for self-check
            pause_seconds: Pause duration in seconds (max 10 minutes)
            on_event: Optional callback for events
            
        Returns:
            Dictionary with check results
        """
        # Cap pause at max allowed
        max_pause_seconds = self.max_pause_minutes * 60
        if pause_seconds > max_pause_seconds:
            logger.warning(f"Pause duration {pause_seconds}s exceeds max {max_pause_seconds}s, capping")
            pause_seconds = max_pause_seconds
        
        result = {
            'type': 'pause_and_check',
            'pause_seconds': pause_seconds,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        
        if on_event:
            on_event({
                'type': 'pause_start',
                'pause_seconds': pause_seconds,
                'timestamp': result['timestamp']
            })
        
        # Pause
        time.sleep(pause_seconds)
        
        # Run check
        try:
            check_result = check_func()
            result['check_result'] = check_result
            result['status'] = 'success'
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            logger.error(f"Self-check failed: {e}")
        
        if on_event:
            on_event({
                'type': 'pause_end',
                'status': result['status'],
                'timestamp': datetime.now().isoformat()
            })
        
        return result
    
    def write_heartbeat(self, on_event: Optional[Callable] = None) -> None:
        """
        Write heartbeat event.
        
        Args:
            on_event: Optional callback for events
        """
        if on_event:
            on_event({
                'type': 'heartbeat',
                'phase': self.current_phase,
                'timestamp': datetime.now().isoformat()
            })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all phase metrics."""
        return self.metrics.copy()
