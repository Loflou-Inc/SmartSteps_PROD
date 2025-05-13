"""
Common API models for the Smart Steps AI API.

This module defines common data models used across different API endpoints.
"""

from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

T = TypeVar('T')


class StatusResponse(BaseModel):
    """Status response model."""
    status: str = Field(..., description="Operation status (success or error)")
    message: str = Field(..., description="Status message")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Page size")
    

class SortOrder(str, Enum):
    """Sort order options."""
    ASC = "asc"
    DESC = "desc"


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
