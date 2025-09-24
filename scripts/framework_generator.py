#!/usr/bin/env python3
"""
TeamFlow Framework Generator

Transforms TeamFlow into customized templates for different use cases.
Creates domain-specific versions while maintaining the core architecture.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from jinja2 import Template


@dataclass
class UseCase:
    """Definition of a use case template."""
    name: str
    description: str
    domain: str
    entities: List[Dict[str, Any]]
    workflows: List[Dict[str, Any]]
    api_endpoints: List[str]
    ui_components: List[str]
    database_extensions: List[str]


class TeamFlowFrameworkGenerator:
    """Generate customized templates from TeamFlow base."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.templates_dir = base_path / "templates"
        self.use_cases = self._load_use_cases()
    
    def _load_use_cases(self) -> Dict[str, UseCase]:
        """Load predefined use case configurations."""
        return {
            "property_management": UseCase(
                name="Property Management System",
                description="Real estate and property management platform",
                domain="property",
                entities=[
                    {"name": "Property", "fields": ["address", "type", "size", "rent"]},
                    {"name": "Tenant", "fields": ["name", "contact", "lease_start", "lease_end"]},
                    {"name": "Maintenance", "fields": ["property_id", "type", "priority", "status"]},
                    {"name": "Payment", "fields": ["tenant_id", "amount", "due_date", "status"]}
                ],
                workflows=[
                    {"name": "Lease Management", "trigger": "lease_expiry", "actions": ["notify_tenant", "schedule_renewal"]},
                    {"name": "Maintenance Requests", "trigger": "maintenance_created", "actions": ["assign_contractor", "schedule_inspection"]}
                ],
                api_endpoints=[
                    "/properties", "/tenants", "/maintenance", "/payments", 
                    "/leases", "/inspections", "/contractors"
                ],
                ui_components=[
                    "PropertyCard", "TenantProfile", "MaintenanceBoard", 
                    "PaymentTracker", "LeaseCalendar"
                ],
                database_extensions=[
                    "property_types", "maintenance_categories", "payment_methods"
                ]
            ),
            
            "event_management": UseCase(
                name="Event Management Platform",
                description="Comprehensive event planning and management system",
                domain="event",
                entities=[
                    {"name": "Event", "fields": ["title", "date", "venue", "capacity", "status"]},
                    {"name": "Attendee", "fields": ["name", "email", "ticket_type", "status"]},
                    {"name": "Vendor", "fields": ["name", "service_type", "contact", "cost"]},
                    {"name": "Schedule", "fields": ["event_id", "activity", "start_time", "duration"]}
                ],
                workflows=[
                    {"name": "Event Planning", "trigger": "event_created", "actions": ["create_checklist", "assign_coordinator"]},
                    {"name": "Registration Management", "trigger": "registration_received", "actions": ["send_confirmation", "update_capacity"]}
                ],
                api_endpoints=[
                    "/events", "/attendees", "/vendors", "/schedules", 
                    "/tickets", "/registrations", "/venues"
                ],
                ui_components=[
                    "EventCard", "AttendeeList", "VendorPanel", 
                    "ScheduleCalendar", "TicketManager"
                ],
                database_extensions=[
                    "event_categories", "ticket_types", "venue_amenities"
                ]
            ),
            
            "inventory_management": UseCase(
                name="Inventory Management System",
                description="Warehouse and inventory tracking platform",
                domain="inventory",
                entities=[
                    {"name": "Product", "fields": ["sku", "name", "description", "category", "price"]},
                    {"name": "Stock", "fields": ["product_id", "quantity", "location", "reorder_level"]},
                    {"name": "Supplier", "fields": ["name", "contact", "terms", "rating"]},
                    {"name": "Order", "fields": ["supplier_id", "items", "total", "status"]}
                ],
                workflows=[
                    {"name": "Restock Management", "trigger": "low_stock", "actions": ["create_purchase_order", "notify_procurement"]},
                    {"name": "Quality Control", "trigger": "stock_received", "actions": ["schedule_inspection", "update_inventory"]}
                ],
                api_endpoints=[
                    "/products", "/stock", "/suppliers", "/orders", 
                    "/warehouses", "/transfers", "/reports"
                ],
                ui_components=[
                    "ProductCatalog", "StockLevels", "SupplierGrid", 
                    "OrderTracker", "WarehouseMap"
                ],
                database_extensions=[
                    "product_categories", "warehouse_locations", "supplier_types"
                ]
            ),
            
            "learning_management": UseCase(
                name="Learning Management System",
                description="Educational platform for courses and student management",
                domain="education",
                entities=[
                    {"name": "Course", "fields": ["title", "description", "instructor", "duration", "level"]},
                    {"name": "Student", "fields": ["name", "email", "enrollment_date", "status"]},
                    {"name": "Lesson", "fields": ["course_id", "title", "content", "order", "type"]},
                    {"name": "Assignment", "fields": ["lesson_id", "title", "due_date", "points"]}
                ],
                workflows=[
                    {"name": "Course Enrollment", "trigger": "student_enrolled", "actions": ["send_welcome", "create_progress_tracker"]},
                    {"name": "Assignment Grading", "trigger": "assignment_submitted", "actions": ["notify_instructor", "update_gradebook"]}
                ],
                api_endpoints=[
                    "/courses", "/students", "/lessons", "/assignments", 
                    "/enrollments", "/grades", "/certificates"
                ],
                ui_components=[
                    "CourseCard", "StudentDashboard", "LessonPlayer", 
                    "AssignmentBoard", "GradeBook"
                ],
                database_extensions=[
                    "course_categories", "learning_paths", "assessment_types"
                ]
            )
        }
    
    def generate_use_case_template(self, use_case_key: str, output_dir: Path) -> bool:
        """Generate a complete template for a specific use case."""
        
        if use_case_key not in self.use_cases:
            print(f"❌ Unknown use case: {use_case_key}")
            return False
        
        use_case = self.use_cases[use_case_key]
        print(f"🚀 Generating {use_case.name} template...")
        
        # Create output directory structure
        self._create_directory_structure(output_dir, use_case)
        
        # Generate core components
        self._generate_models(output_dir, use_case)
        self._generate_schemas(output_dir, use_case)
        self._generate_api_routes(output_dir, use_case)
        self._generate_services(output_dir, use_case)
        self._generate_workflows(output_dir, use_case)
        self._generate_frontend_components(output_dir, use_case)
        self._generate_database_migrations(output_dir, use_case)
        self._generate_configuration(output_dir, use_case)
        self._generate_documentation(output_dir, use_case)
        self._copy_core_files(output_dir)
        
        print(f"✅ {use_case.name} template generated successfully!")
        return True
    
    def _create_directory_structure(self, output_dir: Path, use_case: UseCase):
        """Create the directory structure for the template."""
        directories = [
            "backend/app/api/routes",
            "backend/app/models",
            "backend/app/schemas", 
            "backend/app/services",
            "backend/app/workflows",
            "backend/alembic/versions",
            "frontend/src/components",
            "frontend/src/pages",
            "frontend/src/hooks",
            "frontend/src/types",
            "docs",
            "scripts",
            "tests"
        ]
        
        for dir_path in directories:
            (output_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    def _generate_models(self, output_dir: Path, use_case: UseCase):
        """Generate SQLAlchemy models for the use case."""
        models_dir = output_dir / "backend/app/models"
        
        # Base model (copy from TeamFlow)
        base_model_template = '''"""Base model class with common fields and utilities."""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.ext.declarative import declared_attr
from app.core.database import Base


class BaseModel(Base):
    """Base model class with common fields."""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    def to_dict(self) -> dict:
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
'''
        
        with open(models_dir / "base.py", "w") as f:
            f.write(base_model_template)
        
        # Generate domain-specific models
        for entity in use_case.entities:
            model_template = self._create_model_template(entity, use_case)
            model_file = models_dir / f"{entity['name'].lower()}.py"
            with open(model_file, "w") as f:
                f.write(model_template)
    
    def _create_model_template(self, entity: Dict[str, Any], use_case: UseCase) -> str:
        """Create a SQLAlchemy model template for an entity."""
        
        entity_name = entity["name"]
        fields = entity["fields"]
        
        imports = [
            "from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey",
            "from sqlalchemy.orm import relationship",
            "from app.models.base import BaseModel"
        ]
        
        field_definitions = []
        for field in fields:
            if field.endswith("_id"):
                field_definitions.append(f'    {field} = Column(Integer, ForeignKey("TBD.id"), nullable=True)')
            elif field in ["description", "content", "notes"]:
                field_definitions.append(f'    {field} = Column(Text, nullable=True)')
            elif field in ["status", "type", "category", "priority"]:
                field_definitions.append(f'    {field} = Column(String(50), nullable=True)')
            elif field in ["email", "phone", "contact"]:
                field_definitions.append(f'    {field} = Column(String(255), nullable=True)')
            elif "date" in field or "time" in field:
                field_definitions.append(f'    {field} = Column(DateTime, nullable=True)')
            elif field in ["price", "cost", "amount", "rent"]:
                field_definitions.append(f'    {field} = Column(Integer, nullable=True)  # In cents')
            elif field in ["active", "enabled", "public"]:
                field_definitions.append(f'    {field} = Column(Boolean, default=True)')
            else:
                field_definitions.append(f'    {field} = Column(String(255), nullable=True)')
        
        template = f'''"""{entity_name} model for {use_case.domain} domain."""

{chr(10).join(imports)}


class {entity_name}(BaseModel):
    """{entity_name} entity for {use_case.description}."""
    
    __tablename__ = "{entity_name.lower()}s"
    
{chr(10).join(field_definitions)}
    
    # Add organization relationship for multi-tenancy
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    organization = relationship("Organization")
    
    def __repr__(self):
        return f"<{entity_name}(id={{self.id}}, name={{getattr(self, 'name', 'N/A')}})>"
'''
        
        return template
    
    def _generate_schemas(self, output_dir: Path, use_case: UseCase):
        """Generate Pydantic schemas for the use case."""
        schemas_dir = output_dir / "backend/app/schemas"
        
        for entity in use_case.entities:
            schema_template = self._create_schema_template(entity, use_case)
            schema_file = schemas_dir / f"{entity['name'].lower()}.py"
            with open(schema_file, "w") as f:
                f.write(schema_template)
    
    def _create_schema_template(self, entity: Dict[str, Any], use_case: UseCase) -> str:
        """Create Pydantic schemas for an entity."""
        
        entity_name = entity["name"]
        fields = entity["fields"]
        
        # Create field definitions for Pydantic
        pydantic_fields = []
        for field in fields:
            if "date" in field or "time" in field:
                pydantic_fields.append(f'    {field}: Optional[datetime] = None')
            elif field in ["price", "cost", "amount", "rent", "quantity"]:
                pydantic_fields.append(f'    {field}: Optional[int] = None')
            elif field in ["active", "enabled", "public"]:
                pydantic_fields.append(f'    {field}: bool = True')
            else:
                pydantic_fields.append(f'    {field}: Optional[str] = None')
        
        template = f'''"""{entity_name} schemas for {use_case.domain} domain."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class {entity_name}Base(BaseModel):
    """Base schema for {entity_name}."""
{chr(10).join(pydantic_fields)}


class {entity_name}Create({entity_name}Base):
    """Schema for creating a {entity_name.lower()}."""
    organization_id: int = Field(..., description="Organization ID")


class {entity_name}Update(BaseModel):
    """Schema for updating a {entity_name.lower()}."""
{chr(10).join([f'    {field}: Optional[str] = None' for field in fields[:3]])}


class {entity_name}Response({entity_name}Base):
    """Schema for {entity_name.lower()} responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uuid: str
    organization_id: int
    created_at: datetime
    updated_at: datetime


class {entity_name}List(BaseModel):
    """Schema for {entity_name.lower()} list responses."""
    items: List[{entity_name}Response]
    total: int
    page: int
    per_page: int
'''
        
        return template
    
    def _generate_api_routes(self, output_dir: Path, use_case: UseCase):
        """Generate FastAPI routes for the use case."""
        routes_dir = output_dir / "backend/app/api/routes"
        
        for entity in use_case.entities:
            route_template = self._create_route_template(entity, use_case)
            route_file = routes_dir / f"{entity['name'].lower()}.py"
            with open(route_file, "w") as f:
                f.write(route_template)
    
    def _create_route_template(self, entity: Dict[str, Any], use_case: UseCase) -> str:
        """Create FastAPI routes for an entity."""
        
        entity_name = entity["name"]
        entity_lower = entity_name.lower()
        
        template = f'''"""{entity_name} API routes for {use_case.domain} domain."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.{entity_lower} import {entity_name}
from app.schemas.{entity_lower} import (
    {entity_name}Create, {entity_name}Update, {entity_name}Response, {entity_name}List
)

router = APIRouter(prefix="/{entity_lower}s", tags=["{entity_name}s"])


@router.post("/", response_model={entity_name}Response, status_code=status.HTTP_201_CREATED)
async def create_{entity_lower}(
    {entity_lower}_data: {entity_name}Create,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new {entity_lower}."""
    
    # TODO: Add authorization checks
    
    {entity_lower} = {entity_name}(**{entity_lower}_data.model_dump())
    db.add({entity_lower})
    await db.commit()
    await db.refresh({entity_lower})
    
    return {entity_lower}


@router.get("/", response_model={entity_name}List)
async def list_{entity_lower}s(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    organization_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List {entity_lower}s with pagination."""
    
    query = select({entity_name})
    
    if organization_id:
        query = query.where({entity_name}.organization_id == organization_id)
    
    # Add user access control
    # query = query.where(...)
    
    result = await db.execute(query.offset(skip).limit(limit))
    {entity_lower}s = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(select({entity_name}).where(query.whereclause))
    total = len(count_result.scalars().all())
    
    return {entity_name}List(
        items={entity_lower}s,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )


@router.get("/{{{{id}}}}", response_model={entity_name}Response)
async def get_{entity_lower}(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific {entity_lower}."""
    
    result = await db.execute(select({entity_name}).where({entity_name}.id == id))
    {entity_lower} = result.scalar_one_or_none()
    
    if not {entity_lower}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{entity_name} not found"
        )
    
    # TODO: Add authorization checks
    
    return {entity_lower}


@router.put("/{{{{id}}}}", response_model={entity_name}Response)
async def update_{entity_lower}(
    id: int,
    {entity_lower}_data: {entity_name}Update,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a {entity_lower}."""
    
    result = await db.execute(select({entity_name}).where({entity_name}.id == id))
    {entity_lower} = result.scalar_one_or_none()
    
    if not {entity_lower}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{entity_name} not found"
        )
    
    # TODO: Add authorization checks
    
    # Update fields
    for field, value in {entity_lower}_data.model_dump(exclude_unset=True).items():
        setattr({entity_lower}, field, value)
    
    await db.commit()
    await db.refresh({entity_lower})
    
    return {entity_lower}


@router.delete("/{{{{id}}}}")
async def delete_{entity_lower}(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a {entity_lower}."""
    
    result = await db.execute(select({entity_name}).where({entity_name}.id == id))
    {entity_lower} = result.scalar_one_or_none()
    
    if not {entity_lower}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{entity_name} not found"
        )
    
    # TODO: Add authorization checks
    
    await db.delete({entity_lower})
    await db.commit()
    
    return {{"message": "{entity_name} deleted successfully"}}
'''
        
        return template
    
    def _generate_services(self, output_dir: Path, use_case: UseCase):
        """Generate service classes for business logic."""
        services_dir = output_dir / "backend/app/services"
        
        service_template = f'''"""{use_case.name} business logic services."""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.user import User


class {use_case.domain.title()}Service:
    """Service class for {use_case.domain} domain business logic."""
    
    @staticmethod
    async def get_dashboard_stats(
        db: AsyncSession,
        organization_id: int,
        user: User
    ) -> Dict[str, Any]:
        """Get dashboard statistics for the organization."""
        
        # TODO: Implement domain-specific dashboard logic
        return {{
            "total_items": 0,
            "active_items": 0,
            "recent_activity": [],
            "upcoming_deadlines": []
        }}
    
    @staticmethod
    async def generate_report(
        db: AsyncSession,
        organization_id: int,
        report_type: str,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate domain-specific reports."""
        
        # TODO: Implement reporting logic
        return {{
            "report_type": report_type,
            "data": [],
            "summary": {{}}
        }}
    
    @staticmethod
    async def bulk_import(
        db: AsyncSession,
        organization_id: int,
        data: List[Dict[str, Any]],
        user: User
    ) -> Dict[str, Any]:
        """Bulk import data for the domain."""
        
        # TODO: Implement bulk import logic
        return {{
            "imported": 0,
            "errors": [],
            "warnings": []
        }}
'''
        
        with open(services_dir / f"{use_case.domain}_service.py", "w") as f:
            f.write(service_template)
    
    def _generate_workflows(self, output_dir: Path, use_case: UseCase):
        """Generate workflow definitions."""
        workflows_dir = output_dir / "backend/app/workflows"
        
        for workflow in use_case.workflows:
            workflow_template = f'''"""{workflow['name']} workflow for {use_case.domain} domain."""

from typing import Dict, Any
from datetime import datetime

from app.models.workflow import WorkflowDefinition, WorkflowExecution


class {workflow['name'].replace(' ', '')}Workflow:
    """Workflow class for {workflow['name'].lower()}."""
    
    @staticmethod
    def get_definition() -> Dict[str, Any]:
        """Get workflow definition."""
        return {{
            "name": "{workflow['name']}",
            "trigger_type": "{workflow['trigger']}",
            "steps": [
                {{
                    "name": action,
                    "type": "action",
                    "config": {{}}
                }}
                for action in {workflow['actions']}
            ]
        }}
    
    @staticmethod
    async def execute(execution_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow."""
        
        # TODO: Implement workflow execution logic
        return {{
            "execution_id": execution_id,
            "status": "completed",
            "results": {{}}
        }}
'''
            
            workflow_file = workflows_dir / f"{workflow['name'].lower().replace(' ', '_')}_workflow.py"
            with open(workflow_file, "w") as f:
                f.write(workflow_template)
    
    def _generate_frontend_components(self, output_dir: Path, use_case: UseCase):
        """Generate React components."""
        components_dir = output_dir / "frontend/src/components"
        
        for component in use_case.ui_components:
            component_template = f'''/**
 * {component} component for {use_case.name}
 */

import React from 'react';
import {{ Card, CardContent, CardHeader, CardTitle }} from '@/components/ui/card';

interface {component}Props {{
  // TODO: Add component props
  data?: any;
}}

export const {component}: React.FC<{component}Props> = ({{ data }}) => {{
  return (
    <Card>
      <CardHeader>
        <CardTitle>{component}</CardTitle>
      </CardHeader>
      <CardContent>
        <p>TODO: Implement {component} component for {use_case.domain} domain</p>
        {{/* Add component implementation */}}
      </CardContent>
    </Card>
  );
}};

export default {component};
'''
            
            component_file = components_dir / f"{component}.tsx"
            with open(component_file, "w") as f:
                f.write(component_template)
    
    def _generate_database_migrations(self, output_dir: Path, use_case: UseCase):
        """Generate database migration files."""
        migrations_dir = output_dir / "backend/alembic/versions"
        
        # Create initial migration for the use case
        migration_template = f'''"""Initial {use_case.domain} domain tables

Revision ID: {use_case.domain}_001
Revises: 
Create Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '{use_case.domain}_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create tables for {use_case.domain} domain."""
    
    # TODO: Add table creation statements for:
    {chr(10).join([f'    # - {entity["name"].lower()}s' for entity in use_case.entities])}
    
    pass


def downgrade() -> None:
    """Drop tables for {use_case.domain} domain."""
    
    # TODO: Add table drop statements
    pass
'''
        
        migration_file = migrations_dir / f"{use_case.domain}_001_initial_tables.py"
        with open(migration_file, "w") as f:
            f.write(migration_template)
    
    def _generate_configuration(self, output_dir: Path, use_case: UseCase):
        """Generate configuration files."""
        
        # Domain-specific settings
        config_template = f'''"""{use_case.name} configuration settings."""

from typing import List, Optional
from pydantic import Field
from app.core.config import Settings as BaseSettings


class {use_case.domain.title()}Settings(BaseSettings):
    """Extended settings for {use_case.domain} domain."""
    
    # Domain-specific settings
    {use_case.domain.upper()}_FEATURE_ENABLED: bool = Field(
        default=True, 
        description="Enable {use_case.domain} domain features"
    )
    
    {use_case.domain.upper()}_DEFAULT_PAGE_SIZE: int = Field(
        default=20,
        description="Default page size for {use_case.domain} listings"
    )
    
    # TODO: Add domain-specific configuration options
    
    class Config:
        env_prefix = "{use_case.domain.upper()}_"


# Create domain settings instance
{use_case.domain}_settings = {use_case.domain.title()}Settings()
'''
        
        config_file = output_dir / "backend/app/core" / f"{use_case.domain}_config.py"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w") as f:
            f.write(config_template)
    
    def _generate_documentation(self, output_dir: Path, use_case: UseCase):
        """Generate documentation for the use case."""
        docs_dir = output_dir / "docs"
        
        readme_template = f'''# {use_case.name}

**Generated from TeamFlow Framework**

{use_case.description}

## Features

### Core Entities
{chr(10).join([f'- **{entity["name"]}**: {", ".join(entity["fields"])}' for entity in use_case.entities])}

### Automated Workflows
{chr(10).join([f'- **{wf["name"]}**: Triggered by {wf["trigger"]} → {", ".join(wf["actions"])}' for wf in use_case.workflows])}

### API Endpoints
{chr(10).join([f'- `{endpoint}`' for endpoint in use_case.api_endpoints])}

### UI Components
{chr(10).join([f'- `{component}`' for component in use_case.ui_components])}

## Quick Start

### 1. Setup Database
```bash
cd backend
alembic upgrade head
```

### 2. Start Backend
```bash
python -m uvicorn app.main:app --reload
```

### 3. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Access Application
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Architecture

This application follows the TeamFlow framework architecture:

- **Multi-tenant**: Organization-based data isolation
- **API-First**: RESTful API with automatic documentation
- **Real-time**: WebSocket support for live updates
- **Extensible**: Plugin-based architecture for custom features

## Customization

### Adding New Entities
1. Create model in `backend/app/models/`
2. Create schema in `backend/app/schemas/`
3. Create API routes in `backend/app/api/routes/`
4. Generate migration: `alembic revision --autogenerate`

### Adding Workflows
1. Define workflow in `backend/app/workflows/`
2. Register trigger handlers
3. Add workflow templates via API

### Extending Frontend
1. Create components in `frontend/src/components/`
2. Add pages in `frontend/src/pages/`
3. Define types in `frontend/src/types/`

## License

Generated from TeamFlow Framework - MIT License
'''
        
        with open(docs_dir / "README.md", "w") as f:
            f.write(readme_template)
    
    def _copy_core_files(self, output_dir: Path):
        """Copy core TeamFlow files that are domain-agnostic."""
        
        core_files = [
            "backend/app/core/database.py",
            "backend/app/core/security.py", 
            "backend/app/models/base.py",
            "backend/app/models/user.py",
            "backend/app/models/organization.py",
            "backend/requirements.txt",
            "backend/alembic.ini",
            "docker-compose.yml",
            "frontend/package.json",
            "frontend/tsconfig.json"
        ]
        
        for file_path in core_files:
            src = self.base_path / file_path
            dst = output_dir / file_path
            
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(src, dst)
                except Exception as e:
                    print(f"⚠️ Could not copy {file_path}: {e}")
    
    def list_available_use_cases(self) -> None:
        """List all available use case templates."""
        print("🎯 Available Use Case Templates:")
        print("=" * 50)
        
        for key, use_case in self.use_cases.items():
            print(f"\n📋 {key}")
            print(f"   Name: {use_case.name}")
            print(f"   Domain: {use_case.domain}")
            print(f"   Description: {use_case.description}")
            print(f"   Entities: {len(use_case.entities)} models")
            print(f"   Workflows: {len(use_case.workflows)} automations")
            print(f"   Endpoints: {len(use_case.api_endpoints)} API routes")
    
    def generate_comparison_matrix(self) -> None:
        """Generate a comparison matrix of all use cases."""
        print("\n🔍 Use Case Comparison Matrix")
        print("=" * 80)
        
        headers = ["Use Case", "Domain", "Entities", "Workflows", "API Routes", "UI Components"]
        print(f"{{:<20}} {{:<12}} {{:<10}} {{:<10}} {{:<12}} {{:<15}}".format(*headers))
        print("-" * 80)
        
        for key, use_case in self.use_cases.items():
            row = [
                key[:18],
                use_case.domain,
                str(len(use_case.entities)),
                str(len(use_case.workflows)),
                str(len(use_case.api_endpoints)),
                str(len(use_case.ui_components))
            ]
            print(f"{{:<20}} {{:<12}} {{:<10}} {{:<10}} {{:<12}} {{:<15}}".format(*row))


def main():
    """Main function for the framework generator."""
    import sys
    
    base_path = Path(__file__).parent.parent
    generator = TeamFlowFrameworkGenerator(base_path)
    
    if len(sys.argv) < 2:
        print("TeamFlow Framework Generator")
        print("Usage: python framework_generator.py <command> [args]")
        print("\nCommands:")
        print("  list                     - List available use case templates")
        print("  compare                  - Show comparison matrix of use cases")
        print("  generate <use_case> <dir> - Generate template for use case")
        print("\nExample:")
        print("  python framework_generator.py generate property_management ./property-system")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        generator.list_available_use_cases()
    
    elif command == "compare":
        generator.generate_comparison_matrix()
    
    elif command == "generate":
        if len(sys.argv) < 4:
            print("Usage: python framework_generator.py generate <use_case> <output_directory>")
            print("\nAvailable use cases:")
            for key in generator.use_cases.keys():
                print(f"  - {key}")
            return
        
        use_case_key = sys.argv[2]
        output_dir = Path(sys.argv[3])
        
        if generator.generate_use_case_template(use_case_key, output_dir):
            print(f"\n🎉 Template generated successfully in: {output_dir}")
            print(f"\nNext steps:")
            print(f"1. cd {output_dir}")
            print(f"2. Review and customize the generated code")
            print(f"3. Set up your database and environment")
            print(f"4. Run the application!")
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()