"""
Service service for salon services management.
"""
from app.core.exceptions import NotFoundError
from app.models.service import Service
from app.repositories.service_repository import ServiceRepository
from app.schemas.service import ServiceCreate, ServiceUpdate


class ServiceService:
    """Service for salon services management."""
    
    def __init__(self, service_repository: ServiceRepository):
        self.service_repository = service_repository
    
    async def create_service(self, data: ServiceCreate) -> Service:
        """Create a new service."""
        service = Service(
            name=data.name,
            duration_minutes=data.duration_minutes,
            price=data.price,
            is_active=True,
        )
        return await self.service_repository.create(service)
    
    async def get_service(self, service_id: int) -> Service:
        """Get service by ID."""
        service = await self.service_repository.get_by_id(service_id)
        if not service:
            raise NotFoundError("Service", service_id)
        return service
    
    async def list_services(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> tuple[list[Service], int]:
        """List services with optional active filter."""
        if active_only:
            services = await self.service_repository.get_active(skip, limit)
            count = await self.service_repository.count_active()
        else:
            services = await self.service_repository.get_all(skip, limit)
            count = await self.service_repository.count()
        return services, count
    
    async def update_service(self, service_id: int, data: ServiceUpdate) -> Service:
        """Update service details."""
        service = await self.get_service(service_id)
        
        if data.name is not None:
            service.name = data.name
        if data.duration_minutes is not None:
            service.duration_minutes = data.duration_minutes
        if data.price is not None:
            service.price = data.price
        if data.is_active is not None:
            service.is_active = data.is_active
        
        return await self.service_repository.update(service)
    
    async def deactivate_service(self, service_id: int) -> Service:
        """Deactivate (soft delete) a service."""
        service = await self.get_service(service_id)
        service.is_active = False
        return await self.service_repository.update(service)
