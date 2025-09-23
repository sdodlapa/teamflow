"""Organization Pydantic schemas for API serialization."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.models.organization import OrganizationPlan, OrganizationStatus, OrganizationMemberRole


class OrganizationBase(BaseModel):
    """Base organization schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = Field(None, max_length=255)


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""
    slug: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-z0-9-]+$')
    plan: OrganizationPlan = Field(default=OrganizationPlan.FREE)


class OrganizationUpdate(BaseModel):
    """Schema for updating organization information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=255)


class OrganizationRead(OrganizationBase):
    """Schema for reading organization data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    slug: str
    logo_url: Optional[str]
    plan: OrganizationPlan
    status: OrganizationStatus
    max_members: int
    max_projects: int
    created_at: datetime
    updated_at: datetime
    trial_ends_at: Optional[datetime]


class OrganizationMemberBase(BaseModel):
    """Base organization member schema."""
    role: OrganizationMemberRole = Field(default=OrganizationMemberRole.MEMBER)


class OrganizationMemberCreate(OrganizationMemberBase):
    """Schema for adding a member to organization."""
    user_id: int
    organization_id: int


class OrganizationMemberUpdate(BaseModel):
    """Schema for updating organization member."""
    role: Optional[OrganizationMemberRole] = None
    is_active: Optional[bool] = None


class OrganizationMemberRead(OrganizationMemberBase):
    """Schema for reading organization member data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    organization_id: int
    is_active: bool
    joined_at: datetime
    updated_at: datetime


class OrganizationInvite(BaseModel):
    """Schema for inviting users to organization."""
    email: str
    role: OrganizationMemberRole = Field(default=OrganizationMemberRole.MEMBER)
    message: Optional[str] = Field(None, max_length=500)


class OrganizationStats(BaseModel):
    """Schema for organization statistics."""
    total_members: int
    active_members: int
    total_projects: int
    active_projects: int
    completed_projects: int