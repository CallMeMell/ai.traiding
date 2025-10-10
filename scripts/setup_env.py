#!/usr/bin/env python3
"""
setup_env.py - Environment Setup Script
========================================
Cross-platform script to ensure:
- Required directories exist
- .env file has defaults from .env.example
- Python output is unbuffered for live logs
"""

import os
import sys
import shutil
from pathlib import Path


def ensure_directories():
    """Ensure required directories exist."""
    base_dir = Path(__file__).parent.parent
    dirs = [
        base_dir / "data" / "session",
        base_dir / "logs",
        base_dir / "config",
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory ready: {dir_path.relative_to(base_dir)}")


def ensure_env_defaults():
    """Ensure .env file exists with defaults from .env.example."""
    base_dir = Path(__file__).parent.parent
    env_file = base_dir / ".env"
    env_example = base_dir / ".env.example"
    
    # If .env doesn't exist but .env.example does, copy it
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print(f"✓ Created .env from .env.example")
    elif env_file.exists():
        print(f"✓ .env file already exists")
    else:
        # Create a minimal .env file
        with open(env_file, 'w') as f:
            f.write("# Trading Bot Environment Variables\n")
            f.write("# DRY_RUN mode is default - no real trades\n")
            f.write("DRY_RUN=true\n")
            f.write("LOG_LEVEL=INFO\n")
        print(f"✓ Created minimal .env file")


def set_unbuffered_output():
    """Set Python output to unbuffered mode for live logs."""
    # Force unbuffered output
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    # Reconfigure stdout/stderr to be unbuffered
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    
    print("✓ Python output set to unbuffered mode")


def main():
    """Main entry point."""
    print("=" * 60)
    print("Setting up environment...")
    print("=" * 60)
    
    ensure_directories()
    ensure_env_defaults()
    set_unbuffered_output()
    
    print("=" * 60)
    print("✓ Environment setup complete!")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
