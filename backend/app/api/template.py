"""Enhanced template system API routes with Pydantic validation."""

from datetime import datetime
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


# Pydantic models for code generation
class CodeGenerationOptions(PydanticBaseModel):
    """Options for code generation."""
    include_backend: bool = True
    include_frontend: bool = True
    include_database: bool = True
    include_tests: bool = False
    include_documentation: bool = False
    output_path: str = "/generated"
    entities: Optional[List[str]] = None


class CodeGenerationResponse(PydanticBaseModel):
    """Response model for code generation."""
    success: bool
    generation_id: str
    domain_name: str
    message: str
    files_generated: int = 0
    total_lines: int = 0
    generation_time_seconds: float = 0
    output_directory: str = ""
    errors: List[str] = []


@router.post("/domains/{domain_name}/generate", response_model=CodeGenerationResponse)
async def generate_code(
    domain_name: str,
    options: CodeGenerationOptions,
    db: AsyncSession = Depends(get_db)
):
    """Generate code from a domain configuration."""
    try:
        # Load domain configuration
        config = legacy_loader.load_domain_config(domain_name)
        if not config:
            raise HTTPException(status_code=404, detail=f"Domain {domain_name} not found")
        
        # Import and use the CodeGenerationOrchestrator
        from app.services.code_generation_orchestrator import CodeGenerationOrchestrator
        from app.core.domain_config import DomainConfig, EntityConfig, FieldConfig, FieldType
        
        # Convert legacy config to new DomainConfig format
        # This is a simplified conversion - in a full implementation you'd need proper mapping
        entities = []
        if hasattr(config, 'entities') and config.entities:
            for entity in config.entities:
                fields = []
                if hasattr(entity, 'fields') and entity.fields:
                    for field in entity.fields:
                        # Map field types
                        field_type = FieldType.STRING  # Default
                        if hasattr(field, 'type'):
                            type_mapping = {
                                'string': FieldType.STRING,
                                'text': FieldType.TEXT,
                                'integer': FieldType.INTEGER,
                                'boolean': FieldType.BOOLEAN,
                                'datetime': FieldType.DATETIME,
                                'date': FieldType.DATE,
                                'time': FieldType.TIME,
                                'decimal': FieldType.DECIMAL,
                                'email': FieldType.EMAIL,
                                'phone': FieldType.PHONE,
                                'url': FieldType.URL,
                                'json': FieldType.JSON,
                                'enum': FieldType.ENUM
                            }
                            field_type = type_mapping.get(field.type.lower(), FieldType.STRING)
                        
                        fields.append(FieldConfig(
                            name=field.name,
                            type=field_type,
                            required=not getattr(field, 'nullable', True),
                            description=getattr(field, 'description', '')
                        ))
                
                entities.append(EntityConfig(
                    name=entity.name,
                    description=getattr(entity, 'description', ''),
                    fields=fields
                ))
        
        # Create DomainConfig
        domain_config = DomainConfig(
            name=getattr(config, 'name', domain_name),
            description=getattr(config, 'description', f"Generated from {domain_name}"),
            entities=entities
        )
        
        # Initialize orchestrator
        orchestrator = CodeGenerationOrchestrator()
        
        # Generate the application
        result = orchestrator.generate_full_application(
            domain_config=domain_config,
            include_backend=options.include_backend,
            include_frontend=options.include_frontend,
            entities=options.entities
        )
        
        # Return the result
        return CodeGenerationResponse(
            success=result.failed_generations == 0,
            generation_id=f"gen_{domain_name}_{int(datetime.now().timestamp())}",
            domain_name=result.domain_name,
            message="Code generation completed successfully" if result.failed_generations == 0 else "Code generation completed with errors",
            files_generated=result.total_files_created,
            total_lines=result.total_content_length,
            generation_time_seconds=result.generation_time_seconds,
            output_directory=result.output_directory,
            errors=result.errors
        )
        
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Code generation service not available: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")


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


# Marketplace API endpoints - Day 12
class MarketplaceTemplate(PydanticBaseModel):
    """Marketplace template model."""
    id: str
    name: str
    title: str
    description: str
    category: str
    author: dict
    version: str
    rating: float
    total_ratings: int
    downloads: int
    price: int
    tags: List[str]
    features: List[str]
    complexity: str
    estimated_time: str
    last_updated: str
    entities: int
    is_popular: bool = False
    is_featured: bool = False
    is_new: bool = False


