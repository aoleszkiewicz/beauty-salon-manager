"""
Schedule controller.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import (
    CurrentUser,
    get_current_user,
    get_schedule_service,
)
from app.core.exceptions import ForbiddenError
from app.models.user import User, UserRole
from app.schemas.schedule import (
    BreakCreate,
    BreakListResponse,
    BreakResponse,
    ScheduleCreate,
    ScheduleListResponse,
    ScheduleResponse,
    ScheduleUpdate,
)
from app.schemas.user import MessageResponse
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/employees/{employee_id}/schedules", tags=["Schedules"])


def _check_owner_or_admin(current_user: User, employee_id: int) -> None:
    """Check if current user is the employee owner or an admin."""
    if current_user.role != UserRole.ADMIN and current_user.id != employee_id:
        raise ForbiddenError("You can only manage your own schedule")


@router.post(
    "",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create schedule for a day",
)
async def create_schedule(
    employee_id: int,
    data: ScheduleCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    schedule_service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> ScheduleResponse:
    """Create a work schedule for a specific day. Owner or Admin only."""
    _check_owner_or_admin(current_user, employee_id)
    schedule = await schedule_service.create_schedule(employee_id, data)
    return ScheduleResponse.model_validate(schedule)


@router.get(
    "",
    response_model=ScheduleListResponse,
    summary="Get employee's weekly schedule",
)
async def list_schedules(
    employee_id: int,
    _user: CurrentUser,
    schedule_service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> ScheduleListResponse:
    """Get all schedules for an employee."""
    schedules = await schedule_service.get_employee_schedules(employee_id)
    return ScheduleListResponse(
        items=[ScheduleResponse.model_validate(s) for s in schedules],
        total=len(schedules),
    )


@router.put(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="Update schedule",
)
async def update_schedule(
    employee_id: int,
    schedule_id: int,
    data: ScheduleUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    schedule_service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> ScheduleResponse:
    """Update a work schedule. Owner or Admin only."""
    _check_owner_or_admin(current_user, employee_id)
    schedule = await schedule_service.update_schedule(schedule_id, data)
    return ScheduleResponse.model_validate(schedule)


@router.delete(
    "/{schedule_id}",
    response_model=MessageResponse,
    summary="Remove schedule",
)
async def delete_schedule(
    employee_id: int,
    schedule_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    schedule_service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> MessageResponse:
    """Delete a work schedule. Owner or Admin only."""
    _check_owner_or_admin(current_user, employee_id)
    await schedule_service.delete_schedule(schedule_id)
    return MessageResponse(message="Schedule deleted successfully.")


# Break endpoints
@router.post(
    "/{schedule_id}/breaks",
    response_model=BreakResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add break to schedule",
)
async def add_break(
    employee_id: int,
    schedule_id: int,
    data: BreakCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    schedule_service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> BreakResponse:
    """Add a break to a schedule. Owner or Admin only."""
    _check_owner_or_admin(current_user, employee_id)
    break_ = await schedule_service.add_break(schedule_id, data)
    return BreakResponse.model_validate(break_)


@router.get(
    "/{schedule_id}/breaks",
    response_model=BreakListResponse,
    summary="List breaks for schedule",
)
async def list_breaks(
    employee_id: int,
    schedule_id: int,
    _user: CurrentUser,
    schedule_service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> BreakListResponse:
    """Get all breaks for a schedule."""
    breaks = await schedule_service.get_schedule_breaks(schedule_id)
    return BreakListResponse(
        items=[BreakResponse.model_validate(b) for b in breaks],
        total=len(breaks),
    )


# Separate delete endpoint for breaks (simpler path)
break_router = APIRouter(prefix="/employees/{employee_id}/breaks", tags=["Schedules"])


@break_router.delete(
    "/{break_id}",
    response_model=MessageResponse,
    summary="Remove break",
)
async def delete_break(
    employee_id: int,
    break_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    schedule_service: Annotated[ScheduleService, Depends(get_schedule_service)],
) -> MessageResponse:
    """Delete a break. Owner or Admin only."""
    _check_owner_or_admin(current_user, employee_id)
    await schedule_service.delete_break(break_id)
    return MessageResponse(message="Break deleted successfully.")
