"""
Property Model
Generated on: 2025-09-24
Domain: real_estate_simple
"""

from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, Time, Text, Numeric, JSON, ForeignKey, UUID, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


# Enum definitions
class PropertyTypeEnum(enum.Enum):
    """Type of property enumeration."""
    HOUSE = "house"
    APARTMENT = "apartment"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    LAND = "land"


class StatusEnum(enum.Enum):
    """Current status of property enumeration."""
    AVAILABLE = "available"
    PENDING = "pending"
    SOLD = "sold"
    RENTED = "rented"
    WITHDRAWN = "withdrawn"


class Property(BaseModel):
    """
    Real estate property listing model.
    
    Real estate property listing
    
    Fields:
    - title: FieldType.STRING (required) - Property title/headline    - description: FieldType.TEXT - Detailed property description    - address: FieldType.STRING (required) - Property address    - city: FieldType.STRING (required) - City    - state: FieldType.STRING (required) - State/Province    - zip_code: FieldType.STRING (required) - Postal/ZIP code    - property_type: FieldType.ENUM (required) - Type of property    - status: FieldType.ENUM (required) - Current status of property    - price: FieldType.DECIMAL (required) - Property price    - bedrooms: FieldType.INTEGER - Number of bedrooms    - bathrooms: FieldType.DECIMAL - Number of bathrooms    - square_feet: FieldType.INTEGER - Total square footage    - lot_size: FieldType.DECIMAL - Lot size in acres    - year_built: FieldType.INTEGER - Year property was built    - listing_date: FieldType.DATE (required) - Date property was listed    - is_featured: FieldType.BOOLEAN - Whether property is featured    
    Relationships:
    - agent: RelationshipType.MANY_TO_ONE to Agent - Real estate agent handling the property    - inquiries: RelationshipType.ONE_TO_MANY to Inquiry - Customer inquiries for this property    """
    
    __tablename__ = "properties"
    
    # Fields
    title = Column(String(200), nullable=False)
    # Property title/headline
    description = Column(Text, nullable=True)
    # Detailed property description
    address = Column(String(300), nullable=False)
    # Property address
    city = Column(String(100), nullable=False)
    # City
    state = Column(String(50), nullable=False)
    # State/Province
    zip_code = Column(String(20), nullable=False)
    # Postal/ZIP code
    property_type = Column(Enum(PropertyTypeEnum), nullable=False)
    # Type of property
    status = Column(Enum(StatusEnum), nullable=False, default=available)
    # Current status of property
    price = Column(Numeric, nullable=False)
    # Property price
    bedrooms = Column(Integer, nullable=True)
    # Number of bedrooms
    bathrooms = Column(Numeric, nullable=True)
    # Number of bathrooms
    square_feet = Column(Integer, nullable=True)
    # Total square footage
    lot_size = Column(Numeric, nullable=True)
    # Lot size in acres
    year_built = Column(Integer, nullable=True)
    # Year property was built
    listing_date = Column(Date, nullable=False)
    # Date property was listed
    is_featured = Column(Boolean, nullable=True)
    # Whether property is featured
    
    # Relationships
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    agent = relationship("Agent", back_populates="properties")
    # Real estate agent handling the property
    inquiries = relationship("Inquiry", back_populates="property")
    # Customer inquiries for this property
    
    def __repr__(self) -> str:
        """String representation of Property."""
        return f"<Property(id={self.id}, title={getattr(self, 'title', 'N/A')})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "property_type": self.property_type.value if self.property_type else None,
            "status": self.status.value if self.status else None,
            "price": float(self.price) if self.price else None,
            "bedrooms": self.bedrooms,
            "bathrooms": float(self.bathrooms) if self.bathrooms else None,
            "square_feet": self.square_feet,
            "lot_size": float(self.lot_size) if self.lot_size else None,
            "year_built": self.year_built,
            "listing_date": self.listing_date.isoformat() if self.listing_date else None,
            "is_featured": self.is_featured,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }