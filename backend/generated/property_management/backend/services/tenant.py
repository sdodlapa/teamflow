"""
Tenant Service
Generated on: 2025-09-25
Domain: property_management
"""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tenant import Tenant
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate
)
from app.core.exceptions import NotFoundError, ValidationError


class TenantService:
    """Service class for Tenant operations."""
    
    async def list_tenants(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Tenant], int]:
        """
        List tenants with pagination, filtering, and search.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of filters to apply
            search: Search term for full-text search
            
        Returns:
            Tuple of (tenants, total_count)
        """
        query = select(Tenant)
        count_query = select(func.count(Tenant.id))
        
        # Apply filters
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if hasattr(Tenant, key) and value is not None:
                    filter_conditions.append(getattr(Tenant, key) == value)
            
            if filter_conditions:
                query = query.where(and_(*filter_conditions))
                count_query = count_query.where(and_(*filter_conditions))
        
        # Apply search
        if search:
            search_conditions = []
            # Default search in common text fields
            search_conditions.append(Tenant.first_name.ilike(f"%{search}%"))
            search_conditions.append(Tenant.last_name.ilike(f"%{search}%"))
            search_conditions.append(Tenant.email.ilike(f"%{search}%"))
            search_conditions.append(Tenant.phone.ilike(f"%{search}%"))
            
            if search_conditions:
                search_filter = or_(*search_conditions)
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)
        
        # Apply ordering
        query = query.order_by(Tenant.created_at.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        tenants = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        return tenants, total or 0
    
    async def get_tenant(
        self, 
        db: AsyncSession, 
        tenant_id: UUID,
        load_relationships: bool = False
    ) -> Optional[Tenant]:
        """
        Get a tenant by ID.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            load_relationships: Whether to load related objects
            
        Returns:
            Tenant instance or None if not found
        """
        query = select(Tenant).where(Tenant.id == tenant_id)
        
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_tenant(
        self,
        db: AsyncSession,
        tenant_create: TenantCreate,
        created_by: Optional[UUID] = None
    ) -> Tenant:
        """
        Create a new tenant.
        
        Args:
            db: Database session
            tenant_create: Tenant creation data
            created_by: ID of the user creating the tenant
            
        Returns:
            Created Tenant instance
        """
        # Validate data
        await self._validate_tenant_create(db, tenant_create)
        
        # Create model instance
        tenant_data = tenant_create.model_dump(exclude_unset=True)
        
        tenant = Tenant(**tenant_data)
        
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
        
        return tenant
    
    async def update_tenant(
        self,
        db: AsyncSession,
        tenant: Tenant,
        tenant_update: TenantUpdate
    ) -> Tenant:
        """
        Update an existing tenant.
        
        Args:
            db: Database session
            tenant: Tenant instance to update
            tenant_update: Update data
            
        Returns:
            Updated Tenant instance
        """
        # Validate update data
        await self._validate_tenant_update(db, tenant, tenant_update)
        
        # Apply updates
        update_data = tenant_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tenant, field, value)
        
        await db.commit()
        await db.refresh(tenant)
        
        return tenant
    
    async def delete_tenant(
        self, 
        db: AsyncSession, 
        tenant: Tenant
    ) -> None:
        """
        Delete a tenant.
        
        Args:
            db: Database session
            tenant: Tenant instance to delete
        """
        # Hard delete
        await db.delete(tenant)
        await db.commit()
    
    async def bulk_create_tenants(
        self,
        db: AsyncSession,
        tenants_create: List[TenantCreate],
        created_by: Optional[UUID] = None
    ) -> List[Tenant]:
        """
        Create multiple tenants in a single transaction.
        
        Args:
            db: Database session
            tenants_create: List of Tenant creation data
            created_by: ID of the user creating the tenants
            
        Returns:
            List of created Tenant instances
        """
        tenants = []
        
        for tenant_create in tenants_create:
            # Validate each item
            await self._validate_tenant_create(db, tenant_create)
            
            # Create model instance
            tenant_data = tenant_create.model_dump(exclude_unset=True)
            
            tenant = Tenant(**tenant_data)
            tenants.append(tenant)
        
        db.add_all(tenants)
        await db.commit()
        
        # Refresh all instances
        for tenant in tenants:
            await db.refresh(tenant)
        
        return tenants
    
    # Validation methods
    async def _validate_tenant_create(
        self,
        db: AsyncSession,
        tenant_create: TenantCreate
    ) -> None:
        """Validate tenant creation data."""
    
    async def _validate_tenant_update(
        self,
        db: AsyncSession,
        tenant: Tenant,
        tenant_update: TenantUpdate
    ) -> None:
        """Validate tenant update data."""
