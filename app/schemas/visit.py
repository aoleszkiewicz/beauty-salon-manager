"""
Visit schemas for request/response validation.
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.visit import VisitStatus
from app.schemas.customer import CustomerResponse
from app.schemas.service import ServiceResponse
from app.schemas.user import UserResponse

# ============== Request Schemas ==============

class VisitCreate(BaseModel):
    """Schema for creating a visit (booking)."""

    customer_id: int
    employee_id: int
    service_id: int
    start_datetime: datetime
    comment: str | None = None


class VisitUpdate(BaseModel):
    """Schema for updating a visit (rescheduling)."""

    customer_id: int | None = None
    employee_id: int | None = None
    service_id: int | None = None
    start_datetime: datetime | None = None
    comment: str | None = None


class VisitStatusUpdate(BaseModel):
    """Schema for updating visit status."""

    status: VisitStatus


# ============== Response Schemas ==============

class VisitResponse(BaseModel):
    """Schema for visit response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    employee_id: int
    service_id: int
    start_datetime: datetime
    end_datetime: datetime
    price: Decimal
    comment: str | None
    status: VisitStatus


class VisitDetailResponse(BaseModel):
    """Schema for detailed visit response with related entities."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    customer: CustomerResponse
    employee: UserResponse
    service: ServiceResponse
    start_datetime: datetime
    end_datetime: datetime
    price: Decimal
    comment: str | None
    status: VisitStatus


class VisitListResponse(BaseModel):
    """Schema for list of visits response."""

    items: list[VisitResponse]
    total: int
