"""
API Server Monitoring Endpoints

Adds monitoring, health check, and maintenance endpoints to the Smart Steps AI API.

Usage:
    This module is automatically imported by the API server.
    
    Access monitoring endpoints at:
    - /api/v1/admin/health
    - /api/v1/admin/clear-cache
    - /api/v1/admin/maintenance
    - /api/v1/admin/metrics

Author: Smart Steps Team
Date: May 13, 2025
"""

import datetime
import logging
import os
import platform
import sys
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from smart_steps_ai.utils.maintenance import perform_maintenance, check_system_health
try:
    from smart_steps_ai.api.security.simple_auth import get_admin_user
    use_auth = True
except ImportError:
    use_auth = False
    
from smart_steps_ai.api.dependencies import get_config_manager

# Configure logging
logger = logging.getLogger(__name__)

# Create router
if use_auth:
    router = APIRouter(
        prefix="/api/v1/admin",
        tags=["admin"],
        dependencies=[Depends(get_admin_user)]
    )
else:
    router = APIRouter(
        prefix="/api/v1/admin",
        tags=["admin"]
    )

# Models
class MaintenanceRequest(BaseModel):
    """Model for maintenance request."""
    tasks: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None

class MaintenanceResponse(BaseModel):
    """Model for maintenance response."""
    success: bool
    results: Dict[str, Any]
    timestamp: str
    duration_seconds: float

class HealthResponse(BaseModel):
    """Model for health check response."""
    status: str
    version: str
    uptime: float
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    cpu: Dict[str, Any]
    python: Dict[str, Any]
    timestamp: str

class MetricsResponse(BaseModel):
    """Model for metrics response."""
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    requests: Dict[str, Any]
    cache: Dict[str, Any]
    providers: Dict[str, Any]
    timestamp: str
    
class CacheClearResponse(BaseModel):
    """Model for cache clear response."""
    success: bool
    details: Dict[str, Any]
    timestamp: str

# Request statistics tracking
request_stats = {
    "total_requests": 0,
    "requests_by_endpoint": {},
    "errors_by_endpoint": {},
    "start_time": datetime.datetime.now()
}

# Global server start time
SERVER_START_TIME = datetime.datetime.now()

# Note: We can't use middleware directly on a router, but we can track requests in our endpoints

@router.get("/health", response_model=HealthResponse)
async def health_check(config_manager=Depends(get_config_manager)):
    """
    Get health status of the API server.
    
    Returns:
        HealthResponse: Health status
    """
    # Get server uptime
    uptime = (datetime.datetime.now() - SERVER_START_TIME).total_seconds()
    
    # Get memory information
    memory_info = psutil.virtual_memory()
    
    # Get disk information
    disk_info = psutil.disk_usage('/')
    
    # Get CPU information
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_count = psutil.cpu_count()
    
    # Get system health information
    root_dir = Path(config_manager.get("root_dir", os.getcwd()))
    
    return HealthResponse(
        status="ok",
        version=config_manager.get("version", "1.0.0"),
        uptime=uptime,
        memory={
            "total": memory_info.total,
            "available": memory_info.available,
            "used": memory_info.used,
            "percent": memory_info.percent,
            "total_human": _bytes_to_human(memory_info.total),
            "available_human": _bytes_to_human(memory_info.available),
            "used_human": _bytes_to_human(memory_info.used)
        },
        disk={
            "total": disk_info.total,
            "free": disk_info.free,
            "used": disk_info.used,
            "percent": disk_info.percent,
            "total_human": _bytes_to_human(disk_info.total),
            "free_human": _bytes_to_human(disk_info.free),
            "used_human": _bytes_to_human(disk_info.used)
        },
        cpu={
            "percent": cpu_percent,
            "count": cpu_count,
            "load_average": _get_load_average()
        },
        python={
            "version": sys.version,
            "platform": platform.platform(),
            "implementation": platform.python_implementation()
        },
        timestamp=datetime.datetime.now().isoformat()
    )

