"""
Service repository for data access.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service import Service
from app.repositories.base_repository import BaseRepository


class ServiceRepository(BaseRepository[Service]):
    """Repository for Service entity."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Service, session)
    
    async def get_active(self, skip: int = 0, limit: int = 100) -> list[Service]:
        """Get all active services."""
        result = await self.session.execute(
            select(Service)
            .where(Service.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_active(self) -> int:
        """Count active services."""
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count())
            .select_from(Service)
            .where(Service.is_active == True)
        )
        return result.scalar() or 0
