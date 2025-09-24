# 🏗️ PHASE 2: TEMPLATE EXTRACTION & ENGINE DESIGN
## TeamFlow Universal Template System Architecture

**Date**: September 2025  
**Version**: 2.0  
**Purpose**: Detailed technical specification for template extraction engine and universal framework design

---

## 🎯 EXECUTIVE SUMMARY

**Phase 2 Objective**: Transform TeamFlow from a task management system into a **universal business application template engine** that can generate complete, production-ready applications for any domain in minutes.

**Key Deliverables**:
- 🏗️ **Template Extraction Engine** - Automated extraction of reusable patterns
- 🔧 **Configuration System** - YAML/JSON-driven domain configuration
- 🤖 **Code Generation Engine** - Automated creation of domain-specific applications
- 📚 **Adaptation Manual System** - Step-by-step transformation guides
- 🧪 **Domain Validation** - Multi-domain proof of concept

---

## 🏛️ TEMPLATE ARCHITECTURE DESIGN

### **1. Core Template Hierarchy**

```
TeamFlow Universal Template System
├── 🟦 UNIVERSAL CORE (Never Changes)
│   ├── Authentication System (JWT, RBAC, Security)
│   ├── Multi-tenant Architecture (Organizations, Users)  
│   ├── Database Layer (AsyncSession, Connection Pooling)
│   ├── Middleware Stack (Security, Performance, Monitoring)
│   └── Base Models (BaseModel, UUID, Timestamps)
│
├── 🟨 CONFIGURABLE LAYER (Domain-Driven)
│   ├── Entity Models (Configurable Fields, Relations)
│   ├── API Routes (CRUD Operations, Business Logic)
│   ├── Schema Definitions (Validation, Serialization)
│   ├── UI Components (Dashboard, Forms, Lists)
│   └── Navigation Structure (Menus, Views, Workflows)
│
└── 🟩 DOMAIN EXTENSIONS (Custom Features)
    ├── Business Rules (Domain-Specific Logic)
    ├── Custom Fields (Specialized Data Types)
    ├── Integrations (External APIs, Services)
    └── Custom UI (Domain-Specific Components)
```

### **2. Template Extraction Strategy**

#### **Universal Core Components (Copy As-Is)**
```python
# These components work for ANY domain without modification:

# 1. Authentication & Security (backend/app/core/)
- security.py                 # JWT, password hashing
- security_middleware.py      # Enterprise security headers, CORS, rate limiting
- dependencies.py             # Authentication dependencies

# 2. Database Infrastructure (backend/app/core/)  
- database.py                 # Async SQLAlchemy setup
- config.py                   # Environment configuration

# 3. Base Models (backend/app/models/)
- base.py                     # Universal BaseModel with UUID, timestamps

# 4. Middleware Stack (backend/app/middleware/)
- performance.py              # Response compression, metrics
- compression.py              # Smart compression algorithms

# 5. Core Services (backend/app/services/)
- security_service.py         # GDPR, audit logging, compliance
- performance_service.py      # Performance monitoring
- analytics_service.py        # Universal analytics engine (parameterized)
```

#### **Configurable Layer Components (Template Engine)**
```python
# These components are generated from domain configuration:

# 1. Domain Models (Generated from YAML)
class {EntityName}(BaseModel):
    # Universal fields (name, description, status) 
    # + Domain-specific fields from config
    # + Relationships based on domain hierarchy

# 2. Pydantic Schemas (Generated Pattern)  
class {EntityName}Base(BaseModel): # Shared fields
class {EntityName}Create({EntityName}Base): # Creation schema
class {EntityName}Read({EntityName}Base): # Response schema  
class {EntityName}Update(BaseModel): # Update schema
class {EntityName}List(BaseModel): # Paginated list

# 3. API Routes (Generated CRUD)
@router.post("/", response_model={EntityName}Read)
async def create_{entity_name}(data: {EntityName}Create):
    # Generated CRUD operations with domain-specific validation

# 4. UI Components (Generated from Templates)
const {EntityName}Dashboard = () => {
    // Domain-specific dashboard with configurable metrics
    // Generated based on entity relationships and workflows
}
```

---

## 🔧 CONFIGURATION SYSTEM DESIGN

### **Domain Configuration Schema**

