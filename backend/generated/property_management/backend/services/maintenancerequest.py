"""
MaintenanceRequest Service
Generated on: 2025-09-25
Domain: property_management
"""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.maintenance_request import Maintenancerequest
from app.schemas.maintenance_request import (
    MaintenancerequestCreate,
    MaintenancerequestUpdate
)
from app.core.exceptions import NotFoundError, ValidationError


class MaintenancerequestService:
    """Service class for Maintenancerequest operations."""
    
    async def list_maintenance_requests(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Maintenancerequest], int]:
        """
        List maintenance_requests with pagination, filtering, and search.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of filters to apply
            search: Search term for full-text search
            
        Returns:
            Tuple of (maintenance_requests, total_count)
        """
        query = select(Maintenancerequest)
        count_query = select(func.count(Maintenancerequest.id))
        
        # Apply filters
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if hasattr(Maintenancerequest, key) and value is not None:
                    filter_conditions.append(getattr(Maintenancerequest, key) == value)
            
            if filter_conditions:
                query = query.where(and_(*filter_conditions))
                count_query = count_query.where(and_(*filter_conditions))
        
        # Apply search
        if search:
            search_conditions = []
            # Default search in common text fields
            search_conditions.append(Maintenancerequest.title.ilike(f"%{search}%"))
            search_conditions.append(Maintenancerequest.description.ilike(f"%{search}%"))
            
            if search_conditions:
                search_filter = or_(*search_conditions)
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)
        
        # Apply ordering
        query = query.order_by(Maintenancerequest.created_at.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        maintenance_requests = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        return maintenance_requests, total or 0
    
    async def get_maintenance_request(
        self, 
        db: AsyncSession, 
        maintenance_request_id: UUID,
        load_relationships: bool = False
    ) -> Optional[Maintenancerequest]:
        """
        Get a maintenance_request by ID.
        
        Args:
            db: Database session
            maintenance_request_id: Maintenancerequest ID
            load_relationships: Whether to load related objects
            
        Returns:
            Maintenancerequest instance or None if not found
        """
        query = select(Maintenancerequest).where(Maintenancerequest.id == maintenance_request_id)
        
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_maintenance_request(
        self,
        db: AsyncSession,
        maintenance_request_create: MaintenancerequestCreate,
        created_by: Optional[UUID] = None
    ) -> Maintenancerequest:
        """
        Create a new maintenance_request.
        
        Args:
            db: Database session
            maintenance_request_create: Maintenancerequest creation data
            created_by: ID of the user creating the maintenance_request
            
        Returns:
            Created Maintenancerequest instance
        """
        # Validate data
        await self._validate_maintenance_request_create(db, maintenance_request_create)
        
        # Create model instance
        maintenance_request_data = maintenance_request_create.model_dump(exclude_unset=True)
        
        maintenance_request = Maintenancerequest(**maintenance_request_data)
        
        db.add(maintenance_request)
        await db.commit()
        await db.refresh(maintenance_request)
        
        return maintenance_request
    
    async def update_maintenance_request(
        self,
        db: AsyncSession,
        maintenance_request: Maintenancerequest,
        maintenance_request_update: MaintenancerequestUpdate
    ) -> Maintenancerequest:
        """
        Update an existing maintenance_request.
        
        Args:
            db: Database session
            maintenance_request: Maintenancerequest instance to update
            maintenance_request_update: Update data
            
        Returns:
            Updated Maintenancerequest instance
        """
        # Validate update data
        await self._validate_maintenance_request_update(db, maintenance_request, maintenance_request_update)
        
        # Apply updates
        update_data = maintenance_request_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(maintenance_request, field, value)
        
        await db.commit()
        await db.refresh(maintenance_request)
        
        return maintenance_request
    
    async def delete_maintenance_request(
        self, 
        db: AsyncSession, 
        maintenance_request: Maintenancerequest
    ) -> None:
        """
        Delete a maintenance_request.
        
        Args:
            db: Database session
            maintenance_request: Maintenancerequest instance to delete
        """
        # Hard delete
        await db.delete(maintenance_request)
        await db.commit()
    
    async def bulk_create_maintenance_requests(
        self,
        db: AsyncSession,
        maintenance_requests_create: List[MaintenancerequestCreate],
        created_by: Optional[UUID] = None
    ) -> List[Maintenancerequest]:
        """
        Create multiple maintenance_requests in a single transaction.
        
        Args:
            db: Database session
            maintenance_requests_create: List of Maintenancerequest creation data
            created_by: ID of the user creating the maintenance_requests
            
        Returns:
            List of created Maintenancerequest instances
        """
        maintenance_requests = []
        
        for maintenance_request_create in maintenance_requests_create:
            # Validate each item
            await self._validate_maintenance_request_create(db, maintenance_request_create)
            
            # Create model instance
            maintenance_request_data = maintenance_request_create.model_dump(exclude_unset=True)
            
            maintenance_request = Maintenancerequest(**maintenance_request_data)
            maintenance_requests.append(maintenance_request)
        
        db.add_all(maintenance_requests)
        await db.commit()
        
        # Refresh all instances
        for maintenance_request in maintenance_requests:
            await db.refresh(maintenance_request)
        
        return maintenance_requests
    
    # Validation methods
    async def _validate_maintenance_request_create(
        self,
        db: AsyncSession,
        maintenance_request_create: MaintenancerequestCreate
    ) -> None:
        """Validate maintenance_request creation data."""
    
    async def _validate_maintenance_request_update(
        self,
        db: AsyncSession,
        maintenance_request: Maintenancerequest,
        maintenance_request_update: MaintenancerequestUpdate
    ) -> None:
        """Validate maintenance_request update data."""
