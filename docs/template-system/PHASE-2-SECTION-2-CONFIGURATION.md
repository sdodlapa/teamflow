# 🏗️ PHASE 2: TEMPLATE EXTRACTION & ENGINE DESIGN
## Section 2: Configuration System Design

---

## 🔧 CONFIGURATION SYSTEM DESIGN

### **Domain Configuration Schema**

The configuration system uses YAML files to define complete business domains. Each domain configuration specifies entities, relationships, UI structure, and business rules.

#### **Configuration File Structure** (`domain-config.yaml`)

##### **1. Domain Metadata**
```yaml
# Basic domain information
domain:
  name: "real_estate"           # Internal identifier (snake_case)
  title: "PropertyFlow"         # Display name for UI
  description: "Real Estate Property Management System"
  logo: "🏠"                   # Emoji or icon identifier
  color_scheme: "blue"         # Primary color theme
  version: "1.0.0"             # Domain version
```

##### **2. Entity Definitions**
```yaml
# PRIMARY BUSINESS ENTITIES
entities:
  property:                    # Entity name (snake_case)
    display_name: "Property"   # Singular form for UI
    display_name_plural: "Properties"  # Plural form for UI
    
    # Entity fields (beyond base fields: id, uuid, created_at, updated_at)
    fields:
      - name: "address"
        type: "string"
        required: true
        max_length: 500
        description: "Property street address"
        
      - name: "price"
        type: "decimal"
        required: true
        validation: "positive"
        description: "Property listing price"
        
      - name: "bedrooms"
        type: "integer"
        default: 1
        min_value: 0
        max_value: 20
        
      - name: "property_type"
        type: "enum"
        required: true
        options: ["house", "apartment", "condo", "townhouse"]
        default: "house"
    
    # Relationships with other entities
    relationships:
      - entity: "tenant"
        type: "one_to_many"
        description: "Property can have multiple tenants"
        foreign_key: "property_id"
        
      - entity: "maintenance_request"
        type: "one_to_many"
        description: "Property maintenance requests"
    
    # Business rules and validation
    business_rules:
      - name: "price_validation"
        condition: "price > 0"
        message: "Property price must be positive"
        
      - name: "auto_assign_manager"
        trigger: "property_created"
        action: "assign_to_default_manager"
        parameters:
          manager_role: "property_manager"

  tenant:
    display_name: "Tenant"
    inherits_from: "user"      # Extends base User model
    
    fields:
      - name: "lease_start_date"
        type: "date"
        required: true
        
      - name: "lease_end_date" 
        type: "date"
        required: true
        validation: "after_lease_start"
        
      - name: "rent_amount"
        type: "decimal"
        required: true
        validation: "positive"
    
    relationships:
      - entity: "property"
        type: "many_to_one"
        foreign_key: "property_id"
        required: true
```

##### **3. Navigation Configuration**
```yaml
# UI NAVIGATION STRUCTURE
navigation:
  primary_menu:
    - key: "dashboard"
      label: "Dashboard"
      icon: "📊"
      route: "/dashboard"
      permissions: ["user", "admin"]
      
    - key: "properties"
      label: "Properties"
      icon: "🏠" 
      route: "/properties"
      permissions: ["property_manager", "admin"]
      
    - key: "tenants"
      label: "Tenants"
      icon: "👥"
      route: "/tenants"
      permissions: ["property_manager", "admin"]
      
    - key: "maintenance"
      label: "Maintenance"
      icon: "🔧"
      route: "/maintenance"
      permissions: ["property_manager", "maintenance_staff", "admin"]

  secondary_menu:
    - key: "reports"
      label: "Reports"
      icon: "📈"
      route: "/reports"
      permissions: ["admin"]
```

