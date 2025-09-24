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
    IMAGE_GALLERY = "image_gallery"


class RelationType(str, Enum):
    """Available relationship types."""
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"


class ValidationConfig(BaseModel):
    """Field validation configuration."""
    rule: ValidationRule
    message: str = ""
    value: Optional[Any] = None

    @field_validator('rule')
    @classmethod
    def validate_rule(cls, v):
        if isinstance(v, str):
            try:
                return ValidationRule(v)
            except ValueError:
                # Allow unknown validation rules for extensibility
                return v
        return v


class SelectOption(BaseModel):
    """Select field option configuration."""
    value: str
    label: str
    disabled: Optional[bool] = False


class FieldConfig(BaseModel):
    """Enhanced field configuration."""
    name: str
    type: FieldType
    display_name: str
    description: Optional[str] = ""
    required: Optional[bool] = False
    unique: Optional[bool] = False
    searchable: Optional[bool] = False
    filterable: Optional[bool] = False
    sortable: Optional[bool] = False
    default_value: Optional[Any] = None
    ui_component: Optional[UIComponent] = None
    
    # Validation
    validations: List[ValidationConfig] = Field(default_factory=list)
    
    # UI-specific options
    options: List[SelectOption] = Field(default_factory=list)
    placeholder: Optional[str] = ""
    help_text: Optional[str] = ""
    
    # Advanced properties
    indexed: Optional[bool] = False
    encrypted: Optional[bool] = False
    audit_log: Optional[bool] = True

    @field_validator('ui_component')
    @classmethod
    def validate_ui_component(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return UIComponent(v)
            except ValueError:
                # Allow unknown UI components for extensibility
                return v
        return v


class RelationshipConfig(BaseModel):
    """Entity relationship configuration."""
    name: str
    target_entity: str
    type: RelationType
    display_name: str
    description: Optional[str] = ""
    foreign_key: Optional[str] = None
    through_entity: Optional[str] = None
    cascade_delete: Optional[bool] = False
    required: Optional[bool] = False


class IndexConfig(BaseModel):
    """Database index configuration."""
    name: str
    fields: List[str]
    unique: Optional[bool] = False
    partial: Optional[str] = None


class EntityConfig(BaseModel):
    """Enhanced entity configuration."""
    name: str
    table_name: Optional[str] = None
    display_name: str
    description: Optional[str] = ""
    
    # Fields and relationships
    fields: List[FieldConfig]
    relationships: List[RelationshipConfig] = Field(default_factory=list)
    
    # Database configuration
    indexes: List[IndexConfig] = Field(default_factory=list)
    
    # UI configuration
    list_display: List[str] = Field(default_factory=list)
    search_fields: List[str] = Field(default_factory=list)
    filter_fields: List[str] = Field(default_factory=list)
    default_sort_field: Optional[str] = None
    default_sort_order: Optional[str] = "asc"
    
    # Permissions
    permissions: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Multi-tenant support
    tenant_field: Optional[str] = None

    @field_validator('default_sort_field')
    @classmethod
    def validate_default_sort_field(cls, v, info):
        if v and 'fields' in info.data:
            field_names = [f.name for f in info.data['fields']]
            if v not in field_names and v != 'id':  # Allow 'id' as it's typically auto-added
                raise ValueError(f'default_sort_field "{v}" not found in entity fields')
        return v

    @model_validator(mode='after')
    def validate_entity_config(self):
        # Validate list_display fields exist
        field_names = [f.name for f in self.fields]
        for field_name in self.list_display:
            if field_name not in field_names:
                raise ValueError(f'list_display field "{field_name}" not found in entity fields')
        
        # Validate search_fields exist
        for field_name in self.search_fields:
            if field_name not in field_names:
                raise ValueError(f'search_fields field "{field_name}" not found in entity fields')
        
        return self


class BusinessRuleConfig(BaseModel):
    """Business rule configuration."""
    name: str
    description: str
    entity: Optional[str] = None
    condition: str
    action: str
    priority: Optional[int] = 1
    active: Optional[bool] = True


class NavigationConfig(BaseModel):
    """Navigation menu configuration."""
    key: str
    label: str
    icon: Optional[str] = None
    url: Optional[str] = None
    entity: Optional[str] = None
    children: List['NavigationConfig'] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    order: Optional[int] = 0

# Allow self-referencing
NavigationConfig.model_rebuild()


class DashboardWidgetConfig(BaseModel):
    """Dashboard widget configuration."""
    key: str
    type: str
    title: str
    entity: Optional[str] = None
    query: Optional[str] = None
    chart_type: Optional[str] = None
    size: Optional[str] = "medium"
    position: Dict[str, int] = Field(default_factory=dict)
    permissions: List[str] = Field(default_factory=list)


class FeatureConfig(BaseModel):
    """Feature configuration."""
    enabled: bool = True
    configuration: Dict[str, Any] = Field(default_factory=dict)


class DomainInfo(BaseModel):
    """Domain metadata."""
    name: str
    display_name: str
    description: str
    version: str = "1.0.0"
    domain_type: DomainType
    author: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DomainConfig(BaseModel):
    """Complete domain configuration."""
    domain: DomainInfo
    entities: Dict[str, EntityConfig]
    navigation: Dict[str, NavigationConfig] = Field(default_factory=dict)
    dashboard: List[DashboardWidgetConfig] = Field(default_factory=list)
    business_rules: List[BusinessRuleConfig] = Field(default_factory=list)
    features: Dict[str, FeatureConfig] = Field(default_factory=dict)

    @model_validator(mode='after')
    def validate_domain_config(self):
        """Validate domain configuration integrity."""
        entity_names = set(self.entities.keys())
        
        # Validate relationships reference existing entities
        for entity_name, entity in self.entities.items():
            for relationship in entity.relationships:
                if relationship.target_entity not in entity_names:
                    raise ValueError(f'Entity "{entity_name}" has relationship to non-existent entity "{relationship.target_entity}"')
        
        # Validate navigation entities exist
        for nav_key, nav_config in self.navigation.items():
            if nav_config.entity and nav_config.entity not in entity_names:
                raise ValueError(f'Navigation "{nav_key}" references non-existent entity "{nav_config.entity}"')
        
        # Validate dashboard widgets
        for widget in self.dashboard:
            if widget.entity and widget.entity not in entity_names:
                raise ValueError(f'Dashboard widget "{widget.key}" references non-existent entity "{widget.entity}"')
        
        return self


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
        """Check for circular relationship dependencies."""
        errors = []
        
        def has_circular_dependency(entity_name: str, target: str, visited: Set[str]) -> bool:
            if target == entity_name:
                return True
            if target in visited:
                return False
            
            visited.add(target)
            entity = config.entities.get(target)
            if entity:
                for rel in entity.relationships:
                    if has_circular_dependency(entity_name, rel.target_entity, visited):
                        return True
            return False
        
        for entity_name, entity in config.entities.items():
            for relationship in entity.relationships:
                if has_circular_dependency(entity_name, relationship.target_entity, set()):
                    errors.append(f"Circular relationship detected: {entity_name} -> {relationship.target_entity}")
        
        return errors
    
    def _check_orphaned_relationships(self, config: DomainConfig) -> List[str]:
        """Check for relationships to non-existent entities."""
        errors = []
        entity_names = set(config.entities.keys())
        
        for entity_name, entity in config.entities.items():
            for relationship in entity.relationships:
                if relationship.target_entity not in entity_names:
                    errors.append(f"Entity {entity_name} has relationship to non-existent entity: {relationship.target_entity}")
        
        return errors
    
    def _check_navigation_consistency(self, config: DomainConfig) -> List[str]:
        """Check navigation references to entities."""
        errors = []
        entity_names = set(config.entities.keys())
        
        for nav_key, nav_config in config.navigation.items():
            if nav_config.entity and nav_config.entity not in entity_names:
                errors.append(f"Navigation {nav_key} references non-existent entity: {nav_config.entity}")
        
        return errors


# Export configuration management utilities
class DomainConfigManager:
    """Advanced domain configuration management utilities."""
    
    def __init__(self, loader: DomainConfigLoader):
        self.loader = loader
    
    def compare_configs(self, config1: DomainConfig, config2: DomainConfig) -> Dict[str, Any]:
        """Compare two domain configurations."""
        differences = {
            "entities": {
                "added": [],
                "removed": [],
                "modified": []
            },
            "fields": {
                "added": [],
                "removed": [],
                "modified": []
            },
            "relationships": {
                "added": [],
                "removed": [],
                "modified": []
            }
        }
        
        # Compare entities
        entities1 = set(config1.entities.keys())
        entities2 = set(config2.entities.keys())
        
        differences["entities"]["added"] = list(entities2 - entities1)
        differences["entities"]["removed"] = list(entities1 - entities2)
        
        # Compare common entities
        common_entities = entities1 & entities2
        for entity_name in common_entities:
            entity1 = config1.entities[entity_name]
            entity2 = config2.entities[entity_name]
            
            # Compare fields
            fields1 = {f.name: f for f in entity1.fields}
            fields2 = {f.name: f for f in entity2.fields}
            
            field_names1 = set(fields1.keys())
            field_names2 = set(fields2.keys())
            
            for field_name in field_names2 - field_names1:
                differences["fields"]["added"].append(f"{entity_name}.{field_name}")
            
            for field_name in field_names1 - field_names2:
                differences["fields"]["removed"].append(f"{entity_name}.{field_name}")
            
            # Check for field modifications
            for field_name in field_names1 & field_names2:
                if fields1[field_name].dict() != fields2[field_name].dict():
                    differences["fields"]["modified"].append(f"{entity_name}.{field_name}")
        
        return differences
    
    def generate_schema_export(self, config: DomainConfig) -> Dict[str, Any]:
        """Generate exportable schema from domain configuration."""
        return {
            "domain": config.domain.dict(),
            "entities": {name: entity.dict() for name, entity in config.entities.items()},
            "navigation": {name: nav.dict() for name, nav in config.navigation.items()},
            "dashboard": [widget.dict() for widget in config.dashboard],
            "business_rules": [rule.dict() for rule in config.business_rules],
            "features": {name: feature.dict() for name, feature in config.features.items()}
        }


# Global loader instance
_default_loader = None

def get_domain_loader(config_dir: Union[str, Path] = "domain_configs") -> DomainConfigLoader:
    """Get default domain configuration loader."""
    global _default_loader
    if _default_loader is None or _default_loader.config_dir != Path(config_dir):
        _default_loader = DomainConfigLoader(config_dir)
    return _default_loader