#### **Primary Configuration File** (`domain-config.yaml`)
```yaml
# COMPLETE DOMAIN SPECIFICATION
domain:
  name: "real_estate"
  title: "PropertyFlow"
  description: "Real Estate Property Management System"
  logo: "🏠"
  color_scheme: "blue"

# PRIMARY BUSINESS ENTITIES
entities:
  property:
    display_name: "Property"
    fields:
      - name: "address"
        type: "string"
        required: true
        max_length: 500
      - name: "price"
        type: "decimal"
        required: true
        validation: "positive"
      - name: "bedrooms"
        type: "integer"
        default: 1
      - name: "bathrooms"
        type: "integer"  
      - name: "square_feet"
        type: "integer"
      - name: "property_type"
        type: "enum"
        options: ["house", "apartment", "condo", "townhouse"]
    
    relationships:
      - entity: "tenant"
        type: "one_to_many"
        description: "Property can have multiple tenants"
      - entity: "maintenance_request"
        type: "one_to_many"
        description: "Property can have multiple maintenance requests"
    
    business_rules:
      - name: "price_validation"
        condition: "price > 0"
        message: "Property price must be positive"
      - name: "auto_assign_manager"
        trigger: "property_created"
        action: "assign_to_default_manager"

  tenant:
    display_name: "Tenant"
    inherits_from: "user"  # Extends base User model
    fields:
      - name: "lease_start_date"
        type: "date"
        required: true
      - name: "lease_end_date" 
        type: "date"
        required: true
      - name: "rent_amount"
        type: "decimal"
        required: true
      - name: "deposit_amount"
        type: "decimal"
        default: 0
      - name: "emergency_contact"
        type: "string"
        max_length: 255
    
    relationships:
      - entity: "property"
        type: "many_to_one"
        foreign_key: "property_id"
        required: true
      - entity: "rent_payment"
        type: "one_to_many"

  maintenance_request:
    display_name: "Maintenance Request"
    fields:
      - name: "request_type"
        type: "enum"
        options: ["plumbing", "electrical", "hvac", "general", "emergency"]
        required: true
      - name: "urgency"
        type: "enum"  
        options: ["low", "medium", "high", "emergency"]
        default: "medium"
      - name: "scheduled_date"
        type: "datetime"
      - name: "completed_date"
        type: "datetime"
      - name: "contractor_notes"
        type: "text"
      - name: "cost"
        type: "decimal"
        default: 0
    
    relationships:
      - entity: "property"
        type: "many_to_one"
        foreign_key: "property_id"
        required: true
      - entity: "tenant"
        type: "many_to_one"
        foreign_key: "requested_by"
        required: true

# NAVIGATION & UI CONFIGURATION
navigation:
  primary_menu:
    - key: "dashboard"
      label: "Dashboard"
      icon: "📊"
      route: "/dashboard"
    - key: "properties"
      label: "Properties"
      icon: "🏠" 
      route: "/properties"
    - key: "tenants"
      label: "Tenants"
      icon: "👥"
      route: "/tenants"
    - key: "maintenance"
      label: "Maintenance"
      icon: "🔧"
      route: "/maintenance"

# DASHBOARD CONFIGURATION
dashboard:
  metrics:
    - name: "total_properties"
      label: "Total Properties"
      entity: "property"
      calculation: "count"
      icon: "🏠"
    - name: "occupied_properties"
      label: "Occupied Properties"
      entity: "property"
      calculation: "count_where"
      condition: "tenant_id IS NOT NULL"
      icon: "✅"
    - name: "pending_maintenance"
      label: "Pending Maintenance"
      entity: "maintenance_request"
      calculation: "count_where"
      condition: "status = 'open'"
      icon: "🔧"
    - name: "monthly_revenue"
      label: "Monthly Revenue"
      entity: "rent_payment"
      calculation: "sum"
      field: "amount"
      period: "current_month"
      icon: "💰"

  charts:
    - name: "occupancy_rate"
      type: "gauge"
      title: "Occupancy Rate"
      calculation: "percentage"
      numerator: "occupied_properties"
      denominator: "total_properties"
    - name: "maintenance_by_type"
      type: "pie"
      title: "Maintenance Requests by Type"
      entity: "maintenance_request"
      group_by: "request_type"

# WORKFLOW AUTOMATION
workflows:
  - name: "new_tenant_onboarding"
    trigger:
      event: "tenant_created"
    actions:
      - type: "send_email"
        template: "welcome_tenant"
        recipient: "{{tenant.email}}"
      - type: "create_task"
        title: "Setup tenant account"
        assigned_to: "property_manager"
      - type: "schedule_reminder"
        message: "Follow up with new tenant"
        delay: "3_days"

  - name: "maintenance_escalation"
    trigger:
      event: "maintenance_request_created"
      condition: "urgency = 'emergency'"
    actions:
      - type: "send_sms"
        recipient: "{{property.manager.phone}}"
        message: "Emergency maintenance required at {{property.address}}"
      - type: "update_priority"
        value: "urgent"
      - type: "assign_to"
        user: "emergency_contractor"

# API CONFIGURATION  
api:
  endpoints:
    - entity: "property"
      operations: ["create", "read", "update", "delete", "list"]
      permissions:
        create: ["admin", "property_manager"]
        read: ["admin", "property_manager", "tenant"]
        update: ["admin", "property_manager"]  
        delete: ["admin"]
    - entity: "tenant"
      operations: ["create", "read", "update", "list"]
      permissions:
        create: ["admin", "property_manager"]
        read: ["admin", "property_manager", "self"]
        update: ["admin", "property_manager", "self"]

# INTEGRATION CONFIGURATION
integrations:
  - name: "payment_processing"
    type: "stripe"
    config:
      webhook_url: "/webhooks/stripe"
      events: ["payment_succeeded", "payment_failed"]
  - name: "email_service"
    type: "sendgrid"
    templates:
      - name: "welcome_tenant"
        subject: "Welcome to {{property.name}}"
        template_id: "d-123456789"
  - name: "sms_service"
    type: "twilio"
    phone_number: "+1234567890"

# VALIDATION RULES
validation:
  business_rules:
    - name: "lease_dates_valid"
      entities: ["tenant"]
      condition: "lease_end_date > lease_start_date"
      message: "Lease end date must be after start date"
    - name: "rent_amount_positive"
      entities: ["tenant", "rent_payment"]
      condition: "rent_amount > 0"
      message: "Rent amount must be positive"
    - name: "property_address_unique"
      entities: ["property"]
      condition: "unique(address)"
      message: "Property address must be unique"
```

