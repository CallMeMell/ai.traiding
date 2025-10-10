"""
validate.py - Validation Utilities
==================================
Validation utilities for events and summaries.
"""

import logging
from typing import Dict, Any, Optional
from pydantic import ValidationError

from automation.schemas import validate_event, validate_summary, Event, Summary

logger = logging.getLogger(__name__)


def validate_event_lenient(event_dict: Dict[str, Any]) -> Optional[Event]:
    """
    Validate an event with lenient error handling.
    
    Args:
        event_dict: Event dictionary to validate
        
    Returns:
        Validated Event instance or None if validation fails
    """
    try:
        return validate_event(event_dict)
    except ValidationError as e:
        logger.warning(f"Event validation failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error validating event: {e}")
        return None


def validate_summary_lenient(summary_dict: Dict[str, Any]) -> Optional[Summary]:
    """
    Validate a summary with lenient error handling.
    
    Args:
        summary_dict: Summary dictionary to validate
        
    Returns:
        Validated Summary instance or None if validation fails
    """
    try:
        return validate_summary(summary_dict)
    except ValidationError as e:
        logger.warning(f"Summary validation failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error validating summary: {e}")
        return None


def validate_event_strict(event_dict: Dict[str, Any]) -> Event:
    """
    Validate an event with strict error handling (raises exceptions).
    
    Args:
        event_dict: Event dictionary to validate
        
    Returns:
        Validated Event instance
        
    Raises:
        ValidationError: If validation fails
    """
    return validate_event(event_dict)


def validate_summary_strict(summary_dict: Dict[str, Any]) -> Summary:
    """
    Validate a summary with strict error handling (raises exceptions).
    
    Args:
        summary_dict: Summary dictionary to validate
        
    Returns:
        Validated Summary instance
        
    Raises:
        ValidationError: If validation fails
    """
    return validate_summary(summary_dict)
