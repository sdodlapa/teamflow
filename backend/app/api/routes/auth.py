"""Authentication API routes."""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.security import (create_access_token, get_password_hash,
                               verify_password)
from app.models.user import User, UserStatus
from app.schemas.user import (Token, UserLogin, UserRead,
                              UserRegister)

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)) -> Any:
    """Register a new user account."""

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
        status=UserStatus.PENDING,  # Require email verification
    )

    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""

    # Get user
    user = await User.get_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if user is active
    if user.status in [UserStatus.SUSPENDED, UserStatus.INACTIVE]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is suspended or inactive"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )

    # Update last login (handle concurrent access gracefully)
    try:
        await user.update(db, last_login_at=user.updated_at)
    except Exception:
        # Ignore login time update failures to prevent concurrent access issues
        pass

    return Token(access_token=access_token, token_type="bearer")


@router.post("/login/json", response_model=Token)
async def login_json(user_data: UserLogin, db: AsyncSession = Depends(get_db)) -> Any:
    """JSON login, get an access token for future requests."""

    # Get user
    user = await User.get_by_email(db, email=user_data.email)
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if user is active
    if user.status in [UserStatus.SUSPENDED, UserStatus.INACTIVE]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is suspended or inactive"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )

    # Update last login (handle concurrent access gracefully)
    try:
        await user.update(db, last_login_at=user.updated_at)
    except Exception:
        # Ignore login time update failures to prevent concurrent access issues
        pass

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: UserRead = Depends(get_current_active_user),
) -> Any:
    """Get current authenticated user information."""
    return current_user


@router.post("/verify-token", response_model=UserRead)
async def verify_token(
    current_user: UserRead = Depends(get_current_active_user),
) -> Any:
    """Verify token and return user info (for frontend auth checks)."""
    return current_user
