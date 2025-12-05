"""
Calendar controller.
"""
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUser, get_calendar_service
from app.schemas.calendar import CalendarResponse
from app.services.calendar_service import CalendarService

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get(
    "",
    response_model=CalendarResponse,
    summary="Get calendar events",
)
async def get_calendar(
    _user: CurrentUser,
    calendar_service: Annotated[CalendarService, Depends(get_calendar_service)],
    start_date: date = Query(..., description="Start date (inclusive)"),
    end_date: date = Query(..., description="End date (inclusive)"),
    employee_id: int | None = Query(None, description="Filter by employee"),
) -> CalendarResponse:
    """
    Get calendar events for a date range.
    
    Returns visits and breaks formatted for calendar display.
    Compatible with frontend calendar libraries (e.g., FullCalendar).
    """
    return await calendar_service.get_calendar(start_date, end_date, employee_id)
