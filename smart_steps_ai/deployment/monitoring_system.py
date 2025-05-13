#!/usr/bin/env python
"""
Monitoring System for Smart Steps AI

This module provides runtime monitoring and maintenance for Smart Steps AI API:
- System health monitoring (CPU, memory, disk usage)
- API performance metrics (response times, error rates, request counts)
- Automatic alerting via email and other channels
- Log aggregation and analysis
- Periodic maintenance tasks

Usage:
    python monitoring_system.py start
    python monitoring_system.py status
    python monitoring_system.py stop
    python monitoring_system.py run-maintenance

Author: Smart Steps Team
Date: May, 2025
"""

import argparse
import datetime
import json
import logging
import os
import platform
import psutil
import re
import requests
import signal
import smtplib
import socket
import sqlite3
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("monitoring.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("monitoring_system")

# Constants
ROOT_DIR = Path(__file__).parent.parent.absolute()
CONFIG_PATH = ROOT_DIR / "config" / "monitoring.yaml"
DB_PATH = ROOT_DIR / "logs" / "monitoring.db"
PID_FILE = ROOT_DIR / "logs" / "monitoring.pid"
API_ENDPOINTS = [
    "/api/v1/status",
    "/api/v1/sessions",
    "/api/v1/personas",
    "/api/v1/analysis/metrics"
]

# Default configuration
DEFAULT_CONFIG = {
    "monitoring": {
        "interval": 60,  # seconds
        "log_retention_days": 30,
        "alert_thresholds": {
            "cpu_percent": 80,
            "memory_percent": 80,
            "disk_percent": 90,
            "response_time_ms": 2000,
            "error_rate_percent": 5
        }
    },
    "api": {
        "base_url": "http://localhost:9500",
        "timeout": 5,  # seconds
        "health_endpoint": "/health"
    },
    "alerts": {
        "email": {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "",
            "password": "",
            "from_email": "",
            "to_emails": []
        },
        "sms": {
            "enabled": False,
            "provider": "twilio",
            "account_sid": "",
            "auth_token": "",
            "from_number": "",
            "to_numbers": []
        }
    },
    "maintenance": {
        "log_cleanup": {
            "enabled": True,
            "schedule": "0 0 * * *",  # cron syntax: midnight daily
            "max_age_days": 30
        },
        "db_vacuum": {
            "enabled": True,
            "schedule": "0 1 * * 0",  # cron syntax: 1:00 AM on Sundays
        },
        "memory_cache_clear": {
            "enabled": True,
            "schedule": "0 */6 * * *",  # cron syntax: every 6 hours
        }
    }
}

# Database initialization
def init_database():
    """Initialize the monitoring database if it doesn't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME NOT NULL,
        cpu_percent REAL,
        memory_total INTEGER,
        memory_used INTEGER,
        memory_percent REAL,
        disk_total INTEGER,
        disk_used INTEGER,
        disk_percent REAL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME NOT NULL,
        endpoint TEXT NOT NULL,
        response_time_ms REAL,
        status_code INTEGER,
        success BOOLEAN
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME NOT NULL,
        type TEXT NOT NULL,
        message TEXT NOT NULL,
        acknowledged BOOLEAN DEFAULT FALSE
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS maintenance_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME NOT NULL,
        task TEXT NOT NULL,
        status TEXT NOT NULL,
        details TEXT
    )
    ''')
    
    # Create indexes for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_metrics_timestamp ON api_metrics(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_metrics_endpoint ON api_metrics(endpoint)')
    
    conn.commit()
    conn.close()
    
    logger.info("Database initialized at %s", DB_PATH)

class MonitoringConfig:
    """Class to manage monitoring configuration."""
    
    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from YAML file, creating it if it doesn't exist."""
        if not self.config_path.exists():
            logger.info("Configuration file not found, creating default configuration")
            self._create_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Validate the configuration (basic validation)
            self._validate_config(config)
            return config
        except Exception as e:
            logger.error("Error loading configuration: %s", str(e))
            logger.info("Using default configuration instead")
            return DEFAULT_CONFIG
    
    def _create_default_config(self):
        """Create a default configuration file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
        
        logger.info("Created default configuration at %s", self.config_path)
    
    def _validate_config(self, config: dict):
        """Validate the configuration structure (basic validation)."""
        required_sections = ["monitoring", "api", "alerts", "maintenance"]
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required configuration section: {section}")
    
    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """Get a configuration value."""
        if section not in self.config:
            return default
        
        if key is None:
            return self.config[section]
        
        if key not in self.config[section]:
            return default
        
        return self.config[section][key]
    
    def set(self, section: str, key: str, value: Any):
        """Set a configuration value."""
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
        
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

class SystemMonitor:
    """Monitor system resources (CPU, memory, disk)."""
    
    def __init__(self, config: MonitoringConfig, db_path: Path = DB_PATH):
        self.config = config
        self.db_path = db_path
        self.should_run = False
        self.monitor_thread = None
    
    def start(self):
        """Start the monitoring thread."""
        if self.monitor_thread and self.monitor_thread.is_alive():
            logger.warning("System monitor is already running")
            return
        
        self.should_run = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("System monitor started")
    
    def stop(self):
        """Stop the monitoring thread."""
        self.should_run = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            logger.info("System monitor stopped")
    
    def _monitor_loop(self):
        """Monitoring loop that collects system metrics periodically."""
        interval = self.config.get("monitoring", "interval", 60)
        
        while self.should_run:
            try:
                self._collect_system_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error("Error in system monitoring: %s", str(e))
                time.sleep(interval)
    
    def _collect_system_metrics(self):
        """Collect and store system metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_total = memory.total
        memory_used = memory.used
        memory_percent = memory.percent
        
        # Disk usage (root disk)
        disk = psutil.disk_usage('/')
        disk_total = disk.total
        disk_used = disk.used
        disk_percent = disk.percent
        
        # Store metrics in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO system_metrics 
            (timestamp, cpu_percent, memory_total, memory_used, memory_percent, 
             disk_total, disk_used, disk_percent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            cpu_percent,
            memory_total,
            memory_used,
            memory_percent,
            disk_total,
            disk_used,
            disk_percent
        ))
        
        conn.commit()
        conn.close()
        
        # Check for threshold violations
        self._check_thresholds(cpu_percent, memory_percent, disk_percent)
    
    def _check_thresholds(self, cpu_percent: float, memory_percent: float, disk_percent: float):
        """Check if any metrics exceed configured thresholds."""
        thresholds = self.config.get("monitoring", "alert_thresholds", {})
        
        alerts = []
        
        if cpu_percent > thresholds.get("cpu_percent", 80):
            message = f"CPU usage is high: {cpu_percent:.1f}% (threshold: {thresholds.get('cpu_percent', 80)}%)"
            alerts.append(("cpu", message))
        
        if memory_percent > thresholds.get("memory_percent", 80):
            message = f"Memory usage is high: {memory_percent:.1f}% (threshold: {thresholds.get('memory_percent', 80)}%)"
            alerts.append(("memory", message))
        
        if disk_percent > thresholds.get("disk_percent", 90):
            message = f"Disk usage is high: {disk_percent:.1f}% (threshold: {thresholds.get('disk_percent', 90)}%)"
            alerts.append(("disk", message))
        
        # Send alerts if needed
        for alert_type, message in alerts:
            self._record_alert(alert_type, message)
    
    def _record_alert(self, alert_type: str, message: str):
        """Record an alert in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO alerts (timestamp, type, message, acknowledged)
        VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            alert_type,
            message,
            False
        ))
        
        conn.commit()
        conn.close()
        
        logger.warning("Alert: %s", message)
        
        # Send the alert
        AlertManager(self.config).send_alert(alert_type, message)

class ApiMonitor:
    """Monitor API health and performance."""
    
    def __init__(self, config: MonitoringConfig, db_path: Path = DB_PATH):
        self.config = config
        self.db_path = db_path
        self.should_run = False
        self.monitor_thread = None
    
    def start(self):
        """Start the API monitoring thread."""
        if self.monitor_thread and self.monitor_thread.is_alive():
            logger.warning("API monitor is already running")
            return
        
        self.should_run = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("API monitor started")
    
    def stop(self):
        """Stop the API monitoring thread."""
        self.should_run = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            logger.info("API monitor stopped")
    
    def _monitor_loop(self):
        """Monitoring loop that tests API endpoints periodically."""
        interval = self.config.get("monitoring", "interval", 60)
        
        while self.should_run:
            try:
                self._check_api_health()
                time.sleep(interval)
            except Exception as e:
                logger.error("Error in API monitoring: %s", str(e))
                time.sleep(interval)
    
    def _check_api_health(self):
        """Check API health by calling the health endpoint and selected API endpoints."""
        api_config = self.config.get("api", {})
        base_url = api_config.get("base_url", "http://localhost:9500")
        timeout = api_config.get("timeout", 5)
        health_endpoint = api_config.get("health_endpoint", "/health")
        
        # Check health endpoint
        self._check_endpoint(base_url + health_endpoint, "health")
        
        # Check other API endpoints
        for endpoint in API_ENDPOINTS:
            self._check_endpoint(base_url + endpoint, endpoint)
    
    def _check_endpoint(self, url: str, endpoint_name: str):
        """Check a specific API endpoint and record metrics."""
        start_time = time.time()
        success = False
        status_code = 0
        
        try:
            response = requests.get(url, timeout=self.config.get("api", "timeout", 5))
            status_code = response.status_code
            success = 200 <= status_code < 300
        except requests.RequestException as e:
            logger.error("Error checking endpoint %s: %s", endpoint_name, str(e))
        finally:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
        
        # Record metrics in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO api_metrics 
            (timestamp, endpoint, response_time_ms, status_code, success)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            endpoint_name,
            response_time_ms,
            status_code,
            success
        ))
        
        conn.commit()
        conn.close()
        
        # Check for threshold violations
        self._check_api_thresholds(endpoint_name, response_time_ms, success)
    
    def _check_api_thresholds(self, endpoint_name: str, response_time_ms: float, success: bool):
        """Check if API metrics exceed configured thresholds."""
        thresholds = self.config.get("monitoring", "alert_thresholds", {})
        
        # Check response time threshold
        max_response_time = thresholds.get("response_time_ms", 2000)
        if response_time_ms > max_response_time:
            message = f"API endpoint {endpoint_name} response time is high: {response_time_ms:.1f}ms (threshold: {max_response_time}ms)"
            self._record_alert("api_response_time", message)
        
        # Check for failure
        if not success:
            message = f"API endpoint {endpoint_name} failed"
            self._record_alert("api_failure", message)
        
        # Check error rate (over the last hour)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT COUNT(*) as total, SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failures
        FROM api_metrics
        WHERE endpoint = ? AND timestamp > datetime('now', '-1 hour')
        ''', (endpoint_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] > 0:  # if we have data
            total = row[0]
            failures = row[1]
            error_rate = (failures / total) * 100
            
            max_error_rate = thresholds.get("error_rate_percent", 5)
            if error_rate > max_error_rate:
                message = f"API endpoint {endpoint_name} error rate is high: {error_rate:.1f}% (threshold: {max_error_rate}%)"
                self._record_alert("api_error_rate", message)
    
    def _record_alert(self, alert_type: str, message: str):
        """Record an alert in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO alerts (timestamp, type, message, acknowledged)
        VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            alert_type,
            message,
            False
        ))
        
        conn.commit()
        conn.close()
        
        logger.warning("Alert: %s", message)
        
        # Send the alert
        AlertManager(self.config).send_alert(alert_type, message)