### **Configuration Processing Engine**

#### **Domain Configuration Parser** (`backend/app/core/domain_config.py`)
```python
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import yaml
from pathlib import Path

class FieldConfig(BaseModel):
    """Configuration for entity field"""
    name: str
    type: str  # string, integer, decimal, date, datetime, enum, text
    required: bool = False
    max_length: Optional[int] = None
    default: Optional[Any] = None
    options: Optional[List[str]] = None  # For enum fields
    validation: Optional[str] = None  # positive, email, url, etc.

class RelationshipConfig(BaseModel):
    """Configuration for entity relationship"""
    entity: str
    type: str  # one_to_one, one_to_many, many_to_one, many_to_many
    foreign_key: Optional[str] = None
    required: bool = False
    description: Optional[str] = None

class EntityConfig(BaseModel):
    """Configuration for business entity"""
    display_name: str
    inherits_from: Optional[str] = None
    fields: List[FieldConfig] = []
    relationships: List[RelationshipConfig] = []
    business_rules: List[Dict[str, Any]] = []

class NavigationItem(BaseModel):
    """Navigation menu item"""
    key: str
    label: str
    icon: str
    route: str
    permissions: Optional[List[str]] = None

class DashboardMetric(BaseModel):
    """Dashboard metric configuration"""
    name: str
    label: str
    entity: str
    calculation: str  # count, sum, avg, count_where, sum_where
    field: Optional[str] = None
    condition: Optional[str] = None
    period: Optional[str] = None
    icon: str

class DomainConfig(BaseModel):
    """Complete domain configuration"""
    domain: Dict[str, str]  # name, title, description, etc.
    entities: Dict[str, EntityConfig]
    navigation: Dict[str, List[NavigationItem]]
    dashboard: Dict[str, List[Any]]
    workflows: List[Dict[str, Any]] = []
    api: Dict[str, Any] = {}
    integrations: List[Dict[str, Any]] = []
    validation: Dict[str, Any] = {}

class DomainConfigParser:
    """Parse and validate domain configuration files"""
    
    @staticmethod
    def load_from_file(config_path: Path) -> DomainConfig:
        """Load domain configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config_data = yaml.safe_load(file)
            
            return DomainConfig(**config_data)
        except Exception as e:
            raise ValueError(f"Failed to parse domain configuration: {e}")
    
    @staticmethod
    def validate_config(config: DomainConfig) -> List[str]:
        """Validate domain configuration and return list of errors"""
        errors = []
        
        # Validate entity relationships
        entity_names = set(config.entities.keys())
        for entity_name, entity_config in config.entities.items():
            for relationship in entity_config.relationships:
                if relationship.entity not in entity_names:
                    errors.append(
                        f"Entity '{entity_name}' references unknown entity '{relationship.entity}'"
                    )
        
        # Validate navigation references
        for nav_item in config.navigation.get('primary_menu', []):
            # Check if route references valid entity
            entity_key = nav_item.route.strip('/').split('/')[0]
            if entity_key not in ['dashboard'] and entity_key not in entity_names:
                errors.append(f"Navigation item '{nav_item.key}' references unknown entity '{entity_key}'")
        
        # Validate dashboard metrics
        for metric in config.dashboard.get('metrics', []):
            if metric.entity not in entity_names:
                errors.append(f"Dashboard metric '{metric.name}' references unknown entity '{metric.entity}'")
        
        return errors
    
    @staticmethod
    def get_entity_hierarchy(config: DomainConfig) -> Dict[str, List[str]]:
        """Get entity inheritance hierarchy"""
        hierarchy = {}
        
        for entity_name, entity_config in config.entities.items():
            if entity_config.inherits_from:
                if entity_config.inherits_from not in hierarchy:
                    hierarchy[entity_config.inherits_from] = []
                hierarchy[entity_config.inherits_from].append(entity_name)
        
        return hierarchy
```

---

## 🤖 CODE GENERATION ENGINE

### **Template Generator Architecture**

