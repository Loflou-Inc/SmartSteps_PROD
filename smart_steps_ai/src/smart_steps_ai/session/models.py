"""Data models for sessions and conversations."""

import datetime
import uuid
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

from ..persona.models import Persona, PersonaMetadata


class MessageRole(str, Enum):
    """Role of a message sender."""

    SYSTEM = "system"
    CLIENT = "client"
    ASSISTANT = "assistant"
    INTERNAL = "internal"


class Message(BaseModel):
    """A message in a conversation."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    metadata: Dict[str, str] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        """Validate that the content is not empty."""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v


class SessionType(str, Enum):
    """Type of a session."""

    INITIAL = "initial"
    STANDARD = "standard"
    FOLLOWUP = "followup"
    ASSESSMENT = "assessment"
    CRISIS = "crisis"
    TERMINATION = "termination"
    CUSTOM = "custom"


class SessionState(str, Enum):
    """State of a session."""

    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SessionMetadata(BaseModel):
    """Metadata for a session."""

    id: str
    client_name: str
    session_type: SessionType
    persona_name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    state: SessionState
    messages_count: int = 0
    duration_seconds: int = 0
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, str] = Field(default_factory=dict)


class SessionConfig(BaseModel):
    """Configuration for a session."""

    max_history_length: int = Field(default=50, ge=1)
    auto_save: bool = True
    auto_save_interval: int = Field(default=60, ge=5)
    include_timestamps: bool = True
    include_message_ids: bool = True
    context_window_size: int = Field(default=4000, ge=1)


class Session(BaseModel):
    """A conversation session between a client and an AI professional persona."""

    # Basic session information
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    session_type: SessionType = SessionType.STANDARD
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    # State and configuration
    state: SessionState = SessionState.CREATED
    config: SessionConfig = Field(default_factory=SessionConfig)
    
    # Persona information
    persona_name: str
    persona_metadata: PersonaMetadata
    
    # Messages and history
    messages: List[Message] = Field(default_factory=list)
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, str] = Field(default_factory=dict)
    notes: str = ""  # Add session notes field
    
    # Summary and analysis
    summary: Optional[str] = None
    insights: List[str] = Field(default_factory=list)
    
    # Session metrics
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    
    @property
    def duration_seconds(self) -> int:
        """Get the duration of the session in seconds."""
        if not self.start_time:
            return 0
        
        end = self.end_time or datetime.datetime.now()
        return int((end - self.start_time).total_seconds())
    
    @property
    def messages_count(self) -> int:
        """Get the number of messages in the session."""
        return len(self.messages)
    
    def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict[str, str]] = None) -> Message:
        """
        Add a message to the session.

        Args:
            role (MessageRole): Role of the message sender
            content (str): Content of the message
            metadata (Optional[Dict[str, str]]): Additional metadata for the message

        Returns:
            Message: The added message
        """
        # Create a new message
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {},
        )
        
        # Add to the messages list
        self.messages.append(message)
        
        # Update session metadata
        self.updated_at = datetime.datetime.now()
        
        # If this is the first message and the session is in CREATED state, update to ACTIVE
        if self.state == SessionState.CREATED and len(self.messages) == 1:
            self.state = SessionState.ACTIVE
            self.start_time = datetime.datetime.now()
        
        return message
    
    def start(self) -> None:
        """Start the session."""
        if self.state == SessionState.CREATED:
            self.state = SessionState.ACTIVE
            self.start_time = datetime.datetime.now()
            self.updated_at = datetime.datetime.now()
    
    def pause(self) -> None:
        """Pause the session."""
        if self.state == SessionState.ACTIVE:
            self.state = SessionState.PAUSED
            self.updated_at = datetime.datetime.now()
    
    def resume(self) -> None:
        """Resume the session."""
        if self.state == SessionState.PAUSED:
            self.state = SessionState.ACTIVE
            self.updated_at = datetime.datetime.now()
    
    def complete(self) -> None:
        """Complete the session."""
        if self.state in [SessionState.ACTIVE, SessionState.PAUSED]:
            self.state = SessionState.COMPLETED
            self.end_time = datetime.datetime.now()
            self.updated_at = datetime.datetime.now()
    
    def cancel(self) -> None:
        """Cancel the session."""
        self.state = SessionState.CANCELLED
        self.end_time = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
    
    def to_metadata(self) -> SessionMetadata:
        """
        Convert to a session metadata object.

        Returns:
            SessionMetadata: Metadata for this session
        """
        return SessionMetadata(
            id=self.id,
            client_name=self.client_name,
            session_type=self.session_type,
            persona_name=self.persona_name,
            created_at=self.created_at,
            updated_at=self.updated_at,
            state=self.state,
            messages_count=self.messages_count,
            duration_seconds=self.duration_seconds,
            tags=self.tags,
            custom_fields=self.custom_fields,
        )
    
    def get_conversation_history(self, max_messages: Optional[int] = None) -> List[Message]:
        """
        Get the conversation history.

        Args:
            max_messages (Optional[int]): Maximum number of messages to return (default: None)

        Returns:
            List[Message]: Messages in the conversation
        """
        if max_messages is None:
            return self.messages
        
        return self.messages[-max_messages:]
    
    def get_conversation_text(self, include_role: bool = True, include_timestamps: bool = False) -> str:
        """
        Get the conversation as a formatted text.

        Args:
            include_role (bool): Whether to include the role of each message (default: True)
            include_timestamps (bool): Whether to include timestamps (default: False)

        Returns:
            str: Formatted conversation text
        """
        lines = []
        
        for message in self.messages:
            # Format message based on options
            if include_role and include_timestamps:
                timestamp = message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                lines.append(f"[{timestamp}] {message.role.value.upper()}: {message.content}")
            elif include_role:
                lines.append(f"{message.role.value.upper()}: {message.content}")
            elif include_timestamps:
                timestamp = message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                lines.append(f"[{timestamp}] {message.content}")
            else:
                lines.append(message.content)
        
        return "\n\n".join(lines)
