"""
User repository for data access.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User entity."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_active_employees(self) -> list[User]:
        """Get all active employees."""
        result = await self.session.execute(
            select(User).where(
                User.is_active,
                User.role == UserRole.EMPLOYEE
            )
        )
        return list(result.scalars().all())

    async def get_all_active(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all active users with pagination."""
        result = await self.session.execute(
            select(User)
            .where(User.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_active(self) -> int:
        """Count active users."""
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count())
            .select_from(User)
            .where(User.is_active)
        )
        return result.scalar() or 0
