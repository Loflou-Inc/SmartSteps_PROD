#!/usr/bin/env python
"""
Automated Update System for Smart Steps AI

This script handles the automated update process for Smart Steps AI:
- Checks for updates in the Git repository
- Performs a backup before updating
- Updates the application code
- Migrates the database if needed
- Restarts the services

Usage:
    python auto_update.py check
    python auto_update.py update [--force] [--no-backup]
    python auto_update.py rollback [--version VERSION]

Author: Smart Steps Team
Date: May 13, 2025
"""

import argparse
import datetime
import json
import logging
import os
import shutil
import signal
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='update.log',
    filemode='a'
)
logger = logging.getLogger('auto_update')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(console)

# Constants
ROOT_DIR = Path(__file__).parent.parent.absolute()
BACKUP_DIR = ROOT_DIR / "backup" / "auto_update"
UPDATE_LOCK_FILE = ROOT_DIR / "update.lock"
VERSION_FILE = ROOT_DIR / "src" / "smart_steps_ai" / "__init__.py"
DOCKER_COMPOSE_FILE = ROOT_DIR / "deployment" / "docker-compose.yml"
ENV_FILE = ROOT_DIR / ".env"
MIGRATION_DIR = ROOT_DIR / "src" / "smart_steps_ai" / "db" / "migrations"
DB_PATH = ROOT_DIR / "data" / "smart_steps.db"

