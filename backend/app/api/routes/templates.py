"""
API routes for template management and persistence.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.templates import (
    TemplateCreate, TemplateUpdate, TemplateListResponse, TemplateResponse,
    TemplateVersionResponse, TemplateCollaboratorResponse, CollaborationHistoryResponse,
    TemplateAnalyticsResponse, TemplateStatus, CollaboratorCreate
)
from app.services import template_service


router = APIRouter()


@router.get("/", response_model=TemplateListResponse)
async def get_templates(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    status: Optional[TemplateStatus] = None,
    sort_by: str = "updatedAt",
    sort_order: str = "desc",
    organization_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get templates with pagination and filtering.
    
    - **page**: Page number (starts at 1)
    - **limit**: Number of items per page
    - **search**: Search query for template name/description
    - **tags**: Filter by tags
    - **status**: Filter by template status
    - **sort_by**: Field to sort by
    - **sort_order**: Sort direction (asc/desc)
    - **organization_id**: Filter by organization
    """
    templates, total = await template_service.get_templates(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit,
        search=search,
        tags=tags,
        status=status.value if status else None,
        sort_by=sort_by,
        sort_order=sort_order,
        organization_id=organization_id
    )
    
    # Convert DB models to response schemas
    template_responses = []
    for template in templates:
        template_responses.append(
            TemplateResponse(
                id=template.id,
                name=template.name,
                description=template.description,
                domainConfig=template.to_domain_config(),
                entities=[],  # Would be converted from entities_config
                relationships=[],  # Would be calculated from relationships
                tags=[],  # Would be added from tags field
                isPublic=template.is_public,
                status=TemplateStatus.DRAFT,  # Would be converted from status
                metadata={  # Would be constructed from template metadata
                    "version": 1,
                    "createdAt": template.created_at,
                    "updatedAt": template.updated_at,
                    "createdBy": UUID(template.created_by) if template.created_by else None,
                    "collaborators": [],
                    "tags": [],
                    "isPublic": template.is_public
                },
                organizationId=None  # Would be added from organization_id
            )
        )
    
    return TemplateListResponse(
        templates=template_responses,
        total=total,
        page=page,
        limit=limit
    )


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new template.
    
    - Requires authentication
    - Returns the created template
    """
    created_template = await template_service.create_template(
        db=db,
        template_data=template,
        user_id=current_user.id
    )
    
    # Convert to response model (simplified for this example)
    return TemplateResponse(
        id=created_template.id,
        name=created_template.name,
        description=created_template.description,
        domainConfig=created_template.to_domain_config(),
        entities=[],  # Would be converted from entities_config
        relationships=[],  # Would be calculated from relationships
        tags=[],  # Would be added from tags field
        isPublic=created_template.is_public,
        status=TemplateStatus.DRAFT,
        metadata={
            "version": 1,
            "createdAt": created_template.created_at,
            "updatedAt": created_template.updated_at,
            "createdBy": UUID(created_template.created_by) if created_template.created_by else None,
            "collaborators": [],
            "tags": [],
            "isPublic": created_template.is_public
        },
        organizationId=None
    )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a template by ID.
    
    - Requires authentication
    - Records template view
    """
    template = await template_service.get_template(db, template_id)
    
    # Record view
    await template_service.record_template_view(
        db=db,
        template_id=template_id,
        user_id=current_user.id
    )
    
    # Convert to response model
    return TemplateResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        domainConfig=template.to_domain_config(),
        entities=[],  # Would be converted from entities_config
        relationships=[],  # Would be calculated from relationships
        tags=[],  # Would be added from tags field
        isPublic=template.is_public,
        status=TemplateStatus.DRAFT,  # Would be converted from status
        metadata={
            "version": 1,
            "createdAt": template.created_at,
            "updatedAt": template.updated_at,
            "createdBy": UUID(template.created_by) if template.created_by else None,
            "collaborators": [],
            "tags": [],
            "isPublic": template.is_public
        },
        organizationId=None
    )


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_data: TemplateUpdate,
    template_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a template.
    
    - Requires authentication
    - User must be the template owner or have admin permissions
    """
    updated_template = await template_service.update_template(
        db=db,
        template_id=template_id,
        template_data=template_data,
        user_id=current_user.id
    )
    
    # Convert to response model
    return TemplateResponse(
        id=updated_template.id,
        name=updated_template.name,
        description=updated_template.description,
        domainConfig=updated_template.to_domain_config(),
        entities=[],  # Would be converted from entities_config
        relationships=[],  # Would be calculated from relationships
        tags=[],  # Would be added from tags field
        isPublic=updated_template.is_public,
        status=TemplateStatus.DRAFT,  # Would be converted from status
        metadata={
            "version": 1,
            "createdAt": updated_template.created_at,
            "updatedAt": updated_template.updated_at,
            "createdBy": UUID(updated_template.created_by) if updated_template.created_by else None,
            "collaborators": [],
            "tags": [],
            "isPublic": updated_template.is_public
        },
        organizationId=None
    )


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a template.
    
    - Requires authentication
    - User must be the template owner or have admin permissions
    - Returns 204 No Content on success
    """
    await template_service.delete_template(
        db=db,
        template_id=template_id,
        user_id=current_user.id
    )
    return None


