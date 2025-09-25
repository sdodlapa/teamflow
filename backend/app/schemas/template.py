"""
Pydantic schemas for template builder API
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import uuid

# Base schemas for template configuration
class FieldType(str, Enum):
    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    EMAIL = "email"
    URL = "url"
    UUID = "uuid"
    JSON = "json"
    FILE = "file"
    IMAGE = "image"
    ENUM = "enum"
    ARRAY = "array"

class RelationshipType(str, Enum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"

class Permission(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"
    DETAIL = "detail"

class DomainType(str, Enum):
    TASK_MANAGEMENT = "task_management"
    E_COMMERCE = "e_commerce"
    CRM = "crm"
    HEALTHCARE = "healthcare"
    REAL_ESTATE = "real_estate"
    EDUCATION = "education"
    FINANCE = "finance"
    CUSTOM = "custom"

class ColorScheme(str, Enum):
    BLUE = "blue"
    GREEN = "green"
    PURPLE = "purple"
    RED = "red"
    ORANGE = "orange"
    PINK = "pink"
    GRAY = "gray"
    DARK = "dark"

class Theme(str, Enum):
    DEFAULT = "default"
    MODERN = "modern"
    MINIMAL = "minimal"
    DARK = "dark"
    COLORFUL = "colorful"

# Field configuration schemas
class ValidationConfig(BaseModel):
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    choices: Optional[List[str]] = None
    custom_validator: Optional[str] = None

class FieldUIConfig(BaseModel):
    widget: Optional[str] = None
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    grid_column: Optional[int] = None
    hide_in_list: Optional[bool] = False
    hide_in_form: Optional[bool] = False

class FieldConfig(BaseModel):
    name: str = Field(..., description="Field name (snake_case)")
    title: str = Field(..., description="Human-readable field title")
    type: FieldType = Field(..., description="Field data type")
    required: bool = Field(default=False, description="Whether field is required")
    default_value: Optional[Any] = Field(default=None, description="Default field value")
    validation: Optional[ValidationConfig] = None
    ui_config: Optional[FieldUIConfig] = None

class RelationshipConfig(BaseModel):
    name: str = Field(..., description="Relationship name")
    type: RelationshipType = Field(..., description="Relationship type")
    target_entity: str = Field(..., description="Target entity name")
    foreign_key: Optional[str] = None
    back_populates: Optional[str] = None
    cascade: Optional[List[str]] = None

class PermissionConfig(BaseModel):
    role: str = Field(..., description="Role name")
    permissions: List[Permission] = Field(..., description="Allowed permissions")

class FormLayout(BaseModel):
    section: str = Field(..., description="Section name")
    fields: List[str] = Field(..., description="Fields in this section")
    columns: Optional[int] = Field(default=1, description="Number of columns")

class EntityUIConfig(BaseModel):
    icon: Optional[str] = None
    color: Optional[str] = None
    list_display: Optional[List[str]] = None
    search_fields: Optional[List[str]] = None
    filter_fields: Optional[List[str]] = None
    form_layout: Optional[List[FormLayout]] = None

class EntityConfig(BaseModel):
    name: str = Field(..., description="Entity name (snake_case)")
    title: str = Field(..., description="Human-readable entity title")
    description: Optional[str] = None
    fields: List[FieldConfig] = Field(..., description="Entity fields")
    relationships: Optional[List[RelationshipConfig]] = None
    permissions: Optional[List[PermissionConfig]] = None
    ui_config: Optional[EntityUIConfig] = None

class FeatureConfig(BaseModel):
    name: str = Field(..., description="Feature name")
    enabled: bool = Field(default=True, description="Whether feature is enabled")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Feature-specific configuration")

class DomainConfig(BaseModel):
    name: str = Field(..., description="Domain name (snake_case)")
    title: str = Field(..., description="Human-readable domain title")
    description: Optional[str] = None
    domain_type: DomainType = Field(default=DomainType.CUSTOM)
    version: str = Field(default="1.0.0", description="Semantic version")
    logo: Optional[str] = Field(default="🏢", description="Logo emoji or icon")
    color_scheme: ColorScheme = Field(default=ColorScheme.BLUE)
    theme: Theme = Field(default=Theme.DEFAULT)
    entities: Optional[List[EntityConfig]] = Field(default_factory=list)
    features: Optional[List[FeatureConfig]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

# Validation schemas
class ValidationError(BaseModel):
    field: str = Field(..., description="Field path where error occurred")
    message: str = Field(..., description="Error message")
    code: Optional[str] = None

class ValidationResult(BaseModel):
    is_valid: bool = Field(..., description="Whether validation passed")
    errors: Optional[List[ValidationError]] = None
    warnings: Optional[List[ValidationError]] = None

class ValidationRequest(BaseModel):
    config: DomainConfig = Field(..., description="Domain configuration to validate")

class ValidationResponse(BaseModel):
    is_valid: bool = Field(..., description="Whether validation passed")
    errors: Optional[List[ValidationError]] = None
    warnings: Optional[List[ValidationError]] = None

# Code generation schemas
class GeneratedFile(BaseModel):
    path: str = Field(..., description="File path relative to output directory")
    type: str = Field(..., description="File type: model, schema, api, component, config")
    size: int = Field(..., description="File size in bytes")
    checksum: str = Field(..., description="File content checksum")

class GenerationRequest(BaseModel):
    domain_config: DomainConfig = Field(..., description="Domain configuration")
    generate_backend: bool = Field(default=True, description="Generate backend code")
    generate_frontend: bool = Field(default=True, description="Generate frontend code")
    target_directory: Optional[str] = None

class GenerationResponse(BaseModel):
    success: bool = Field(..., description="Whether generation succeeded")
    files_generated: List[GeneratedFile] = Field(default_factory=list)
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    task_id: Optional[str] = None
    message: Optional[str] = None

class GenerationStatus(BaseModel):
    status: str = Field(..., description="pending, running, completed, failed")
    progress: int = Field(..., description="Progress percentage 0-100")
    current_step: str = Field(..., description="Current generation step")
    total_steps: int = Field(..., description="Total number of steps")
    files_generated: int = Field(default=0)
    errors: List[str] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

# Template CRUD schemas
class TemplateConfigBase(BaseModel):
    name: str = Field(..., description="Unique template name")
    title: str = Field(..., description="Template display title")
    description: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    is_public: bool = Field(default=False, description="Whether template is publicly available")
    config: DomainConfig = Field(..., description="Template domain configuration")

class TemplateConfigCreate(TemplateConfigBase):
    pass

class TemplateConfigUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    config: Optional[DomainConfig] = None

class TemplateConfigResponse(TemplateConfigBase):
    id: str = Field(..., description="Template unique ID")
    created_at: datetime
    updated_at: datetime
    created_by: str = Field(..., description="Creator user ID")
    downloads: int = Field(default=0)
    rating: Optional[float] = None
    
    class Config:
        from_attributes = True

class TemplateMetadata(BaseModel):
    id: str
    name: str
    title: str
    description: Optional[str]
    domain_type: DomainType
    version: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    created_by: str
    downloads: int
    rating: Optional[float]
    is_public: bool

class TemplateListResponse(BaseModel):
    templates: List[TemplateMetadata]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

# Preview schemas
class EntityPreview(BaseModel):
    name: str
    title: str
    field_count: int
    relationship_count: int
    sample_data: List[Dict[str, Any]] = Field(default_factory=list)

class TemplatePreview(BaseModel):
    domain_config: DomainConfig
    preview_data: Dict[str, Any] = Field(
        description="Preview data including entities, endpoints, components"
    )

# API response wrapper
class ApiResponse(BaseModel):
    success: bool = Field(..., description="Whether request succeeded")
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: Optional[List[ValidationError]] = None

# Template marketplace schemas
class TemplateDownloadRequest(BaseModel):
    template_id: str
    target_directory: Optional[str] = None

class TemplateRatingRequest(BaseModel):
    template_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review: Optional[str] = None

class TemplateSearchRequest(BaseModel):
    query: Optional[str] = None
    domain_type: Optional[DomainType] = None
    tags: Optional[List[str]] = None
    min_rating: Optional[float] = None
    sort_by: Optional[str] = Field(default="created_at", description="Sort field")
    sort_order: Optional[str] = Field(default="desc", description="asc or desc")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


# Code Generation Results Schemas
class GenerationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GeneratedFile(BaseModel):
    path: str = Field(..., description="Relative path of the generated file")
    content: str = Field(..., description="Generated file content")
    size: int = Field(..., description="File size in bytes")
    type: str = Field(..., description="File type (e.g., 'model', 'api', 'frontend')")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GenerationResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_name: str = Field(..., description="Name of the entity generated")
    files: List[GeneratedFile] = Field(default_factory=list)
    status: GenerationStatus = Field(default=GenerationStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    
    @property
    def total_files(self) -> int:
        return len(self.files)
    
    @property
    def total_size(self) -> int:
        return sum(f.size for f in self.files)


class GenerationSummary(BaseModel):
    domain_name: str
    total_entities: int
    successful_generations: int
    failed_generations: int
    total_files: int
    total_size: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    results: List[GenerationResult] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        if self.total_entities == 0:
            return 0.0
        return (self.successful_generations / self.total_entities) * 100