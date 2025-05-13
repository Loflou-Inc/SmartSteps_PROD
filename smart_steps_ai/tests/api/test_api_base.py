"""Base test case for API tests."""

import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi.testclient import TestClient
from src.smart_steps_ai.api.app import app
from src.smart_steps_ai.api.security.auth import create_access_token
from src.smart_steps_ai.config import ConfigManager


class APITestCase(unittest.TestCase):
    """Base test case for API tests."""

    def setUp(self):
        """Set up the test environment."""
        # Create a test client
        self.client = TestClient(app)
        
        # Create access tokens for different roles
        self.admin_token = create_access_token(
            data={"sub": "admin", "scopes": ["sessions:read", "sessions:write", "personas:read", "personas:write", "analysis:read", "analysis:write"]},
            config_manager=ConfigManager()
        )
        
        self.therapist_token = create_access_token(
            data={"sub": "therapist", "scopes": ["sessions:read", "sessions:write", "personas:read", "analysis:read"]},
            config_manager=ConfigManager()
        )
        
        self.client_token = create_access_token(
            data={"sub": "client", "scopes": ["sessions:read"]},
            config_manager=ConfigManager()
        )
        
        # Headers for authenticated requests
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        self.therapist_headers = {"Authorization": f"Bearer {self.therapist_token}"}
        self.client_headers = {"Authorization": f"Bearer {self.client_token}"}
