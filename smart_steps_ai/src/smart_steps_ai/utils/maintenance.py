"""
Smart Steps AI System Maintenance Module

This module provides utilities for system maintenance and health checks:
- Log rotation and cleanup
- Database backups and optimization
- Cache management
- System health checks
- Performance monitoring and optimization

Usage:
    from smart_steps_ai.utils.maintenance import perform_maintenance, check_system_health

Author: Smart Steps Team
Date: May 13, 2025
"""

import datetime
import glob
import json
import logging
import os
import shutil
import sqlite3
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

logger = logging.getLogger(__name__)

class MaintenanceManager:
    """Manager for system maintenance tasks."""
    
    def __init__(self, root_dir: Union[str, Path], config: Optional[Dict[str, Any]] = None):
        """
        Initialize the maintenance manager.
        
        Args:
            root_dir: Root directory of the Smart Steps AI system
            config: Optional configuration dictionary
        """
        self.root_dir = Path(root_dir)
        self.config = config or {}
        
        # Set default paths
        self.log_dir = self.root_dir / "logs"
        self.data_dir = self.root_dir / "data"
        self.backup_dir = self.root_dir / "backup"
        self.temp_dir = self.root_dir / "temp"
        
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure that required directories exist."""
        for directory in [self.log_dir, self.data_dir, self.backup_dir, self.temp_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def perform_maintenance(self, tasks: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform maintenance tasks.
        
        Args:
            tasks: List of task names to perform. If None, perform all tasks.
            
        Returns:
            Dictionary with results of maintenance tasks
        """
        all_tasks = {
            "rotate_logs": self.rotate_logs,
            "backup_database": self.backup_database,
            "optimize_database": self.optimize_database,
            "clear_cache": self.clear_cache,
            "clean_temp_files": self.clean_temp_files,
            "check_disk_space": self.check_disk_space,
        }
        
        if tasks is None:
            tasks = list(all_tasks.keys())
        
        results = {}
        for task in tasks:
            if task in all_tasks:
                logger.info(f"Performing maintenance task: {task}")
                try:
                    result = all_tasks[task]()
                    results[task] = {
                        "status": "success",
                        "details": result
                    }
                except Exception as e:
                    logger.error(f"Error performing maintenance task {task}: {str(e)}")
                    logger.error(traceback.format_exc())
                    results[task] = {
                        "status": "error",
                        "error": str(e)
                    }
            else:
                results[task] = {
                    "status": "error",
                    "error": f"Unknown task: {task}"
                }
        
        return results
    
    def rotate_logs(self) -> Dict[str, Any]:
        """
        Rotate log files.
        
        Returns:
            Dictionary with results of log rotation
        """
        # Get log retention settings
        retention_days = self.config.get("log_retention_days", 30)
        max_log_size = self.config.get("max_log_size_mb", 100) * 1024 * 1024  # Convert to bytes
        
        results = {
            "rotated_logs": [],
            "deleted_logs": []
        }
        
        # Calculate cutoff date for old logs
        cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
        
        # Process each log file
        for log_file in self.log_dir.glob("*.log"):
            # Check if file is a symlink (avoid rotating symlinks)
            if log_file.is_symlink():
                continue
            
            # Check if file is too old
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                results["deleted_logs"].append(str(log_file))
                continue
            
            # Check if file is too large
            if log_file.stat().st_size > max_log_size:
                # Create rotated log filename with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                rotated_file = log_file.with_name(f"{log_file.stem}_{timestamp}.log")
                
                # Try to rotate the log
                try:
                    # Create a new empty file, then rename the old file
                    open(log_file, 'a').close()
                    shutil.copy2(log_file, rotated_file)
                    with open(log_file, 'w') as f:
                        f.write(f"Log rotated at {datetime.datetime.now().isoformat()}\n")
                    
                    results["rotated_logs"].append(str(log_file))
                except Exception as e:
                    logger.error(f"Error rotating log file {log_file}: {str(e)}")
        
        return results
    
    def backup_database(self) -> Dict[str, Any]:
        """
        Backup database files.
        
        Returns:
            Dictionary with results of database backup
        """
        # Find database files
        database_files = list(self.data_dir.glob("*.db")) + list(self.data_dir.glob("*.sqlite"))
        
        # Create backup directory with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.backup_dir / f"db_backup_{timestamp}"
        os.makedirs(backup_dir, exist_ok=True)
        
        results = {
            "backed_up_files": [],
            "backup_dir": str(backup_dir),
            "timestamp": timestamp
        }
        
        # Backup each database file
        for db_file in database_files:
            try:
                # Create a connection to the database
                conn = sqlite3.connect(db_file)
                
                # Create the backup file path
                backup_file = backup_dir / db_file.name
                
                # Create a backup connection
                backup_conn = sqlite3.connect(backup_file)
                
                # Backup the database
                conn.backup(backup_conn)
                
                # Close connections
                backup_conn.close()
                conn.close()
                
                results["backed_up_files"].append({
                    "source": str(db_file),
                    "destination": str(backup_file),
                    "size": os.path.getsize(backup_file)
                })
            except Exception as e:
                logger.error(f"Error backing up database {db_file}: {str(e)}")
        
        # Cleanup old backups
        retention_days = self.config.get("backup_retention_days", 30)
        cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
        
        deleted_backups = []
        for backup_dir in self.backup_dir.glob("db_backup_*"):
            if backup_dir.is_dir() and backup_dir.stat().st_mtime < cutoff_time:
                try:
                    shutil.rmtree(backup_dir)
                    deleted_backups.append(str(backup_dir))
                except Exception as e:
                    logger.error(f"Error deleting old backup {backup_dir}: {str(e)}")
        
        results["deleted_old_backups"] = deleted_backups
        
        return results
    
    def optimize_database(self) -> Dict[str, Any]:
        """
        Optimize database files (vacuum and analyze).
        
        Returns:
            Dictionary with results of database optimization
        """
        # Find database files
        database_files = list(self.data_dir.glob("*.db")) + list(self.data_dir.glob("*.sqlite"))
        
        results = {
            "optimized_files": []
        }
        
        # Optimize each database file
        for db_file in database_files:
            try:
                # Get file size before optimization
                size_before = os.path.getsize(db_file)
                
                # Create a connection to the database
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Run VACUUM to defragment the database
                cursor.execute("VACUUM")
                
                # Run ANALYZE to update statistics
                cursor.execute("ANALYZE")
                
                # Close connection
                conn.close()
                
                # Get file size after optimization
                size_after = os.path.getsize(db_file)
                
                results["optimized_files"].append({
                    "file": str(db_file),
                    "size_before": size_before,
                    "size_after": size_after,
                    "bytes_saved": size_before - size_after
                })
            except Exception as e:
                logger.error(f"Error optimizing database {db_file}: {str(e)}")
        
        return results
    
    def clear_cache(self) -> Dict[str, Any]:
        """
        Clear cached data.
        
        Returns:
            Dictionary with results of cache clearing
        """
        # Find cache directories
        cache_dirs = [
            self.root_dir / "cache",
            self.root_dir / ".cache",
            self.root_dir / "src" / "smart_steps_ai" / "cache"
        ]
        
        results = {
            "cleared_cache_dirs": [],
            "bytes_freed": 0
        }
        
        # Clear each cache directory
        for cache_dir in cache_dirs:
            if cache_dir.exists() and cache_dir.is_dir():
                try:
                    # Calculate size before clearing
                    size_before = sum(f.stat().st_size for f in cache_dir.glob("**/*") if f.is_file())
                    
                    # Delete all files in the cache directory
                    for cache_file in cache_dir.glob("**/*"):
                        if cache_file.is_file():
                            cache_file.unlink()
                    
                    results["cleared_cache_dirs"].append(str(cache_dir))
                    results["bytes_freed"] += size_before
                except Exception as e:
                    logger.error(f"Error clearing cache directory {cache_dir}: {str(e)}")
        
        # Clear API cache if enabled
        api_cache_file = self.data_dir / "api_cache.db"
        if api_cache_file.exists():
            try:
                # Calculate size before clearing
                size_before = os.path.getsize(api_cache_file)
                
                # Open the database and truncate the cache table
                conn = sqlite3.connect(api_cache_file)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cache")
                conn.commit()
                conn.close()
                
                # Calculate size after clearing
                size_after = os.path.getsize(api_cache_file)
                
                results["cleared_cache_dirs"].append(str(api_cache_file))
                results["bytes_freed"] += (size_before - size_after)
            except Exception as e:
                logger.error(f"Error clearing API cache {api_cache_file}: {str(e)}")
        
        # Convert bytes freed to human-readable format
        bytes_freed = results["bytes_freed"]
        if bytes_freed > 1024 * 1024 * 1024:
            results["human_readable_freed"] = f"{bytes_freed / (1024 * 1024 * 1024):.2f} GB"
        elif bytes_freed > 1024 * 1024:
            results["human_readable_freed"] = f"{bytes_freed / (1024 * 1024):.2f} MB"
        elif bytes_freed > 1024:
            results["human_readable_freed"] = f"{bytes_freed / 1024:.2f} KB"
        else:
            results["human_readable_freed"] = f"{bytes_freed} bytes"
        
        return results
    
    def clean_temp_files(self) -> Dict[str, Any]:
        """
        Clean temporary files.
        
        Returns:
            Dictionary with results of temp file cleaning
        """
        # Identify temporary directories
        temp_dirs = [
            self.temp_dir,
            self.root_dir / "tmp",
            Path(os.environ.get("TEMP", "/tmp"))
        ]
        
        results = {
            "cleaned_dirs": [],
            "deleted_files": 0,
            "bytes_freed": 0
        }
        
        # Get temp file retention settings
        retention_hours = self.config.get("temp_retention_hours", 24)
        
        # Calculate cutoff time
        cutoff_time = time.time() - (retention_hours * 60 * 60)
        
        # Clean each temp directory
        for temp_dir in temp_dirs:
            if temp_dir.exists() and temp_dir.is_dir():
                try:
                    # Find temp files with our project prefix
                    project_temp_files = list(temp_dir.glob("smart_steps_*"))
                    
                    deleted_count = 0
                    bytes_freed = 0
                    
                    for temp_file in project_temp_files:
                        # Check if file is old enough to delete
                        if temp_file.stat().st_mtime < cutoff_time:
                            # Get file size
                            if temp_file.is_file():
                                bytes_freed += temp_file.stat().st_size
                            
                            # Delete the file or directory
                            if temp_file.is_dir():
                                shutil.rmtree(temp_file)
                            else:
                                temp_file.unlink()
                            
                            deleted_count += 1
                    
                    if deleted_count > 0:
                        results["cleaned_dirs"].append({
                            "dir": str(temp_dir),
                            "deleted_files": deleted_count,
                            "bytes_freed": bytes_freed
                        })
                        
                        results["deleted_files"] += deleted_count
                        results["bytes_freed"] += bytes_freed
                except Exception as e:
                    logger.error(f"Error cleaning temp directory {temp_dir}: {str(e)}")
        
        # Convert bytes freed to human-readable format
        bytes_freed = results["bytes_freed"]
        if bytes_freed > 1024 * 1024 * 1024:
            results["human_readable_freed"] = f"{bytes_freed / (1024 * 1024 * 1024):.2f} GB"
        elif bytes_freed > 1024 * 1024:
            results["human_readable_freed"] = f"{bytes_freed / (1024 * 1024):.2f} MB"
        elif bytes_freed > 1024:
            results["human_readable_freed"] = f"{bytes_freed / 1024:.2f} KB"
        else:
            results["human_readable_freed"] = f"{bytes_freed} bytes"
        
        return results
    
    def check_disk_space(self) -> Dict[str, Any]:
        """
        Check available disk space.
        
        Returns:
            Dictionary with disk space information
        """
        import shutil
        
        results = {
            "disks": []
        }
        
        # Check each important directory
        dirs_to_check = [
            self.root_dir,
            self.data_dir,
            self.log_dir,
            self.backup_dir
        ]
        
        # Get warning threshold
        warning_threshold = self.config.get("disk_space_warning_percent", 10)
        
        for directory in dirs_to_check:
            try:
                # Get disk usage
                usage = shutil.disk_usage(directory)
                
                # Calculate percentage free
                percent_free = (usage.free / usage.total) * 100
                
                # Check if space is low
                is_low = percent_free < warning_threshold
                
                # Add to results
                results["disks"].append({
                    "path": str(directory),
                    "total_bytes": usage.total,
                    "used_bytes": usage.used,
                    "free_bytes": usage.free,
                    "percent_used": ((usage.total - usage.free) / usage.total) * 100,
                    "percent_free": percent_free,
                    "is_low": is_low,
                    "total_human": self._bytes_to_human(usage.total),
                    "used_human": self._bytes_to_human(usage.used),
                    "free_human": self._bytes_to_human(usage.free)
                })
                
                # Log warning if space is low
                if is_low:
                    logger.warning(
                        f"Low disk space on {directory}: {percent_free:.1f}% free "
                        f"({self._bytes_to_human(usage.free)} / {self._bytes_to_human(usage.total)})"
                    )
            except Exception as e:
                logger.error(f"Error checking disk space for {directory}: {str(e)}")
        
        return results
    
    def _bytes_to_human(self, num_bytes: int) -> str:
        """
        Convert bytes to human-readable format.
        
        Args:
            num_bytes: Number of bytes
            
        Returns:
            Human-readable string
        """
        if num_bytes > 1024 * 1024 * 1024:
            return f"{num_bytes / (1024 * 1024 * 1024):.2f} GB"
        elif num_bytes > 1024 * 1024:
            return f"{num_bytes / (1024 * 1024):.2f} MB"
        elif num_bytes > 1024:
            return f"{num_bytes / 1024:.2f} KB"
        else:
            return f"{num_bytes} bytes"

