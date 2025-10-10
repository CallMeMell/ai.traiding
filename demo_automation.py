"""
demo_automation.py - Demo of automation runner and session storage
================================================================
Demonstrates the complete workflow from runner to session data.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.session_store import SessionStore
from automation.runner import AutomationRunner


def main():
    """Demo the automation workflow."""
    print("=" * 70)
    print("AUTOMATION DEMO")
    print("=" * 70)
    print()
    print("This demo will:")
    print("1. Run the automation workflow with all 3 phases")
    print("2. Write session events and summary")
    print("3. Display the results")
    print()
    print("=" * 70)
    input("Press Enter to start...")
    print()
    
    # Clean up previous session data
    store = SessionStore()
    store.clear_events()
    store.clear_summary()
    
    # Create runner with shorter timeouts for demo
    print("Creating automation runner...")
    runner = AutomationRunner(
        data_phase_timeout=30,  # 30 seconds for demo
        strategy_phase_timeout=30,
        api_phase_timeout=30
    )
    
    print("Running automation workflow...")
    print()
    results = runner.run()
    
    print()
    print("=" * 70)
    print("DEMO RESULTS")
    print("=" * 70)
    
    # Display results
    print(f"\n✓ Workflow Status: {results['status']}")
    print(f"✓ Duration: {results.get('duration_seconds', 0):.2f} seconds")
    
    # Display phase results
    print(f"\n📊 Phase Results:")
    for phase_name, phase_result in results.get('phases', {}).items():
        status_icon = "✓" if phase_result['status'] == 'success' else "✗"
        print(f"  {status_icon} {phase_name}: {phase_result['status']} ({phase_result.get('duration_seconds', 0):.2f}s)")
    
    # Read and display session data
    print(f"\n💾 Session Data:")
    summary = store.read_summary()
    events = store.read_events()
    
    if summary:
        print(f"  ✓ Summary: {summary.get('phases_completed', 0)}/{summary.get('phases_total', 0)} phases")
        print(f"  ✓ ROI: {summary.get('roi', 0):.2f}%")
        print(f"  ✓ Capital: ${summary.get('initial_capital', 0):,.2f} → ${summary.get('current_equity', 0):,.2f}")
    
    print(f"  ✓ Events: {len(events)} events logged")
    
    # Display file locations
    print(f"\n📁 Session Files:")
    print(f"  ✓ Events: {store.events_path}")
    print(f"  ✓ Summary: {store.summary_path}")
    
    print()
    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print()
    print("To view the session data in the dashboard:")
    print("1. Install Streamlit: pip install streamlit plotly")
    print("2. Run: streamlit run tools/view_session_app.py")
    print("3. Open browser at http://localhost:8501")
    print()
    print("Or explore the session files directly:")
    print(f"  - cat {store.events_path}")
    print(f"  - cat {store.summary_path}")
    print()
    print("=" * 70)


if __name__ == '__main__':
    main()
