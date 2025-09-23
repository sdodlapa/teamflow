"""Organization management API routes."""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.organization import Organization, OrganizationMember, OrganizationMemberRole
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
    OrganizationList,
    OrganizationMemberRead,
    OrganizationMemberCreate,
    OrganizationMemberUpdate,
)
from app.schemas.user import UserRead

router = APIRouter()


async def get_organization_or_404(
    db: AsyncSession, org_id: int, user_id: int
) -> Organization:
    """Get organization by ID or raise 404. Verify user has access."""
    
    # Get organization with member info
    result = await db.execute(
        select(Organization)
        .options(selectinload(Organization.members))
        .where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Check if user is a member
    is_member = any(member.user_id == user_id for member in org.members)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization"
        )
    
    return org


async def check_admin_permission(
    db: AsyncSession, org_id: int, user_id: int
) -> OrganizationMember:
    """Check if user has admin permission in organization."""
    
    result = await db.execute(
        select(OrganizationMember)
        .where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id,
            OrganizationMember.role.in_([OrganizationMemberRole.ADMIN, OrganizationMemberRole.OWNER])
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions in organization"
        )
    
    return member


@router.get("/", response_model=OrganizationList)
async def list_my_organizations(
    skip: int = Query(0, ge=0, description="Number of organizations to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of organizations to return"),
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get list of organizations for current user."""
    
    # Get organizations where user is a member
    query = (
        select(Organization)
        .join(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .options(selectinload(Organization.members))
    )
    
    # Get total count
    count_query = (
        select(func.count(Organization.id))
        .join(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
    )
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(Organization.created_at.desc())
    result = await db.execute(query)
    organizations = result.scalars().all()
    
    return OrganizationList(
        organizations=[OrganizationRead.model_validate(org) for org in organizations],
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("/", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new organization."""
    
    # Create organization
    org = Organization(
        name=org_data.name,
        description=org_data.description,
        website=org_data.website,
        plan=org_data.plan,
        is_active=True
    )
    db.add(org)
    await db.flush()  # Get the ID
    
    # Add creator as owner
    member = OrganizationMember(
        organization_id=org.id,
        user_id=current_user.id,
        role=OrganizationMemberRole.OWNER
    )
    db.add(member)
    
    await db.commit()
    await db.refresh(org)
    
    # Load with members for response
    result = await db.execute(
        select(Organization)
        .options(selectinload(Organization.members))
        .where(Organization.id == org.id)
    )
    org_with_members = result.scalar_one()
    
    return OrganizationRead.model_validate(org_with_members)


@router.get("/{org_id}", response_model=OrganizationRead)
async def get_organization(
    org_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get organization by ID."""
    
    org = await get_organization_or_404(db, org_id, current_user.id)
    return OrganizationRead.model_validate(org)


@router.put("/{org_id}", response_model=OrganizationRead)
async def update_organization(
    org_id: int,
    org_data: OrganizationUpdate,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update organization (admin/owner only)."""
    
    # Check permissions
    await check_admin_permission(db, org_id, current_user.id)
    
    # Get organization
    org = await get_organization_or_404(db, org_id, current_user.id)
    
    # Update fields
    update_data = org_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(org, key, value)
    
    await db.commit()
    await db.refresh(org)
    
    # Reload with members
    result = await db.execute(
        select(Organization)
        .options(selectinload(Organization.members))
        .where(Organization.id == org_id)
    )
    org_with_members = result.scalar_one()
    
    return OrganizationRead.model_validate(org_with_members)


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete organization (owner only)."""
    
    # Check if user is owner
    result = await db.execute(
        select(OrganizationMember)
        .where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == current_user.id,
            OrganizationMember.role == OrganizationMemberRole.OWNER
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owners can delete organizations"
        )
    
    # Get organization
    org = await get_organization_or_404(db, org_id, current_user.id)
    
    # Delete organization (cascade will handle members)
    await db.delete(org)
    await db.commit()


@router.get("/{org_id}/members", response_model=List[OrganizationMemberRead])
async def list_organization_members(
    org_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get list of organization members."""
    
    # Verify access to organization
    await get_organization_or_404(db, org_id, current_user.id)
    
    # Get members with user info
    result = await db.execute(
        select(OrganizationMember)
        .options(selectinload(OrganizationMember.user))
        .where(OrganizationMember.organization_id == org_id)
        .order_by(OrganizationMember.joined_at.asc())
    )
    members = result.scalars().all()
    
    return [OrganizationMemberRead.model_validate(member) for member in members]


@router.post("/{org_id}/members", response_model=OrganizationMemberRead)
async def add_organization_member(
    org_id: int,
    member_data: OrganizationMemberCreate,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Add member to organization (admin/owner only)."""
    
    # Check permissions
    await check_admin_permission(db, org_id, current_user.id)
    
    # Verify organization exists
    await get_organization_or_404(db, org_id, current_user.id)
    
    # Check if user exists
    user = await User.get_by_email(db, email=member_data.user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already a member
    result = await db.execute(
        select(OrganizationMember)
        .where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user.id
        )
    )
    existing_member = result.scalar_one_or_none()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this organization"
        )
    
    # Add member
    member = OrganizationMember(
        organization_id=org_id,
        user_id=user.id,
        role=member_data.role
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    
    # Load with user info
    result = await db.execute(
        select(OrganizationMember)
        .options(selectinload(OrganizationMember.user))
        .where(OrganizationMember.id == member.id)
    )
    member_with_user = result.scalar_one()
    
    return OrganizationMemberRead.model_validate(member_with_user)


@router.put("/{org_id}/members/{member_id}", response_model=OrganizationMemberRead)
async def update_organization_member(
    org_id: int,
    member_id: int,
    member_data: OrganizationMemberUpdate,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update organization member role (admin/owner only)."""
    
    # Check permissions
    await check_admin_permission(db, org_id, current_user.id)
    
    # Get member
    result = await db.execute(
        select(OrganizationMember)
        .options(selectinload(OrganizationMember.user))
        .where(
            OrganizationMember.id == member_id,
            OrganizationMember.organization_id == org_id
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Update role
    member.role = member_data.role
    await db.commit()
    await db.refresh(member)
    
    return OrganizationMemberRead.model_validate(member)


@router.delete("/{org_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_organization_member(
    org_id: int,
    member_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Remove member from organization (admin/owner only)."""
    
    # Check permissions
    await check_admin_permission(db, org_id, current_user.id)
    
    # Get member
    result = await db.execute(
        select(OrganizationMember)
        .where(
            OrganizationMember.id == member_id,
            OrganizationMember.organization_id == org_id
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Prevent removing self if owner
    if member.user_id == current_user.id and member.role == OrganizationMemberRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization owners cannot remove themselves"
        )
    
    await db.delete(member)
    await db.commit()