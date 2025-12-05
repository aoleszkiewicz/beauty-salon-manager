"""
Report service for business analytics.
"""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service import Service
from app.models.user import User
from app.models.visit import Visit, VisitStatus
from app.schemas.calendar import (
    EmployeePerformanceItem,
    EmployeePerformanceResponse,
    IncomeReportResponse,
    ServicePopularityItem,
    ServicePopularityResponse,
)


class ReportService:
    """Service for generating business reports."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_income_report(
        self,
        start_date: date,
        end_date: date,
    ) -> IncomeReportResponse:
        """Generate income report for date range."""
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

        # Get completed visits income
        completed_result = await self.session.execute(
            select(
                func.coalesce(func.sum(Visit.price), 0).label("total"),
                func.count(Visit.id).label("count"),
            )
            .where(
                Visit.start_datetime >= start_dt,
                Visit.start_datetime <= end_dt,
                Visit.status == VisitStatus.COMPLETED,
            )
        )
        completed = completed_result.one()

        # Get cancelled count
        cancelled_result = await self.session.execute(
            select(func.count(Visit.id))
            .where(
                Visit.start_datetime >= start_dt,
                Visit.start_datetime <= end_dt,
                Visit.status == VisitStatus.CANCELLED,
            )
        )
        cancelled_count = cancelled_result.scalar() or 0

        return IncomeReportResponse(
            start_date=start_date,
            end_date=end_date,
            total_income=Decimal(str(completed.total)),
            completed_visits=completed.count,
            cancelled_visits=cancelled_count,
        )

    async def get_service_popularity(
        self,
        start_date: date,
        end_date: date,
    ) -> ServicePopularityResponse:
        """Generate service popularity report."""
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

        result = await self.session.execute(
            select(
                Service.id,
                Service.name,
                func.count(Visit.id).label("visit_count"),
                func.coalesce(func.sum(Visit.price), 0).label("total_revenue"),
            )
            .join(Visit, Service.id == Visit.service_id)
            .where(
                Visit.start_datetime >= start_dt,
                Visit.start_datetime <= end_dt,
                Visit.status == VisitStatus.COMPLETED,
            )
            .group_by(Service.id, Service.name)
            .order_by(func.count(Visit.id).desc())
        )

        services = [
            ServicePopularityItem(
                service_id=row.id,
                service_name=row.name,
                visit_count=row.visit_count,
                total_revenue=Decimal(str(row.total_revenue)),
            )
            for row in result.all()
        ]

        return ServicePopularityResponse(
            start_date=start_date,
            end_date=end_date,
            services=services,
        )

    async def get_employee_performance(
        self,
        start_date: date,
        end_date: date,
    ) -> EmployeePerformanceResponse:
        """Generate employee performance report."""
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

        result = await self.session.execute(
            select(
                User.id,
                User.full_name,
                func.count(Visit.id).label("completed_visits"),
                func.coalesce(func.sum(Visit.price), 0).label("total_revenue"),
            )
            .join(Visit, User.id == Visit.employee_id)
            .where(
                Visit.start_datetime >= start_dt,
                Visit.start_datetime <= end_dt,
                Visit.status == VisitStatus.COMPLETED,
            )
            .group_by(User.id, User.full_name)
            .order_by(func.sum(Visit.price).desc())
        )

        employees = [
            EmployeePerformanceItem(
                employee_id=row.id,
                employee_name=row.full_name,
                completed_visits=row.completed_visits,
                total_revenue=Decimal(str(row.total_revenue)),
            )
            for row in result.all()
        ]

        return EmployeePerformanceResponse(
            start_date=start_date,
            end_date=end_date,
            employees=employees,
        )
