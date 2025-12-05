"""
Beauty Salon Manager API - Main Application Entry Point
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers import (
    auth_controller,
    calendar_controller,
    customer_controller,
    employee_controller,
    report_controller,
    schedule_controller,
    service_controller,
    visit_controller,
)
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Ensure data directory exists for SQLite
    os.makedirs("data", exist_ok=True)
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Cleanup
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Beauty Salon Manager API - Manage appointments, employees, services, and reporting.
    
    ## Features
    - **Employee Management**: Create and manage salon staff
    - **Customer Database**: Maintain client information
    - **Service Catalog**: Define services with pricing and duration
    - **Scheduling**: Work schedules with breaks per employee
    - **Appointments**: Book visits with availability validation
    - **Calendar**: Aggregated view of appointments and breaks
    - **Reports**: Income, service popularity, and employee performance
    
    ## Authentication
    This API uses HTTP Basic Authentication. Include your email and password
    in the Authorization header for all authenticated endpoints.
    """,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_controller.router, prefix="/api/v1")
app.include_router(employee_controller.router, prefix="/api/v1")
app.include_router(customer_controller.router, prefix="/api/v1")
app.include_router(service_controller.router, prefix="/api/v1")
app.include_router(schedule_controller.router, prefix="/api/v1")
app.include_router(schedule_controller.break_router, prefix="/api/v1")
app.include_router(visit_controller.router, prefix="/api/v1")
app.include_router(calendar_controller.router, prefix="/api/v1")
app.include_router(report_controller.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}
