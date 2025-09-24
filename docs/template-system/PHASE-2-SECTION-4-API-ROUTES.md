# 🏗️ PHASE 2: TEMPLATE EXTRACTION & ENGINE DESIGN
## Section 4: API Routes Generation

---

## 🛣️ API ROUTES GENERATION ENGINE

### **FastAPI Routes Generator**

The routes generator creates complete REST API endpoints with authentication, validation, and business logic integration. It follows the TeamFlow pattern of route organization and middleware integration.

#### **Routes Generator** (`backend/app/core/routes_generator.py`)
```python
from typing import Dict, Any, List
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from app.core.domain_config import DomainConfig, EntityConfig

class RoutesGenerator:
    """Generate FastAPI routes from domain configuration"""
    
    def __init__(self, template_dir: Path):
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.routes_template = self.env.get_template('routes.py.j2')
        self.api_init_template = self.env.get_template('api_init.py.j2')
    
    def generate_entity_routes(self, entity_name: str, entity_config: EntityConfig, 
                              domain_config: DomainConfig) -> str:
        """Generate complete CRUD routes for an entity"""
        
        class_name = entity_name.title()
        snake_name = entity_name.lower()
        plural_name = f"{snake_name}s"
        
        # Determine route prefix based on domain
        domain_prefix = domain_config.domain.name.lower().replace(' ', '-')
        route_prefix = f"/{domain_prefix}/{plural_name}"
        
        # Generate operations based on entity configuration
        operations = self._get_supported_operations(entity_config)
        
        # Security configuration
        auth_required = entity_config.security.get('authentication', True)
        role_required = entity_config.security.get('role')
        permissions = entity_config.security.get('permissions', [])
        
        # Business logic hooks
        hooks = self._extract_business_hooks(entity_config)
        
        return self.routes_template.render(
            class_name=class_name,
            snake_name=snake_name,
            plural_name=plural_name,
            route_prefix=route_prefix,
            operations=operations,
            auth_required=auth_required,
            role_required=role_required,
            permissions=permissions,
            hooks=hooks,
            domain_name=domain_config.domain.name,
            pagination_limit=entity_config.pagination.get('default_limit', 20),
            max_limit=entity_config.pagination.get('max_limit', 100)
        )
    
    def _get_supported_operations(self, entity_config: EntityConfig) -> List[str]:
        """Determine which CRUD operations to generate"""
        operations = entity_config.operations or ['create', 'read', 'update', 'delete', 'list']
        
        # Add additional operations based on configuration
        if entity_config.features.get('bulk_operations'):
            operations.extend(['bulk_create', 'bulk_update', 'bulk_delete'])
        
        if entity_config.features.get('soft_delete'):
            operations.append('restore')
        
        if entity_config.features.get('export'):
            operations.append('export')
        
        if entity_config.features.get('search'):
            operations.append('search')
        
        return operations
    
    def _extract_business_hooks(self, entity_config: EntityConfig) -> Dict[str, str]:
        """Extract business logic hooks from configuration"""
        hooks = {}
        
        # Pre/post operation hooks
        if entity_config.business_logic:
            for operation in ['create', 'update', 'delete']:
                pre_hook = entity_config.business_logic.get(f'pre_{operation}')
                post_hook = entity_config.business_logic.get(f'post_{operation}')
                
                if pre_hook:
                    hooks[f'pre_{operation}'] = pre_hook
                if post_hook:
                    hooks[f'post_{operation}'] = post_hook
        
        # Validation hooks
        validation = entity_config.validation
        if validation:
            hooks['custom_validation'] = validation.get('custom_function')
        
        return hooks

    def generate_api_initialization(self, domain_config: DomainConfig, 
                                  entity_routes: Dict[str, str]) -> str:
        """Generate API router initialization file"""
        
        domain_name = domain_config.domain.name
        route_imports = []
        route_includes = []
        
        for entity_name in entity_routes.keys():
            snake_name = entity_name.lower()
            route_imports.append(f"from .{snake_name} import router as {snake_name}_router")
            route_includes.append({
                'router': f"{snake_name}_router",
                'prefix': f"/{snake_name}s",
                'tags': [entity_name.title()]
            })
        
        return self.api_init_template.render(
            domain_name=domain_name,
            route_imports=route_imports,
            route_includes=route_includes,
            version=domain_config.api.get('version', 'v1'),
            middleware=domain_config.api.get('middleware', [])
        )
```

