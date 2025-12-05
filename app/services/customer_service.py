"""
Customer service for customer management.
"""
from app.core.exceptions import NotFoundError
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    """Service for customer management."""

    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    async def create_customer(self, data: CustomerCreate) -> Customer:
        """Create a new customer."""
        customer = Customer(
            full_name=data.full_name,
            phone=data.phone,
            email=data.email,
            notes=data.notes,
        )
        return await self.customer_repository.create(customer)

    async def get_customer(self, customer_id: int) -> Customer:
        """Get customer by ID."""
        customer = await self.customer_repository.get_by_id(customer_id)
        if not customer:
            raise NotFoundError("Customer", customer_id)
        return customer

    async def list_customers(
        self,
        search: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Customer], int]:
        """List customers with optional search."""
        customers = await self.customer_repository.search(search, skip, limit)
        count = await self.customer_repository.count_search(search)
        return customers, count

    async def update_customer(self, customer_id: int, data: CustomerUpdate) -> Customer:
        """Update customer details."""
        customer = await self.get_customer(customer_id)

        if data.full_name is not None:
            customer.full_name = data.full_name
        if data.phone is not None:
            customer.phone = data.phone
        if data.email is not None:
            customer.email = data.email
        if data.notes is not None:
            customer.notes = data.notes

        return await self.customer_repository.update(customer)

    async def delete_customer(self, customer_id: int) -> None:
        """Delete a customer."""
        customer = await self.get_customer(customer_id)
        await self.customer_repository.delete(customer)
