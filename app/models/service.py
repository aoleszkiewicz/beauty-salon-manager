"""
Service model for salon services.
"""
from decimal import Decimal

from sqlalchemy import Boolean, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Service(Base, TimestampMixin):
    """Service model representing salon services (haircut, coloring, etc.)."""

    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    visits: Mapped[list["Visit"]] = relationship(
        "Visit",
        back_populates="service",
    )

    def __repr__(self) -> str:
        return f"<Service {self.name} ({self.duration_minutes}min, ${self.price})>"


from app.models.visit import Visit  # noqa: E402, F401
