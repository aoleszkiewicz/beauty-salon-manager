"""
Visit model for appointments.
"""
import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class VisitStatus(str, enum.Enum):
    """Visit status enumeration."""

    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Visit(Base, TimestampMixin):
    """Visit model representing a booked appointment."""

    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[VisitStatus] = mapped_column(
        Enum(VisitStatus),
        default=VisitStatus.SCHEDULED,
        nullable=False,
    )

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="visits")
    employee: Mapped["User"] = relationship("User", back_populates="visits")
    service: Mapped["Service"] = relationship("Service", back_populates="visits")

    def __repr__(self) -> str:
        return f"<Visit {self.id} {self.start_datetime} ({self.status.value})>"


from app.models.customer import Customer  # noqa: E402, F401
from app.models.service import Service  # noqa: E402, F401
from app.models.user import User  # noqa: E402, F401
