"""Project management API routes."""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.organization import OrganizationMember
from app.models.project import Project, ProjectMember, ProjectMemberRole
from app.models.user import User
from app.schemas.project import (ProjectCreate, ProjectList,
                                 ProjectMemberCreate, ProjectMemberRead,
                                 ProjectMemberUpdate, ProjectRead,
                                 ProjectUpdate)
from app.schemas.user import UserRead

router = APIRouter()


async def get_project_or_404(
    db: AsyncSession, project_id: int, user_id: int
) -> Project:
    """Get project by ID or raise 404. Verify user has access."""

    # Get project with member info
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.members))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # Check if user is a member or organization member
    is_project_member = any(member.user_id == user_id for member in project.members)

    if not is_project_member:
        # Check if user is a member of the organization
        result = await db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == project.organization_id,
                OrganizationMember.user_id == user_id,
            )
        )
        org_member = result.scalar_one_or_none()

        if not org_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this project",
            )

    return project


async def check_project_admin_permission(
    db: AsyncSession, project_id: int, user_id: int
) -> ProjectMember:
    """Check if user has admin permission in project."""

    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role.in_([ProjectMemberRole.ADMIN, ProjectMemberRole.OWNER]),
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions in project",
        )

    return member


@router.get("/", response_model=ProjectList)
async def list_my_projects(
    skip: int = Query(0, ge=0, description="Number of projects to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of projects to return"),
    organization_id: int = Query(None, description="Filter by organization ID"),
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get list of projects for current user."""

    # Base query: projects where user is a member
    query = (
        select(Project)
        .join(ProjectMember)
        .where(ProjectMember.user_id == current_user.id)
        .options(selectinload(Project.members))
    )

    count_query = (
        select(func.count(Project.id))
        .join(ProjectMember)
        .where(ProjectMember.user_id == current_user.id)
    )

    # Filter by organization if specified
    if organization_id:
        # Verify user is member of organization
        result = await db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == current_user.id,
            )
        )
        org_member = result.scalar_one_or_none()

        if not org_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of specified organization",
            )

        query = query.where(Project.organization_id == organization_id)
        count_query = count_query.where(Project.organization_id == organization_id)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(Project.created_at.desc())
    result = await db.execute(query)
    projects = result.scalars().all()

    return ProjectList(
        projects=[ProjectRead.model_validate(project) for project in projects],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new project."""

    # Verify user is member of organization
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == project_data.organization_id,
            OrganizationMember.user_id == current_user.id,
        )
    )
    org_member = result.scalar_one_or_none()

    if not org_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create projects in this organization",
        )

    # Create project
    project = Project(
        name=project_data.name,
        description=project_data.description,
        organization_id=project_data.organization_id,
        status=project_data.status,
        priority=project_data.priority,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        is_active=True,
    )
    db.add(project)
    await db.flush()  # Get the ID

    # Add creator as owner
    member = ProjectMember(
        project_id=project.id, user_id=current_user.id, role=ProjectMemberRole.OWNER
    )
    db.add(member)

    await db.commit()
    await db.refresh(project)

    # Load with members for response
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.members))
        .where(Project.id == project.id)
    )
    project_with_members = result.scalar_one()

    return ProjectRead.model_validate(project_with_members)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get project by ID."""

    project = await get_project_or_404(db, project_id, current_user.id)
    return ProjectRead.model_validate(project)


@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update project (admin/owner only)."""

    # Check permissions
    await check_project_admin_permission(db, project_id, current_user.id)

    # Get project
    project = await get_project_or_404(db, project_id, current_user.id)

    # Update fields
    update_data = project_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    await db.commit()
    await db.refresh(project)

    # Reload with members
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.members))
        .where(Project.id == project_id)
    )
    project_with_members = result.scalar_one()

    return ProjectRead.model_validate(project_with_members)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete project (owner only)."""

    # Check if user is owner
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
            ProjectMember.role == ProjectMemberRole.OWNER,
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owners can delete projects",
        )

    # Get project
    project = await get_project_or_404(db, project_id, current_user.id)

    # Delete project (cascade will handle members)
    await db.delete(project)
    await db.commit()


@router.get("/{project_id}/members", response_model=List[ProjectMemberRead])
async def list_project_members(
    project_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get list of project members."""

    # Verify access to project
    await get_project_or_404(db, project_id, current_user.id)

    # Get members with user info
    result = await db.execute(
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(ProjectMember.project_id == project_id)
        .order_by(ProjectMember.joined_at.asc())
    )
    members = result.scalars().all()

    return [ProjectMemberRead.model_validate(member) for member in members]


@router.post("/{project_id}/members", response_model=ProjectMemberRead)
async def add_project_member(
    project_id: int,
    member_data: ProjectMemberCreate,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Add member to project (admin/owner only)."""

    # Check permissions
    await check_project_admin_permission(db, project_id, current_user.id)

    # Verify project exists
    project = await get_project_or_404(db, project_id, current_user.id)

    # Check if user exists
    user = await User.get_by_email(db, email=member_data.user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Verify user is member of organization
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == project.organization_id,
            OrganizationMember.user_id == user.id,
        )
    )
    org_member = result.scalar_one_or_none()

    if not org_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be a member of the organization first",
        )

    # Check if already a project member
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user.id
        )
    )
    existing_member = result.scalar_one_or_none()

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this project",
        )

    # Add member
    member = ProjectMember(
        project_id=project_id, user_id=user.id, role=member_data.role
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)

    # Load with user info
    result = await db.execute(
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(ProjectMember.id == member.id)
    )
    member_with_user = result.scalar_one()

    return ProjectMemberRead.model_validate(member_with_user)


@router.put("/{project_id}/members/{member_id}", response_model=ProjectMemberRead)
async def update_project_member(
    project_id: int,
    member_id: int,
    member_data: ProjectMemberUpdate,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update project member role (admin/owner only)."""

    # Check permissions
    await check_project_admin_permission(db, project_id, current_user.id)

    # Get member
    result = await db.execute(
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(ProjectMember.id == member_id, ProjectMember.project_id == project_id)
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
        )

    # Update role
    member.role = member_data.role
    await db.commit()
    await db.refresh(member)

    return ProjectMemberRead.model_validate(member)


@router.delete(
    "/{project_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_project_member(
    project_id: int,
    member_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove member from project (admin/owner only)."""

    # Check permissions
    await check_project_admin_permission(db, project_id, current_user.id)

    # Get member
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.id == member_id, ProjectMember.project_id == project_id
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
        )

    # Prevent removing self if owner
    if member.user_id == current_user.id and member.role == ProjectMemberRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project owners cannot remove themselves",
        )

    await db.delete(member)
    await db.commit()
