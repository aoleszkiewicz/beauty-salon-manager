"""
Authentication controller.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_auth_service
from app.schemas.user import LoginRequest, MessageResponse, TokenResponse, UserCreate
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=MessageResponse,
    summary="Login with email and password",
)
async def login(
    data: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    """
    Authenticate with email and password.
    
    Note: This API uses HTTP Basic Authentication for subsequent requests.
    This endpoint validates credentials and confirms they are correct.
    """
    await auth_service.authenticate(data.email, data.password)
    return MessageResponse(message="Login successful. Use HTTP Basic Auth for API requests.")


@router.post(
    "/setup",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create initial admin user",
)
async def setup_admin(
    data: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    """
    Create the initial admin user.
    
    This endpoint should only be used once during initial setup.
    """
    await auth_service.create_initial_admin(
        email=data.email,
        password=data.password,
        full_name=data.full_name,
    )
    return MessageResponse(message="Admin user created successfully.")
