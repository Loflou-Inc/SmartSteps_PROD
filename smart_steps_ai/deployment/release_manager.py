#!/usr/bin/env python
"""
Release Manager for Smart Steps AI

This script manages the release process for Smart Steps AI, including:
- Version management and updating version numbers
- Release notes generation from git commits
- Package building and verification
- Release artifact management

Usage:
    python release_manager.py create-release [--major|--minor|--patch]
    python release_manager.py build-package
    python release_manager.py tag-release
    python release_manager.py generate-notes
    python release_manager.py full-release [--major|--minor|--patch]

Author: Smart Steps Team
Date: May, 2025
"""

import argparse
import configparser
import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Constants
ROOT_DIR = Path(__file__).parent.parent.absolute()
SRC_DIR = ROOT_DIR / "src"
VERSION_FILE = SRC_DIR / "smart_steps_ai" / "__init__.py"
SETUP_PY = ROOT_DIR / "setup.py"
RELEASE_NOTES_DIR = ROOT_DIR / "docs" / "release_notes"
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"

# Ensure the release notes directory exists
os.makedirs(RELEASE_NOTES_DIR, exist_ok=True)

def get_current_version() -> str:
    """Get the current version from the package __init__.py file."""
    if not VERSION_FILE.exists():
        print(f"Error: Version file not found at {VERSION_FILE}")
        sys.exit(1)
        
    version_pattern = r'__version__\s*=\s*["\']([^"\']+)["\']'
    with open(VERSION_FILE, "r") as f:
        content = f.read()
        version_match = re.search(version_pattern, content)
        if version_match:
            return version_match.group(1)
        else:
            print("Error: Unable to find version string in __init__.py")
            sys.exit(1)

def update_version(version_type: str) -> str:
    """
    Update version based on semantic versioning.
    
    Args:
        version_type: One of 'major', 'minor', or 'patch'
        
    Returns:
        The new version string
    """
    current_version = get_current_version()
    
    # Parse the version
    try:
        major, minor, patch = map(int, current_version.split('.'))
    except ValueError:
        print(f"Error: Current version {current_version} does not follow semantic versioning")
        sys.exit(1)
    
    # Update version number
    if version_type == "major":
        new_version = f"{major + 1}.0.0"
    elif version_type == "minor":
        new_version = f"{major}.{minor + 1}.0"
    elif version_type == "patch":
        new_version = f"{major}.{minor}.{patch + 1}"
    else:
        print(f"Error: Invalid version type: {version_type}")
        sys.exit(1)
    
    # Update the version in __init__.py
    with open(VERSION_FILE, "r") as f:
        content = f.read()
    
    new_content = re.sub(
        r'__version__\s*=\s*["\']([^"\']+)["\']',
        f'__version__ = "{new_version}"',
        content
    )
    
    with open(VERSION_FILE, "w") as f:
        f.write(new_content)
    
    print(f"Updated version from {current_version} to {new_version}")
    return new_version

