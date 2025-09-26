"""
Tenant Pydantic Schemas
Generated on: 2025-09-25
Domain: property_management
"""

from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid

from pydantic import BaseModel, Field, ConfigDict, validator, field_validator
from pydantic.types import UUID4


# Base schema (shared fields)
class TenantBase(BaseModel):
    """Base schema for Tenant with common fields."""
    
    first_name: str    last_name: str    email: str    phone: Optional[str] = None    lease_start: Optional[date] = None    lease_end: Optional[date] = None    monthly_rent: int    # Monthly rent in cents
    security_deposit: Optional[int] = None    # Security deposit in cents
    
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
    


# Schema for creating Tenant
class TenantCreate(TenantBase):
    """Schema for creating a new Tenant."""
    
    pass


# Schema for updating Tenant
class TenantUpdate(BaseModel):
    """Schema for updating an existing Tenant."""
    
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    lease_start: Optional[date] = None
    lease_end: Optional[date] = None
    monthly_rent: Optional[int] = None
    security_deposit: Optional[int] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )


# Schema for Tenant response (includes ID and timestamps)
class TenantResponse(TenantBase):
    """Schema for Tenant response with ID and timestamps."""
    
    id: UUID4
    created_at: datetime
    updated_at: datetime
    


# Schema for listing Tenants
class TenantList(BaseModel):
    """Schema for paginated list of Tenants."""
    
    items: List[TenantResponse]
    total: int
    page: int = 1
    size: int = 20
    pages: int
    
    model_config = ConfigDict(from_attributes=True)


