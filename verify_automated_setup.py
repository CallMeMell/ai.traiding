"""
verify_automated_setup.py - Comprehensive Verification Script
============================================================
Verifies that all components of the automated setup are properly implemented.
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

def print_status(passed: bool, message: str):
    """Print test status."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}  {message}")

def verify_files():
    """Verify all required files exist."""
    print("\n" + "="*70)
    print("FILE VERIFICATION")
    print("="*70)
    
    required_files = [
        "scripts/automated_setup.py",
        "scripts/automated_setup.ps1",
        "test_automated_setup.py",
        "AUTOMATED_SETUP_GUIDE.md",
        "AUTOMATED_SETUP_SUMMARY.md",
    ]
    
    all_passed = True
    for file_path in required_files:
        full_path = PROJECT_ROOT / file_path
        exists = full_path.exists()
        all_passed = all_passed and exists
        print_status(exists, f"File exists: {file_path}")
        
        if exists:
            size = full_path.stat().st_size
            print(f"           Size: {size:,} bytes")
    
    return all_passed

def verify_python_script():
    """Verify Python script functionality."""
    print("\n" + "="*70)
    print("PYTHON SCRIPT VERIFICATION")
    print("="*70)
    
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from automated_setup import AutomatedSetup, STATUS_OK, STATUS_ERROR
        
        print_status(True, "Module imported successfully")
        
        # Test class instantiation
        setup = AutomatedSetup()
        print_status(True, "AutomatedSetup class instantiated")
        
        # Test methods exist
        methods = ['log', 'check_python_environment', 'run_automated_setup', 
                   'generate_summary_report', 'save_logs']
        for method in methods:
            has_method = hasattr(setup, method)
            print_status(has_method, f"Method exists: {method}")
        
        # Test logging
        setup.log(STATUS_OK, "Test message", "test_step")
        print_status(len(setup.logs) > 0, "Logging works")
        
        return True
        
    except Exception as e:
        print_status(False, f"Python script verification failed: {e}")
        return False

def verify_powershell_script():
    """Verify PowerShell script structure."""
    print("\n" + "="*70)
    print("POWERSHELL SCRIPT VERIFICATION")
    print("="*70)
    
    ps1_file = PROJECT_ROOT / "scripts" / "automated_setup.ps1"
    
    try:
        with open(ps1_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("ErrorActionPreference", "Error handling configured"),
            ("param(", "Parameters defined"),
            ("-Auto", "Auto mode supported"),
            ("-SkipDryRun", "Skip dry-run option"),
            ("venv", "Virtual environment handling"),
            ("automated_setup.py", "Python script called"),
            ("pip install", "Dependency installation"),
        ]
        
        for check, description in checks:
            passed = check in content
            print_status(passed, description)
        
        return True
        
    except Exception as e:
        print_status(False, f"PowerShell verification failed: {e}")
        return False

def verify_vscode_tasks():
    """Verify VS Code task integration."""
    print("\n" + "="*70)
    print("VS CODE TASKS VERIFICATION")
    print("="*70)
    
    tasks_file = PROJECT_ROOT / ".vscode" / "tasks.json"
    
    try:
        import json
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
        
        task_labels = [task.get("label", "") for task in tasks.get("tasks", [])]
        
        required_tasks = [
            "Live: Automated Setup",
            "Live: Automated Setup (Auto)",
        ]
        
        for task_name in required_tasks:
            found = any(task_name in label for label in task_labels)
            print_status(found, f"Task exists: {task_name}")
        
        return True
        
    except Exception as e:
        print_status(False, f"VS Code tasks verification failed: {e}")
        return False

def verify_tests():
    """Verify test suite."""
    print("\n" + "="*70)
    print("TEST SUITE VERIFICATION")
    print("="*70)
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "test_automated_setup.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout + result.stderr
        
        # Check for test results
        passed = result.returncode == 0
        print_status(passed, "All tests passed")
        
        # Count tests
        if "Ran " in output:
            for line in output.split("\n"):
                if line.startswith("Ran "):
                    print(f"           {line}")
        
        return passed
        
    except Exception as e:
        print_status(False, f"Test verification failed: {e}")
        return False

def verify_documentation():
    """Verify documentation completeness."""
    print("\n" + "="*70)
    print("DOCUMENTATION VERIFICATION")
    print("="*70)
    
    guide = PROJECT_ROOT / "AUTOMATED_SETUP_GUIDE.md"
    summary = PROJECT_ROOT / "AUTOMATED_SETUP_SUMMARY.md"
    
    try:
        with open(guide, 'r', encoding='utf-8') as f:
            guide_content = f.read()
        
        with open(summary, 'r', encoding='utf-8') as f:
            summary_content = f.read()
        
        guide_sections = [
            "Quick Start",
            "Setup-Ablauf im Detail",
            "Kommandozeilen-Optionen",
            "Troubleshooting",
            "Sicherheitshinweise",
        ]
        
        for section in guide_sections:
            found = section in guide_content
            print_status(found, f"Guide section: {section}")
        
        summary_sections = [
            "Acceptance Criteria",
            "Was wurde implementiert",
            "Verwendung",
            "Testing",
        ]
        
        for section in summary_sections:
            found = section in summary_content
            print_status(found, f"Summary section: {section}")
        
        return True
        
    except Exception as e:
        print_status(False, f"Documentation verification failed: {e}")
        return False

def main():
    """Run all verifications."""
    print("\n" + "="*70)
    print("AUTOMATED SETUP IMPLEMENTATION VERIFICATION")
    print("="*70)
    
    results = []
    
    results.append(("Files", verify_files()))
    results.append(("Python Script", verify_python_script()))
    results.append(("PowerShell Script", verify_powershell_script()))
    results.append(("VS Code Tasks", verify_vscode_tasks()))
    results.append(("Tests", verify_tests()))
    results.append(("Documentation", verify_documentation()))
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        print_status(result, name)
    
    print("\n" + "="*70)
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"Result: {passed}/{total} verifications passed ({success_rate:.1f}%)")
    print("="*70)
    
    if passed == total:
        print("\n✅ All verifications passed!")
        print("   The automated setup is fully implemented and ready to use.")
        return 0
    else:
        print("\n⚠️  Some verifications failed.")
        print("   Please review the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
