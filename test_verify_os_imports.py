"""
test_verify_os_imports.py - Unit Tests for OS Import Verification
================================================================
Tests to ensure the verification script works correctly.
"""

import sys
import tempfile
import shutil
from pathlib import Path


def test_missing_import_detection():
    """Test that missing os import is detected."""
    print("=" * 70)
    print("TEST: Missing OS Import Detection")
    print("=" * 70)
    
    # Create a temporary directory for test files
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_bad_import.py"
        
        # Create a file that uses os but doesn't import it
        test_file.write_text("""
# This file intentionally has a missing import
def main():
    path = os.path.join('data', 'file.txt')
    return path
""")
        
        # Import and run verification on this file
        sys.path.insert(0, str(Path(__file__).parent))
        from verify_os_imports import check_os_import
        
        result = check_os_import(test_file)
        
        if result:
            line_num, code = result
            print(f"  ✅ Correctly detected missing import at line {line_num}")
            print(f"     Code: {code}")
            return True
        else:
            print("  ❌ Failed to detect missing import")
            return False


def test_proper_import_accepted():
    """Test that proper os import is accepted."""
    print("\n" + "=" * 70)
    print("TEST: Proper OS Import Accepted")
    print("=" * 70)
    
    # Create a temporary directory for test files
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_good_import.py"
        
        # Create a file that properly imports os
        test_file.write_text("""
import os

def main():
    path = os.path.join('data', 'file.txt')
    return path
""")
        
        # Import and run verification on this file
        sys.path.insert(0, str(Path(__file__).parent))
        from verify_os_imports import check_os_import
        
        result = check_os_import(test_file)
        
        if result is None:
            print("  ✅ Correctly accepted proper import")
            return True
        else:
            print("  ❌ Incorrectly flagged proper import")
            return False


def test_no_os_usage():
    """Test that files without os usage are not flagged."""
    print("\n" + "=" * 70)
    print("TEST: No OS Usage")
    print("=" * 70)
    
    # Create a temporary directory for test files
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_no_os.py"
        
        # Create a file that doesn't use os
        test_file.write_text("""
import sys

def main():
    print("Hello, world!")
    return 0
""")
        
        # Import and run verification on this file
        sys.path.insert(0, str(Path(__file__).parent))
        from verify_os_imports import check_os_import
        
        result = check_os_import(test_file)
        
        if result is None:
            print("  ✅ Correctly ignored file without os usage")
            return True
        else:
            print("  ❌ Incorrectly flagged file without os usage")
            return False


def main():
    """Run all tests."""
    print("\n")
    print("=" * 70)
    print("OS IMPORT VERIFICATION - UNIT TESTS")
    print("=" * 70)
    print()
    
    results = []
    
    # Run tests
    results.append(("Missing Import Detection", test_missing_import_detection()))
    results.append(("Proper Import Accepted", test_proper_import_accepted()))
    results.append(("No OS Usage", test_no_os_usage()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {name}")
    
    print("\n" + "=" * 70)
    print(f"Result: {passed}/{total} tests passed")
    print("=" * 70)
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
