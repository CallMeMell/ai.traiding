#!/usr/bin/env python3
"""
validate_session.py - Session Data Validation
==============================================
Validates events.jsonl and summary.json against schemas.
Exit code 0 if valid, non-zero if validation fails.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from automation.validate import validate_event_strict, validate_summary_strict
from pydantic import ValidationError


def validate_events_file(events_path: str) -> tuple[int, int, List[str]]:
    """
    Validate all events in events.jsonl file.
    
    Returns:
        Tuple of (valid_count, total_count, errors)
    """
    if not os.path.exists(events_path):
        return 0, 0, [f"Events file not found: {events_path}"]
    
    valid_count = 0
    total_count = 0
    errors = []
    
    with open(events_path, 'r') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            
            total_count += 1
            try:
                event_dict = json.loads(line)
                validate_event_strict(event_dict)
                valid_count += 1
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: Invalid JSON - {e}")
            except ValidationError as e:
                errors.append(f"Line {line_num}: Validation failed - {e}")
            except Exception as e:
                errors.append(f"Line {line_num}: Unexpected error - {e}")
    
    return valid_count, total_count, errors


def validate_summary_file(summary_path: str) -> tuple[bool, List[str]]:
    """
    Validate summary.json file.
    
    Returns:
        Tuple of (is_valid, errors)
    """
    if not os.path.exists(summary_path):
        return False, [f"Summary file not found: {summary_path}"]
    
    errors = []
    
    try:
        with open(summary_path, 'r') as f:
            summary_dict = json.load(f)
        validate_summary_strict(summary_dict)
        return True, []
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
    except ValidationError as e:
        errors.append(f"Validation failed: {e}")
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
    
    return False, errors


def print_summary_stats(summary_path: str):
    """Print summary statistics for reporting."""
    if not os.path.exists(summary_path):
        print("Summary file not found")
        return
    
    try:
        with open(summary_path, 'r') as f:
            summary = json.load(f)
        
        print("\nSession Summary Statistics:")
        print(f"  Session ID: {summary.get('session_id', 'N/A')}")
        print(f"  Status: {summary.get('status', 'N/A')}")
        print(f"  Phases completed: {summary.get('phases_completed', 0)}/{summary.get('phases_total', 3)}")
        print(f"  Initial capital: ${summary.get('initial_capital', 0):.2f}")
        print(f"  Current equity: ${summary.get('current_equity', 0):.2f}")
        
        # Print totals if available
        if 'totals' in summary:
            totals = summary['totals']
            print(f"\nTotals:")
            print(f"  Trades: {totals.get('trades', 0)}")
            print(f"  Wins: {totals.get('wins', 0)}")
            print(f"  Losses: {totals.get('losses', 0)}")
        
        # Print last phase info
        if 'last_phase' in summary:
            print(f"\nLast phase: {summary['last_phase']}")
        
        # Print heartbeat age if available
        if 'last_updated' in summary:
            print(f"Last updated: {summary['last_updated']}")
            
    except Exception as e:
        print(f"Error reading summary: {e}")


def main():
    """Main entry point."""
    base_dir = Path(__file__).parent.parent
    events_path = base_dir / "data" / "session" / "events.jsonl"
    summary_path = base_dir / "data" / "session" / "summary.json"
    
    print("=" * 70)
    print("Session Data Validation")
    print("=" * 70)
    
    # Validate events
    print(f"\nValidating events: {events_path}")
    valid_events, total_events, event_errors = validate_events_file(str(events_path))
    
    if event_errors:
        print(f"✗ Events validation failed ({valid_events}/{total_events} valid)")
        print("\nErrors:")
        for error in event_errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(event_errors) > 10:
            print(f"  ... and {len(event_errors) - 10} more errors")
    else:
        print(f"✓ All events valid ({valid_events}/{total_events})")
    
    # Validate summary
    print(f"\nValidating summary: {summary_path}")
    summary_valid, summary_errors = validate_summary_file(str(summary_path))
    
    if summary_errors:
        print(f"✗ Summary validation failed")
        print("\nErrors:")
        for error in summary_errors:
            print(f"  - {error}")
    else:
        print(f"✓ Summary valid")
    
    # Print summary stats
    print_summary_stats(str(summary_path))
    
    print("\n" + "=" * 70)
    
    # Exit with appropriate code
    if event_errors or summary_errors:
        print("Validation FAILED")
        return 1
    else:
        print("Validation PASSED")
        return 0


if __name__ == '__main__':
    sys.exit(main())
