"""
Claude Memory System integration for the Smart Steps AI module.

This module provides integration with the Claude Memory System for
persistent memory across conversations.
"""

import os
import sys
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime

class ClaudeMemoryIntegration:
    """
    Integration with Claude Memory System.
    
    This class provides methods to interact with the Claude Memory
    System for persistent memory across conversations.
    """
    
    def __init__(
        self,
        memory_path: Optional[str] = None,
        integration_script: Optional[str] = None
    ):
        """
        Initialize the Claude Memory integration.
        
        Args:
            memory_path: Path to the Claude Memory System
            integration_script: Path to the integration script
        """
        # Set default memory system path
        if not memory_path:
            # Check common locations
            potential_paths = [
                r"G:\My Drive\Deftech\SmartSteps\claude-memory",
                r"C:\Users\user\Documents\claude-memory",
                os.path.join(os.path.expanduser("~"), "claude-memory")
            ]
            
            for path in potential_paths:
                if os.path.exists(path):
                    memory_path = path
                    break
        
        self.memory_path = memory_path
        
        if not integration_script and memory_path:
            # Find integration script
            default_script = os.path.join(memory_path, "claude_dc_integration.py")
            if os.path.exists(default_script):
                integration_script = default_script
        
        self.integration_script = integration_script
        self.enabled = memory_path is not None and integration_script is not None
    
    def is_available(self) -> bool:
        """
        Check if the Claude Memory System is available.
        
        Returns:
            True if available, False otherwise
        """
        if not self.enabled:
            return False
        
        # Try to list memories as a test
        try:
            result = self.run_memory_command("list")
            return result is not None
        except Exception:
            return False
    
    def run_memory_command(self, command: str, arg: Optional[str] = None) -> Optional[str]:
        """
        Run a Claude Memory System command.
        
        Args:
            command: Command to run (remember, recall, context, list)
            arg: Optional argument for the command
            
        Returns:
            Command output or None if failed
        """
        if not self.enabled:
            return None
        
        try:
            # Construct command
            cmd = ["python", self.integration_script, command]
            if arg:
                cmd.append(arg)
            
            # Run command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return result.stdout.strip()
        except subprocess.SubprocessError as e:
            print(f"Error running memory command: {e}")
            return None
    
    def remember(self, memory: str) -> bool:
        """
        Store a memory in the Claude Memory System.
        
        Args:
            memory: Memory text to store
            
        Returns:
            True if successful, False otherwise
        """
        result = self.run_memory_command("remember", memory)
        return result is not None and "stored" in result.lower()
    
    def recall(self, query: str) -> List[str]:
        """
        Recall memories related to a query.
        
        Args:
            query: Query to search for
            
        Returns:
            List of related memories
        """
        result = self.run_memory_command("recall", query)
        if not result:
            return []
        
        # Parse memories from result
        memories = []
        for line in result.split('\n'):
            line = line.strip()
            if line and not line.startswith("Memory search results for:"):
                # Remove any numbering
                if '. ' in line and line[0].isdigit():
                    line = line.split('. ', 1)[1]
                memories.append(line)
        
        return memories
    
    def get_context(self, query: str) -> str:
        """
        Get memory context for a query.
        
        Args:
            query: Query to get context for
            
        Returns:
            Formatted memory context
        """
        result = self.run_memory_command("context", query)
        return result or ""
    
    def list_memories(self) -> List[Dict[str, Any]]:
        """
        List all memories in the Claude Memory System.
        
        Returns:
            List of memory dictionaries
        """
        result = self.run_memory_command("list")
        if not result:
            return []
        
        # Parse memories from result
        memories = []
        current_date = None
        
        for line in result.split('\n'):
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or line.startswith("All memories") or "---" in line:
                continue
            
            # Check if line contains a date
            if line.startswith('[') and ']' in line:
                # Extract date
                date_str = line.split(']', 1)[0].strip('[')
                current_date = date_str
                
                # Extract memory text
                memory_text = line.split(']', 1)[1].strip()
                
                if memory_text:
                    memories.append({
                        "date": current_date,
                        "text": memory_text
                    })
            else:
                # This is a continuation of the previous memory
                if memories:
                    memories[-1]["text"] += " " + line
        
        return memories
    
    def store_persona_insight(self, persona_id: str, insight: Dict[str, Any]) -> bool:
        """
        Store a persona insight in the Claude Memory System.
        
        Args:
            persona_id: ID of the persona
            insight: Insight dictionary
            
        Returns:
            True if successful, False otherwise
        """
        # Format the memory
        memory = f"[Persona: {persona_id}] {insight['content']}"
        
        # Include domain and confidence if available
        if "domain" in insight and "confidence" in insight:
            memory += f" (Domain: {insight['domain']}, Confidence: {insight['confidence']:.2f})"
        
        # Store the memory
        return self.remember(memory)
    
    def get_persona_memories(self, persona_id: str) -> List[Dict[str, Any]]:
        """
        Get all memories related to a persona.
        
        Args:
            persona_id: ID of the persona
            
        Returns:
            List of memory dictionaries
        """
        all_memories = self.list_memories()
        
        # Filter memories related to this persona
        persona_memories = []
        for memory in all_memories:
            if f"[Persona: {persona_id}]" in memory["text"]:
                persona_memories.append(memory)
        
        return persona_memories


# Example usage
if __name__ == "__main__":
    memory_system = ClaudeMemoryIntegration()
    
    if memory_system.is_available():
        print("Claude Memory System is available.")
        
        # Store a memory
        memory_system.remember("Smart Steps AI can integrate with the Claude Memory System.")
        
        # Recall memories
        memories = memory_system.recall("Smart Steps")
        print("Found memories:")
        for memory in memories:
            print(f"  - {memory}")
    else:
        print("Claude Memory System is not available.")
