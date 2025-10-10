"""
release.py - Release Automation Script
=====================================
Automate version bumping, changelog generation, and tagging.
"""

import sys
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def get_current_version():
    """Get current version from VERSION file."""
    version_file = Path(__file__).parent.parent / 'VERSION'
    with open(version_file, 'r') as f:
        return f.read().strip()


def bump_version(version, bump_type='patch'):
    """
    Bump version number.
    
    Args:
        version: Current version (e.g., '1.0.0')
        bump_type: Type of bump ('major', 'minor', 'patch')
        
    Returns:
        New version string
    """
    # Remove -dev suffix if present
    version = version.replace('-dev', '')
    
    major, minor, patch = map(int, version.split('.'))
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return f"{major}.{minor}.{patch}"


def update_version_file(new_version):
    """Update VERSION file."""
    version_file = Path(__file__).parent.parent / 'VERSION'
    with open(version_file, 'w') as f:
        f.write(f"{new_version}\n")
    print(f"✓ Updated VERSION file to {new_version}")


def update_changelog(new_version):
    """Update CHANGELOG.md with new version."""
    changelog_file = Path(__file__).parent.parent / 'CHANGELOG.md'
    
    with open(changelog_file, 'r') as f:
        content = f.read()
    
    # Replace [Unreleased] with version and date
    today = datetime.now().strftime('%Y-%m-%d')
    new_header = f"## [{new_version}] - {today}"
    
    content = content.replace('## [Unreleased]', f'## [Unreleased]\n\n{new_header}')
    
    with open(changelog_file, 'w') as f:
        f.write(content)
    
    print(f"✓ Updated CHANGELOG.md with version {new_version}")


def create_git_tag(version):
    """Create git tag for release."""
    try:
        # Commit changes
        subprocess.run(['git', 'add', 'VERSION', 'CHANGELOG.md'], check=True)
        subprocess.run(['git', 'commit', '-m', f'Release v{version}'], check=True)
        
        # Create tag
        subprocess.run(['git', 'tag', '-a', f'v{version}', '-m', f'Release v{version}'], check=True)
        
        print(f"✓ Created git tag v{version}")
        print("\n⚠️  Don't forget to push:")
        print(f"   git push origin main")
        print(f"   git push origin v{version}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")
        return False
    
    return True


def main():
    """Main release script."""
    print("=" * 60)
    print("🚀 Release Automation Script")
    print("=" * 60)
    print()
    
    # Get current version
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    print()
    
    # Ask for bump type
    print("Select release type:")
    print("  1. Patch (x.x.X) - Bug fixes")
    print("  2. Minor (x.X.0) - New features")
    print("  3. Major (X.0.0) - Breaking changes")
    print()
    
    choice = input("Enter choice (1-3) or 'q' to quit: ").strip()
    
    if choice == 'q':
        print("Cancelled.")
        return
    
    bump_types = {'1': 'patch', '2': 'minor', '3': 'major'}
    if choice not in bump_types:
        print("❌ Invalid choice")
        return
    
    bump_type = bump_types[choice]
    
    # Calculate new version
    new_version = bump_version(current_version, bump_type)
    print()
    print(f"New version will be: {new_version}")
    print()
    
    # Confirm
    confirm = input("Proceed with release? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return
    
    print()
    print("Processing release...")
    print()
    
    # Update files
    update_version_file(new_version)
    update_changelog(new_version)
    
    # Create git tag
    if create_git_tag(new_version):
        print()
        print("=" * 60)
        print(f"✅ Release v{new_version} prepared successfully!")
        print("=" * 60)
    else:
        print()
        print("⚠️  Release prepared but git tagging failed")
        print("   Please review and commit manually")


if __name__ == '__main__':
    main()
