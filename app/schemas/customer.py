"""
Customer schemas for request/response validation.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============== Request Schemas ==============

class CustomerCreate(BaseModel):
    """Schema for creating a new customer."""
    
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str | None = Field(None, max_length=50)
    email: EmailStr | None = None
    notes: str | None = None


class CustomerUpdate(BaseModel):
    """Schema for updating a customer."""
    
    full_name: str | None = Field(None, min_length=1, max_length=255)
    phone: str | None = Field(None, max_length=50)
    email: EmailStr | None = None
    notes: str | None = None


# ============== Response Schemas ==============

class CustomerResponse(BaseModel):
    """Schema for customer response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    full_name: str
    phone: str | None
    email: str | None
    notes: str | None
    created_at: datetime


class CustomerListResponse(BaseModel):
    """Schema for list of customers response."""
    
    items: list[CustomerResponse]
    total: int