class UpdateManager:
    """Manager for handling application updates."""
    
    def __init__(self, root_dir: Path = ROOT_DIR):
        """
        Initialize the update manager.
        
        Args:
            root_dir: Root directory of the Smart Steps AI system
        """
        self.root_dir = root_dir
        self.backup_dir = BACKUP_DIR
        self.update_lock_file = UPDATE_LOCK_FILE
        
        # Make sure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def check_for_updates(self) -> Dict[str, Any]:
        """
        Check for available updates.
        
        Returns:
            Dictionary with update information
        """
        logger.info("Checking for updates...")
        
        try:
            # Get current version
            current_version = self._get_current_version()
            
            # Fetch latest changes from Git
            self._run_command(["git", "fetch", "origin"])
            
            # Get the latest version from remote
            result = self._run_command(["git", "describe", "--tags", "--abbrev=0", "origin/main"])
            remote_version = result.strip()
            
            # Get commit difference count
            result = self._run_command(["git", "rev-list", "--count", f"HEAD..origin/main"])
            commit_count = int(result.strip())
            
            # Get commit messages
            result = self._run_command(["git", "log", "--pretty=format:%s", f"HEAD..origin/main"])
            commit_messages = result.strip().split("\n") if result.strip() else []
            
            # Check if update is available
            update_available = commit_count > 0
            
            if update_available:
                logger.info(f"Update available: {current_version} -> {remote_version}")
                logger.info(f"New commits: {commit_count}")
                for message in commit_messages:
                    logger.info(f"- {message}")
            else:
                logger.info("No updates available")
            
            return {
                "current_version": current_version,
                "remote_version": remote_version,
                "update_available": update_available,
                "commit_count": commit_count,
                "commit_messages": commit_messages
            }
        except Exception as e:
            logger.error(f"Error checking for updates: {str(e)}")
            return {
                "error": str(e),
                "update_available": False
            }
    
    def update(self, force: bool = False, no_backup: bool = False) -> Dict[str, Any]:
        """
        Update the application.
        
        Args:
            force: Force update even if lock file exists
            no_backup: Skip backup before updating
            
        Returns:
            Dictionary with update results
        """
        # Check if update is in progress
        if self.update_lock_file.exists() and not force:
            logger.error("Update already in progress. Use --force to override.")
            return {
                "success": False,
                "error": "Update already in progress"
            }
        
        # Create lock file
        with open(self.update_lock_file, 'w') as f:
            f.write(f"Update started at {datetime.datetime.now().isoformat()}")
        
        try:
            # Check for updates
            update_info = self.check_for_updates()
            
            if not update_info.get("update_available", False) and not force:
                logger.info("No updates available. Skipping update.")
                self._remove_lock_file()
                return {
                    "success": True,
                    "message": "No updates available"
                }
            
            # Backup before updating
            if not no_backup:
                logger.info("Creating backup before update...")
                backup_result = self._backup()
                if not backup_result.get("success", False):
                    logger.error(f"Backup failed: {backup_result.get('error')}")
                    self._remove_lock_file()
                    return {
                        "success": False,
                        "error": f"Backup failed: {backup_result.get('error')}"
                    }
            
            # Update application code
            logger.info("Updating application code...")
            self._run_command(["git", "pull", "origin", "main"])
            
            # Check if database migration is needed
            migration_needed = self._check_migration_needed()
            
            # Stop services
            logger.info("Stopping services...")
            if self._is_docker_deployment():
                self._run_command(["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "down"])
            else:
                self._stop_services()
            
            # Perform database migration if needed
            if migration_needed:
                logger.info("Performing database migration...")
                migration_result = self._migrate_database()
                if not migration_result.get("success", False):
                    logger.error(f"Database migration failed: {migration_result.get('error')}")
                    self._restore_backup(backup_result.get("backup_dir"))
                    self._remove_lock_file()
                    return {
                        "success": False,
                        "error": f"Database migration failed: {migration_result.get('error')}"
                    }
            
            # Rebuild if needed
            rebuild_needed = self._check_rebuild_needed()
            if rebuild_needed:
                logger.info("Rebuilding application...")
                if self._is_docker_deployment():
                    self._run_command(["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "build"])
                else:
                    self._run_command([sys.executable, "-m", "pip", "install", "-e", "."])
            
            # Start services
            logger.info("Starting services...")
            if self._is_docker_deployment():
                self._run_command(["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "up", "-d"])
            else:
                self._start_services()
            
            # Update successful
            logger.info("Update completed successfully!")
            self._remove_lock_file()
            
            return {
                "success": True,
                "message": "Update completed successfully",
                "backup": backup_result if not no_backup else None,
                "migration_performed": migration_needed,
                "rebuild_performed": rebuild_needed
            }
        except Exception as e:
            logger.error(f"Error during update: {str(e)}")
            self._remove_lock_file()
            return {
                "success": False,
                "error": str(e)
            }
    
    def rollback(self, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Rollback to a previous version.
        
        Args:
            version: Version to rollback to. If None, rollback to the latest backup.
            
        Returns:
            Dictionary with rollback results
        """
        # Check if update is in progress
        if self.update_lock_file.exists():
            logger.error("Update in progress. Cannot rollback.")
            return {
                "success": False,
                "error": "Update in progress"
            }
        
        # Create lock file
        with open(self.update_lock_file, 'w') as f:
            f.write(f"Rollback started at {datetime.datetime.now().isoformat()}")
        
        try:
            # Find backup to restore
            if version:
                # Find backup for the specified version
                backup_dir = self._find_backup_by_version(version)
                if not backup_dir:
                    logger.error(f"No backup found for version {version}")
                    self._remove_lock_file()
                    return {
                        "success": False,
                        "error": f"No backup found for version {version}"
                    }
            else:
                # Find the latest backup
                backup_dir = self._find_latest_backup()
                if not backup_dir:
                    logger.error("No backups found")
                    self._remove_lock_file()
                    return {
                        "success": False,
                        "error": "No backups found"
                    }
            
            # Stop services
            logger.info("Stopping services...")
            if self._is_docker_deployment():
                self._run_command(["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "down"])
            else:
                self._stop_services()
            
            # Restore backup
            logger.info(f"Restoring backup from {backup_dir}...")
            restore_result = self._restore_backup(backup_dir)
            if not restore_result.get("success", False):
                logger.error(f"Restore failed: {restore_result.get('error')}")
                self._remove_lock_file()
                return {
                    "success": False,
                    "error": f"Restore failed: {restore_result.get('error')}"
                }
            
            # Start services
            logger.info("Starting services...")
            if self._is_docker_deployment():
                self._run_command(["docker-compose", "-f", str(DOCKER_COMPOSE_FILE), "up", "-d"])
            else:
                self._start_services()
            
            # Rollback successful
            logger.info("Rollback completed successfully!")
            self._remove_lock_file()
            
            return {
                "success": True,
                "message": "Rollback completed successfully",
                "restored_backup": str(backup_dir)
            }
        except Exception as e:
            logger.error(f"Error during rollback: {str(e)}")
            self._remove_lock_file()
            return {
                "success": False,
                "error": str(e)
            }
    
    def _backup(self) -> Dict[str, Any]:
        """
        Create a backup of the application.
        
        Returns:
            Dictionary with backup results
        """
        try:
            # Create backup directory with timestamp and version
            current_version = self._get_current_version()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.backup_dir / f"{current_version}_{timestamp}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup database
            if DB_PATH.exists():
                db_backup_dir = backup_dir / "db"
                os.makedirs(db_backup_dir, exist_ok=True)
                
                # Create a connection to the database
                conn = sqlite3.connect(DB_PATH)
                
                # Create the backup file path
                backup_file = db_backup_dir / DB_PATH.name
                
                # Create a backup connection
                backup_conn = sqlite3.connect(backup_file)
                
                # Backup the database
                conn.backup(backup_conn)
                
                # Close connections
                backup_conn.close()
                conn.close()
            
            # Backup code snapshot (git archive)
            code_backup_file = backup_dir / "code_snapshot.tar.gz"
            self._run_command(["git", "archive", "--format=tar.gz", "-o", str(code_backup_file), "HEAD"])
            
            # Backup configuration
            config_backup_dir = backup_dir / "config"
            os.makedirs(config_backup_dir, exist_ok=True)
            
            # Backup .env file
            if ENV_FILE.exists():
                shutil.copy2(ENV_FILE, config_backup_dir / ".env")
            
            # Backup other important configuration files
            for config_file in (ROOT_DIR / "config").glob("*.yaml"):
                shutil.copy2(config_file, config_backup_dir / config_file.name)
            
            # Create backup info file
            backup_info = {
                "version": current_version,
                "timestamp": timestamp,
                "git_commit": self._run_command(["git", "rev-parse", "HEAD"]).strip(),
                "backup_items": [
                    "database",
                    "code_snapshot",
                    "configuration"
                ]
            }
            
            with open(backup_dir / "backup_info.json", 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            logger.info(f"Backup created at {backup_dir}")
            
            return {
                "success": True,
                "backup_dir": str(backup_dir),
                "version": current_version,
                "timestamp": timestamp
            }
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _restore_backup(self, backup_dir: Union[str, Path]) -> Dict[str, Any]:
        """
        Restore a backup.
        
        Args:
            backup_dir: Path to the backup directory
            
        Returns:
            Dictionary with restore results
        """
        backup_dir = Path(backup_dir)
        
        try:
            # Check if backup directory exists
            if not backup_dir.exists():
                return {
                    "success": False,
                    "error": f"Backup directory not found: {backup_dir}"
                }
            
            # Load backup info
            backup_info_file = backup_dir / "backup_info.json"
            if not backup_info_file.exists():
                return {
                    "success": False,
                    "error": f"Backup info file not found: {backup_info_file}"
                }
            
            with open(backup_info_file, 'r') as f:
                backup_info = json.load(f)
            
            # Restore database
            db_backup_file = backup_dir / "db" / DB_PATH.name
            if db_backup_file.exists():
                # Make sure the DB directory exists
                os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
                
                # Stop any connections to the database
                conn = None
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.close()
                except:
                    pass
                finally:
                    if conn:
                        conn.close()
                
                # Copy the backup database to the original location
                shutil.copy2(db_backup_file, DB_PATH)
            
            # Restore code snapshot
            code_backup_file = backup_dir / "code_snapshot.tar.gz"
            if code_backup_file.exists():
                # Extract the code snapshot
                self._run_command(["git", "checkout", backup_info.get("git_commit")])
            
            # Restore configuration
            config_backup_dir = backup_dir / "config"
            if config_backup_dir.exists():
                # Restore .env file
                env_backup_file = config_backup_dir / ".env"
                if env_backup_file.exists():
                    shutil.copy2(env_backup_file, ENV_FILE)
                
                # Restore other important configuration files
                config_dir = ROOT_DIR / "config"
                os.makedirs(config_dir, exist_ok=True)
                
                for config_file in config_backup_dir.glob("*.yaml"):
                    shutil.copy2(config_file, config_dir / config_file.name)
            
            logger.info(f"Backup restored from {backup_dir}")
            
            return {
                "success": True,
                "backup_dir": str(backup_dir),
                "version": backup_info.get("version"),
                "timestamp": backup_info.get("timestamp")
            }
        except Exception as e:
            logger.error(f"Error restoring backup: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _find_backup_by_version(self, version: str) -> Optional[Path]:
        """
        Find a backup for the specified version.
        
        Args:
            version: Version to find
            
        Returns:
            Path to the backup directory, or None if not found
        """
        try:
            # Look for backup directories that start with the version
            version_backups = list(self.backup_dir.glob(f"{version}_*"))
            
            if not version_backups:
                return None
            
            # Return the latest backup for the version
            return sorted(version_backups, key=lambda p: p.name.split('_')[1])[-1]
        except Exception as e:
            logger.error(f"Error finding backup for version {version}: {str(e)}")
            return None
    
    def _find_latest_backup(self) -> Optional[Path]:
        """
        Find the latest backup.
        
        Returns:
            Path to the latest backup directory, or None if not found
        """
        try:
            # Get all backup directories
            backups = list(self.backup_dir.glob("*_*"))
            
            if not backups:
                return None
            
            # Return the latest backup (sorted by timestamp in directory name)
            return sorted(backups, key=lambda p: p.name.split('_')[1])[-1]
        except Exception as e:
            logger.error(f"Error finding latest backup: {str(e)}")
            return None
    
    def _check_migration_needed(self) -> bool:
        """
        Check if database migration is needed.
        
        Returns:
            True if migration is needed, False otherwise
        """
        # This is a simplified check. In a real implementation, 
        # you would have a more sophisticated way to check if migration is needed.
        return MIGRATION_DIR.exists() and len(list(MIGRATION_DIR.glob("*.py"))) > 0
    
    def _migrate_database(self) -> Dict[str, Any]:
        """
        Migrate the database.
        
        Returns:
            Dictionary with migration results
        """
        try:
            # This is a simplified migration. In a real implementation,
            # you would have a more sophisticated migration system.
            
            # For now, we'll just run a hypothetical migration script
            if self._is_docker_deployment():
                self._run_command([
                    "docker-compose", 
                    "-f", str(DOCKER_COMPOSE_FILE), 
                    "run", 
                    "--rm", 
                    "api", 
                    "python", 
                    "-m", 
                    "src.smart_steps_ai.db.migrate"
                ])
            else:
                self._run_command([
                    sys.executable, 
                    "-m", 
                    "src.smart_steps_ai.db.migrate"
                ])
            
            return {
                "success": True,
                "message": "Database migration completed successfully"
            }
        except Exception as e:
            logger.error(f"Error migrating database: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _check_rebuild_needed(self) -> bool:
        """
        Check if the application needs to be rebuilt.
        
        Returns:
            True if rebuild is needed, False otherwise
        """
        # Check if setup.py has changed
        try:
            result = self._run_command(["git", "diff", "--name-only", "HEAD@{1}", "HEAD", "setup.py"])
            if result.strip():
                return True
            
            # Check if requirements.txt has changed
            result = self._run_command(["git", "diff", "--name-only", "HEAD@{1}", "HEAD", "requirements.txt"])
            if result.strip():
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking if rebuild is needed: {str(e)}")
            return True  # Rebuild to be safe
    
    def _is_docker_deployment(self) -> bool:
        """
        Check if this is a Docker deployment.
        
        Returns:
            True if this is a Docker deployment, False otherwise
        """
        return DOCKER_COMPOSE_FILE.exists()
    
    def _stop_services(self):
        """Stop the services."""
        # Find PID files
        pid_files = [
            ROOT_DIR / "logs" / "api.pid",
            ROOT_DIR / "logs" / "monitoring.pid"
        ]
        
        for pid_file in pid_files:
            if pid_file.exists():
                try:
                    with open(pid_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    # Send SIGTERM to the process
                    os.kill(pid, signal.SIGTERM)
                    
                    # Wait for the process to terminate
                    for _ in range(10):
                        try:
                            os.kill(pid, 0)  # Check if process exists
                            time.sleep(1)
                        except OSError:
                            break
                    
                    # If process still exists, force kill
                    try:
                        os.kill(pid, 0)
                        os.kill(pid, signal.SIGKILL)
                    except OSError:
                        pass
                    
                    # Remove PID file
                    pid_file.unlink()
                except Exception as e:
                    logger.error(f"Error stopping process from PID file {pid_file}: {str(e)}")
    
    def _start_services(self):
        """Start the services."""
        # Start API server
        self._run_command([
            sys.executable,
            str(ROOT_DIR / "run_api_server.bat")
        ], shell=True, background=True)
        
        # Start monitoring system
        self._run_command([
            sys.executable,
            str(ROOT_DIR / "deployment" / "monitoring_system.py"),
            "start"
        ], shell=True, background=True)
    
    def _get_current_version(self) -> str:
        """
        Get the current version from the package __init__.py file.
        
        Returns:
            Current version string
        """
        if not VERSION_FILE.exists():
            raise ValueError(f"Version file not found: {VERSION_FILE}")
        
        with open(VERSION_FILE, 'r') as f:
            content = f.read()
        
        import re
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if not match:
            raise ValueError("Version not found in __init__.py")
        
        return match.group(1)
    
    def _run_command(self, command: List[str], shell: bool = False, background: bool = False) -> str:
        """
        Run a shell command.
        
        Args:
            command: Command to run
            shell: Whether to run through shell
            background: Whether to run in background
            
        Returns:
            Command output
        """
        logger.debug(f"Running command: {' '.join(command)}")
        
        if background:
            if shell:
                subprocess.Popen(' '.join(command), shell=True)
            else:
                subprocess.Popen(command)
            return ""
        
        result = subprocess.run(
            command if not shell else ' '.join(command),
            shell=shell,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Command failed: {result.stderr}")
            raise ValueError(f"Command failed: {result.stderr}")
        
        return result.stdout
    
    def _remove_lock_file(self):
        """Remove the update lock file."""
        if self.update_lock_file.exists():
            self.update_lock_file.unlink()

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Smart Steps AI Automated Update System")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Check command
    subparsers.add_parser("check", help="Check for updates")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update the application")
    update_parser.add_argument("--force", action="store_true", help="Force update even if lock file exists")
    update_parser.add_argument("--no-backup", action="store_true", help="Skip backup before updating")
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback to a previous version")
    rollback_parser.add_argument("--version", help="Version to rollback to")
    
    args = parser.parse_args()
    
    update_manager = UpdateManager()
    
    if args.command == "check":
        result = update_manager.check_for_updates()
        
        if result.get("update_available", False):
            print("Update available!")
            print(f"Current version: {result.get('current_version')}")
            print(f"Remote version: {result.get('remote_version')}")
            print(f"New commits: {result.get('commit_count')}")
            print("Commit messages:")
            for message in result.get("commit_messages", []):
                print(f"- {message}")
        else:
            print("No updates available")
            if "error" in result:
                print(f"Error: {result['error']}")
    
    elif args.command == "update":
        result = update_manager.update(args.force, args.no_backup)
        
        if result.get("success", False):
            print(f"Update successful: {result.get('message')}")
        else:
            print(f"Update failed: {result.get('error')}")
    
    elif args.command == "rollback":
        result = update_manager.rollback(args.version)
        
        if result.get("success", False):
            print(f"Rollback successful: {result.get('message')}")
            print(f"Restored from: {result.get('restored_backup')}")
        else:
            print(f"Rollback failed: {result.get('error')}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
