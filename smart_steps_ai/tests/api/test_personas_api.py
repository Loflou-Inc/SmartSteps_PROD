"""Test the Personas API endpoints."""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .test_api_base import APITestCase


class TestPersonasAPI(APITestCase):
    """Test the Personas API endpoints."""

    def test_create_persona(self):
        """Test creating a persona."""
        # Prepare persona data
        persona_data = {
            "name": "test-persona",
            "display_name": "Test Persona",
            "version": "1.0.0",
            "description": "A test persona for API testing",
            "system_prompt": "You are a test persona designed for API testing.",
            "personality_traits": {
                "empathy": 7,
                "analytical": 8,
                "patience": 6,
                "directness": 5,
                "formality": 4,
                "warmth": 7,
                "curiosity": 9,
                "confidence": 8
            },
            "expertise_areas": ["testing", "API", "psychology"],
            "conversation_style": {
                "greeting_format": "Hello {{client_name}}. How can I help you today?",
                "question_frequency": "medium",
                "session_structure": ["introduction", "assessment", "discussion", "summary"],
                "typical_phrases": ["Let's examine this further", "That's an interesting point"]
            },
            "rules": ["Be precise", "Provide examples", "Ask clarifying questions"]
        }
        
        # Send request with admin token
        response = self.client.post("/api/v1/personas/", json=persona_data, headers=self.admin_headers)
        
        # Check response
        self.assertEqual(response.status_code, 201, f"Failed to create persona: {response.text}")
        data = response.json()
        
        # Verify response data
        self.assertIn("id", data)
        self.assertEqual(data["name"], persona_data["name"])
        self.assertEqual(data["display_name"], persona_data["display_name"])
        
        # Store persona ID for later tests
        self.persona_id = data["id"]
        
        print(f"Created persona with ID {self.persona_id}")

    def test_list_personas(self):
        """Test listing personas."""
        # First create a persona
        self.test_create_persona()
        
        # Test listing all personas
        response = self.client.get("/api/v1/personas/", headers=self.admin_headers)
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Failed to list personas: {response.text}")
        data = response.json()
        
        # Verify response data
        self.assertIn("personas", data)
        self.assertIn("total_count", data)
        self.assertGreaterEqual(data["total_count"], 1)
        
        # Test filtering by expertise
        response = self.client.get(
            "/api/v1/personas/?expertise=psychology",
            headers=self.admin_headers
        )
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Failed to filter personas: {response.text}")
        data = response.json()
        
        # Verify response data
        self.assertIn("personas", data)
        self.assertGreaterEqual(len(data["personas"]), 1)
        
        print(f"Successfully listed {data['total_count']} personas")

    def test_get_persona(self):
        """Test getting a persona by ID."""
        # First create a persona
        self.test_create_persona()
        
        # Get the persona
        response = self.client.get(f"/api/v1/personas/{self.persona_id}", headers=self.admin_headers)
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Failed to get persona: {response.text}")
        data = response.json()
        
        # Verify response data
        self.assertEqual(data["id"], self.persona_id)
        self.assertEqual(data["name"], "test-persona")
        
        print(f"Successfully retrieved persona {self.persona_id}")

    def test_update_persona(self):
        """Test updating a persona."""
        # First create a persona
        self.test_create_persona()
        
        # Update data
        update_data = {
            "display_name": "Updated Test Persona",
            "description": "An updated test persona for API testing",
            "expertise": ["testing", "API", "psychology", "counseling"],
            "traits": {
                "empathy": 8,
                "analytical": 8,
                "patience": 7,
                "directness": 6,
                "formality": 5,
                "warmth": 8,
                "curiosity": 9,
                "confidence": 8
            }
        }
        
        # Update the persona
        response = self.client.patch(
            f"/api/v1/personas/{self.persona_id}",
            json=update_data,
            headers=self.admin_headers
        )
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Failed to update persona: {response.text}")
        data = response.json()
        
        # Verify response data
        self.assertEqual(data["id"], self.persona_id)
        self.assertEqual(data["display_name"], update_data["display_name"])
        self.assertEqual(data["description"], update_data["description"])
        
        print(f"Successfully updated persona {self.persona_id}")

    def test_validate_persona(self):
        """Test validating a persona."""
        # First create a persona
        self.test_create_persona()
        
        # Validate the persona
        response = self.client.post(
            f"/api/v1/personas/{self.persona_id}/validate",
            headers=self.admin_headers
        )
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Failed to validate persona: {response.text}")
        data = response.json()
        
        # Verify response data
        self.assertIn("persona_id", data)
        self.assertEqual(data["persona_id"], self.persona_id)
        self.assertIn("is_valid", data)
        
        print(f"Successfully validated persona {self.persona_id}: {data['is_valid']}")

    def test_import_export_persona(self):
        """Test importing and exporting a persona."""
        # First create a persona
        self.test_create_persona()
        
        # Export the persona
        response = self.client.get(
            f"/api/v1/personas/{self.persona_id}/export",
            headers=self.admin_headers
        )
        
        # Check response
        self.assertEqual(response.status_code, 200, f"Failed to export persona: {response.text}")
        export_data = response.json()
        
        # Create a temporary file with the exported data
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp.write(json.dumps(export_data).encode('utf-8'))
            tmp_path = tmp.name
        
        # Import the persona with a different name
        export_data["name"] = "imported-persona"
        
        with open(tmp_path, "rb") as f:
            response = self.client.post(
                "/api/v1/personas/import",
                files={"file": ("persona.json", f, "application/json")},
                headers=self.admin_headers
            )
        
        # Clean up the temporary file
        os.unlink(tmp_path)
        
        # Check response
        self.assertEqual(response.status_code, 201, f"Failed to import persona: {response.text}")
        data = response.json()
        
        # Verify response data
        self.assertIn("id", data)
        self.assertEqual(data["name"], "imported-persona")
        
        print(f"Successfully imported persona with ID {data['id']}")

    def test_delete_persona(self):
        """Test deleting a persona."""
        # First create a persona
        self.test_create_persona()
        
        # Delete the persona
        response = self.client.delete(f"/api/v1/personas/{self.persona_id}", headers=self.admin_headers)
        
        # Check response
        self.assertEqual(response.status_code, 204, f"Failed to delete persona: {response.text}")
        
        # Verify deletion by trying to get the persona
        response = self.client.get(f"/api/v1/personas/{self.persona_id}", headers=self.admin_headers)
        self.assertEqual(response.status_code, 404, "Persona still exists after deletion")
        
        print(f"Successfully deleted persona {self.persona_id}")


if __name__ == "__main__":
    import unittest
    unittest.main()
