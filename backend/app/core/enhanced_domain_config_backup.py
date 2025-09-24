"""
Enhanced domain configuration system using Pydantic models.
Phase 2: Template Engine Section 2 - Enhanced Configuration System
"""

from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Set
from pathlib import Path
import yaml
import json
import logging
from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Configuration-related errors."""
    pass


class DomainType(str, Enum):
    """Available domain types."""
    BUSINESS = "business"
    TECHNICAL = "technical"
    EDUCATIONAL = "educational"
    HEALTHCARE = "healthcare"
    ECOMMERCE = "ecommerce"
    REAL_ESTATE = "real_estate"
    FINANCE = "finance"
    OTHER = "other"


class FieldType(str, Enum):
    """Available field types."""
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    TEXT = "text"
    JSON = "json"
    FILE = "file"


class ValidationRule(str, Enum):
    """Predefined validation rules."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    EMAIL_FORMAT = "email_format"
    PHONE_FORMAT = "phone_format"
    URL_FORMAT = "url"
    ALPHANUMERIC = "alphanumeric"
    LETTERS_ONLY = "letters_only"
    NUMBERS_ONLY = "numbers_only"
    NO_SPACES = "no_spaces"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    REGEX = "regex"
    # Custom domain-specific rules
    AFTER_LEASE_START = "after_lease_start"


class UIComponent(str, Enum):
    """Available UI components for fields."""
    INPUT = "input"
    TEXTAREA = "textarea"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DATE_PICKER = "date_picker"
    FILE_UPLOAD = "file_upload"
    RICH_TEXT = "rich_text"
    NUMBER_INPUT = "number_input"
    SLIDER = "slider"
    RATING = "rating"
    COLOR_PICKER = "color_picker"
    # Additional UI components for complex data
    JSON = "json"
    IMAGE_GALLERY = "image_gallery"esign - Section 2 Implementation
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Union, Literal
from pathlib import Path
from enum import Enum
import yaml
import json
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import StrictStr, StrictInt, StrictBool


class FieldType(str, Enum):
    """Supported field types for domain entities."""
    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ENUM = "enum"
    JSON = "json"
    UUID = "uuid"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    FILE = "file"
    IMAGE = "image"


class RelationshipType(str, Enum):
    """Supported relationship types between entities."""
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"


