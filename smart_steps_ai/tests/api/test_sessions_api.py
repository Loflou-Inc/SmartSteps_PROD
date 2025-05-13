"""Test the Sessions API endpoints."""

import os
import sys
import uuid
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .test_api_base import APITestCase


class TestSessionsAPI(APITestCase):
    """Test the Sessions API endpoints."""

    def test_create_session(self):
        """Test creating a session."""
        # Prepare session data
        session_data = {
            "title": "Test Session",
            "client_id": "test-client",
            "persona_id": "jane",  # Assuming 'jane' is a valid persona
            "provider_id": None,
            "metadata": {"purpose": "API test"}
        }
        
        # Send request with admin token
        response = self.client.post("/api/v1/sessions/", json=session_data, headers=self.admin_headers)
        
        # Check response
        self.assertEqual(response.status_code, 201, f"Failed to create session: {response.text}")
        data = response.json()
        
        # Verify response data
        self.assertIn("id", data)
        self.assertEqual(data["title"], session_data["title"])
        self.assertEqual(data["client_id"], session_data["client_id"])
        self.assertEqual(data["persona_id"], session_data["persona_id"])
        
        # Store session ID for later tests
        self.session_id = data["id"]
        
        print(f"Created session with ID {self.session_id}")

    def test_list_sessions(self):
        """Test listing sessions."""
        # First create a session
        self.test_create_session()
        
        # Test listing all sessions
        response = self.client.get("/api/v1/sessions/", headers=self.admin_headers)
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Failed to list sessions: {response.text}")
        data = response.json()
        
        # Verify response data
        self.assertIn("sessions", data)
        self.assertIn("total_count", data)
        self.assertGreaterEqual(data["total_count"], 1)
        
        # Test filtering by client ID
        response = self.client.get(
            "/api/v1/sessions/?client_id=test-client",
            headers=self.admin_headers
        )
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Failed to filter sessions: {response.text}")
        data = response.json()
        
        # Verify response data
        self.assertIn("sessions", data)
        for session in data["sessions"]:
            self.assertEqual(session["client_id"], "test-client")
        
        print(f"Successfully listed {data['total_count']} sessions")

    def test_get_session(self):
        """Test getting a session by ID."""
        # First create a session
        self.test_create_session()
        
        # Get the session
        response = self.client.get(f"/api/v1/sessions/{self.session_id}", headers=self.admin_headers)
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Failed to get session: {response.text}")
        data = response.json()
        
        # Verify response data
        self.assertEqual(data["id"], self.session_id)
        self.assertEqual(data["client_id"], "test-client")
        
        print(f"Successfully retrieved session {self.session_id}")

    def test_update_session(self):
        """Test updating a session."""
        # First create a session
        self.test_create_session()
        
        # Update data
        update_data = {
            "title": "Updated Session Title",
            "status": "active",
            "metadata": {"updated": True, "purpose": "API test"}
        }
        
        # Update the session
        response = self.client.patch(
            f"/api/v1/sessions/{self.session_id}",
            json=update_data,
            headers=self.admin_headers
        )
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Failed to update session: {response.text}")
        data = response.json()
        
        # Verify response data
        self.assertEqual(data["id"], self.session_id)
        self.assertEqual(data["title"], update_data["title"])
        self.assertEqual(data["status"], update_data["status"])
        
        print(f"Successfully updated session {self.session_id}")

    def test_delete_session(self):
        """Test deleting a session."""
        # First create a session
        self.test_create_session()
        
        # Delete the session
        response = self.client.delete(f"/api/v1/sessions/{self.session_id}", headers=self.admin_headers)
        
        # Check response
        self.assertEqual(response.status_code, 204, f"Failed to delete session: {response.text}")
        
        # Verify deletion by trying to get the session
        response = self.client.get(f"/api/v1/sessions/{self.session_id}", headers=self.admin_headers)
        self.assertEqual(response.status_code, 404, "Session still exists after deletion")
        
        print(f"Successfully deleted session {self.session_id}")

    def test_authorization(self):
        """Test authorization for session endpoints."""
        # Prepare session data
        session_data = {
            "title": "Test Session",
            "client_id": "test-client",
            "persona_id": "jane",
            "provider_id": None,
            "metadata": {"purpose": "API test"}
        }
        
        # Test with client token (should fail for create)
        response = self.client.post("/api/v1/sessions/", json=session_data, headers=self.client_headers)
        self.assertNotEqual(response.status_code, 201, "Client should not be able to create sessions")
        
        # Test with therapist token (should succeed for create)
        response = self.client.post("/api/v1/sessions/", json=session_data, headers=self.therapist_headers)
        self.assertEqual(response.status_code, 201, "Therapist should be able to create sessions")
        session_id = response.json()["id"]
        
        # Test with client token (should succeed for read)
        response = self.client.get(f"/api/v1/sessions/{session_id}", headers=self.client_headers)
        self.assertEqual(response.status_code, 200, "Client should be able to read sessions")
        
        # Test with client token (should fail for update)
        update_data = {"title": "Unauthorized Update"}
        response = self.client.patch(
            f"/api/v1/sessions/{session_id}",
            json=update_data,
            headers=self.client_headers
        )
        self.assertNotEqual(response.status_code, 200, "Client should not be able to update sessions")
        
        print("Successfully tested authorization for session endpoints")


if __name__ == "__main__":
    import unittest
    unittest.main()
