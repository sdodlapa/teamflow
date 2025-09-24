"""Template system API routes."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.template_config import (
    get_domain_config, 
    get_available_domains,
    template_config_loader
)
from app.services.universal_service import UniversalAnalyticsService
from app.models.template import DomainTemplate, DomainInstance, TemplateUsage
from app.models.base import BaseModel

router = APIRouter()


@router.get("/domain-config")
async def get_current_domain_config():
    """Get the current domain configuration."""
    # For now, return the default TeamFlow configuration
    config = get_domain_config("teamflow_original")
    if not config:
        # Return default config if not found
        return {
            "name": "teamflow_original",
            "title": "TeamFlow",
            "primaryEntity": "Task",
            "secondaryEntity": "Project",
            "logo": "🚀"
        }
    
    return {
        "name": config.name,
        "title": config.title,
        "primaryEntity": config.entities[0].name if config.entities else "Task",
        "secondaryEntity": config.entities[1].name if len(config.entities) > 1 else "Project",
        "logo": config.logo
    }


@router.get("/domains")
async def list_available_domains():
    """List all available domain configurations."""
    domains = get_available_domains()
    domain_configs = []
    
    for domain_name in domains:
        config = get_domain_config(domain_name)
        if config:
            domain_configs.append({
                "name": config.name,
                "title": config.title,
                "description": config.description,
                "domain_type": config.domain_type.value,
                "version": config.version,
                "logo": config.logo,
                "entities": [entity.name for entity in config.entities],
                "features": config.features
            })
    
    return {"domains": domain_configs}


@router.get("/domains/{domain_name}")
async def get_domain_details(domain_name: str):
    """Get detailed information about a specific domain."""
    config = get_domain_config(domain_name)
    if not config:
        raise HTTPException(status_code=404, detail=f"Domain {domain_name} not found")
    
    return {
        "name": config.name,
        "title": config.title,
        "description": config.description,
        "domain_type": config.domain_type.value,
        "version": config.version,
        "logo": config.logo,
        "color_scheme": config.color_scheme,
        "theme": config.theme,
        "entities": [
            {
                "name": entity.name,
                "table_name": entity.table_name,
                "description": entity.description,
                "fields": [
                    {
                        "name": field.name,
                        "type": field.type,
                        "nullable": field.nullable,
                        "default": field.default,
                        "max_length": field.max_length,
                        "choices": field.choices,
                        "indexed": field.indexed,
                        "unique": field.unique,
                        "description": field.description
                    }
                    for field in entity.fields
                ],
                "relationships": [
                    {
                        "name": rel.name,
                        "target_entity": rel.target_entity,
                        "relationship_type": rel.relationship_type,
                        "foreign_key": rel.foreign_key,
                        "back_populates": rel.back_populates
                    }
                    for rel in entity.relationships
                ]
            }
            for entity in config.entities
        ],
        "navigation": [
            {
                "key": nav.key,
                "label": nav.label,
                "icon": nav.icon,
                "route": nav.route,
                "order": nav.order,
                "permissions": nav.permissions
            }
            for nav in config.navigation
        ],
        "features": config.features,
        "custom_config": config.custom_config
    }


@router.post("/domains/{domain_name}/validate")
async def validate_domain_config(domain_name: str):
    """Validate a domain configuration."""
    config = get_domain_config(domain_name)
    if not config:
        raise HTTPException(status_code=404, detail=f"Domain {domain_name} not found")
    
    errors = template_config_loader.validate_config(config)
    
    return {
        "domain": domain_name,
        "valid": len(errors) == 0,
        "errors": errors
    }


@router.get("/templates")
async def list_templates(
    domain_type: Optional[str] = Query(None, description="Filter by domain type"),
    status: Optional[str] = Query(None, description="Filter by template status"),
    db: AsyncSession = Depends(get_db)
):
    """List available templates."""
    # For now, return domain configurations as templates
    domains = get_available_domains()
    templates = []
    
    for domain_name in domains:
        config = get_domain_config(domain_name)
        if config:
            if domain_type and config.domain_type.value != domain_type:
                continue
                
            templates.append({
                "id": domain_name,
                "name": config.name,
                "title": config.title,
                "description": config.description,
                "domain_type": config.domain_type.value,
                "version": config.version,
                "logo": config.logo,
                "status": "active",
                "is_official": True,
                "usage_count": 0,
                "features": list(config.features.keys()) if config.features else []
            })
    
    return {"templates": templates}


@router.get("/analytics/dashboard")
async def get_dashboard_analytics(db: AsyncSession = Depends(get_db)):
    """Get dashboard analytics data."""
    # For now, return mock data that matches the new interface
    # In a real implementation, this would query actual data
    return {
        "totalEntities": 0,
        "completedEntities": 0,
        "inProgressEntities": 0,
        "overdueEntities": 0,
        "totalProjects": 0,
        "activeProjects": 0,
        "teamMembers": 1,
        "completionRate": 0
    }


@router.get("/analytics/recent-activity")
async def get_recent_activity(
    limit: int = Query(10, description="Number of activities to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get recent activity data."""
    # For now, return empty array
    # In a real implementation, this would query actual activity data
    return []


@router.get("/analytics/project-progress") 
async def get_project_progress(db: AsyncSession = Depends(get_db)):
    """Get project progress data."""
    # For now, return empty array
    # In a real implementation, this would query actual project data
    return []


@router.post("/analytics/log-usage")
async def log_template_usage(
    template_id: str,
    action: str,
    context: Optional[dict] = None,
    db: AsyncSession = Depends(get_db)
):
    """Log template usage for analytics."""
    # Create usage log entry
    usage = TemplateUsage(
        template_id=0,  # Would map from template_id string
        action=action,
        context_data=context
    )
    
    db.add(usage)
    await db.commit()
    
    return {"message": "Usage logged successfully"}


@router.get("/health")
async def template_system_health():
    """Health check for template system."""
    domains = get_available_domains()
    
    return {
        "status": "healthy",
        "template_system": "active",
        "available_domains": len(domains),
        "domains": domains,
        "config_loader": "functional"
    }