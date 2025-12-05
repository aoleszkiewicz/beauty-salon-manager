"""
Customer controller.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import (
    CurrentAdmin,
    CurrentUser,
    get_customer_service,
)
from app.schemas.customer import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)
from app.schemas.user import MessageResponse
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new customer",
)
async def create_customer(
    data: CustomerCreate,
    _user: CurrentUser,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
) -> CustomerResponse:
    """Create a new customer."""
    customer = await customer_service.create_customer(data)
    return CustomerResponse.model_validate(customer)


@router.get(
    "",
    response_model=CustomerListResponse,
    summary="List customers",
)
async def list_customers(
    _user: CurrentUser,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    search: str | None = Query(None, description="Search by name, email, or phone"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> CustomerListResponse:
    """List customers with optional search."""
    customers, total = await customer_service.list_customers(search, skip, limit)
    return CustomerListResponse(
        items=[CustomerResponse.model_validate(c) for c in customers],
        total=total,
    )


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Get customer details",
)
async def get_customer(
    customer_id: int,
    _user: CurrentUser,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
) -> CustomerResponse:
    """Get customer by ID."""
    customer = await customer_service.get_customer(customer_id)
    return CustomerResponse.model_validate(customer)


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update customer",
)
async def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    _user: CurrentUser,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
) -> CustomerResponse:
    """Update customer details."""
    customer = await customer_service.update_customer(customer_id, data)
    return CustomerResponse.model_validate(customer)


@router.delete(
    "/{customer_id}",
    response_model=MessageResponse,
    summary="Delete customer",
)
async def delete_customer(
    customer_id: int,
    _admin: CurrentAdmin,
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
) -> MessageResponse:
    """Delete a customer. Admin only."""
    await customer_service.delete_customer(customer_id)
    return MessageResponse(message="Customer deleted successfully.")
