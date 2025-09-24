"""
TeamFlow Framework Configuration System

Provides configurable templates and customization options for different domains.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class DomainType(Enum):
    """Available domain types for templates."""
    PROPERTY_MANAGEMENT = "property_management"
    EVENT_MANAGEMENT = "event_management" 
    INVENTORY_MANAGEMENT = "inventory_management"
    LEARNING_MANAGEMENT = "learning_management"
    HEALTHCARE_MANAGEMENT = "healthcare_management"
    RESTAURANT_MANAGEMENT = "restaurant_management"
    FLEET_MANAGEMENT = "fleet_management"
    CRM = "customer_relationship"
    HR_MANAGEMENT = "human_resources"
    FINANCIAL_PLANNING = "financial_planning"


@dataclass
class EntityField:
    """Definition of an entity field."""
    name: str
    type: str  # string, integer, datetime, boolean, text, foreign_key
    nullable: bool = True
    indexed: bool = False
    unique: bool = False
    default: Optional[Any] = None
    description: Optional[str] = None


@dataclass
class EntityDefinition:
    """Definition of a domain entity."""
    name: str
    table_name: str
    description: str
    fields: List[EntityField]
    relationships: List[Dict[str, Any]]
    indexes: List[List[str]]
    constraints: List[Dict[str, Any]]


@dataclass
class WorkflowStep:
    """Definition of a workflow step."""
    name: str
    type: str  # action, condition, notification, integration
    config: Dict[str, Any]
    next_steps: List[str]


@dataclass
class WorkflowDefinition:
    """Definition of a domain workflow."""
    name: str
    description: str
    trigger_type: str
    trigger_config: Dict[str, Any]
    steps: List[WorkflowStep]
    permissions: List[str]


@dataclass
class UIComponent:
    """Definition of a UI component."""
    name: str
    type: str  # card, table, form, chart, dashboard
    props: Dict[str, Any]
    dependencies: List[str]


@dataclass
class APIEndpoint:
    """Definition of an API endpoint."""
    path: str
    method: str
    description: str
    parameters: List[Dict[str, Any]]
    response_model: str
    permissions: List[str]


@dataclass
class DomainTemplate:
    """Complete domain template definition."""
    name: str
    description: str
    domain_type: DomainType
    version: str
    entities: List[EntityDefinition]
    workflows: List[WorkflowDefinition]
    ui_components: List[UIComponent]
    api_endpoints: List[APIEndpoint]
    database_extensions: List[str]
    configuration: Dict[str, Any]
    dependencies: List[str]


class TemplateRegistry:
    """Registry of all available domain templates."""
    
    def __init__(self):
        self.templates: Dict[str, DomainTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load built-in templates."""
        
        # Property Management Template
        self.templates["property_management"] = DomainTemplate(
            name="Property Management System",
            description="Complete property management platform for real estate",
            domain_type=DomainType.PROPERTY_MANAGEMENT,
            version="1.0.0",
            entities=[
                EntityDefinition(
                    name="Property",
                    table_name="properties",
                    description="Real estate properties under management",
                    fields=[
                        EntityField("address", "string", nullable=False, indexed=True),
                        EntityField("property_type", "string", nullable=False, indexed=True),
                        EntityField("size_sqft", "integer"),
                        EntityField("bedrooms", "integer"),
                        EntityField("bathrooms", "integer"),
                        EntityField("rent_amount", "integer", description="Monthly rent in cents"),
                        EntityField("status", "string", default="available", indexed=True),
                        EntityField("description", "text"),
                        EntityField("amenities", "text", description="JSON array of amenities"),
                        EntityField("images", "text", description="JSON array of image URLs"),
                    ],
                    relationships=[
                        {"name": "leases", "type": "one_to_many", "target": "Lease"},
                        {"name": "maintenance_requests", "type": "one_to_many", "target": "MaintenanceRequest"}
                    ],
                    indexes=[["address"], ["property_type", "status"], ["rent_amount"]],
                    constraints=[]
                ),
                EntityDefinition(
                    name="Tenant",
                    table_name="tenants",
                    description="Property tenants and applicants",
                    fields=[
                        EntityField("first_name", "string", nullable=False),
                        EntityField("last_name", "string", nullable=False),
                        EntityField("email", "string", nullable=False, unique=True, indexed=True),
                        EntityField("phone", "string"),
                        EntityField("emergency_contact", "text", description="JSON contact info"),
                        EntityField("employment_info", "text", description="JSON employment details"),
                        EntityField("status", "string", default="active", indexed=True),
                    ],
                    relationships=[
                        {"name": "leases", "type": "one_to_many", "target": "Lease"},
                        {"name": "payments", "type": "one_to_many", "target": "Payment"}
                    ],
                    indexes=[["email"], ["last_name", "first_name"]],
                    constraints=[]
                ),
                EntityDefinition(
                    name="Lease",
                    table_name="leases", 
                    description="Property lease agreements",
                    fields=[
                        EntityField("property_id", "foreign_key", nullable=False),
                        EntityField("tenant_id", "foreign_key", nullable=False),
                        EntityField("start_date", "datetime", nullable=False),
                        EntityField("end_date", "datetime", nullable=False),
                        EntityField("rent_amount", "integer", nullable=False),
                        EntityField("security_deposit", "integer"),
                        EntityField("status", "string", default="active", indexed=True),
                        EntityField("terms", "text", description="Lease terms and conditions"),
                    ],
                    relationships=[
                        {"name": "property", "type": "many_to_one", "target": "Property"},
                        {"name": "tenant", "type": "many_to_one", "target": "Tenant"},
                        {"name": "payments", "type": "one_to_many", "target": "Payment"}
                    ],
                    indexes=[["property_id"], ["tenant_id"], ["start_date", "end_date"]],
                    constraints=[]
                ),
                EntityDefinition(
                    name="MaintenanceRequest",
                    table_name="maintenance_requests",
                    description="Property maintenance and repair requests",
                    fields=[
                        EntityField("property_id", "foreign_key", nullable=False),
                        EntityField("tenant_id", "foreign_key"),
                        EntityField("title", "string", nullable=False),
                        EntityField("description", "text", nullable=False),
                        EntityField("priority", "string", default="medium", indexed=True),
                        EntityField("status", "string", default="open", indexed=True),
                        EntityField("category", "string", indexed=True),
                        EntityField("estimated_cost", "integer"),
                        EntityField("actual_cost", "integer"),
                        EntityField("scheduled_date", "datetime"),
                        EntityField("completed_date", "datetime"),
                        EntityField("contractor_notes", "text"),
                    ],
                    relationships=[
                        {"name": "property", "type": "many_to_one", "target": "Property"},
                        {"name": "tenant", "type": "many_to_one", "target": "Tenant"}
                    ],
                    indexes=[["property_id"], ["status", "priority"], ["scheduled_date"]],
                    constraints=[]
                )
            ],
            workflows=[
                WorkflowDefinition(
                    name="Lease Renewal Process",
                    description="Automated lease renewal notification and processing",
                    trigger_type="scheduled",
                    trigger_config={"schedule": "daily", "condition": "lease_expiry_60_days"},
                    steps=[
                        WorkflowStep("send_renewal_notice", "notification", 
                                   {"template": "lease_renewal", "recipient": "tenant"}, ["await_response"]),
                        WorkflowStep("await_response", "condition",
                                   {"timeout_days": 30}, ["process_renewal", "start_marketing"]),
                        WorkflowStep("process_renewal", "action",
                                   {"create_new_lease": True}, []),
                        WorkflowStep("start_marketing", "action", 
                                   {"list_property": True, "notify_agents": True}, [])
                    ],
                    permissions=["property_manager", "admin"]
                ),
                WorkflowDefinition(
                    name="Maintenance Request Processing", 
                    description="Automated maintenance request handling and assignment",
                    trigger_type="event",
                    trigger_config={"event": "maintenance_request_created"},
                    steps=[
                        WorkflowStep("categorize_request", "action",
                                   {"auto_categorize": True, "priority_assessment": True}, ["assign_contractor"]),
                        WorkflowStep("assign_contractor", "action",
                                   {"match_by_category": True, "check_availability": True}, ["schedule_work"]),
                        WorkflowStep("schedule_work", "action",
                                   {"auto_schedule": True, "notify_tenant": True}, ["track_progress"])
                    ],
                    permissions=["maintenance_manager", "admin"]
                )
            ],
            ui_components=[
                UIComponent("PropertyCard", "card", 
                          {"fields": ["address", "rent_amount", "status"], "actions": ["view", "edit"]}, []),
                UIComponent("PropertyDashboard", "dashboard",
                          {"widgets": ["occupancy_rate", "rent_collection", "maintenance_alerts"]}, ["PropertyCard"]),
                UIComponent("TenantProfile", "form",
                          {"sections": ["personal", "employment", "lease_history"]}, []),
                UIComponent("MaintenanceBoard", "table", 
                          {"columns": ["title", "property", "priority", "status", "scheduled_date"]}, []),
                UIComponent("LeaseCalendar", "chart",
                          {"type": "timeline", "data_source": "leases"}, [])
            ],
            api_endpoints=[
                APIEndpoint("/properties", "GET", "List properties", 
                          [{"name": "status", "type": "string"}, {"name": "property_type", "type": "string"}],
                          "PropertyList", ["property_viewer"]),
                APIEndpoint("/properties", "POST", "Create property",
                          [{"name": "property_data", "type": "PropertyCreate"}],
                          "PropertyResponse", ["property_manager"]),
                APIEndpoint("/tenants", "GET", "List tenants",
                          [{"name": "status", "type": "string"}],
                          "TenantList", ["tenant_viewer"]),
                APIEndpoint("/leases", "GET", "List leases",
                          [{"name": "property_id", "type": "integer"}, {"name": "status", "type": "string"}],
                          "LeaseList", ["lease_viewer"]),
                APIEndpoint("/maintenance", "GET", "List maintenance requests",
                          [{"name": "property_id", "type": "integer"}, {"name": "status", "type": "string"}],
                          "MaintenanceList", ["maintenance_viewer"])
            ],
            database_extensions=[
                "property_types_enum", "maintenance_categories", "lease_statuses", "payment_methods"
            ],
            configuration={
                "features": {
                    "online_payments": True,
                    "tenant_portal": True,
                    "maintenance_tracking": True,
                    "document_management": True,
                    "automated_reminders": True
                },
                "integrations": {
                    "payment_processors": ["stripe", "plaid"],
                    "background_checks": ["rentspree", "smartmove"],
                    "accounting": ["quickbooks", "xero"]
                },
                "notifications": {
                    "rent_reminders": {"days_before": [7, 3, 1]},
                    "lease_renewals": {"days_before": [90, 60, 30]},
                    "maintenance_updates": {"immediate": True}
                }
            },
            dependencies=["payment_processing", "document_storage", "notification_service"]
        )
        
        # Restaurant Management Template
        self.templates["restaurant_management"] = DomainTemplate(
            name="Restaurant Management System",
            description="Complete restaurant operations management platform",
            domain_type=DomainType.RESTAURANT_MANAGEMENT,
            version="1.0.0",
            entities=[
                EntityDefinition(
                    name="MenuItem",
                    table_name="menu_items",
                    description="Restaurant menu items and dishes",
                    fields=[
                        EntityField("name", "string", nullable=False, indexed=True),
                        EntityField("description", "text"),
                        EntityField("price", "integer", nullable=False, description="Price in cents"),
                        EntityField("category", "string", nullable=False, indexed=True),
                        EntityField("ingredients", "text", description="JSON array of ingredients"),
                        EntityField("allergens", "text", description="JSON array of allergens"),
                        EntityField("nutritional_info", "text", description="JSON nutritional data"),
                        EntityField("preparation_time", "integer", description="Minutes to prepare"),
                        EntityField("availability", "boolean", default=True, indexed=True),
                        EntityField("image_url", "string"),
                    ],
                    relationships=[
                        {"name": "order_items", "type": "one_to_many", "target": "OrderItem"}
                    ],
                    indexes=[["category", "availability"], ["name"]],
                    constraints=[]
                ),
                EntityDefinition(
                    name="Order",
                    table_name="orders",
                    description="Customer orders and transactions",
                    fields=[
                        EntityField("order_number", "string", nullable=False, unique=True, indexed=True),
                        EntityField("customer_name", "string"),
                        EntityField("customer_phone", "string"),
                        EntityField("table_number", "integer"),
                        EntityField("order_type", "string", nullable=False, indexed=True), # dine_in, takeout, delivery
                        EntityField("status", "string", default="pending", indexed=True),
                        EntityField("total_amount", "integer", nullable=False),
                        EntityField("tax_amount", "integer"),
                        EntityField("tip_amount", "integer"),
                        EntityField("payment_method", "string"),
                        EntityField("special_instructions", "text"),
                        EntityField("estimated_ready_time", "datetime"),
                        EntityField("completed_at", "datetime"),
                    ],
                    relationships=[
                        {"name": "order_items", "type": "one_to_many", "target": "OrderItem"}
                    ],
                    indexes=[["order_number"], ["status", "order_type"], ["created_at"]],
                    constraints=[]
                ),
                EntityDefinition(
                    name="OrderItem",
                    table_name="order_items",
                    description="Individual items within an order",
                    fields=[
                        EntityField("order_id", "foreign_key", nullable=False),
                        EntityField("menu_item_id", "foreign_key", nullable=False),
                        EntityField("quantity", "integer", nullable=False, default=1),
                        EntityField("unit_price", "integer", nullable=False),
                        EntityField("customizations", "text", description="JSON customization details"),
                        EntityField("status", "string", default="pending", indexed=True),
                        EntityField("prepared_at", "datetime"),
                    ],
                    relationships=[
                        {"name": "order", "type": "many_to_one", "target": "Order"},
                        {"name": "menu_item", "type": "many_to_one", "target": "MenuItem"}
                    ],
                    indexes=[["order_id"], ["menu_item_id"], ["status"]],
                    constraints=[]
                ),
                EntityDefinition(
                    name="Inventory",
                    table_name="inventory",
                    description="Restaurant inventory and stock management",
                    fields=[
                        EntityField("item_name", "string", nullable=False, indexed=True),
                        EntityField("category", "string", nullable=False, indexed=True),
                        EntityField("unit", "string", nullable=False), # kg, liters, pieces, etc.
                        EntityField("current_stock", "integer", nullable=False),
                        EntityField("minimum_stock", "integer", default=0),
                        EntityField("unit_cost", "integer", description="Cost per unit in cents"),
                        EntityField("supplier", "string"),
                        EntityField("expiry_date", "datetime"),
                        EntityField("last_restock_date", "datetime"),
                        EntityField("restock_quantity", "integer"),
                    ],
                    relationships=[],
                    indexes=[["category"], ["current_stock", "minimum_stock"], ["expiry_date"]],
                    constraints=[]
                )
            ],
            workflows=[
                WorkflowDefinition(
                    name="Order Processing Pipeline",
                    description="Automated order processing from placement to completion",
                    trigger_type="event",
                    trigger_config={"event": "order_created"},
                    steps=[
                        WorkflowStep("validate_order", "condition",
                                   {"check_availability": True, "validate_payment": True}, ["send_to_kitchen", "cancel_order"]),
                        WorkflowStep("send_to_kitchen", "action",
                                   {"print_ticket": True, "update_status": "in_preparation"}, ["track_preparation"]),
                        WorkflowStep("track_preparation", "action",
                                   {"monitor_time": True, "update_customer": True}, ["ready_for_pickup"]),
                        WorkflowStep("ready_for_pickup", "notification",
                                   {"customer_notification": True, "status": "ready"}, [])
                    ],
                    permissions=["kitchen_staff", "manager"]
                ),
                WorkflowDefinition(
                    name="Inventory Management",
                    description="Automated inventory tracking and reordering",
                    trigger_type="scheduled",
                    trigger_config={"schedule": "daily", "time": "06:00"},
                    steps=[
                        WorkflowStep("check_stock_levels", "condition",
                                   {"compare_minimum": True}, ["generate_reorder_list"]),
                        WorkflowStep("generate_reorder_list", "action",
                                   {"calculate_quantities": True, "group_by_supplier": True}, ["send_orders"]),
                        WorkflowStep("send_orders", "notification",
                                   {"notify_suppliers": True, "manager_approval": True}, [])
                    ],
                    permissions=["inventory_manager", "admin"]
                )
            ],
            ui_components=[
                UIComponent("MenuBoard", "table",
                          {"columns": ["name", "category", "price", "availability"], "actions": ["edit", "toggle"]}, []),
                UIComponent("OrderQueue", "card",
                          {"display": "kanban", "columns": ["pending", "preparing", "ready", "completed"]}, []),
                UIComponent("KitchenDisplay", "dashboard",
                          {"widgets": ["active_orders", "preparation_times", "order_alerts"]}, ["OrderQueue"]),
                UIComponent("POS Terminal", "form",
                          {"sections": ["menu_selection", "order_summary", "payment"]}, ["MenuBoard"]),
                UIComponent("InventoryTracker", "table",
                          {"columns": ["item", "current_stock", "minimum", "status"], "alerts": True}, [])
            ],
            api_endpoints=[
                APIEndpoint("/menu", "GET", "Get menu items",
                          [{"name": "category", "type": "string"}, {"name": "available", "type": "boolean"}],
                          "MenuItemList", ["public"]),
                APIEndpoint("/orders", "POST", "Create new order",
                          [{"name": "order_data", "type": "OrderCreate"}],
                          "OrderResponse", ["customer", "staff"]),
                APIEndpoint("/orders/{id}/status", "PUT", "Update order status",
                          [{"name": "status", "type": "string"}],
                          "OrderResponse", ["kitchen_staff", "manager"]),
                APIEndpoint("/inventory", "GET", "Get inventory levels",
                          [{"name": "category", "type": "string"}, {"name": "low_stock", "type": "boolean"}],
                          "InventoryList", ["inventory_manager"]),
                APIEndpoint("/reports/sales", "GET", "Sales reports",
                          [{"name": "start_date", "type": "datetime"}, {"name": "end_date", "type": "datetime"}],
                          "SalesReport", ["manager", "admin"])
            ],
            database_extensions=[
                "menu_categories", "order_statuses", "payment_methods", "inventory_units"
            ],
            configuration={
                "features": {
                    "online_ordering": True,
                    "table_reservations": True,
                    "loyalty_program": True,
                    "kitchen_display": True,
                    "inventory_tracking": True
                },
                "integrations": {
                    "payment_processors": ["square", "stripe", "toast"],
                    "delivery_services": ["ubereats", "doordash", "grubhub"],
                    "accounting": ["quickbooks", "xero"]
                },
                "operations": {
                    "prep_time_tracking": True,
                    "automatic_86ing": True, # Remove unavailable items
                    "price_scheduling": True,
                    "multi_location": False
                }
            },
            dependencies=["payment_processing", "notification_service", "receipt_printing"]
        )
    
    def get_template(self, template_key: str) -> Optional[DomainTemplate]:
        """Get a specific template by key."""
        return self.templates.get(template_key)
    
    def list_templates(self) -> List[str]:
        """Get list of available template keys."""
        return list(self.templates.keys())
    
    def add_custom_template(self, key: str, template: DomainTemplate):
        """Add a custom template to the registry."""
        self.templates[key] = template
    
    def export_template(self, template_key: str, file_path: Path, format: str = "yaml"):
        """Export a template to file."""
        template = self.get_template(template_key)
        if not template:
            raise ValueError(f"Template {template_key} not found")
        
        data = asdict(template)
        
        if format.lower() == "yaml":
            with open(file_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
        elif format.lower() == "json":
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_template(self, file_path: Path, template_key: str):
        """Import a template from file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")
        
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
        elif file_path.suffix.lower() == '.json':
            with open(file_path, "r") as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Convert dict back to DomainTemplate
        # This would need proper deserialization logic
        # For now, we'll store as dict and convert when needed
        self.templates[template_key] = data


# Global template registry instance
template_registry = TemplateRegistry()


def get_available_templates() -> Dict[str, str]:
    """Get a summary of available templates."""
    templates = {}
    for key, template in template_registry.templates.items():
        templates[key] = template.description
    return templates


def create_custom_template(
    name: str,
    description: str,
    domain_type: str,
    entities: List[Dict],
    workflows: List[Dict] = None,
    ui_components: List[Dict] = None
) -> DomainTemplate:
    """Create a custom domain template."""
    
    # Convert dict entities to EntityDefinition objects
    entity_definitions = []
    for entity_dict in entities:
        fields = [
            EntityField(
                name=field["name"],
                type=field["type"],
                nullable=field.get("nullable", True),
                indexed=field.get("indexed", False),
                unique=field.get("unique", False),
                default=field.get("default"),
                description=field.get("description")
            )
            for field in entity_dict.get("fields", [])
        ]
        
        entity_definitions.append(EntityDefinition(
            name=entity_dict["name"],
            table_name=entity_dict.get("table_name", entity_dict["name"].lower() + "s"),
            description=entity_dict.get("description", ""),
            fields=fields,
            relationships=entity_dict.get("relationships", []),
            indexes=entity_dict.get("indexes", []),
            constraints=entity_dict.get("constraints", [])
        ))
    
    return DomainTemplate(
        name=name,
        description=description,
        domain_type=DomainType(domain_type) if isinstance(domain_type, str) else domain_type,
        version="1.0.0",
        entities=entity_definitions,
        workflows=workflows or [],
        ui_components=ui_components or [],
        api_endpoints=[],
        database_extensions=[],
        configuration={},
        dependencies=[]
    )