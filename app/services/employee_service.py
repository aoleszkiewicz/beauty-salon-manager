"""
Employee service for user management.
"""
from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class EmployeeService:
    """Service for employee (user) management."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def create_employee(self, data: UserCreate) -> User:
        """Create a new employee."""
        # Check email uniqueness
        existing = await self.user_repository.get_by_email(data.email)
        if existing:
            raise ConflictError(f"User with email {data.email} already exists")
        
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role=data.role,
            is_active=True,
        )
        
        return await self.user_repository.create(user)
    
    async def get_employee(self, employee_id: int) -> User:
        """Get employee by ID."""
        user = await self.user_repository.get_by_id(employee_id)
        if not user:
            raise NotFoundError("Employee", employee_id)
        return user
    
    async def list_employees(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[User], int]:
        """List all active employees."""
        users = await self.user_repository.get_all_active(skip, limit)
        count = await self.user_repository.count_active()
        return users, count
    
    async def update_employee(self, employee_id: int, data: UserUpdate) -> User:
        """Update employee details."""
        user = await self.get_employee(employee_id)
        
        if data.email is not None and data.email != user.email:
            existing = await self.user_repository.get_by_email(data.email)
            if existing:
                raise ConflictError(f"User with email {data.email} already exists")
            user.email = data.email
        
        if data.password is not None:
            user.hashed_password = hash_password(data.password)
        
        if data.full_name is not None:
            user.full_name = data.full_name
        
        if data.role is not None:
            user.role = data.role
        
        if data.is_active is not None:
            user.is_active = data.is_active
        
        return await self.user_repository.update(user)
    
    async def deactivate_employee(self, employee_id: int) -> User:
        """Deactivate (soft delete) an employee."""
        user = await self.get_employee(employee_id)
        user.is_active = False
        return await self.user_repository.update(user)
