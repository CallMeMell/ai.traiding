"""
slo_monitor.py - SLO Monitor for Automation
===========================================
Monitor SLOs and generate needs-review events when thresholds are breached.
"""

import logging
import sys
import os
from typing import Optional, Dict, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.monitoring.slo import SLOMonitor as BaseSLOMonitor, SLOStatus
from core.session_store import SessionStore

logger = logging.getLogger(__name__)


class SLOMonitor:
    """
    SLO Monitor for automation workflows.
    
    Monitors error rates and render times, generating needs-review events
    when SLOs are breached.
    
    Example:
        >>> monitor = SLOMonitor()
        >>> monitor.check_error_rate()
        >>> monitor.check_render_time()
        >>> monitor.error_rate_threshold = 0.05
    """
    
    def __init__(self, 
                 error_rate_threshold: float = 0.01,
                 render_time_threshold_ms: float = 500.0,
                 session_store: Optional[SessionStore] = None):
        """
        Initialize SLO monitor.
        
        Args:
            error_rate_threshold: Error rate threshold (default 0.01 = 1%)
            render_time_threshold_ms: Render time threshold in milliseconds (default 500ms)
            session_store: Optional session store for writing events
        """
        self.base_monitor = BaseSLOMonitor()
        self._error_rate_threshold = error_rate_threshold
        self._render_time_threshold_ms = render_time_threshold_ms
        self.session_store = session_store or SessionStore()
        
        logger.info(f"SLOMonitor initialized with error_rate_threshold={error_rate_threshold}, "
                   f"render_time_threshold={render_time_threshold_ms}ms")
    
    @property
    def error_rate_threshold(self) -> float:
        """Get error rate threshold."""
        return self._error_rate_threshold
    
    @error_rate_threshold.setter
    def error_rate_threshold(self, value: float) -> None:
        """Set error rate threshold."""
        if not 0.0 <= value <= 1.0:
            raise ValueError("error_rate_threshold must be between 0.0 and 1.0")
        self._error_rate_threshold = value
        logger.info(f"Error rate threshold set to {value}")
    
    @property
    def render_time_threshold_ms(self) -> float:
        """Get render time threshold in milliseconds."""
        return self._render_time_threshold_ms
    
    @render_time_threshold_ms.setter
    def render_time_threshold_ms(self, value: float) -> None:
        """Set render time threshold in milliseconds."""
        if value <= 0:
            raise ValueError("render_time_threshold_ms must be positive")
        self._render_time_threshold_ms = value
        logger.info(f"Render time threshold set to {value}ms")
    
    def add_error_measurement(self, success: bool, timestamp: Optional[datetime] = None) -> None:
        """
        Add an error rate measurement.
        
        Args:
            success: Whether the operation was successful
            timestamp: Optional timestamp for the measurement
        """
        self.base_monitor.add_measurement('error_rate', success=success, timestamp=timestamp)
    
    def add_render_time_measurement(self, render_time_ms: float, timestamp: Optional[datetime] = None) -> None:
        """
        Add a render time measurement.
        
        Args:
            render_time_ms: Render time in milliseconds
            timestamp: Optional timestamp for the measurement
        """
        # Consider it successful if under threshold
        success = render_time_ms <= self._render_time_threshold_ms
        self.base_monitor.add_measurement('api_response_time', success=success, 
                                         value=render_time_ms, timestamp=timestamp)
    
    def check_error_rate(self) -> Dict[str, Any]:
        """
        Check error rate SLO and generate needs-review event if breached.
        
        Returns:
            Dictionary with error rate status
        """
        status = self.base_monitor.get_slo_status('error_rate')
        
        # Generate needs-review event if breached or at risk
        if status['status'] in [SLOStatus.BREACHED.value, SLOStatus.AT_RISK.value]:
            self._generate_needs_review_event(
                slo_name='error_rate',
                status=status,
                threshold=self._error_rate_threshold
            )
        
        logger.info(f"Error rate check: {status['status']} - "
                   f"{status['current_percentage']:.2f}% (target: {status['target_percentage']}%)")
        
        return status
    
    def check_render_time(self) -> Dict[str, Any]:
        """
        Check render time SLO and generate needs-review event if breached.
        
        Returns:
            Dictionary with render time status
        """
        status = self.base_monitor.get_slo_status('api_response_time')
        
        # Generate needs-review event if breached or at risk
        if status['status'] in [SLOStatus.BREACHED.value, SLOStatus.AT_RISK.value]:
            self._generate_needs_review_event(
                slo_name='render_time',
                status=status,
                threshold=self._render_time_threshold_ms
            )
        
        logger.info(f"Render time check: {status['status']} - "
                   f"{status['current_percentage']:.2f}% (target: {status['target_percentage']}%)")
        
        return status
    
    def _generate_needs_review_event(self, slo_name: str, status: Dict[str, Any], 
                                    threshold: float) -> None:
        """
        Generate a needs-review event for SLO breach.
        
        Args:
            slo_name: Name of the SLO
            status: SLO status dictionary
            threshold: Configured threshold value
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': 'needs-review',
            'level': 'warning' if status['status'] == SLOStatus.AT_RISK.value else 'error',
            'message': f"SLO {slo_name} is {status['status']}: "
                      f"{status['current_percentage']:.2f}% (target: {status['target_percentage']}%)",
            'details': {
                'slo_name': slo_name,
                'status': status['status'],
                'current_percentage': status['current_percentage'],
                'target_percentage': status['target_percentage'],
                'error_budget_remaining': status['error_budget_remaining'],
                'threshold': threshold,
                'total_measurements': status['total_measurements'],
                'failed_measurements': status['failed_measurements']
            }
        }
        
        try:
            self.session_store.append_event(event, validate=True)
            logger.warning(f"Generated needs-review event for {slo_name}: {status['status']}")
        except Exception as e:
            logger.error(f"Failed to write needs-review event: {e}")
    
    def get_all_status(self) -> Dict[str, Any]:
        """
        Get status of all monitored SLOs.
        
        Returns:
            Dictionary with error_rate and render_time status
        """
        return {
            'error_rate': self.check_error_rate(),
            'render_time': self.check_render_time()
        }
