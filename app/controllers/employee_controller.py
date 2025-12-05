"""
Employee controller.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import (
    CurrentAdmin,
    CurrentUser,
    get_employee_service,
)
from app.schemas.user import (
    MessageResponse,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new employee",
)
async def create_employee(
    data: UserCreate,
    _admin: CurrentAdmin,
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> UserResponse:
    """Create a new employee. Admin only."""
    employee = await employee_service.create_employee(data)
    return UserResponse.model_validate(employee)


@router.get(
    "",
    response_model=UserListResponse,
    summary="List all employees",
)
async def list_employees(
    _user: CurrentUser,
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> UserListResponse:
    """List all active employees."""
    employees, total = await employee_service.list_employees(skip, limit)
    return UserListResponse(
        items=[UserResponse.model_validate(e) for e in employees],
        total=total,
    )


@router.get(
    "/{employee_id}",
    response_model=UserResponse,
    summary="Get employee details",
)
async def get_employee(
    employee_id: int,
    _user: CurrentUser,
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> UserResponse:
    """Get employee by ID."""
    employee = await employee_service.get_employee(employee_id)
    return UserResponse.model_validate(employee)


@router.put(
    "/{employee_id}",
    response_model=UserResponse,
    summary="Update employee",
)
async def update_employee(
    employee_id: int,
    data: UserUpdate,
    _admin: CurrentAdmin,
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> UserResponse:
    """Update employee details. Admin only."""
    employee = await employee_service.update_employee(employee_id, data)
    return UserResponse.model_validate(employee)


@router.delete(
    "/{employee_id}",
    response_model=MessageResponse,
    summary="Deactivate employee",
)
async def deactivate_employee(
    employee_id: int,
    _admin: CurrentAdmin,
    employee_service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> MessageResponse:
    """Deactivate (soft delete) an employee. Admin only."""
    await employee_service.deactivate_employee(employee_id)
    return MessageResponse(message="Employee deactivated successfully.")
