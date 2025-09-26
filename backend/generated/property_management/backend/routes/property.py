"""
Property API Routes
Generated on: 2025-09-25
Domain: property_management
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.property import Property
from app.schemas.property import (
    PropertyCreate,
    PropertyUpdate,
    PropertyResponse,
    PropertyList
)
from app.services.property_service import PropertyService


router = APIRouter()
property_service = PropertyService()


@router.get("/", response_model=PropertyList)
async def list_properties(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term")
) -> PropertyList:
    """
    List properties with pagination and filtering.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "property.read"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    filters = {}
    
    properties, total = await property_service.list_properties(
        db=db,
        skip=skip,
        limit=limit,
        filters=filters,
        search=search
    )
    
    return PropertyList(
        items=properties,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    property_create: PropertyCreate
) -> PropertyResponse:
    """
    Create a new property.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "property.create"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    property = await property_service.create_property(
        db=db, 
        property_create=property_create,
        created_by=current_user.id
    )
    
    return property


@router.get("/{{ entity.name | snake_case }}_id}", response_model=PropertyResponse)
async def get_property(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    property_id: UUID
) -> PropertyResponse:
    """
    Get a specific property by ID.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "property.read"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    property = await property_service.get_property(
        db=db, 
        property_id=property_id
    )
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    return property


@router.put("/{{ entity.name | snake_case }}_id}", response_model=PropertyResponse)
async def update_property(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    property_id: UUID,
    property_update: PropertyUpdate
) -> PropertyResponse:
    """
    Update a specific property.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "property.update"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    property = await property_service.get_property(
        db=db, 
        property_id=property_id
    )
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    updated_property = await property_service.update_property(
        db=db,
        property=property,
        property_update=property_update
    )
    
    return updated_property


@router.delete("/{{ entity.name | snake_case }}_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    property_id: UUID
) -> None:
    """
    Delete a specific property.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "property.delete"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    property = await property_service.get_property(
        db=db, 
        property_id=property_id
    )
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    await property_service.delete_property(
        db=db, 
        property=property
    )


