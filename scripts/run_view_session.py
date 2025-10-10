#!/usr/bin/env python3
"""
run_view_session.py - View Session Wrapper
==========================================
Cross-platform wrapper for Streamlit View Session app that:
- Ensures environment is set up
- Starts Streamlit with proper configuration
- Configures unbuffered output for live logs
"""

import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.setup_env import ensure_directories, ensure_env_defaults, set_unbuffered_output


def main():
    """Main entry point."""
    # Ensure environment is set up
    print("Preparing environment...")
    ensure_directories()
    ensure_env_defaults()
    set_unbuffered_output()
    
    # Get paths
    base_dir = Path(__file__).parent.parent
    app_path = base_dir / "tools" / "view_session_app.py"
    
    if not app_path.exists():
        print(f"Error: Streamlit app not found at {app_path}")
        return 1
    
    print(f"\nStarting View Session (Streamlit)...")
    print(f"  App: {app_path.relative_to(base_dir)}")
    print(f"  Port: 8501")
    print(f"  Address: 0.0.0.0")
    print()
    
    # Check if streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("Warning: Streamlit is not installed. Installing now...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit", "plotly"], check=True)
    
    # Run streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return 0
    except KeyboardInterrupt:
        print("\n\nStreamlit stopped by user.")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\nError running Streamlit: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
