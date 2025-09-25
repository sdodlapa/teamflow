"""
Optimized authentication routes that use direct SQLite access.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.schemas.auth import Token, RefreshToken
from app.schemas.user import UserCreate, UserRead
from app.services.optimized_auth import get_optimized_auth, OptimizedAuthService

# Create router
router = APIRouter()

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/optimized-auth/login")


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    auth_service: OptimizedAuthService = Depends(get_optimized_auth)
) -> Any:
    """
    Register a new user with optimized database access.
    """
    user = await auth_service.register_user(
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        db=db
    )
    
    return user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: OptimizedAuthService = Depends(get_optimized_auth)
) -> Dict[str, str]:
    """
    Get access token using optimized direct database access.
    """
    success, user, error_message = await auth_service.authenticate_user(
        email=form_data.username, 
        password=form_data.password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message or "Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create access and refresh tokens
    access_token = create_access_token(subject=user["email"])
    refresh_token = create_refresh_token(subject=user["email"])
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshToken,
    auth_service: OptimizedAuthService = Depends(get_optimized_auth)
) -> Dict[str, str]:
    """
    Refresh access token using refresh token.
    """
    # Verify refresh token and get user email
    email = auth_service.verify_jwt_token(refresh_data.refresh_token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify user exists
    user = auth_service.get_user_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create new access and refresh tokens
    access_token = create_access_token(subject=email)
    refresh_token = create_refresh_token(subject=email)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# Fast dependency to get the current user
async def get_current_user_fast(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    auth_service: OptimizedAuthService = Depends(get_optimized_auth)
):
    """Get current user from token with optimized auth."""
    user = await auth_service.get_user_from_token(token, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    return user


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user = Depends(get_current_user_fast)
):
    """Get current user information."""
    return current_user