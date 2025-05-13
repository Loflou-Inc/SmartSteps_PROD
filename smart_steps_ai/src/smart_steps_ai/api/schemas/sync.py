"""
Synchronization schema definitions.

This module defines Pydantic models for data synchronization API requests and responses.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field

class SyncRecordBase(BaseModel):
    """Base model for sync record data."""
    entity_type: str = Field(..., description="Type of entity (session, message, persona, etc.)")
    entity_id: str = Field(..., description="Identifier of the entity")
    operation: str = Field(..., description="Type of operation (create, update, delete)")
    data: Dict[str, Any] = Field(..., description="Data associated with the operation")
    client_id: str = Field(..., description="Identifier of the client that performed the operation")
    version: int = Field(1, description="Version number of the entity")

class SyncRecordCreate(SyncRecordBase):
    """Model for creating a new sync record."""
    pass

class SyncRecordResponse(SyncRecordBase):
    """Model for sync record response data."""
    record_id: str = Field(..., description="Unique identifier for the sync record")
    timestamp: float = Field(..., description="Timestamp of the operation")
    status: str = Field(..., description="Status of the sync record (pending, synced, conflict)")

class SyncBatch(BaseModel):
    """Model for a batch of sync records."""
    records: List[SyncRecordCreate] = Field(..., description="List of sync records to process")
    client_id: str = Field(..., description="Identifier of the client sending the batch")
    force_sync: bool = Field(False, description="Whether to force synchronization even with conflicts")

class BackupResponse(BaseModel):
    """Model for backup response data."""
    backup_id: str = Field(..., description="Identifier of the backup")
    timestamp: datetime = Field(..., description="Timestamp when the backup was created")
    status: str = Field(..., description="Status of the backup operation")
    message: str = Field("", description="Additional message about the backup")

class BackupList(BaseModel):
    """Model for a list of backups."""
    backups: List[BackupResponse] = Field(..., description="List of available backups")
    count: int = Field(..., description="Number of available backups")
