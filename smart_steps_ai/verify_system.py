#!/usr/bin/env python
"""
Smart Steps AI End-to-End Verification Script

This script performs comprehensive testing of the Smart Steps AI system:
- Verifies API server functionality and authentication
- Tests monitoring system metrics collection
- Validates deployment configurations
- Ensures proper interaction between all components

Usage:
    python verify_system.py --all
    python verify_system.py --api-auth
    python verify_system.py --monitoring
    python verify_system.py --deployment

Author: Smart Steps Team
Date: May 13, 2025
"""

import argparse
import datetime
import json
import logging
import os
import platform
import re
import requests
import socket
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("verification.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("verification")

# Constants
ROOT_DIR = Path(__file__).parent.absolute()
CONFIG_DIR = ROOT_DIR / "config"
DEPLOYMENT_DIR = ROOT_DIR / "deployment"
DOCKER_COMPOSE_FILE = DEPLOYMENT_DIR / "docker-compose.yml"
ENV_FILE = ROOT_DIR / ".env"
TEMP_DIR = ROOT_DIR / "temp" / "verification"

# Create temp directory
os.makedirs(TEMP_DIR, exist_ok=True)

# Test settings
DEFAULT_API_URL = "http://localhost:9500"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "password"
DEFAULT_TIMEOUT = 10  # seconds

class SystemVerifier:
    """Main class for system verification."""
    
    def __init__(self, api_url: str = DEFAULT_API_URL, 
                 username: str = DEFAULT_USERNAME,
                 password: str = DEFAULT_PASSWORD):
        """
        Initialize the verifier.
        
        Args:
            api_url: URL of the API server
            username: Username for authentication
            password: Password for authentication
        """
        self.api_url = api_url
        self.username = username
        self.password = password
        self.access_token = None
        self.session = requests.Session()
    
    def verify_all(self) -> Dict[str, Any]:
        """
        Run all verification tests.
        
        Returns:
            Results of all verification tests
        """
        results = {
            "api_auth": self.verify_api_auth(),
            "monitoring": self.verify_monitoring(),
            "deployment": self.verify_deployment(),
            "timestamp": datetime.datetime.now().isoformat(),
            "system_info": self._get_system_info()
        }
        
        # Calculate overall status
        all_successful = all(
            result.get("success", False) 
            for result in [results["api_auth"], results["monitoring"], results["deployment"]]
        )
        
        results["success"] = all_successful
        results["summary"] = "All tests passed!" if all_successful else "Some tests failed. Check detailed results."
        
        # Print summary
        self._print_results_summary(results)
        
        return results
    
    def verify_api_auth(self) -> Dict[str, Any]:
        """
        Verify API authentication and basic functionality.
        
        Returns:
            Results of API authentication verification
        """
        logger.info("Starting API authentication verification")
        
        results = {
            "tests": [],
            "success": False,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        try:
            # Test 1: Check API health endpoint
            test_result = self._test_api_health()
            results["tests"].append(test_result)
            
            # Test 2: Authenticate with the API
            test_result = self._test_api_authentication()
            results["tests"].append(test_result)
            
            if test_result["success"]:
                # Successfully authenticated, store token for subsequent tests
                self.access_token = test_result["details"]["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
            
            # Test 3: Access protected endpoint
            test_result = self._test_protected_endpoint()
            results["tests"].append(test_result)
            
            # Test 4: Create and retrieve a session
            test_result = self._test_session_creation()
            results["tests"].append(test_result)
            
            # Test 5: Test session message exchange
            if test_result["success"] and "session_id" in test_result["details"]:
                session_id = test_result["details"]["session_id"]
                test_result = self._test_message_exchange(session_id)
                results["tests"].append(test_result)
            
            # Test 6: Test persona listing
            test_result = self._test_persona_listing()
            results["tests"].append(test_result)
            
            # Calculate overall success
            results["success"] = all(test["success"] for test in results["tests"])
            
            logger.info(f"API authentication verification {'successful' if results['success'] else 'failed'}")
        except Exception as e:
            logger.error(f"Error during API authentication verification: {str(e)}")
            results["error"] = str(e)
            results["success"] = False
        
        return results
    
    def verify_monitoring(self) -> Dict[str, Any]:
        """
        Verify monitoring system functionality.
        
        Returns:
            Results of monitoring verification
        """
        logger.info("Starting monitoring system verification")
        
        results = {
            "tests": [],
            "success": False,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        try:
            # Test 1: Check monitoring health endpoint
            test_result = self._test_monitoring_health()
            results["tests"].append(test_result)
            
            # Test 2: Check metrics endpoint
            test_result = self._test_metrics_endpoint()
            results["tests"].append(test_result)
            
            # Test 3: Test cache clearing
            test_result = self._test_cache_clearing()
            results["tests"].append(test_result)
            
            # Test 4: Test maintenance endpoint
            test_result = self._test_maintenance_endpoint()
            results["tests"].append(test_result)
            
            # Calculate overall success
            results["success"] = all(test["success"] for test in results["tests"])
            
            logger.info(f"Monitoring system verification {'successful' if results['success'] else 'failed'}")
        except Exception as e:
            logger.error(f"Error during monitoring system verification: {str(e)}")
            results["error"] = str(e)
            results["success"] = False
        
        return results
    
    def verify_deployment(self) -> Dict[str, Any]:
        """
        Verify deployment configurations.
        
        Returns:
            Results of deployment verification
        """
        logger.info("Starting deployment verification")
        
        results = {
            "tests": [],
            "success": False,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        try:
            # Test 1: Verify Docker configurations
            test_result = self._test_docker_config()
            results["tests"].append(test_result)
            
            # Test 2: Verify environment configurations
            test_result = self._test_env_configs()
            results["tests"].append(test_result)
            
            # Test 3: Verify release management
            test_result = self._test_release_management()
            results["tests"].append(test_result)
            
            # Test 4: Verify monitoring config
            test_result = self._test_monitoring_config()
            results["tests"].append(test_result)
            
            # Test 5: Verify backup system
            test_result = self._test_backup_system()
            results["tests"].append(test_result)
            
            # Calculate overall success
            results["success"] = all(test["success"] for test in results["tests"])
            
            logger.info(f"Deployment verification {'successful' if results['success'] else 'failed'}")
        except Exception as e:
            logger.error(f"Error during deployment verification: {str(e)}")
            results["error"] = str(e)
            results["success"] = False
        
        return results
    
    def _test_api_health(self) -> Dict[str, Any]:
        """Test API health endpoint."""
        test_name = "API Health Check"
        logger.info(f"Running test: {test_name}")
        
        try:
            url = f"{self.api_url}/health"
            response = self.session.get(url, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                logger.info(f"Test {test_name} passed")
                return {
                    "name": test_name,
                    "success": True,
                    "details": {
                        "status_code": response.status_code,
                        "response": response.json()
                    }
                }
            else:
                logger.warning(f"Test {test_name} failed: Unexpected status code {response.status_code}")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "status_code": response.status_code,
                        "response": response.text
                    }
                }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _test_api_authentication(self) -> Dict[str, Any]:
        """Test API authentication."""
        test_name = "API Authentication"
        logger.info(f"Running test: {test_name}")
        
        try:
            url = f"{self.api_url}/api/v1/auth/token"
            response = self.session.post(
                url, 
                data={
                    "username": self.username,
                    "password": self.password
                },
                timeout=DEFAULT_TIMEOUT
            )
            
            if response.status_code == 200:
                token_data = response.json()
                logger.info(f"Test {test_name} passed")
                return {
                    "name": test_name,
                    "success": True,
                    "details": {
                        "status_code": response.status_code,
                        "access_token": token_data.get("access_token"),
                        "token_type": token_data.get("token_type")
                    }
                }
            else:
                logger.warning(f"Test {test_name} failed: Unexpected status code {response.status_code}")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "status_code": response.status_code,
                        "response": response.text
                    }
                }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _test_protected_endpoint(self) -> Dict[str, Any]:
        """Test access to a protected endpoint."""
        test_name = "Protected Endpoint Access"
        logger.info(f"Running test: {test_name}")
        
        try:
            url = f"{self.api_url}/api/v1/auth/me"
            response = self.session.get(url, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Test {test_name} passed")
                return {
                    "name": test_name,
                    "success": True,
                    "details": {
                        "status_code": response.status_code,
                        "user": user_data
                    }
                }
            else:
                logger.warning(f"Test {test_name} failed: Unexpected status code {response.status_code}")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "status_code": response.status_code,
                        "response": response.text
                    }
                }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _test_session_creation(self) -> Dict[str, Any]:
        """Test creation of a session."""
        test_name = "Session Creation"
        logger.info(f"Running test: {test_name}")
        
        try:
            url = f"{self.api_url}/api/v1/sessions"
            response = self.session.post(url, json={
                "client_id": "test_client",
                "persona_id": "test_therapist",
                "metadata": {
                    "client_name": "Test Client",
                    "therapist_name": "Test Therapist",
                    "session_type": "verification"
                }
            }, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 201:
                session_data = response.json()
                logger.info(f"Test {test_name} passed")
                return {
                    "name": test_name,
                    "success": True,
                    "details": {
                        "status_code": response.status_code,
                        "session_id": session_data.get("id"),
                        "client_id": session_data.get("client_id"),
                        "persona_id": session_data.get("persona_id")
                    }
                }
            else:
                logger.warning(f"Test {test_name} failed: Unexpected status code {response.status_code}")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "status_code": response.status_code,
                        "response": response.text
                    }
                }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _test_message_exchange(self, session_id: str) -> Dict[str, Any]:
        """Test message exchange in a session."""
        test_name = "Message Exchange"
        logger.info(f"Running test: {test_name}")
        
        try:
            url = f"{self.api_url}/api/v1/sessions/{session_id}/messages"
            
            # Send a message
            send_response = self.session.post(url, json={
                "role": "client",
                "content": "Hello, this is a test message for verification."
            }, timeout=DEFAULT_TIMEOUT)
            
            if send_response.status_code != 201:
                logger.warning(f"Test {test_name} failed: Unexpected status code {send_response.status_code}")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "status_code": send_response.status_code,
                        "response": send_response.text
                    }
                }
            
            # Get messages
            get_response = self.session.get(url, timeout=DEFAULT_TIMEOUT)
            
            if get_response.status_code == 200:
                messages = get_response.json()
                
                # Check if we received at least one message back from the persona
                persona_messages = [msg for msg in messages if msg.get("role") == "assistant"]
                
                if persona_messages:
                    logger.info(f"Test {test_name} passed")
                    return {
                        "name": test_name,
                        "success": True,
                        "details": {
                            "status_code": get_response.status_code,
                            "message_count": len(messages),
                            "persona_message_count": len(persona_messages),
                            "first_response": persona_messages[0].get("content") if persona_messages else None
                        }
                    }
                else:
                    logger.warning(f"Test {test_name} failed: No persona messages received")
                    return {
                        "name": test_name,
                        "success": False,
                        "details": {
                            "status_code": get_response.status_code,
                            "message_count": len(messages),
                            "persona_message_count": 0
                        }
                    }
            else:
                logger.warning(f"Test {test_name} failed: Unexpected status code {get_response.status_code}")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "status_code": get_response.status_code,
                        "response": get_response.text
                    }
                }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _test_persona_listing(self) -> Dict[str, Any]:
        """Test listing of available personas."""
        test_name = "Persona Listing"
        logger.info(f"Running test: {test_name}")
        
        try:
            url = f"{self.api_url}/api/v1/personas"
            response = self.session.get(url, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                personas = response.json()
                logger.info(f"Test {test_name} passed")
                return {
                    "name": test_name,
                    "success": True,
                    "details": {
                        "status_code": response.status_code,
                        "persona_count": len(personas),
                        "personas": [p.get("id") for p in personas]
                    }
                }
            else:
                logger.warning(f"Test {test_name} failed: Unexpected status code {response.status_code}")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "status_code": response.status_code,
                        "response": response.text
                    }
                }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _test_monitoring_health(self) -> Dict[str, Any]:
        """Test monitoring health endpoint."""
        test_name = "Monitoring Health Check"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Ensure we have an auth token
            if not self.access_token:
                auth_result = self._test_api_authentication()
                if auth_result["success"]:
                    self.access_token = auth_result["details"]["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.access_token}"
                    })
                else:
                    logger.warning("Authentication failed, cannot proceed with monitoring tests")
                    return {
                        "name": test_name,
                        "success": False,
                        "error": "Authentication required for monitoring tests"
                    }
            
            url = f"{self.api_url}/api/v1/admin/health"
            response = self.session.get(url, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"Test {test_name} passed")
                return {
                    "name": test_name,
                    "success": True,
                    "details": {
                        "status_code": response.status_code,
                        "status": health_data.get("status"),
                        "version": health_data.get("version"),
                        "uptime": health_data.get("uptime")
                    }
                }
            else:
                logger.warning(f"Test {test_name} failed: Unexpected status code {response.status_code}")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "status_code": response.status_code,
                        "response": response.text
                    }
                }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _test_metrics_endpoint(self) -> Dict[str, Any]:
        """Test metrics endpoint."""
        test_name = "Metrics Endpoint"
        logger.info(f"Running test: {test_name}")
        
        try:
            url = f"{self.api_url}/api/v1/admin/metrics"
            response = self.session.get(url, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                metrics_data = response.json()
                
                # Verify metrics structure
                required_sections = ["cpu", "memory", "disk", "requests", "timestamp"]
                missing_sections = [section for section in required_sections if section not in metrics_data]
                
                if missing_sections:
                    logger.warning(f"Test {test_name} failed: Missing metrics sections: {', '.join(missing_sections)}")
                    return {
                        "name": test_name,
                        "success": False,
                        "details": {
                            "status_code": response.status_code,
                            "missing_sections": missing_sections
                        }
                    }
                
                logger.info(f"Test {test_name} passed")
                return {
                    "name": test_name,
                    "success": True,
                    "details": {
                        "status_code": response.status_code,
                        "metrics_sections": list(metrics_data.keys()),
                        "cpu_percent": metrics_data.get("cpu", {}).get("percent"),
                        "memory_percent": metrics_data.get("memory", {}).get("percent"),
                        "disk_percent": metrics_data.get("disk", {}).get("percent")
                    }
                }
            else:
                logger.warning(f"Test {test_name} failed: Unexpected status code {response.status_code}")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "status_code": response.status_code,
                        "response": response.text
                    }
                }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _test_cache_clearing(self) -> Dict[str, Any]:
        """Test cache clearing endpoint."""
        test_name = "Cache Clearing"
        logger.info(f"Running test: {test_name}")
        
        try:
            url = f"{self.api_url}/api/v1/admin/clear-cache"
            response = self.session.post(url, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                cache_data = response.json()
                logger.info(f"Test {test_name} passed")
                return {
                    "name": test_name,
                    "success": True,
                    "details": {
                        "status_code": response.status_code,
                        "success": cache_data.get("success"),
                        "details": cache_data.get("details")
                    }
                }
            else:
                logger.warning(f"Test {test_name} failed: Unexpected status code {response.status_code}")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "status_code": response.status_code,
                        "response": response.text
                    }
                }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _test_maintenance_endpoint(self) -> Dict[str, Any]:
        """Test maintenance endpoint."""
        test_name = "Maintenance Endpoint"
        logger.info(f"Running test: {test_name}")
        
        try:
            url = f"{self.api_url}/api/v1/admin/maintenance"
            response = self.session.post(url, json={
                "tasks": ["clean_temp_files"]
            }, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                maintenance_data = response.json()
                logger.info(f"Test {test_name} passed")
                return {
                    "name": test_name,
                    "success": True,
                    "details": {
                        "status_code": response.status_code,
                        "success": maintenance_data.get("success"),
                        "results": maintenance_data.get("results")
                    }
                }
            else:
                logger.warning(f"Test {test_name} failed: Unexpected status code {response.status_code}")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "status_code": response.status_code,
                        "response": response.text
                    }
                }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _test_docker_config(self) -> Dict[str, Any]:
        """Test Docker configuration files."""
        test_name = "Docker Configuration"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Check if Dockerfile exists
            dockerfile = DEPLOYMENT_DIR / "Dockerfile"
            dockerfile_monitoring = DEPLOYMENT_DIR / "Dockerfile.monitoring"
            docker_compose = DOCKER_COMPOSE_FILE
            
            missing_files = []
            if not dockerfile.exists():
                missing_files.append("Dockerfile")
            if not dockerfile_monitoring.exists():
                missing_files.append("Dockerfile.monitoring")
            if not docker_compose.exists():
                missing_files.append("docker-compose.yml")
            
            if missing_files:
                logger.warning(f"Test {test_name} failed: Missing files: {', '.join(missing_files)}")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "missing_files": missing_files
                    }
                }
            
            # Verify Docker Compose file structure
            with open(docker_compose, 'r') as f:
                try:
                    # Just check if it's valid YAML
                    import yaml
                    docker_compose_data = yaml.safe_load(f)
                    
                    # Check for required services
                    required_services = ["api", "monitoring"]
                    services = docker_compose_data.get("services", {})
                    missing_services = [service for service in required_services if service not in services]
                    
                    if missing_services:
                        logger.warning(f"Test {test_name} failed: Missing services: {', '.join(missing_services)}")
                        return {
                            "name": test_name,
                            "success": False,
                            "details": {
                                "missing_services": missing_services
                            }
                        }
                    
                    logger.info(f"Test {test_name} passed")
                    return {
                        "name": test_name,
                        "success": True,
                        "details": {
                            "dockerfile_exists": True,
                            "dockerfile_monitoring_exists": True,
                            "docker_compose_exists": True,
                            "services": list(services.keys())
                        }
                    }
                except yaml.YAMLError:
                    logger.warning(f"Test {test_name} failed: Invalid YAML in docker-compose.yml")
                    return {
                        "name": test_name,
                        "success": False,
                        "details": {
                            "error": "Invalid YAML in docker-compose.yml"
                        }
                    }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _test_env_configs(self) -> Dict[str, Any]:
        """Test environment configuration files."""
        test_name = "Environment Configurations"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Check for environment files
            production_env = DEPLOYMENT_DIR / "config" / "production.env"
            development_env = DEPLOYMENT_DIR / "config" / "development.env"
            testing_env = DEPLOYMENT_DIR / "config" / "testing.env"
            
            missing_files = []
            if not production_env.exists():
                missing_files.append("production.env")
            if not development_env.exists():
                missing_files.append("development.env")
            if not testing_env.exists():
                missing_files.append("testing.env")
            
            if missing_files:
                logger.warning(f"Test {test_name} failed: Missing files: {', '.join(missing_files)}")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "missing_files": missing_files
                    }
                }
            
            # Check that environment files contain required settings
            required_settings = [
                "API_SECRET_KEY",
                "DATABASE_TYPE",
                "DEFAULT_PROVIDER",
                "ENVIRONMENT"
            ]
            
            # Check production.env
            with open(production_env, 'r') as f:
                production_content = f.read()
                missing_settings = []
                
                for setting in required_settings:
                    if not re.search(fr'{setting}\s*=', production_content):
                        missing_settings.append(setting)
                
                if missing_settings:
                    logger.warning(f"Test {test_name} failed: Missing settings in production.env: {', '.join(missing_settings)}")
                    return {
                        "name": test_name,
                        "success": False,
                        "details": {
                            "missing_settings": missing_settings
                        }
                    }
            
            logger.info(f"Test {test_name} passed")
            return {
                "name": test_name,
                "success": True,
                "details": {
                    "production_env_exists": True,
                    "development_env_exists": True,
                    "testing_env_exists": True,
                    "settings_verified": True
                }
            }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _test_release_management(self) -> Dict[str, Any]:
        """Test release management script."""
        test_name = "Release Management"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Check if release_manager.py exists
            release_manager = DEPLOYMENT_DIR / "release_manager.py"
            
            if not release_manager.exists():
                logger.warning(f"Test {test_name} failed: release_manager.py not found")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "error": "release_manager.py not found"
                    }
                }
            
            # Verify script is executable
            is_executable = os.access(release_manager, os.X_OK)
            
            if not is_executable and platform.system() != "Windows":
                logger.warning(f"Test {test_name} failed: release_manager.py is not executable")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "error": "release_manager.py is not executable"
                    }
                }
            
            # Verify script is valid Python
            with open(release_manager, 'r') as f:
                script_content = f.read()
                
                try:
                    compile(script_content, release_manager, 'exec')
                except SyntaxError as e:
                    logger.warning(f"Test {test_name} failed: release_manager.py has syntax errors: {str(e)}")
                    return {
                        "name": test_name,
                        "success": False,
                        "details": {
                            "error": f"Syntax error in release_manager.py: {str(e)}"
                        }
                    }
            
            logger.info(f"Test {test_name} passed")
            return {
                "name": test_name,
                "success": True,
                "details": {
                    "release_manager_exists": True,
                    "is_executable": is_executable or platform.system() == "Windows",
                    "is_valid_python": True
                }
            }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _test_monitoring_config(self) -> Dict[str, Any]:
        """Test monitoring configuration file."""
        test_name = "Monitoring Configuration"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Check if monitoring.yaml exists
            monitoring_config = DEPLOYMENT_DIR / "config" / "monitoring.yaml"
            
            if not monitoring_config.exists():
                logger.warning(f"Test {test_name} failed: monitoring.yaml not found")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "error": "monitoring.yaml not found"
                    }
                }
            
            # Verify file is valid YAML
            with open(monitoring_config, 'r') as f:
                try:
                    import yaml
                    config_data = yaml.safe_load(f)
                    
                    # Check for required sections
                    required_sections = ["monitoring", "api", "maintenance"]
                    missing_sections = [section for section in required_sections if section not in config_data]
                    
                    if missing_sections:
                        logger.warning(f"Test {test_name} failed: Missing sections in monitoring.yaml: {', '.join(missing_sections)}")
                        return {
                            "name": test_name,
                            "success": False,
                            "details": {
                                "missing_sections": missing_sections
                            }
                        }
                    
                    logger.info(f"Test {test_name} passed")
                    return {
                        "name": test_name,
                        "success": True,
                        "details": {
                            "monitoring_config_exists": True,
                            "is_valid_yaml": True,
                            "sections": list(config_data.keys())
                        }
                    }
                except yaml.YAMLError:
                    logger.warning(f"Test {test_name} failed: Invalid YAML in monitoring.yaml")
                    return {
                        "name": test_name,
                        "success": False,
                        "details": {
                            "error": "Invalid YAML in monitoring.yaml"
                        }
                    }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _test_backup_system(self) -> Dict[str, Any]:
        """Test backup system script."""
        test_name = "Backup System"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Check if auto_update.py exists
            auto_update = DEPLOYMENT_DIR / "auto_update.py"
            
            if not auto_update.exists():
                logger.warning(f"Test {test_name} failed: auto_update.py not found")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "error": "auto_update.py not found"
                    }
                }
            
            # Verify script is executable
            is_executable = os.access(auto_update, os.X_OK)
            
            if not is_executable and platform.system() != "Windows":
                logger.warning(f"Test {test_name} failed: auto_update.py is not executable")
                return {
                    "name": test_name,
                    "success": False,
                    "details": {
                        "error": "auto_update.py is not executable"
                    }
                }
            
            # Verify script is valid Python
            with open(auto_update, 'r') as f:
                script_content = f.read()
                
                try:
                    compile(script_content, auto_update, 'exec')
                except SyntaxError as e:
                    logger.warning(f"Test {test_name} failed: auto_update.py has syntax errors: {str(e)}")
                    return {
                        "name": test_name,
                        "success": False,
                        "details": {
                            "error": f"Syntax error in auto_update.py: {str(e)}"
                        }
                    }
            
            logger.info(f"Test {test_name} passed")
            return {
                "name": test_name,
                "success": True,
                "details": {
                    "auto_update_exists": True,
                    "is_executable": is_executable or platform.system() == "Windows",
                    "is_valid_python": True
                }
            }
        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            return {
                "name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        try:
            import psutil
            import platform
            
            # Get CPU info
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "current_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else "N/A",
                "percent_used": psutil.cpu_percent(interval=1)
            }
            
            # Get memory info
            memory = psutil.virtual_memory()
            memory_info = {
                "total": memory.total,
                "available": memory.available,
                "percent_used": memory.percent,
                "total_gb": memory.total / (1024 ** 3),
                "available_gb": memory.available / (1024 ** 3)
            }
            
            # Get disk info
            disk = psutil.disk_usage('/')
            disk_info = {
                "total": disk.total,
                "free": disk.free,
                "percent_used": disk.percent,
                "total_gb": disk.total / (1024 ** 3),
                "free_gb": disk.free / (1024 ** 3)
            }
            
            # Get Python info
            python_info = {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
                "compiler": platform.python_compiler()
            }
            
            # Get platform info
            platform_info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
            
            # Get network info
            network_info = {
                "hostname": socket.gethostname(),
                "ip_address": socket.gethostbyname(socket.gethostname()),
                "interfaces": list(psutil.net_if_addrs().keys())
            }
            
            return {
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info,
                "python": python_info,
                "platform": platform_info,
                "network": network_info
            }
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _print_results_summary(self, results: Dict[str, Any]):
        """Print a summary of the verification results."""
        print("\n" + "=" * 50)
        print("VERIFICATION RESULTS SUMMARY")
        print("=" * 50)
        
        # Overall result
        success = results.get("success", False)
        print(f"\nOverall Result: {'PASSED' if success else 'FAILED'}")
        print(f"Summary: {results.get('summary', 'N/A')}")
        
        # API Auth tests
        api_auth = results.get("api_auth", {})
        api_tests = api_auth.get("tests", [])
        api_success_count = sum(1 for test in api_tests if test.get("success", False))
        print(f"\nAPI Authentication Tests: {api_success_count}/{len(api_tests)} passed")
        
        for test in api_tests:
            status = "✅" if test.get("success", False) else "❌"
            print(f"  {status} {test.get('name', 'Unknown Test')}")
        
        # Monitoring tests
        monitoring = results.get("monitoring", {})
        monitoring_tests = monitoring.get("tests", [])
        monitoring_success_count = sum(1 for test in monitoring_tests if test.get("success", False))
        print(f"\nMonitoring Tests: {monitoring_success_count}/{len(monitoring_tests)} passed")
        
        for test in monitoring_tests:
            status = "✅" if test.get("success", False) else "❌"
            print(f"  {status} {test.get('name', 'Unknown Test')}")
        
        # Deployment tests
        deployment = results.get("deployment", {})
        deployment_tests = deployment.get("tests", [])
        deployment_success_count = sum(1 for test in deployment_tests if test.get("success", False))
        print(f"\nDeployment Tests: {deployment_success_count}/{len(deployment_tests)} passed")
        
        for test in deployment_tests:
            status = "✅" if test.get("success", False) else "❌"
            print(f"  {status} {test.get('name', 'Unknown Test')}")
        
        print("\n" + "=" * 50)
        print(f"Test completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50 + "\n")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Smart Steps AI End-to-End Verification")
    
    # Add arguments for different test types
    parser.add_argument("--all", action="store_true", help="Run all verification tests")
    parser.add_argument("--api-auth", action="store_true", help="Test API authentication and functionality")
    parser.add_argument("--monitoring", action="store_true", help="Test monitoring system")
    parser.add_argument("--deployment", action="store_true", help="Test deployment configurations")
    
    # Add connection arguments
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="URL of the API server")
    parser.add_argument("--username", default=DEFAULT_USERNAME, help="Username for authentication")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Password for authentication")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create verifier
    verifier = SystemVerifier(args.api_url, args.username, args.password)
    
    # Run tests based on arguments
    if args.all:
        results = verifier.verify_all()
    elif args.api_auth:
        results = verifier.verify_api_auth()
        verifier._print_results_summary({"api_auth": results, "success": results.get("success", False)})
    elif args.monitoring:
        results = verifier.verify_monitoring()
        verifier._print_results_summary({"monitoring": results, "success": results.get("success", False)})
    elif args.deployment:
        results = verifier.verify_deployment()
        verifier._print_results_summary({"deployment": results, "success": results.get("success", False)})
    else:
        # No specific tests specified, run all
        results = verifier.verify_all()
    
    # Save results to file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = TEMP_DIR / f"verification_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {results_file}")
    
    # Exit with appropriate status code
    if results.get("success", False):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
