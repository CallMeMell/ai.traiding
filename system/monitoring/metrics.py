"""
metrics.py - Metrics Collection
==============================
Collect and aggregate system metrics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict
import statistics


class MetricsCollector:
    """
    Collect and aggregate system metrics.
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def record(self, metric_name: str, value: float, 
              tags: Optional[Dict[str, str]] = None,
              timestamp: Optional[datetime] = None) -> None:
        """
        Record a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for filtering
            timestamp: Optional timestamp
        """
        metric = {
            'timestamp': timestamp or datetime.now(),
            'value': value,
            'tags': tags or {}
        }
        
        self.metrics[metric_name].append(metric)
    
    def get_stats(self, metric_name: str, 
                 since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get statistics for a metric.
        
        Args:
            metric_name: Name of the metric
            since: Optional start time for filtering
            
        Returns:
            Statistics dictionary
        """
        if metric_name not in self.metrics:
            return {
                'count': 0,
                'mean': 0,
                'min': 0,
                'max': 0,
                'p50': 0,
                'p95': 0,
                'p99': 0
            }
        
        # Filter by time if specified
        values = self.metrics[metric_name]
        if since:
            values = [m for m in values if m['timestamp'] >= since]
        
        if not values:
            return {
                'count': 0,
                'mean': 0,
                'min': 0,
                'max': 0,
                'p50': 0,
                'p95': 0,
                'p99': 0
            }
        
        numeric_values = [m['value'] for m in values]
        numeric_values.sort()
        
        count = len(numeric_values)
        
        return {
            'count': count,
            'mean': statistics.mean(numeric_values),
            'min': min(numeric_values),
            'max': max(numeric_values),
            'p50': numeric_values[int(count * 0.50)] if count > 0 else 0,
            'p95': numeric_values[int(count * 0.95)] if count > 0 else 0,
            'p99': numeric_values[int(count * 0.99)] if count > 0 else 0
        }
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all metrics.
        
        Returns:
            Dictionary mapping metric names to their statistics
        """
        return {
            metric_name: self.get_stats(metric_name)
            for metric_name in self.metrics.keys()
        }
    
    def clear(self, metric_name: Optional[str] = None) -> None:
        """
        Clear metrics.
        
        Args:
            metric_name: Optional metric name to clear, or all if None
        """
        if metric_name:
            if metric_name in self.metrics:
                self.metrics[metric_name].clear()
        else:
            self.metrics.clear()