class AlertManager:
    """Manage alerts and notifications."""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
    
    def send_alert(self, alert_type: str, message: str):
        """Send an alert notification."""
        logger.info("Sending alert: %s - %s", alert_type, message)
        
        # Send email alert if enabled
        if self.config.get("alerts", "email", {}).get("enabled", False):
            self._send_email_alert(alert_type, message)
        
        # Send SMS alert if enabled
        if self.config.get("alerts", "sms", {}).get("enabled", False):
            self._send_sms_alert(alert_type, message)
    
    def _send_email_alert(self, alert_type: str, message: str):
        """Send an email alert."""
        try:
            email_config = self.config.get("alerts", "email", {})
            
            # Prepare email
            hostname = socket.gethostname()
            subject = f"Smart Steps AI Alert: {alert_type} on {hostname}"
            
            body = f"""
            <html>
            <body>
            <h2>Smart Steps AI Monitoring Alert</h2>
            <p><strong>Type:</strong> {alert_type}</p>
            <p><strong>Server:</strong> {hostname}</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Message:</strong> {message}</p>
            </body>
            </html>
            """
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = email_config.get("from_email")
            msg['To'] = ", ".join(email_config.get("to_emails", []))
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(email_config.get("smtp_server"), email_config.get("smtp_port", 587))
            server.starttls()
            server.login(email_config.get("username"), email_config.get("password"))
            server.send_message(msg)
            server.quit()
            
            logger.info("Email alert sent successfully")
        except Exception as e:
            logger.error("Error sending email alert: %s", str(e))
    
    def _send_sms_alert(self, alert_type: str, message: str):
        """Send an SMS alert."""
        try:
            sms_config = self.config.get("alerts", "sms", {})
            provider = sms_config.get("provider", "").lower()
            
            if provider == "twilio":
                # This is a placeholder - in a real implementation, you would import the Twilio client
                # and send the SMS using their API
                account_sid = sms_config.get("account_sid")
                auth_token = sms_config.get("auth_token")
                from_number = sms_config.get("from_number")
                to_numbers = sms_config.get("to_numbers", [])
                
                sms_text = f"Smart Steps Alert: {alert_type} - {message}"
                
                # This is just a placeholder for the Twilio API call
                logger.info("Would send SMS via Twilio: %s", sms_text)
                
                # In a real implementation:
                # from twilio.rest import Client
                # client = Client(account_sid, auth_token)
                # for to_number in to_numbers:
                #     client.messages.create(body=sms_text, from_=from_number, to=to_number)
            else:
                logger.warning("Unknown SMS provider: %s", provider)
        except Exception as e:
            logger.error("Error sending SMS alert: %s", str(e))

