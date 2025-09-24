"""Template system models for tracking templates and domains."""

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime

from app.models.base import BaseModel, JSONField


class TemplateStatus(PyEnum):
    """Template status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class DomainTemplate(BaseModel):
    """Template definition for a specific domain."""
    
    __tablename__ = "domain_templates"
    
    # Template identification
    name = Column(String(255), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Template metadata
    domain_type = Column(String(100), nullable=False, index=True)
    version = Column(String(50), nullable=False, default="1.0.0")
    status = Column(Enum(TemplateStatus), default=TemplateStatus.DRAFT, nullable=False)
    
    # Template configuration
    config_schema = Column(JSONField, nullable=False)  # Domain configuration
    entities_config = Column(JSONField, nullable=False)  # Entity definitions
    ui_config = Column(JSONField, nullable=True)  # UI configuration
    navigation_config = Column(JSONField, nullable=True)  # Navigation structure
    
    # Template features
    features = Column(JSONField, nullable=True)  # Enabled features
    custom_config = Column(JSONField, nullable=True)  # Custom settings
    
    # Template metadata
    created_by = Column(String(255), nullable=True)
    is_official = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    
    # Usage statistics
    usage_count = Column(Integer, default=0, nullable=False)
    last_used = Column(DateTime, nullable=True)
    
    def to_domain_config(self):
        """Convert template to domain configuration object."""
        from app.core.template_config import DomainConfig, DomainType
        
        return DomainConfig(
            name=self.name,
            title=self.title,
            description=self.description or "",
            domain_type=DomainType(self.domain_type),
            version=self.version,
            entities=[],  # Would be parsed from entities_config
            navigation=[],  # Would be parsed from navigation_config
            features=self.features or {},
            custom_config=self.custom_config or {}
        )


class DomainInstance(BaseModel):
    """Instance of a domain created from a template."""
    
    __tablename__ = "domain_instances"
    
    # Instance identification
    name = Column(String(255), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Template reference
    template_id = Column(Integer, nullable=False, index=True)
    template_version = Column(String(50), nullable=False)
    
    # Instance configuration
    instance_config = Column(JSONField, nullable=False)  # Customized configuration
    entity_mappings = Column(JSONField, nullable=True)  # Entity customizations
    ui_customizations = Column(JSONField, nullable=True)  # UI customizations
    
    # Instance metadata
    organization_id = Column(Integer, nullable=True, index=True)  # Multi-tenant support
    created_by = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Usage tracking
    last_accessed = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0, nullable=False)


class TemplateUsage(BaseModel):
    """Track template usage and analytics."""
    
    __tablename__ = "template_usage"
    
    # Usage identification
    template_id = Column(Integer, nullable=False, index=True)
    instance_id = Column(Integer, nullable=True, index=True)
    
    # Usage details
    action = Column(String(100), nullable=False)  # created, updated, accessed, etc.
    user_id = Column(String(255), nullable=True)
    organization_id = Column(Integer, nullable=True, index=True)
    
    # Context information
    context_data = Column(JSONField, nullable=True)  # Additional context
    duration = Column(Integer, nullable=True)  # Duration in seconds
    
    # Metadata
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    @classmethod
    def log_usage(cls, template_id: int, action: str, **kwargs):
        """Helper method to log template usage."""
        usage = cls(
            template_id=template_id,
            action=action,
            instance_id=kwargs.get('instance_id'),
            user_id=kwargs.get('user_id'),
            organization_id=kwargs.get('organization_id'),
            context_data=kwargs.get('context_data'),
            duration=kwargs.get('duration'),
            user_agent=kwargs.get('user_agent'),
            ip_address=kwargs.get('ip_address')
        )
        return usage


class TemplateRegistry:
    """Registry for managing available templates."""
    
    def __init__(self):
        self._templates = {}
    
    def register_template(self, template: DomainTemplate):
        """Register a new template."""
        self._templates[template.name] = template
    
    def get_template(self, name: str) -> DomainTemplate:
        """Get template by name."""
        return self._templates.get(name)
    
    def list_templates(self, domain_type: str = None, status: TemplateStatus = None):
        """List available templates with optional filtering."""
        templates = list(self._templates.values())
        
        if domain_type:
            templates = [t for t in templates if t.domain_type == domain_type]
        
        if status:
            templates = [t for t in templates if t.status == status]
        
        return templates
    
    def get_popular_templates(self, limit: int = 10):
        """Get most popular templates by usage count."""
        templates = list(self._templates.values())
        return sorted(templates, key=lambda t: t.usage_count, reverse=True)[:limit]


# Global template registry
template_registry = TemplateRegistry()