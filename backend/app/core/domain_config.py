"""
Domain Configuration Classes
For Section 3: Code Generation Engine
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from enum import Enum


class FieldType(str, Enum):
    """Supported field types."""
    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    JSON = "json"
    ENUM = "enum"


class RelationshipType(str, Enum):
    """Supported relationship types."""
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"


@dataclass
class EnumOption:
    """Enum option configuration."""
    value: str
    label: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ValidationRule:
    """Field validation rule."""
    type: str  # 'email', 'phone', 'range', 'regex', etc.
    field: str
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    message: Optional[str] = None


@dataclass
class FieldConfig:
    """Field configuration."""
    name: str
    type: FieldType
    required: bool = False
    unique: bool = False
    default: Optional[Any] = None
    description: Optional[str] = None
    max_length: Optional[int] = None
    updatable: bool = True
    
    # For enum fields
    options: Optional[List[EnumOption]] = None
    
    # For validation
    validations: Optional[List[ValidationRule]] = None


@dataclass  
class RelationshipConfig:
    """Relationship configuration."""
    name: str
    target: str
    type: RelationshipType
    required: bool = False
    description: Optional[str] = None
    
    # For many-to-many relationships
    through_table: Optional[str] = None
    
    # Back reference name
    back_populates: Optional[str] = None


@dataclass
class CustomEndpoint:
    """Custom API endpoint configuration."""
    name: str
    method: str  # GET, POST, PUT, DELETE
    path: str
    description: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = None


@dataclass
class PermissionConfig:
    """Permission configuration."""
    read: Optional[str] = None
    create: Optional[str] = None
    update: Optional[str] = None
    delete: Optional[str] = None


@dataclass
class SortConfig:
    """Default sort configuration."""
    field: str
    direction: str = "asc"  # asc or desc


@dataclass
class EntityConfig:
    """Entity configuration."""
    name: str
    description: Optional[str] = None
    fields: List[FieldConfig] = field(default_factory=list)
    relationships: List[RelationshipConfig] = field(default_factory=list)
    
    # Display configuration
    display_field: Optional[str] = None
    
    # Behavior configuration
    soft_delete: bool = False
    bulk_operations: bool = True
    
    # API configuration
    filterable_fields: Optional[List[FieldConfig]] = None
    searchable_fields: Optional[List[FieldConfig]] = None
    required_on_create: Optional[List[str]] = None
    unique_constraints: Optional[List[List[str]]] = None
    
    # Permission configuration
    permissions: Optional[PermissionConfig] = None
    
    # Sorting
    default_sort: Optional[SortConfig] = None
    
    # Custom endpoints
    custom_endpoints: Optional[List[CustomEndpoint]] = None
    
    # Computed properties
    @property
    def enums(self) -> List[FieldConfig]:
        """Get all enum fields."""
        return [f for f in self.fields if f.type == FieldType.ENUM]
    
    @property
    def validations(self) -> List[ValidationRule]:
        """Get all validation rules from all fields."""
        validations = []
        for field_config in self.fields:
            if field_config.validations:
                validations.extend(field_config.validations)
        return validations


@dataclass
class DomainConfig:
    """Domain configuration."""
    name: str
    description: Optional[str] = None
    entities: List[EntityConfig] = field(default_factory=list)
    
    # Global configuration
    api_prefix: str = "/api/v1"
    enable_audit: bool = True
    enable_cache: bool = False
    
    def get_entity(self, name: str) -> Optional[EntityConfig]:
        """Get entity by name."""
        for entity in self.entities:
            if entity.name == name:
                return entity
        return None