#### **Model Generation Engine** (`backend/app/core/template_generator.py`)
```python
from typing import Dict, Any, List
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import os

class ModelGenerator:
    """Generate SQLAlchemy models from domain configuration"""
    
    def __init__(self, template_dir: Path):
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.model_template = self.env.get_template('model.py.j2')
    
    def generate_model(self, entity_name: str, entity_config: EntityConfig) -> str:
        """Generate SQLAlchemy model class"""
        
        # Map configuration types to SQLAlchemy types
        type_mapping = {
            'string': 'String',
            'text': 'Text', 
            'integer': 'Integer',
            'decimal': 'Numeric',
            'date': 'Date',
            'datetime': 'DateTime',
            'boolean': 'Boolean',
            'enum': 'Enum'
        }
        
        # Process fields
        fields = []
        for field in entity_config.fields:
            field_def = {
                'name': field.name,
                'type': type_mapping.get(field.type, 'String'),
                'nullable': not field.required,
                'default': field.default,
                'max_length': field.max_length
            }
            
            if field.type == 'enum' and field.options:
                field_def['enum_name'] = f"{entity_name.title()}{field.name.title()}"
                field_def['enum_options'] = field.options
            
            fields.append(field_def)
        
        # Process relationships
        relationships = []
        for rel in entity_config.relationships:
            rel_def = {
                'name': rel.entity if rel.type in ['many_to_one', 'one_to_one'] else f"{rel.entity}s",
                'type': rel.type,
                'target_entity': rel.entity.title(),
                'foreign_key': rel.foreign_key,
                'required': rel.required
            }
            relationships.append(rel_def)
        
        return self.model_template.render(
            class_name=entity_name.title(),
            table_name=entity_name.lower(),
            fields=fields,
            relationships=relationships,
            inherits_from=entity_config.inherits_from or 'BaseModel'
        )

class SchemaGenerator:
    """Generate Pydantic schemas from domain configuration"""
    
    def __init__(self, template_dir: Path):
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.schema_template = self.env.get_template('schema.py.j2')
    
    def generate_schemas(self, entity_name: str, entity_config: EntityConfig) -> str:
        """Generate complete set of Pydantic schemas"""
        
        # Map configuration types to Pydantic types
        type_mapping = {
            'string': 'str',
            'text': 'str',
            'integer': 'int', 
            'decimal': 'Decimal',
            'date': 'date',
            'datetime': 'datetime',
            'boolean': 'bool',
            'enum': f"{entity_name.title()}{field.name.title()}"  # Custom enum
        }
        
        # Process fields for schemas
        base_fields = []
        create_fields = []
        update_fields = []
        
        for field in entity_config.fields:
            field_type = type_mapping.get(field.type, 'str')
            if not field.required:
                field_type = f"Optional[{field_type}]"
            
            field_def = {
                'name': field.name,
                'type': field_type,
                'required': field.required,
                'validation': self._get_field_validation(field)
            }
            
            base_fields.append(field_def)
            create_fields.append(field_def)
            
            # All fields optional in update schema
            update_field_def = field_def.copy()
            update_field_def['type'] = f"Optional[{field_type.replace('Optional[', '').replace(']', '')}]"
            update_field_def['required'] = False
            update_fields.append(update_field_def)
        
        return self.schema_template.render(
            class_name=entity_name.title(),
            base_fields=base_fields,
            create_fields=create_fields,
            update_fields=update_fields
        )
    
    def _get_field_validation(self, field: FieldConfig) -> str:
        """Generate Pydantic field validation"""
        validations = []
        
        if field.max_length:
            validations.append(f"max_length={field.max_length}")
        
        if field.validation == 'positive':
            validations.append("gt=0")
        elif field.validation == 'email':
            return "Field(..., regex=r'^[^@]+@[^@]+\\.[^@]+$')"
        
        if validations:
            return f"Field(..., {', '.join(validations)})"
        
        return "Field(...)" if field.required else "Field(default=None)"

class RouteGenerator:
    """Generate FastAPI routes from domain configuration"""
    
    def __init__(self, template_dir: Path):
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.route_template = self.env.get_template('routes.py.j2')
    
    def generate_routes(self, entity_name: str, entity_config: EntityConfig, 
                       api_config: Dict[str, Any]) -> str:
        """Generate complete CRUD routes for entity"""
        
        operations = api_config.get('operations', ['create', 'read', 'update', 'delete', 'list'])
        permissions = api_config.get('permissions', {})
        
        route_operations = []
        
        for operation in operations:
            op_def = {
                'operation': operation,
                'permissions': permissions.get(operation, ['user']),
                'method': self._get_http_method(operation),
                'path': self._get_route_path(operation),
                'response_model': self._get_response_model(operation, entity_name)
            }
            route_operations.append(op_def)
        
        return self.route_template.render(
            entity_name=entity_name,
            class_name=entity_name.title(),
            operations=route_operations,
            entity_config=entity_config
        )
    
    def _get_http_method(self, operation: str) -> str:
        mapping = {
            'create': 'POST',
            'read': 'GET', 
            'update': 'PUT',
            'delete': 'DELETE',
            'list': 'GET'
        }
        return mapping.get(operation, 'GET')
    
    def _get_route_path(self, operation: str) -> str:
        if operation == 'list':
            return '/'
        elif operation in ['read', 'update', 'delete']:
            return '/{id}'
        else:
            return '/'
    
    def _get_response_model(self, operation: str, entity_name: str) -> str:
        class_name = entity_name.title()
        if operation == 'list':
            return f"{class_name}List"
        elif operation == 'delete':
            return "Dict[str, str]"
        else:
            return f"{class_name}Read"

class UIComponentGenerator:
    """Generate React components from domain configuration"""
    
    def __init__(self, template_dir: Path):
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.component_template = self.env.get_template('component.tsx.j2')
    
    def generate_dashboard(self, domain_config: DomainConfig) -> str:
        """Generate domain-specific dashboard component"""
        
        metrics = domain_config.dashboard.get('metrics', [])
        charts = domain_config.dashboard.get('charts', [])
        
        return self.component_template.render(
            component_name="Dashboard",
            domain_title=domain_config.domain['title'],
            metrics=metrics,
            charts=charts,
            entities=domain_config.entities
        )
    
    def generate_entity_management(self, entity_name: str, 
                                 entity_config: EntityConfig) -> str:
        """Generate entity management component (list/create/edit)"""
        
        return self.component_template.render(
            component_name=f"{entity_name.title()}Management",
            entity_name=entity_name,
            entity_config=entity_config,
            fields=entity_config.fields,
            relationships=entity_config.relationships
        )
```

