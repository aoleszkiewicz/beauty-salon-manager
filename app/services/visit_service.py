"""
Visit service for appointment booking and management.
"""
from datetime import date, timedelta

from app.core.exceptions import NotFoundError, ValidationError
from app.models.visit import Visit, VisitStatus
from app.repositories.customer_repository import CustomerRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.user_repository import UserRepository
from app.repositories.visit_repository import VisitRepository
from app.schemas.visit import VisitCreate, VisitStatusUpdate, VisitUpdate
from app.services.availability_service import AvailabilityService


class VisitService:
    """Service for visit (appointment) management."""
    
    def __init__(
        self,
        visit_repository: VisitRepository,
        customer_repository: CustomerRepository,
        user_repository: UserRepository,
        service_repository: ServiceRepository,
        availability_service: AvailabilityService,
    ):
        self.visit_repository = visit_repository
        self.customer_repository = customer_repository
        self.user_repository = user_repository
        self.service_repository = service_repository
        self.availability_service = availability_service
    
    async def create_visit(self, data: VisitCreate) -> Visit:
        """Book a new visit."""
        # Verify customer exists
        customer = await self.customer_repository.get_by_id(data.customer_id)
        if not customer:
            raise NotFoundError("Customer", data.customer_id)
        
        # Verify employee exists
        employee = await self.user_repository.get_by_id(data.employee_id)
        if not employee:
            raise NotFoundError("Employee", data.employee_id)
        
        # Verify service exists and is active
        service = await self.service_repository.get_by_id(data.service_id)
        if not service:
            raise NotFoundError("Service", data.service_id)
        if not service.is_active:
            raise ValidationError("Service is not active")
        
        # Check availability (will raise SlotUnavailableError if not available)
        await self.availability_service.is_slot_available(
            data.employee_id,
            data.start_datetime,
            service.duration_minutes,
        )
        
        # Calculate end time and create visit
        end_datetime = data.start_datetime + timedelta(minutes=service.duration_minutes)
        
        visit = Visit(
            customer_id=data.customer_id,
            employee_id=data.employee_id,
            service_id=data.service_id,
            start_datetime=data.start_datetime,
            end_datetime=end_datetime,
            price=service.price,  # Snapshot current price
            comment=data.comment,
            status=VisitStatus.SCHEDULED,
        )
        
        return await self.visit_repository.create(visit)
    
    async def get_visit(self, visit_id: int) -> Visit:
        """Get visit by ID."""
        visit = await self.visit_repository.get_by_id(visit_id)
        if not visit:
            raise NotFoundError("Visit", visit_id)
        return visit
    
    async def get_visit_detail(self, visit_id: int) -> Visit:
        """Get visit with all relations loaded."""
        visit = await self.visit_repository.get_with_relations(visit_id)
        if not visit:
            raise NotFoundError("Visit", visit_id)
        return visit
    
    async def list_visits(
        self,
        employee_id: int | None = None,
        customer_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        status: VisitStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Visit], int]:
        """List visits with optional filters."""
        visits = await self.visit_repository.filter_visits(
            employee_id=employee_id,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            skip=skip,
            limit=limit,
        )
        count = await self.visit_repository.count_filter(
            employee_id=employee_id,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
        )
        return visits, count
    
    async def update_visit(self, visit_id: int, data: VisitUpdate) -> Visit:
        """Update/reschedule a visit."""
        visit = await self.get_visit(visit_id)
        
        if visit.status != VisitStatus.SCHEDULED:
            raise ValidationError("Can only update scheduled visits")
        
        # Get current service for duration
        service = await self.service_repository.get_by_id(
            data.service_id or visit.service_id
        )
        if not service:
            raise NotFoundError("Service", data.service_id)
        
        # Check availability if changing time or employee
        if data.start_datetime or data.employee_id:
            start_dt = data.start_datetime or visit.start_datetime
            emp_id = data.employee_id or visit.employee_id
            
            await self.availability_service.is_slot_available(
                emp_id,
                start_dt,
                service.duration_minutes,
                exclude_visit_id=visit_id,
            )
            
            if data.start_datetime:
                visit.start_datetime = data.start_datetime
                visit.end_datetime = data.start_datetime + timedelta(
                    minutes=service.duration_minutes
                )
            
            if data.employee_id:
                visit.employee_id = data.employee_id
        
        # Update other fields
        if data.customer_id:
            customer = await self.customer_repository.get_by_id(data.customer_id)
            if not customer:
                raise NotFoundError("Customer", data.customer_id)
            visit.customer_id = data.customer_id
        
        if data.service_id:
            visit.service_id = data.service_id
            visit.price = service.price
            visit.end_datetime = visit.start_datetime + timedelta(
                minutes=service.duration_minutes
            )
        
        if data.comment is not None:
            visit.comment = data.comment
        
        return await self.visit_repository.update(visit)
    
    async def update_status(
        self,
        visit_id: int,
        data: VisitStatusUpdate,
    ) -> Visit:
        """Update visit status."""
        visit = await self.get_visit(visit_id)
        visit.status = data.status
        return await self.visit_repository.update(visit)
    
    async def cancel_visit(self, visit_id: int) -> None:
        """Cancel and delete a visit."""
        visit = await self.get_visit(visit_id)
        await self.visit_repository.delete(visit)
