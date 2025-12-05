"""
Authentication service for login and user validation.
"""
from app.core.exceptions import UnauthorizedError
from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


class AuthService:
    """Service for authentication operations."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def authenticate(self, email: str, password: str) -> User:
        """Authenticate user with email and password."""
        user = await self.user_repository.get_by_email(email)

        if not user:
            raise UnauthorizedError("Invalid email or password")

        if not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("User account is deactivated")

        return user

    async def create_initial_admin(
        self,
        email: str,
        password: str,
        full_name: str,
    ) -> User:
        """Create initial admin user if no users exist."""
        # Check if any user exists
        existing = await self.user_repository.get_by_email(email)
        if existing:
            raise ValueError("User already exists")

        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=UserRole.ADMIN,
            is_active=True,
        )

        return await self.user_repository.create(user)