class MaintenanceManager:
    """Manage periodic maintenance tasks."""
    
    def __init__(self, config: MonitoringConfig, db_path: Path = DB_PATH):
        self.config = config
        self.db_path = db_path
    
    def run_maintenance(self):
        """Run all enabled maintenance tasks."""
        logger.info("Starting maintenance tasks")
        
        maintenance_config = self.config.get("maintenance", {})
        
        # Log cleanup task
        if maintenance_config.get("log_cleanup", {}).get("enabled", True):
            self._cleanup_logs()
        
        # Database vacuum task
        if maintenance_config.get("db_vacuum", {}).get("enabled", True):
            self._vacuum_database()
        
        # Memory cache clear task
        if maintenance_config.get("memory_cache_clear", {}).get("enabled", True):
            self._clear_memory_caches()
        
        logger.info("Maintenance tasks completed")
    
    def _cleanup_logs(self):
        """Clean up old log files and database records."""
        try:
            logger.info("Running log cleanup task")
            
            # Get max age from config
            max_age_days = self.config.get("maintenance", "log_cleanup", {}).get("max_age_days", 30)
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            cutoff_date_str = cutoff_date.isoformat()
            
            # Clean up database records
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete old system metrics
            cursor.execute("DELETE FROM system_metrics WHERE timestamp < ?", (cutoff_date_str,))
            sys_metrics_deleted = cursor.rowcount
            
            # Delete old API metrics
            cursor.execute("DELETE FROM api_metrics WHERE timestamp < ?", (cutoff_date_str,))
            api_metrics_deleted = cursor.rowcount
            
            # Delete old acknowledged alerts
            cursor.execute("DELETE FROM alerts WHERE timestamp < ? AND acknowledged = 1", (cutoff_date_str,))
            alerts_deleted = cursor.rowcount
            
            conn.commit()
            
            # Record the maintenance run
            cursor.execute('''
            INSERT INTO maintenance_runs (timestamp, task, status, details)
            VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                "log_cleanup",
                "success",
                json.dumps({
                    "system_metrics_deleted": sys_metrics_deleted,
                    "api_metrics_deleted": api_metrics_deleted,
                    "alerts_deleted": alerts_deleted,
                    "max_age_days": max_age_days
                })
            ))
            
            conn.commit()
            conn.close()
            
            # Clean up log files
            log_dir = Path(ROOT_DIR) / "logs"
            if log_dir.exists():
                cutoff_timestamp = cutoff_date.timestamp()
                for log_file in log_dir.glob("*.log"):
                    if log_file.stat().st_mtime < cutoff_timestamp:
                        log_file.unlink()
                        logger.info("Deleted old log file: %s", log_file)
            
            logger.info(
                "Log cleanup complete: removed %d system metrics, %d API metrics, %d alerts",
                sys_metrics_deleted, api_metrics_deleted, alerts_deleted
            )
        except Exception as e:
            logger.error("Error in log cleanup task: %s", str(e))
            
            # Record the failed maintenance run
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                INSERT INTO maintenance_runs (timestamp, task, status, details)
                VALUES (?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    "log_cleanup",
                    "error",
                    str(e)
                ))
                
                conn.commit()
                conn.close()
            except Exception as inner_e:
                logger.error("Error recording maintenance failure: %s", str(inner_e))
    
    def _vacuum_database(self):
        """Vacuum the SQLite database to optimize it."""
        try:
            logger.info("Running database vacuum task")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get database size before vacuum
            cursor.execute("PRAGMA page_count")
            page_count_before = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            size_before = page_count_before * page_size
            
            # Run vacuum
            cursor.execute("VACUUM")
            
            # Get database size after vacuum
            cursor.execute("PRAGMA page_count")
            page_count_after = cursor.fetchone()[0]
            size_after = page_count_after * page_size
            
            # Record the maintenance run
            cursor.execute('''
            INSERT INTO maintenance_runs (timestamp, task, status, details)
            VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                "db_vacuum",
                "success",
                json.dumps({
                    "size_before_bytes": size_before,
                    "size_after_bytes": size_after,
                    "bytes_saved": size_before - size_after
                })
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(
                "Database vacuum complete: size reduced from %.2f MB to %.2f MB (saved %.2f MB)",
                size_before / (1024 * 1024), size_after / (1024 * 1024),
                (size_before - size_after) / (1024 * 1024)
            )
        except Exception as e:
            logger.error("Error in database vacuum task: %s", str(e))
            
            # Record the failed maintenance run
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                INSERT INTO maintenance_runs (timestamp, task, status, details)
                VALUES (?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    "db_vacuum",
                    "error",
                    str(e)
                ))
                
                conn.commit()
                conn.close()
            except Exception as inner_e:
                logger.error("Error recording maintenance failure: %s", str(inner_e))
    
    def _clear_memory_caches(self):
        """Clear memory caches in the Smart Steps API."""
        try:
            logger.info("Running memory cache clear task")
            
            api_config = self.config.get("api", {})
            base_url = api_config.get("base_url", "http://localhost:9500")
            cache_clear_endpoint = base_url + "/api/v1/admin/clear-cache"
            
            # Call the clear cache endpoint
            response = requests.post(cache_clear_endpoint, timeout=api_config.get("timeout", 5))
            
            success = 200 <= response.status_code < 300
            
            # Record the maintenance run
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO maintenance_runs (timestamp, task, status, details)
            VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                "memory_cache_clear",
                "success" if success else "error",
                json.dumps({
                    "status_code": response.status_code,
                    "response": response.text
                })
            ))
            
            conn.commit()
            conn.close()
            
            if success:
                logger.info("Memory cache clear complete: %s", response.text)
            else:
                logger.error("Memory cache clear failed: %s", response.text)
        except Exception as e:
            logger.error("Error in memory cache clear task: %s", str(e))
            
            # Record the failed maintenance run
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                INSERT INTO maintenance_runs (timestamp, task, status, details)
                VALUES (?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    "memory_cache_clear",
                    "error",
                    str(e)
                ))
                
                conn.commit()
                conn.close()
            except Exception as inner_e:
                logger.error("Error recording maintenance failure: %s", str(inner_e))

