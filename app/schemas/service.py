"""
Service schemas for request/response validation.
"""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ============== Request Schemas ==============

class ServiceCreate(BaseModel):
    """Schema for creating a new service."""
    
    name: str = Field(..., min_length=1, max_length=255)
    duration_minutes: int = Field(..., gt=0)
    price: Decimal = Field(..., ge=0, decimal_places=2)


class ServiceUpdate(BaseModel):
    """Schema for updating a service."""
    
    name: str | None = Field(None, min_length=1, max_length=255)
    duration_minutes: int | None = Field(None, gt=0)
    price: Decimal | None = Field(None, ge=0)
    is_active: bool | None = None


# ============== Response Schemas ==============

class ServiceResponse(BaseModel):
    """Schema for service response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    duration_minutes: int
    price: Decimal
    is_active: bool


class ServiceListResponse(BaseModel):
    """Schema for list of services response."""
    
    items: list[ServiceResponse]
    total: int
