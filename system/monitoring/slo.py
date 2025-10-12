"""
slo.py - Service Level Objectives Monitoring
==========================================
Track and monitor SLOs and error budgets.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


class SLOStatus(Enum):
    """SLO compliance status."""
    COMPLIANT = "compliant"
    AT_RISK = "at_risk"
    BREACHED = "breached"


@dataclass
class SLODefinition:
    """SLO definition."""
    name: str
    description: str
    target_percentage: float  # e.g., 99.5 for 99.5%
    window_days: int  # Time window for measurement
    error_budget_percentage: float  # e.g., 0.5 for 0.5% error budget


class SLOMonitor:
    """
    Monitor Service Level Objectives and error budgets.
    
    Tracks system performance against defined SLOs.
    """
    
    # Standard SLO definitions
    STANDARD_SLOS = [
        SLODefinition(
            name="system_uptime",
            description="System availability",
            target_percentage=99.5,
            window_days=30,
            error_budget_percentage=0.5
        ),
        SLODefinition(
            name="api_response_time",
            description="API response time P95 < 500ms",
            target_percentage=95.0,
            window_days=7,
            error_budget_percentage=5.0
        ),
        SLODefinition(
            name="trade_execution_time",
            description="Trade execution P99 < 1s",
            target_percentage=99.0,
            window_days=7,
            error_budget_percentage=1.0
        ),
        SLODefinition(
            name="error_rate",
            description="Error rate < 1%",
            target_percentage=99.0,
            window_days=7,
            error_budget_percentage=1.0
        ),
    ]
    
    def __init__(self):
        """Initialize SLO monitor."""
        self.slos = {slo.name: slo for slo in self.STANDARD_SLOS}
        self.measurements: Dict[str, List[Dict[str, Any]]] = {
            slo.name: [] for slo in self.STANDARD_SLOS
        }
    
    def add_measurement(self, slo_name: str, success: bool, 
                       value: Optional[float] = None,
                       timestamp: Optional[datetime] = None) -> None:
        """
        Add a measurement for an SLO.
        
        Args:
            slo_name: SLO identifier
            success: Whether the measurement was successful
            value: Optional measurement value (e.g., response time)
            timestamp: Measurement timestamp
        """
        if slo_name not in self.slos:
            raise ValueError(f"Unknown SLO: {slo_name}")
        
        measurement = {
            'timestamp': timestamp or datetime.now(),
            'success': success,
            'value': value
        }
        
        self.measurements[slo_name].append(measurement)
        
        # Keep only measurements within the window
        slo = self.slos[slo_name]
        cutoff = datetime.now() - timedelta(days=slo.window_days)
        self.measurements[slo_name] = [
            m for m in self.measurements[slo_name]
            if m['timestamp'] >= cutoff
        ]
    
    def get_slo_status(self, slo_name: str) -> Dict[str, Any]:
        """
        Get current status of an SLO.
        
        Args:
            slo_name: SLO identifier
            
        Returns:
            Dictionary with SLO status information
        """
        if slo_name not in self.slos:
            raise ValueError(f"Unknown SLO: {slo_name}")
        
        slo = self.slos[slo_name]
        measurements = self.measurements[slo_name]
        
        if not measurements:
            return {
                'slo': slo.name,
                'status': SLOStatus.COMPLIANT.value,
                'current_percentage': 100.0,
                'target_percentage': slo.target_percentage,
                'error_budget_remaining': 100.0,
                'total_measurements': 0,
                'message': 'No measurements yet'
            }
        
        # Calculate success rate
        total = len(measurements)
        successful = sum(1 for m in measurements if m['success'])
        success_rate = (successful / total) * 100.0
        
        # Calculate error budget consumption
        allowed_failures = total * (slo.error_budget_percentage / 100.0)
        actual_failures = total - successful
        error_budget_remaining = max(0, (allowed_failures - actual_failures) / allowed_failures * 100.0)
        
        # Determine status
        if success_rate >= slo.target_percentage:
            status = SLOStatus.COMPLIANT
        elif error_budget_remaining > 20:
            status = SLOStatus.AT_RISK
        else:
            status = SLOStatus.BREACHED
        
        return {
            'slo': slo.name,
            'description': slo.description,
            'status': status.value,
            'current_percentage': success_rate,
            'target_percentage': slo.target_percentage,
            'error_budget_remaining': error_budget_remaining,
            'total_measurements': total,
            'successful_measurements': successful,
            'failed_measurements': actual_failures,
            'window_days': slo.window_days
        }
    
    def get_all_slo_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all SLOs.
        
        Returns:
            List of SLO status dictionaries
        """
        return [self.get_slo_status(slo_name) for slo_name in self.slos.keys()]
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all SLOs.
        
        Returns:
            Summary dictionary
        """
        all_status = self.get_all_slo_status()
        
        compliant = sum(1 for s in all_status if s['status'] == SLOStatus.COMPLIANT.value)
        at_risk = sum(1 for s in all_status if s['status'] == SLOStatus.AT_RISK.value)
        breached = sum(1 for s in all_status if s['status'] == SLOStatus.BREACHED.value)
        
        return {
            'total_slos': len(all_status),
            'compliant': compliant,
            'at_risk': at_risk,
            'breached': breached,
            'overall_health': 'healthy' if breached == 0 else 'degraded' if at_risk > 0 else 'critical',
            'slos': all_status
        }
