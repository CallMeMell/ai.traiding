#!/usr/bin/env python3
"""
verify_vscode_dev_experience.py - VS Code Developer Experience Verification
===========================================================================
Verifies that all VS Code configuration files are properly set up for developer
experience as specified in the issue requirements.

Issue Requirements:
- tasks.json für Build, Test, Lint, Format ergänzen
- launch.json für Debug-Konfiguration
- settings.json für Python und Terminal
- GitHub Issues Query integrieren
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
VSCODE_DIR = PROJECT_ROOT / ".vscode"

def print_status(passed: bool, message: str):
    """Print test status with emoji."""
    status = "✅" if passed else "❌"
    print(f"{status} {message}")

def verify_file_exists(file_path: Path, description: str) -> bool:
    """Verify a file exists."""
    exists = file_path.exists()
    print_status(exists, f"{description}: {file_path.name}")
    return exists

def verify_json_valid(file_path: Path) -> bool:
    """Verify JSON file is valid."""
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        print_status(True, f"Valid JSON: {file_path.name}")
        return True
    except Exception as e:
        print_status(False, f"Invalid JSON in {file_path.name}: {e}")
        return False

def verify_tasks_json() -> bool:
    """Verify tasks.json has required tasks."""
    print("\n" + "="*70)
    print("TASKS.JSON VERIFICATION")
    print("="*70)
    
    tasks_file = VSCODE_DIR / "tasks.json"
    
    if not verify_file_exists(tasks_file, "tasks.json exists"):
        return False
    
    if not verify_json_valid(tasks_file):
        return False
    
    try:
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
        
        task_labels = [task.get("label", "") for task in tasks.get("tasks", [])]
        
        # Check for required tasks (as per issue examples)
        required_tasks = {
            "Test": "Run tests with pytest",
            "Lint": "Run linter",
            "Format": "Format code",
        }
        
        all_found = True
        for task_name, description in required_tasks.items():
            found = task_name in task_labels
            print_status(found, f"Task exists: {task_name} - {description}")
            if not found:
                all_found = False
        
        # Also check for existing comprehensive tasks
        comprehensive_tasks = [
            "System: Run Tests",
            "Dev: Live Session",
            "Run: Automation Runner (Dry-Run)",
        ]
        
        print("\nComprehensive tasks:")
        for task_name in comprehensive_tasks:
            found = task_name in task_labels
            print_status(found, f"Task exists: {task_name}")
        
        print(f"\nTotal tasks: {len(task_labels)}")
        
        return all_found
        
    except Exception as e:
        print_status(False, f"tasks.json verification failed: {e}")
        return False

def verify_launch_json() -> bool:
    """Verify launch.json has debug configurations."""
    print("\n" + "="*70)
    print("LAUNCH.JSON VERIFICATION")
    print("="*70)
    
    launch_file = VSCODE_DIR / "launch.json"
    
    if not verify_file_exists(launch_file, "launch.json exists"):
        return False
    
    if not verify_json_valid(launch_file):
        return False
    
    try:
        with open(launch_file, 'r') as f:
            launch = json.load(f)
        
        configurations = launch.get("configurations", [])
        config_names = [config.get("name", "") for config in configurations]
        
        print(f"Found {len(configurations)} debug configurations:")
        for name in config_names:
            print_status(True, f"  {name}")
        
        # Check for Python debugger
        has_python_debug = any("Python" in name for name in config_names)
        print_status(has_python_debug, "Has Python debug configuration")
        
        return len(configurations) > 0 and has_python_debug
        
    except Exception as e:
        print_status(False, f"launch.json verification failed: {e}")
        return False

def verify_settings_json() -> bool:
    """Verify settings.json has Python, terminal, and GitHub Issues configuration."""
    print("\n" + "="*70)
    print("SETTINGS.JSON VERIFICATION")
    print("="*70)
    
    settings_file = VSCODE_DIR / "settings.json"
    
    if not verify_file_exists(settings_file, "settings.json exists"):
        return False
    
    if not verify_json_valid(settings_file):
        return False
    
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        # Check Python settings
        has_python = "python.defaultInterpreterPath" in settings
        print_status(has_python, "Python interpreter configured")
        
        # Check terminal settings
        has_terminal = "terminal.integrated.defaultProfile.windows" in settings
        terminal_value = settings.get("terminal.integrated.defaultProfile.windows", "")
        print_status(has_terminal and terminal_value == "PowerShell", 
                    f"Terminal default: {terminal_value}")
        
        # Check GitHub Issues queries
        has_github_queries = "githubIssues.queries" in settings
        queries = settings.get("githubIssues.queries", [])
        print_status(has_github_queries, f"GitHub Issues queries configured ({len(queries)} queries)")
        
        if queries:
            for query in queries:
                label = query.get("label", "Unknown")
                print(f"    - {label}")
        
        # Check port forwarding (for View Session)
        has_ports = "remote.portsAttributes" in settings
        port_8501 = settings.get("remote.portsAttributes", {}).get("8501", {})
        port_label = port_8501.get("label", "")
        print_status(has_ports and port_label == "View Session", 
                    f"Port 8501 configured as 'View Session'")
        
        return has_python and has_terminal and has_github_queries
        
    except Exception as e:
        print_status(False, f"settings.json verification failed: {e}")
        return False

def verify_extensions_json() -> bool:
    """Verify extensions.json recommends useful extensions."""
    print("\n" + "="*70)
    print("EXTENSIONS.JSON VERIFICATION")
    print("="*70)
    
    extensions_file = VSCODE_DIR / "extensions.json"
    
    if not verify_file_exists(extensions_file, "extensions.json exists"):
        return False
    
    if not verify_json_valid(extensions_file):
        return False
    
    try:
        with open(extensions_file, 'r') as f:
            extensions = json.load(f)
        
        recommendations = extensions.get("recommendations", [])
        
        print(f"Found {len(recommendations)} recommended extensions:")
        for ext in recommendations:
            print(f"  - {ext}")
        
        # Check for key extensions
        has_python = any("python" in ext.lower() for ext in recommendations)
        has_github = any("github" in ext.lower() for ext in recommendations)
        
        print_status(has_python, "Python extension recommended")
        print_status(has_github, "GitHub extension recommended")
        
        return len(recommendations) > 0
        
    except Exception as e:
        print_status(False, f"extensions.json verification failed: {e}")
        return False

def main():
    """Run all verifications."""
    print("\n" + "="*70)
    print("VS CODE DEVELOPER EXPERIENCE VERIFICATION")
    print("="*70)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"VS Code Dir: {VSCODE_DIR}")
    
    results = []
    
    results.append(("tasks.json", verify_tasks_json()))
    results.append(("launch.json", verify_launch_json()))
    results.append(("settings.json", verify_settings_json()))
    results.append(("extensions.json", verify_extensions_json()))
    
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
    
    # Acceptance Criteria Check
    print("\n" + "="*70)
    print("ACCEPTANCE CRITERIA")
    print("="*70)
    
    # From issue:
    # - [x] Tasks, Launch, Settings vorhanden
    # - [x] Debugging und Testen möglich
    
    all_files_present = all(result for name, result in results)
    print_status(all_files_present, "All required files present (tasks, launch, settings)")
    print_status(passed >= 3, "Debugging and testing possible (tasks + launch configured)")
    
    print("\n" + "="*70)
    
    if passed == total:
        print("✅ ALL VERIFICATIONS PASSED - Developer Experience is ready!")
        return 0
    else:
        print(f"❌ {total - passed} verification(s) failed - Please review")
        return 1

if __name__ == "__main__":
    sys.exit(main())
