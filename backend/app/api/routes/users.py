"""User management API routes."""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.dependencies import (get_current_active_user,
                                   get_current_admin_user)
from app.core.security import get_password_hash
from app.models.user import User, UserStatus
from app.schemas.user import UserCreate, UserList, UserRead, UserUpdate

router = APIRouter()


@router.get("/", response_model=UserList)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of users to return"),
    search: str = Query(None, description="Search by name or email"),
    status_filter: UserStatus = Query(None, description="Filter by user status"),
    current_user: UserRead = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get list of users (admin only)."""

    # Build query
    query = select(User)

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (User.first_name.ilike(search_term))
            | (User.last_name.ilike(search_term))
            | (User.email.ilike(search_term))
        )

    # Apply status filter
    if status_filter:
        query = query.where(User.status == status_filter)

    # Get total count
    count_query = select(func.count(User.id))
    if search:
        search_term = f"%{search}%"
        count_query = count_query.where(
            (User.first_name.ilike(search_term))
            | (User.last_name.ilike(search_term))
            | (User.email.ilike(search_term))
        )
    if status_filter:
        count_query = count_query.where(User.status == status_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination and execute
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()

    return UserList(
        users=[UserRead.model_validate(user) for user in users],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: UserRead = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new user (admin only)."""

    # Check if user already exists
    existing_user = await User.get_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = await User.create(
        db,
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role,
        status=user_data.status or UserStatus.ACTIVE,
        is_verified=True,  # Admin-created users are automatically verified
    )

    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get user by ID."""

    # Users can view their own profile, admins can view any profile
    if user_id != current_user.id and current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    user = await User.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserRead.model_validate(user)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update user information."""

    # Users can update their own profile, admins can update any profile
    if user_id != current_user.id and current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    user = await User.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Build update data
    update_data = {}

    # Basic fields that users can update
    if user_data.first_name is not None:
        update_data["first_name"] = user_data.first_name
    if user_data.last_name is not None:
        update_data["last_name"] = user_data.last_name
    if user_data.bio is not None:
        update_data["bio"] = user_data.bio
    if user_data.avatar_url is not None:
        update_data["avatar_url"] = user_data.avatar_url

    # Admin-only fields
    if current_user.role in ["admin", "super_admin"]:
        if user_data.role is not None:
            update_data["role"] = user_data.role
        if user_data.status is not None:
            update_data["status"] = user_data.status
        if user_data.is_verified is not None:
            update_data["is_verified"] = user_data.is_verified

    # Handle password update
    if user_data.password is not None:
        if user_id != current_user.id and current_user.role not in [
            "admin",
            "super_admin",
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change password for other users",
            )
        update_data["hashed_password"] = get_password_hash(user_data.password)

    # Update user
    updated_user = await user.update(db, **update_data)

    return UserRead.model_validate(updated_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: UserRead = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete user (admin only)."""

    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    user = await User.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await db.delete(user)
    await db.commit()


@router.get("/me/profile", response_model=UserRead)
async def get_my_profile(
    current_user: UserRead = Depends(get_current_active_user),
) -> Any:
    """Get current user's profile (convenience endpoint)."""
    return current_user
