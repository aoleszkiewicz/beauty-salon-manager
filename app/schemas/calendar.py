"""
Calendar and report schemas.
"""
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

# ============== Calendar Schemas ==============

class CalendarEvent(BaseModel):
    """Schema for a calendar event."""

    type: str  # "visit" or "break"
    id: int | None = None
    title: str
    start: datetime
    end: datetime
    color: str


class CalendarResponse(BaseModel):
    """Schema for calendar response."""

    events: list[CalendarEvent]


# ============== Report Schemas ==============

class IncomeReportResponse(BaseModel):
    """Schema for income report."""

    start_date: date
    end_date: date
    total_income: Decimal
    completed_visits: int
    cancelled_visits: int


class ServicePopularityItem(BaseModel):
    """Single service in popularity report."""

    service_id: int
    service_name: str
    visit_count: int
    total_revenue: Decimal


class ServicePopularityResponse(BaseModel):
    """Schema for service popularity report."""

    start_date: date
    end_date: date
    services: list[ServicePopularityItem]


class EmployeePerformanceItem(BaseModel):
    """Single employee in performance report."""

    employee_id: int
    employee_name: str
    completed_visits: int
    total_revenue: Decimal


class EmployeePerformanceResponse(BaseModel):
    """Schema for employee performance report."""

    start_date: date
    end_date: date
    employees: list[EmployeePerformanceItem]
