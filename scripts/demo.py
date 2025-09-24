#!/usr/bin/env python3
"""
TeamFlow Framework Demo

Demonstrates the framework's adaptability by generating different use case examples.
"""

import os
import sys
from pathlib import Path

# Add the scripts directory to Python path
sys.path.append(str(Path(__file__).parent))

from framework_generator import TeamFlowFrameworkGenerator
from template_registry import template_registry, get_available_templates


def demo_framework_capabilities():
    """Demonstrate the framework's capabilities."""
    
    print("🎯 TeamFlow Framework Capabilities Demo")
    print("=" * 60)
    
    # Show available templates
    print("\n📋 Available Domain Templates:")
    templates = get_available_templates()
    for key, description in templates.items():
        print(f"  • {key}: {description}")
    
    # Show detailed comparison
    generator = TeamFlowFrameworkGenerator(Path(__file__).parent.parent)
    generator.generate_comparison_matrix()
    
    print("\n🔧 Framework Features:")
    print("  ✅ Multi-tenant architecture with organization isolation")
    print("  ✅ Configurable entity models with relationships")
    print("  ✅ Automated workflow definitions and execution")
    print("  ✅ REST API generation with authentication")
    print("  ✅ React component templates with TypeScript")
    print("  ✅ Database migration management")
    print("  ✅ Role-based access control")
    print("  ✅ Real-time updates via WebSockets")
    print("  ✅ File upload and management")
    print("  ✅ Advanced search and filtering")
    print("  ✅ Analytics and reporting")
    print("  ✅ Audit logging and compliance")


def demo_property_management():
    """Demo property management system generation."""
    
    print("\n🏠 Property Management System Demo")
    print("=" * 50)
    
    template = template_registry.get_template("property_management")
    if not template:
        print("❌ Property management template not found")
        return
    
    print(f"📊 Template Overview:")
    print(f"  Name: {template.name}")
    print(f"  Entities: {len(template.entities)} models")
    print(f"  Workflows: {len(template.workflows)} automations")
    print(f"  UI Components: {len(template.ui_components)} components")
    print(f"  API Endpoints: {len(template.api_endpoints)} routes")
    
    print(f"\n🏗️ Generated Components:")
    print(f"  Database Models:")
    for entity in template.entities:
        print(f"    • {entity.name} ({len(entity.fields)} fields)")
    
    print(f"  Automated Workflows:")
    for workflow in template.workflows:
        print(f"    • {workflow.name}: {len(workflow.steps)} steps")
    
    print(f"  UI Components:")
    for component in template.ui_components:
        print(f"    • {component.name} ({component.type})")
    
    print(f"\n⚙️ Key Features:")
    for feature, enabled in template.configuration["features"].items():
        status = "✅" if enabled else "❌"
        print(f"    {status} {feature.replace('_', ' ').title()}")


def demo_restaurant_management():
    """Demo restaurant management system generation."""
    
    print("\n🍽️ Restaurant Management System Demo")
    print("=" * 50)
    
    template = template_registry.get_template("restaurant_management")
    if not template:
        print("❌ Restaurant management template not found")
        return
    
    print(f"📊 Template Overview:")
    print(f"  Name: {template.name}")
    print(f"  Domain: Restaurant Operations")
    print(f"  Entities: {len(template.entities)} models")
    print(f"  Workflows: {len(template.workflows)} automations")
    
    print(f"\n🏗️ Core Entities:")
    for entity in template.entities:
        key_fields = [f.name for f in entity.fields[:3]]
        print(f"    • {entity.name}: {', '.join(key_fields)}...")
    
    print(f"\n🔄 Business Workflows:")
    for workflow in template.workflows:
        print(f"    • {workflow.name}")
        print(f"      Trigger: {workflow.trigger_type}")
        print(f"      Steps: {len(workflow.steps)} automated actions")
    
    print(f"\n🎯 Specialized Features:")
    features = template.configuration["features"]
    for feature, enabled in features.items():
        if enabled:
            print(f"    ✅ {feature.replace('_', ' ').title()}")