class TemplateInstallation(PydanticBaseModel):
    """Template installation request."""
    template_id: str
    project_id: Optional[str] = None
    custom_name: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None


class InstallationResponse(PydanticBaseModel):
    """Template installation response."""
    success: bool
    installation_id: str
    message: str
    project_id: Optional[str] = None
    template_id: str
    installed_components: List[str] = []


@router.get("/marketplace/templates", response_model=List[MarketplaceTemplate])
async def get_marketplace_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search query"),
    sort_by: str = Query("popular", description="Sort by: popular, rating, downloads, newest, name"),
    price_filter: Optional[str] = Query(None, description="Price filter: free, paid"),
    complexity: Optional[str] = Query(None, description="Complexity filter: beginner, intermediate, advanced"),
    db: AsyncSession = Depends(get_db)
):
    """Get marketplace templates with filtering and search."""
    # Mock marketplace templates
    marketplace_templates = [
        MarketplaceTemplate(
            id="task-management-pro",
            name="task_management_pro",
            title="Task Management Pro",
            description="Advanced task management system with team collaboration, time tracking, and project analytics. Perfect for growing teams.",
            category="business",
            author={"name": "TeamFlow", "verified": True, "organization": "TeamFlow Inc."},
            version="2.1.0",
            rating=4.9,
            total_ratings=234,
            downloads=1250,
            price=0,
            tags=["tasks", "projects", "collaboration", "analytics"],
            features=["Team Collaboration", "Time Tracking", "Analytics Dashboard", "Mobile App"],
            complexity="intermediate",
            estimated_time="30 minutes",
            last_updated="2025-09-20",
            entities=8,
            is_popular=True,
            is_featured=True,
            is_new=False
        ),
        MarketplaceTemplate(
            id="ecommerce-store",
            name="ecommerce_store",
            title="E-commerce Store",
            description="Complete e-commerce solution with product catalog, shopping cart, payment processing, and order management.",
            category="ecommerce",
            author={"name": "Commerce Labs", "verified": True, "organization": "Commerce Labs"},
            version="1.8.2",
            rating=4.7,
            total_ratings=189,
            downloads=890,
            price=49,
            tags=["ecommerce", "shopping", "payments", "inventory"],
            features=["Product Catalog", "Shopping Cart", "Payment Gateway", "Order Tracking"],
            complexity="advanced",
            estimated_time="45 minutes",
            last_updated="2025-09-18",
            entities=12,
            is_popular=True,
            is_featured=False,
            is_new=False
        ),
        MarketplaceTemplate(
            id="property-management",
            name="property_management",
            title="Property Management",
            description="Complete property management solution with tenant tracking, maintenance requests, and rent collection.",
            category="business",
            author={"name": "PropTech", "verified": True, "organization": "PropTech Solutions"},
            version="2.3.1",
            rating=4.6,
            total_ratings=167,
            downloads=780,
            price=0,
            tags=["property", "tenants", "maintenance", "rent"],
            features=["Tenant Management", "Maintenance Tracking", "Rent Collection", "Property Analytics"],
            complexity="intermediate",
            estimated_time="35 minutes",
            last_updated="2025-09-10",
            entities=10,
            is_popular=True,
            is_featured=False,
            is_new=False
        )
    ]
    
    # Apply filters
    filtered_templates = marketplace_templates
    
    if category:
        filtered_templates = [t for t in filtered_templates if t.category == category]
    
    if search:
        search_lower = search.lower()
        filtered_templates = [
            t for t in filtered_templates 
            if search_lower in t.title.lower() 
            or search_lower in t.description.lower()
            or any(search_lower in tag.lower() for tag in t.tags)
        ]
    
    if price_filter == "free":
        filtered_templates = [t for t in filtered_templates if t.price == 0]
    elif price_filter == "paid":
        filtered_templates = [t for t in filtered_templates if t.price > 0]
    
    if complexity:
        filtered_templates = [t for t in filtered_templates if t.complexity == complexity]
    
    # Apply sorting
    if sort_by == "rating":
        filtered_templates.sort(key=lambda x: x.rating, reverse=True)
    elif sort_by == "downloads":
        filtered_templates.sort(key=lambda x: x.downloads, reverse=True)
    elif sort_by == "newest":
        filtered_templates.sort(key=lambda x: x.last_updated, reverse=True)
    elif sort_by == "name":
        filtered_templates.sort(key=lambda x: x.title)
    else:  # popular
        filtered_templates.sort(key=lambda x: (x.downloads * 0.4 + x.rating * x.total_ratings * 0.4), reverse=True)
    
    return filtered_templates


