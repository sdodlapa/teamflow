#!/usr/bin/env python3
"""
TeamFlow Universal Framework - Plugin System Implementation

This module provides the foundation for runtime plugin registration,
dynamic model creation, and hot-swappable domain modules.
"""

import asyncio
import importlib
import inspect
import json
import yaml
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from fastapi import APIRouter
from pydantic import BaseModel

# Framework Core Types
Base = declarative_base()


class FieldType(Enum):
    """Available field types for dynamic models."""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    TEXT = "text"
    DATETIME = "datetime"
    FOREIGN_KEY = "foreign_key"
    DECIMAL = "decimal"
    JSON = "json"
    ENUM = "enum"


@dataclass
class FieldSpec:
    """Specification for a model field."""
    name: str
    type: FieldType
    nullable: bool = True
    indexed: bool = False
    unique: bool = False
    default: Any = None
    max_length: Optional[int] = None
    foreign_table: Optional[str] = None
    enum_values: Optional[List[str]] = None
    description: str = ""

    def to_sqlalchemy_column(self):
        """Convert field spec to SQLAlchemy column."""
        column_args = []
        column_kwargs = {
            'nullable': self.nullable,
            'index': self.indexed,
            'unique': self.unique
        }
        
        if self.default is not None:
            column_kwargs['default'] = self.default

        if self.type == FieldType.STRING:
            length = self.max_length or 255
            column_type = String(length)
        elif self.type == FieldType.INTEGER:
            column_type = Integer
        elif self.type == FieldType.BOOLEAN:
            column_type = Boolean
        elif self.type == FieldType.TEXT:
            column_type = Text
        elif self.type == FieldType.DATETIME:
            column_type = DateTime
        elif self.type == FieldType.FOREIGN_KEY:
            column_type = Integer
            if self.foreign_table:
                column_args.append(ForeignKey(f"{self.foreign_table}.id"))
        else:
            column_type = String(255)  # Default fallback

        return Column(column_type, *column_args, **column_kwargs)


@dataclass
class RelationshipSpec:
    """Specification for model relationships."""
    name: str
    target_model: str
    relationship_type: str  # "one_to_many", "many_to_one", "many_to_many"
    back_populates: Optional[str] = None
    cascade: str = "all, delete-orphan"

    def to_sqlalchemy_relationship(self):
        """Convert relationship spec to SQLAlchemy relationship."""
        return relationship(
            self.target_model,
            back_populates=self.back_populates,
            cascade=self.cascade if self.relationship_type == "one_to_many" else None
        )


@dataclass
class ModelSpec:
    """Complete specification for a domain model."""
    name: str
    table_name: str
    description: str = ""
    fields: List[FieldSpec] = field(default_factory=list)
    relationships: List[RelationshipSpec] = field(default_factory=list)
    indexes: List[List[str]] = field(default_factory=list)
    constraints: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class WorkflowStep:
    """Specification for a workflow step."""
    name: str
    type: str  # "action", "condition", "notification", "integration"
    config: Dict[str, Any] = field(default_factory=dict)
    next_steps: List[str] = field(default_factory=list)


@dataclass
class WorkflowSpec:
    """Complete workflow specification."""
    name: str
    description: str
    trigger_type: str  # "event", "scheduled", "manual"
    trigger_config: Dict[str, Any] = field(default_factory=dict)
    steps: List[WorkflowStep] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)


@dataclass
class APIEndpointSpec:
    """Specification for API endpoints."""
    path: str
    methods: List[str]
    description: str
    permissions: List[str] = field(default_factory=list)
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    response_model: Optional[str] = None


@dataclass
class UIComponentSpec:
    """Specification for UI components."""
    name: str
    type: str  # "dashboard", "table", "form", "chart"
    props: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class DomainSpec:
    """Complete domain specification."""
    name: str
    description: str
    version: str = "1.0.0"
    models: List[ModelSpec] = field(default_factory=list)
    workflows: List[WorkflowSpec] = field(default_factory=list)
    api_endpoints: List[APIEndpointSpec] = field(default_factory=list)
    ui_components: List[UIComponentSpec] = field(default_factory=list)
    integrations: Dict[str, Any] = field(default_factory=dict)
    business_rules: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


