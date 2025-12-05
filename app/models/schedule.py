"""
Schedule models for employee work hours and breaks.
"""
import enum
from datetime import time

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DayOfWeek(str, enum.Enum):
    """Days of the week enumeration."""
    
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class WorkSchedule(Base):
    """Work schedule defining employee working hours for a specific day."""
    
    __tablename__ = "work_schedules"
    __table_args__ = (
        UniqueConstraint("employee_id", "day_of_week", name="uq_employee_day"),
        CheckConstraint("start_time < end_time", name="ck_schedule_times"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_of_week: Mapped[DayOfWeek] = mapped_column(Enum(DayOfWeek), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    
    # Relationships
    employee: Mapped["User"] = relationship("User", back_populates="schedules")
    breaks: Mapped[list["WorkBreak"]] = relationship(
        "WorkBreak",
        back_populates="schedule",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<WorkSchedule {self.day_of_week.value} {self.start_time}-{self.end_time}>"


class WorkBreak(Base):
    """Break within a work schedule."""
    
    __tablename__ = "work_breaks"
    __table_args__ = (
        CheckConstraint("start_time < end_time", name="ck_break_times"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("work_schedules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    
    # Relationships
    schedule: Mapped["WorkSchedule"] = relationship("WorkSchedule", back_populates="breaks")
    
    def __repr__(self) -> str:
        return f"<WorkBreak {self.start_time}-{self.end_time}>"


from app.models.user import User  # noqa: E402, F401
