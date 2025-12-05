"""
Schedule repository for data access.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.schedule import DayOfWeek, WorkBreak, WorkSchedule
from app.repositories.base_repository import BaseRepository


class ScheduleRepository(BaseRepository[WorkSchedule]):
    """Repository for WorkSchedule entity."""

    def __init__(self, session: AsyncSession):
        super().__init__(WorkSchedule, session)

    async def get_by_employee(self, employee_id: int) -> list[WorkSchedule]:
        """Get all schedules for an employee."""
        result = await self.session.execute(
            select(WorkSchedule)
            .where(WorkSchedule.employee_id == employee_id)
            .options(selectinload(WorkSchedule.breaks))
            .order_by(WorkSchedule.day_of_week)
        )
        return list(result.scalars().all())

    async def get_by_employee_and_day(
        self,
        employee_id: int,
        day_of_week: DayOfWeek,
    ) -> WorkSchedule | None:
        """Get schedule for specific employee and day."""
        result = await self.session.execute(
            select(WorkSchedule)
            .where(
                WorkSchedule.employee_id == employee_id,
                WorkSchedule.day_of_week == day_of_week,
            )
            .options(selectinload(WorkSchedule.breaks))
        )
        return result.scalar_one_or_none()

    async def get_with_breaks(self, schedule_id: int) -> WorkSchedule | None:
        """Get schedule with breaks loaded."""
        result = await self.session.execute(
            select(WorkSchedule)
            .where(WorkSchedule.id == schedule_id)
            .options(selectinload(WorkSchedule.breaks))
        )
        return result.scalar_one_or_none()


class BreakRepository(BaseRepository[WorkBreak]):
    """Repository for WorkBreak entity."""

    def __init__(self, session: AsyncSession):
        super().__init__(WorkBreak, session)

    async def get_by_schedule(self, schedule_id: int) -> list[WorkBreak]:
        """Get all breaks for a schedule."""
        result = await self.session.execute(
            select(WorkBreak)
            .where(WorkBreak.schedule_id == schedule_id)
            .order_by(WorkBreak.start_time)
        )
        return list(result.scalars().all())
