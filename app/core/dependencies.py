"""
Dependency injection for FastAPI.
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import verify_password
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.customer_repository import CustomerRepository
from app.repositories.schedule_repository import BreakRepository, ScheduleRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.user_repository import UserRepository
from app.repositories.visit_repository import VisitRepository
from app.services.auth_service import AuthService
from app.services.availability_service import AvailabilityService
from app.services.calendar_service import CalendarService
from app.services.customer_service import CustomerService
from app.services.employee_service import EmployeeService
from app.services.report_service import ReportService
from app.services.schedule_service import ScheduleService
from app.services.service_service import ServiceService
from app.services.visit_service import VisitService

# HTTP Basic auth scheme
security = HTTPBasic()


# ============== Repository Dependencies ==============

async def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRepository:
    return UserRepository(db)


async def get_service_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ServiceRepository:
    return ServiceRepository(db)


async def get_customer_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CustomerRepository:
    return CustomerRepository(db)


async def get_schedule_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ScheduleRepository:
    return ScheduleRepository(db)


async def get_break_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BreakRepository:
    return BreakRepository(db)


async def get_visit_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VisitRepository:
    return VisitRepository(db)


# ============== Service Dependencies ==============

async def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(user_repo)


async def get_employee_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> EmployeeService:
    return EmployeeService(user_repo)


async def get_customer_service(
    customer_repo: Annotated[CustomerRepository, Depends(get_customer_repository)],
) -> CustomerService:
    return CustomerService(customer_repo)


async def get_service_service(
    service_repo: Annotated[ServiceRepository, Depends(get_service_repository)],
) -> ServiceService:
    return ServiceService(service_repo)


async def get_schedule_service(
    schedule_repo: Annotated[ScheduleRepository, Depends(get_schedule_repository)],
    break_repo: Annotated[BreakRepository, Depends(get_break_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> ScheduleService:
    return ScheduleService(schedule_repo, break_repo, user_repo)


async def get_availability_service(
    schedule_repo: Annotated[ScheduleRepository, Depends(get_schedule_repository)],
    visit_repo: Annotated[VisitRepository, Depends(get_visit_repository)],
) -> AvailabilityService:
    return AvailabilityService(schedule_repo, visit_repo)


async def get_visit_service(
    visit_repo: Annotated[VisitRepository, Depends(get_visit_repository)],
    customer_repo: Annotated[CustomerRepository, Depends(get_customer_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    service_repo: Annotated[ServiceRepository, Depends(get_service_repository)],
    availability_svc: Annotated[AvailabilityService, Depends(get_availability_service)],
) -> VisitService:
    return VisitService(
        visit_repo, customer_repo, user_repo, service_repo, availability_svc
    )


async def get_calendar_service(
    visit_repo: Annotated[VisitRepository, Depends(get_visit_repository)],
    schedule_repo: Annotated[ScheduleRepository, Depends(get_schedule_repository)],
) -> CalendarService:
    return CalendarService(visit_repo, schedule_repo)


async def get_report_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReportService:
    return ReportService(db)


# ============== Auth Dependencies ==============

async def get_current_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    """Get current authenticated user from HTTP Basic credentials."""
    user = await user_repo.get_by_email(credentials.username)
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise UnauthorizedError("Invalid credentials")
    
    if not user.is_active:
        raise UnauthorizedError("User account is deactivated")
    
    return user


async def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure current user is an admin."""
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenError("Admin access required")
    return current_user


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]