### **Template Files Structure**

#### **Jinja2 Templates** (`templates/`)
```
templates/
├── backend/
│   ├── model.py.j2           # SQLAlchemy model template
│   ├── schema.py.j2          # Pydantic schema template
│   ├── routes.py.j2          # FastAPI routes template
│   └── service.py.j2         # Business logic service template
├── frontend/
│   ├── component.tsx.j2      # React component template
│   ├── dashboard.tsx.j2      # Dashboard component template
│   ├── form.tsx.j2           # Form component template
│   └── list.tsx.j2           # List component template
└── config/
    ├── main.py.j2            # FastAPI main app template
    ├── api_init.py.j2        # API router initialization
    └── navigation.tsx.j2     # Navigation component template
```

#### **Model Template Example** (`templates/backend/model.py.j2`)
```python
"""{{ class_name }} model definition."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Numeric, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
{% if enum_fields %}
import enum
{% endif %}

from app.models.base import BaseModel

{% for enum_field in enum_fields %}
class {{ enum_field.enum_name }}(enum.Enum):
    """{{ enum_field.description | default('Enum for ' + enum_field.name) }}"""
    {% for option in enum_field.enum_options %}
    {{ option.upper() }} = "{{ option }}"
    {% endfor %}

{% endfor %}

class {{ class_name }}({{ inherits_from }}):
    """{{ class_name }} entity for {{ domain_name }} domain."""
    
    __tablename__ = "{{ table_name }}"
    
    {% for field in fields %}
    {% if field.type == 'String' %}
    {{ field.name }} = Column(String({{ field.max_length | default(255) }}), 
                             nullable={{ field.nullable }})
    {% elif field.type == 'Enum' %}
    {{ field.name }} = Column(Enum({{ field.enum_name }}), 
                             nullable={{ field.nullable }})
    {% else %}
    {{ field.name }} = Column({{ field.type }}, nullable={{ field.nullable }})
    {% endif %}
    {% endfor %}
    
    {% for relationship in relationships %}
    {% if relationship.type == 'many_to_one' %}
    {{ relationship.foreign_key }} = Column(Integer, 
                                           ForeignKey('{{ relationship.target_entity.lower() }}.id'),
                                           nullable={{ not relationship.required }})
    {{ relationship.name }} = relationship("{{ relationship.target_entity }}", 
                                          back_populates="{{ table_name }}s")
    {% elif relationship.type == 'one_to_many' %}
    {{ relationship.name }} = relationship("{{ relationship.target_entity }}", 
                                          back_populates="{{ table_name }}")
    {% endif %}
    {% endfor %}
    
    def __repr__(self) -> str:
        return f"<{{ class_name }}(id={self.id}, name={getattr(self, 'name', 'N/A')})>"
```

---

## 📋 ADAPTATION MANUAL GENERATOR

### **Step-by-Step Manual Generation System**

