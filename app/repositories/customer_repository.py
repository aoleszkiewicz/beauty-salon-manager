"""
Customer repository for data access.
"""
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    """Repository for Customer entity."""

    def __init__(self, session: AsyncSession):
        super().__init__(Customer, session)

    async def search(
        self,
        query: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Customer]:
        """Search customers by name, email, or phone."""
        stmt = select(Customer)

        if query:
            search_pattern = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Customer.full_name.ilike(search_pattern),
                    Customer.email.ilike(search_pattern),
                    Customer.phone.ilike(search_pattern),
                )
            )

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_search(self, query: str | None = None) -> int:
        """Count customers matching search query."""
        from sqlalchemy import func

        stmt = select(func.count()).select_from(Customer)

        if query:
            search_pattern = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Customer.full_name.ilike(search_pattern),
                    Customer.email.ilike(search_pattern),
                    Customer.phone.ilike(search_pattern),
                )
            )

        result = await self.session.execute(stmt)
        return result.scalar() or 0