class DomainPlugin(ABC):
    """Abstract base class for domain plugins."""
    
    name: str
    version: str
    description: str
    dependencies: List[str] = []
    
    @abstractmethod
    def get_domain_spec(self) -> DomainSpec:
        """Return the complete domain specification."""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> bool:
        """Cleanup plugin resources. Return True if successful."""
        pass
    
    def validate_dependencies(self, available_plugins: List[str]) -> bool:
        """Check if all dependencies are available."""
        return all(dep in available_plugins for dep in self.dependencies)


class ModelFactory:
    """Factory for creating SQLAlchemy models dynamically."""
    
    def __init__(self, base_model_class=None):
        self.base_model_class = base_model_class or Base
        self.created_models: Dict[str, Type] = {}
    
    def create_model(self, spec: ModelSpec) -> Type:
        """Create a SQLAlchemy model from specification."""
        
        if spec.name in self.created_models:
            return self.created_models[spec.name]
        
        # Build model attributes
        attributes = {
            '__tablename__': spec.table_name,
            '__module__': 'teamflow.dynamic_models',
            '__doc__': spec.description
        }
        
        # Add ID field (all models need primary key)
        attributes['id'] = Column(Integer, primary_key=True, index=True)
        
        # Add fields from specification
        for field_spec in spec.fields:
            attributes[field_spec.name] = field_spec.to_sqlalchemy_column()
        
        # Add relationships (will be resolved after all models are created)
        for rel_spec in spec.relationships:
            # Store relationship spec for later resolution
            if not hasattr(attributes, '_pending_relationships'):
                attributes['_pending_relationships'] = []
            attributes['_pending_relationships'].append(rel_spec)
        
        # Create the model class
        model_class = type(spec.name, (self.base_model_class,), attributes)
        
        # Store created model
        self.created_models[spec.name] = model_class
        
        return model_class
    
    def resolve_relationships(self):
        """Resolve all pending relationships after all models are created."""
        for model_name, model_class in self.created_models.items():
            if hasattr(model_class, '_pending_relationships'):
                for rel_spec in model_class._pending_relationships:
                    if rel_spec.target_model in self.created_models:
                        setattr(
                            model_class,
                            rel_spec.name,
                            rel_spec.to_sqlalchemy_relationship()
                        )
                
                # Clean up pending relationships
                delattr(model_class, '_pending_relationships')


