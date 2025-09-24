# 🏗️ PHASE 2: TEMPLATE EXTRACTION & ENGINE DESIGN
## Section 3: Code Generation Engine

---

## 🤖 CODE GENERATION ENGINE

### **Template Generator Architecture**

The code generation engine uses Jinja2 templates to generate complete applications from domain configurations. It creates models, schemas, API routes, and UI components automatically.

#### **Template Files Structure**
```
templates/
├── backend/
│   ├── model.py.j2           # SQLAlchemy model template
│   ├── schema.py.j2          # Pydantic schema template
│   ├── routes.py.j2          # FastAPI routes template
│   ├── service.py.j2         # Business logic service template
│   └── __init__.py.j2        # Module initialization template
├── frontend/
│   ├── component.tsx.j2      # Generic React component template
│   ├── dashboard.tsx.j2      # Dashboard component template
│   ├── form.tsx.j2           # Form component template
│   ├── list.tsx.j2           # List component template
│   └── navigation.tsx.j2     # Navigation component template
└── config/
    ├── main.py.j2            # FastAPI main app template
    ├── api_init.py.j2        # API router initialization
    └── package.json.j2       # Frontend package.json template
```

### **Model Generation Engine**

#### **SQLAlchemy Model Generator** (`backend/app/core/model_generator.py`)
```python
from typing import Dict, Any, List
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from app.core.domain_config import DomainConfig, EntityConfig, FieldConfig, RelationshipConfig

class ModelGenerator:
    """Generate SQLAlchemy models from domain configuration"""
    
    def __init__(self, template_dir: Path):
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.model_template = self.env.get_template('model.py.j2')
    
    def generate_model(self, entity_name: str, entity_config: EntityConfig, 
                      domain_config: DomainConfig) -> str:
        """Generate SQLAlchemy model class"""
        
        # Map configuration types to SQLAlchemy types
        type_mapping = {
            'string': 'String',
            'text': 'Text',
            'integer': 'Integer',
            'decimal': 'Numeric',
            'boolean': 'Boolean',
            'date': 'Date',
            'datetime': 'DateTime',
            'enum': 'Enum'
        }
        
        # Process fields
        fields = []
        enum_classes = []
        
        for field in entity_config.fields:
            field_def = {
                'name': field.name,
                'type': type_mapping.get(field.type, 'String'),
                'nullable': not field.required,
                'default': field.default,
                'max_length': field.max_length if field.type == 'string' else None
            }
            
            # Handle enum fields
            if field.type == 'enum' and field.options:
                enum_name = f"{entity_name.title()}{field.name.title()}"
                field_def['type'] = f"Enum({enum_name})"
                enum_classes.append({
                    'name': enum_name,
                    'options': field.options,
                    'description': field.description or f"Enum for {field.name}"
                })
            
            # Add validation constraints
            if field.validation:
                field_def['validation'] = field.validation
            
            fields.append(field_def)
        
        # Process relationships
        relationships = []
        foreign_keys = []
        
        for rel in entity_config.relationships:
            if rel.type == 'many_to_one':
                # Add foreign key column
                fk_name = rel.foreign_key or f"{rel.entity}_id"
                foreign_keys.append({
                    'name': fk_name,
                    'target_table': rel.entity.lower(),
                    'nullable': not rel.required
                })
                
                # Add relationship
                relationships.append({
                    'name': rel.entity,
                    'type': 'many_to_one',
                    'target_class': rel.entity.title(),
                    'back_populates': f"{entity_name}s"
                })
            
            elif rel.type == 'one_to_many':
                relationships.append({
                    'name': f"{rel.entity}s",
                    'type': 'one_to_many',
                    'target_class': rel.entity.title(),
                    'back_populates': entity_name
                })
        
        return self.model_template.render(
            class_name=entity_name.title(),
            table_name=entity_name.lower(),
            fields=fields,
            foreign_keys=foreign_keys,
            relationships=relationships,
            enum_classes=enum_classes,
            inherits_from=entity_config.inherits_from or 'BaseModel',
            domain_name=domain_config.domain.title
        )

    def generate_all_models(self, domain_config: DomainConfig, output_dir: Path) -> Dict[str, str]:
        """Generate all models for a domain"""
        generated_models = {}
        
        for entity_name, entity_config in domain_config.entities.items():
            model_code = self.generate_model(entity_name, entity_config, domain_config)
            
            # Write to file
            model_file = output_dir / f"{entity_name}.py"
            model_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(model_file, 'w') as f:
                f.write(model_code)
            
            generated_models[entity_name] = str(model_file)
        
        return generated_models
```

