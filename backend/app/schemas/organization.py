"""Organization Pydantic schemas for API serialization."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from app.models.organization import OrganizationPlan, OrganizationMemberRole


class OrganizationBase(BaseModel):
    """Base organization schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = Field(None, max_length=255)


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""
    plan: OrganizationPlan = Field(default=OrganizationPlan.FREE)


class OrganizationUpdate(BaseModel):
    """Schema for updating organization information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = Field(None, max_length=255)


class OrganizationMemberBase(BaseModel):
    """Base organization member schema."""
    role: OrganizationMemberRole = Field(default=OrganizationMemberRole.MEMBER)


class OrganizationMemberCreate(BaseModel):
    """Schema for adding a member to organization."""
    user_email: EmailStr
    role: OrganizationMemberRole = Field(default=OrganizationMemberRole.MEMBER)


class OrganizationMemberUpdate(BaseModel):
    """Schema for updating organization member."""
    role: OrganizationMemberRole


class OrganizationMemberRead(OrganizationMemberBase):
    """Schema for reading organization member data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    organization_id: int
    joined_at: datetime
    
    # Include user details (will be populated by the API)
    # user: Optional[UserRead] = None


class OrganizationRead(OrganizationBase):
    """Schema for reading organization data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    plan: OrganizationPlan
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Include member list
    # members: List[OrganizationMemberRead] = []


class OrganizationList(BaseModel):
    """Schema for paginated organization list."""
    organizations: List[OrganizationRead]
    total: int
    skip: int
    limit: int


# Import after class definitions to avoid circular imports
# from app.schemas.user import UserRead