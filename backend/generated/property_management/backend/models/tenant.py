"""
Tenant Model
Generated on: 2025-09-25
Domain: property_management
"""

from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, Time, Text, Numeric, JSON, ForeignKey, UUID, Enum
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Tenant(BaseModel):
    """
    Property tenants and renters model.
    
    Property tenants and renters
    
    Fields:
    - first_name: FieldType.STRING (required)    - last_name: FieldType.STRING (required)    - email: FieldType.STRING (required)    - phone: FieldType.STRING    - lease_start: FieldType.DATE    - lease_end: FieldType.DATE    - monthly_rent: FieldType.INTEGER (required) - Monthly rent in cents    - security_deposit: FieldType.INTEGER - Security deposit in cents    
    """
    
    __tablename__ = "tenants"
    
    # Fields
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    lease_start = Column(Date, nullable=True)
    lease_end = Column(Date, nullable=True)
    monthly_rent = Column(Integer, nullable=False)
    # Monthly rent in cents
    security_deposit = Column(Integer, nullable=True)
    # Security deposit in cents
    
    
    def __repr__(self) -> str:
        """String representation of Tenant."""
        return f"<Tenant(id={self.id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "lease_start": self.lease_start.isoformat() if self.lease_start else None,
            "lease_end": self.lease_end.isoformat() if self.lease_end else None,
            "monthly_rent": self.monthly_rent,
            "security_deposit": self.security_deposit,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }