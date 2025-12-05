"""
Unit tests for availability service - Core scheduling logic.
These tests should be written FIRST (TDD approach).
"""
from datetime import datetime, time, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import SlotUnavailableError
from app.models.schedule import DayOfWeek, WorkBreak, WorkSchedule
from app.models.visit import Visit, VisitStatus
from app.services.availability_service import AvailabilityService


@pytest.fixture
def mock_schedule_repo():
    """Mock schedule repository."""
    return AsyncMock()


@pytest.fixture
def mock_visit_repo():
    """Mock visit repository."""
    return AsyncMock()


@pytest.fixture
def availability_service(mock_schedule_repo, mock_visit_repo):
    """Create availability service with mocked dependencies."""
    return AvailabilityService(mock_schedule_repo, mock_visit_repo)


@pytest.fixture
def monday_schedule():
    """Sample Monday 9-17 schedule with lunch break."""
    schedule = MagicMock(spec=WorkSchedule)
    schedule.start_time = time(9, 0)
    schedule.end_time = time(17, 0)
    
    lunch_break = MagicMock(spec=WorkBreak)
    lunch_break.start_time = time(12, 0)
    lunch_break.end_time = time(13, 0)
    schedule.breaks = [lunch_break]
    
    return schedule


class TestSlotWithinWorkingHours:
    """Test availability within working hours."""
    
    @pytest.mark.asyncio
    async def test_slot_within_working_hours(
        self,
        availability_service,
        mock_schedule_repo,
        mock_visit_repo,
        monday_schedule,
    ):
        """Valid slot within working hours should be available."""
        # 2024-01-15 is a Monday
        start_dt = datetime(2024, 1, 15, 10, 0)
        
        mock_schedule_repo.get_by_employee_and_day.return_value = monday_schedule
        mock_visit_repo.get_overlapping.return_value = []
        
        result = await availability_service.is_slot_available(
            employee_id=1,
            start_datetime=start_dt,
            duration_minutes=30,
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_slot_outside_working_hours_before(
        self,
        availability_service,
        mock_schedule_repo,
        monday_schedule,
    ):
        """Slot starting before working hours should fail."""
        start_dt = datetime(2024, 1, 15, 8, 0)  # Before 9:00
        
        mock_schedule_repo.get_by_employee_and_day.return_value = monday_schedule
        
        with pytest.raises(SlotUnavailableError) as exc_info:
            await availability_service.is_slot_available(
                employee_id=1,
                start_datetime=start_dt,
                duration_minutes=30,
            )
        
        assert "before work hours" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_slot_outside_working_hours_after(
        self,
        availability_service,
        mock_schedule_repo,
        monday_schedule,
    ):
        """Slot ending after working hours should fail."""
        start_dt = datetime(2024, 1, 15, 16, 45)  # Ends at 17:15
        
        mock_schedule_repo.get_by_employee_and_day.return_value = monday_schedule
        
        with pytest.raises(SlotUnavailableError) as exc_info:
            await availability_service.is_slot_available(
                employee_id=1,
                start_datetime=start_dt,
                duration_minutes=30,
            )
        
        assert "after work hours" in str(exc_info.value.detail)


class TestSlotOnDayOff:
    """Test availability on days without schedule."""
    
    @pytest.mark.asyncio
    async def test_slot_on_day_off(
        self,
        availability_service,
        mock_schedule_repo,
    ):
        """Slot on a day without schedule should fail."""
        # 2024-01-14 is a Sunday
        start_dt = datetime(2024, 1, 14, 10, 0)
        
        mock_schedule_repo.get_by_employee_and_day.return_value = None
        
        with pytest.raises(SlotUnavailableError) as exc_info:
            await availability_service.is_slot_available(
                employee_id=1,
                start_datetime=start_dt,
                duration_minutes=30,
            )
        
        assert "no schedule" in str(exc_info.value.detail)


class TestSlotOverlapsBreak:
    """Test availability with break conflicts."""
    
    @pytest.mark.asyncio
    async def test_slot_overlaps_break(
        self,
        availability_service,
        mock_schedule_repo,
        monday_schedule,
    ):
        """Slot overlapping with break should fail."""
        start_dt = datetime(2024, 1, 15, 11, 45)  # Overlaps 12:00-13:00 break
        
        mock_schedule_repo.get_by_employee_and_day.return_value = monday_schedule
        
        with pytest.raises(SlotUnavailableError) as exc_info:
            await availability_service.is_slot_available(
                employee_id=1,
                start_datetime=start_dt,
                duration_minutes=30,
            )
        
        assert "overlaps with break" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_slot_adjacent_to_break_before(
        self,
        availability_service,
        mock_schedule_repo,
        mock_visit_repo,
        monday_schedule,
    ):
        """Slot ending exactly when break starts is OK."""
        start_dt = datetime(2024, 1, 15, 11, 30)  # Ends at 12:00
        
        mock_schedule_repo.get_by_employee_and_day.return_value = monday_schedule
        mock_visit_repo.get_overlapping.return_value = []
        
        result = await availability_service.is_slot_available(
            employee_id=1,
            start_datetime=start_dt,
            duration_minutes=30,
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_slot_adjacent_to_break_after(
        self,
        availability_service,
        mock_schedule_repo,
        mock_visit_repo,
        monday_schedule,
    ):
        """Slot starting exactly when break ends is OK."""
        start_dt = datetime(2024, 1, 15, 13, 0)  # Starts at 13:00
        
        mock_schedule_repo.get_by_employee_and_day.return_value = monday_schedule
        mock_visit_repo.get_overlapping.return_value = []
        
        result = await availability_service.is_slot_available(
            employee_id=1,
            start_datetime=start_dt,
            duration_minutes=30,
        )
        
        assert result is True


class TestSlotOverlapsVisit:
    """Test availability with visit conflicts."""
    
    @pytest.mark.asyncio
    async def test_slot_overlaps_existing_visit(
        self,
        availability_service,
        mock_schedule_repo,
        mock_visit_repo,
        monday_schedule,
    ):
        """Slot overlapping with existing visit should fail."""
        start_dt = datetime(2024, 1, 15, 10, 0)
        
        existing_visit = MagicMock(spec=Visit)
        existing_visit.start_datetime = datetime(2024, 1, 15, 10, 15)
        existing_visit.end_datetime = datetime(2024, 1, 15, 10, 45)
        
        mock_schedule_repo.get_by_employee_and_day.return_value = monday_schedule
        mock_visit_repo.get_overlapping.return_value = [existing_visit]
        
        with pytest.raises(SlotUnavailableError) as exc_info:
            await availability_service.is_slot_available(
                employee_id=1,
                start_datetime=start_dt,
                duration_minutes=30,
            )
        
        assert "conflicts with existing visit" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_slot_adjacent_to_visit_no_gap(
        self,
        availability_service,
        mock_schedule_repo,
        mock_visit_repo,
        monday_schedule,
    ):
        """Back-to-back booking is allowed."""
        start_dt = datetime(2024, 1, 15, 10, 30)  # Starts when previous ends
        
        mock_schedule_repo.get_by_employee_and_day.return_value = monday_schedule
        mock_visit_repo.get_overlapping.return_value = []  # No overlap
        
        result = await availability_service.is_slot_available(
            employee_id=1,
            start_datetime=start_dt,
            duration_minutes=30,
        )
        
        assert result is True


class TestSlotSpansMidnight:
    """Test slots that span midnight."""
    
    @pytest.mark.asyncio
    async def test_slot_spans_midnight(
        self,
        availability_service,
    ):
        """Slot spanning midnight should fail."""
        start_dt = datetime(2024, 1, 15, 23, 45)  # Ends next day
        
        with pytest.raises(SlotUnavailableError) as exc_info:
            await availability_service.is_slot_available(
                employee_id=1,
                start_datetime=start_dt,
                duration_minutes=30,
            )
        
        assert "span midnight" in str(exc_info.value.detail)


class TestSlotDurationExceedsHours:
    """Test slots with duration exceeding remaining hours."""
    
    @pytest.mark.asyncio
    async def test_slot_duration_exceeds_remaining_hours(
        self,
        availability_service,
        mock_schedule_repo,
        monday_schedule,
    ):
        """Slot extending past end of day should fail."""
        start_dt = datetime(2024, 1, 15, 16, 0)  # 16:00 + 90min = 17:30
        
        mock_schedule_repo.get_by_employee_and_day.return_value = monday_schedule
        
        with pytest.raises(SlotUnavailableError) as exc_info:
            await availability_service.is_slot_available(
                employee_id=1,
                start_datetime=start_dt,
                duration_minutes=90,
            )
        
        assert "after work hours" in str(exc_info.value.detail)
