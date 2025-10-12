"""
verify_os_imports.py - Verification Script for OS Module Imports
===============================================================
Verifies that all Python files using the os module have proper imports.
This script helps prevent F821 flake8 errors (undefined name 'os').
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional


def check_os_import(filepath: Path) -> Optional[Tuple[int, str]]:
    """
    Check if a file uses os module but doesn't import it.
    
    Args:
        filepath: Path to the Python file to check
        
    Returns:
        Tuple of (line_number, code_snippet) if issue found, None otherwise
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for os module usage (os.something)
        has_os_usage = bool(re.search(r'\bos\.[a-zA-Z_]', content))
        
        if not has_os_usage:
            return None
        
        # Check for import os statement
        has_import = bool(
            re.search(r'^\s*import\s+os\s*($|,|\s)', content, re.MULTILINE) or
            re.search(r'^\s*from\s+os\s+import', content, re.MULTILINE)
        )
        
        if not has_import:
            # Find first line where os. is used
            for i, line in enumerate(content.split('\n'), 1):
                if re.search(r'\bos\.', line) and not line.strip().startswith('#'):
                    return (i, line.strip()[:80])
        
        return None
    except Exception as e:
        print(f"  ⚠️ Error checking {filepath}: {e}")
        return None


def verify_all_python_files() -> List[Tuple[Path, int, str]]:
    """
    Verify all Python files in the repository.
    
    Returns:
        List of issues found (filepath, line_number, code_snippet)
    """
    issues = []
    excluded_dirs = {'venv', 'env', 'Git', '__pycache__', '.git', 'node_modules'}
    
    for py_file in Path('.').rglob('*.py'):
        # Skip excluded directories
        if any(excluded in py_file.parts for excluded in excluded_dirs):
            continue
        
        result = check_os_import(py_file)
        if result:
            line_num, code = result
            issues.append((py_file, line_num, code))
    
    return issues


def main():
    """Main verification function."""
    print("=" * 70)
    print("OS MODULE IMPORT VERIFICATION")
    print("=" * 70)
    print()
    print("Checking all Python files for proper 'import os' statements...")
    print()
    
    issues = verify_all_python_files()
    
    if issues:
        print(f"❌ Found {len(issues)} file(s) with missing os imports:")
        print()
        for filepath, line_num, code in sorted(issues):
            print(f"  {filepath} (line {line_num}):")
            print(f"    {code}")
            print()
        print("=" * 70)
        print("Please add 'import os' at the top of these files.")
        return 1
    else:
        print("✅ All Python files have proper os imports!")
        print()
        print("=" * 70)
        print("Verification complete - no issues found.")
        return 0


if __name__ == '__main__':
    sys.exit(main())