#### **Manual Generator Engine** (`backend/app/core/manual_generator.py`)
```python
from typing import List, Dict, Any
from pathlib import Path
from dataclasses import dataclass

@dataclass
class AdaptationStep:
    """Single step in domain adaptation process"""
    step_number: int
    category: str  # database, api, frontend, configuration
    title: str
    description: str
    files_to_modify: List[str]
    changes: List[Dict[str, Any]]
    validation_steps: List[str]
    estimated_time: int  # minutes
    difficulty: str  # easy, medium, hard

@dataclass  
class FileChange:
    """Specific file change instruction"""
    file_path: str
    line_range: tuple  # (start_line, end_line) or None for append
    old_code: str
    new_code: str
    explanation: str
    change_type: str  # replace, insert, append, delete

class AdaptationManualGenerator:
    """Generate step-by-step adaptation manuals"""
    
    def generate_adaptation_manual(
        self,
        source_config: DomainConfig,
        target_config: DomainConfig
    ) -> List[AdaptationStep]:
        """Generate complete adaptation manual"""
        
        steps = []
        step_number = 1
        
        # 1. Database Schema Changes
        db_steps = self._generate_database_steps(source_config, target_config, step_number)
        steps.extend(db_steps)
        step_number += len(db_steps)
        
        # 2. Model Updates
        model_steps = self._generate_model_steps(source_config, target_config, step_number)
        steps.extend(model_steps)
        step_number += len(model_steps)
        
        # 3. Schema Updates
        schema_steps = self._generate_schema_steps(source_config, target_config, step_number)
        steps.extend(schema_steps)
        step_number += len(schema_steps)
        
        # 4. API Route Updates
        api_steps = self._generate_api_steps(source_config, target_config, step_number)
        steps.extend(api_steps)
        step_number += len(api_steps)
        
        # 5. Frontend Updates
        frontend_steps = self._generate_frontend_steps(source_config, target_config, step_number)
        steps.extend(frontend_steps)
        step_number += len(frontend_steps)
        
        # 6. Configuration Updates
        config_steps = self._generate_config_steps(source_config, target_config, step_number)
        steps.extend(config_steps)
        
        return steps
    
    def _generate_database_steps(
        self, 
        source_config: DomainConfig, 
        target_config: DomainConfig,
        start_step: int
    ) -> List[AdaptationStep]:
        """Generate database migration steps"""
        
        steps = []
        
        # Compare entities and generate migration steps
        source_entities = set(source_config.entities.keys())
        target_entities = set(target_config.entities.keys())
        
        # Entities to rename
        renamed_entities = []
        for source_entity in source_entities:
            if source_entity not in target_entities:
                # Find best match in target entities
                best_match = self._find_best_entity_match(
                    source_entity, 
                    source_config.entities[source_entity],
                    target_config.entities
                )
                if best_match:
                    renamed_entities.append((source_entity, best_match))
        
        # Generate rename table steps
        for old_name, new_name in renamed_entities:
            step = AdaptationStep(
                step_number=start_step,
                category="database",
                title=f"Rename {old_name} table to {new_name}",
                description=f"Update database table name from {old_name} to {new_name}",
                files_to_modify=[
                    f"backend/alembic/versions/rename_{old_name}_to_{new_name}.py"
                ],
                changes=[
                    {
                        "type": "create_migration",
                        "operation": "rename_table",
                        "old_table": old_name,
                        "new_table": new_name
                    }
                ],
                validation_steps=[
                    f"Run migration: alembic upgrade head",
                    f"Verify table renamed: Check database has {new_name} table",
                    f"Verify data preserved: Check row count matches"
                ],
                estimated_time=10,
                difficulty="easy"
            )
            steps.append(step)
            start_step += 1
        
        # Generate field modification steps
        for entity_name in target_entities:
            if entity_name in source_config.entities:
                field_steps = self._generate_field_modification_steps(
                    entity_name,
                    source_config.entities[entity_name],
                    target_config.entities[entity_name],
                    start_step
                )
                steps.extend(field_steps)
                start_step += len(field_steps)
        
        return steps
    
    def _generate_model_steps(
        self,
        source_config: DomainConfig,
        target_config: DomainConfig, 
        start_step: int
    ) -> List[AdaptationStep]:
        """Generate model class modification steps"""
        
        steps = []
        
        for entity_name, entity_config in target_config.entities.items():
            # Generate model file modification step
            step = AdaptationStep(
                step_number=start_step,
                category="api",
                title=f"Update {entity_name.title()} model class",
                description=f"Modify SQLAlchemy model for {entity_name} entity",
                files_to_modify=[f"backend/app/models/{entity_name}.py"],
                changes=[
                    FileChange(
                        file_path=f"backend/app/models/{entity_name}.py",
                        line_range=None,
                        old_code=f"# Placeholder for {entity_name} model updates",
                        new_code=self._generate_model_code(entity_name, entity_config),
                        explanation=f"Replace model definition with {target_config.domain['name']} specific fields",
                        change_type="replace"
                    )
                ],
                validation_steps=[
                    f"Import model: from app.models.{entity_name} import {entity_name.title()}",
                    f"Test model creation: Create test {entity_name} instance",
                    f"Check relationships: Verify foreign key constraints"
                ],
                estimated_time=15,
                difficulty="medium"
            )
            steps.append(step)
            start_step += 1
        
        return steps
    
    def generate_markdown_manual(self, steps: List[AdaptationStep]) -> str:
        """Generate markdown documentation for adaptation manual"""
        
        total_time = sum(step.estimated_time for step in steps)
        
        markdown = f"""# Domain Adaptation Manual
## From Task Management to {target_config.domain['title']}

**Estimated Total Time**: {total_time} minutes ({total_time//60}h {total_time%60}m)
**Total Steps**: {len(steps)}
**Difficulty**: {"Hard" if any(s.difficulty == "hard" for s in steps) else "Medium"}

---

## 📋 Overview

This manual provides step-by-step instructions to adapt the TeamFlow task management system into a {target_config.domain['title']} system.

### What You'll Build:
- ✅ Complete {target_config.domain['title']} application
- ✅ Database schema for {target_config.domain['name']} domain
- ✅ REST API with full CRUD operations
- ✅ React frontend with domain-specific UI
- ✅ Authentication and authorization
- ✅ Admin dashboard with analytics

### Prerequisites:
- Python 3.8+ and Node.js 16+
- Basic knowledge of FastAPI and React
- Database setup (PostgreSQL or SQLite)

---

## 🔧 Adaptation Steps

"""
        
        for step in steps:
            markdown += f"""
### Step {step.step_number}: {step.title}

**Category**: {step.category.title()}  
**Estimated Time**: {step.estimated_time} minutes  
**Difficulty**: {step.difficulty.title()}

{step.description}

#### Files to Modify:
"""
            for file_path in step.files_to_modify:
                markdown += f"- `{file_path}`\n"
            
            markdown += "\n#### Changes:\n"
            for i, change in enumerate(step.changes, 1):
                if isinstance(change, FileChange):
                    markdown += f"""
{i}. **{change.file_path}**
   - **Change Type**: {change.change_type}
   - **Explanation**: {change.explanation}
   
   ```python
   # OLD CODE:
   {change.old_code}
   
   # NEW CODE:  
   {change.new_code}
   ```
"""
                else:
                    markdown += f"{i}. {change}\n"
            
            markdown += "\n#### Validation Steps:\n"
            for validation in step.validation_steps:
                markdown += f"- [ ] {validation}\n"
            
            markdown += "\n---\n"
        
        return markdown
```

