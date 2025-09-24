"""
Template Builder Services for domain configuration management
"""
import asyncio
import hashlib
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import ValidationError

from app.schemas.template import (
    DomainConfig,
    ValidationResult,
    ValidationError as SchemaValidationError,
    GenerationResult,
    GeneratedFile,
    GenerationStatus,
    TemplateConfigCreate,
    TemplateConfigResponse,
    TemplateConfigUpdate,
    TemplateListResponse,
    TemplateMetadata
)

# Mock database models - in a real implementation, create proper SQLAlchemy models
class TemplateConfigModel:
    """Mock model for template configurations"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.name = kwargs.get('name')
        self.title = kwargs.get('title')
        self.description = kwargs.get('description')
        self.tags = kwargs.get('tags', [])
        self.is_public = kwargs.get('is_public', False)
        self.config = kwargs.get('config')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.created_by = kwargs.get('created_by')
        self.downloads = kwargs.get('downloads', 0)
        self.rating = kwargs.get('rating')

# In-memory storage for demo purposes
# In production, use proper database
_templates_storage: Dict[str, TemplateConfigModel] = {}
_generation_tasks: Dict[str, GenerationStatus] = {}

class ValidationService:
    """Service for validating domain configurations"""
    
    async def validate_domain_config(self, config: DomainConfig) -> ValidationResult:
        """Validate a domain configuration"""
        errors = []
        warnings = []
        
        try:
            # Basic validation
            if not config.name or not config.name.strip():
                errors.append(SchemaValidationError(
                    field="name",
                    message="Domain name is required",
                    code="required"
                ))
            
            if not config.title or not config.title.strip():
                errors.append(SchemaValidationError(
                    field="title",
                    message="Domain title is required",
                    code="required"
                ))
            
            # Name format validation
            if config.name and not config.name.replace('_', '').replace('-', '').isalnum():
                errors.append(SchemaValidationError(
                    field="name",
                    message="Domain name must contain only letters, numbers, underscores, and hyphens",
                    code="invalid_format"
                ))
            
            # Version format validation
            if config.version and not self._is_valid_semver(config.version):
                errors.append(SchemaValidationError(
                    field="version",
                    message="Version must follow semantic versioning (e.g., 1.0.0)",
                    code="invalid_format"
                ))
            
            # Entity validation
            if config.entities:
                entity_names = set()
                for i, entity in enumerate(config.entities):
                    # Check for duplicate entity names
                    if entity.name in entity_names:
                        errors.append(SchemaValidationError(
                            field=f"entities[{i}].name",
                            message=f"Duplicate entity name: {entity.name}",
                            code="duplicate"
                        ))
                    entity_names.add(entity.name)
                    
                    # Check entity has fields
                    if not entity.fields:
                        warnings.append(SchemaValidationError(
                            field=f"entities[{i}].fields",
                            message=f"Entity '{entity.name}' has no fields defined",
                            code="empty_fields"
                        ))
                    
                    # Validate field names are unique within entity
                    field_names = set()
                    for j, field in enumerate(entity.fields):
                        if field.name in field_names:
                            errors.append(SchemaValidationError(
                                field=f"entities[{i}].fields[{j}].name",
                                message=f"Duplicate field name '{field.name}' in entity '{entity.name}'",
                                code="duplicate"
                            ))
                        field_names.add(field.name)
                    
                    # Validate relationships reference existing entities
                    if entity.relationships:
                        for j, rel in enumerate(entity.relationships):
                            if rel.target_entity not in entity_names:
                                warnings.append(SchemaValidationError(
                                    field=f"entities[{i}].relationships[{j}].target_entity",
                                    message=f"Relationship '{rel.name}' references unknown entity '{rel.target_entity}'",
                                    code="unknown_reference"
                                ))
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors if errors else None,
                warnings=warnings if warnings else None
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[SchemaValidationError(
                    field="general",
                    message=f"Validation failed: {str(e)}",
                    code="validation_error"
                )]
            )
    
    def _is_valid_semver(self, version: str) -> bool:
        """Check if version string follows semantic versioning"""
        parts = version.split('.')
        if len(parts) != 3:
            return False
        
        try:
            for part in parts:
                int(part)
            return True
        except ValueError:
            return False

class CodeGenerationService:
    """Service for generating code from domain configurations"""
    
    async def start_generation(
        self,
        config: DomainConfig,
        user_id: str,
        generate_backend: bool = True,
        generate_frontend: bool = True,
        target_directory: Optional[str] = None
    ) -> str:
        """Start code generation task"""
        task_id = str(uuid.uuid4())
        
        # Initialize generation status
        _generation_tasks[task_id] = GenerationStatus(
            status="pending",
            progress=0,
            current_step="Starting generation...",
            total_steps=5,
            started_at=datetime.utcnow()
        )
        
        # Start generation in background
        asyncio.create_task(self._run_generation(
            task_id, config, user_id, generate_backend, generate_frontend, target_directory
        ))
        
        return task_id
    
    async def get_generation_status(self, task_id: str, user_id: str) -> GenerationStatus:
        """Get status of generation task"""
        if task_id not in _generation_tasks:
            raise ValueError(f"Generation task {task_id} not found")
        
        return _generation_tasks[task_id]
    
    async def _run_generation(
        self,
        task_id: str,
        config: DomainConfig,
        user_id: str,
        generate_backend: bool,
        generate_frontend: bool,
        target_directory: Optional[str]
    ):
        """Run the actual code generation"""
        status = _generation_tasks[task_id]
        
        try:
            status.status = "running"
            status.current_step = "Analyzing configuration..."
            status.progress = 10
            await asyncio.sleep(1)  # Simulate work
            
            # Step 2: Generate models
            status.current_step = "Generating database models..."
            status.progress = 30
            await asyncio.sleep(1)
            
            # Step 3: Generate API endpoints
            status.current_step = "Creating API endpoints..."
            status.progress = 50
            await asyncio.sleep(1)
            
            # Step 4: Generate frontend components
            status.current_step = "Building frontend components..."
            status.progress = 80
            await asyncio.sleep(1)
            
            # Step 5: Finalize
            status.current_step = "Finalizing code structure..."
            status.progress = 100
            status.status = "completed"
            status.completed_at = datetime.utcnow()
            
            # Mock generated files
            status.files_generated = 15  # Simulate file count
            
        except Exception as e:
            status.status = "failed"
            status.errors.append(str(e))
            status.completed_at = datetime.utcnow()
    
    async def generate_preview(self, config: DomainConfig) -> Dict[str, Any]:
        """Generate a preview of what the template will produce"""
        entity_previews = []
        
        if config.entities:
            for entity in config.entities:
                entity_previews.append({
                    "name": entity.name,
                    "title": entity.title,
                    "field_count": len(entity.fields),
                    "relationship_count": len(entity.relationships) if entity.relationships else 0,
                    "sample_data": [
                        {field.name: f"sample_{field.type}" for field in entity.fields[:3]}
                    ]
                })
        
        api_endpoints = []
        if config.entities:
            for entity in config.entities:
                base_path = f"/api/v1/{entity.name.lower()}s"
                api_endpoints.extend([
                    f"GET {base_path}",
                    f"POST {base_path}",
                    f"GET {base_path}/{{id}}",
                    f"PUT {base_path}/{{id}}",
                    f"DELETE {base_path}/{{id}}"
                ])
        
        ui_components = []
        if config.entities:
            for entity in config.entities:
                name = entity.name.lower().capitalize()
                ui_components.extend([
                    f"{name}List.tsx",
                    f"{name}Detail.tsx",
                    f"{name}Form.tsx",
                    f"{name}Card.tsx"
                ])
        
        return {
            "domain_config": config.dict(),
            "preview_data": {
                "entities": entity_previews,
                "api_endpoints": api_endpoints,
                "ui_components": ui_components,
                "estimated_files": len(api_endpoints) * 2 + len(ui_components) + 5,
                "estimated_lines": len(config.entities or []) * 300 if config.entities else 100
            }
        }

class TemplateService:
    """Service for managing template configurations"""
    
    async def create_template(
        self,
        db: AsyncSession,
        template_data: TemplateConfigCreate,
        user_id: str
    ) -> TemplateConfigResponse:
        """Create a new template configuration"""
        template_id = str(uuid.uuid4())
        
        template = TemplateConfigModel(
            id=template_id,
            name=template_data.name,
            title=template_data.title,
            description=template_data.description,
            tags=template_data.tags,
            is_public=template_data.is_public,
            config=template_data.config.dict(),
            created_by=user_id
        )
        
        _templates_storage[template_id] = template
        
        return TemplateConfigResponse(
            id=template.id,
            name=template.name,
            title=template.title,
            description=template.description,
            tags=template.tags,
            is_public=template.is_public,
            config=DomainConfig(**template.config),
            created_at=template.created_at,
            updated_at=template.updated_at,
            created_by=template.created_by,
            downloads=template.downloads,
            rating=template.rating
        )
    
    async def list_templates(
        self,
        db: AsyncSession,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        domain_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> TemplateListResponse:
        """List templates with filtering"""
        templates = list(_templates_storage.values())
        
        # Filter by domain type
        if domain_type:
            templates = [t for t in templates if t.config.get('domain_type') == domain_type]
        
        # Filter by search term
        if search:
            search_lower = search.lower()
            templates = [
                t for t in templates 
                if search_lower in t.title.lower() 
                or search_lower in (t.description or '').lower()
            ]
        
        # Apply pagination
        total = len(templates)
        templates = templates[skip:skip + limit]
        
        template_metadata = []
        for template in templates:
            metadata = TemplateMetadata(
                id=template.id,
                name=template.name,
                title=template.title,
                description=template.description,
                domain_type=template.config.get('domain_type', 'custom'),
                version=template.config.get('version', '1.0.0'),
                tags=template.tags,
                created_at=template.created_at,
                updated_at=template.updated_at,
                created_by=template.created_by,
                downloads=template.downloads,
                rating=template.rating,
                is_public=template.is_public
            )
            template_metadata.append(metadata)
        
        return TemplateListResponse(
            templates=template_metadata,
            total=total,
            page=(skip // limit) + 1,
            per_page=limit,
            has_next=(skip + limit) < total,
            has_prev=skip > 0
        )
    
    async def get_template_by_id(
        self,
        db: AsyncSession,
        template_id: str,
        user_id: str
    ) -> Optional[TemplateConfigResponse]:
        """Get template by ID"""
        template = _templates_storage.get(template_id)
        if not template:
            return None
        
        return TemplateConfigResponse(
            id=template.id,
            name=template.name,
            title=template.title,
            description=template.description,
            tags=template.tags,
            is_public=template.is_public,
            config=DomainConfig(**template.config),
            created_at=template.created_at,
            updated_at=template.updated_at,
            created_by=template.created_by,
            downloads=template.downloads,
            rating=template.rating
        )
    
    async def update_template(
        self,
        db: AsyncSession,
        template_id: str,
        template_data: TemplateConfigUpdate,
        user_id: str
    ) -> Optional[TemplateConfigResponse]:
        """Update template configuration"""
        template = _templates_storage.get(template_id)
        if not template:
            return None
        
        # Update fields
        if template_data.title:
            template.title = template_data.title
        if template_data.description is not None:
            template.description = template_data.description
        if template_data.tags is not None:
            template.tags = template_data.tags
        if template_data.is_public is not None:
            template.is_public = template_data.is_public
        if template_data.config:
            template.config = template_data.config.dict()
        
        template.updated_at = datetime.utcnow()
        
        return TemplateConfigResponse(
            id=template.id,
            name=template.name,
            title=template.title,
            description=template.description,
            tags=template.tags,
            is_public=template.is_public,
            config=DomainConfig(**template.config),
            created_at=template.created_at,
            updated_at=template.updated_at,
            created_by=template.created_by,
            downloads=template.downloads,
            rating=template.rating
        )
    
    async def delete_template(
        self,
        db: AsyncSession,
        template_id: str,
        user_id: str
    ) -> bool:
        """Delete template configuration"""
        if template_id in _templates_storage:
            del _templates_storage[template_id]
            return True
        return False
    
    async def is_name_available(
        self,
        db: AsyncSession,
        name: str,
        user_id: str
    ) -> bool:
        """Check if template name is available"""
        for template in _templates_storage.values():
            if template.name == name:
                return False
        return True
    
    async def clone_template(
        self,
        db: AsyncSession,
        template_id: str,
        new_name: str,
        user_id: str
    ) -> Optional[TemplateConfigResponse]:
        """Clone an existing template"""
        source_template = _templates_storage.get(template_id)
        if not source_template:
            return None
        
        new_template_id = str(uuid.uuid4())
        cloned_template = TemplateConfigModel(
            id=new_template_id,
            name=new_name,
            title=f"{source_template.title} (Copy)",
            description=source_template.description,
            tags=source_template.tags.copy(),
            is_public=False,  # Cloned templates start as private
            config=source_template.config.copy(),
            created_by=user_id
        )
        
        _templates_storage[new_template_id] = cloned_template
        
        return TemplateConfigResponse(
            id=cloned_template.id,
            name=cloned_template.name,
            title=cloned_template.title,
            description=cloned_template.description,
            tags=cloned_template.tags,
            is_public=cloned_template.is_public,
            config=DomainConfig(**cloned_template.config),
            created_at=cloned_template.created_at,
            updated_at=cloned_template.updated_at,
            created_by=cloned_template.created_by,
            downloads=cloned_template.downloads,
            rating=cloned_template.rating
        )
    
    async def import_template(
        self,
        db: AsyncSession,
        file_content: dict,
        user_id: str
    ) -> TemplateConfigResponse:
        """Import template from file content"""
        try:
            # Validate structure
            if 'config' not in file_content:
                raise ValueError("Template file must contain 'config' field")
            
            config = DomainConfig(**file_content['config'])
            
            template_data = TemplateConfigCreate(
                name=file_content.get('name', config.name),
                title=file_content.get('title', config.title),
                description=file_content.get('description', config.description),
                tags=file_content.get('tags', []),
                is_public=file_content.get('is_public', False),
                config=config
            )
            
            return await self.create_template(db, template_data, user_id)
            
        except Exception as e:
            raise ValueError(f"Invalid template file format: {str(e)}")
    
    async def export_template(self, template: TemplateConfigResponse) -> dict:
        """Export template as dictionary"""
        return {
            "format_version": "1.0",
            "exported_at": datetime.utcnow().isoformat(),
            "name": template.name,
            "title": template.title,
            "description": template.description,
            "tags": template.tags,
            "config": template.config.dict(),
            "metadata": {
                "created_at": template.created_at.isoformat(),
                "updated_at": template.updated_at.isoformat(),
                "version": template.config.version
            }
        }

# Service instances
validation_service = ValidationService()
code_generation_service = CodeGenerationService()
template_service = TemplateService()