def perform_maintenance(root_dir: Union[str, Path], tasks: Optional[List[str]] = None, 
                        config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Perform maintenance tasks.
    
    Args:
        root_dir: Root directory of the Smart Steps AI system
        tasks: List of task names to perform. If None, perform all tasks.
        config: Optional configuration dictionary
        
    Returns:
        Dictionary with results of maintenance tasks
    """
    manager = MaintenanceManager(root_dir, config)
    return manager.perform_maintenance(tasks)

def check_system_health(root_dir: Union[str, Path], 
                      config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Check the health of the system.
    
    Args:
        root_dir: Root directory of the Smart Steps AI system
        config: Optional configuration dictionary
        
    Returns:
        Dictionary with system health information
    """
    manager = MaintenanceManager(root_dir, config)
    
    # Check disk space
    disk_space = manager.check_disk_space()
    
    # Return health information
    return {
        "disk_space": disk_space,
        "timestamp": datetime.datetime.now().isoformat(),
        "python_version": sys.version,
        "platform": sys.platform,
        "memory_info": _get_memory_info()
    }

def _get_memory_info() -> Dict[str, Any]:
    """
    Get memory usage information.
    
    Returns:
        Dictionary with memory usage information
    """
    try:
        import psutil
        
        # Get virtual memory info
        memory = psutil.virtual_memory()
        
        return {
            "total_bytes": memory.total,
            "available_bytes": memory.available,
            "used_bytes": memory.used,
            "percent_used": memory.percent,
            "total_human": _bytes_to_human(memory.total),
            "available_human": _bytes_to_human(memory.available),
            "used_human": _bytes_to_human(memory.used)
        }
    except ImportError:
        return {
            "error": "psutil module not available"
        }

def _bytes_to_human(num_bytes: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        num_bytes: Number of bytes
        
    Returns:
        Human-readable string
    """
    if num_bytes > 1024 * 1024 * 1024:
        return f"{num_bytes / (1024 * 1024 * 1024):.2f} GB"
    elif num_bytes > 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.2f} MB"
    elif num_bytes > 1024:
        return f"{num_bytes / 1024:.2f} KB"
    else:
        return f"{num_bytes} bytes"

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("maintenance.log"),
            logging.StreamHandler()
        ]
    )
    
    # Get root directory from command line argument or use current directory
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = os.getcwd()
    
    # Perform maintenance
    results = perform_maintenance(root_dir)
    
    # Print results
    print(json.dumps(results, indent=2))
