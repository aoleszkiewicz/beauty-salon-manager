"""
Pytest fixtures and configuration.
"""
from datetime import time
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.customer import Customer
from app.models.schedule import DayOfWeek, WorkBreak, WorkSchedule
from app.models.service import Service
from app.models.user import User, UserRole

# In-memory SQLite for test isolation
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create tables and provide a session for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session_factory() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """TestClient with overridden DB dependency."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Pre-created admin user."""
    user = User(
        email="admin@salon.com",
        hashed_password=hash_password("adminpass"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def employee_user(db_session: AsyncSession) -> User:
    """Pre-created employee user."""
    user = User(
        email="employee@salon.com",
        hashed_password=hash_password("employeepass"),
        full_name="Test Employee",
        role=UserRole.EMPLOYEE,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def employee_with_schedule(
    db_session: AsyncSession,
    employee_user: User,
) -> User:
    """Employee with Monday-Friday 9-17 schedule."""
    for day in [
        DayOfWeek.MONDAY,
        DayOfWeek.TUESDAY,
        DayOfWeek.WEDNESDAY,
        DayOfWeek.THURSDAY,
        DayOfWeek.FRIDAY,
    ]:
        schedule = WorkSchedule(
            employee_id=employee_user.id,
            day_of_week=day,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        db_session.add(schedule)
        
        # Add lunch break 12:00-13:00
        await db_session.flush()
        lunch_break = WorkBreak(
            schedule_id=schedule.id,
            start_time=time(12, 0),
            end_time=time(13, 0),
        )
        db_session.add(lunch_break)
    
    await db_session.commit()
    await db_session.refresh(employee_user)
    return employee_user


@pytest_asyncio.fixture
async def sample_service(db_session: AsyncSession) -> Service:
    """Haircut service, 30 min, $25."""
    service = Service(
        name="Haircut",
        duration_minutes=30,
        price=25.00,
        is_active=True,
    )
    db_session.add(service)
    await db_session.commit()
    await db_session.refresh(service)
    return service


@pytest_asyncio.fixture
async def sample_customer(db_session: AsyncSession) -> Customer:
    """Sample customer."""
    customer = Customer(
        full_name="John Doe",
        phone="+1234567890",
        email="john@example.com",
        notes="Regular customer",
    )
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)
    return customer


def admin_auth():
    """Return auth tuple for admin user."""
    return ("admin@salon.com", "adminpass")


def employee_auth():
    """Return auth tuple for employee user."""
    return ("employee@salon.com", "employeepass")