---

## 🧪 DOMAIN VALIDATION SYSTEM

### **Multi-Domain Proof of Concept**

#### **Domain Examples for Validation**
```yaml
# 1. REAL ESTATE MANAGEMENT
real_estate_config.yaml:
  - Properties, Tenants, Maintenance Requests
  - Lease management, rent tracking
  - Property analytics dashboard

# 2. E-COMMERCE PLATFORM  
ecommerce_config.yaml:
  - Products, Orders, Customers
  - Inventory management, payment processing
  - Sales analytics dashboard

# 3. HEALTHCARE MANAGEMENT
healthcare_config.yaml:
  - Patients, Appointments, Medical Records
  - Provider scheduling, insurance tracking
  - Patient outcomes dashboard

# 4. EDUCATION MANAGEMENT
education_config.yaml:
  - Students, Courses, Assignments
  - Grade tracking, attendance management
  - Academic performance dashboard
```

#### **Validation Testing Framework** (`tests/template_validation.py`)
```python
import pytest
from pathlib import Path
from app.core.domain_config import DomainConfigParser
from app.core.template_generator import ModelGenerator, SchemaGenerator, RouteGenerator

class TemplateValidationTests:
    """Comprehensive validation tests for template system"""
    
    @pytest.fixture
    def domain_configs(self):
        """Load all domain configuration files"""
        config_dir = Path("tests/domain_configs")
        configs = {}
        
        for config_file in config_dir.glob("*.yaml"):
            domain_name = config_file.stem
            configs[domain_name] = DomainConfigParser.load_from_file(config_file)
        
        return configs
    
    def test_all_domains_valid_config(self, domain_configs):
        """Test all domain configurations are valid"""
        for domain_name, config in domain_configs.items():
            errors = DomainConfigParser.validate_config(config)
            assert len(errors) == 0, f"Domain {domain_name} has configuration errors: {errors}"
    
    def test_model_generation(self, domain_configs):
        """Test model generation for all domains"""
        generator = ModelGenerator(Path("templates/backend"))
        
        for domain_name, config in domain_configs.items():
            for entity_name, entity_config in config.entities.items():
                model_code = generator.generate_model(entity_name, entity_config)
                
                # Validate generated code compiles
                compile(model_code, f"{domain_name}_{entity_name}_model.py", "exec")
                
                # Check for required patterns
                assert f"class {entity_name.title()}" in model_code
                assert "BaseModel" in model_code or entity_config.inherits_from in model_code
    
    def test_schema_generation(self, domain_configs):
        """Test schema generation for all domains"""
        generator = SchemaGenerator(Path("templates/backend"))
        
        for domain_name, config in domain_configs.items():
            for entity_name, entity_config in config.entities.items():
                schema_code = generator.generate_schemas(entity_name, entity_config)
                
                # Validate generated code compiles
                compile(schema_code, f"{domain_name}_{entity_name}_schema.py", "exec")
                
                # Check for required schema classes
                assert f"class {entity_name.title()}Base" in schema_code
                assert f"class {entity_name.title()}Create" in schema_code
                assert f"class {entity_name.title()}Read" in schema_code
    
    def test_api_generation(self, domain_configs):
        """Test API route generation for all domains"""
        generator = RouteGenerator(Path("templates/backend"))
        
        for domain_name, config in domain_configs.items():
            for entity_name, entity_config in config.entities.items():
                api_config = config.api.get(entity_name, {})
                route_code = generator.generate_routes(entity_name, entity_config, api_config)
                
                # Validate generated code compiles
                compile(route_code, f"{domain_name}_{entity_name}_routes.py", "exec")
                
                # Check for CRUD operations
                assert "async def create_" in route_code
                assert "async def list_" in route_code
    
    def test_complete_domain_generation(self, domain_configs):
        """Test complete application generation for each domain"""
        from app.core.template_system import TemplateSystemGenerator
        
        generator = TemplateSystemGenerator()
        
        for domain_name, config in domain_configs.items():
            # Generate complete application
            output_dir = Path(f"tests/generated/{domain_name}")
            generator.generate_complete_application(config, output_dir)
            
            # Validate generated application structure
            assert (output_dir / "backend" / "app" / "main.py").exists()
            assert (output_dir / "backend" / "app" / "models").exists()
            assert (output_dir / "frontend" / "src" / "App.tsx").exists()
            
            # Test generated application starts without errors
            # (Would need Docker/subprocess testing for full validation)
    
    def test_adaptation_manual_generation(self, domain_configs):
        """Test adaptation manual generation between domains"""
        from app.core.manual_generator import AdaptationManualGenerator
        
        generator = AdaptationManualGenerator()
        
        # Test adaptation from task_management to real_estate
        source_config = domain_configs['task_management']
        target_config = domain_configs['real_estate']
        
        steps = generator.generate_adaptation_manual(source_config, target_config)
        
        # Validate manual completeness
        assert len(steps) > 0
        
        categories = set(step.category for step in steps)
        assert 'database' in categories
        assert 'api' in categories
        assert 'frontend' in categories
        
        # Validate step details
        for step in steps:
            assert step.title
            assert step.description
            assert len(step.files_to_modify) > 0
            assert step.estimated_time > 0
```

