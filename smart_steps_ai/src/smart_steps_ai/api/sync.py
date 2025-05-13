"""
Data synchronization utilities for the Smart Steps AI API.

This module provides functions and classes for handling data synchronization
between the API and clients, including conflict resolution and backup mechanisms.
"""

import logging
import time
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from smart_steps_ai.config import ConfigManager
from smart_steps_ai.utils.logging import setup_logger
from smart_steps_ai.persistence import PersistenceManager

# Configure logging
logger = setup_logger(__name__)

class SyncRecord:
    """
    Represents a synchronization record for tracking changes.
    """
    
    def __init__(
        self,
        record_id: str,
        entity_type: str,
        entity_id: str,
        operation: str,
        timestamp: float,
        data: Dict[str, Any],
        client_id: str,
        version: int = 1,
        status: str = "pending",
    ):
        """
        Initialize a sync record.
        
        Args:
            record_id: Unique identifier for the sync record
            entity_type: Type of entity (session, message, persona, etc.)
            entity_id: Identifier of the entity
            operation: Type of operation (create, update, delete)
            timestamp: Timestamp of the operation
            data: Data associated with the operation
            client_id: Identifier of the client that performed the operation
            version: Version number of the entity
            status: Status of the sync record (pending, synced, conflict)
        """
        self.record_id = record_id
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.operation = operation
        self.timestamp = timestamp
        self.data = data
        self.client_id = client_id
        self.version = version
        self.status = status
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SyncRecord":
        """
        Create a sync record from a dictionary.
        
        Args:
            data: Dictionary representation of the sync record
            
        Returns:
            SyncRecord: Instantiated sync record
        """
        return cls(
            record_id=data.get("record_id"),
            entity_type=data.get("entity_type"),
            entity_id=data.get("entity_id"),
            operation=data.get("operation"),
            timestamp=data.get("timestamp"),
            data=data.get("data", {}),
            client_id=data.get("client_id"),
            version=data.get("version", 1),
            status=data.get("status", "pending"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the sync record to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the sync record
        """
        return {
            "record_id": self.record_id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "operation": self.operation,
            "timestamp": self.timestamp,
            "data": self.data,
            "client_id": self.client_id,
            "version": self.version,
            "status": self.status,
        }


class SyncManager:
    """
    Manager for data synchronization between the API and clients.
    """
    
    def __init__(self, config_manager: ConfigManager, persistence_manager: PersistenceManager):
        """
        Initialize the sync manager.
        
        Args:
            config_manager: Configuration manager instance
            persistence_manager: Persistence manager instance
        """
        self.config = config_manager
        self.persistence = persistence_manager
        self.sync_records: Dict[str, SyncRecord] = {}
        self.load_sync_records()
    
    def load_sync_records(self):
        """
        Load sync records from persistent storage.
        """
        try:
            records = self.persistence.load_data("sync_records")
            if records:
                for record_data in records:
                    record = SyncRecord.from_dict(record_data)
                    self.sync_records[record.record_id] = record
            logger.info(f"Loaded {len(self.sync_records)} sync records")
        except Exception as e:
            logger.error(f"Error loading sync records: {e}")
    
    def save_sync_records(self):
        """
        Save sync records to persistent storage.
        """
        try:
            records_data = [record.to_dict() for record in self.sync_records.values()]
            self.persistence.save_data("sync_records", records_data)
            logger.info(f"Saved {len(records_data)} sync records")
        except Exception as e:
            logger.error(f"Error saving sync records: {e}")
    
    def create_sync_record(
        self,
        entity_type: str,
        entity_id: str,
        operation: str,
        data: Dict[str, Any],
        client_id: str,
        version: int = 1,
    ) -> SyncRecord:
        """
        Create a new sync record.
        
        Args:
            entity_type: Type of entity (session, message, persona, etc.)
            entity_id: Identifier of the entity
            operation: Type of operation (create, update, delete)
            data: Data associated with the operation
            client_id: Identifier of the client that performed the operation
            version: Version number of the entity
            
        Returns:
            SyncRecord: Created sync record
        """
        record_id = str(uuid.uuid4())
        timestamp = time.time()
        
        record = SyncRecord(
            record_id=record_id,
            entity_type=entity_type,
            entity_id=entity_id,
            operation=operation,
            timestamp=timestamp,
            data=data,
            client_id=client_id,
            version=version,
            status="pending",
        )
        
        self.sync_records[record_id] = record
        self.save_sync_records()
        
        return record
    
    def get_sync_records(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        client_id: Optional[str] = None,
        status: Optional[str] = None,
        since_timestamp: Optional[float] = None,
    ) -> List[SyncRecord]:
        """
        Get sync records with optional filtering.
        
        Args:
            entity_type: Optional filter by entity type
            entity_id: Optional filter by entity ID
            client_id: Optional filter by client ID
            status: Optional filter by status
            since_timestamp: Optional filter for records after this timestamp
            
        Returns:
            List[SyncRecord]: Filtered sync records
        """
        records = list(self.sync_records.values())
        
        # Apply filters
        if entity_type:
            records = [r for r in records if r.entity_type == entity_type]
        
        if entity_id:
            records = [r for r in records if r.entity_id == entity_id]
        
        if client_id:
            records = [r for r in records if r.client_id == client_id]
        
        if status:
            records = [r for r in records if r.status == status]
        
        if since_timestamp:
            records = [r for r in records if r.timestamp >= since_timestamp]
        
        # Sort by timestamp
        records.sort(key=lambda r: r.timestamp)
        
        return records
    
    def update_sync_record_status(self, record_id: str, status: str) -> bool:
        """
        Update the status of a sync record.
        
        Args:
            record_id: ID of the sync record
            status: New status for the record
            
        Returns:
            bool: True if the record was updated, False otherwise
        """
        if record_id in self.sync_records:
            self.sync_records[record_id].status = status
            self.save_sync_records()
            return True
        return False
    
    def process_pending_sync_records(self) -> Tuple[int, int, int]:
        """
        Process pending sync records.
        
        Returns:
            Tuple[int, int, int]: (processed, synced, conflicts)
        """
        pending_records = self.get_sync_records(status="pending")
        processed = 0
        synced = 0
        conflicts = 0
        
        for record in pending_records:
            processed += 1
            
            # Check for conflicts
            conflict = self.check_for_conflicts(record)
            
            if conflict:
                # Handle conflict
                result = self.resolve_conflict(record, conflict)
                if result:
                    synced += 1
                else:
                    conflicts += 1
            else:
                # Apply changes
                success = self.apply_sync_record(record)
                if success:
                    self.update_sync_record_status(record.record_id, "synced")
                    synced += 1
                else:
                    self.update_sync_record_status(record.record_id, "error")
                    conflicts += 1
        
        return processed, synced, conflicts
    
    def check_for_conflicts(self, record: SyncRecord) -> Optional[SyncRecord]:
        """
        Check if a sync record conflicts with existing records.
        
        Args:
            record: Sync record to check
            
        Returns:
            Optional[SyncRecord]: Conflicting record if found, None otherwise
        """
        # Get all records for the same entity
        entity_records = self.get_sync_records(
            entity_type=record.entity_type,
            entity_id=record.entity_id,
        )
        
        # Filter out the current record and those with lower timestamps
        potential_conflicts = [
            r for r in entity_records
            if r.record_id != record.record_id and r.timestamp > record.timestamp
        ]
        
        if not potential_conflicts:
            return None
        
        # Find the most recent conflicting record
        return max(potential_conflicts, key=lambda r: r.timestamp)
    
    def resolve_conflict(self, record: SyncRecord, conflict: SyncRecord) -> bool:
        """
        Resolve a conflict between two sync records.
        
        Args:
            record: Original sync record
            conflict: Conflicting sync record
            
        Returns:
            bool: True if the conflict was resolved, False otherwise
        """
        # Basic conflict resolution strategy: latest wins
        if record.timestamp >= conflict.timestamp:
            # Current record is newer, apply it
            return self.apply_sync_record(record)
        else:
            # Conflicting record is newer, mark the current record as conflicted
            self.update_sync_record_status(record.record_id, "conflict")
            return False
    
    def apply_sync_record(self, record: SyncRecord) -> bool:
        """
        Apply changes from a sync record.
        
        Args:
            record: Sync record to apply
            
        Returns:
            bool: True if the changes were applied successfully, False otherwise
        """
        try:
            # Implementation depends on entity types and operations
            # This is a simplified example
            if record.operation == "create":
                # Create entity
                pass
            elif record.operation == "update":
                # Update entity
                pass
            elif record.operation == "delete":
                # Delete entity
                pass
            
            return True
        except Exception as e:
            logger.error(f"Error applying sync record {record.record_id}: {e}")
            return False
    
    def create_backup(self, backup_id: Optional[str] = None) -> str:
        """
        Create a backup of the current data.
        
        Args:
            backup_id: Optional identifier for the backup
            
        Returns:
            str: Identifier of the created backup
        """
        if not backup_id:
            backup_id = f"backup_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        try:
            # Create backup of sync records
            records_data = [record.to_dict() for record in self.sync_records.values()]
            self.persistence.save_data(f"backups/{backup_id}/sync_records", records_data)
            
            # Backup other data as needed
            # ...
            
            logger.info(f"Created backup with ID {backup_id}")
            return backup_id
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise
    
    def restore_backup(self, backup_id: str) -> bool:
        """
        Restore data from a backup.
        
        Args:
            backup_id: Identifier of the backup to restore
            
        Returns:
            bool: True if the backup was restored successfully, False otherwise
        """
        try:
            # Load sync records from backup
            records_data = self.persistence.load_data(f"backups/{backup_id}/sync_records")
            if not records_data:
                logger.error(f"Backup {backup_id} not found or is empty")
                return False
            
            # Clear current sync records
            self.sync_records = {}
            
            # Restore sync records
            for record_data in records_data:
                record = SyncRecord.from_dict(record_data)
                self.sync_records[record.record_id] = record
            
            # Save restored records
            self.save_sync_records()
            
            # Restore other data as needed
            # ...
            
            logger.info(f"Restored backup with ID {backup_id}")
            return True
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    def get_available_backups(self) -> List[str]:
        """
        Get a list of available backup IDs.
        
        Returns:
            List[str]: List of backup IDs
        """
        try:
            # Get backup IDs from persistence manager
            backups = self.persistence.list_data_keys("backups")
            return [b.split("/")[1] for b in backups if "/" in b]
        except Exception as e:
            logger.error(f"Error getting available backups: {e}")
            return []
