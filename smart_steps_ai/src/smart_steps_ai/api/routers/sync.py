"""
Data synchronization API endpoints.

This module provides endpoints for data synchronization between clients
and the API server, including sync operations and backup/restore functionality.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse

from smart_steps_ai.config import ConfigManager
from ..schemas.sync import (
    SyncRecordCreate,
    SyncRecordResponse,
    SyncBatch,
    BackupResponse,
    BackupList
)
from ..security.auth import get_current_user
from ..dependencies import get_config_manager
from ..sync import SyncManager

# Create router
router = APIRouter()

# Get sync manager instance
def get_sync_manager():
    from smart_steps_ai.persistence import PersistenceManager
    from smart_steps_ai.config import ConfigManager
    config_manager = ConfigManager()
    persistence_manager = PersistenceManager(config_manager)
    return SyncManager(config_manager, persistence_manager)

@router.post(
    "/records", 
    response_model=SyncRecordResponse,
    status_code=201,
    summary="Create sync record",
    description="Creates a new synchronization record."
)
async def create_sync_record(
    record_data: SyncRecordCreate,
    current_user = Depends(get_current_user),
    sync_manager = Depends(get_sync_manager)
):
    """Create a new sync record."""
    try:
        # Create the sync record
        record = sync_manager.create_sync_record(
            entity_type=record_data.entity_type,
            entity_id=record_data.entity_id,
            operation=record_data.operation,
            data=record_data.data,
            client_id=record_data.client_id,
            version=record_data.version
        )
        
        # Create response
        return SyncRecordResponse(
            record_id=record.record_id,
            entity_type=record.entity_type,
            entity_id=record.entity_id,
            operation=record.operation,
            timestamp=record.timestamp,
            data=record.data,
            client_id=record.client_id,
            version=record.version,
            status=record.status
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create sync record: {str(e)}")

@router.post(
    "/batch", 
    response_model=List[SyncRecordResponse],
    summary="Process sync batch",
    description="Processes a batch of synchronization records."
)
async def process_sync_batch(
    batch: SyncBatch,
    current_user = Depends(get_current_user),
    sync_manager = Depends(get_sync_manager)
):
    """Process a batch of sync records."""
    try:
        responses = []
        
        # Process each record
        for record_data in batch.records:
            record = sync_manager.create_sync_record(
                entity_type=record_data.entity_type,
                entity_id=record_data.entity_id,
                operation=record_data.operation,
                data=record_data.data,
                client_id=record_data.client_id,
                version=record_data.version
            )
            
            # Add to responses
            responses.append(SyncRecordResponse(
                record_id=record.record_id,
                entity_type=record.entity_type,
                entity_id=record.entity_id,
                operation=record.operation,
                timestamp=record.timestamp,
                data=record.data,
                client_id=record.client_id,
                version=record.version,
                status=record.status
            ))
        
        # Process pending records
        processed, synced, conflicts = sync_manager.process_pending_sync_records()
        
        return responses
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process sync batch: {str(e)}")

@router.get(
    "/records", 
    response_model=List[SyncRecordResponse],
    summary="Get sync records",
    description="Retrieves synchronization records with optional filtering."
)
async def get_sync_records(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    client_id: Optional[str] = Query(None, description="Filter by client ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    since: Optional[float] = Query(None, description="Only return records after this timestamp"),
    current_user = Depends(get_current_user),
    sync_manager = Depends(get_sync_manager)
):
    """Get sync records with optional filtering."""
    try:
        # Get records
        records = sync_manager.get_sync_records(
            entity_type=entity_type,
            entity_id=entity_id,
            client_id=client_id,
            status=status,
            since_timestamp=since
        )
        
        # Create responses
        responses = [SyncRecordResponse(
            record_id=record.record_id,
            entity_type=record.entity_type,
            entity_id=record.entity_id,
            operation=record.operation,
            timestamp=record.timestamp,
            data=record.data,
            client_id=record.client_id,
            version=record.version,
            status=record.status
        ) for record in records]
        
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sync records: {str(e)}")

@router.patch(
    "/records/{record_id}/status", 
    response_model=SyncRecordResponse,
    summary="Update sync record status",
    description="Updates the status of a synchronization record."
)
async def update_sync_record_status(
    record_id: str = Path(..., description="ID of the sync record"),
    status: str = Query(..., description="New status for the record"),
    current_user = Depends(get_current_user),
    sync_manager = Depends(get_sync_manager)
):
    """Update the status of a sync record."""
    try:
        # Update status
        success = sync_manager.update_sync_record_status(record_id, status)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Sync record {record_id} not found")
        
        # Get updated record
        records = sync_manager.get_sync_records(record_id=record_id)
        if not records:
            raise HTTPException(status_code=404, detail=f"Sync record {record_id} not found")
        
        record = records[0]
        
        # Create response
        return SyncRecordResponse(
            record_id=record.record_id,
            entity_type=record.entity_type,
            entity_id=record.entity_id,
            operation=record.operation,
            timestamp=record.timestamp,
            data=record.data,
            client_id=record.client_id,
            version=record.version,
            status=record.status
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update sync record status: {str(e)}")

@router.post(
    "/process", 
    response_model=Dict[str, int],
    summary="Process pending records",
    description="Processes all pending synchronization records."
)
async def process_pending_records(
    current_user = Depends(get_current_user),
    sync_manager = Depends(get_sync_manager)
):
    """Process all pending sync records."""
    try:
        # Process pending records
        processed, synced, conflicts = sync_manager.process_pending_sync_records()
        
        # Create response
        return {
            "processed": processed,
            "synced": synced,
            "conflicts": conflicts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process pending records: {str(e)}")

@router.post(
    "/backups", 
    response_model=BackupResponse,
    status_code=201,
    summary="Create backup",
    description="Creates a backup of the current data."
)
async def create_backup(
    backup_id: Optional[str] = Query(None, description="Optional identifier for the backup"),
    current_user = Depends(get_current_user),
    sync_manager = Depends(get_sync_manager)
):
    """Create a data backup."""
    try:
        # Create backup
        backup_id = sync_manager.create_backup(backup_id)
        
        # Create response
        return BackupResponse(
            backup_id=backup_id,
            timestamp=datetime.now(),
            status="success",
            message="Backup created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")

@router.get(
    "/backups", 
    response_model=BackupList,
    summary="List backups",
    description="Retrieves a list of available data backups."
)
async def list_backups(
    current_user = Depends(get_current_user),
    sync_manager = Depends(get_sync_manager)
):
    """List available backups."""
    try:
        # Get backup IDs
        backup_ids = sync_manager.get_available_backups()
        
        # Create response
        return BackupList(
            backups=[BackupResponse(
                backup_id=backup_id,
                timestamp=datetime.fromtimestamp(float(backup_id.split('_')[1])) if '_' in backup_id else datetime.now(),
                status="available",
                message=""
            ) for backup_id in backup_ids],
            count=len(backup_ids)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")

@router.post(
    "/backups/{backup_id}/restore", 
    response_model=BackupResponse,
    summary="Restore backup",
    description="Restores data from a backup."
)
async def restore_backup(
    backup_id: str = Path(..., description="ID of the backup to restore"),
    current_user = Depends(get_current_user),
    sync_manager = Depends(get_sync_manager)
):
    """Restore data from a backup."""
    try:
        # Restore backup
        success = sync_manager.restore_backup(backup_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Backup {backup_id} not found or could not be restored")
        
        # Create response
        return BackupResponse(
            backup_id=backup_id,
            timestamp=datetime.now(),
            status="success",
            message="Backup restored successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restore backup: {str(e)}")
