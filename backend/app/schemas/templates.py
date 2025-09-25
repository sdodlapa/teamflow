"""
Pydantic schemas for template models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, validator

from app.models.templates import TemplateStatus, CollaboratorPermissions


# Enums
class TemplateStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CollaboratorPermissions(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class CollaborationAction(str, Enum):
    JOIN = "join"
    LEAVE = "leave"
    EDIT = "edit"
    COMMENT = "comment"
    SAVE = "save"
    PUBLISH = "publish"
    ARCHIVE = "archive"


# Domain configuration schemas
class DomainConfig(BaseModel):
    """Domain configuration schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Domain name")
    title: str = Field(..., min_length=1, max_length=200, description="Domain title")
    description: str = Field(..., min_length=1, description="Domain description")
    domain_type: str = Field(..., description="Domain type")
    version: str = Field("1.0.0", description="Domain version")
    logo: Optional[str] = Field(None, description="Logo URL")
    color_scheme: str = Field("blue", description="Color scheme")
    theme: str = Field("modern", description="Theme")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Name can only contain letters, numbers, hyphens, and underscores')
        return v.lower()


# Entity and Field schemas (matching frontend types)
class Field(BaseModel):
    """Field schema"""
    id: str
    name: str
    type: str
    required: bool = False
    unique: bool = False
    default_value: Optional[Union[str, int, float, bool]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class Entity(BaseModel):
    """Entity schema"""
    id: str
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    fields: List[Field] = []
    table_name: Optional[str] = None
    is_system: bool = False


class Relationship(BaseModel):
    """Relationship schema"""
    id: str
    name: str
    from_entity: str
    to_entity: str
    relationship_type: str  # one-to-one, one-to-many, many-to-many
    from_field: Optional[str] = None
    to_field: Optional[str] = None
    description: Optional[str] = None
    is_required: bool = False
    description: Optional[str] = None
    sourceEntityId: str
    targetEntityId: str
    type: str
    isRequired: bool = False
    metadata: Optional[Dict[str, Any]] = None


class DomainConfig(BaseModel):
    """Domain configuration for template."""
    name: str
    title: str
    description: Optional[str] = None
    version: str = "1.0.0"
    domainType: str
    features: Optional[Dict[str, Any]] = None
    uiConfig: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class TemplateMetadata(BaseModel):
    """Template metadata."""
    version: int
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    createdBy: UUID
    collaborators: List[UUID] = []
    tags: List[str] = []
    isPublic: bool = False
    views: int = 0
    clones: int = 0


class TemplateBase(BaseModel):
    """Base schema for template creation and updates."""
    name: str
    description: Optional[str] = None
    domainConfig: DomainConfig
    entities: List[Entity] = []
    relationships: List[Relationship] = []
    tags: List[str] = []
    isPublic: bool = False


class TemplateCreate(TemplateBase):
    """Schema for creating a new template."""
    organizationId: Optional[UUID] = None


class TemplateUpdate(BaseModel):
    """Schema for updating a template."""
    name: Optional[str] = None
    description: Optional[str] = None
    domainConfig: Optional[DomainConfig] = None
    entities: Optional[List[Entity]] = None
    relationships: Optional[List[Relationship]] = None
    tags: Optional[List[str]] = None
    isPublic: Optional[bool] = None
    changeDescription: Optional[str] = None


class TemplateVersionCreate(BaseModel):
    """Schema for creating a template version."""
    domainConfig: DomainConfig
    entities: List[Entity]
    relationships: List[Relationship]
    changeDescription: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None


class CollaboratorCreate(BaseModel):
    """Schema for adding a collaborator to a template."""
    userId: UUID
    permissions: CollaboratorPermissions = CollaboratorPermissions.READ


class TemplateResponse(TemplateBase):
    """Schema for template response."""
    id: UUID
    status: TemplateStatus
    metadata: TemplateMetadata
    organizationId: Optional[UUID] = None
    
    class Config:
        orm_mode = True


class TemplateListResponse(BaseModel):
    """Schema for template list response."""
    templates: List[TemplateResponse]
    total: int
    page: int
    limit: int


class TemplateVersionResponse(BaseModel):
    """Schema for template version response."""
    id: UUID
    templateId: UUID
    versionNumber: int
    domainConfig: DomainConfig
    entities: List[Entity]
    relationships: List[Relationship]
    changes: Optional[Dict[str, Any]] = None
    changeDescription: Optional[str] = None
    createdById: UUID
    createdAt: datetime
    
    class Config:
        orm_mode = True


class TemplateCollaboratorResponse(BaseModel):
    """Schema for template collaborator response."""
    id: UUID
    templateId: UUID
    userId: UUID
    permissions: CollaboratorPermissions
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class CollaborationHistoryResponse(BaseModel):
    """Schema for collaboration history response."""
    id: UUID
    templateId: UUID
    userId: UUID
    action: CollaborationAction
    actionData: Optional[Dict[str, Any]] = None
    createdAt: datetime
    
    class Config:
        orm_mode = True


class TemplateAnalyticsResponse(BaseModel):
    """Schema for template analytics response."""
    views: int = 0
    clones: int = 0
    collaborators: int = 0
    versions: int = 0
    lastActivity: Optional[datetime] = None
    popularEntities: List[str] = []
    usageByDate: List[Dict[str, Any]] = []