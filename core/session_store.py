"""
session_store.py - Session Event and Summary Storage
===================================================
Lightweight data model for session events and summaries.
- Events stored in JSONL (one event per line)
- Summary stored in JSON (rolling update)
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class SessionStore:
    """
    Store for session events and summary.
    Writes events to JSONL and summary to JSON.
    """
    
    def __init__(self, events_path: str = "data/session/events.jsonl",
                 summary_path: str = "data/session/summary.json"):
        """
        Initialize session store.
        
        Args:
            events_path: Path to JSONL file for events
            summary_path: Path to JSON file for summary
        """
        self.events_path = events_path
        self.summary_path = summary_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.events_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.summary_path), exist_ok=True)
    
    def append_event(self, event: Dict[str, Any], validate: bool = False) -> None:
        """
        Append an event to the JSONL file.
        
        Args:
            event: Event dictionary with timestamp, type, and data
            validate: Whether to validate against schema (optional, defaults to False for backward compatibility)
        """
        # Add timestamp if not present
        if 'timestamp' not in event:
            event['timestamp'] = datetime.now().isoformat()
        
        # Optional validation
        if validate:
            try:
                from automation.validate import validate_event_lenient
                validated = validate_event_lenient(event)
                if validated is None:
                    logger.warning(f"Event validation failed, writing anyway: {event.get('type')}")
            except Exception as e:
                logger.warning(f"Could not validate event: {e}")
        
        # Append to JSONL file and flush immediately for real-time updates
        with open(self.events_path, 'a') as f:
            f.write(json.dumps(event) + '\n')
            f.flush()  # Ensure immediate write to disk
    
    def read_events(self, tail: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Read events from JSONL file.
        
        Args:
            tail: If specified, only return the last N events
        
        Returns:
            List of event dictionaries
        """
        if not os.path.exists(self.events_path):
            return []
        
        events = []
        with open(self.events_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        
        # Return tail if specified
        if tail is not None and tail > 0:
            return events[-tail:]
        return events
    
    def write_summary(self, summary: Dict[str, Any], validate: bool = False) -> None:
        """
        Write summary to JSON file (overwrites).
        
        Args:
            summary: Summary dictionary
            validate: Whether to validate against schema (optional, defaults to False for backward compatibility)
        """
        # Add last_updated timestamp
        summary['last_updated'] = datetime.now().isoformat()
        
        # Optional validation
        if validate:
            try:
                from automation.validate import validate_summary_lenient
                validated = validate_summary_lenient(summary)
                if validated is None:
                    logger.warning(f"Summary validation failed, writing anyway")
            except Exception as e:
                logger.warning(f"Could not validate summary: {e}")
        
        # Write and flush immediately for real-time updates
        with open(self.summary_path, 'w') as f:
            f.write(json.dumps(summary, indent=2))
            f.flush()  # Ensure immediate write to disk
    
    def read_summary(self) -> Optional[Dict[str, Any]]:
        """
        Read summary from JSON file.
        
        Returns:
            Summary dictionary or None if not found
        """
        if not os.path.exists(self.summary_path):
            return None
        
        try:
            with open(self.summary_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def calculate_roi(self, initial_capital: float, current_equity: float) -> float:
        """
        Calculate return on investment.
        
        Args:
            initial_capital: Starting capital
            current_equity: Current equity
            
        Returns:
            ROI as percentage
        """
        if initial_capital <= 0:
            return 0.0
        return ((current_equity - initial_capital) / initial_capital) * 100.0
    
    def clear_events(self) -> None:
        """Clear all events (for testing or new session)."""
        if os.path.exists(self.events_path):
            os.remove(self.events_path)
    
    def clear_summary(self) -> None:
        """Clear summary (for testing or new session)."""
        if os.path.exists(self.summary_path):
            os.remove(self.summary_path)
