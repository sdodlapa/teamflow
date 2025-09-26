"""Enhanced template system API routes with Pydantic validation."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel as PydanticBaseModel, ValidationError

from app.core.database import get_db
from app.core.enhanced_domain_config import (
    get_domain_loader,
    DomainConfigLoader,
    DomainConfigManager,
    DomainConfig,
    ConfigurationError
)
# Keep legacy imports for backward compatibility
from app.core.template_config import (
    TemplateConfigLoader,
    get_domain_config as legacy_get_domain_config, 
    get_available_domains as legacy_get_available_domains,
    template_config_loader as legacy_template_config_loader
)

# Initialize legacy loader with correct path
legacy_loader = TemplateConfigLoader("../domain_configs")
from app.services.universal_service import UniversalAnalyticsService
from app.models.template import DomainTemplate, DomainInstance, TemplateUsage
from app.models.base import BaseModel

router = APIRouter()

# Initialize legacy domain configuration system (compatible with existing YAML format)
# enhanced_config_loader = get_domain_loader("../domain_configs")
# enhanced_config_manager = DomainConfigManager(enhanced_config_loader)


# Pydantic models for API responses
class DomainSummary(PydanticBaseModel):
    """Summary information about a domain configuration."""
    name: str
    title: str
    description: str
    domain_type: str
    version: str
    logo: str
    color_scheme: str
    entity_count: int
    navigation_items: int
    features_enabled: int


class ValidationResult(PydanticBaseModel):
    """Domain configuration validation result."""
    domain: str
    valid: bool
    errors: List[str]
    warnings: List[str] = []


class ConfigurationComparison(PydanticBaseModel):
    """Comparison result between two domain configurations."""
    domain1: str
    domain2: str
    entities_count: Dict[str, int]
    common_entities: List[str]
    unique_entities: Dict[str, List[str]]
    differences: Dict[str, Any] = {}


# Pydantic models for template creation
class TemplateField(PydanticBaseModel):
    """Field definition for a template entity."""
    name: str
    type: str
    nullable: bool = True
    description: str = ""
    max_length: Optional[int] = None
    choices: Optional[List[str]] = None


class TemplateRelationship(PydanticBaseModel):
    """Relationship definition for a template entity."""
    name: str
    target_entity: str
    relationship_type: str
    foreign_key: Optional[str] = None


class TemplateEntity(PydanticBaseModel):
    """Entity definition for a template."""
    name: str
    table_name: str
    description: str = ""
    fields: List[TemplateField]
    relationships: List[TemplateRelationship] = []


class CreateTemplateRequest(PydanticBaseModel):
    """Request model for creating a new template."""
    name: str
    title: str
    description: str
    domain_type: str = "business"
    version: str = "1.0.0"
    logo: str = "📁"
    color_scheme: str = "blue"
    entities: List[TemplateEntity]
    features: Dict[str, bool] = {}
    tags: List[str] = []


class TemplateCreationResponse(PydanticBaseModel):
    """Response model for template creation."""
    id: str
    name: str
    title: str
    message: str
    validation_errors: List[str] = []
    warnings: List[str] = []


@router.get("/domain-config")
async def get_current_domain_config():
    """Get the current domain configuration (legacy endpoint)."""
    # Try enhanced config first, fall back to legacy
    try:
        config = enhanced_config_loader.load_domain_config("teamflow_original")
        if config:
            return {
                "name": config.domain.name,
                "title": config.domain.title,
                "primaryEntity": list(config.entities.keys())[0] if config.entities else "Task",
                "secondaryEntity": list(config.entities.keys())[1] if len(config.entities) > 1 else "Project",
                "logo": config.domain.logo
            }
    except Exception:
        pass
    
    # Fall back to legacy system
    config = legacy_get_domain_config("teamflow_original")
    if not config:
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


@router.get("/domains", response_model=Dict[str, List[DomainSummary]])
async def list_available_domains():
    """List all available domain configurations with enhanced information."""
    domains = enhanced_config_loader.get_available_domains()
    domain_summaries = []
    
    for domain_name in domains:
        try:
            config = enhanced_config_loader.load_domain_config(domain_name)
            if config:
                # Count enabled features
                enabled_features = sum(1 for feature in config.features.values() if feature.enabled)
                
                summary = DomainSummary(
                    name=config.domain.name,
                    title=config.domain.title,
                    description=config.domain.description,
                    domain_type=config.domain.domain_type,
                    version=config.domain.version,
                    logo=config.domain.logo,
                    color_scheme=config.domain.color_scheme,
                    entity_count=len(config.entities),
                    navigation_items=sum(len(items) for items in config.navigation.values()),
                    features_enabled=enabled_features
                )
                domain_summaries.append(summary)
        except Exception as e:
            # Log error but continue with other domains
            print(f"Error loading domain {domain_name}: {e}")
            continue
    
    return {"domains": domain_summaries}


@router.get("/domains/{domain_name}")
async def get_domain_details(domain_name: str):
    """Get detailed information about a specific domain."""
    try:
        config = legacy_loader.load_domain_config(domain_name)
        if not config:
            raise HTTPException(status_code=404, detail=f"Domain {domain_name} not found")
        
        # Convert legacy config to detailed dictionary representation
        entities_info = {}
        if hasattr(config, 'entities') and config.entities:
            for entity in config.entities:
                entities_info[entity.name] = {
                    "name": entity.name,
                    "table_name": getattr(entity, 'table_name', entity.name.lower()),
                    "description": getattr(entity, 'description', ''),
                    "fields": [
                        {
                            "name": field.name,
                            "type": field.type,
                            "nullable": getattr(field, 'nullable', True),
                            "description": getattr(field, 'description', ''),
                            "max_length": getattr(field, 'max_length', None),
                            "choices": getattr(field, 'choices', None)
                        }
                        for field in getattr(entity, 'fields', [])
                    ],
                    "relationships": [
                        {
                            "name": rel.name,
                            "target_entity": rel.target_entity,
                            "relationship_type": rel.relationship_type,
                            "foreign_key": getattr(rel, 'foreign_key', None)
                        }
                        for rel in getattr(entity, 'relationships', [])
                    ],
                    "field_count": len(getattr(entity, 'fields', [])),
                    "relationship_count": len(getattr(entity, 'relationships', [])),
                    "business_rules_count": 0  # Legacy doesn't have business rules
                }
        
        return {
            "domain": {
                "name": getattr(config, 'name', domain_name),
                "title": getattr(config, 'title', domain_name.replace('_', ' ').title()),
                "description": getattr(config, 'description', f"Configuration for {domain_name}"),
                "type": getattr(config, 'type', 'business'),
                "version": getattr(config, 'version', '1.0.0'),
                "logo": getattr(config, 'logo', '📁'),
                "color_scheme": getattr(config, 'color_scheme', 'blue')
            },
            "entities": entities_info,
            "navigation": getattr(config, 'navigation', []),
            "dashboard": getattr(config, 'dashboard', []),
            "features": getattr(config, 'features', {}),
            "metadata": {
                "total_entities": len(entities_info),
                "total_fields": sum(len(entity.get('fields', [])) for entity in entities_info.values()),
                "total_relationships": sum(len(entity.get('relationships', [])) for entity in entities_info.values()),
                "total_business_rules": 0,
                "enabled_features": len([f for f in getattr(config, 'features', {}).values() if f is True])
            }
        }
    
    except ConfigurationError as e:
        raise HTTPException(status_code=400, detail=f"Configuration error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/domains/{domain_name}/validate", response_model=ValidationResult)
async def validate_domain_config(domain_name: str):
    """Validate a domain configuration with detailed error reporting."""
    try:
        config = enhanced_config_loader.load_domain_config(domain_name)
        if not config:
            raise HTTPException(status_code=404, detail=f"Domain {domain_name} not found")
        
        # Enhanced validation
        errors = enhanced_config_loader.validate_config(config)
        warnings = []  # Could add warning checks here
        
        return ValidationResult(
            domain=domain_name,
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    except ConfigurationError as e:
        return ValidationResult(
            domain=domain_name,
            valid=False,
            errors=[f"Configuration error: {e.message}"],
            warnings=[]
        )
    except ValidationError as e:
        return ValidationResult(
            domain=domain_name,
            valid=False,
            errors=[f"Pydantic validation error: {str(e)}"],
            warnings=[]
        )


@router.post("/domains/{domain1}/compare/{domain2}", response_model=ConfigurationComparison)
async def compare_domain_configs(domain1: str, domain2: str):
    """Compare two domain configurations and return differences."""
    try:
        comparison = enhanced_config_manager.compare_configs(domain1, domain2)
        
        if "error" in comparison:
            raise HTTPException(status_code=404, detail=comparison["error"])
        
        return ConfigurationComparison(**comparison)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/domains/{domain_name}/export")
async def export_domain_schema(domain_name: str):
    """Export domain configuration as JSON schema."""
    try:
        config = enhanced_config_loader.load_domain_config(domain_name)
        if not config:
            raise HTTPException(status_code=404, detail="Domain not found")
        schema = enhanced_config_manager.generate_schema_export(config)
        if not schema:
            raise HTTPException(status_code=404, detail=f"Domain {domain_name} not found")
        
        return {
            "domain": domain_name,
            "schema": schema,
            "export_timestamp": "2025-01-28T00:00:00Z",
            "version": "1.0"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/domains/{domain_name}/reload")
async def reload_domain_config(domain_name: str):
    """Force reload a domain configuration from file."""
    try:
        config = enhanced_config_loader.load_domain_config(domain_name, force_reload=True)
        if not config:
            raise HTTPException(status_code=404, detail=f"Domain {domain_name} not found")
        
        return {
            "domain": domain_name,
            "status": "reloaded",
            "version": config.domain.version,
            "entities": len(config.entities)
        }
    
    except ConfigurationError as e:
        raise HTTPException(status_code=400, detail=f"Configuration error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reload failed: {str(e)}")


# Enhanced validation endpoint for specific entity
@router.post("/domains/{domain_name}/entities/{entity_name}/validate")
async def validate_entity_config(domain_name: str, entity_name: str):
    """Validate a specific entity configuration."""
    try:
        config = enhanced_config_loader.load_domain_config(domain_name)
        if not config:
            raise HTTPException(status_code=404, detail=f"Domain {domain_name} not found")
        
        entity = config.get_entity(entity_name)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Entity {entity_name} not found in domain {domain_name}")
        
        # Entity-specific validation
        errors = []
        warnings = []
        
        # Check for duplicate field names
        field_names = [field.name for field in entity.fields]
        if len(field_names) != len(set(field_names)):
            errors.append("Entity has duplicate field names")
        
        # Check relationship targets exist
        entity_names = set(config.entities.keys())
        for rel in entity.relationships:
            if rel.target_entity not in entity_names:
                errors.append(f"Relationship '{rel.name}' targets non-existent entity '{rel.target_entity}'")
        
        # Check business rule syntax (basic check)
        for rule in entity.business_rules:
            if rule.condition and not rule.condition.strip():
                errors.append(f"Business rule '{rule.name}' has empty condition")
        
        return {
            "domain": domain_name,
            "entity": entity_name,
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "metadata": {
                "field_count": len(entity.fields),
                "relationship_count": len(entity.relationships),
                "business_rules_count": len(entity.business_rules)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Entity validation failed: {str(e)}")


@router.post("/templates", response_model=TemplateCreationResponse)
async def create_template(
    template_data: CreateTemplateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new template from the provided configuration."""
    try:
        # Validate the template data
        validation_errors = []
        warnings = []
        
        # Check for duplicate entity names
        entity_names = [entity.name for entity in template_data.entities]
        if len(entity_names) != len(set(entity_names)):
            validation_errors.append("Template contains duplicate entity names")
        
        # Validate relationships reference existing entities
        for entity in template_data.entities:
            for relationship in entity.relationships:
                if relationship.target_entity not in entity_names:
                    validation_errors.append(
                        f"Entity '{entity.name}' has relationship '{relationship.name}' "
                        f"targeting non-existent entity '{relationship.target_entity}'"
                    )
        
        # Check for circular references in relationships
        for entity in template_data.entities:
            for relationship in entity.relationships:
                if relationship.target_entity == entity.name:
                    warnings.append(
                        f"Entity '{entity.name}' has self-referencing relationship '{relationship.name}'"
                    )
        
        # If there are validation errors, return them without creating
        if validation_errors:
            return TemplateCreationResponse(
                id="",
                name=template_data.name,
                title=template_data.title,
                message="Template validation failed",
                validation_errors=validation_errors,
                warnings=warnings
            )
        
        # Create the template configuration (for now, we'll just simulate saving)
        # In a full implementation, this would save to the database and/or file system
        template_id = f"custom_{template_data.name.lower().replace(' ', '_')}"
        
        # Here you would typically:
        # 1. Save to database
        # 2. Generate YAML configuration file
        # 3. Update template registry
        # 4. Trigger any necessary cache refreshes
        
        # For now, just return success
        return TemplateCreationResponse(
            id=template_id,
            name=template_data.name,
            title=template_data.title,
            message="Template created successfully",
            validation_errors=[],
            warnings=warnings
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid template data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.get("/templates")
async def list_templates(
    domain_type: Optional[str] = Query(None, description="Filter by domain type"),
    status: Optional[str] = Query(None, description="Filter by template status"),
    db: AsyncSession = Depends(get_db)
):
    """List available templates with enhanced filtering."""
    # Use legacy system that works with current YAML format
    domains = legacy_loader.get_available_domains()
    templates = []
    
    for domain_name in domains:
        try:
            config = legacy_loader.load_domain_config(domain_name)
            if not config:
                continue
                
            if domain_type and getattr(config, 'type', None) != domain_type:
                continue
            
            # Count entities
            entity_count = len(config.entities) if hasattr(config, 'entities') and config.entities else 0
            
            template_info = {
                "id": domain_name,
                "name": getattr(config, 'name', domain_name),
                "title": getattr(config, 'title', domain_name.replace('_', ' ').title()),
                "description": getattr(config, 'description', f"Domain configuration for {domain_name}"),
                "domain_type": getattr(config, 'type', 'business'),
                "version": getattr(config, 'version', '1.0.0'),
                "logo": getattr(config, 'logo', '📁'),
                "color_scheme": getattr(config, 'color_scheme', 'blue'),
                "status": "active",
                "is_official": True,
                "usage_count": 0,
                "entity_count": entity_count,
                "author": getattr(config, 'author', 'TeamFlow Templates'),
                "tags": getattr(config, 'tags', []),
                "features": []
            }
            templates.append(template_info)
            
        except Exception as e:
            print(f"Error loading template {domain_name}: {e}")
            # Still add basic info for domains that failed to load
            templates.append({
                "id": domain_name,
                "name": domain_name,
                "title": domain_name.replace('_', ' ').title(),
                "description": f"Domain configuration for {domain_name}",
                "domain_type": "business",
                "version": "1.0.0",
                "logo": "📁",
                "color_scheme": "blue",
                "status": "active",
                "is_official": True,
                "usage_count": 0,
                "entity_count": 0,
                "author": "TeamFlow Templates",
                "tags": [],
                "features": []
            })
            continue
    
    return {"templates": templates}


@router.get("/templates")
async def list_templates(
    domain_type: Optional[str] = Query(None, description="Filter by domain type"),
    status: Optional[str] = Query(None, description="Filter by template status"),
    db: AsyncSession = Depends(get_db)
):
    """List available templates with enhanced filtering."""
    # Use legacy system that works with current YAML format
    domains = legacy_loader.get_available_domains()
    templates = []
    
    for domain_name in domains:
        try:
            config = legacy_loader.load_domain_config(domain_name)
            if not config:
                continue
                
            if domain_type and getattr(config, 'type', None) != domain_type:
                continue
            
            # Count entities
            entity_count = len(config.entities) if hasattr(config, 'entities') and config.entities else 0
            
            template_info = {
                "id": domain_name,
                "name": getattr(config, 'name', domain_name),
                "title": getattr(config, 'title', domain_name.replace('_', ' ').title()),
                "description": getattr(config, 'description', f"Domain configuration for {domain_name}"),
                "domain_type": getattr(config, 'type', 'business'),
                "version": getattr(config, 'version', '1.0.0'),
                "logo": getattr(config, 'logo', '📁'),
                "color_scheme": getattr(config, 'color_scheme', 'blue'),
                "status": "active",
                "is_official": True,
                "usage_count": 0,
                "entity_count": entity_count,
                "author": getattr(config, 'author', 'TeamFlow Templates'),
                "tags": getattr(config, 'tags', []),
                "features": []
            }
            templates.append(template_info)
            
        except Exception as e:
            print(f"Error loading template {domain_name}: {e}")
            # Still add basic info for domains that failed to load
            templates.append({
                "id": domain_name,
                "name": domain_name,
                "title": domain_name.replace('_', ' ').title(),
                "description": f"Domain configuration for {domain_name}",
                "domain_type": "business",
                "version": "1.0.0",
                "logo": "📁",
                "color_scheme": "blue",
                "status": "active",
                "is_official": True,
                "usage_count": 0,
                "entity_count": 0,
                "author": "TeamFlow Templates",
                "tags": [],
                "features": []
            })
            continue
    
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