@router.post("/marketplace/templates/{template_id}/install", response_model=InstallationResponse)
async def install_marketplace_template(
    template_id: str,
    installation: TemplateInstallation,
    db: AsyncSession = Depends(get_db)
):
    """Install a template from the marketplace."""
    try:
        # Simulate template installation process
        installation_id = f"install_{template_id}_{int(datetime.now().timestamp())}"
        
        # In a real implementation, this would:
        # 1. Download template files
        # 2. Create project structure
        # 3. Configure template settings
        # 4. Generate initial code
        # 5. Set up database schema
        
        return InstallationResponse(
            success=True,
            installation_id=installation_id,
            message=f"Template {template_id} installed successfully",
            template_id=template_id,
            project_id=installation.project_id,
            installed_components=[
                "Database Models",
                "API Endpoints", 
                "Frontend Components",
                "Configuration Files"
            ]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template installation failed: {str(e)}")


@router.get("/marketplace/categories")
async def get_marketplace_categories():
    """Get available template categories."""
    return [
        {"id": "business", "name": "Business", "count": 15},
        {"id": "ecommerce", "name": "E-commerce", "count": 8},
        {"id": "healthcare", "name": "Healthcare", "count": 6},
        {"id": "education", "name": "Education", "count": 4},
        {"id": "finance", "name": "Finance", "count": 7},
        {"id": "technology", "name": "Technology", "count": 12},
        {"id": "government", "name": "Government", "count": 3}
    ]


@router.get("/marketplace/featured")
async def get_featured_templates():
    """Get featured marketplace templates."""
    # Return a subset of featured templates
    return [
        {
            "id": "task-management-pro",
            "title": "Task Management Pro",
            "description": "Advanced task management with analytics",
            "rating": 4.9,
            "downloads": 1250,
            "price": 0,
            "is_featured": True
        }
    ]


# Template Management API Endpoints (Day 13)

@router.get("/{template_id}/manage")
async def get_template_for_management(template_id: str):
    """Get template details for management interface."""
    # In real implementation: fetch from database with full details
    # For now, return comprehensive mock data
    return {
        "id": template_id,
        "name": "task_management_pro",
        "title": "Task Management Pro",
        "description": "Advanced task management system with team collaboration, time tracking, and project analytics.",
        "category": "business",
        "tags": ["tasks", "projects", "collaboration", "analytics", "time-tracking"],
        "entities": [
            {"name": "Task", "fields": 12, "relationships": 3},
            {"name": "Project", "fields": 8, "relationships": 4},
            {"name": "User", "fields": 6, "relationships": 2},
            {"name": "Team", "fields": 5, "relationships": 3}
        ],
        "relationships": [
            {"from": "Task", "to": "Project", "type": "belongs_to"},
            {"from": "Task", "to": "User", "type": "assigned_to"},
            {"from": "User", "to": "Team", "type": "member_of"}
        ],
        "workflows": [
            {"name": "Task Creation", "steps": 5},
            {"name": "Project Setup", "steps": 8}
        ],
        "version": "2.1.0",
        "author": "TeamFlow Admin",
        "created_at": "2025-08-15T10:00:00Z",
        "updated_at": "2025-09-20T14:30:00Z",
        "is_public": True,
        "is_official": True,
        "usage_count": 1250,
        "rating": 4.9,
        "total_ratings": 234,
        "versions": [
            {
                "id": "v2.1.0",
                "version": "2.1.0",
                "description": "Added advanced analytics and reporting features",
                "author": "TeamFlow Admin",
                "created_at": "2025-09-20T14:30:00Z",
                "is_current": True,
                "changes": [
                    "Added analytics dashboard",
                    "Enhanced reporting system",
                    "Improved performance",
                    "Bug fixes and optimizations"
                ],
                "size": "2.4 MB"
            },
            {
                "id": "v2.0.0",
                "version": "2.0.0",
                "description": "Major update with workflow automation",
                "author": "TeamFlow Admin",
                "created_at": "2025-09-01T09:15:00Z",
                "is_current": False,
                "changes": [
                    "Added workflow automation",
                    "New user interface",
                    "Enhanced security features"
                ],
                "size": "2.1 MB"
            }
        ],
        "permissions": [
            {
                "user_id": "user1",
                "user_name": "Alice Johnson",
                "permission": "admin",
                "granted_at": "2025-08-15T10:00:00Z",
                "granted_by": "System"
            },
            {
                "user_id": "user2",
                "user_name": "Bob Smith",
                "permission": "edit",
                "granted_at": "2025-09-01T12:00:00Z",
                "granted_by": "Alice Johnson"
            }
        ],
        "metadata": {
            "total_entities": 4,
            "total_fields": 31,
            "total_relationships": 7,
            "complexity_score": 8.5
        }
    }


@router.put("/{template_id}/manage")
async def update_template(template_id: str, template_data: dict = Body(...)):
    """Update template information."""
    # In real implementation: validate and update database
    # Return updated template data
    return {
        "id": template_id,
        "message": "Template updated successfully",
        "updated_at": datetime.utcnow().isoformat(),
        "version": "2.1.1"  # Auto-increment version
    }


@router.post("/{template_id}/versions")
async def create_template_version(template_id: str, version_data: dict = Body(...)):
    """Create a new version of the template."""
    # In real implementation: create new version in database
    return {
        "id": f"v2.2.0",
        "version": "2.2.0",
        "description": version_data.get("description", ""),
        "author": "Current User",
        "created_at": datetime.utcnow().isoformat(),
        "is_current": True,
        "changes": ["Manual version creation"],
        "size": "2.5 MB"
    }


@router.post("/{template_id}/clone")
async def clone_template(template_id: str, clone_options: dict = Body(...)):
    """Clone a template with specified options."""
    new_template_id = f"{template_id}_clone_{int(datetime.utcnow().timestamp())}"
    
    # In real implementation: perform actual cloning in database
    return {
        "id": new_template_id,
        "name": clone_options.get("new_name", f"cloned_{template_id}"),
        "title": clone_options.get("new_title", "Cloned Template"),
        "message": "Template cloned successfully",
        "created_at": datetime.utcnow().isoformat()
    }


@router.delete("/{template_id}/manage")
async def delete_template(template_id: str):
    """Delete a template and all its versions."""
    # In real implementation: soft delete template and associated data
    return {
        "message": f"Template {template_id} deleted successfully",
        "deleted_at": datetime.utcnow().isoformat()
    }


@router.post("/{template_id}/permissions")
async def add_template_permission(template_id: str, permission_data: dict = Body(...)):
    """Add user permission to template."""
    # In real implementation: validate user exists and add permission
    return {
        "user_id": "new_user_id",
        "user_name": permission_data.get("user_name"),
        "permission": permission_data.get("permission"),
        "granted_at": datetime.utcnow().isoformat(),
        "granted_by": "Current User"
    }


@router.delete("/{template_id}/permissions/{user_id}")
async def remove_template_permission(template_id: str, user_id: str):
    """Remove user permission from template."""
    # In real implementation: remove permission from database
    return {
        "message": f"Permission removed for user {user_id}",
        "removed_at": datetime.utcnow().isoformat()
    }


@router.get("/{template_id}/export")
async def export_template(template_id: str, format: str = Query("json")):
    """Export template in specified format."""
    # In real implementation: generate export file
    return {
        "template_id": template_id,
        "export_format": format,
        "download_url": f"/api/v1/templates/{template_id}/download?format={format}",
        "expires_at": datetime.utcnow().isoformat()
    }


@router.post("/import")
async def import_template(template_file: dict = Body(...)):
    """Import template from uploaded file."""
    # In real implementation: validate and import template
    new_template_id = f"imported_{int(datetime.utcnow().timestamp())}"
    
    return {
        "id": new_template_id,
        "name": template_file.get("name", "imported_template"),
        "message": "Template imported successfully",
        "imported_at": datetime.utcnow().isoformat()
    }