#### **Routes Template** (`templates/backend/routes.py.j2`)
```python
"""{{ class_name }} API routes for {{ domain_name }}."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
{% if auth_required %}
from app.core.security import get_current_user
from app.models.user import User
{% endif %}
from app.models.{{ snake_name }} import {{ class_name }}
from app.schemas.{{ snake_name }} import (
    {{ class_name }}Create,
    {{ class_name }}Update,
    {{ class_name }}Read,
    {{ class_name }}List
)
{% if hooks.get('custom_validation') %}
from app.services.{{ snake_name }}_service import {{ class_name }}Service
{% endif %}

router = APIRouter()

{% if 'create' in operations %}
@router.post("/", response_model={{ class_name }}Read, status_code=status.HTTP_201_CREATED)
async def create_{{ snake_name }}(
    {{ snake_name }}_data: {{ class_name }}Create,
    db: AsyncSession = Depends(get_db){% if auth_required %},
    current_user: User = Depends(get_current_user){% endif %}
):
    """Create a new {{ snake_name }}."""
    
    {% if hooks.get('pre_create') %}
    # Pre-creation business logic
    await {{ hooks.pre_create }}({{ snake_name }}_data, current_user, db)
    {% endif %}
    
    {% if hooks.get('custom_validation') %}
    # Custom validation
    service = {{ class_name }}Service(db)
    await service.validate_{{ snake_name }}({{ snake_name }}_data{% if auth_required %}, current_user{% endif %})
    {% endif %}
    
    # Create {{ snake_name }}
    db_{{ snake_name }} = {{ class_name }}(**{{ snake_name }}_data.model_dump())
    {% if auth_required %}
    db_{{ snake_name }}.created_by = current_user.id
    {% endif %}
    
    db.add(db_{{ snake_name }})
    await db.commit()
    await db.refresh(db_{{ snake_name }})
    
    {% if hooks.get('post_create') %}
    # Post-creation business logic
    await {{ hooks.post_create }}(db_{{ snake_name }}, current_user, db)
    {% endif %}
    
    return db_{{ snake_name }}
{% endif %}

{% if 'read' in operations %}
@router.get("/{id}", response_model={{ class_name }}Read)
async def get_{{ snake_name }}(
    id: int = Path(..., description="{{ class_name }} ID"),
    db: AsyncSession = Depends(get_db){% if auth_required %},
    current_user: User = Depends(get_current_user){% endif %}
):
    """Get {{ snake_name }} by ID."""
    
    query = select({{ class_name }}).where({{ class_name }}.id == id)
    
    {% if role_required %}
    # Apply role-based filtering
    if current_user.role != "{{ role_required }}":
        query = query.where({{ class_name }}.created_by == current_user.id)
    {% endif %}
    
    result = await db.execute(query)
    {{ snake_name }} = result.scalar_one_or_none()
    
    if not {{ snake_name }}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{{ class_name }} not found"
        )
    
    return {{ snake_name }}
{% endif %}

{% if 'list' in operations %}
@router.get("/", response_model={{ class_name }}List)
async def list_{{ plural_name }}(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query({{ pagination_limit }}, ge=1, le={{ max_limit }}, description="Number of items to return"),
    db: AsyncSession = Depends(get_db){% if auth_required %},
    current_user: User = Depends(get_current_user){% endif %}
):
    """Get paginated list of {{ plural_name }}."""
    
    # Base query
    query = select({{ class_name }})
    
    {% if role_required %}
    # Apply role-based filtering
    if current_user.role != "{{ role_required }}":
        query = query.where({{ class_name }}.created_by == current_user.id)
    {% endif %}
    
    # Count query
    count_query = select(func.count({{ class_name }}.id))
    {% if role_required %}
    if current_user.role != "{{ role_required }}":
        count_query = count_query.where({{ class_name }}.created_by == current_user.id)
    {% endif %}
    
    # Execute queries
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    items_result = await db.execute(
        query.offset(skip).limit(limit).order_by({{ class_name }}.created_at.desc())
    )
    items = items_result.scalars().all()
    
    return {{ class_name }}List(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )
{% endif %}

{% if 'update' in operations %}
@router.put("/{id}", response_model={{ class_name }}Read)
async def update_{{ snake_name }}(
    id: int = Path(..., description="{{ class_name }} ID"),
    {{ snake_name }}_data: {{ class_name }}Update,
    db: AsyncSession = Depends(get_db){% if auth_required %},
    current_user: User = Depends(get_current_user){% endif %}
):
    """Update {{ snake_name }}."""
    
    # Get existing {{ snake_name }}
    query = select({{ class_name }}).where({{ class_name }}.id == id)
    {% if role_required %}
    if current_user.role != "{{ role_required }}":
        query = query.where({{ class_name }}.created_by == current_user.id)
    {% endif %}
    
    result = await db.execute(query)
    db_{{ snake_name }} = result.scalar_one_or_none()
    
    if not db_{{ snake_name }}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{{ class_name }} not found"
        )
    
    {% if hooks.get('pre_update') %}
    # Pre-update business logic
    await {{ hooks.pre_update }}(db_{{ snake_name }}, {{ snake_name }}_data, current_user, db)
    {% endif %}
    
    # Update fields
    update_data = {{ snake_name }}_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_{{ snake_name }}, field, value)
    
    await db.commit()
    await db.refresh(db_{{ snake_name }})
    
    {% if hooks.get('post_update') %}
    # Post-update business logic
    await {{ hooks.post_update }}(db_{{ snake_name }}, current_user, db)
    {% endif %}
    
    return db_{{ snake_name }}
{% endif %}

{% if 'delete' in operations %}
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{{ snake_name }}(
    id: int = Path(..., description="{{ class_name }} ID"),
    db: AsyncSession = Depends(get_db){% if auth_required %},
    current_user: User = Depends(get_current_user){% endif %}
):
    """Delete {{ snake_name }}."""
    
    # Get existing {{ snake_name }}
    query = select({{ class_name }}).where({{ class_name }}.id == id)
    {% if role_required %}
    if current_user.role != "{{ role_required }}":
        query = query.where({{ class_name }}.created_by == current_user.id)
    {% endif %}
    
    result = await db.execute(query)
    db_{{ snake_name }} = result.scalar_one_or_none()
    
    if not db_{{ snake_name }}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{{ class_name }} not found"
        )
    
    {% if hooks.get('pre_delete') %}
    # Pre-deletion business logic
    await {{ hooks.pre_delete }}(db_{{ snake_name }}, current_user, db)
    {% endif %}
    
    {% if 'soft_delete' in entity_config.features %}
    # Soft delete
    db_{{ snake_name }}.is_active = False
    await db.commit()
    {% else %}
    # Hard delete
    await db.delete(db_{{ snake_name }})
    await db.commit()
    {% endif %}
    
    {% if hooks.get('post_delete') %}
    # Post-deletion business logic
    await {{ hooks.post_delete }}(db_{{ snake_name }}, current_user, db)
    {% endif %}
{% endif %}

{% if 'search' in operations %}
@router.get("/search", response_model={{ class_name }}List)
async def search_{{ plural_name }}(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db){% if auth_required %},
    current_user: User = Depends(get_current_user){% endif %}
):
    """Search {{ plural_name }}."""
    
    # Build search query (this would need to be customized per entity)
    search_fields = [{{ class_name }}.name]  # Adjust based on searchable fields
    conditions = []
    
    for field in search_fields:
        conditions.append(field.ilike(f"%{q}%"))
    
    query = select({{ class_name }}).where(or_(*conditions))
    
    {% if role_required %}
    if current_user.role != "{{ role_required }}":
        query = query.where({{ class_name }}.created_by == current_user.id)
    {% endif %}
    
    # Count and items queries
    count_query = select(func.count({{ class_name }}.id)).where(or_(*conditions))
    {% if role_required %}
    if current_user.role != "{{ role_required }}":
        count_query = count_query.where({{ class_name }}.created_by == current_user.id)
    {% endif %}
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    items_result = await db.execute(
        query.offset(skip).limit(limit).order_by({{ class_name }}.created_at.desc())
    )
    items = items_result.scalars().all()
    
    return {{ class_name }}List(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )
{% endif %}
```

