"""
Service controller.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import (
    CurrentAdmin,
    CurrentUser,
    get_service_service,
)
from app.schemas.service import (
    ServiceCreate,
    ServiceListResponse,
    ServiceResponse,
    ServiceUpdate,
)
from app.schemas.user import MessageResponse
from app.services.service_service import ServiceService

router = APIRouter(prefix="/services", tags=["Services"])


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new service",
)
async def create_service(
    data: ServiceCreate,
    _admin: CurrentAdmin,
    service_service: Annotated[ServiceService, Depends(get_service_service)],
) -> ServiceResponse:
    """Create a new service. Admin only."""
    service = await service_service.create_service(data)
    return ServiceResponse.model_validate(service)


@router.get(
    "",
    response_model=ServiceListResponse,
    summary="List services",
)
async def list_services(
    _user: CurrentUser,
    service_service: Annotated[ServiceService, Depends(get_service_service)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(True, description="Show only active services"),
) -> ServiceListResponse:
    """List services."""
    services, total = await service_service.list_services(skip, limit, active_only)
    return ServiceListResponse(
        items=[ServiceResponse.model_validate(s) for s in services],
        total=total,
    )


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Get service details",
)
async def get_service(
    service_id: int,
    _user: CurrentUser,
    service_service: Annotated[ServiceService, Depends(get_service_service)],
) -> ServiceResponse:
    """Get service by ID."""
    service = await service_service.get_service(service_id)
    return ServiceResponse.model_validate(service)


@router.put(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Update service",
)
async def update_service(
    service_id: int,
    data: ServiceUpdate,
    _admin: CurrentAdmin,
    service_service: Annotated[ServiceService, Depends(get_service_service)],
) -> ServiceResponse:
    """Update service details. Admin only."""
    service = await service_service.update_service(service_id, data)
    return ServiceResponse.model_validate(service)


@router.delete(
    "/{service_id}",
    response_model=MessageResponse,
    summary="Deactivate service",
)
async def deactivate_service(
    service_id: int,
    _admin: CurrentAdmin,
    service_service: Annotated[ServiceService, Depends(get_service_service)],
) -> MessageResponse:
    """Deactivate (soft delete) a service. Admin only."""
    await service_service.deactivate_service(service_id)
    return MessageResponse(message="Service deactivated successfully.")