class ConfigParser:
    """Parser for YAML/JSON domain configurations."""
    
    @staticmethod
    def parse_file(file_path: Path) -> DomainSpec:
        """Parse domain configuration from file."""
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        # Load configuration
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                config = yaml.safe_load(f)
            elif file_path.suffix.lower() == '.json':
                config = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        return ConfigParser._parse_domain_config(config)
    
    @staticmethod
    def _parse_domain_config(config: Dict[str, Any]) -> DomainSpec:
        """Parse domain configuration dictionary."""
        
        domain_config = config.get('domain', {})
        
        # Parse models
        models = []
        for entity_config in config.get('entities', []):
            model_spec = ConfigParser._parse_model_config(entity_config)
            models.append(model_spec)
        
        # Parse workflows
        workflows = []
        for workflow_config in config.get('workflows', []):
            workflow_spec = ConfigParser._parse_workflow_config(workflow_config)
            workflows.append(workflow_spec)
        
        # Parse API endpoints
        api_endpoints = []
        for endpoint_config in config.get('api_endpoints', []):
            endpoint_spec = ConfigParser._parse_endpoint_config(endpoint_config)
            api_endpoints.append(endpoint_spec)
        
        # Parse UI components
        ui_components = []
        for component_config in config.get('ui_components', []):
            component_spec = ConfigParser._parse_component_config(component_config)
            ui_components.append(component_spec)
        
        return DomainSpec(
            name=domain_config.get('name', 'Unknown Domain'),
            description=domain_config.get('description', ''),
            version=domain_config.get('version', '1.0.0'),
            models=models,
            workflows=workflows,
            api_endpoints=api_endpoints,
            ui_components=ui_components,
            integrations=config.get('integrations', {}),
            business_rules=config.get('business_rules', []),
            dependencies=config.get('dependencies', [])
        )
    
    @staticmethod
    def _parse_model_config(entity_config: Dict[str, Any]) -> ModelSpec:
        """Parse model configuration."""
        
        name = entity_config.get('name', 'UnknownModel')
        table_name = entity_config.get('table', f"{name.lower()}s")
        
        # Parse fields
        fields = []
        for field_name, field_config in entity_config.get('fields', {}).items():
            if isinstance(field_config, str):
                # Simple field: "name: string"
                field_type = FieldType(field_config)
                field_spec = FieldSpec(name=field_name, type=field_type)
            else:
                # Complex field definition
                field_type = FieldType(field_config.get('type', 'string'))
                field_spec = FieldSpec(
                    name=field_name,
                    type=field_type,
                    nullable=field_config.get('nullable', True),
                    indexed=field_config.get('indexed', False),
                    unique=field_config.get('unique', False),
                    default=field_config.get('default'),
                    max_length=field_config.get('max_length'),
                    foreign_table=field_config.get('references'),
                    enum_values=field_config.get('values'),
                    description=field_config.get('description', '')
                )
            fields.append(field_spec)
        
        return ModelSpec(
            name=name,
            table_name=table_name,
            description=entity_config.get('description', ''),
            fields=fields,
            relationships=[],  # TODO: Parse relationships
            indexes=entity_config.get('indexes', []),
            constraints=entity_config.get('constraints', [])
        )
    
    @staticmethod
    def _parse_workflow_config(workflow_config: Dict[str, Any]) -> WorkflowSpec:
        """Parse workflow configuration."""
        
        # Parse workflow steps
        steps = []
        for step_config in workflow_config.get('steps', []):
            if isinstance(step_config, str):
                # Simple step: just name
                step = WorkflowStep(name=step_config, type='action')
            else:
                step = WorkflowStep(
                    name=step_config.get('name', 'unknown_step'),
                    type=step_config.get('type', 'action'),
                    config=step_config.get('config', {}),
                    next_steps=step_config.get('next_steps', [])
                )
            steps.append(step)
        
        return WorkflowSpec(
            name=workflow_config.get('name', 'Unknown Workflow'),
            description=workflow_config.get('description', ''),
            trigger_type=workflow_config.get('trigger', 'manual'),
            trigger_config=workflow_config.get('trigger_config', {}),
            steps=steps,
            permissions=workflow_config.get('permissions', [])
        )
    
    @staticmethod
    def _parse_endpoint_config(endpoint_config: Dict[str, Any]) -> APIEndpointSpec:
        """Parse API endpoint configuration."""
        
        return APIEndpointSpec(
            path=endpoint_config.get('path', '/unknown'),
            methods=endpoint_config.get('methods', ['GET']),
            description=endpoint_config.get('description', ''),
            permissions=endpoint_config.get('permissions', []),
            parameters=endpoint_config.get('parameters', []),
            response_model=endpoint_config.get('response_model')
        )
    
    @staticmethod
    def _parse_component_config(component_config: Dict[str, Any]) -> UIComponentSpec:
        """Parse UI component configuration."""
        
        return UIComponentSpec(
            name=component_config.get('name', 'UnknownComponent'),
            type=component_config.get('type', 'component'),
            props=component_config.get('props', {}),
            dependencies=component_config.get('dependencies', [])
        )