---

## 📊 SUCCESS METRICS & VALIDATION

### **Phase 2 Success Criteria**

#### **Code Reduction Targets**
| Component | Current | Template | Reduction | Status |
|-----------|---------|----------|-----------|---------|
| Frontend Mock Data | 267 lines | 0 lines | 100% | 🎯 Target |
| Schema Boilerplate | 1,200 lines | 50 lines | 96% | 🎯 Target |
| CRUD Routes | 800 lines | 100 lines | 88% | 🎯 Target |
| Component Templates | 900 lines | 300 lines | 67% | 🎯 Target |
| **TOTAL** | **3,167 lines** | **450 lines** | **86%** | 🎯 Target |

#### **Template System Quality Metrics**
- ✅ **Configuration Validation**: 100% of domain configs pass validation
- ✅ **Code Generation**: 100% of generated code compiles without errors  
- ✅ **Domain Coverage**: 4+ different domains successfully generated
- ✅ **Adaptation Manual**: Complete step-by-step instructions for 2+ domain transformations
- ✅ **Functional Testing**: Generated applications start and serve requests

#### **Business Value Metrics**
- **Development Time**: 95% reduction (weeks → hours)
- **Code Quality**: Enterprise security, performance, analytics included
- **Maintainability**: Single template update affects all domains
- **Scalability**: Unlimited domains from single template system

---

## 🚀 IMPLEMENTATION ROADMAP

### **Phase 2 Timeline (4 weeks)**

#### **Week 1: Foundation & Configuration**
- ✅ Create domain configuration schema
- ✅ Build configuration parser and validator
- ✅ Design template file structure
- ✅ Create first domain example (real estate)

#### **Week 2: Code Generation Engine**
- ✅ Build model generator with Jinja2 templates
- ✅ Build schema generator for Pydantic classes
- ✅ Build route generator for FastAPI endpoints  
- ✅ Build UI component generator for React

#### **Week 3: Adaptation Manual System**
- ✅ Build adaptation step generation engine
- ✅ Create step-by-step manual generator
- ✅ Generate sample adaptation manual (task → real estate)
- ✅ Test manual with actual domain transformation

#### **Week 4: Validation & Testing**
- ✅ Create 4 complete domain examples
- ✅ Build automated validation test suite
- ✅ Test complete application generation
- ✅ Validate adaptation manuals work correctly

### **Deliverables Checklist**
- [ ] **Domain Configuration System** - YAML-based domain specification
- [ ] **Template Generation Engine** - Automated code generation
- [ ] **Adaptation Manual Generator** - Step-by-step transformation guides
- [ ] **Multi-Domain Validation** - 4+ working domain examples
- [ ] **Testing Framework** - Automated validation of generated code
- [ ] **Documentation** - Complete technical documentation

---

## 📋 CONCLUSION

**Phase 2 will transform TeamFlow from a single-purpose application into a revolutionary universal template system.**

Key achievements:
- 🏗️ **Template Architecture** - Clean separation between universal and configurable layers
- 🔧 **Configuration System** - YAML-driven domain specification
- 🤖 **Code Generation** - Automated creation of complete applications  
- 📚 **Adaptation Manuals** - Step-by-step transformation guides
- 🧪 **Validation Framework** - Comprehensive testing of generated code

**The result will be the world's most efficient business application template system**, capable of generating production-ready applications for any domain in minutes rather than months.

**Success Metrics**: 86% code reduction, 95% time savings, enterprise-grade features included automatically.

---

*Next: Phase 3 - Implementation & Market Validation*