"""
Schedule service for work schedule and break management.
"""
from datetime import time

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.schedule import WorkBreak, WorkSchedule
from app.repositories.schedule_repository import BreakRepository, ScheduleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.schedule import BreakCreate, ScheduleCreate, ScheduleUpdate


class ScheduleService:
    """Service for work schedule management."""

    def __init__(
        self,
        schedule_repository: ScheduleRepository,
        break_repository: BreakRepository,
        user_repository: UserRepository,
    ):
        self.schedule_repository = schedule_repository
        self.break_repository = break_repository
        self.user_repository = user_repository

    async def create_schedule(
        self,
        employee_id: int,
        data: ScheduleCreate,
    ) -> WorkSchedule:
        """Create a new work schedule for an employee."""
        # Verify employee exists
        employee = await self.user_repository.get_by_id(employee_id)
        if not employee:
            raise NotFoundError("Employee", employee_id)

        # Check for duplicate day
        existing = await self.schedule_repository.get_by_employee_and_day(
            employee_id, data.day_of_week
        )
        if existing:
            raise ConflictError(
                f"Schedule for {data.day_of_week.value} already exists for this employee"
            )

        schedule = WorkSchedule(
            employee_id=employee_id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time,
        )

        return await self.schedule_repository.create(schedule)

    async def get_employee_schedules(
        self,
        employee_id: int,
    ) -> list[WorkSchedule]:
        """Get all schedules for an employee."""
        employee = await self.user_repository.get_by_id(employee_id)
        if not employee:
            raise NotFoundError("Employee", employee_id)

        return await self.schedule_repository.get_by_employee(employee_id)

    async def get_schedule(self, schedule_id: int) -> WorkSchedule:
        """Get schedule by ID."""
        schedule = await self.schedule_repository.get_with_breaks(schedule_id)
        if not schedule:
            raise NotFoundError("Schedule", schedule_id)
        return schedule

    async def update_schedule(
        self,
        schedule_id: int,
        data: ScheduleUpdate,
    ) -> WorkSchedule:
        """Update a work schedule."""
        schedule = await self.get_schedule(schedule_id)

        new_start = data.start_time if data.start_time else schedule.start_time
        new_end = data.end_time if data.end_time else schedule.end_time

        # Validate breaks still fit within new hours
        for break_ in schedule.breaks:
            if break_.start_time < new_start or break_.end_time > new_end:
                raise ValidationError(
                    f"Break {break_.start_time}-{break_.end_time} would be outside "
                    f"updated schedule hours {new_start}-{new_end}"
                )

        if data.start_time:
            schedule.start_time = data.start_time
        if data.end_time:
            schedule.end_time = data.end_time

        return await self.schedule_repository.update(schedule)

    async def delete_schedule(self, schedule_id: int) -> None:
        """Delete a work schedule."""
        schedule = await self.get_schedule(schedule_id)
        await self.schedule_repository.delete(schedule)

    # Break management
    async def add_break(
        self,
        schedule_id: int,
        data: BreakCreate,
    ) -> WorkBreak:
        """Add a break to a schedule."""
        schedule = await self.get_schedule(schedule_id)

        # Validate break is within schedule hours
        if data.start_time < schedule.start_time or data.end_time > schedule.end_time:
            raise ValidationError(
                f"Break must be within schedule hours ({schedule.start_time}-{schedule.end_time})"
            )

        # Check for overlapping breaks
        for existing_break in schedule.breaks:
            if self._times_overlap(
                data.start_time, data.end_time,
                existing_break.start_time, existing_break.end_time,
            ):
                raise ConflictError(
                    f"Break overlaps with existing break "
                    f"({existing_break.start_time}-{existing_break.end_time})"
                )

        break_ = WorkBreak(
            schedule_id=schedule_id,
            start_time=data.start_time,
            end_time=data.end_time,
        )

        return await self.break_repository.create(break_)

    async def get_schedule_breaks(self, schedule_id: int) -> list[WorkBreak]:
        """Get all breaks for a schedule."""
        schedule = await self.get_schedule(schedule_id)
        return schedule.breaks

    async def delete_break(self, break_id: int) -> None:
        """Delete a break."""
        break_ = await self.break_repository.get_by_id(break_id)
        if not break_:
            raise NotFoundError("Break", break_id)
        await self.break_repository.delete(break_)

    @staticmethod
    def _times_overlap(
        start1: time,
        end1: time,
        start2: time,
        end2: time,
    ) -> bool:
        """Check if two time ranges overlap."""
        return start1 < end2 and end1 > start2
