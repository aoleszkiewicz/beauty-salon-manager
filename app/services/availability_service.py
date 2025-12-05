"""
Availability service - Core business logic for slot validation.
"""
from datetime import datetime, time, timedelta

from app.core.exceptions import SlotUnavailableError
from app.models.schedule import DayOfWeek
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.visit_repository import VisitRepository

# Map Python weekday (0=Monday) to DayOfWeek enum
WEEKDAY_MAP = {
    0: DayOfWeek.MONDAY,
    1: DayOfWeek.TUESDAY,
    2: DayOfWeek.WEDNESDAY,
    3: DayOfWeek.THURSDAY,
    4: DayOfWeek.FRIDAY,
    5: DayOfWeek.SATURDAY,
    6: DayOfWeek.SUNDAY,
}


class AvailabilityService:
    """Service for checking time slot availability."""

    def __init__(
        self,
        schedule_repository: ScheduleRepository,
        visit_repository: VisitRepository,
    ):
        self.schedule_repository = schedule_repository
        self.visit_repository = visit_repository

    async def is_slot_available(
        self,
        employee_id: int,
        start_datetime: datetime,
        duration_minutes: int,
        exclude_visit_id: int | None = None,
    ) -> bool:
        """
        Check if a time slot is available for booking.

        Returns True if available, raises SlotUnavailableError if not.
        """
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)

        # 1. Check if slot spans midnight (invalid)
        if start_datetime.date() != end_datetime.date():
            raise SlotUnavailableError("Visit cannot span midnight")

        # 2. Get employee's schedule for this day
        day_of_week = WEEKDAY_MAP[start_datetime.weekday()]
        schedule = await self.schedule_repository.get_by_employee_and_day(
            employee_id, day_of_week
        )

        if not schedule:
            raise SlotUnavailableError(
                f"Employee has no schedule for {day_of_week.value}"
            )

        # 3. Check if within working hours
        slot_start_time = start_datetime.time()
        slot_end_time = end_datetime.time()

        if slot_start_time < schedule.start_time:
            raise SlotUnavailableError(
                f"Start time {slot_start_time} is before work hours ({schedule.start_time})"
            )

        if slot_end_time > schedule.end_time:
            raise SlotUnavailableError(
                f"End time {slot_end_time} is after work hours ({schedule.end_time})"
            )

        # 4. Check for break overlaps
        for break_ in schedule.breaks:
            if self._times_overlap(
                slot_start_time, slot_end_time,
                break_.start_time, break_.end_time,
            ):
                raise SlotUnavailableError(
                    f"Time slot overlaps with break ({break_.start_time}-{break_.end_time})"
                )

        # 5. Check for existing visit conflicts
        overlapping = await self.visit_repository.get_overlapping(
            employee_id,
            start_datetime,
            end_datetime,
            exclude_visit_id=exclude_visit_id,
        )

        if overlapping:
            visit = overlapping[0]
            raise SlotUnavailableError(
                f"Time slot conflicts with existing visit "
                f"({visit.start_datetime.strftime('%H:%M')}-{visit.end_datetime.strftime('%H:%M')})"
            )

        return True

    @staticmethod
    def _times_overlap(
        start1: time,
        end1: time,
        start2: time,
        end2: time,
    ) -> bool:
        """Check if two time ranges overlap."""
        return start1 < end2 and end1 > start2
