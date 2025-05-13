"""Test the Authentication API endpoints."""

import os
import sys
import jwt
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi.testclient import TestClient
from src.smart_steps_ai.api.app import app
from src.smart_steps_ai.config import ConfigManager

class TestAuthAPI(unittest.TestCase):
    """Test the Authentication API endpoints."""

    def setUp(self):
        """Set up the test environment."""
        # Create a test client
        self.client = TestClient(app)
        
        # Get configuration
        self.config = ConfigManager()
        
        # Secret key for token verification
        self.secret_key = self.config.get("api.security.secret_key", 
                                        os.environ.get("API_SECRET_KEY", "development_secret_key"))

    def test_login(self):
        """Test login and token generation."""
        # Test valid login
        response = self.client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "password"}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Failed to login: {response.text}")
        data = response.json()
        
        # Verify response data
        self.assertIn("access_token", data)
        self.assertIn("token_type", data)
        self.assertEqual(data["token_type"], "bearer")
        
        # Decode and verify token
        token = data["access_token"]
        decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
        
        self.assertEqual(decoded["sub"], "admin")
        self.assertIn("scopes", decoded)
        
        # Store token for later tests
        self.admin_token = token
        
        # Test invalid credentials
        response = self.client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "wrong_password"}
        )
        
        # Check response
        self.assertEqual(response.status_code, 401, "Invalid credentials should return 401")
        
        print("Successfully tested login endpoint")

    def test_me_endpoint(self):
        """Test the /me endpoint."""
        # First login
        self.test_login()
        
        # Get current user info
        response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Failed to get current user: {response.text}")
        data = response.json()
        
        # Verify response data
        self.assertEqual(data["username"], "admin")
        self.assertIn("scopes", data)
        
        # Test without token
        response = self.client.get("/api/v1/auth/me")
        self.assertEqual(response.status_code, 401, "Missing token should return 401")
        
        # Test with invalid token
        response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        self.assertEqual(response.status_code, 401, "Invalid token should return 401")
        
        print("Successfully tested me endpoint")


if __name__ == "__main__":
    import unittest
    unittest.main()
