"""
MaintenanceRequest API Routes
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
from app.models.maintenance_request import Maintenancerequest
from app.schemas.maintenance_request import (
    MaintenancerequestCreate,
    MaintenancerequestUpdate,
    MaintenancerequestResponse,
    MaintenancerequestList
)
from app.services.maintenance_request_service import MaintenancerequestService


router = APIRouter()
maintenance_request_service = MaintenancerequestService()


@router.get("/", response_model=MaintenancerequestList)
async def list_maintenance_requests(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term")
) -> MaintenancerequestList:
    """
    List maintenance_requests with pagination and filtering.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "maintenance_request.read"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    filters = {}
    
    maintenance_requests, total = await maintenance_request_service.list_maintenance_requests(
        db=db,
        skip=skip,
        limit=limit,
        filters=filters,
        search=search
    )
    
    return MaintenancerequestList(
        items=maintenance_requests,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=MaintenancerequestResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance_request(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    maintenance_request_create: MaintenancerequestCreate
) -> MaintenancerequestResponse:
    """
    Create a new maintenance_request.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "maintenance_request.create"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    maintenance_request = await maintenance_request_service.create_maintenance_request(
        db=db, 
        maintenance_request_create=maintenance_request_create,
        created_by=current_user.id
    )
    
    return maintenance_request


@router.get("/{{ entity.name | snake_case }}_id}", response_model=MaintenancerequestResponse)
async def get_maintenance_request(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    maintenance_request_id: UUID
) -> MaintenancerequestResponse:
    """
    Get a specific maintenance_request by ID.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "maintenance_request.read"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    maintenance_request = await maintenance_request_service.get_maintenance_request(
        db=db, 
        maintenance_request_id=maintenance_request_id
    )
    
    if not maintenance_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenancerequest not found"
        )
    
    return maintenance_request


@router.put("/{{ entity.name | snake_case }}_id}", response_model=MaintenancerequestResponse)
async def update_maintenance_request(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    maintenance_request_id: UUID,
    maintenance_request_update: MaintenancerequestUpdate
) -> MaintenancerequestResponse:
    """
    Update a specific maintenance_request.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "maintenance_request.update"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    maintenance_request = await maintenance_request_service.get_maintenance_request(
        db=db, 
        maintenance_request_id=maintenance_request_id
    )
    
    if not maintenance_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenancerequest not found"
        )
    
    updated_maintenance_request = await maintenance_request_service.update_maintenance_request(
        db=db,
        maintenance_request=maintenance_request,
        maintenance_request_update=maintenance_request_update
    )
    
    return updated_maintenance_request


@router.delete("/{{ entity.name | snake_case }}_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maintenance_request(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    maintenance_request_id: UUID
) -> None:
    """
    Delete a specific maintenance_request.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "maintenance_request.delete"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    maintenance_request = await maintenance_request_service.get_maintenance_request(
        db=db, 
        maintenance_request_id=maintenance_request_id
    )
    
    if not maintenance_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenancerequest not found"
        )
    
    await maintenance_request_service.delete_maintenance_request(
        db=db, 
        maintenance_request=maintenance_request
    )


