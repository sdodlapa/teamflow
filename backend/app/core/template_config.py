"""Template configuration system for domain-driven applications."""

import os
import yaml
import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class DomainType(Enum):
    """Supported domain types for template system."""
    TASK_MANAGEMENT = "task_management"
    PROPERTY_MANAGEMENT = "property_management"
    E_COMMERCE = "e_commerce"
    HEALTHCARE = "healthcare"
    RESTAURANT = "restaurant"
    EDUCATION = "education"
    FINANCE = "finance"
    CUSTOM = "custom"


@dataclass
class EntityField:
    """Configuration for an entity field."""
    name: str
    type: str
    nullable: bool = True
    default: Optional[Any] = None
    max_length: Optional[int] = None
    choices: Optional[List[str]] = None
    indexed: bool = False
    unique: bool = False
    description: Optional[str] = None


@dataclass
class EntityRelationship:
    """Configuration for entity relationships."""
    name: str
    target_entity: str
    relationship_type: str  # one_to_many, many_to_one, many_to_many
    foreign_key: Optional[str] = None
    back_populates: Optional[str] = None
    cascade: Optional[str] = None


@dataclass
class EntityDefinition:
    """Complete entity definition for domain."""
    name: str
    table_name: str
    description: str
    fields: List[EntityField] = field(default_factory=list)
    relationships: List[EntityRelationship] = field(default_factory=list)
    business_rules: List[Dict[str, Any]] = field(default_factory=list)
    ui_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NavigationItem:
    """Navigation menu item configuration."""
    key: str
    label: str
    icon: str
    route: str
    order: int = 0
    permissions: List[str] = field(default_factory=list)


@dataclass
class DomainConfig:
    """Complete domain configuration for template system."""
    name: str
    title: str
    description: str
    domain_type: DomainType
    version: str = "1.0.0"
    
    # Branding
    logo: str = "🏢"
    color_scheme: str = "blue"
    theme: str = "default"
    
    # Entities
    entities: List[EntityDefinition] = field(default_factory=list)
    
    # Navigation
    navigation: List[NavigationItem] = field(default_factory=list)
    
    # Features
    features: Dict[str, bool] = field(default_factory=dict)
    
    # Custom configuration
    custom_config: Dict[str, Any] = field(default_factory=dict)


class TemplateConfigLoader:
    """Loads and validates domain configurations."""
    
    def __init__(self, config_dir: str = "domain_configs"):
        self.config_dir = Path(config_dir)
        self._loaded_configs: Dict[str, DomainConfig] = {}
    
    def load_domain_config(self, domain_name: str) -> Optional[DomainConfig]:
        """Load domain configuration from file."""
        if domain_name in self._loaded_configs:
            return self._loaded_configs[domain_name]
        
        config_file = self.config_dir / f"{domain_name}.yaml"
        if not config_file.exists():
            config_file = self.config_dir / f"{domain_name}.json"
        
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, 'r') as f:
                if config_file.suffix == '.yaml':
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            domain_config = self._parse_config_data(config_data)
            self._loaded_configs[domain_name] = domain_config
            return domain_config
        
        except Exception as e:
            print(f"Error loading domain config {domain_name}: {e}")
            return None
    
    def _parse_config_data(self, data: Dict[str, Any]) -> DomainConfig:
        """Parse configuration data into DomainConfig object."""
        domain_info = data.get('domain', {})
        
        # Parse entities
        entities = []
        for entity_data in data.get('entities', []):
            fields = [
                EntityField(**field_data) 
                for field_data in entity_data.get('fields', [])
            ]
            
            relationships = [
                EntityRelationship(**rel_data)
                for rel_data in entity_data.get('relationships', [])
            ]
            
            entity = EntityDefinition(
                name=entity_data['name'],
                table_name=entity_data.get('table_name', entity_data['name'].lower()),
                description=entity_data.get('description', ''),
                fields=fields,
                relationships=relationships,
                business_rules=entity_data.get('business_rules', []),
                ui_config=entity_data.get('ui_config', {})
            )
            entities.append(entity)
        
        # Parse navigation
        navigation = []
        for nav_data in data.get('navigation', []):
            nav_item = NavigationItem(**nav_data)
            navigation.append(nav_item)
        
        return DomainConfig(
            name=domain_info.get('name', 'unknown'),
            title=domain_info.get('title', 'Unknown Domain'),
            description=domain_info.get('description', ''),
            domain_type=DomainType(domain_info.get('type', 'custom')),
            version=domain_info.get('version', '1.0.0'),
            logo=domain_info.get('logo', '🏢'),
            color_scheme=domain_info.get('color_scheme', 'blue'),
            theme=domain_info.get('theme', 'default'),
            entities=entities,
            navigation=navigation,
            features=data.get('features', {}),
            custom_config=data.get('custom_config', {})
        )
    
    def get_available_domains(self) -> List[str]:
        """Get list of available domain configurations."""
        if not self.config_dir.exists():
            return []
        
        domains = []
        for file_path in self.config_dir.glob("*.yaml"):
            domains.append(file_path.stem)
        for file_path in self.config_dir.glob("*.json"):
            if f"{file_path.stem}.yaml" not in [f.name for f in self.config_dir.glob("*.yaml")]:
                domains.append(file_path.stem)
        
        return sorted(domains)
    
    def validate_config(self, config: DomainConfig) -> List[str]:
        """Validate domain configuration and return list of errors."""
        errors = []
        
        # Validate basic fields
        if not config.name:
            errors.append("Domain name is required")
        if not config.title:
            errors.append("Domain title is required")
        
        # Validate entities
        entity_names = set()
        for entity in config.entities:
            if not entity.name:
                errors.append("Entity name is required")
            elif entity.name in entity_names:
                errors.append(f"Duplicate entity name: {entity.name}")
            else:
                entity_names.add(entity.name)
            
            # Validate fields
            field_names = set()
            for field in entity.fields:
                if not field.name:
                    errors.append(f"Field name is required in entity {entity.name}")
                elif field.name in field_names:
                    errors.append(f"Duplicate field name {field.name} in entity {entity.name}")
                else:
                    field_names.add(field.name)
        
        return errors


# Global template config loader instance
template_config_loader = TemplateConfigLoader()


def get_domain_config(domain_name: str) -> Optional[DomainConfig]:
    """Get domain configuration by name."""
    return template_config_loader.load_domain_config(domain_name)


def get_available_domains() -> List[str]:
    """Get list of available domain configurations."""
    return template_config_loader.get_available_domains()