##### **4. Dashboard Configuration**
```yaml
# DASHBOARD METRICS AND CHARTS
dashboard:
  title: "Property Management Dashboard"
  
  # Key metrics displayed as cards
  metrics:
    - name: "total_properties"
      label: "Total Properties"
      entity: "property"
      calculation: "count"
      icon: "🏠"
      color: "blue"
      
    - name: "occupied_properties"
      label: "Occupied Properties"
      entity: "property"
      calculation: "count_where"
      condition: "tenant_id IS NOT NULL"
      icon: "✅"
      color: "green"
      
    - name: "monthly_revenue"
      label: "Monthly Revenue"
      entity: "rent_payment"
      calculation: "sum"
      field: "amount"
      period: "current_month"
      icon: "💰"
      color: "gold"
      format: "currency"

  # Charts and visualizations
  charts:
    - name: "occupancy_rate"
      type: "gauge"
      title: "Occupancy Rate"
      calculation: "percentage"
      numerator: "occupied_properties"
      denominator: "total_properties"
      target: 90
      
    - name: "maintenance_by_type"
      type: "pie"
      title: "Maintenance Requests by Type"
      entity: "maintenance_request"
      group_by: "request_type"
      time_period: "last_30_days"

  # Recent activity feed
  activity_feed:
    - entity: "property"
      events: ["created", "updated", "rented"]
      limit: 10
    - entity: "maintenance_request"
      events: ["created", "completed"]
      limit: 5
```

### **Configuration Processing Engine**

#### **Domain Configuration Parser** (`backend/app/core/domain_config.py`)
```python
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
import yaml
from pathlib import Path
from enum import Enum

class FieldType(str, Enum):
    """Supported field types"""
    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ENUM = "enum"

class RelationshipType(str, Enum):
    """Supported relationship types"""
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"

class FieldConfig(BaseModel):
    """Configuration for entity field"""
    name: str
    type: FieldType
    required: bool = False
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default: Optional[Any] = None
    options: Optional[List[str]] = None  # For enum fields
    validation: Optional[str] = None
    description: Optional[str] = None
    
    @validator('options')
    def validate_enum_options(cls, v, values):
        if values.get('type') == FieldType.ENUM and not v:
            raise ValueError('Enum fields must have options defined')
        return v

class RelationshipConfig(BaseModel):
    """Configuration for entity relationship"""
    entity: str
    type: RelationshipType
    foreign_key: Optional[str] = None
    required: bool = False
    description: Optional[str] = None

class BusinessRuleConfig(BaseModel):
    """Configuration for business rule"""
    name: str
    condition: Optional[str] = None
    trigger: Optional[str] = None
    action: Optional[str] = None
    message: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class EntityConfig(BaseModel):
    """Configuration for business entity"""
    display_name: str
    display_name_plural: Optional[str] = None
    inherits_from: Optional[str] = None
    fields: List[FieldConfig] = []
    relationships: List[RelationshipConfig] = []
    business_rules: List[BusinessRuleConfig] = []
    
    @validator('display_name_plural')
    def set_plural_name(cls, v, values):
        if not v and 'display_name' in values:
            return f"{values['display_name']}s"
        return v

class NavigationItem(BaseModel):
    """Navigation menu item"""
    key: str
    label: str
    icon: str
    route: str
    permissions: List[str] = ["user"]

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
    color: Optional[str] = "blue"
    format: Optional[str] = None  # currency, percentage, number

class DomainMetadata(BaseModel):
    """Domain metadata"""
    name: str
    title: str
    description: str
    logo: str
    color_scheme: str = "blue"
    version: str = "1.0.0"

class DomainConfig(BaseModel):
    """Complete domain configuration"""
    domain: DomainMetadata
    entities: Dict[str, EntityConfig]
    navigation: Dict[str, List[NavigationItem]]
    dashboard: Dict[str, Any]
    workflows: List[Dict[str, Any]] = []
    api: Dict[str, Any] = {}
    integrations: List[Dict[str, Any]] = []
    validation: Dict[str, Any] = {}
```

---

*Continue to Section 3: Code Generation Engine...*