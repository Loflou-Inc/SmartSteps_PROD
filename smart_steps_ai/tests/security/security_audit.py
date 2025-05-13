"""
Security audit script for the Smart Steps AI application.

This script performs a comprehensive security audit of the Smart Steps AI
application, including authentication, authorization, input validation,
API security, and data protection.
"""

import os
import sys
import time
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re
import hashlib
import random
import string
import subprocess
import urllib.parse

import httpx
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from smart_steps_ai.utils.logging import setup_logger

# Configure logging
logger = setup_logger(__name__)

# Create console for rich output
console = Console()

def generate_random_string(length=10):
    """Generate a random string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def check_dependency_vulnerabilities():
    """Check for known vulnerabilities in dependencies."""
    console.print(Panel("[bold]Checking Dependencies for Vulnerabilities[/bold]"))
    
    try:
        # Run safety check on requirements.txt
        requirements_path = Path(__file__).parent.parent.parent / "requirements.txt"
        
        if requirements_path.exists():
            console.print(f"Checking dependencies in: {requirements_path}")
            
            # Try installing safety if not available
            try:
                subprocess.run(["safety", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                console.print("Installing safety package...")
                subprocess.run([sys.executable, "-m", "pip", "install", "safety"], check=True)
            
            # Run safety check
            result = subprocess.run(
                ["safety", "check", "-r", str(requirements_path), "--json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print("[green]✓ No vulnerable dependencies found[/green]")
                return []
            else:
                try:
                    safety_data = json.loads(result.stdout)
                    vulnerabilities = safety_data.get("vulnerabilities", [])
                    
                    if vulnerabilities:
                        table = Table(title=f"Found {len(vulnerabilities)} Vulnerable Dependencies")
                        table.add_column("Package")
                        table.add_column("Installed Version")
                        table.add_column("Vulnerable Version(s)")
                        table.add_column("Vulnerability ID")
                        table.add_column("Severity")
                        
                        for vuln in vulnerabilities:
                            table.add_row(
                                vuln.get("package_name", ""),
                                vuln.get("installed_version", ""),
                                vuln.get("vulnerable_spec", ""),
                                vuln.get("vulnerability_id", ""),
                                vuln.get("severity", "")
                            )
                        
                        console.print(table)
                        return vulnerabilities
                    else:
                        console.print("[green]✓ No vulnerable dependencies found[/green]")
                        return []
                except json.JSONDecodeError:
                    console.print("[red]Failed to parse safety output[/red]")
                    console.print(result.stdout)
                    return []
        else:
            console.print(f"[yellow]Requirements file not found: {requirements_path}[/yellow]")
            return []
    except Exception as e:
        console.print(f"[red]Error checking dependencies: {e}[/red]")
        return []

def scan_code_for_vulnerabilities(directories=None):
    """
    Scan code for potential security vulnerabilities.
    
    Args:
        directories: List of directories to scan
    
    Returns:
        List of findings
    """
    console.print(Panel("[bold]Scanning Code for Vulnerabilities[/bold]"))
    
    if not directories:
        # Default directories to scan
        directories = [
            Path(__file__).parent.parent.parent / "src",
            Path(__file__).parent.parent.parent / "tests",
        ]
    
    findings = []
    
    # Security patterns to check for
    patterns = {
        "Hardcoded Secret": [
            r'(?i)(?:password|passwd|pwd|secret|key|token|auth)[\s]*=[\s]*["\'](?![\s]*\$|[\s]*{)[^\'"]+["\']',
            r'(?i)(?:password|passwd|pwd|secret|key|token|auth)[\s]*=[\s]*["\'](?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?["\']',
        ],
        "SQL Injection Risk": [
            r'f"SELECT.*{',
            r"f'SELECT.*{",
            r'f"UPDATE.*{',
            r"f'UPDATE.*{",
            r'f"INSERT.*{',
            r"f'INSERT.*{",
            r'f"DELETE.*{',
            r"f'DELETE.*{",
            r'execute\(f".*{',
            r"execute\(f'.*{",
            r'cursor\.execute\(.*\+',
            r'\.execute\(".*" % ',
        ],
        "Path Traversal Risk": [
            r'open\(.*\+',
            r'open\(f["\'].*{.*}',
        ],
        "Command Injection Risk": [
            r'subprocess\.(?:call|run|Popen|check_output)\((?:f|r)["\']',
            r'os\.(?:system|popen)\((?:f|r)["\']',
            r'(?:subprocess|os)\.(?:call|run|Popen|check_output|system|popen)\([^,)]*\+[^,)]*\)',
        ],
        "Insecure Deserialization": [
            r'pickle\.loads?\(',
            r'yaml\.load\([^,)]*\)',  # Only unsafe without SafeLoader
            r'marshal\.loads?\(',
        ],
        "JWT No Verification": [
            r'jwt\.decode\([^,)]*\)',  # Only unsafe without verify
        ],
        "Insecure Hash Function": [
            r'hashlib\.md5\(',
            r'hashlib\.sha1\(',
        ],
        "Timing Attack Vulnerability": [
            r'==',  # When used for password/token comparison
        ],
    }
    
    total_files = 0
    
    # Count files
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    total_files += 1
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Scanning files...", total=total_files)
        
        for directory in directories:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                                for issue_type, issue_patterns in patterns.items():
                                    for pattern in issue_patterns:
                                        matches = re.finditer(pattern, content)
                                        
                                        for match in matches:
                                            # Skip false positives in test files
                                            if "test_" in file and issue_type in ["Hardcoded Secret", "Insecure Hash Function"]:
                                                continue
                                            
                                            # Get the line number
                                            line_number = content[:match.start()].count('\n') + 1
                                            
                                            # Get the line content
                                            lines = content.split('\n')
                                            line_content = lines[line_number - 1] if line_number <= len(lines) else ""
                                            
                                            # Add finding
                                            findings.append({
                                                "type": issue_type,
                                                "file": file_path,
                                                "line": line_number,
                                                "content": line_content.strip(),
                                                "match": match.group(0),
                                                "severity": "High" if issue_type in ["Hardcoded Secret", "SQL Injection Risk", "Command Injection Risk", "Path Traversal Risk"] else "Medium"
                                            })
                        except Exception as e:
                            console.print(f"[red]Error scanning file {file_path}: {e}[/red]")
                    
                    progress.update(task, advance=1)
    
    # Display findings
    if findings:
        table = Table(title=f"Found {len(findings)} Potential Security Issues")
        table.add_column("Type")
        table.add_column("File")
        table.add_column("Line")
        table.add_column("Content")
        table.add_column("Severity")
        
        for finding in findings:
            table.add_row(
                finding["type"],
                os.path.relpath(finding["file"], Path(__file__).parent.parent.parent),
                str(finding["line"]),
                finding["content"],
                finding["severity"]
            )
        
        console.print(table)
    else:
        console.print("[green]✓ No code vulnerabilities found[/green]")
    
    return findings

def check_api_security(base_url="http://localhost:8000"):
    """
    Check API security.
    
    Args:
        base_url: Base URL of the API
        
    Returns:
        List of findings
    """
    console.print(Panel("[bold]Checking API Security[/bold]"))
    
    findings = []
    client = httpx.Client(timeout=10.0, verify=False)
    
    # Endpoints to check
    endpoints = [
        "/api/v1/sessions",
        "/api/v1/personas",
        "/api/v1/auth/token",
        "/api/v1/analysis/sessions/test",
        "/api/docs",
    ]
    
    # Check for CORS misconfigurations
    console.print("Checking CORS configuration...")
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        
        try:
            # Send OPTIONS request with origin header
            response = client.options(
                url,
                headers={
                    "Origin": "https://evil.example.com",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type",
                }
            )
            
            # Check for overly permissive CORS headers
            if "Access-Control-Allow-Origin" in response.headers:
                if response.headers["Access-Control-Allow-Origin"] == "*":
                    findings.append({
                        "type": "CORS Misconfiguration",
                        "endpoint": endpoint,
                        "details": "Allows any origin (*) for cross-origin requests",
                        "severity": "Medium",
                    })
                elif "evil.example.com" in response.headers["Access-Control-Allow-Origin"]:
                    findings.append({
                        "type": "CORS Misconfiguration",
                        "endpoint": endpoint,
                        "details": "Reflects Origin header in Access-Control-Allow-Origin",
                        "severity": "High",
                    })
        except Exception as e:
            console.print(f"[yellow]Error checking CORS for {endpoint}: {e}[/yellow]")
    
    # Check for authentication bypass
    console.print("Checking authentication...")
    
    for endpoint in endpoints:
        if endpoint == "/api/v1/auth/token" or endpoint == "/api/docs":
            continue
        
        url = f"{base_url}{endpoint}"
        
        try:
            # Try to access without authentication
            response = client.get(url)
            
            if response.status_code != 401 and response.status_code != 403:
                findings.append({
                    "type": "Authentication Bypass",
                    "endpoint": endpoint,
                    "details": f"Endpoint accessible without authentication (Status: {response.status_code})",
                    "severity": "High",
                })
        except Exception as e:
            console.print(f"[yellow]Error checking authentication for {endpoint}: {e}[/yellow]")
    
    # Check for common security headers
    console.print("Checking security headers...")
    
    security_headers = {
        "Strict-Transport-Security": "Missing HSTS header",
        "X-Content-Type-Options": "Missing X-Content-Type-Options header",
        "X-Frame-Options": "Missing X-Frame-Options header",
        "Content-Security-Policy": "Missing Content-Security-Policy header",
    }
    
    try:
        response = client.get(f"{base_url}/api/docs")
        
        for header, message in security_headers.items():
            if header not in response.headers:
                findings.append({
                    "type": "Missing Security Header",
                    "endpoint": "/api/docs",
                    "details": message,
                    "severity": "Medium",
                })
    except Exception as e:
        console.print(f"[yellow]Error checking security headers: {e}[/yellow]")
    
    # Check for SQL injection
    console.print("Checking for SQL injection vulnerabilities...")
    
    sql_injection_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
    ]
    
    for payload in sql_injection_payloads:
        try:
            # Try to login with SQL injection payload
            response = client.post(
                f"{base_url}/api/v1/auth/token",
                data={
                    "username": payload,
                    "password": payload,
                }
            )
            
            # If successful login, potential SQL injection
            if response.status_code == 200:
                findings.append({
                    "type": "SQL Injection",
                    "endpoint": "/api/v1/auth/token",
                    "details": f"Potential SQL injection vulnerability with payload: {payload}",
                    "severity": "Critical",
                })
                break
        except Exception as e:
            console.print(f"[yellow]Error checking SQL injection: {e}[/yellow]")
    
    # Check for path traversal
    console.print("Checking for path traversal vulnerabilities...")
    
    path_traversal_payloads = [
        "../../../etc/passwd",
        "..\\..\\..\\Windows\\win.ini",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    ]
    
    for payload in path_traversal_payloads:
        try:
            # Check if we can access sensitive files
            response = client.get(f"{base_url}/api/v1/sessions/{payload}")
            
            # If successful and contains sensitive data, potential path traversal
            if response.status_code == 200 and (
                "root:" in response.text or
                "[fonts]" in response.text
            ):
                findings.append({
                    "type": "Path Traversal",
                    "endpoint": "/api/v1/sessions/{id}",
                    "details": f"Potential path traversal vulnerability with payload: {payload}",
                    "severity": "Critical",
                })
                break
        except Exception as e:
            console.print(f"[yellow]Error checking path traversal: {e}[/yellow]")
    
    # Display findings
    if findings:
        table = Table(title=f"Found {len(findings)} API Security Issues")
        table.add_column("Type")
        table.add_column("Endpoint")
        table.add_column("Details")
        table.add_column("Severity")
        
        for finding in findings:
            table.add_row(
                finding["type"],
                finding["endpoint"],
                finding["details"],
                finding["severity"]
            )
        
        console.print(table)
    else:
        console.print("[green]✓ No API security issues found[/green]")
    
    client.close()
    return findings

def check_data_protection():
    """
    Check data protection measures.
    
    Returns:
        List of findings
    """
    console.print(Panel("[bold]Checking Data Protection[/bold]"))
    
    findings = []
    
    # Check for sensitive data in config files
    console.print("Checking for sensitive data in configuration...")
    
    config_files = [
        Path(__file__).parent.parent.parent / "config" / "config.yaml",
        Path(__file__).parent.parent.parent / ".env",
        Path(__file__).parent.parent.parent / ".env.template",
    ]
    
    sensitive_patterns = [
        r'(?i)password[\s]*=[\s]*["\'][^\'"]+["\']',
        r'(?i)secret[\s]*=[\s]*["\'][^\'"]+["\']',
        r'(?i)api_key[\s]*=[\s]*["\'][^\'"]+["\']',
        r'(?i)token[\s]*=[\s]*["\'][^\'"]+["\']',
    ]
    
    for file_path in config_files:
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for pattern in sensitive_patterns:
                        matches = re.finditer(pattern, content)
                        
                        for match in matches:
                            # Skip template values
                            if "{{" in match.group(0) or "${" in match.group(0):
                                continue
                            
                            # Skip environment variables
                            if "$" in match.group(0) or "%" in match.group(0):
                                continue
                            
                            # Get the line number
                            line_number = content[:match.start()].count('\n') + 1
                            
                            # Get the line content
                            lines = content.split('\n')
                            line_content = lines[line_number - 1] if line_number <= len(lines) else ""
                            
                            # Add finding
                            findings.append({
                                "type": "Sensitive Data Exposure",
                                "file": os.path.relpath(file_path, Path(__file__).parent.parent.parent),
                                "line": line_number,
                                "content": line_content.strip(),
                                "details": "Sensitive data found in configuration file",
                                "severity": "High",
                            })
            except Exception as e:
                console.print(f"[yellow]Error checking file {file_path}: {e}[/yellow]")
    
    # Check for encryption of sensitive data in code
    console.print("Checking for encryption of sensitive data...")
    
    encryption_patterns = [
        (r'(?i)encrypt', r'(?i)(aes|rsa|encrypt)'),
        (r'(?i)password', r'(?i)(hash|encrypt|bcrypt|scrypt|pbkdf2)'),
        (r'(?i)token', r'(?i)(encrypt|jwt|sign)'),
    ]
    
    src_dir = Path(__file__).parent.parent.parent / "src"
    
    if src_dir.exists():
        encryption_found = {pattern[0]: False for pattern in encryption_patterns}
        
        for root, _, files in os.walk(src_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            for data_pattern, encryption_pattern in encryption_patterns:
                                if re.search(data_pattern, content, re.IGNORECASE):
                                    if re.search(encryption_pattern, content, re.IGNORECASE):
                                        encryption_found[data_pattern] = True
                    except Exception as e:
                        console.print(f"[yellow]Error checking file {file_path}: {e}[/yellow]")
        
        for data_pattern, found in encryption_found.items():
            if not found:
                data_type = data_pattern.replace('(?i)', '').replace('\\b', '')
                findings.append({
                    "type": "Insufficient Data Protection",
                    "file": "Multiple files",
                    "line": "N/A",
                    "content": "N/A",
                    "details": f"No evidence of encryption for {data_type}",
                    "severity": "Medium",
                })
    
    # Display findings
    if findings:
        table = Table(title=f"Found {len(findings)} Data Protection Issues")
        table.add_column("Type")
        table.add_column("File")
        table.add_column("Line")
        table.add_column("Content")
        table.add_column("Severity")
        
        for finding in findings:
            table.add_row(
                finding["type"],
                finding["file"],
                str(finding.get("line", "N/A")),
                finding.get("content", "N/A"),
                finding["severity"]
            )
        
        console.print(table)
    else:
        console.print("[green]✓ No data protection issues found[/green]")
    
    return findings

def check_input_validation():
    """
    Check input validation.
    
    Returns:
        List of findings
    """
    console.print(Panel("[bold]Checking Input Validation[/bold]"))
    
    findings = []
    
    # Check for proper input validation in API routes
    console.print("Checking for input validation in API routes...")
    
    router_dir = Path(__file__).parent.parent.parent / "src" / "smart_steps_ai" / "api" / "routers"
    
    if router_dir.exists():
        for file in os.listdir(router_dir):
            if file.endswith('.py'):
                file_path = router_dir / file
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Check for route handlers
                        route_handlers = re.finditer(r'@router\.(get|post|put|patch|delete)\([^)]+\)\s*\n\s*(?:async\s+)?def\s+([^(]+)\(', content)
                        
                        for match in route_handlers:
                            handler_name = match.group(2)
                            
                            # Check if the handler validates input
                            if not re.search(r'raise\s+HTTPException\([^)]*status_code\s*=\s*400', content[match.end():]):
                                findings.append({
                                    "type": "Insufficient Input Validation",
                                    "file": os.path.relpath(file_path, Path(__file__).parent.parent.parent),
                                    "handler": handler_name,
                                    "details": "No input validation (400 error) in API route handler",
                                    "severity": "Medium",
                                })
                except Exception as e:
                    console.print(f"[yellow]Error checking file {file_path}: {e}[/yellow]")
    
    # Check for proper validation in schema definitions
    console.print("Checking for validation in schema definitions...")
    
    schema_dir = Path(__file__).parent.parent.parent / "src" / "smart_steps_ai" / "api" / "schemas"
    
    if schema_dir.exists():
        for file in os.listdir(schema_dir):
            if file.endswith('.py'):
                file_path = schema_dir / file
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Check for schema classes
                        schema_classes = re.finditer(r'class\s+([A-Za-z0-9_]+)\(BaseModel\):', content)
                        
                        for match in schema_classes:
                            class_name = match.group(1)
                            class_body = content[match.end():]
                            
                            # Find the end of the class
                            next_class = re.search(r'class\s+', class_body)
                            if next_class:
                                class_body = class_body[:next_class.start()]
                            
                            # Check if the class has validation
                            has_validation = False
                            
                            # Check for Field validations
                            if re.search(r'Field\([^)]*(?:min_|max_|regex|validator)', class_body):
                                has_validation = True
                            
                            # Check for validator methods
                            if re.search(r'@validator\(', class_body):
                                has_validation = True
                            
                            # Check for root_validator
                            if re.search(r'@root_validator', class_body):
                                has_validation = True
                            
                            if not has_validation and not ("Response" in class_name or "Base" in class_name):
                                findings.append({
                                    "type": "Insufficient Schema Validation",
                                    "file": os.path.relpath(file_path, Path(__file__).parent.parent.parent),
                                    "class": class_name,
                                    "details": "No validation in schema class",
                                    "severity": "Low",
                                })
                except Exception as e:
                    console.print(f"[yellow]Error checking file {file_path}: {e}[/yellow]")
    
    # Display findings
    if findings:
        table = Table(title=f"Found {len(findings)} Input Validation Issues")
        table.add_column("Type")
        table.add_column("File")
        table.add_column("Component")
        table.add_column("Details")
        table.add_column("Severity")
        
        for finding in findings:
            component = finding.get("handler", finding.get("class", "N/A"))
            table.add_row(
                finding["type"],
                finding["file"],
                component,
                finding["details"],
                finding["severity"]
            )
        
        console.print(table)
    else:
        console.print("[green]✓ No input validation issues found[/green]")
    
    return findings
