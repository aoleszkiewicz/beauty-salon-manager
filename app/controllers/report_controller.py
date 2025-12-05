"""
Report controller.
"""
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentAdmin, get_report_service
from app.schemas.calendar import (
    EmployeePerformanceResponse,
    IncomeReportResponse,
    ServicePopularityResponse,
)
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/income",
    response_model=IncomeReportResponse,
    summary="Get income report",
)
async def get_income_report(
    _admin: CurrentAdmin,
    report_service: Annotated[ReportService, Depends(get_report_service)],
    start_date: date = Query(..., description="Start date (inclusive)"),
    end_date: date = Query(..., description="End date (inclusive)"),
) -> IncomeReportResponse:
    """Get total income report for date range. Admin only."""
    return await report_service.get_income_report(start_date, end_date)


@router.get(
    "/services",
    response_model=ServicePopularityResponse,
    summary="Get service popularity report",
)
async def get_service_popularity(
    _admin: CurrentAdmin,
    report_service: Annotated[ReportService, Depends(get_report_service)],
    start_date: date = Query(..., description="Start date (inclusive)"),
    end_date: date = Query(..., description="End date (inclusive)"),
) -> ServicePopularityResponse:
    """Get service popularity breakdown. Admin only."""
    return await report_service.get_service_popularity(start_date, end_date)


@router.get(
    "/employees",
    response_model=EmployeePerformanceResponse,
    summary="Get employee performance report",
)
async def get_employee_performance(
    _admin: CurrentAdmin,
    report_service: Annotated[ReportService, Depends(get_report_service)],
    start_date: date = Query(..., description="Start date (inclusive)"),
    end_date: date = Query(..., description="End date (inclusive)"),
) -> EmployeePerformanceResponse:
    """Get per-employee performance report. Admin only."""
    return await report_service.get_employee_performance(start_date, end_date)