@router.post("/{template_id}/publish", response_model=TemplateResponse)
async def publish_template(
    template_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Publish a draft template.
    
    - Requires authentication
    - User must be the template owner or have admin permissions
    """
    published_template = await template_service.publish_template(
        db=db,
        template_id=template_id,
        user_id=current_user.id
    )
    
    # Convert to response model
    return TemplateResponse(
        id=published_template.id,
        name=published_template.name,
        description=published_template.description,
        domainConfig=published_template.to_domain_config(),
        entities=[],  # Would be converted from entities_config
        relationships=[],  # Would be calculated from relationships
        tags=[],  # Would be added from tags field
        isPublic=published_template.is_public,
        status=TemplateStatus.PUBLISHED,  # Would be converted from status
        metadata={
            "version": 1,
            "createdAt": published_template.created_at,
            "updatedAt": published_template.updated_at,
            "createdBy": UUID(published_template.created_by) if published_template.created_by else None,
            "collaborators": [],
            "tags": [],
            "isPublic": published_template.is_public
        },
        organizationId=None
    )


@router.post("/{template_id}/archive", response_model=TemplateResponse)
async def archive_template(
    template_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Archive a template.
    
    - Requires authentication
    - User must be the template owner or have admin permissions
    """
    archived_template = await template_service.archive_template(
        db=db,
        template_id=template_id,
        user_id=current_user.id
    )
    
    # Convert to response model
    return TemplateResponse(
        id=archived_template.id,
        name=archived_template.name,
        description=archived_template.description,
        domainConfig=archived_template.to_domain_config(),
        entities=[],  # Would be converted from entities_config
        relationships=[],  # Would be calculated from relationships
        tags=[],  # Would be added from tags field
        isPublic=archived_template.is_public,
        status=TemplateStatus.ARCHIVED,  # Would be converted from status
        metadata={
            "version": 1,
            "createdAt": archived_template.created_at,
            "updatedAt": archived_template.updated_at,
            "createdBy": UUID(archived_template.created_by) if archived_template.created_by else None,
            "collaborators": [],
            "tags": [],
            "isPublic": archived_template.is_public
        },
        organizationId=None
    )


@router.post("/{template_id}/duplicate", response_model=TemplateResponse)
async def duplicate_template(
    template_id: UUID = Path(...),
    name: str = Query(..., description="Name for the duplicated template"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Duplicate a template.
    
    - Requires authentication
    - Creates a new template based on the source
    - New template will be owned by the current user
    """
    duplicated_template = await template_service.duplicate_template(
        db=db,
        template_id=template_id,
        new_name=name,
        user_id=current_user.id
    )
    
    # Convert to response model
    return TemplateResponse(
        id=duplicated_template.id,
        name=duplicated_template.name,
        description=duplicated_template.description,
        domainConfig=duplicated_template.to_domain_config(),
        entities=[],  # Would be converted from entities_config
        relationships=[],  # Would be calculated from relationships
        tags=[],  # Would be added from tags field
        isPublic=duplicated_template.is_public,
        status=TemplateStatus.DRAFT,  # Would be converted from status
        metadata={
            "version": 1,
            "createdAt": duplicated_template.created_at,
            "updatedAt": duplicated_template.updated_at,
            "createdBy": UUID(duplicated_template.created_by) if duplicated_template.created_by else None,
            "collaborators": [],
            "tags": [],
            "isPublic": duplicated_template.is_public
        },
        organizationId=None
    )


@router.get("/{template_id}/analytics", response_model=TemplateAnalyticsResponse)
async def get_template_analytics(
    template_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get analytics for a template.
    
    - Requires authentication
    - Returns usage statistics and analytics data
    """
    analytics = await template_service.get_template_analytics(
        db=db,
        template_id=template_id
    )
    
    return TemplateAnalyticsResponse(**analytics)