"""Data models for memory management."""

import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Type of memory."""

    SESSION_SUMMARY = "session_summary"
    CLIENT_INFORMATION = "client_information"
    INSIGHT = "insight"
    GOAL = "goal"
    PROGRESS = "progress"
    EVENT = "event"
    BEHAVIOR = "behavior"
    PREFERENCE = "preference"
    OBSERVATION = "observation"
    STRATEGY = "strategy"
    CUSTOM = "custom"


class MemorySource(BaseModel):
    """Source of a memory."""

    type: str
    id: str
    reference: Optional[str] = None
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)


class MemoryEntry(BaseModel):
    """A memory entry that can be stored and retrieved."""

    id: str
    text: str
    type: MemoryType
    client_name: str
    source: MemorySource
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    importance: int = Field(default=5, ge=1, le=10)
    metadata: Dict[str, str] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    associated_memories: List[str] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime.datetime: lambda v: v.isoformat(),
        }
