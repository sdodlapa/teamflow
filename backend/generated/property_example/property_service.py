"""
Property Service
Generated on: 2025-09-24
Domain: real_estate_simple
"""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.property import Property
from app.schemas.property import (
    PropertyCreate,
    PropertyUpdate
)
from app.core.exceptions import NotFoundError, ValidationError


class PropertyService:
    """Service class for Property operations."""
    
    async def list_properties(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Property], int]:
        """
        List properties with pagination, filtering, and search.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of filters to apply
            search: Search term for full-text search
            
        Returns:
            Tuple of (properties, total_count)
        """
        query = select(Property)
        count_query = select(func.count(Property.id))
        
        # Apply filters
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if hasattr(Property, key) and value is not None:
                    filter_conditions.append(getattr(Property, key) == value)
            
            if filter_conditions:
                query = query.where(and_(*filter_conditions))
                count_query = count_query.where(and_(*filter_conditions))
        
        # Apply search
        if search:
            search_conditions = []
            # Search in specified searchable fields
            search_conditions.append(Property.title.ilike(f"%{search}%"))
            search_conditions.append(Property.description.ilike(f"%{search}%"))
            search_conditions.append(Property.address.ilike(f"%{search}%"))
            search_conditions.append(Property.city.ilike(f"%{search}%"))
            
            if search_conditions:
                search_filter = or_(*search_conditions)
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)
        
        # Apply ordering
        query = query.order_by(Property.listing_date.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        properties = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        return properties, total or 0
    
    async def get_property(
        self, 
        db: AsyncSession, 
        property_id: UUID,
        load_relationships: bool = False
    ) -> Optional[Property]:
        """
        Get a property by ID.
        
        Args:
            db: Database session
            property_id: Property ID
            load_relationships: Whether to load related objects
            
        Returns:
            Property instance or None if not found
        """
        query = select(Property).where(Property.id == property_id)
        
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_property(
        self,
        db: AsyncSession,
        property_create: PropertyCreate,
        created_by: Optional[UUID] = None
    ) -> Property:
        """
        Create a new property.
        
        Args:
            db: Database session
            property_create: Property creation data
            created_by: ID of the user creating the property
            
        Returns:
            Created Property instance
        """
        # Validate data
        await self._validate_property_create(db, property_create)
        
        # Create model instance
        property_data = property_create.model_dump(exclude_unset=True)
        
        property = Property(**property_data)
        
        db.add(property)
        await db.commit()
        await db.refresh(property)
        
        return property
    
    async def update_property(
        self,
        db: AsyncSession,
        property: Property,
        property_update: PropertyUpdate
    ) -> Property:
        """
        Update an existing property.
        
        Args:
            db: Database session
            property: Property instance to update
            property_update: Update data
            
        Returns:
            Updated Property instance
        """
        # Validate update data
        await self._validate_property_update(db, property, property_update)
        
        # Apply updates
        update_data = property_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(property, field, value)
        
        await db.commit()
        await db.refresh(property)
        
        return property
    
    async def delete_property(
        self, 
        db: AsyncSession, 
        property: Property
    ) -> None:
        """
        Delete a property.
        
        Args:
            db: Database session
            property: Property instance to delete
        """
        # Soft delete - mark as inactive
        property.is_active = False
        await db.commit()
    
    async def bulk_create_properties(
        self,
        db: AsyncSession,
        properties_create: List[PropertyCreate],
        created_by: Optional[UUID] = None
    ) -> List[Property]:
        """
        Create multiple properties in a single transaction.
        
        Args:
            db: Database session
            properties_create: List of Property creation data
            created_by: ID of the user creating the properties
            
        Returns:
            List of created Property instances
        """
        properties = []
        
        for property_create in properties_create:
            # Validate each item
            await self._validate_property_create(db, property_create)
            
            # Create model instance
            property_data = property_create.model_dump(exclude_unset=True)
            
            property = Property(**property_data)
            properties.append(property)
        
        db.add_all(properties)
        await db.commit()
        
        # Refresh all instances
        for property in properties:
            await db.refresh(property)
        
        return properties
    
    # Validation methods
    async def _validate_property_create(
        self,
        db: AsyncSession,
        property_create: PropertyCreate
    ) -> None:
        """Validate property creation data."""
        # Check unique constraints
        # Multi-field uniqueness check
        conditions = []
        field_value = getattr(property_create, "address")
        if field_value:
            conditions.append(Property.address == field_value)
        field_value = getattr(property_create, "city")
        if field_value:
            conditions.append(Property.city == field_value)
        field_value = getattr(property_create, "state")
        if field_value:
            conditions.append(Property.state == field_value)
        field_value = getattr(property_create, "zip_code")
        if field_value:
            conditions.append(Property.zip_code == field_value)
        
        if conditions:
            existing = await db.execute(
                select(Property).where(and_(*conditions))
            )
            if existing.scalar_one_or_none():
                raise ValidationError("Combination of address, city, state, zip_code already exists")
    
    async def _validate_property_update(
        self,
        db: AsyncSession,
        property: Property,
        property_update: PropertyUpdate
    ) -> None:
        """Validate property update data."""
        # Check unique constraints for updated fields
        update_data = property_update.model_dump(exclude_unset=True)
        
