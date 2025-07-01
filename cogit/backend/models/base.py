"""
Base models for VAULT_APP v2.0
Common Pydantic models used across all API endpoints
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Generic, TypeVar
from uuid import UUID, uuid4

try:
    from pydantic import BaseModel, Field, ConfigDict
except ImportError:
    # Fallback for when pydantic is not installed
    class BaseModel:
        pass
    
    def Field(*args, **kwargs):
        return None
    
    def ConfigDict(*args, **kwargs):
        return {}


T = TypeVar('T')


class BaseResponse(BaseModel):
    """Base response model for all API responses."""
    
    if hasattr(BaseModel, 'model_config'):
        model_config = ConfigDict(
            json_encoders={
                datetime: lambda v: v.isoformat(),
                UUID: lambda v: str(v)
            }
        )
    
    success: bool = True
    message: str = "Success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


class ErrorResponse(BaseResponse):
    """Error response model for API errors."""
    
    success: bool = False
    error_code: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None


class PaginationParams(BaseModel):
    """Standard pagination parameters."""
    
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$", description="Sort order")


class PaginatedResponse(BaseResponse, Generic[T]):
    """Paginated response wrapper."""
    
    data: List[T]
    pagination: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        data: List[T],
        page: int,
        page_size: int,
        total_items: int,
        **kwargs
    ) -> 'PaginatedResponse[T]':
        """Create a paginated response with calculated pagination metadata."""
        total_pages = (total_items + page_size - 1) // page_size
        
        pagination = {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
        
        return cls(
            data=data,
            pagination=pagination,
            **kwargs
        )


class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""
    
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class UserContext(BaseModel):
    """User context information for requests."""
    
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ValidationError(BaseModel):
    """Validation error details."""
    
    field: str
    message: str
    invalid_value: Any = None


class HealthCheck(BaseResponse):
    """Health check response."""
    
    status: str = "healthy"
    version: str = "2.0.0"
    uptime: Optional[float] = None
    dependencies: Dict[str, str] = Field(default_factory=dict)