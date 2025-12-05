"""
Base repository with common CRUD operations.
"""
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository providing common CRUD operations."""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> ModelType | None:
        """Get a single record by ID."""
        return await self.session.get(self.model, id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Get all records with pagination."""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        """Create a new record."""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        """Update an existing record."""
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        """Delete a record."""
        await self.session.delete(obj)
        await self.session.flush()

    async def count(self) -> int:
        """Count total records."""
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0