def demo_code_generation():
    """Demonstrate actual code generation."""
    
    print("\n💻 Code Generation Demo")
    print("=" * 40)
    
    # Generate a small sample to show the capability
    print("🔧 Sample Generated Model (Property):")
    print("```python")
    
    sample_model = '''class Property(BaseModel):
    """Property entity for property management domain."""
    
    __tablename__ = "properties"
    
    address = Column(String(255), nullable=False, index=True)
    property_type = Column(String(50), nullable=False, index=True)
    size_sqft = Column(Integer, nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    rent_amount = Column(Integer, nullable=True)  # In cents
    status = Column(String(20), default="available", index=True)
    description = Column(Text, nullable=True)
    amenities = Column(Text, nullable=True)  # JSON array
    
    # Multi-tenant relationship
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    organization = relationship("Organization")
    
    # Property-specific relationships
    leases = relationship("Lease", back_populates="property")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="property")
'''
    
    print(sample_model)
    print("```")
    
    print("\n🔧 Sample Generated API Route:")
    print("```python")
    
    sample_route = '''@router.get("/properties", response_model=PropertyList)
async def list_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    property_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List properties with filtering and pagination."""
    
    query = select(Property)
    
    # Apply filters
    if property_type:
        query = query.where(Property.property_type == property_type)
    if status:
        query = query.where(Property.status == status)
    
    # Apply organization isolation
    query = query.where(Property.organization_id.in_(
        current_user.get_accessible_organizations()
    ))
    
    result = await db.execute(query.offset(skip).limit(limit))
    properties = result.scalars().all()
    
    return PropertyList(items=properties, total=len(properties))
'''
    
    print(sample_route)
    print("```")


def demo_customization():
    """Demonstrate framework customization capabilities."""
    
    print("\n🎨 Framework Customization Demo")
    print("=" * 45)
    
    print("🔧 Customization Options:")
    print("  1. Entity Field Types:")
    print("     • string, integer, datetime, boolean, text")
    print("     • foreign_key, json, enum")
    print("     • Custom validation rules")
    
    print("  2. Workflow Triggers:")
    print("     • Event-based (model created/updated)")
    print("     • Time-based (scheduled)")
    print("     • Condition-based (threshold reached)")
    print("     • Manual (user-initiated)")
    
    print("  3. UI Component Types:")
    print("     • Cards, Tables, Forms, Charts")
    print("     • Dashboards, Calendars, Kanban boards")
    print("     • Custom React components")
    
    print("  4. Integration Points:")
    print("     • Payment processors")
    print("     • Email/SMS services")
    print("     • Third-party APIs")
    print("     • Webhooks and external systems")
    
    print("  5. Configuration Levels:")
    print("     • Global application settings")
    print("     • Organization-specific config")
    print("     • User preferences")
    print("     • Feature flags")


def generate_sample_templates():
    """Generate sample templates to demonstrate usage."""
    
    print("\n🚀 Generating Sample Templates")
    print("=" * 40)
    
    base_path = Path(__file__).parent.parent
    generator = TeamFlowFrameworkGenerator(base_path)
    
    output_dir = base_path / "generated_templates"
    output_dir.mkdir(exist_ok=True)
    
    # Generate property management
    if generator.generate_use_case_template("property_management", output_dir / "property_system"):
        print("✅ Property Management template generated")
    
    # Generate restaurant management  
    if generator.generate_use_case_template("restaurant_management", output_dir / "restaurant_system"):
        print("✅ Restaurant Management template generated")
    
    print(f"\n📁 Templates generated in: {output_dir}")
    print("Each template includes:")
    print("  • Complete backend API with FastAPI")
    print("  • React frontend components")
    print("  • Database models and migrations")
    print("  • Business logic services")
    print("  • Automated workflows")
    print("  • Configuration files")
    print("  • Documentation")


def main():
    """Main demo function."""
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "overview":
            demo_framework_capabilities()
        elif command == "property":
            demo_property_management()
        elif command == "restaurant":
            demo_restaurant_management()
        elif command == "codegen":
            demo_code_generation()
        elif command == "custom":
            demo_customization()
        elif command == "generate":
            generate_sample_templates()
        elif command == "all":
            demo_framework_capabilities()
            demo_property_management()
            demo_restaurant_management()
            demo_code_generation()
            demo_customization()
        else:
            print(f"Unknown command: {command}")
            show_usage()
    else:
        show_usage()


def show_usage():
    """Show usage instructions."""
    print("TeamFlow Framework Demo")
    print("Usage: python demo.py <command>")
    print("\nCommands:")
    print("  overview    - Show framework capabilities overview")
    print("  property    - Demo property management template")
    print("  restaurant  - Demo restaurant management template")
    print("  codegen     - Show sample generated code")
    print("  custom      - Show customization options")
    print("  generate    - Generate sample templates")
    print("  all         - Run all demos")
    print("\nExample:")
    print("  python demo.py all")


if __name__ == "__main__":
    main()