class ValidationRule(str, Enum):
    """Predefined validation rules."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    EMAIL_FORMAT = "email_format"
    PHONE_FORMAT = "phone_format"
    URL_FORMAT = "url"
    ALPHANUMERIC = "alphanumeric"
    LETTERS_ONLY = "letters_only"
    NUMBERS_ONLY = "numbers_only"
    NO_SPACES = "no_spaces"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    REGEX = "regex"
    # Custom domain-specific rules
    AFTER_LEASE_START = "after_lease_start"


class DomainType(str, Enum):
    """Supported domain types for template system."""
    TASK_MANAGEMENT = "task_management"
    PROPERTY_MANAGEMENT = "property_management"
    E_COMMERCE = "e_commerce"
    HEALTHCARE = "healthcare"
    RESTAURANT = "restaurant"
    EDUCATION = "education"
    FINANCE = "finance"
    INVENTORY = "inventory"
    CRM = "crm"
    PROJECT_MANAGEMENT = "project_management"
    CUSTOM = "custom"


class PermissionLevel(str, Enum):
    """User permission levels."""
    PUBLIC = "public"
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"
    OWNER = "owner"


class UIComponentType(str, Enum):
    """UI component types for fields."""
    INPUT = "input"
    TEXTAREA = "textarea"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DATE_PICKER = "date_picker"
    FILE_UPLOAD = "file_upload"
    RICH_TEXT = "rich_text"
    NUMBER_INPUT = "number_input"
    SLIDER = "slider"
    RATING = "rating"
    COLOR_PICKER = "color_picker"


class FieldValidation(BaseModel):
    """Validation configuration for entity fields."""
    rule: ValidationRule = Field(..., description="Validation rule to apply")
    value: Optional[Union[str, int, float, bool]] = Field(None, description="Validation parameter value")
    message: Optional[str] = Field(None, description="Custom validation error message")
    
    class Config:
        use_enum_values = True


class FieldConfig(BaseModel):
    """Configuration for entity field."""
    name: StrictStr = Field(..., description="Field name (snake_case)")
    type: FieldType = Field(..., description="Field data type")
    display_name: Optional[str] = Field(None, description="Human-readable field name")
    description: Optional[str] = Field(None, description="Field description")
    
    # Field constraints
    required: bool = Field(False, description="Whether field is required")
    nullable: bool = Field(True, description="Whether field can be null")
    unique: bool = Field(False, description="Whether field must be unique")
    indexed: bool = Field(False, description="Whether field should be indexed")
    
    # Type-specific constraints
    max_length: Optional[int] = Field(None, description="Maximum length for string fields")
    min_length: Optional[int] = Field(None, description="Minimum length for string fields")
    min_value: Optional[float] = Field(None, description="Minimum value for numeric fields")
    max_value: Optional[float] = Field(None, description="Maximum value for numeric fields")
    
    # Default value and choices
    default: Optional[Any] = Field(None, description="Default field value")
    choices: Optional[List[str]] = Field(None, description="Predefined choices for enum fields")
    
    # Validation rules
    validations: List[FieldValidation] = Field(default_factory=list, description="Validation rules")
    
    # UI configuration
    ui_component: UIComponentType = Field(UIComponentType.INPUT, description="UI component type")
    ui_config: Dict[str, Any] = Field(default_factory=dict, description="Additional UI configuration")
    
    # Display configuration  
    sortable: bool = Field(True, description="Whether field can be sorted in lists")
    searchable: bool = Field(False, description="Whether field is searchable")
    filterable: bool = Field(False, description="Whether field can be filtered")
    show_in_list: bool = Field(True, description="Whether to show field in list views")
    show_in_detail: bool = Field(True, description="Whether to show field in detail views")
    
    class Config:
        use_enum_values = True
    
    @field_validator('display_name')
    @classmethod
    def set_display_name(cls, v, info):
        if not v and 'name' in info.data:
            # Convert snake_case to Title Case
            return ' '.join(word.capitalize() for word in info.data['name'].split('_'))
        return v
    
    @field_validator('choices')
    @classmethod
    def validate_enum_choices(cls, v, info):
        if info.data.get('type') == FieldType.ENUM and not v:
            raise ValueError('Enum fields must have choices defined')
        return v
    
    @field_validator('max_length', 'min_length')
    @classmethod
    def validate_string_constraints(cls, v, info):
        if v is not None and info.data.get('type') not in [FieldType.STRING, FieldType.TEXT]:
            field_name = info.field_name
            raise ValueError(f'{field_name} can only be set for string/text fields')
        return v
    
    @field_validator('min_value', 'max_value')
    @classmethod
    def validate_numeric_constraints(cls, v, info):
        if v is not None and info.data.get('type') not in [FieldType.INTEGER, FieldType.DECIMAL]:
            field_name = info.field_name
            raise ValueError(f'{field_name} can only be set for numeric fields')
        return v


class RelationshipConfig(BaseModel):
    """Configuration for entity relationship."""
    name: StrictStr = Field(..., description="Relationship name")
    target_entity: StrictStr = Field(..., description="Target entity name")
    type: RelationshipType = Field(..., description="Relationship type")
    
    # Foreign key configuration
    foreign_key: Optional[str] = Field(None, description="Foreign key column name")
    target_foreign_key: Optional[str] = Field(None, description="Target foreign key for many-to-many")
    
    # Relationship metadata
    required: bool = Field(False, description="Whether relationship is required")
    cascade_delete: bool = Field(False, description="Whether to cascade deletes")
    back_populates: Optional[str] = Field(None, description="Reverse relationship name")
    
    # Display configuration
    display_name: Optional[str] = Field(None, description="Human-readable relationship name")
    description: Optional[str] = Field(None, description="Relationship description")
    show_in_forms: bool = Field(True, description="Whether to show in forms")
    
    class Config:
        use_enum_values = True
    
    @field_validator('display_name')
    @classmethod
    def set_display_name(cls, v, info):
        if not v and 'name' in info.data:
            return ' '.join(word.capitalize() for word in info.data['name'].split('_'))
        return v


class BusinessRule(BaseModel):
    """Business rule configuration."""
    name: StrictStr = Field(..., description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    
    # Rule definition
    condition: Optional[str] = Field(None, description="Rule condition (Python expression)")
    trigger: Optional[str] = Field(None, description="Trigger event (created, updated, deleted)")
    action: Optional[str] = Field(None, description="Action to perform")
    
    # Rule parameters
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Rule parameters")
    error_message: Optional[str] = Field(None, description="Error message when rule fails")
    
    # Rule metadata
    enabled: bool = Field(True, description="Whether rule is enabled")
    priority: int = Field(100, description="Rule execution priority (lower = higher priority)")


class EntityConfig(BaseModel):
    """Configuration for business entity."""
    name: StrictStr = Field(..., description="Entity name (snake_case)")
    display_name: Optional[str] = Field(None, description="Human-readable entity name")
    display_name_plural: Optional[str] = Field(None, description="Plural form")
    description: Optional[str] = Field(None, description="Entity description")
    
    # Table configuration
    table_name: Optional[str] = Field(None, description="Database table name")
    inherits_from: Optional[str] = Field(None, description="Parent entity to inherit from")
    
    # Entity structure
    fields: List[FieldConfig] = Field(default_factory=list, description="Entity fields")
    relationships: List[RelationshipConfig] = Field(default_factory=list, description="Entity relationships")
    business_rules: List[BusinessRule] = Field(default_factory=list, description="Business rules")
    
    # UI configuration
    icon: Optional[str] = Field(None, description="Entity icon (emoji or icon class)")
    color: Optional[str] = Field(None, description="Entity color theme")
    ui_config: Dict[str, Any] = Field(default_factory=dict, description="Additional UI configuration")
    
    # List/table configuration
    default_sort_field: Optional[str] = Field(None, description="Default sort field")
    default_sort_order: Literal["asc", "desc"] = Field("asc", description="Default sort order")
    items_per_page: int = Field(20, description="Default items per page")
    
    # Permissions
    permissions: Dict[str, List[PermissionLevel]] = Field(
        default_factory=lambda: {
            "create": [PermissionLevel.USER],
            "read": [PermissionLevel.USER],
            "update": [PermissionLevel.USER],
            "delete": [PermissionLevel.MANAGER]
        },
        description="Entity-level permissions"
    )
    
    class Config:
        use_enum_values = True
    
    @field_validator('display_name')
    @classmethod
    def set_display_name(cls, v, info):
        if not v and 'name' in info.data:
            return ' '.join(word.capitalize() for word in info.data['name'].split('_'))
        return v
    
    @field_validator('display_name_plural')
    @classmethod
    def set_plural_name(cls, v, info):
        if not v and 'display_name' in info.data:
            name = info.data['display_name']
            # Simple pluralization rules
            if name.endswith(('s', 'sh', 'ch', 'x', 'z')):
                return f"{name}es"
            elif name.endswith('y') and len(name) > 1 and name[-2] not in 'aeiou':
                return f"{name[:-1]}ies"
            else:
                return f"{name}s"
        return v
    
    @field_validator('table_name')
    @classmethod
    def set_table_name(cls, v, info):
        if not v and 'name' in info.data:
            return info.data['name'].lower()
        return v
    
    @field_validator('default_sort_field')
    @classmethod
    def validate_sort_field(cls, v, info):
        if v and 'fields' in info.data:
            field_names = [f.name for f in info.data['fields']]
            if v not in field_names:
                raise ValueError(f'default_sort_field "{v}" not found in entity fields')
        return v


class NavigationItem(BaseModel):
    """Navigation menu item configuration."""
    key: StrictStr = Field(..., description="Navigation item key")
    label: StrictStr = Field(..., description="Display label")
    icon: StrictStr = Field(..., description="Icon (emoji or icon class)")
    route: StrictStr = Field(..., description="Route path")
    
    # Navigation metadata
    description: Optional[str] = Field(None, description="Navigation item description")
    order: int = Field(0, description="Display order")
    parent: Optional[str] = Field(None, description="Parent navigation item")
    
    # Access control
    permissions: List[PermissionLevel] = Field(
        default_factory=lambda: [PermissionLevel.USER],
        description="Required permissions"
    )
    roles: List[str] = Field(default_factory=list, description="Required roles")
    
    # Display configuration
    visible: bool = Field(True, description="Whether item is visible")
    badge: Optional[str] = Field(None, description="Badge text")
    badge_color: Optional[str] = Field(None, description="Badge color")
    
    class Config:
        use_enum_values = True


class DashboardMetric(BaseModel):
    """Dashboard metric configuration."""
    name: StrictStr = Field(..., description="Metric name")
    label: StrictStr = Field(..., description="Display label")
    description: Optional[str] = Field(None, description="Metric description")
    
    # Data source
    entity: StrictStr = Field(..., description="Source entity")
    calculation: Literal["count", "sum", "avg", "min", "max", "count_distinct"] = Field(..., description="Calculation type")
    field: Optional[str] = Field(None, description="Field to calculate (for sum, avg, etc.)")
    condition: Optional[str] = Field(None, description="Filter condition")
    
    # Time period
    period: Optional[str] = Field(None, description="Time period (today, this_week, this_month, etc.)")
    
    # Display configuration
    icon: StrictStr = Field(..., description="Metric icon")
    color: Optional[str] = Field("blue", description="Metric color")
    format_type: Optional[str] = Field("number", description="Format type (number, currency, percentage)")
    format_precision: int = Field(0, description="Decimal precision")
    
    # Chart configuration
    show_chart: bool = Field(False, description="Whether to show trend chart")
    chart_type: Optional[str] = Field("line", description="Chart type")
    chart_period: Optional[str] = Field("last_30_days", description="Chart time period")


class DashboardChart(BaseModel):
    """Dashboard chart configuration."""
    name: StrictStr = Field(..., description="Chart name")
    title: StrictStr = Field(..., description="Chart title")
    type: Literal["bar", "line", "pie", "doughnut", "area", "scatter", "gauge"] = Field(..., description="Chart type")
    
    # Data source
    entity: StrictStr = Field(..., description="Source entity")
    x_axis: Optional[str] = Field(None, description="X-axis field")
    y_axis: Optional[str] = Field(None, description="Y-axis field")
    group_by: Optional[str] = Field(None, description="Grouping field")
    
    # Aggregation
    calculation: Literal["count", "sum", "avg", "min", "max"] = Field("count", description="Y-axis calculation")
    condition: Optional[str] = Field(None, description="Filter condition")
    time_period: Optional[str] = Field("last_30_days", description="Time period")
    
    # Display configuration
    width: int = Field(6, description="Chart width (1-12)")
    height: int = Field(300, description="Chart height in pixels")
    colors: List[str] = Field(default_factory=list, description="Custom colors")
    show_legend: bool = Field(True, description="Whether to show legend")
    show_labels: bool = Field(True, description="Whether to show labels")


class DomainMetadata(BaseModel):
    """Domain metadata configuration."""
    name: StrictStr = Field(..., description="Domain name (snake_case)")
    title: StrictStr = Field(..., description="Domain title")
    description: StrictStr = Field(..., description="Domain description")
    version: str = Field("1.0.0", description="Domain version")
    
    # Branding
    logo: str = Field("🏢", description="Domain logo (emoji or URL)")
    color_scheme: str = Field("blue", description="Primary color scheme")
    theme: str = Field("default", description="UI theme")
    
    # Domain classification
    domain_type: DomainType = Field(..., description="Domain type")
    category: Optional[str] = Field(None, description="Domain category")
    tags: List[str] = Field(default_factory=list, description="Domain tags")
    
    # Metadata
    author: Optional[str] = Field(None, description="Domain author")
    created_date: Optional[datetime] = Field(None, description="Creation date")
    license: Optional[str] = Field("MIT", description="License")
    homepage: Optional[str] = Field(None, description="Homepage URL")
    
    class Config:
        use_enum_values = True


class FeatureConfig(BaseModel):
    """Feature configuration."""
    name: StrictStr = Field(..., description="Feature name")
    enabled: bool = Field(True, description="Whether feature is enabled")
    description: Optional[str] = Field(None, description="Feature description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Feature parameters")


class DomainConfig(BaseModel):
    """Complete domain configuration."""
    domain: DomainMetadata = Field(..., description="Domain metadata")
    entities: Dict[str, EntityConfig] = Field(..., description="Domain entities")
    
    # Navigation structure
    navigation: Dict[str, List[NavigationItem]] = Field(
        default_factory=dict, 
        description="Navigation structure"
    )
    
    # Dashboard configuration
    dashboard: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dashboard configuration"
    )
    
    # Features and integrations
    features: Dict[str, FeatureConfig] = Field(
        default_factory=dict,
        description="Feature configuration"
    )
    
    # API configuration
    api: Dict[str, Any] = Field(
        default_factory=lambda: {
            "prefix": "/api/v1",
            "pagination": {"default_size": 20, "max_size": 100}
        },
        description="API configuration"
    )
    
    # Workflow configuration
    workflows: List[Dict[str, Any]] = Field(default_factory=list, description="Workflow definitions")
    
    # Integration configuration
    integrations: List[Dict[str, Any]] = Field(default_factory=list, description="External integrations")
    
    # Custom configuration
    custom_config: Dict[str, Any] = Field(default_factory=dict, description="Custom configuration")
    
    @field_validator('entities')
    @classmethod
    def validate_entity_relationships(cls, v):
        """Validate that all relationship targets exist."""
        entity_names = set(v.keys())
        
        for entity_name, entity in v.items():
            for relationship in entity.relationships:
                if relationship.target_entity not in entity_names:
                    raise ValueError(
                        f'Entity "{entity_name}" has relationship to non-existent entity "{relationship.target_entity}"'
                    )
        
        return v
    
    @model_validator(mode='after')
    def validate_configuration(self):
        """Perform cross-field validation."""
        domain = self.domain
        entities = self.entities
        
        # Validate that all entities have at least one field
        for entity_name, entity in entities.items():
            if not entity.fields:
                raise ValueError(f'Entity "{entity_name}" must have at least one field')
        
        # Validate navigation references to entities
        navigation = self.navigation
        entity_names = set(entities.keys())
        
        for nav_section, nav_items in navigation.items():
            for nav_item in nav_items:
                # Check if route references an entity
                route_parts = nav_item.route.strip('/').split('/')
                if len(route_parts) >= 2 and route_parts[0] == 'api' and route_parts[2] in entity_names:
                    # Valid entity reference
                    pass
        
        return self
    
    def get_entity_names(self) -> List[str]:
        """Get list of entity names."""
        return list(self.entities.keys())
    
    def get_entity(self, name: str) -> Optional[EntityConfig]:
        """Get entity configuration by name."""
        return self.entities.get(name)
    
    def get_primary_entity(self) -> Optional[EntityConfig]:
        """Get the primary entity (first one defined)."""
        if self.entities:
            return list(self.entities.values())[0]
        return None


class ConfigurationError(Exception):
    """Configuration error exception."""
    def __init__(self, message: str, field: Optional[str] = None, entity: Optional[str] = None):
        self.message = message
        self.field = field
        self.entity = entity
        super().__init__(self.message)


class DomainConfigLoader:
    """Enhanced domain configuration loader with validation."""
    
    def __init__(self, config_dir: Union[str, Path] = "domain_configs"):
        self.config_dir = Path(config_dir)
        self._loaded_configs: Dict[str, DomainConfig] = {}
        self._config_cache_time: Dict[str, float] = {}
    
    def load_domain_config(self, domain_name: str, force_reload: bool = False) -> Optional[DomainConfig]:
        """Load domain configuration from file with caching."""
        # Check cache first
        if not force_reload and domain_name in self._loaded_configs:
            config_file = self._find_config_file(domain_name)
            if config_file:
                file_mtime = config_file.stat().st_mtime
                cache_time = self._config_cache_time.get(domain_name, 0)
                
                # Return cached config if file hasn't changed
                if file_mtime <= cache_time:
                    return self._loaded_configs[domain_name]
        
        # Load from file
        config_file = self._find_config_file(domain_name)
        if not config_file:
            return None
        
        try:
            config_data = self._load_config_file(config_file)
            domain_config = self._parse_config_data(config_data, domain_name)
            
            # Cache the config
            self._loaded_configs[domain_name] = domain_config
            self._config_cache_time[domain_name] = datetime.now().timestamp()
            
            return domain_config
        
        except Exception as e:
            raise ConfigurationError(f"Error loading domain config {domain_name}: {e}")
    
    def _find_config_file(self, domain_name: str) -> Optional[Path]:
        """Find configuration file for domain."""
        # Try YAML first, then JSON
        for extension in ['.yaml', '.yml', '.json']:
            config_file = self.config_dir / f"{domain_name}{extension}"
            if config_file.exists():
                return config_file
        return None
    
    def _load_config_file(self, config_file: Path) -> Dict[str, Any]:
        """Load configuration file content."""
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                return json.load(f)
    
    def _parse_config_data(self, data: Dict[str, Any], domain_name: str) -> DomainConfig:
        """Parse configuration data into DomainConfig object."""
        try:
            # Ensure domain name matches file name
            if 'domain' in data and 'name' in data['domain']:
                data['domain']['name'] = domain_name
            
            return DomainConfig(**data)
        
        except ValueError as e:
            raise ConfigurationError(f"Invalid configuration format: {e}")
    
    def get_available_domains(self) -> List[str]:
        """Get list of available domain configurations."""
        if not self.config_dir.exists():
            return []
        
        domains = set()
        for pattern in ['*.yaml', '*.yml', '*.json']:
            for file_path in self.config_dir.glob(pattern):
                domains.add(file_path.stem)
        
        return sorted(list(domains))

    def load_all_domains(self) -> Dict[str, DomainConfig]:
        """Load all available domain configurations."""
        domains = {}
        available_domains = self.get_available_domains()
        
        for domain_name in available_domains:
            try:
                config = self.load_domain_config(domain_name)
                if config:
                    domains[domain_name] = config
            except Exception as e:
                print(f"Failed to load domain {domain_name}: {e}")
                continue
                
        return domains
    
    def validate_config(self, config: DomainConfig) -> List[str]:
        """Validate domain configuration and return list of errors."""
        errors = []
        
        try:
            # Pydantic validation already handles most cases
            # Additional custom validation can go here
            
            # Check for circular relationships
            errors.extend(self._check_circular_relationships(config))
            
            # Check for orphaned relationships
            errors.extend(self._check_orphaned_relationships(config))
            
            # Check navigation consistency
            errors.extend(self._check_navigation_consistency(config))
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return errors
    
    def _check_circular_relationships(self, config: DomainConfig) -> List[str]:
        """Check for circular relationships between entities."""
        errors = []
        # Implementation for circular relationship detection
        # This is a complex graph traversal problem
        return errors
    
    def _check_orphaned_relationships(self, config: DomainConfig) -> List[str]:
        """Check for relationships pointing to non-existent entities."""
        errors = []
        entity_names = set(config.entities.keys())
        
        for entity_name, entity in config.entities.items():
            for rel in entity.relationships:
                if rel.target_entity not in entity_names:
                    errors.append(
                        f"Entity '{entity_name}' has relationship '{rel.name}' "
                        f"pointing to non-existent entity '{rel.target_entity}'"
                    )
        
        return errors
    
    def _check_navigation_consistency(self, config: DomainConfig) -> List[str]:
        """Check navigation consistency with entities."""
        errors = []
        # Check that navigation routes are consistent with entities
        return errors
    
    def export_schema(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """Export domain configuration as JSON schema."""
        config = self.load_domain_config(domain_name)
        if not config:
            return None
        
        return config.dict()
    
    def compare_configs(self, domain1: str, domain2: str) -> Dict[str, Any]:
        """Compare two domain configurations."""
        config1 = self.load_domain_config(domain1)
        config2 = self.load_domain_config(domain2)
        
        if not config1 or not config2:
            return {"error": "One or both configurations not found"}
        
        # Simple comparison - can be enhanced
        return {
            "domain1": domain1,
            "domain2": domain2,
            "entities_count": {
                domain1: len(config1.entities),
                domain2: len(config2.entities)
            },
            "common_entities": list(
                set(config1.entities.keys()) & set(config2.entities.keys())
            ),
            "unique_entities": {
                domain1: list(set(config1.entities.keys()) - set(config2.entities.keys())),
                domain2: list(set(config2.entities.keys()) - set(config1.entities.keys()))
            }
        }


# Global enhanced config loader instance - use absolute path to domain configs
enhanced_config_loader = DomainConfigLoader("../domain_configs")