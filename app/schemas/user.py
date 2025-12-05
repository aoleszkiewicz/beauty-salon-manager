"""
User schemas for request/response validation.
"""
from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


# ============== Request Schemas ==============

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.EMPLOYEE


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    
    email: EmailStr | None = None
    password: str | None = None
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class LoginRequest(BaseModel):
    """Schema for login request."""
    
    email: EmailStr
    password: str


# ============== Response Schemas ==============

class UserResponse(BaseModel):
    """Schema for user response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool


class UserListResponse(BaseModel):
    """Schema for list of users response."""
    
    items: list[UserResponse]
    total: int


class TokenResponse(BaseModel):
    """Schema for token response."""
    
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Generic message response."""
    
    message: str
