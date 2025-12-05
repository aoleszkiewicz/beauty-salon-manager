"""
Visit controller.
"""
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import (
    CurrentAdmin,
    CurrentUser,
    get_visit_service,
)
from app.models.visit import VisitStatus
from app.schemas.user import MessageResponse
from app.schemas.visit import (
    VisitCreate,
    VisitDetailResponse,
    VisitListResponse,
    VisitResponse,
    VisitStatusUpdate,
    VisitUpdate,
)
from app.services.visit_service import VisitService

router = APIRouter(prefix="/visits", tags=["Visits"])


@router.post(
    "",
    response_model=VisitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Book a new visit",
)
async def create_visit(
    data: VisitCreate,
    _user: CurrentUser,
    visit_service: Annotated[VisitService, Depends(get_visit_service)],
) -> VisitResponse:
    """Book a new visit (appointment)."""
    visit = await visit_service.create_visit(data)
    return VisitResponse.model_validate(visit)


@router.get(
    "",
    response_model=VisitListResponse,
    summary="List visits",
)
async def list_visits(
    _user: CurrentUser,
    visit_service: Annotated[VisitService, Depends(get_visit_service)],
    employee_id: int | None = Query(None, description="Filter by employee"),
    customer_id: int | None = Query(None, description="Filter by customer"),
    start_date: date | None = Query(None, description="Filter from date (inclusive)"),
    end_date: date | None = Query(None, description="Filter to date (inclusive)"),
    visit_status: VisitStatus | None = Query(None, alias="status", description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> VisitListResponse:
    """List visits with optional filters."""
    visits, total = await visit_service.list_visits(
        employee_id=employee_id,
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date,
        status=visit_status,
        skip=skip,
        limit=limit,
    )
    return VisitListResponse(
        items=[VisitResponse.model_validate(v) for v in visits],
        total=total,
    )


@router.get(
    "/{visit_id}",
    response_model=VisitDetailResponse,
    summary="Get visit details",
)
async def get_visit(
    visit_id: int,
    _user: CurrentUser,
    visit_service: Annotated[VisitService, Depends(get_visit_service)],
) -> VisitDetailResponse:
    """Get detailed visit information."""
    visit = await visit_service.get_visit_detail(visit_id)
    return VisitDetailResponse.model_validate(visit)


@router.put(
    "/{visit_id}",
    response_model=VisitResponse,
    summary="Update visit (reschedule)",
)
async def update_visit(
    visit_id: int,
    data: VisitUpdate,
    _user: CurrentUser,
    visit_service: Annotated[VisitService, Depends(get_visit_service)],
) -> VisitResponse:
    """Update/reschedule a visit."""
    visit = await visit_service.update_visit(visit_id, data)
    return VisitResponse.model_validate(visit)


@router.patch(
    "/{visit_id}/status",
    response_model=VisitResponse,
    summary="Change visit status",
)
async def update_status(
    visit_id: int,
    data: VisitStatusUpdate,
    _user: CurrentUser,
    visit_service: Annotated[VisitService, Depends(get_visit_service)],
) -> VisitResponse:
    """Update visit status (complete/cancel)."""
    visit = await visit_service.update_status(visit_id, data)
    return VisitResponse.model_validate(visit)


@router.delete(
    "/{visit_id}",
    response_model=MessageResponse,
    summary="Cancel and remove visit",
)
async def cancel_visit(
    visit_id: int,
    _admin: CurrentAdmin,
    visit_service: Annotated[VisitService, Depends(get_visit_service)],
) -> MessageResponse:
    """Cancel and remove a visit. Admin only."""
    await visit_service.cancel_visit(visit_id)
    return MessageResponse(message="Visit cancelled and removed.")