class PluginRegistry:
    """Registry for managing domain plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, DomainPlugin] = {}
        self.active_domains: Dict[str, DomainSpec] = {}
        self.model_factory = ModelFactory()
    
    def register_plugin(self, plugin_id: str, plugin: DomainPlugin):
        """Register a new plugin."""
        
        # Validate plugin
        if not plugin.validate_dependencies(list(self.plugins.keys())):
            missing_deps = set(plugin.dependencies) - set(self.plugins.keys())
            raise ValueError(f"Missing dependencies for plugin {plugin_id}: {missing_deps}")
        
        self.plugins[plugin_id] = plugin
        print(f"✅ Plugin registered: {plugin_id}")
    
    async def activate_plugin(self, plugin_id: str) -> bool:
        """Activate a registered plugin."""
        
        if plugin_id not in self.plugins:
            raise ValueError(f"Plugin not found: {plugin_id}")
        
        plugin = self.plugins[plugin_id]
        
        try:
            # Initialize plugin
            if not await plugin.initialize():
                raise RuntimeError(f"Plugin initialization failed: {plugin_id}")
            
            # Get domain specification
            domain_spec = plugin.get_domain_spec()
            
            # Create database models
            self._create_domain_models(domain_spec)
            
            # Register domain
            self.active_domains[plugin_id] = domain_spec
            
            print(f"🚀 Plugin activated: {plugin_id}")
            return True
            
        except Exception as e:
            print(f"❌ Plugin activation failed: {plugin_id} - {e}")
            return False
    
    async def deactivate_plugin(self, plugin_id: str) -> bool:
        """Deactivate an active plugin."""
        
        if plugin_id not in self.active_domains:
            raise ValueError(f"Plugin not active: {plugin_id}")
        
        plugin = self.plugins[plugin_id]
        
        try:
            # Cleanup plugin resources
            if not await plugin.cleanup():
                print(f"⚠️ Plugin cleanup had issues: {plugin_id}")
            
            # Remove from active domains
            del self.active_domains[plugin_id]
            
            print(f"🔄 Plugin deactivated: {plugin_id}")
            return True
            
        except Exception as e:
            print(f"❌ Plugin deactivation failed: {plugin_id} - {e}")
            return False
    
    def load_domain_from_config(self, config_path: Path, plugin_id: str):
        """Load domain from configuration file."""
        
        domain_spec = ConfigParser.parse_file(config_path)
        
        # Create a configuration-based plugin
        class ConfigPlugin(DomainPlugin):
            name = domain_spec.name
            version = domain_spec.version
            description = domain_spec.description
            dependencies = domain_spec.dependencies
            
            def get_domain_spec(self) -> DomainSpec:
                return domain_spec
            
            async def initialize(self) -> bool:
                return True
            
            async def cleanup(self) -> bool:
                return True
        
        # Register and activate
        self.register_plugin(plugin_id, ConfigPlugin())
        return plugin_id
    
    def _create_domain_models(self, domain_spec: DomainSpec):
        """Create SQLAlchemy models for domain."""
        
        # Create models
        for model_spec in domain_spec.models:
            self.model_factory.create_model(model_spec)
        
        # Resolve relationships
        self.model_factory.resolve_relationships()
    
    def get_active_domains(self) -> List[str]:
        """Get list of active domain IDs."""
        return list(self.active_domains.keys())
    
    def get_domain_spec(self, plugin_id: str) -> Optional[DomainSpec]:
        """Get domain specification for active plugin."""
        return self.active_domains.get(plugin_id)


# Global plugin registry instance
plugin_registry = PluginRegistry()


# Example Stock Portfolio Plugin Implementation
class StockPortfolioPlugin(DomainPlugin):
    """Stock portfolio management plugin."""
    
    name = "Stock Portfolio Management"
    version = "1.0.0"
    description = "Complete investment portfolio tracking and analysis"
    dependencies = []
    
    def get_domain_spec(self) -> DomainSpec:
        """Return stock portfolio domain specification."""
        
        return DomainSpec(
            name=self.name,
            description=self.description,
            version=self.version,
            models=[
                ModelSpec(
                    name="Portfolio",
                    table_name="portfolios",
                    description="Investment portfolio",
                    fields=[
                        FieldSpec("name", FieldType.STRING, nullable=False, indexed=True),
                        FieldSpec("total_value", FieldType.DECIMAL, default=0.00),
                        FieldSpec("risk_tolerance", FieldType.STRING, indexed=True),
                        FieldSpec("auto_rebalance", FieldType.BOOLEAN, default=False),
                        FieldSpec("created_at", FieldType.DATETIME),
                        FieldSpec("updated_at", FieldType.DATETIME)
                    ]
                ),
                ModelSpec(
                    name="Stock",
                    table_name="stocks",
                    description="Stock information",
                    fields=[
                        FieldSpec("symbol", FieldType.STRING, nullable=False, unique=True, max_length=10),
                        FieldSpec("company_name", FieldType.STRING, nullable=False),
                        FieldSpec("sector", FieldType.STRING, indexed=True),
                        FieldSpec("current_price", FieldType.DECIMAL),
                        FieldSpec("market_cap", FieldType.INTEGER)
                    ]
                ),
                ModelSpec(
                    name="Holding",
                    table_name="holdings",
                    description="Portfolio holdings",
                    fields=[
                        FieldSpec("portfolio_id", FieldType.FOREIGN_KEY, foreign_table="portfolios", nullable=False),
                        FieldSpec("stock_id", FieldType.FOREIGN_KEY, foreign_table="stocks", nullable=False),
                        FieldSpec("shares", FieldType.DECIMAL, nullable=False),
                        FieldSpec("average_cost", FieldType.DECIMAL, nullable=False),
                        FieldSpec("purchase_date", FieldType.DATETIME, nullable=False)
                    ]
                )
            ],
            workflows=[
                WorkflowSpec(
                    name="Portfolio Rebalancing",
                    description="Automated portfolio rebalancing",
                    trigger_type="scheduled",
                    trigger_config={"schedule": "0 9 * * 1"},  # Monday 9 AM
                    steps=[
                        WorkflowStep("analyze_allocations", "condition", {"check": "deviation > threshold"}),
                        WorkflowStep("generate_trades", "action", {"calculate_trades": True}),
                        WorkflowStep("execute_trades", "integration", {"broker_api": "alpaca"})
                    ],
                    permissions=["portfolio_manager"]
                )
            ],
            api_endpoints=[
                APIEndpointSpec("/portfolios", ["GET", "POST"], "Manage portfolios", ["portfolio_owner"]),
                APIEndpointSpec("/portfolios/{id}/performance", ["GET"], "Portfolio performance", ["portfolio_viewer"]),
                APIEndpointSpec("/stocks/search", ["GET"], "Search stocks", ["public"])
            ],
            ui_components=[
                UIComponentSpec("PortfolioDashboard", "dashboard", 
                              {"charts": ["allocation_pie", "performance_line"], "refresh_interval": 30000}),
                UIComponentSpec("StockSearchWidget", "autocomplete", 
                              {"placeholder": "Search stocks...", "min_chars": 2})
            ],
            integrations={
                "alpaca_trading": {"type": "broker_api", "base_url": "https://paper-api.alpaca.markets"},
                "alpha_vantage": {"type": "market_data", "base_url": "https://www.alphavantage.co"}
            }
        )
    
    async def initialize(self) -> bool:
        """Initialize stock portfolio plugin."""
        print(f"🚀 Initializing {self.name}...")
        
        # Setup integrations
        # Initialize database tables
        # Register API endpoints
        # Load initial data
        
        return True
    
    async def cleanup(self) -> bool:
        """Cleanup stock portfolio plugin."""
        print(f"🧹 Cleaning up {self.name}...")
        
        # Cleanup integrations
        # Remove API endpoints
        # Clear caches
        
        return True


# Demo usage
async def demo_plugin_system():
    """Demonstrate the plugin system."""
    
    print("🎯 TeamFlow Universal Framework - Plugin System Demo")
    print("=" * 60)
    
    # Register stock portfolio plugin
    plugin_registry.register_plugin("stock_portfolio", StockPortfolioPlugin())
    
    # Activate plugin
    success = await plugin_registry.activate_plugin("stock_portfolio")
    if success:
        print(f"✅ Stock Portfolio domain is now active!")
        
        # Show active domains
        active = plugin_registry.get_active_domains()
        print(f"📊 Active domains: {active}")
        
        # Get domain specification
        spec = plugin_registry.get_domain_spec("stock_portfolio")
        print(f"📋 Domain has {len(spec.models)} models, {len(spec.workflows)} workflows")
    
    # Load domain from configuration file
    print("\n🔧 Loading domain from configuration...")
    
    # Create sample config file
    config_path = Path("domains/education.yaml")
    config_path.parent.mkdir(exist_ok=True)
    
    sample_config = {
        "domain": {
            "name": "Learning Management System",
            "description": "Complete LMS platform",
            "version": "1.0.0"
        },
        "entities": [
            {
                "name": "Course",
                "table": "courses",
                "description": "Educational courses",
                "fields": {
                    "title": {"type": "string", "nullable": False, "indexed": True},
                    "description": {"type": "text"},
                    "instructor_id": {"type": "foreign_key", "references": "users.id"},
                    "duration": {"type": "integer"},
                    "price": {"type": "integer", "description": "Price in cents"}
                }
            },
            {
                "name": "Enrollment",
                "table": "enrollments", 
                "description": "Student course enrollments",
                "fields": {
                    "student_id": {"type": "foreign_key", "references": "users.id", "nullable": False},
                    "course_id": {"type": "foreign_key", "references": "courses.id", "nullable": False},
                    "enrollment_date": {"type": "datetime", "nullable": False},
                    "progress": {"type": "integer", "default": 0},
                    "completed": {"type": "boolean", "default": False}
                }
            }
        ],
        "workflows": [
            {
                "name": "Course Completion",
                "description": "Handle course completion",
                "trigger": "event",
                "trigger_config": {"event": "progress_100_percent"},
                "steps": [
                    {"name": "generate_certificate", "type": "action", "config": {"template": "completion_cert"}},
                    {"name": "send_notification", "type": "notification", "config": {"recipients": ["student", "instructor"]}}
                ],
                "permissions": ["system"]
            }
        ],
        "api_endpoints": [
            {
                "path": "/courses",
                "methods": ["GET", "POST"],
                "description": "Manage courses",
                "permissions": ["instructor", "admin"]
            },
            {
                "path": "/enrollments",
                "methods": ["GET", "POST"],
                "description": "Manage enrollments", 
                "permissions": ["student", "instructor", "admin"]
            }
        ],
        "ui_components": [
            {
                "name": "CourseCatalog",
                "type": "grid",
                "props": {"columns": 3, "pagination": True}
            },
            {
                "name": "StudentDashboard", 
                "type": "dashboard",
                "props": {"widgets": ["enrolled_courses", "progress_chart", "assignments"]}
            }
        ]
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(sample_config, f, default_flow_style=False)
    
    # Load the configuration-based domain
    education_id = plugin_registry.load_domain_from_config(config_path, "education")
    await plugin_registry.activate_plugin(education_id)
    
    print(f"✅ Education domain loaded and activated!")
    
    # Show all active domains
    active_domains = plugin_registry.get_active_domains()
    print(f"\n🎯 Final active domains: {active_domains}")
    
    for domain_id in active_domains:
        spec = plugin_registry.get_domain_spec(domain_id)
        print(f"   📚 {spec.name}: {len(spec.models)} models, {len(spec.api_endpoints)} endpoints")


if __name__ == "__main__":
    asyncio.run(demo_plugin_system())