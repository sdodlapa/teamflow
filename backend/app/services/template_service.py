"""
Service for template persistence and management.
Handles template CRUD operations, versioning, and collaboration.
"""
from typing import List, Dict, Any, Optional, Union, Tuple
from uuid import UUID
import logging
from datetime import datetime
import uuid

from sqlalchemy import select, update, delete, func, desc, asc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.templates import Template, TemplateVersion, TemplateCollaborator, TemplateCollaborationHistory, TemplateStatus
from app.schemas.templates import (
    TemplateCreate, TemplateUpdate, TemplateVersionCreate,
    CollaboratorCreate, TemplateResponse, TemplateListResponse,
    TemplateVersionResponse, TemplateCollaboratorResponse, CollaborationHistoryResponse
)


logger = logging.getLogger(__name__)


async def get_templates(
    db: AsyncSession,
    user_id: str,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    tags: Optional[List[str]] = None,
    status: Optional[str] = None,
    sort_by: str = "updated_at",
    sort_order: str = "desc",
    organization_id: Optional[str] = None
) -> Tuple[List[Template], int]:
    """
    Get templates with pagination and filtering options.
    
    Args:
        db: Database session
        user_id: User ID (as string for SQLite)
        page: Page number
        limit: Items per page
        search: Search query
        tags: Filter by tags
        status: Filter by status
        sort_by: Field to sort by
        sort_order: Sort direction ('asc' or 'desc')
        organization_id: Organization ID
        
    Returns:
        Tuple of (templates, total_count)
    """
    # Build base query
    query = select(Template).where(Template.is_active == True)
    
    # Apply user access filter (owner or collaborator)
    access_filter = or_(
        Template.user_id == user_id,
        Template.is_public == True
    )
    query = query.where(access_filter)
    
    # Apply filters
    if search:
        search_filter = or_(
            Template.name.ilike(f"%{search}%"),
            Template.description.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    if status:
        query = query.where(Template.status == status)
        
    if organization_id:
        query = query.where(Template.organization_id == organization_id)
    
    # Apply sorting
    sort_column = getattr(Template, sort_by, Template.updated_at)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Get total count
    count_query = select(func.count(Template.id)).where(query.whereclause)
    total = await db.scalar(count_query)
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    templates = result.scalars().all()
    
    return templates, total or 0
        
    Returns:
        Tuple[List[Template], int]: List of templates and total count
    """
    # Build query
    query = select(DomainTemplate)
    
    # Filter by user or organization access
    query = query.filter(
        (DomainTemplate.created_by == str(user_id)) |
        (DomainTemplate.is_public == True)
    )
    
    # Apply organization filter
    if organization_id:
        query = query.filter(DomainTemplate.organization_id == organization_id)
    
    # Apply search filter
    if search:
        query = query.filter(
            DomainTemplate.name.ilike(f"%{search}%") |
            DomainTemplate.title.ilike(f"%{search}%") |
            DomainTemplate.description.ilike(f"%{search}%")
        )
    
    # Apply tags filter
    if tags:
        # This is a simplified approach - in a real implementation, you'd need 
        # to adapt this to your database's JSON query syntax
        for tag in tags:
            query = query.filter(DomainTemplate.tags.contains(tag))
    
    # Apply status filter
    if status:
        query = query.filter(DomainTemplate.status == status)
    
    # Get total count before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply sorting
    sort_column = getattr(DomainTemplate, sort_by.lower(), DomainTemplate.created_at)
    if sort_order.lower() == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Apply pagination
    query = query.offset((page - 1) * limit).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    templates = result.scalars().all()
    
    return templates, total


async def get_template(db: AsyncSession, template_id: Union[str, UUID]) -> DomainTemplate:
    """Get a single template by ID."""
    query = select(DomainTemplate).where(DomainTemplate.id == template_id)
    result = await db.execute(query)
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with ID {template_id} not found"
        )
    
    return template


async def create_template(
    db: AsyncSession,
    template_data: TemplateCreate,
    user_id: UUID
) -> DomainTemplate:
    """Create a new template."""
    # Convert data from Pydantic model to SQLAlchemy model
    template = DomainTemplate(
        name=template_data.name,
        title=template_data.domainConfig.title,
        description=template_data.description or template_data.domainConfig.description or "",
        domain_type=template_data.domainConfig.domainType,
        version=template_data.domainConfig.version,
        status=TemplateStatus.DRAFT,
        config_schema=template_data.domainConfig.dict(),
        entities_config=[entity.dict() for entity in template_data.entities],
        ui_config=template_data.domainConfig.uiConfig or {},
        features=template_data.domainConfig.features or {},
        custom_config=template_data.domainConfig.metadata or {},
        created_by=str(user_id),
        is_official=False,
        is_public=template_data.isPublic,
    )
    
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    # Log template creation
    usage = TemplateUsage.log_usage(
        template_id=template.id,
        action="created",
        user_id=str(user_id),
        organization_id=template_data.organizationId
    )
    db.add(usage)
    await db.commit()
    
    return template


async def update_template(
    db: AsyncSession,
    template_id: UUID,
    template_data: TemplateUpdate,
    user_id: UUID
) -> DomainTemplate:
    """Update an existing template."""
    # Get current template
    template = await get_template(db, template_id)
    
    # Check if user has permission
    if str(user_id) != template.created_by:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this template"
        )
    
    # Track what needs to be updated
    update_data = {}
    
    if template_data.name:
        update_data["name"] = template_data.name
    
    if template_data.description:
        update_data["description"] = template_data.description
    
    if template_data.domainConfig:
        update_data["config_schema"] = template_data.domainConfig.dict()
        update_data["title"] = template_data.domainConfig.title
        
        if template_data.domainConfig.domainType:
            update_data["domain_type"] = template_data.domainConfig.domainType
        
        if template_data.domainConfig.version:
            update_data["version"] = template_data.domainConfig.version
        
        if template_data.domainConfig.uiConfig:
            update_data["ui_config"] = template_data.domainConfig.uiConfig
        
        if template_data.domainConfig.features:
            update_data["features"] = template_data.domainConfig.features
        
        if template_data.domainConfig.metadata:
            update_data["custom_config"] = template_data.domainConfig.metadata
    
    if template_data.entities is not None:
        update_data["entities_config"] = [entity.dict() for entity in template_data.entities]
    
    if template_data.isPublic is not None:
        update_data["is_public"] = template_data.isPublic
    
    # Apply updates
    if update_data:
        # Update template
        query = (
            update(DomainTemplate)
            .where(DomainTemplate.id == template_id)
            .values(**update_data)
            .returning(DomainTemplate)
        )
        result = await db.execute(query)
        updated_template = result.scalar_one()
        
        # Log template update
        usage = TemplateUsage.log_usage(
            template_id=updated_template.id,
            action="updated",
            user_id=str(user_id),
            context_data={"change_description": template_data.changeDescription}
        )
        db.add(usage)
        
        await db.commit()
        return updated_template
    
    return template


async def delete_template(db: AsyncSession, template_id: UUID, user_id: UUID) -> bool:
    """Delete a template."""
    template = await get_template(db, template_id)
    
    # Check if user has permission
    if str(user_id) != template.created_by:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this template"
        )
    
    # Log template deletion
    usage = TemplateUsage.log_usage(
        template_id=template.id,
        action="deleted",
        user_id=str(user_id)
    )
    db.add(usage)
    
    # Delete template
    await db.delete(template)
    await db.commit()
    
    return True


async def publish_template(db: AsyncSession, template_id: UUID, user_id: UUID) -> DomainTemplate:
    """Publish a draft template."""
    template = await get_template(db, template_id)
    
    # Check if user has permission
    if str(user_id) != template.created_by:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to publish this template"
        )
    
    # Update status
    template.status = TemplateStatus.ACTIVE
    
    # Log template publication
    usage = TemplateUsage.log_usage(
        template_id=template.id,
        action="published",
        user_id=str(user_id)
    )
    db.add(usage)
    
    await db.commit()
    await db.refresh(template)
    
    return template


async def archive_template(db: AsyncSession, template_id: UUID, user_id: UUID) -> DomainTemplate:
    """Archive a template."""
    template = await get_template(db, template_id)
    
    # Check if user has permission
    if str(user_id) != template.created_by:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to archive this template"
        )
    
    # Update status
    template.status = TemplateStatus.ARCHIVED
    
    # Log template archival
    usage = TemplateUsage.log_usage(
        template_id=template.id,
        action="archived",
        user_id=str(user_id)
    )
    db.add(usage)
    
    await db.commit()
    await db.refresh(template)
    
    return template


async def duplicate_template(
    db: AsyncSession,
    template_id: UUID,
    new_name: str,
    user_id: UUID
) -> DomainTemplate:
    """Duplicate a template."""
    # Get source template
    source = await get_template(db, template_id)
    
    # Create new template from source
    new_template = DomainTemplate(
        name=new_name,
        title=f"Copy of {source.title}",
        description=source.description,
        domain_type=source.domain_type,
        version=source.version,
        status=TemplateStatus.DRAFT,
        config_schema=source.config_schema,
        entities_config=source.entities_config,
        ui_config=source.ui_config,
        navigation_config=source.navigation_config,
        features=source.features,
        custom_config=source.custom_config,
        created_by=str(user_id),
        is_official=False,
        is_public=source.is_public
    )
    
    db.add(new_template)
    
    # Log template duplication
    usage = TemplateUsage.log_usage(
        template_id=source.id,
        action="duplicated",
        user_id=str(user_id),
        context_data={"new_template_name": new_name}
    )
    db.add(usage)
    
    await db.commit()
    await db.refresh(new_template)
    
    return new_template


async def get_template_analytics(db: AsyncSession, template_id: UUID) -> Dict[str, Any]:
    """Get analytics for a template."""
    template = await get_template(db, template_id)
    
    # Get usage statistics
    query = select(TemplateUsage).filter(TemplateUsage.template_id == template.id)
    result = await db.execute(query)
    usages = result.scalars().all()
    
    # Process analytics data
    views = sum(1 for u in usages if u.action == "viewed")
    clones = sum(1 for u in usages if u.action == "duplicated")
    
    # Group usage by date for chart data
    usage_by_date = {}
    for usage in usages:
        date_str = usage.created_at.strftime("%Y-%m-%d")
        if date_str not in usage_by_date:
            usage_by_date[date_str] = {"date": date_str, "views": 0, "edits": 0}
        
        if usage.action == "viewed":
            usage_by_date[date_str]["views"] += 1
        elif usage.action in ["updated", "edited"]:
            usage_by_date[date_str]["edits"] += 1
    
    return {
        "views": views,
        "clones": clones,
        "collaborators": 0,  # Would be calculated from collaborators table
        "versions": 1,  # Would be calculated from versions table
        "lastActivity": template.updated_at or template.created_at,
        "popularEntities": [],  # Would require additional analysis
        "usageByDate": list(usage_by_date.values())
    }


async def record_template_view(db: AsyncSession, template_id: UUID, user_id: Optional[UUID] = None):
    """Record a template view."""
    template = await get_template(db, template_id)
    
    # Log template view
    usage = TemplateUsage.log_usage(
        template_id=template.id,
        action="viewed",
        user_id=str(user_id) if user_id else None
    )
    db.add(usage)
    
    await db.commit()