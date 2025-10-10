"""
schemas.py - Event and Summary Schemas
=======================================
Pydantic schemas for structured event validation and summary data.
"""

from typing import Dict, Any, Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class MetricsData(BaseModel):
    """Metrics data within events."""
    equity: Optional[float] = None
    pnl: Optional[float] = None
    win_rate: Optional[float] = None
    trades: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None


class OrderData(BaseModel):
    """Order data within events."""
    symbol: Optional[str] = None
    side: Optional[str] = None
    qty: Optional[float] = None
    price: Optional[float] = None
    status: Optional[str] = None


class Event(BaseModel):
    """Event schema for events.jsonl entries."""
    timestamp: str = Field(description="ISO format timestamp")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    type: str = Field(description="Event type (e.g., session_start, phase_start, heartbeat)")
    phase: Optional[str] = Field(default=None, description="Current phase name")
    level: Optional[Literal["info", "warning", "error", "debug"]] = Field(default="info", description="Log level")
    message: Optional[str] = Field(default=None, description="Human-readable message")
    metrics: Optional[MetricsData] = Field(default=None, description="Performance metrics")
    order: Optional[OrderData] = Field(default=None, description="Order information")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional details")
    status: Optional[str] = Field(default=None, description="Status of the event")
    error: Optional[str] = Field(default=None, description="Error message if applicable")
    duration_seconds: Optional[float] = Field(default=None, description="Duration in seconds")
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v):
        """Validate timestamp is ISO format."""
        try:
            datetime.fromisoformat(v)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid timestamp format: {v}")
        return v


class SummaryTotals(BaseModel):
    """Totals section in summary."""
    trades: int = Field(default=0, description="Total number of trades")
    wins: int = Field(default=0, description="Number of winning trades")
    losses: int = Field(default=0, description="Number of losing trades")


class Summary(BaseModel):
    """Summary schema for summary.json."""
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    session_start: str = Field(description="Session start timestamp (ISO format)")
    session_end: Optional[str] = Field(default=None, description="Session end timestamp (ISO format)")
    started_at: Optional[str] = Field(default=None, description="Alternative start timestamp field")
    ended_at: Optional[str] = Field(default=None, description="Alternative end timestamp field")
    status: str = Field(default="running", description="Session status")
    phases_completed: int = Field(default=0, description="Number of completed phases")
    phases_total: int = Field(default=3, description="Total number of phases")
    initial_capital: float = Field(default=10000.0, description="Starting capital")
    current_equity: float = Field(default=10000.0, description="Current equity")
    totals: Optional[SummaryTotals] = Field(default=None, description="Trade totals")
    roi: Optional[float] = Field(default=None, description="Return on investment percentage")
    max_drawdown: Optional[float] = Field(default=None, description="Maximum drawdown percentage")
    runtime_secs: Optional[float] = Field(default=None, description="Runtime in seconds")
    last_updated: Optional[str] = Field(default=None, description="Last update timestamp")
    
    @field_validator('session_start', 'session_end', 'started_at', 'ended_at', 'last_updated')
    @classmethod
    def validate_timestamp(cls, v):
        """Validate timestamp is ISO format or None."""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid timestamp format: {v}")
        return v


# Helper function to validate event dictionaries
def validate_event(event_dict: Dict[str, Any]) -> Event:
    """
    Validate an event dictionary against the Event schema.
    
    Args:
        event_dict: Dictionary to validate
        
    Returns:
        Validated Event instance
        
    Raises:
        ValidationError: If validation fails
    """
    return Event(**event_dict)


# Helper function to validate summary dictionaries
def validate_summary(summary_dict: Dict[str, Any]) -> Summary:
    """
    Validate a summary dictionary against the Summary schema.
    
    Args:
        summary_dict: Dictionary to validate
        
    Returns:
        Validated Summary instance
        
    Raises:
        ValidationError: If validation fails
    """
    return Summary(**summary_dict)
