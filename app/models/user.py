"""
User model for employees and admins.
"""
import enum

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    """User role enumeration."""
    
    ADMIN = "admin"
    EMPLOYEE = "employee"


class User(Base, TimestampMixin):
    """User model representing salon employees and admins."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.EMPLOYEE,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    schedules: Mapped[list["WorkSchedule"]] = relationship(
        "WorkSchedule",
        back_populates="employee",
        cascade="all, delete-orphan",
    )
    visits: Mapped[list["Visit"]] = relationship(
        "Visit",
        back_populates="employee",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role.value})>"


# Import here to avoid circular imports - models use forward references
from app.models.schedule import WorkSchedule  # noqa: E402, F401
from app.models.visit import Visit  # noqa: E402, F401
