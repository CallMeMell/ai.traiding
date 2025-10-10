#!/usr/bin/env python3
"""
run_automation.py - Automation Runner Wrapper
==============================================
Cross-platform wrapper for automation/runner.py that:
- Ensures environment is set up
- Sets DRY_RUN=true by default
- Configures unbuffered output for live logs
- Accepts optional duration parameter for smoke tests
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.setup_env import ensure_directories, ensure_env_defaults, set_unbuffered_output


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Run automation workflow with optional duration limit'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=None,
        help='Duration in seconds to run (default: unlimited)'
    )
    parser.add_argument(
        '--enable-validation',
        action='store_true',
        help='Enable schema validation for events and summaries'
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Ensure environment is set up
    print("Preparing environment...")
    ensure_directories()
    ensure_env_defaults()
    set_unbuffered_output()
    
    # Set DRY_RUN=true by default (can be overridden by .env)
    if 'DRY_RUN' not in os.environ:
        os.environ['DRY_RUN'] = 'true'
    
    # Set other default environment variables
    if 'BROKER_NAME' not in os.environ:
        os.environ['BROKER_NAME'] = 'binance'
    if 'BINANCE_BASE_URL' not in os.environ:
        os.environ['BINANCE_BASE_URL'] = 'https://testnet.binance.vision'
    
    print(f"\nStarting automation runner...")
    print(f"  DRY_RUN: {os.environ.get('DRY_RUN', 'not set')}")
    print(f"  BROKER_NAME: {os.environ.get('BROKER_NAME', 'not set')}")
    print(f"  Duration: {args.duration if args.duration else 'unlimited'} seconds")
    print(f"  Validation: {'enabled' if args.enable_validation else 'disabled'}")
    print()
    
    # Import and run automation
    from automation.runner import AutomationRunner
    
    # Calculate phase timeouts based on duration
    if args.duration:
        # Distribute time across phases (40% data, 40% strategy, 20% api)
        data_timeout = int(args.duration * 0.4)
        strategy_timeout = int(args.duration * 0.4)
        api_timeout = int(args.duration * 0.2)
    else:
        # Default timeouts (2h, 2h, 1h)
        data_timeout = 7200
        strategy_timeout = 7200
        api_timeout = 3600
    
    runner = AutomationRunner(
        data_phase_timeout=data_timeout,
        strategy_phase_timeout=strategy_timeout,
        api_phase_timeout=api_timeout,
        heartbeat_interval=30,
        enable_validation=args.enable_validation
    )
    
    results = runner.run()
    
    # Print summary
    print("\n" + "=" * 70)
    print("AUTOMATION SUMMARY")
    print("=" * 70)
    print(f"Status: {results['status']}")
    print(f"Duration: {results.get('duration_seconds', 0):.2f} seconds")
    print(f"\nPhases completed:")
    for phase_name, phase_result in results.get('phases', {}).items():
        status = phase_result['status']
        duration = phase_result.get('duration_seconds', 0)
        print(f"  - {phase_name}: {status} ({duration:.2f}s)")
    print("=" * 70)
    
    return 0 if results['status'] == 'success' else 1


if __name__ == '__main__':
    sys.exit(main())