def get_git_changes(since_tag: Optional[str] = None) -> List[str]:
    """
    Get a list of git commit messages since the given tag.
    
    Args:
        since_tag: Git tag to get changes since. If None, get all changes since the 
                   last tag.
                   
    Returns:
        List of commit messages
    """
    try:
        if since_tag is None:
            # Get the latest tag
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                # No tags found, get all commits
                print("No previous tags found. Getting all commits.")
                result = subprocess.run(
                    ["git", "log", "--pretty=format:%s"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.splitlines()
            
            since_tag = result.stdout.strip()
        
        # Get commits since the tag
        result = subprocess.run(
            ["git", "log", f"{since_tag}..HEAD", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=True
        )
        
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error executing git command: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def categorize_changes(commits: List[str]) -> Dict[str, List[str]]:
    """
    Categorize commit messages into features, fixes, docs, etc.
    
    Args:
        commits: List of commit messages
        
    Returns:
        Dictionary mapping categories to lists of commit messages
    """
    categories = {
        "features": [],
        "fixes": [],
        "docs": [],
        "refactor": [],
        "tests": [],
        "other": []
    }
    
    for commit in commits:
        commit = commit.strip()
        if not commit:
            continue
            
        lower_commit = commit.lower()
        
        if any(keyword in lower_commit for keyword in ["add", "feature", "implement", "support"]):
            categories["features"].append(commit)
        elif any(keyword in lower_commit for keyword in ["fix", "bug", "issue", "error", "crash"]):
            categories["fixes"].append(commit)
        elif any(keyword in lower_commit for keyword in ["doc", "readme", "comment"]):
            categories["docs"].append(commit)
        elif any(keyword in lower_commit for keyword in ["refactor", "cleanup", "rewrite", "restructure"]):
            categories["refactor"].append(commit)
        elif any(keyword in lower_commit for keyword in ["test", "spec", "assertion"]):
            categories["tests"].append(commit)
        else:
            categories["other"].append(commit)
    
    return categories

def generate_release_notes(version: str, changes: Dict[str, List[str]]) -> str:
    """
    Generate formatted release notes from categorized changes.
    
    Args:
        version: Version string
        changes: Dictionary mapping categories to lists of changes
        
    Returns:
        Formatted release notes as a string
    """
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    notes = f"# Smart Steps AI v{version} ({date_str})\n\n"
    
    for category, items in changes.items():
        if not items:
            continue
            
        if category == "features":
            notes += "## New Features\n\n"
        elif category == "fixes":
            notes += "## Bug Fixes\n\n"
        elif category == "docs":
            notes += "## Documentation\n\n"
        elif category == "refactor":
            notes += "## Refactoring\n\n"
        elif category == "tests":
            notes += "## Testing\n\n"
        else:
            notes += "## Other Changes\n\n"
        
        for item in items:
            notes += f"* {item}\n"
        
        notes += "\n"
    
    return notes

def save_release_notes(version: str, notes: str) -> str:
    """
    Save release notes to a file.
    
    Args:
        version: Version string
        notes: Release notes content
        
    Returns:
        Path to the saved file
    """
    filename = f"v{version.replace('.', '_')}.md"
    file_path = RELEASE_NOTES_DIR / filename
    
    with open(file_path, "w") as f:
        f.write(notes)
    
    print(f"Release notes saved to {file_path}")
    return str(file_path)

def build_package() -> bool:
    """
    Build the package using setuptools.
    
    Returns:
        True if the build was successful, False otherwise
    """
    try:
        # Clean build and dist directories
        if BUILD_DIR.exists():
            shutil.rmtree(BUILD_DIR)
        if DIST_DIR.exists():
            shutil.rmtree(DIST_DIR)
        
        # Build the package
        result = subprocess.run(
            [sys.executable, "setup.py", "sdist", "bdist_wheel"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("Package built successfully:")
        wheel_files = list(DIST_DIR.glob("*.whl"))
        tar_files = list(DIST_DIR.glob("*.tar.gz"))
        
        if wheel_files:
            print(f"  Wheel: {wheel_files[0].name}")
        if tar_files:
            print(f"  Source: {tar_files[0].name}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building package: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error building package: {e}")
        return False

def tag_release(version: str) -> bool:
    """
    Create a git tag for the release.
    
    Args:
        version: Version string
        
    Returns:
        True if tagging was successful, False otherwise
    """
    try:
        tag_name = f"v{version}"
        message = f"Release {tag_name}"
        
        # Add the version file
        subprocess.run(
            ["git", "add", str(VERSION_FILE)],
            check=True
        )
        
        # Add the release notes
        release_notes_file = RELEASE_NOTES_DIR / f"v{version.replace('.', '_')}.md"
        subprocess.run(
            ["git", "add", str(release_notes_file)],
            check=True
        )
        
        # Commit the changes
        subprocess.run(
            ["git", "commit", "-m", message],
            check=True
        )
        
        # Create the tag
        subprocess.run(
            ["git", "tag", "-a", tag_name, "-m", message],
            check=True
        )
        
        print(f"Created tag {tag_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error tagging release: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error tagging release: {e}")
        return False

def verify_package_integrity() -> bool:
    """
    Verify the integrity of the built packages.
    
    Returns:
        True if all packages pass verification, False otherwise
    """
    if not DIST_DIR.exists():
        print("Error: dist directory does not exist. Build the package first.")
        return False
    
    packages = list(DIST_DIR.glob("*.whl")) + list(DIST_DIR.glob("*.tar.gz"))
    if not packages:
        print("Error: No packages found in dist directory")
        return False
    
    all_valid = True
    for package in packages:
        try:
            # Compute SHA256 checksum
            with open(package, "rb") as f:
                data = f.read()
                checksum = hashlib.sha256(data).hexdigest()
            
            print(f"Verified {package.name} - SHA256: {checksum}")
        except Exception as e:
            print(f"Error verifying {package.name}: {e}")
            all_valid = False
    
    return all_valid

def create_checksum_file() -> str:
    """
    Create a file with checksums for all the packages.
    
    Returns:
        Path to the checksum file
    """
    if not DIST_DIR.exists():
        print("Error: dist directory does not exist. Build the package first.")
        return ""
    
    packages = list(DIST_DIR.glob("*.whl")) + list(DIST_DIR.glob("*.tar.gz"))
    if not packages:
        print("Error: No packages found in dist directory")
        return ""
    
    checksum_file = DIST_DIR / "checksums.txt"
    with open(checksum_file, "w") as f:
        for package in packages:
            try:
                # Compute SHA256 checksum
                with open(package, "rb") as pkg_file:
                    data = pkg_file.read()
                    checksum = hashlib.sha256(data).hexdigest()
                
                f.write(f"{checksum}  {package.name}\n")
            except Exception as e:
                print(f"Error computing checksum for {package.name}: {e}")
    
    print(f"Checksums saved to {checksum_file}")
    return str(checksum_file)

def full_release_process(version_type: str) -> bool:
    """
    Run the full release process.
    
    Args:
        version_type: One of 'major', 'minor', or 'patch'
        
    Returns:
        True if the release was successful, False otherwise
    """
    print("\n=== Starting full release process ===\n")
    
    # 1. Update version
    print("\n--- Updating version ---\n")
    new_version = update_version(version_type)
    
    # 2. Generate release notes
    print("\n--- Generating release notes ---\n")
    changes = get_git_changes()
    categorized_changes = categorize_changes(changes)
    notes = generate_release_notes(new_version, categorized_changes)
    release_notes_file = save_release_notes(new_version, notes)
    
    # 3. Build package
    print("\n--- Building package ---\n")
    if not build_package():
        print("Error: Package build failed")
        return False
    
    # 4. Verify package integrity
    print("\n--- Verifying package integrity ---\n")
    if not verify_package_integrity():
        print("Error: Package verification failed")
        return False
    
    # 5. Create checksums
    print("\n--- Creating checksums ---\n")
    checksum_file = create_checksum_file()
    
    # 6. Tag release
    print("\n--- Tagging release ---\n")
    if not tag_release(new_version):
        print("Error: Tagging release failed")
        return False
    
    print(f"\n=== Release v{new_version} completed successfully ===\n")
    print(f"Release notes: {release_notes_file}")
    print(f"Packages: {DIST_DIR}")
    print(f"Checksums: {checksum_file}")
    
    return True

def main():
    """Main function to parse arguments and execute commands."""
    parser = argparse.ArgumentParser(description="Smart Steps AI Release Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create release command
    create_parser = subparsers.add_parser("create-release", help="Create a new release by updating version number")
    version_group = create_parser.add_mutually_exclusive_group(required=True)
    version_group.add_argument("--major", action="store_true", help="Increment major version")
    version_group.add_argument("--minor", action="store_true", help="Increment minor version")
    version_group.add_argument("--patch", action="store_true", help="Increment patch version")
    
    # Build package command
    subparsers.add_parser("build-package", help="Build package distributions")
    
    # Tag release command
    subparsers.add_parser("tag-release", help="Create git tag for the current version")
    
    # Generate release notes command
    subparsers.add_parser("generate-notes", help="Generate release notes from git commits")
    
    # Full release command
    full_parser = subparsers.add_parser("full-release", help="Run the full release process")
    full_version_group = full_parser.add_mutually_exclusive_group(required=True)
    full_version_group.add_argument("--major", action="store_true", help="Increment major version")
    full_version_group.add_argument("--minor", action="store_true", help="Increment minor version")
    full_version_group.add_argument("--patch", action="store_true", help="Increment patch version")
    
    args = parser.parse_args()
    
    if args.command == "create-release":
        version_type = "major" if args.major else "minor" if args.minor else "patch"
        update_version(version_type)
    
    elif args.command == "build-package":
        build_package()
        verify_package_integrity()
        create_checksum_file()
    
    elif args.command == "tag-release":
        version = get_current_version()
        tag_release(version)
    
    elif args.command == "generate-notes":
        version = get_current_version()
        changes = get_git_changes()
        categorized_changes = categorize_changes(changes)
        notes = generate_release_notes(version, categorized_changes)
        save_release_notes(version, notes)
    
    elif args.command == "full-release":
        version_type = "major" if args.major else "minor" if args.minor else "patch"
        full_release_process(version_type)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
