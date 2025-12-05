"""
Schedule and break schemas for request/response validation.
"""
from datetime import time

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.schedule import DayOfWeek


# ============== Request Schemas ==============

class ScheduleCreate(BaseModel):
    """Schema for creating a work schedule."""
    
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    
    @model_validator(mode="after")
    def validate_times(self) -> "ScheduleCreate":
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        return self


class ScheduleUpdate(BaseModel):
    """Schema for updating a work schedule."""
    
    start_time: time | None = None
    end_time: time | None = None
    
    @model_validator(mode="after")
    def validate_times(self) -> "ScheduleUpdate":
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        return self


class BreakCreate(BaseModel):
    """Schema for creating a work break."""
    
    start_time: time
    end_time: time
    
    @model_validator(mode="after")
    def validate_times(self) -> "BreakCreate":
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        return self


# ============== Response Schemas ==============

class BreakResponse(BaseModel):
    """Schema for break response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    start_time: time
    end_time: time


class ScheduleResponse(BaseModel):
    """Schema for schedule response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    employee_id: int
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    breaks: list[BreakResponse] = Field(default_factory=list)


class ScheduleListResponse(BaseModel):
    """Schema for list of schedules response."""
    
    items: list[ScheduleResponse]
    total: int


class BreakListResponse(BaseModel):
    """Schema for list of breaks response."""
    
    items: list[BreakResponse]
    total: int
