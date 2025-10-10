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

from system.orchestrator import SystemOrchestrator
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
        # Create orchestrator
        orchestrator = SystemOrchestrator(
            dry_run=True,
            enable_health_checks=True,
            enable_recovery=True
        )
        
        # Run system
        results = orchestrator.run()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Nightly Test Summary")
        print("=" * 60)
        print(f"Status: {results['status']}")
        print(f"Duration: {results['duration_seconds']:.2f}s")
        print(f"Phases: {len(results['phases'])}")
        print(f"Errors: {len(results['errors'])}")
        
        if results['errors']:
            print("\n❌ Errors:")
            for error in results['errors']:
                print(f"  - {error}")
        
        print("\n✅ Phases:")
        for phase in results['phases']:
            status_icon = "✅" if phase['status'] == 'success' else "❌"
            print(f"  {status_icon} {phase['phase']}: {phase['status']} ({phase['duration_seconds']:.2f}s)")
        
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
