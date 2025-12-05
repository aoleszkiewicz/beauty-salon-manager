"""
Visit repository for data access.
"""
from datetime import date, datetime

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.visit import Visit, VisitStatus
from app.repositories.base_repository import BaseRepository


class VisitRepository(BaseRepository[Visit]):
    """Repository for Visit entity."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Visit, session)
    
    async def get_with_relations(self, visit_id: int) -> Visit | None:
        """Get visit with all relations loaded."""
        result = await self.session.execute(
            select(Visit)
            .where(Visit.id == visit_id)
            .options(
                selectinload(Visit.customer),
                selectinload(Visit.employee),
                selectinload(Visit.service),
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_employee_and_date(
        self,
        employee_id: int,
        target_date: date,
    ) -> list[Visit]:
        """Get all visits for an employee on a specific date."""
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        
        result = await self.session.execute(
            select(Visit)
            .where(
                Visit.employee_id == employee_id,
                Visit.start_datetime >= start_of_day,
                Visit.start_datetime <= end_of_day,
                Visit.status == VisitStatus.SCHEDULED,
            )
            .order_by(Visit.start_datetime)
        )
        return list(result.scalars().all())
    
    async def get_overlapping(
        self,
        employee_id: int,
        start_dt: datetime,
        end_dt: datetime,
        exclude_visit_id: int | None = None,
    ) -> list[Visit]:
        """Get visits that overlap with the given time range."""
        stmt = select(Visit).where(
            Visit.employee_id == employee_id,
            Visit.status == VisitStatus.SCHEDULED,
            # Overlap condition: start < end_dt AND end > start_dt
            Visit.start_datetime < end_dt,
            Visit.end_datetime > start_dt,
        )
        
        if exclude_visit_id:
            stmt = stmt.where(Visit.id != exclude_visit_id)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def filter_visits(
        self,
        employee_id: int | None = None,
        customer_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        status: VisitStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Visit]:
        """Filter visits by various criteria."""
        stmt = select(Visit)
        
        if employee_id:
            stmt = stmt.where(Visit.employee_id == employee_id)
        if customer_id:
            stmt = stmt.where(Visit.customer_id == customer_id)
        if start_date:
            stmt = stmt.where(Visit.start_datetime >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            stmt = stmt.where(Visit.start_datetime <= datetime.combine(end_date, datetime.max.time()))
        if status:
            stmt = stmt.where(Visit.status == status)
        
        stmt = stmt.order_by(Visit.start_datetime).offset(skip).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def count_filter(
        self,
        employee_id: int | None = None,
        customer_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        status: VisitStatus | None = None,
    ) -> int:
        """Count visits matching filter criteria."""
        stmt = select(func.count()).select_from(Visit)
        
        if employee_id:
            stmt = stmt.where(Visit.employee_id == employee_id)
        if customer_id:
            stmt = stmt.where(Visit.customer_id == customer_id)
        if start_date:
            stmt = stmt.where(Visit.start_datetime >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            stmt = stmt.where(Visit.start_datetime <= datetime.combine(end_date, datetime.max.time()))
        if status:
            stmt = stmt.where(Visit.status == status)
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def get_for_calendar(
        self,
        start_date: date,
        end_date: date,
        employee_id: int | None = None,
    ) -> list[Visit]:
        """Get visits for calendar display."""
        stmt = select(Visit).where(
            Visit.start_datetime >= datetime.combine(start_date, datetime.min.time()),
            Visit.start_datetime <= datetime.combine(end_date, datetime.max.time()),
        ).options(
            selectinload(Visit.customer),
            selectinload(Visit.service),
        )
        
        if employee_id:
            stmt = stmt.where(Visit.employee_id == employee_id)
        
        stmt = stmt.order_by(Visit.start_datetime)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
