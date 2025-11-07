#!/usr/bin/env python3
"""
env-check.py - Environment Validation Script
==============================================
Validates Python version, venv presence, and pip availability.

Exit codes:
  0 - All checks passed
  1 - Critical failure (Python version, pip missing)
  2 - Warning (venv not found, but can continue)

Usage:
  python scripts/env-check.py
  python3 scripts/env-check.py
"""

import sys
import os
import subprocess
from pathlib import Path


def print_header(message):
    """Print a formatted header."""
    print("=" * 70)
    print(f"🔍 {message}")
    print("=" * 70)


def print_success(message):
    """Print a success message."""
    print(f"✅ {message}")


def print_warning(message):
    """Print a warning message."""
    print(f"⚠️  {message}")


def print_error(message):
    """Print an error message."""
    print(f"❌ {message}")


def print_info(message):
    """Print an info message."""
    print(f"ℹ️  {message}")


def check_python_version():
    """
    Check if Python version meets minimum requirements.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    MIN_PYTHON_VERSION = (3, 8)
    current_version = sys.version_info
    
    if current_version >= MIN_PYTHON_VERSION:
        version_str = f"{current_version.major}.{current_version.minor}.{current_version.micro}"
        return True, f"Python version: {version_str} (minimum: {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]})"
    else:
        version_str = f"{current_version.major}.{current_version.minor}.{current_version.micro}"
        min_str = f"{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}"
        return False, f"Python version {version_str} is too old (minimum: {min_str})"


def check_venv_presence():
    """
    Check if virtual environment exists.
    
    Returns:
        tuple: (success: bool, message: str, is_warning: bool)
    """
    # Get project root (parent of scripts directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    venv_dir = project_root / "venv"
    
    if venv_dir.exists():
        # Check for common venv markers
        if sys.platform == "win32":
            python_exe = venv_dir / "Scripts" / "python.exe"
            activate_script = venv_dir / "Scripts" / "activate.ps1"
        else:
            python_exe = venv_dir / "bin" / "python"
            activate_script = venv_dir / "bin" / "activate"
        
        if python_exe.exists():
            return True, f"Virtual environment found: {venv_dir}", False
        else:
            return False, f"Virtual environment directory exists but Python executable not found: {python_exe}", True
    else:
        return False, f"Virtual environment not found: {venv_dir}", True


def check_pip_availability():
    """
    Check if pip is available.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Extract pip version from output
            pip_version = result.stdout.strip().split()[1] if result.stdout else "unknown"
            return True, f"pip version: {pip_version}"
        else:
            return False, "pip is not available (command failed)"
    except FileNotFoundError:
        return False, "pip is not installed"
    except subprocess.TimeoutExpired:
        return False, "pip check timed out"
    except Exception as e:
        return False, f"pip check failed: {str(e)}"


def check_requirements_file():
    """
    Check if requirements.txt exists.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    requirements_file = project_root / "requirements.txt"
    
    if requirements_file.exists():
        # Count lines in requirements file
        try:
            with open(requirements_file, 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            return True, f"requirements.txt found with {len(lines)} package(s)"
        except Exception as e:
            return True, f"requirements.txt found but could not read: {str(e)}"
    else:
        return False, f"requirements.txt not found: {requirements_file}"


def main():
    """Main entry point."""
    print_header("Environment Check")
    print()
    
    has_error = False
    has_warning = False
    
    # Check 1: Python Version
    print("Check 1: Python Version")
    success, message = check_python_version()
    if success:
        print_success(message)
    else:
        print_error(message)
        has_error = True
    print()
    
    # Check 2: Virtual Environment
    print("Check 2: Virtual Environment")
    success, message, is_warning = check_venv_presence()
    if success:
        print_success(message)
    else:
        if is_warning:
            print_warning(message)
            print_info("You can create a venv with: python -m venv venv")
            has_warning = True
        else:
            print_error(message)
            has_error = True
    print()
    
    # Check 3: pip Availability
    print("Check 3: pip Availability")
    success, message = check_pip_availability()
    if success:
        print_success(message)
    else:
        print_error(message)
        print_info("Install pip: https://pip.pypa.io/en/stable/installation/")
        has_error = True
    print()
    
    # Check 4: requirements.txt
    print("Check 4: requirements.txt")
    success, message = check_requirements_file()
    if success:
        print_success(message)
    else:
        print_warning(message)
        has_warning = True
    print()
    
    # Summary
    print("=" * 70)
    if has_error:
        print_error("Environment check FAILED")
        print()
        print("Critical issues found. Please fix the errors above.")
        print("=" * 70)
        return 1
    elif has_warning:
        print_warning("Environment check PASSED with warnings")
        print()
        print("Some optional components are missing but you can continue.")
        print("=" * 70)
        return 2
    else:
        print_success("Environment check PASSED")
        print()
        print("All checks passed! Your environment is ready.")
        print("=" * 70)
        return 0


if __name__ == "__main__":
    sys.exit(main())
