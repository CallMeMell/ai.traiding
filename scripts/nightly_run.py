"""
nightly_run.py - Nightly System Test Runner
==========================================
Automated nightly dry-run test for the complete system.
"""

import sys
import os
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.runner import AutomationRunner
from system.log_system.logger import configure_logging, LogLevel

def main():
    """Run nightly system test."""
    print("=" * 60)
    print("🌙 Nightly System Test")
    print("=" * 60)
    print(f"Start Time: {datetime.now().isoformat()}")
    print()
    
    # Configure logging
    configure_logging(
        log_dir='logs',
        level=LogLevel.INFO,
        enable_console=True,
        enable_json=True
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting nightly system test")
    
    # Force DRY_RUN mode
    os.environ['DRY_RUN'] = 'true'
    
    try:
        # Create automation runner
        runner = AutomationRunner(
            data_phase_timeout=7200,      # 2 hours
            strategy_phase_timeout=7200,  # 2 hours
            api_phase_timeout=3600,       # 1 hour
            heartbeat_interval=30,
            enable_validation=True
        )
        
        # Run automation workflow
        results = runner.run()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Nightly Test Summary")
        print("=" * 60)
        print(f"Status: {results['status']}")
        print(f"Duration: {results.get('duration_seconds', 0):.2f}s")
        print(f"Phases: {len(results.get('phases', {}))}")
        
        print("\n✅ Phases:")
        for phase_name, phase_result in results.get('phases', {}).items():
            status_icon = "✅" if phase_result['status'] == 'success' else "❌"
            print(f"  {status_icon} {phase_name}: {phase_result['status']} ({phase_result.get('duration_seconds', 0):.2f}s)")
        
        # Check if summary.json was generated
        summary_path = os.path.join('data', 'session', 'summary.json')
        if os.path.exists(summary_path):
            print(f"\n✅ Summary saved to {summary_path}")
        else:
            print(f"\n⚠️  Warning: Summary file not found at {summary_path}")
        
        print("=" * 60)
        
        # Exit with appropriate code
        exit_code = 0 if results['status'] == 'success' else 1
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Nightly test failed: {e}", exc_info=True)
        print(f"\n❌ Fatal Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
