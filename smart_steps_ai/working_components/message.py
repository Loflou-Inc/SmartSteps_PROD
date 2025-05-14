"""
Simple message model for mocking
"""

class MessageRole:
    """Message roles for conversation."""
    
    SYSTEM = "system"
    ASSISTANT = "assistant"
    CLIENT = "user"
    INTERNAL = "internal"

class Message:
    """Simple message class for mocking"""
    
    def __init__(self, role, content):
        self.role = role
        self.content = content
