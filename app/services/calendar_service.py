"""
Calendar service for aggregated calendar view.
"""
from datetime import date, datetime, time

from app.models.schedule import DayOfWeek
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.visit_repository import VisitRepository
from app.schemas.calendar import CalendarEvent, CalendarResponse
from app.services.availability_service import WEEKDAY_MAP


class CalendarService:
    """Service for calendar data aggregation."""
    
    def __init__(
        self,
        visit_repository: VisitRepository,
        schedule_repository: ScheduleRepository,
    ):
        self.visit_repository = visit_repository
        self.schedule_repository = schedule_repository
    
    async def get_calendar(
        self,
        start_date: date,
        end_date: date,
        employee_id: int | None = None,
    ) -> CalendarResponse:
        """Get calendar events for a date range."""
        events: list[CalendarEvent] = []
        
        # Get visits
        visits = await self.visit_repository.get_for_calendar(
            start_date, end_date, employee_id
        )
        
        for visit in visits:
            color = "blue"
            if visit.status.value == "completed":
                color = "green"
            elif visit.status.value == "cancelled":
                color = "red"
            
            events.append(CalendarEvent(
                type="visit",
                id=visit.id,
                title=f"{visit.service.name} - {visit.customer.full_name}",
                start=visit.start_datetime,
                end=visit.end_datetime,
                color=color,
            ))
        
        # Get breaks for each day in range (if employee specified)
        if employee_id:
            current = start_date
            while current <= end_date:
                day_of_week = WEEKDAY_MAP[current.weekday()]
                schedule = await self.schedule_repository.get_by_employee_and_day(
                    employee_id, day_of_week
                )
                
                if schedule:
                    for break_ in schedule.breaks:
                        events.append(CalendarEvent(
                            type="break",
                            id=break_.id,
                            title="Break",
                            start=datetime.combine(current, break_.start_time),
                            end=datetime.combine(current, break_.end_time),
                            color="gray",
                        ))
                
                current = date.fromordinal(current.toordinal() + 1)
        
        # Sort by start time
        events.sort(key=lambda e: e.start)
        
        return CalendarResponse(events=events)
