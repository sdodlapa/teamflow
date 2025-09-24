"""
Test Real Estate Domain Configuration
For testing Section 3: Code Generation Engine
"""

from app.core.domain_config import (
    DomainConfig, EntityConfig, FieldConfig, RelationshipConfig, 
    EnumOption, ValidationRule, PermissionConfig, SortConfig,
    FieldType, RelationshipType
)


def create_real_estate_simple_domain() -> DomainConfig:
    """Create a simple real estate domain configuration for testing."""
    
    # Property Status Enum Options
    property_status_options = [
        EnumOption(value="available", label="Available", description="Property is available for sale/rent"),
        EnumOption(value="pending", label="Pending", description="Property sale/rent is pending"),
        EnumOption(value="sold", label="Sold", description="Property has been sold"),
        EnumOption(value="rented", label="Rented", description="Property has been rented"),
        EnumOption(value="withdrawn", label="Withdrawn", description="Property removed from market")
    ]
    
    # Property Type Enum Options  
    property_type_options = [
        EnumOption(value="house", label="House", description="Single family house"),
        EnumOption(value="apartment", label="Apartment", description="Apartment/condo unit"),
        EnumOption(value="condo", label="Condominium", description="Condominium unit"),
        EnumOption(value="townhouse", label="Townhouse", description="Townhouse"),
        EnumOption(value="land", label="Land", description="Vacant land")
    ]
    
    # Property Entity
    property_entity = EntityConfig(
        name="Property",
        description="Real estate property listing",
        fields=[
            FieldConfig(
                name="title",
                type=FieldType.STRING,
                required=True,
                max_length=200,
                description="Property title/headline"
            ),
            FieldConfig(
                name="description",
                type=FieldType.TEXT,
                description="Detailed property description"
            ),
            FieldConfig(
                name="address",
                type=FieldType.STRING,
                required=True,
                max_length=300,
                description="Property address"
            ),
            FieldConfig(
                name="city",
                type=FieldType.STRING,
                required=True,
                max_length=100,
                description="City"
            ),
            FieldConfig(
                name="state",
                type=FieldType.STRING,
                required=True,
                max_length=50,
                description="State/Province"
            ),
            FieldConfig(
                name="zip_code",
                type=FieldType.STRING,
                required=True,
                max_length=20,
                description="Postal/ZIP code"
            ),
            FieldConfig(
                name="property_type",
                type=FieldType.ENUM,
                required=True,
                options=property_type_options,
                description="Type of property"
            ),
            FieldConfig(
                name="status",
                type=FieldType.ENUM,
                required=True,
                default="available",
                options=property_status_options,
                description="Current status of property"
            ),
            FieldConfig(
                name="price",
                type=FieldType.DECIMAL,
                required=True,
                description="Property price",
                validations=[
                    ValidationRule(type="range", field="price", min=0, message="Price must be positive")
                ]
            ),
            FieldConfig(
                name="bedrooms",
                type=FieldType.INTEGER,
                description="Number of bedrooms",
                validations=[
                    ValidationRule(type="range", field="bedrooms", min=0, max=20)
                ]
            ),
            FieldConfig(
                name="bathrooms",
                type=FieldType.DECIMAL,
                description="Number of bathrooms"
            ),
            FieldConfig(
                name="square_feet",
                type=FieldType.INTEGER,
                description="Total square footage",
                validations=[
                    ValidationRule(type="range", field="square_feet", min=1)
                ]
            ),
            FieldConfig(
                name="lot_size",
                type=FieldType.DECIMAL,
                description="Lot size in acres"
            ),
            FieldConfig(
                name="year_built",
                type=FieldType.INTEGER,
                description="Year property was built",
                validations=[
                    ValidationRule(type="range", field="year_built", min=1800, max=2030)
                ]
            ),
            FieldConfig(
                name="listing_date",
                type=FieldType.DATE,
                required=True,
                description="Date property was listed"
            ),
            FieldConfig(
                name="is_featured",
                type=FieldType.BOOLEAN,
                default=False,
                description="Whether property is featured"
            )
        ],
        relationships=[
            RelationshipConfig(
                name="agent",
                target="Agent", 
                type=RelationshipType.MANY_TO_ONE,
                required=True,
                description="Real estate agent handling the property"
            ),
            RelationshipConfig(
                name="inquiries",
                target="Inquiry",
                type=RelationshipType.ONE_TO_MANY,
                description="Customer inquiries for this property"
            )
        ],
        display_field="title",
        soft_delete=True,
        bulk_operations=True,
        required_on_create=["title", "address", "city", "state", "zip_code", "property_type", "price", "listing_date"],
        unique_constraints=[["address", "city", "state", "zip_code"]],
        permissions=PermissionConfig(
            read="property.read",
            create="property.create", 
            update="property.update",
            delete="property.delete"
        ),
        default_sort=SortConfig(field="listing_date", direction="desc")
    )
    
    # Set filterable and searchable fields
    property_entity.filterable_fields = [
        f for f in property_entity.fields 
        if f.name in ["property_type", "status", "city", "state", "is_featured"]
    ]
    property_entity.searchable_fields = [
        f for f in property_entity.fields 
        if f.name in ["title", "description", "address", "city"]
    ]
    
    # Agent Entity
    agent_entity = EntityConfig(
        name="Agent",
        description="Real estate agent/broker",
        fields=[
            FieldConfig(
                name="first_name",
                type=FieldType.STRING,
                required=True,
                max_length=100,
                description="Agent first name"
            ),
            FieldConfig(
                name="last_name",
                type=FieldType.STRING,
                required=True,
                max_length=100,
                description="Agent last name"
            ),
            FieldConfig(
                name="email",
                type=FieldType.EMAIL,
                required=True,
                unique=True,
                description="Agent email address",
                validations=[
                    ValidationRule(type="email", field="email")
                ]
            ),
            FieldConfig(
                name="phone",
                type=FieldType.PHONE,
                required=True,
                description="Agent phone number",
                validations=[
                    ValidationRule(type="phone", field="phone")
                ]
            ),
            FieldConfig(
                name="license_number",
                type=FieldType.STRING,
                required=True,
                unique=True,
                max_length=50,
                description="Real estate license number"
            ),
            FieldConfig(
                name="bio",
                type=FieldType.TEXT,
                description="Agent biography"
            ),
            FieldConfig(
                name="is_active",
                type=FieldType.BOOLEAN,
                default=True,
                description="Whether agent is currently active"
            )
        ],
        relationships=[
            RelationshipConfig(
                name="properties",
                target="Property",
                type=RelationshipType.ONE_TO_MANY,
                description="Properties handled by this agent"
            )
        ],
        display_field="email",
        soft_delete=True,
        unique_constraints=[["email"], ["license_number"]],
        default_sort=SortConfig(field="last_name", direction="asc")
    )
    
    # Set filterable and searchable fields for agent
    agent_entity.filterable_fields = [
        f for f in agent_entity.fields 
        if f.name in ["is_active"]
    ]
    agent_entity.searchable_fields = [
        f for f in agent_entity.fields 
        if f.name in ["first_name", "last_name", "email", "phone"]
    ]
    
    # Create domain configuration
    domain = DomainConfig(
        name="real_estate_simple",
        description="Simple real estate management domain for testing code generation",
        entities=[property_entity, agent_entity],
        api_prefix="/api/v1",
        enable_audit=True,
        enable_cache=False
    )
    
    return domain


# Create and export the domain configuration
real_estate_domain = create_real_estate_simple_domain()