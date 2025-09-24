"""
Property Pydantic Schemas
Generated on: 2025-09-24
Domain: real_estate_simple
"""

from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, validator, field_validator
from pydantic.types import UUID4


# Enum definitions
class PropertyTypeEnum(str, Enum):
    """Type of property enumeration."""
    HOUSE = "house"
    APARTMENT = "apartment"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    LAND = "land"


class StatusEnum(str, Enum):
    """Current status of property enumeration."""
    AVAILABLE = "available"
    PENDING = "pending"
    SOLD = "sold"
    RENTED = "rented"
    WITHDRAWN = "withdrawn"


# Base schema (shared fields)
class PropertyBase(BaseModel):
    """Base schema for Property with common fields."""
    
    title: str    # Property title/headline
    description: Optional[str] = None    # Detailed property description
    address: str    # Property address
    city: str    # City
    state: str    # State/Province
    zip_code: str    # Postal/ZIP code
    property_type: PropertyTypeEnum    # Type of property
    status: StatusEnum = StatusEnum.AVAILABLE    # Current status of property
    price: Decimal    # Property price
    bedrooms: Optional[int] = None    # Number of bedrooms
    bathrooms: Optional[Decimal] = None    # Number of bathrooms
    square_feet: Optional[int] = None    # Total square footage
    lot_size: Optional[Decimal] = None    # Lot size in acres
    year_built: Optional[int] = None    # Year property was built
    listing_date: date    # Date property was listed
    is_featured: Optional[bool] = None    # Whether property is featured
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            time: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
        }
    )
    
    # Field validators
    @field_validator('price')
    @classmethod
    def validate_price_range(cls, v):
        """Validate price is within range."""
        if v is not None:
        return v
    
    @field_validator('bedrooms')
    @classmethod
    def validate_bedrooms_range(cls, v):
        """Validate bedrooms is within range."""
        if v is not None:
            if v > 20:
                raise ValueError('bedrooms must be at most 20')
        return v
    
    @field_validator('square_feet')
    @classmethod
    def validate_square_feet_range(cls, v):
        """Validate square_feet is within range."""
        if v is not None:
            if v < 1:
                raise ValueError('square_feet must be at least 1')
        return v
    
    @field_validator('year_built')
    @classmethod
    def validate_year_built_range(cls, v):
        """Validate year_built is within range."""
        if v is not None:
            if v < 1800:
                raise ValueError('year_built must be at least 1800')
            if v > 2030:
                raise ValueError('year_built must be at most 2030')
        return v
    


# Schema for creating Property
class PropertyCreate(PropertyBase):
    """Schema for creating a new Property."""
    
    # Override fields that are required on creation
    title: str
    address: str
    city: str
    state: str
    zip_code: str
    property_type: str
    price: str
    listing_date: str
    pass


# Schema for updating Property
class PropertyUpdate(BaseModel):
    """Schema for updating an existing Property."""
    
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    property_type: Optional[PropertyTypeEnum] = None
    status: Optional[StatusEnum] = None
    price: Optional[Decimal] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[Decimal] = None
    square_feet: Optional[int] = None
    lot_size: Optional[Decimal] = None
    year_built: Optional[int] = None
    listing_date: Optional[date] = None
    is_featured: Optional[bool] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )


# Schema for Property response (includes ID and timestamps)
class PropertyResponse(PropertyBase):
    """Schema for Property response with ID and timestamps."""
    
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    # Optional relationship fields (for expansion)
    agent: Optional["AgentResponse"] = None
    inquiries: Optional[List["InquiryResponse"]] = None


# Schema for listing Properties
class PropertyList(BaseModel):
    """Schema for paginated list of Properties."""
    
    items: List[PropertyResponse]
    total: int
    page: int = 1
    size: int = 20
    pages: int
    
    model_config = ConfigDict(from_attributes=True)


# Update forward references for relationships
AgentResponse.model_rebuild()
InquiryResponse.model_rebuild()
