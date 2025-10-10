#!/usr/bin/env python3
"""
verify_issue_templates.py - Verification Script for Issue Templates

Verifies that all GitHub Issue Templates are properly implemented and match
the requirements specified in Issue #56.

Requirements from Issue #56:
- automation-task.yml exists
- manual-task.yml exists
- Fields and descriptions match system plan
- Templates are in .github/ISSUE_TEMPLATE/ directory
"""

import sys
from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).parent
TEMPLATE_DIR = PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE"

def print_status(passed: bool, message: str):
    """Print test status with color."""
    status = "✅" if passed else "❌"
    print(f"{status} {message}")
    return passed

def verify_file_exists(filepath: Path, name: str) -> bool:
    """Verify a file exists."""
    exists = filepath.exists()
    print_status(exists, f"{name} exists at {filepath.relative_to(PROJECT_ROOT)}")
    return exists

def verify_template_structure(filepath: Path) -> bool:
    """Verify template has valid YAML structure."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            print_status(False, f"{filepath.name}: Empty YAML")
            return False
        
        # Check required top-level keys
        required_keys = ['name', 'description', 'body']
        missing = [key for key in required_keys if key not in data]
        
        if missing:
            print_status(False, f"{filepath.name}: Missing keys: {missing}")
            return False
        
        print_status(True, f"{filepath.name}: Valid structure")
        return True
    
    except yaml.YAMLError as e:
        print_status(False, f"{filepath.name}: YAML parse error: {e}")
        return False
    except Exception as e:
        print_status(False, f"{filepath.name}: Error: {e}")
        return False

def verify_automation_task_fields() -> bool:
    """Verify automation-task.yml has all required fields."""
    filepath = TEMPLATE_DIR / "automation-task.yml"
    
    required_fields = [
        'goal',
        'measurable-outcome',
        'scope',
        'non-goals',
        'acceptance-criteria',
        'references',
        'effort'
    ]
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Extract field IDs from body
        field_ids = []
        for item in data.get('body', []):
            if 'id' in item.get('attributes', {}):
                field_ids.append(item['attributes']['id'])
            elif 'id' in item:
                field_ids.append(item['id'])
        
        all_present = True
        for field in required_fields:
            present = field in field_ids
            if not present:
                print_status(False, f"automation-task.yml: Missing field '{field}'")
                all_present = False
        
        if all_present:
            print_status(True, f"automation-task.yml: All {len(required_fields)} required fields present")
        
        return all_present
    
    except Exception as e:
        print_status(False, f"automation-task.yml: Error checking fields: {e}")
        return False

def verify_manual_task_fields() -> bool:
    """Verify manual-task.yml has all required fields."""
    filepath = TEMPLATE_DIR / "manual-task.yml"
    
    required_fields = [
        'task-title',
        'steps-checklist',
        'proof',
        'acceptance-criteria',
        'effort',
        'prerequisites'
    ]
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Extract field IDs from body
        field_ids = []
        for item in data.get('body', []):
            if 'id' in item.get('attributes', {}):
                field_ids.append(item['attributes']['id'])
            elif 'id' in item:
                field_ids.append(item['id'])
        
        all_present = True
        for field in required_fields:
            present = field in field_ids
            if not present:
                print_status(False, f"manual-task.yml: Missing field '{field}'")
                all_present = False
        
        if all_present:
            print_status(True, f"manual-task.yml: All {len(required_fields)} required fields present")
        
        return all_present
    
    except Exception as e:
        print_status(False, f"manual-task.yml: Error checking fields: {e}")
        return False

def verify_config() -> bool:
    """Verify config.yml exists and has proper structure."""
    filepath = TEMPLATE_DIR / "config.yml"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Check that blank issues are disabled
        blank_disabled = data.get('blank_issues_enabled') == False
        has_contact_links = 'contact_links' in data and len(data['contact_links']) > 0
        
        print_status(blank_disabled, "config.yml: Blank issues disabled")
        print_status(has_contact_links, "config.yml: Contact links present")
        
        return blank_disabled and has_contact_links
    
    except Exception as e:
        print_status(False, f"config.yml: Error: {e}")
        return False

def verify_documentation() -> bool:
    """Verify documentation mentions the templates."""
    readme = PROJECT_ROOT / "README.md"
    progress = PROJECT_ROOT / "PROGRESS.md"
    
    results = []
    
    # Check README.md
    try:
        with open(readme, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_section = "Effiziente Issues" in content or "Issue-Vorlagen" in content
        mentions_auto = "[Auto]" in content and "Automation Task" in content
        mentions_manual = "[Manual]" in content and "Manual Task" in content
        
        results.append(print_status(has_section, "README.md: Has issue templates section"))
        results.append(print_status(mentions_auto, "README.md: Mentions automation tasks"))
        results.append(print_status(mentions_manual, "README.md: Mentions manual tasks"))
    
    except Exception as e:
        results.append(print_status(False, f"README.md: Error: {e}"))
    
    # Check PROGRESS.md
    try:
        with open(progress, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_section = "GitHub Issue Forms" in content
        mentions_templates = "automation-task.yml" in content and "manual-task.yml" in content
        
        results.append(print_status(has_section, "PROGRESS.md: Has issue forms section"))
        results.append(print_status(mentions_templates, "PROGRESS.md: Documents templates"))
    
    except Exception as e:
        results.append(print_status(False, f"PROGRESS.md: Error: {e}"))
    
    return all(results)

def main():
    """Run all verifications."""
    print("=" * 70)
    print("ISSUE TEMPLATES VERIFICATION - Issue #56")
    print("=" * 70)
    print()
    
    results = []
    
    print("📁 File Existence:")
    results.append(verify_file_exists(TEMPLATE_DIR / "automation-task.yml", "automation-task.yml"))
    results.append(verify_file_exists(TEMPLATE_DIR / "manual-task.yml", "manual-task.yml"))
    results.append(verify_file_exists(TEMPLATE_DIR / "epic-tracking.yml", "epic-tracking.yml (bonus)"))
    results.append(verify_file_exists(TEMPLATE_DIR / "config.yml", "config.yml"))
    print()
    
    print("🔧 YAML Structure:")
    if (TEMPLATE_DIR / "automation-task.yml").exists():
        results.append(verify_template_structure(TEMPLATE_DIR / "automation-task.yml"))
    if (TEMPLATE_DIR / "manual-task.yml").exists():
        results.append(verify_template_structure(TEMPLATE_DIR / "manual-task.yml"))
    if (TEMPLATE_DIR / "epic-tracking.yml").exists():
        results.append(verify_template_structure(TEMPLATE_DIR / "epic-tracking.yml"))
    print()
    
    print("✨ Required Fields:")
    results.append(verify_automation_task_fields())
    results.append(verify_manual_task_fields())
    print()
    
    print("⚙️ Configuration:")
    results.append(verify_config())
    print()
    
    print("📚 Documentation:")
    results.append(verify_documentation())
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"Passed: {passed}/{total} checks ({success_rate:.1f}%)")
    
    if passed == total:
        print("\n🎉 All verifications passed! Issue #56 is COMPLETE.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} verification(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
