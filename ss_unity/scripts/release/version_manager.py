#!/usr/bin/env python3
"""
Smart Steps AI Professional Persona Module - Version Manager

This script manages semantic versioning for the Smart Steps AI module.
It handles version bumping, version file management, and version validation.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

# Constants
VERSION_FILE = "version.json"
DEFAULT_VERSION = "1.0.0"


class VersionType(Enum):
    """Version increment type"""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


class VersionManager:
    """Manages semantic versioning for the Smart Steps AI module"""
    
    def __init__(self, root_dir: str):
        """Initialize the version manager
        
        Args:
            root_dir: Root directory of the project
        """
        self.root_dir = root_dir
        self.version_file_path = os.path.join(self.root_dir, VERSION_FILE)
        self.version_info = self._load_version_info()
    
    def _load_version_info(self) -> Dict:
        """Load version information from version file
        
        Returns:
            Dict containing version information
        """
        if os.path.exists(self.version_file_path):
            try:
                with open(self.version_file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading version file: {e}")
                return self._create_default_version_info()
        else:
            return self._create_default_version_info()
    
    def _create_default_version_info(self) -> Dict:
        """Create default version information
        
        Returns:
            Dict containing default version information
        """
        return {
            "version": DEFAULT_VERSION,
            "major": 1,
            "minor": 0,
            "patch": 0,
            "pre_release": None,
            "build": None,
            "last_updated": datetime.now().isoformat(),
            "history": []
        }
    
    def _save_version_info(self) -> None:
        """Save version information to version file"""
        try:
            with open(self.version_file_path, 'w') as f:
                json.dump(self.version_info, f, indent=2)
        except IOError as e:
            print(f"Error writing version file: {e}")
            sys.exit(1)
    
    def get_version(self) -> str:
        """Get the current version string
        
        Returns:
            Current version string
        """
        return self.version_info["version"]
    
    def get_version_parts(self) -> Tuple[int, int, int, Optional[str], Optional[str]]:
        """Get the parts of the current version
        
        Returns:
            Tuple of (major, minor, patch, pre_release, build)
        """
        return (
            self.version_info["major"],
            self.version_info["minor"],
            self.version_info["patch"],
            self.version_info["pre_release"],
            self.version_info["build"]
        )
    
    def bump_version(self, version_type: VersionType, pre_release: Optional[str] = None,
                     build: Optional[str] = None, commit_msg: Optional[str] = None) -> str:
        """Bump the version according to semantic versioning
        
        Args:
            version_type: Type of version increment (major, minor, patch)
            pre_release: Pre-release identifier (e.g., 'alpha', 'beta')
            build: Build metadata
            commit_msg: Commit message for the version bump
            
        Returns:
            The new version string
        """
        major, minor, patch, _, _ = self.get_version_parts()
        
        # Save the previous version in history
        prev_version = self.get_version()
        history_entry = {
            "version": prev_version,
            "date": datetime.now().isoformat(),
            "message": commit_msg or f"Version bump: {version_type.value}"
        }
        self.version_info["history"].append(history_entry)
        
        # Update version parts based on version type
        if version_type == VersionType.MAJOR:
            major += 1
            minor = 0
            patch = 0
        elif version_type == VersionType.MINOR:
            minor += 1
            patch = 0
        elif version_type == VersionType.PATCH:
            patch += 1
        
        # Update version info
        self.version_info["major"] = major
        self.version_info["minor"] = minor
        self.version_info["patch"] = patch
        self.version_info["pre_release"] = pre_release
        self.version_info["build"] = build
        
        # Build version string
        version = f"{major}.{minor}.{patch}"
        if pre_release:
            version += f"-{pre_release}"
        if build:
            version += f"+{build}"
        
        self.version_info["version"] = version
        self.version_info["last_updated"] = datetime.now().isoformat()
        
        # Save the updated version info
        self._save_version_info()
        
        return version
    
    def set_version(self, version_str: str, commit_msg: Optional[str] = None) -> str:
        """Set the version to a specific value
        
        Args:
            version_str: Version string to set
            commit_msg: Commit message for the version change
            
        Returns:
            The set version string
            
        Raises:
            ValueError: If the version string is invalid
        """
        # Validate and parse the version string
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$"
        match = re.match(pattern, version_str)
        if not match:
            raise ValueError(f"Invalid version string: {version_str}")
        
        major = int(match.group(1))
        minor = int(match.group(2))
        patch = int(match.group(3))
        pre_release = match.group(4)
        build = match.group(5)
        
        # Save the previous version in history
        prev_version = self.get_version()
        history_entry = {
            "version": prev_version,
            "date": datetime.now().isoformat(),
            "message": commit_msg or f"Version set: {version_str}"
        }
        self.version_info["history"].append(history_entry)
        
        # Update version info
        self.version_info["version"] = version_str
        self.version_info["major"] = major
        self.version_info["minor"] = minor
        self.version_info["patch"] = patch
        self.version_info["pre_release"] = pre_release
        self.version_info["build"] = build
        self.version_info["last_updated"] = datetime.now().isoformat()
        
        # Save the updated version info
        self._save_version_info()
        
        return version_str
    
    def get_version_history(self) -> List[Dict]:
        """Get the version history
        
        Returns:
            List of version history entries
        """
        return self.version_info.get("history", [])


def main():
    """Main entry point for the version manager CLI"""
    parser = argparse.ArgumentParser(description="Smart Steps Version Manager")
    parser.add_argument("--root-dir", "-d", default=os.getcwd(),
                        help="Root directory of the project")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Get version command
    get_parser = subparsers.add_parser("get", help="Get the current version")
    
    # Bump version command
    bump_parser = subparsers.add_parser("bump", help="Bump the version")
    bump_parser.add_argument("type", choices=["major", "minor", "patch"],
                            help="Type of version bump")
    bump_parser.add_argument("--pre-release", "-p", help="Pre-release identifier")
    bump_parser.add_argument("--build", "-b", help="Build metadata")
    bump_parser.add_argument("--message", "-m", help="Commit message")
    
    # Set version command
    set_parser = subparsers.add_parser("set", help="Set the version")
    set_parser.add_argument("version", help="Version string to set")
    set_parser.add_argument("--message", "-m", help="Commit message")
    
    # History command
    history_parser = subparsers.add_parser("history", help="Get version history")
    history_parser.add_argument("--limit", "-l", type=int, default=10,
                               help="Limit number of history entries")
    
    args = parser.parse_args()
    
    # Create version manager
    vm = VersionManager(args.root_dir)
    
    # Execute command
    if args.command == "get":
        version = vm.get_version()
        print(f"Current version: {version}")
    
    elif args.command == "bump":
        version_type = VersionType(args.type)
        new_version = vm.bump_version(
            version_type=version_type,
            pre_release=args.pre_release,
            build=args.build,
            commit_msg=args.message
        )
        print(f"Bumped version to: {new_version}")
    
    elif args.command == "set":
        try:
            new_version = vm.set_version(
                version_str=args.version,
                commit_msg=args.message
            )
            print(f"Set version to: {new_version}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.command == "history":
        history = vm.get_version_history()
        limit = min(args.limit, len(history)) if args.limit > 0 else len(history)
        print(f"Version history (latest {limit} entries):")
        for entry in history[-limit:]:
            print(f"- {entry['version']} ({entry['date']}): {entry['message']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