#### **Model Template** (`templates/backend/model.py.j2`)
```python
"""{{ class_name }} model definition for {{ domain_name }}."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Numeric, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
{% if enum_classes %}
import enum
{% endif %}

from app.models.base import BaseModel

{% for enum_class in enum_classes %}
class {{ enum_class.name }}(enum.Enum):
    """{{ enum_class.description }}"""
    {% for option in enum_class.options %}
    {{ option.upper() }} = "{{ option }}"
    {% endfor %}

{% endfor %}

class {{ class_name }}({{ inherits_from }}):
    """{{ class_name }} entity for {{ domain_name }} domain."""
    
    __tablename__ = "{{ table_name }}"
    
    {% for field in fields %}
    {% if field.type == 'String' and field.max_length %}
    {{ field.name }} = Column(String({{ field.max_length }}), nullable={{ field.nullable }})
    {% elif field.type.startswith('Enum(') %}
    {{ field.name }} = Column({{ field.type }}, nullable={{ field.nullable }})
    {% else %}
    {{ field.name }} = Column({{ field.type }}, nullable={{ field.nullable }})
    {% endif %}
    {% endfor %}
    
    {% for fk in foreign_keys %}
    {{ fk.name }} = Column(Integer, ForeignKey('{{ fk.target_table }}.id'), nullable={{ fk.nullable }})
    {% endfor %}
    
    {% for relationship in relationships %}
    {% if relationship.type == 'many_to_one' %}
    {{ relationship.name }} = relationship("{{ relationship.target_class }}", back_populates="{{ relationship.back_populates }}")
    {% elif relationship.type == 'one_to_many' %}
    {{ relationship.name }} = relationship("{{ relationship.target_class }}", back_populates="{{ relationship.back_populates }}")
    {% endif %}
    {% endfor %}
    
    def __repr__(self) -> str:
        name_field = getattr(self, 'name', None) or getattr(self, 'title', None) or 'N/A'
        return f"<{{ class_name }}(id={self.id}, name={name_field})>"
```

### **Schema Generation Engine**

#### **Pydantic Schema Generator** (`backend/app/core/schema_generator.py`)
```python
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
            'boolean': 'bool',
            'date': 'date',
            'datetime': 'datetime',
            'enum': f"{entity_name.title()}{'{field_name}'.title()}"  # Will be replaced per field
        }
        
        # Process fields for different schema types
        base_fields = []
        create_only_fields = []
        enum_imports = set()
        
        for field in entity_config.fields:
            field_type = type_mapping.get(field.type, 'str')
            
            # Handle enum types
            if field.type == 'enum':
                enum_name = f"{entity_name.title()}{field.name.title()}"
                field_type = enum_name
                enum_imports.add(enum_name)
            
            # Make optional if not required or has default
            optional = not field.required or field.default is not None
            if optional:
                field_type = f"Optional[{field_type}]"
            
            field_def = {
                'name': field.name,
                'type': field_type,
                'required': field.required,
                'default': field.default,
                'validation': self._get_field_validation(field),
                'description': field.description
            }
            
            base_fields.append(field_def)
        
        return self.schema_template.render(
            class_name=entity_name.title(),
            base_fields=base_fields,
            enum_imports=list(enum_imports),
            inherits_from=entity_config.inherits_from
        )
    
    def _get_field_validation(self, field: FieldConfig) -> str:
        """Generate Pydantic field validation"""
        validations = []
        
        if field.max_length:
            validations.append(f"max_length={field.max_length}")
        
        if field.min_length:
            validations.append(f"min_length={field.min_length}")
        
        if field.min_value is not None:
            validations.append(f"ge={field.min_value}")
        
        if field.max_value is not None:
            validations.append(f"le={field.max_value}")
        
        if field.validation == 'positive':
            validations.append("gt=0")
        elif field.validation == 'email':
            return "Field(..., regex=r'^[^@]+@[^@]+\\.[^@]+$')"
        
        if validations:
            return f"Field({', '.join(validations)})"
        
        if field.required and field.default is None:
            return "Field(...)"
        
        return f"Field(default={repr(field.default)})" if field.default is not None else "Field(default=None)"
```

#### **Schema Template** (`templates/backend/schema.py.j2`)
```python
"""{{ class_name }} Pydantic schemas for API serialization."""

from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

{% if enum_imports %}
from app.models.{{ class_name.lower() }} import {{ enum_imports | join(', ') }}
{% endif %}
{% if inherits_from %}
from app.schemas.{{ inherits_from }} import {{ inherits_from.title() }}Base
{% endif %}

class {{ class_name }}Base({% if inherits_from %}{{ inherits_from.title() }}Base{% else %}BaseModel{% endif %}):
    """Base {{ class_name.lower() }} schema with common fields."""
    
    {% for field in base_fields %}
    {{ field.name }}: {{ field.type }} = {{ field.validation }}
    {% endfor %}

class {{ class_name }}Create({{ class_name }}Base):
    """Schema for creating a new {{ class_name.lower() }}."""
    pass

class {{ class_name }}Update(BaseModel):
    """Schema for updating {{ class_name.lower() }} information."""
    
    {% for field in base_fields %}
    {{ field.name }}: Optional[{{ field.type.replace('Optional[', '').replace(']', '') }}] = Field(default=None)
    {% endfor %}

class {{ class_name }}Read({{ class_name }}Base):
    """Schema for reading {{ class_name.lower() }} data."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime

class {{ class_name }}List(BaseModel):
    """Schema for paginated {{ class_name.lower() }} list."""
    
    items: List[{{ class_name }}Read]
    total: int
    skip: int
    limit: int
```

---

*Continue to Section 4: API Routes Generation...*