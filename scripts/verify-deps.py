#!/usr/bin/env python3
"""
verify-deps.py - Dependency Verification Script
================================================
Compares requirements.txt with installed packages and optionally installs missing dependencies.

Exit codes:
  0 - All dependencies satisfied
  1 - Missing dependencies (without --install)
  2 - Installation attempted but some packages failed

Usage:
  python scripts/verify-deps.py              # Check only
  python scripts/verify-deps.py --install    # Check and install missing
  python scripts/verify-deps.py -i           # Short form
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple, Dict


def print_header(message):
    """Print a formatted header."""
    print("=" * 70)
    print(f"📦 {message}")
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


def get_installed_packages() -> Dict[str, str]:
    """
    Get list of installed packages using pip list.
    
    Returns:
        dict: Package name -> version mapping
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=freeze"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print_error(f"Failed to get installed packages: {result.stderr}")
            return {}
        
        packages = {}
        for line in result.stdout.strip().split('\n'):
            if '==' in line:
                name, version = line.split('==', 1)
                packages[name.lower()] = version
        
        return packages
    except subprocess.TimeoutExpired:
        print_error("Timeout while getting installed packages")
        return {}
    except Exception as e:
        print_error(f"Error getting installed packages: {str(e)}")
        return {}


def parse_requirements_file(requirements_path: Path) -> List[Tuple[str, str, str]]:
    """
    Parse requirements.txt file.
    
    Args:
        requirements_path: Path to requirements.txt
    
    Returns:
        list: List of (package_name, operator, version) tuples
              operator can be '>=', '==', '<=', '>', '<', or '' (no version specified)
    """
    requirements = []
    
    try:
        with open(requirements_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse package specification
                # Handle various formats: package, package>=1.0, package==1.0, etc.
                if '>=' in line:
                    name, version = line.split('>=', 1)
                    requirements.append((name.strip().lower(), '>=', version.strip()))
                elif '==' in line:
                    name, version = line.split('==', 1)
                    requirements.append((name.strip().lower(), '==', version.strip()))
                elif '<=' in line:
                    name, version = line.split('<=', 1)
                    requirements.append((name.strip().lower(), '<=', version.strip()))
                elif '>' in line:
                    name, version = line.split('>', 1)
                    requirements.append((name.strip().lower(), '>', version.strip()))
                elif '<' in line:
                    name, version = line.split('<', 1)
                    requirements.append((name.strip().lower(), '<', version.strip()))
                else:
                    # No version specified
                    requirements.append((line.strip().lower(), '', ''))
        
        return requirements
    except Exception as e:
        print_error(f"Error parsing requirements.txt: {str(e)}")
        return []


def check_version_compatibility(installed_version: str, operator: str, required_version: str) -> bool:
    """
    Check if installed version satisfies requirement.
    
    Args:
        installed_version: Installed version string
        operator: Comparison operator (>=, ==, <=, >, <)
        required_version: Required version string
    
    Returns:
        bool: True if version is compatible
    """
    if not operator or not required_version:
        # No version requirement, any version is acceptable
        return True
    
    try:
        # Simple version comparison (works for most cases)
        # For production, consider using packaging.version
        from packaging.version import parse as parse_version
        
        installed = parse_version(installed_version)
        required = parse_version(required_version)
        
        if operator == '>=':
            return installed >= required
        elif operator == '==':
            return installed == required
        elif operator == '<=':
            return installed <= required
        elif operator == '>':
            return installed > required
        elif operator == '<':
            return installed < required
        else:
            return True
    except ImportError:
        # If packaging is not available, do simple string comparison
        if operator == '==':
            return installed_version == required_version
        else:
            # For other operators, we can't reliably compare without packaging
            # Assume compatible
            print_warning(f"Cannot verify version compatibility without 'packaging' module")
            return True
    except Exception as e:
        print_warning(f"Version comparison failed: {str(e)}")
        return True  # Assume compatible if we can't verify


def verify_dependencies(requirements_path: Path, installed: Dict[str, str]) -> Tuple[List[str], List[str], List[str]]:
    """
    Verify if all required dependencies are installed.
    
    Args:
        requirements_path: Path to requirements.txt
        installed: Dictionary of installed packages
    
    Returns:
        tuple: (missing_packages, version_mismatches, satisfied_packages)
    """
    requirements = parse_requirements_file(requirements_path)
    
    missing = []
    mismatches = []
    satisfied = []
    
    for package_name, operator, required_version in requirements:
        if package_name not in installed:
            missing.append(f"{package_name}{operator}{required_version}" if operator else package_name)
        else:
            installed_version = installed[package_name]
            if check_version_compatibility(installed_version, operator, required_version):
                satisfied.append(f"{package_name}=={installed_version}")
            else:
                mismatches.append(
                    f"{package_name}: installed={installed_version}, required={operator}{required_version}"
                )
    
    return missing, mismatches, satisfied


def install_packages(packages: List[str]) -> bool:
    """
    Install packages using pip.
    
    Args:
        packages: List of package specifications to install
    
    Returns:
        bool: True if all packages installed successfully
    """
    if not packages:
        return True
    
    print_info(f"Installing {len(packages)} package(s)...")
    
    try:
        # Install packages one by one to track failures
        failed = []
        succeeded = []
        
        for package in packages:
            print(f"  Installing {package}...", end=" ")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package, "--quiet"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes per package
            )
            
            if result.returncode == 0:
                print("✅")
                succeeded.append(package)
            else:
                print("❌")
                failed.append(package)
                print_error(f"    Error: {result.stderr.strip()}")
        
        print()
        
        if succeeded:
            print_success(f"Successfully installed {len(succeeded)} package(s)")
        
        if failed:
            print_error(f"Failed to install {len(failed)} package(s):")
            for pkg in failed:
                print(f"    - {pkg}")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        print_error("Installation timed out")
        return False
    except Exception as e:
        print_error(f"Installation failed: {str(e)}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify dependencies against requirements.txt"
    )
    parser.add_argument(
        '-i', '--install',
        action='store_true',
        help='Automatically install missing dependencies'
    )
    args = parser.parse_args()
    
    print_header("Dependency Verification")
    print()
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    requirements_path = project_root / "requirements.txt"
    
    # Check if requirements.txt exists
    if not requirements_path.exists():
        print_error(f"requirements.txt not found: {requirements_path}")
        return 1
    
    # Get installed packages
    print_info("Scanning installed packages...")
    installed = get_installed_packages()
    if not installed:
        print_warning("Could not get installed packages list")
    else:
        print_success(f"Found {len(installed)} installed package(s)")
    print()
    
    # Verify dependencies
    print_info("Checking requirements.txt...")
    missing, mismatches, satisfied = verify_dependencies(requirements_path, installed)
    print()
    
    # Report results
    if satisfied:
        print_success(f"{len(satisfied)} package(s) satisfied:")
        for pkg in satisfied[:5]:  # Show first 5
            print(f"    ✓ {pkg}")
        if len(satisfied) > 5:
            print(f"    ... and {len(satisfied) - 5} more")
        print()
    
    if mismatches:
        print_warning(f"{len(mismatches)} version mismatch(es):")
        for mismatch in mismatches:
            print(f"    ⚠️  {mismatch}")
        print()
    
    if missing:
        print_error(f"{len(missing)} missing package(s):")
        for pkg in missing:
            print(f"    ❌ {pkg}")
        print()
        
        if args.install:
            print_info("Installing missing packages...")
            print()
            success = install_packages(missing)
            print()
            
            if success:
                print_success("All missing packages installed successfully")
                print("=" * 70)
                return 0
            else:
                print_error("Some packages failed to install")
                print("=" * 70)
                return 2
        else:
            print_info("Run with --install to automatically install missing packages")
            print("=" * 70)
            return 1
    else:
        print_success("All dependencies satisfied!")
        print("=" * 70)
        return 0


if __name__ == "__main__":
    sys.exit(main())
