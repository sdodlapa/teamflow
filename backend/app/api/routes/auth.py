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
                              UserRegister, LoginResponse, LoginResponseUser)

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)) -> Any:
    """Register a new user account using optimized service."""
    from app.services.auth_service import register_user_fast
    
    # Use our new optimized registration service
    user = await register_user_fast(
        db=db,
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    # Return user data
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    from app.services.auth_service import authenticate_user_fast
    
    # Get user with optimized authentication
    user = await authenticate_user_fast(
        db=db, 
        email=form_data.username, 
        password=form_data.password
    )
    
    if not user:
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

    # Update last login (but don't wait for it to complete)
    try:
        # Simply update the timestamp in SQLite directly without waiting
        from app.services.auth_service import get_sqlite_connection
        with get_sqlite_connection() as conn:
            conn.execute(
                "UPDATE users SET last_login_at = ? WHERE id = ?",
                (datetime.utcnow(), user.id)
            )
    except Exception:
        # Ignore login time update failures
        pass

    return Token(access_token=access_token, token_type="bearer")


@router.post("/login/json", response_model=LoginResponse)
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

    # Create user response
    user_data = LoginResponseUser(
        id=str(user.id),
        email=user.email,
        name=f"{user.first_name} {user.last_name}",
        role=user.role.value,
        organizationId=None  # TODO: Get user's primary organization
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=None,  # TODO: Implement refresh tokens
        user=user_data
    )


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