class MonitoringDaemon:
    """Main daemon class for the monitoring system."""
    
    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config = MonitoringConfig(config_path)
        self.system_monitor = SystemMonitor(self.config)
        self.api_monitor = ApiMonitor(self.config)
        self.maintenance_manager = MaintenanceManager(self.config)
        self.running = False
    
    def start(self):
        """Start the monitoring daemon."""
        logger.info("Starting monitoring daemon")
        
        # Initialize database
        init_database()
        
        # Start monitors
        self.system_monitor.start()
        self.api_monitor.start()
        
        # Write PID file
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        
        self.running = True
        logger.info("Monitoring daemon started")
    
    def stop(self):
        """Stop the monitoring daemon."""
        logger.info("Stopping monitoring daemon")
        
        # Stop monitors
        self.system_monitor.stop()
        self.api_monitor.stop()
        
        # Remove PID file
        if os.path.exists(PID_FILE):
            os.unlink(PID_FILE)
        
        self.running = False
        logger.info("Monitoring daemon stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the monitoring system."""
        status = {
            "running": self.running,
            "system_monitor_running": self.system_monitor.monitor_thread is not None and self.system_monitor.monitor_thread.is_alive(),
            "api_monitor_running": self.api_monitor.monitor_thread is not None and self.api_monitor.monitor_thread.is_alive(),
            "uptime": None,
            "recent_alerts": [],
            "metrics_summary": {}
        }
        
        # Get uptime if PID file exists
        if os.path.exists(PID_FILE):
            try:
                pid = int(open(PID_FILE, 'r').read().strip())
                process = psutil.Process(pid)
                status["uptime"] = datetime.now() - datetime.fromtimestamp(process.create_time())
            except (ProcessLookupError, ValueError):
                pass
        
        # Get recent alerts
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT timestamp, type, message
            FROM alerts
            ORDER BY timestamp DESC
            LIMIT 5
            ''')
            
            status["recent_alerts"] = [
                {
                    "timestamp": row[0],
                    "type": row[1],
                    "message": row[2]
                }
                for row in cursor.fetchall()
            ]
            
            # Get metrics summary
            cursor.execute('''
            SELECT
                AVG(cpu_percent) as avg_cpu,
                AVG(memory_percent) as avg_memory,
                AVG(disk_percent) as avg_disk
            FROM system_metrics
            WHERE timestamp > datetime('now', '-1 hour')
            ''')
            
            row = cursor.fetchone()
            if row:
                status["metrics_summary"]["system"] = {
                    "avg_cpu_percent": row[0],
                    "avg_memory_percent": row[1],
                    "avg_disk_percent": row[2]
                }
            
            cursor.execute('''
            SELECT
                endpoint,
                AVG(response_time_ms) as avg_response_time,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
            FROM api_metrics
            WHERE timestamp > datetime('now', '-1 hour')
            GROUP BY endpoint
            ''')
            
            status["metrics_summary"]["api"] = {
                row[0]: {
                    "avg_response_time_ms": row[1],
                    "success_rate_percent": row[2]
                }
                for row in cursor.fetchall()
            }
            
            cursor.execute('''
            SELECT
                task,
                status,
                MAX(timestamp) as last_run
            FROM maintenance_runs
            GROUP BY task
            ''')
            
            status["metrics_summary"]["maintenance"] = {
                row[0]: {
                    "status": row[1],
                    "last_run": row[2]
                }
                for row in cursor.fetchall()
            }
            
            conn.close()
        except Exception as e:
            logger.error("Error getting status: %s", str(e))
        
        return status

def is_daemon_running() -> bool:
    """Check if the monitoring daemon is already running."""
    if not os.path.exists(PID_FILE):
        return False
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process with this PID exists
        process = psutil.Process(pid)
        return True
    except (ProcessLookupError, ValueError):
        # PID file exists but process does not
        return False

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Smart Steps AI Monitoring System")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Start command
    subparsers.add_parser("start", help="Start the monitoring daemon")
    
    # Stop command
    subparsers.add_parser("stop", help="Stop the monitoring daemon")
    
    # Status command
    subparsers.add_parser("status", help="Get the status of the monitoring daemon")
    
    # Run maintenance command
    subparsers.add_parser("run-maintenance", help="Run maintenance tasks")
    
    args = parser.parse_args()
    
    if args.command == "start":
        if is_daemon_running():
            logger.warning("Monitoring daemon is already running")
        else:
            daemon = MonitoringDaemon()
            daemon.start()
    
    elif args.command == "stop":
        if not is_daemon_running():
            logger.warning("Monitoring daemon is not running")
        else:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, signal.SIGTERM)
            logger.info("Sent SIGTERM to monitoring daemon (PID %d)", pid)
    
    elif args.command == "status":
        if not is_daemon_running():
            print("Monitoring daemon is not running")
        else:
            daemon = MonitoringDaemon()
            status = daemon.get_status()
            
            print("Monitoring Status:")
            print(f"  Running: {status['running']}")
            print(f"  System Monitor: {'Running' if status['system_monitor_running'] else 'Stopped'}")
            print(f"  API Monitor: {'Running' if status['api_monitor_running'] else 'Stopped'}")
            
            if status['uptime']:
                days = status['uptime'].days
                hours, remainder = divmod(status['uptime'].seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f"  Uptime: {days}d {hours}h {minutes}m {seconds}s")
            
            if status['recent_alerts']:
                print("\nRecent Alerts:")
                for alert in status['recent_alerts']:
                    print(f"  [{alert['timestamp']}] {alert['type']}: {alert['message']}")
            
            if 'system' in status['metrics_summary']:
                system = status['metrics_summary']['system']
                print("\nSystem Metrics (Last Hour):")
                print(f"  CPU: {system['avg_cpu_percent']:.1f}%")
                print(f"  Memory: {system['avg_memory_percent']:.1f}%")
                print(f"  Disk: {system['avg_disk_percent']:.1f}%")
            
            if 'api' in status['metrics_summary']:
                api = status['metrics_summary']['api']
                print("\nAPI Metrics (Last Hour):")
                for endpoint, metrics in api.items():
                    print(f"  {endpoint}:")
                    print(f"    Response Time: {metrics['avg_response_time_ms']:.1f}ms")
                    print(f"    Success Rate: {metrics['success_rate_percent']:.1f}%")
            
            if 'maintenance' in status['metrics_summary']:
                maintenance = status['metrics_summary']['maintenance']
                print("\nMaintenance:")
                for task, info in maintenance.items():
                    print(f"  {task}: {info['status']} (Last Run: {info['last_run']})")
    
    elif args.command == "run-maintenance":
        logger.info("Running maintenance tasks")
        daemon = MonitoringDaemon()
        daemon.maintenance_manager.run_maintenance()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
