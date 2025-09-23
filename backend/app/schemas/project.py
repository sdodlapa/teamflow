"""Project Pydantic schemas for API serialization."""

from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from app.models.project import ProjectStatus, ProjectPriority, ProjectMemberRole


class ProjectBase(BaseModel):
    """Base project schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    organization_id: int
    status: ProjectStatus = Field(default=ProjectStatus.PLANNING)
    priority: ProjectPriority = Field(default=ProjectPriority.MEDIUM)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectUpdate(BaseModel):
    """Schema for updating project information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectMemberBase(BaseModel):
    """Base project member schema."""
    role: ProjectMemberRole = Field(default=ProjectMemberRole.DEVELOPER)


class ProjectMemberCreate(BaseModel):
    """Schema for adding a member to project."""
    user_email: EmailStr
    role: ProjectMemberRole = Field(default=ProjectMemberRole.DEVELOPER)


class ProjectMemberUpdate(BaseModel):
    """Schema for updating project member."""
    role: ProjectMemberRole


class ProjectMemberRead(ProjectMemberBase):
    """Schema for reading project member data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    project_id: int
    joined_at: datetime
    
    # Include user details (will be populated by the API)
    # user: Optional[UserRead] = None


class ProjectRead(ProjectBase):
    """Schema for reading project data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    status: ProjectStatus
    priority: ProjectPriority
    is_active: bool
    start_date: Optional[date]
    end_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    
    # Include member list
    # members: List[ProjectMemberRead] = []


class ProjectList(BaseModel):
    """Schema for paginated project list."""
    projects: List[ProjectRead]
    total: int
    skip: int
    limit: int


# Import after class definitions to avoid circular imports
# from app.schemas.user import UserRead