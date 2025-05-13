"""
Tests for utility functions.
"""

import unittest
from smart_steps_ai.utils import formatting, validation

class TestFormatting(unittest.TestCase):
    """Tests for the formatting utilities."""
    
    def test_truncate_text(self):
        """Test truncating text."""
        # Test no truncation needed
        self.assertEqual(formatting.truncate_text("Short text", 100), "Short text")
        
        # Test truncation
        self.assertEqual(formatting.truncate_text("This is a long text", 10), "This is...")
        
        # Test custom suffix
        self.assertEqual(formatting.truncate_text("This is a long text", 10, suffix=" [...]"), "This [...]")
    
    def test_format_list(self):
        """Test formatting lists."""
        # Test empty list
        self.assertEqual(formatting.format_list([]), "")
        
        # Test single item
        self.assertEqual(formatting.format_list(["one"]), "one")
        
        # Test two items
        self.assertEqual(formatting.format_list(["one", "two"]), "one and two")
        
        # Test multiple items
        self.assertEqual(formatting.format_list(["one", "two", "three"]), "one, two, and three")
        
        # Test custom conjunction
        self.assertEqual(formatting.format_list(["one", "two", "three"], "or"), "one, two, or three")
    
    def test_format_template(self):
        """Test template formatting."""
        template = "Hello, {{name}}!"
        data = {"name": "World"}
        self.assertEqual(formatting.format_template(template, data), "Hello, World!")
        
        # Test missing variable
        template = "Hello, {{name}}! Welcome to {{place}}."
        data = {"name": "World"}
        self.assertEqual(formatting.format_template(template, data), "Hello, World! Welcome to {{place}}.")
        
        # Test conditional formatting
        template = "Hello, {{if_is_first:new friend|old friend}}!"
        data = {"is_first": True}
        self.assertEqual(formatting.format_template(template, data), "Hello, new friend!")
        
        data = {"is_first": False}
        self.assertEqual(formatting.format_template(template, data), "Hello, old friend!")

class TestValidation(unittest.TestCase):
    """Tests for the validation utilities."""
    
    def test_is_valid_session_id(self):
        """Test session ID validation."""
        # Valid session IDs
        self.assertTrue(validation.is_valid_session_id("session-123"))
        self.assertTrue(validation.is_valid_session_id("abcdef123456"))
        
        # Invalid session IDs
        self.assertFalse(validation.is_valid_session_id(""))
        self.assertFalse(validation.is_valid_session_id("   "))
        self.assertFalse(validation.is_valid_session_id(123))
    
    def test_is_valid_client_id(self):
        """Test client ID validation."""
        # Valid client IDs
        self.assertTrue(validation.is_valid_client_id("client-123"))
        self.assertTrue(validation.is_valid_client_id("abcdef123456"))
        
        # Invalid client IDs
        self.assertFalse(validation.is_valid_client_id(""))
        self.assertFalse(validation.is_valid_client_id("   "))
        self.assertFalse(validation.is_valid_client_id(123))
    
    def test_is_valid_session_type(self):
        """Test session type validation."""
        # Valid session types
        self.assertTrue(validation.is_valid_session_type("therapy"))
        self.assertTrue(validation.is_valid_session_type("assessment"))
        self.assertTrue(validation.is_valid_session_type("initial"))
        
        # Invalid session types
        self.assertFalse(validation.is_valid_session_type(""))
        self.assertFalse(validation.is_valid_session_type("invalid"))
        self.assertFalse(validation.is_valid_session_type(123))
    
    def test_is_valid_analysis_type(self):
        """Test analysis type validation."""
        # Valid analysis types
        self.assertTrue(validation.is_valid_analysis_type("full"))
        self.assertTrue(validation.is_valid_analysis_type("brief"))
        self.assertTrue(validation.is_valid_analysis_type("insights"))
        
        # Invalid analysis types
        self.assertFalse(validation.is_valid_analysis_type(""))
        self.assertFalse(validation.is_valid_analysis_type("invalid"))
        self.assertFalse(validation.is_valid_analysis_type(123))

if __name__ == "__main__":
    unittest.main()
