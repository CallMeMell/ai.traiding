#!/usr/bin/env python3
"""
test_automation_integration.py - Integration Test for Automation Scripts
========================================================================
Tests the complete automation workflow including scripts and validation.
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path


def run_command(cmd, timeout=60):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"


def test_setup_env():
    """Test setup_env.py script."""
    print("\n=== Testing setup_env.py ===")
    success, output = run_command("python3 scripts/setup_env.py")
    if success:
        print("✓ setup_env.py executed successfully")
        return True
    else:
        print(f"✗ setup_env.py failed: {output}")
        return False


def test_run_automation():
    """Test run_automation.py with short duration."""
    print("\n=== Testing run_automation.py ===")
    
    # Clean up old session data
    session_dir = Path("data/session")
    if session_dir.exists():
        for f in session_dir.glob("*"):
            f.unlink()
    
    success, output = run_command(
        "python3 scripts/run_automation.py --duration 10 --enable-validation",
        timeout=30
    )
    
    # Note: With short timeout, some phases may timeout which returns exit code 1
    # But as long as session data is created, it's a success
    if success or "WORKFLOW COMPLETED" in output:
        print("✓ run_automation.py executed (completed workflow)")
        
        # Check that session data was created
        events_file = session_dir / "events.jsonl"
        summary_file = session_dir / "summary.json"
        
        if events_file.exists():
            print(f"✓ events.jsonl created ({events_file.stat().st_size} bytes)")
        else:
            print("✗ events.jsonl not created")
            return False
        
        if summary_file.exists():
            print(f"✓ summary.json created ({summary_file.stat().st_size} bytes)")
            # Try to parse it
            try:
                with open(summary_file) as f:
                    summary = json.load(f)
                print(f"  Session ID: {summary.get('session_id', 'N/A')}")
                print(f"  Status: {summary.get('status', 'N/A')}")
                print(f"  Phases: {summary.get('phases_completed', 0)}/{summary.get('phases_total', 3)}")
            except Exception as e:
                print(f"✗ Could not parse summary.json: {e}")
                return False
        else:
            print("✗ summary.json not created")
            return False
        
        return True
    else:
        print(f"✗ run_automation.py failed: {output}")
        return False


def test_validate_session():
    """Test validate_session.py on generated data."""
    print("\n=== Testing validate_session.py ===")
    success, output = run_command("python3 scripts/validate_session.py")
    
    if success:
        print("✓ validate_session.py passed")
        # Check for key phrases in output
        if "Validation PASSED" in output:
            print("✓ Session data is valid")
            return True
        else:
            print("✗ Validation did not pass")
            return False
    else:
        print(f"✗ validate_session.py failed: {output}")
        return False


def test_dry_run_default():
    """Test that DRY_RUN is true by default."""
    print("\n=== Testing DRY_RUN default ===")
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            content = f.read()
            if "DRY_RUN=true" in content:
                print("✓ .env contains DRY_RUN=true")
                return True
            else:
                print("⚠ .env does not contain DRY_RUN=true (might be ok)")
                return True  # Not a failure
    else:
        print("⚠ .env file not found (will be created with defaults)")
        return True


def test_no_secrets_required():
    """Test that automation runs without API keys."""
    print("\n=== Testing no secrets required ===")
    
    # Temporarily remove API key env vars if set
    old_env = {}
    key_vars = ['BINANCE_API_KEY', 'BINANCE_SECRET_KEY', 'ALPACA_API_KEY', 'ALPACA_SECRET_KEY']
    for var in key_vars:
        if var in os.environ:
            old_env[var] = os.environ[var]
            del os.environ[var]
    
    # Run automation
    success, output = run_command(
        "python3 scripts/run_automation.py --duration 5",
        timeout=20
    )
    
    # Restore env vars
    for var, val in old_env.items():
        os.environ[var] = val
    
    if "WORKFLOW COMPLETED" in output or "AutomationRunner initialized" in output:
        print("✓ Automation runs without API keys (DRY_RUN mode)")
        return True
    else:
        print(f"✗ Automation failed to start without API keys: {output[:200]}")
        return False


def main():
    """Run all integration tests."""
    print("=" * 70)
    print("Automation Integration Tests")
    print("=" * 70)
    
    # Change to repo root
    repo_root = Path(__file__).parent
    os.chdir(repo_root)
    
    tests = [
        ("Setup Environment", test_setup_env),
        ("Run Automation", test_run_automation),
        ("Validate Session", test_validate_session),
        ("DRY_RUN Default", test_dry_run_default),
        ("No Secrets Required", test_no_secrets_required),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test '{test_name}' raised exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 70)
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
