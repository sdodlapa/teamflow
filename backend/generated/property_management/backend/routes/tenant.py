"""
Tenant API Routes
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
from app.models.tenant import Tenant
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantList
)
from app.services.tenant_service import TenantService


router = APIRouter()
tenant_service = TenantService()


@router.get("/", response_model=TenantList)
async def list_tenants(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term")
) -> TenantList:
    """
    List tenants with pagination and filtering.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "tenant.read"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    filters = {}
    
    tenants, total = await tenant_service.list_tenants(
        db=db,
        skip=skip,
        limit=limit,
        filters=filters,
        search=search
    )
    
    return TenantList(
        items=tenants,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_create: TenantCreate
) -> TenantResponse:
    """
    Create a new tenant.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "tenant.create"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    tenant = await tenant_service.create_tenant(
        db=db, 
        tenant_create=tenant_create,
        created_by=current_user.id
    )
    
    return tenant


@router.get("/{{ entity.name | snake_case }}_id}", response_model=TenantResponse)
async def get_tenant(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID
) -> TenantResponse:
    """
    Get a specific tenant by ID.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "tenant.read"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    tenant = await tenant_service.get_tenant(
        db=db, 
        tenant_id=tenant_id
    )
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return tenant


@router.put("/{{ entity.name | snake_case }}_id}", response_model=TenantResponse)
async def update_tenant(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID,
    tenant_update: TenantUpdate
) -> TenantResponse:
    """
    Update a specific tenant.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "tenant.update"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    tenant = await tenant_service.get_tenant(
        db=db, 
        tenant_id=tenant_id
    )
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    updated_tenant = await tenant_service.update_tenant(
        db=db,
        tenant=tenant,
        tenant_update=tenant_update
    )
    
    return updated_tenant


@router.delete("/{{ entity.name | snake_case }}_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID
) -> None:
    """
    Delete a specific tenant.
    
    """
    # TODO: Add permission checking if needed
    # if not has_permission(current_user, "tenant.delete"):
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    tenant = await tenant_service.get_tenant(
        db=db, 
        tenant_id=tenant_id
    )
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    await tenant_service.delete_tenant(
        db=db, 
        tenant=tenant
    )