@router.post("/maintenance", response_model=MaintenanceResponse)
async def run_maintenance(request: MaintenanceRequest, config_manager=Depends(get_config_manager)):
    """
    Run maintenance tasks.
    
    Args:
        request: Maintenance request
        
    Returns:
        MaintenanceResponse: Maintenance results
    """
    start_time = datetime.datetime.now()
    
    # Get root directory
    root_dir = Path(config_manager.get("root_dir", os.getcwd()))
    
    try:
        # Run maintenance tasks
        results = perform_maintenance(root_dir, request.tasks, request.config)
        
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return MaintenanceResponse(
            success=True,
            results=results,
            timestamp=end_time.isoformat(),
            duration_seconds=duration
        )
    except Exception as e:
        logger.error(f"Error running maintenance: {str(e)}")
        
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return MaintenanceResponse(
            success=False,
            results={"error": str(e)},
            timestamp=end_time.isoformat(),
            duration_seconds=duration
        )

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(config_manager=Depends(get_config_manager)):
    """
    Get server metrics.
    
    Returns:
        MetricsResponse: Server metrics
    """
    # Get CPU information
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_times = psutil.cpu_times()
    
    # Get memory information
    memory_info = psutil.virtual_memory()
    
    # Get disk information
    disk_info = psutil.disk_usage('/')
    
    # Get cache information
    cache_info = _get_cache_info()
    
    # Get provider information
    provider_info = _get_provider_info()
    
    return MetricsResponse(
        cpu={
            "percent": cpu_percent,
            "count": psutil.cpu_count(),
            "times": {
                "user": cpu_times.user,
                "system": cpu_times.system,
                "idle": cpu_times.idle
            },
            "load_average": _get_load_average()
        },
        memory={
            "total": memory_info.total,
            "available": memory_info.available,
            "used": memory_info.used,
            "percent": memory_info.percent
        },
        disk={
            "total": disk_info.total,
            "free": disk_info.free,
            "used": disk_info.used,
            "percent": disk_info.percent
        },
        requests={
            "total": request_stats["total_requests"],
            "start_time": request_stats["start_time"].isoformat(),
            "uptime_seconds": (datetime.datetime.now() - request_stats["start_time"]).total_seconds(),
            "by_endpoint": request_stats["requests_by_endpoint"],
            "errors": request_stats["errors_by_endpoint"]
        },
        cache=cache_info,
        providers=provider_info,
        timestamp=datetime.datetime.now().isoformat()
    )

@router.post("/clear-cache", response_model=CacheClearResponse)
async def clear_cache(config_manager=Depends(get_config_manager)):
    """
    Clear server caches.
    
    Returns:
        CacheClearResponse: Cache clear results
    """
    # Get root directory
    root_dir = Path(config_manager.get("root_dir", os.getcwd()))
    
    try:
        # Clear caches
        from smart_steps_ai.utils.maintenance import MaintenanceManager
        manager = MaintenanceManager(root_dir)
        results = manager.clear_cache()
        
        return CacheClearResponse(
            success=True,
            details=results,
            timestamp=datetime.datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        
        return CacheClearResponse(
            success=False,
            details={"error": str(e)},
            timestamp=datetime.datetime.now().isoformat()
        )

def _bytes_to_human(num_bytes: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        num_bytes: Number of bytes
        
    Returns:
        Human-readable string
    """
    if num_bytes > 1024 * 1024 * 1024:
        return f"{num_bytes / (1024 * 1024 * 1024):.2f} GB"
    elif num_bytes > 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.2f} MB"
    elif num_bytes > 1024:
        return f"{num_bytes / 1024:.2f} KB"
    else:
        return f"{num_bytes} bytes"

def _get_load_average() -> List[float]:
    """
    Get system load average.
    
    Returns:
        List of load averages (1min, 5min, 15min)
    """
    try:
        return [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]
    except:
        return [0.0, 0.0, 0.0]

def _get_cache_info() -> Dict[str, Any]:
    """
    Get cache information.
    
    Returns:
        Dictionary with cache information
    """
    try:
        # Import cache modules
        from smart_steps_ai.utils.cache import get_cache_stats
        
        # Get cache statistics
        return get_cache_stats()
    except ImportError:
        # Return empty dictionary if cache module not available
        return {
            "error": "Cache module not available"
        }

def _get_provider_info() -> Dict[str, Any]:
    """
    Get AI provider information.
    
    Returns:
        Dictionary with provider information
    """
    try:
        # Import provider modules
        from smart_steps_ai.provider.manager import get_provider_stats
        
        # Get provider statistics
        return get_provider_stats()
    except ImportError:
        # Return empty dictionary if provider module not available
        return {
            "error": "Provider module not available"
        }