### **Service Layer Generation**

The service layer provides business logic abstraction and reusable components for complex operations.

#### **Service Template** (`templates/backend/service.py.j2`)
```python
"""{{ class_name }} business logic service for {{ domain_name }}."""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.{{ snake_name }} import {{ class_name }}
from app.schemas.{{ snake_name }} import {{ class_name }}Create, {{ class_name }}Update
{% if auth_required %}
from app.models.user import User
{% endif %}

class {{ class_name }}Service:
    """Business logic service for {{ class_name }} operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_{{ snake_name }}(
        self, 
        {{ snake_name }}_data: {{ class_name }}Create{% if auth_required %}, 
        user: User{% endif %}
    ) -> {{ class_name }}:
        """Create a new {{ snake_name }} with business logic."""
        
        # Custom validation
        await self.validate_{{ snake_name }}({{ snake_name }}_data{% if auth_required %}, user{% endif %})
        
        # Create entity
        db_{{ snake_name }} = {{ class_name }}(**{{ snake_name }}_data.model_dump())
        {% if auth_required %}
        db_{{ snake_name }}.created_by = user.id
        {% endif %}
        
        self.db.add(db_{{ snake_name }})
        await self.db.commit()
        await self.db.refresh(db_{{ snake_name }})
        
        return db_{{ snake_name }}
    
    async def validate_{{ snake_name }}(
        self, 
        {{ snake_name }}_data: {{ class_name }}Create{% if auth_required %}, 
        user: User{% endif %}
    ) -> None:
        """Custom validation logic for {{ snake_name }}."""
        
        # Add domain-specific validation here
        {% if hooks.get('custom_validation') %}
        # Custom validation from configuration
        {{ hooks.custom_validation }}
        {% endif %}
        
        pass
    
    async def get_{{ snake_name }}_analytics(self{% if auth_required %}, user: User{% endif %}) -> Dict[str, Any]:
        """Get analytics data for {{ plural_name }}."""
        
        query = select(func.count({{ class_name }}.id))
        {% if auth_required and role_required %}
        if user.role != "{{ role_required }}":
            query = query.where({{ class_name }}.created_by == user.id)
        {% endif %}
        
        result = await self.db.execute(query)
        total_count = result.scalar()
        
        return {
            "total_{{ plural_name }}": total_count,
            # Add more analytics as needed
        }
    
    {% if 'bulk_operations' in entity_config.features %}
    async def bulk_create_{{ plural_name }}(
        self, 
        {{ snake_name }}_list: List[{{ class_name }}Create]{% if auth_required %}, 
        user: User{% endif %}
    ) -> List[{{ class_name }}]:
        """Bulk create {{ plural_name }}."""
        
        db_{{ plural_name }} = []
        for {{ snake_name }}_data in {{ snake_name }}_list:
            await self.validate_{{ snake_name }}({{ snake_name }}_data{% if auth_required %}, user{% endif %})
            
            db_{{ snake_name }} = {{ class_name }}(**{{ snake_name }}_data.model_dump())
            {% if auth_required %}
            db_{{ snake_name }}.created_by = user.id
            {% endif %}
            db_{{ plural_name }}.append(db_{{ snake_name }})
        
        self.db.add_all(db_{{ plural_name }})
        await self.db.commit()
        
        for db_{{ snake_name }} in db_{{ plural_name }}:
            await self.db.refresh(db_{{ snake_name }})
        
        return db_{{ plural_name }}
    {% endif %}
```

---

*Continue to Section 5: Frontend Component Generation...*