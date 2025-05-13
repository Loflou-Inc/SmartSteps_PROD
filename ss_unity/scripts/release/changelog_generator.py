#!/usr/bin/env python3
"""
Smart Steps AI Professional Persona Module - Changelog Generator

This script generates a changelog from Git commit history, 
categorizes changes, and formats them according to Keep a Changelog format.
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Constants
CHANGELOG_FILE = "CHANGELOG.md"
CATEGORIES = [
    "Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"
]
COMMIT_CATEGORIES = {
    "feat": "Added",
    "feature": "Added",
    "add": "Added",
    "change": "Changed",
    "refactor": "Changed",
    "perf": "Changed",
    "deprecate": "Deprecated",
    "remove": "Removed",
    "fix": "Fixed",
    "security": "Security",
    "docs": None,  # Skip documentation changes
    "style": None,  # Skip style changes
    "test": None,  # Skip test changes
    "chore": None,  # Skip chores
}


class ChangelogGenerator:
    """Generates a changelog from Git commit history"""
    
    def __init__(self, repo_dir: str, changelog_file: Optional[str] = None):
        """Initialize the changelog generator
        
        Args:
            repo_dir: Root directory of the Git repository
            changelog_file: Path to the changelog file, defaults to CHANGELOG.md in repo_dir
        """
        self.repo_dir = repo_dir
        self.changelog_file = changelog_file or os.path.join(repo_dir, CHANGELOG_FILE)
    
    def _run_git_command(self, args: List[str]) -> str:
        """Run a Git command and return its output
        
        Args:
            args: Git command arguments
            
        Returns:
            Command output
            
        Raises:
            RuntimeError: If the Git command fails
        """
        cmd = ["git"] + args
        try:
            return subprocess.check_output(cmd, cwd=self.repo_dir, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {e}")
    
    def _get_commit_messages(self, start_ref: Optional[str], end_ref: str = "HEAD") -> List[str]:
        """Get commit messages between two Git references
        
        Args:
            start_ref: Starting Git reference
            end_ref: Ending Git reference
            
        Returns:
            List of commit messages
        """
        if start_ref:
            output = self._run_git_command(["log", f"{start_ref}..{end_ref}", "--pretty=format:%s"])
        else:
            output = self._run_git_command(["log", "--pretty=format:%s"])
        
        return output.splitlines()
    
    def _get_version_tags(self) -> List[Tuple[str, str]]:
        """Get version tags from Git
        
        Returns:
            List of (tag_name, commit_hash) tuples
        """
        try:
            output = self._run_git_command(["tag", "-l", "v*", "--sort=-v:refname"])
            tags = output.splitlines()
            
            result = []
            for tag in tags:
                if tag.startswith('v'):
                    commit_hash = self._run_git_command(["rev-list", "-n", "1", tag]).strip()
                    result.append((tag, commit_hash))
            
            return result
        except RuntimeError:
            return []
    
    def _get_latest_tag(self) -> Optional[Tuple[str, str]]:
        """Get the latest version tag
        
        Returns:
            Tuple of (tag_name, commit_hash) for the latest tag, or None if no tags
        """
        tags = self._get_version_tags()
        return tags[0] if tags else None
    
    def _categorize_commit(self, commit: str) -> Tuple[Optional[str], str]:
        """Categorize a commit message
        
        Args:
            commit: Commit message
            
        Returns:
            Tuple of (category, message)
        """
        # Check conventional commit format: type(scope): message
        conv_pattern = r"^(\w+)(?:\([\w-]+\))?: (.+)$"
        match = re.match(conv_pattern, commit)
        
        if match:
            commit_type = match.group(1).lower()
            message = match.group(2)
            category = COMMIT_CATEGORIES.get(commit_type)
            return category, message
        
        # Check for manual category: [CATEGORY] message
        manual_pattern = r"^\[(\w+)\] (.+)$"
        match = re.match(manual_pattern, commit)
        
        if match:
            category_name = match.group(1).capitalize()
            message = match.group(2)
            if category_name in CATEGORIES:
                return category_name, message
        
        # No category found, try to infer from keywords
        for keyword, category in COMMIT_CATEGORIES.items():
            if commit.lower().startswith(f"{keyword}:") or commit.lower().startswith(f"{keyword} "):
                message = commit[len(keyword):].strip()
                if message.startswith(":"):
                    message = message[1:].strip()
                return category, message
        
        # Default to Changed category
        return "Changed", commit
    
    def generate_changelog_from_commits(
        self, version: str, start_ref: Optional[str] = None, end_ref: str = "HEAD"
    ) -> str:
        """Generate changelog content from Git commit history
        
        Args:
            version: Version to use in the changelog
            start_ref: Starting Git reference
            end_ref: Ending Git reference
            
        Returns:
            Generated changelog content
        """
        commit_messages = self._get_commit_messages(start_ref, end_ref)
        
        # Categorize commits
        categorized_commits: Dict[str, List[str]] = {cat: [] for cat in CATEGORIES}
        
        for commit in commit_messages:
            category, message = self._categorize_commit(commit)
            if category:
                categorized_commits[category].append(message)
        
        # Generate changelog content
        today = datetime.now().strftime("%Y-%m-%d")
        content = f"## [{version}] - {today}\n\n"
        
        for category in CATEGORIES:
            commits = categorized_commits[category]
            if commits:
                content += f"### {category}\n\n"
                for commit in commits:
                    content += f"- {commit}\n"
                content += "\n"
        
        return content
    
    def update_changelog(self, version: str, start_ref: Optional[str] = None, 
                        end_ref: str = "HEAD", dry_run: bool = False) -> str:
        """Update changelog file with new version changes
        
        Args:
            version: Version to use in the changelog
            start_ref: Starting Git reference
            end_ref: Ending Git reference
            dry_run: If True, don't write to the changelog file
            
        Returns:
            Generated changelog content
        """
        # Generate changelog for the new version
        new_content = self.generate_changelog_from_commits(version, start_ref, end_ref)
        
        # Read the existing changelog
        existing_content = ""
        try:
            if os.path.exists(self.changelog_file):
                with open(self.changelog_file, 'r') as f:
                    existing_content = f.read()
        except IOError as e:
            print(f"Warning: Could not read changelog file: {e}")
        
        # Initialize the changelog if it doesn't exist or is empty
        if not existing_content:
            today = datetime.now().strftime("%Y-%m-%d")
            existing_content = (
                "# Changelog\n\n"
                "All notable changes to this project will be documented in this file.\n\n"
                "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),\n"
                "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).\n\n"
            )
        
        # Insert the new content after the header
        header_pattern = r"(# Changelog.*?adheres to \[Semantic Versioning\].*?\n\n)"
        match = re.search(header_pattern, existing_content, re.DOTALL)
        
        if match:
            updated_content = re.sub(
                header_pattern,
                f"{match.group(1)}{new_content}",
                existing_content,
                flags=re.DOTALL
            )
        else:
            # If no header is found, just prepend the new content
            updated_content = f"{existing_content}\n{new_content}"
        
        # Write the updated content to the changelog file
        if not dry_run:
            try:
                with open(self.changelog_file, 'w') as f:
                    f.write(updated_content)
                print(f"Updated changelog at {self.changelog_file}")
            except IOError as e:
                print(f"Error writing changelog file: {e}")
                sys.exit(1)
        
        return new_content
    
    def generate_changelog_between_versions(
        self, start_version: Optional[str] = None, end_version: Optional[str] = None
    ) -> str:
        """Generate changelog between two versions
        
        Args:
            start_version: Starting version tag
            end_version: Ending version tag
            
        Returns:
            Generated changelog content
        """
        # Get all version tags
        tags = self._get_version_tags()
        if not tags:
            print("No version tags found")
            return ""
        
        # Find the start and end tag indices
        start_idx = None
        end_idx = None
        
        if start_version:
            start_version_tag = f"v{start_version}" if not start_version.startswith('v') else start_version
            for i, (tag, _) in enumerate(tags):
                if tag == start_version_tag:
                    start_idx = i
                    break
            
            if start_idx is None:
                print(f"Warning: Start version {start_version} not found")
                start_idx = len(tags) - 1  # Use the oldest tag
        else:
            start_idx = len(tags) - 1  # Use the oldest tag
        
        if end_version:
            end_version_tag = f"v{end_version}" if not end_version.startswith('v') else end_version
            for i, (tag, _) in enumerate(tags):
                if tag == end_version_tag:
                    end_idx = i
                    break
            
            if end_idx is None:
                print(f"Warning: End version {end_version} not found")
                end_idx = 0  # Use the latest tag
        else:
            end_idx = 0  # Use the latest tag
        
        # Generate changelog content for each version
        content = ""
        for i in range(end_idx, start_idx + 1):
            version_tag, _ = tags[i]
            version = version_tag[1:]  # Remove 'v' prefix
            
            if i < len(tags) - 1:
                prev_tag, _ = tags[i + 1]
                version_content = self.generate_changelog_from_commits(version, prev_tag, version_tag)
            else:
                # No previous tag, use all commits up to this tag
                version_content = self.generate_changelog_from_commits(version, None, version_tag)
            
            content += version_content + "\n"
        
        return content


def main():
    """Main entry point for the changelog generator CLI"""
    parser = argparse.ArgumentParser(description="Smart Steps Changelog Generator")
    parser.add_argument("--repo-dir", "-d", default=os.getcwd(),
                        help="Root directory of the Git repository")
    parser.add_argument("--output", "-o", help="Output file path")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Update changelog command
    update_parser = subparsers.add_parser("update", help="Update changelog with new version")
    update_parser.add_argument("version", help="Version to use in the changelog")
    update_parser.add_argument("--start", help="Starting Git reference")
    update_parser.add_argument("--end", default="HEAD", help="Ending Git reference")
    update_parser.add_argument("--dry-run", action="store_true",
                              help="Don't write to the changelog file")
    
    # Generate changelog command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate changelog between versions"
    )
    generate_parser.add_argument("--start", help="Starting version tag")
    generate_parser.add_argument("--end", help="Ending version tag")
    
    args = parser.parse_args()
    
    # Create changelog generator
    changelog_file = args.output
    generator = ChangelogGenerator(args.repo_dir, changelog_file)
    
    # Execute command
    if args.command == "update":
        content = generator.update_changelog(
            version=args.version,
            start_ref=args.start,
            end_ref=args.end,
            dry_run=args.dry_run
        )
        if args.dry_run:
            print(content)
    
    elif args.command == "generate":
        content = generator.generate_changelog_between_versions(
            start_version=args.start,
            end_version=args.end
        )
        
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    f.write(content)
                print(f"Generated changelog at {args.output}")
            except IOError as e:
                print(f"Error writing changelog file: {e}")
                sys.exit(1)
        else:
            print(content)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
