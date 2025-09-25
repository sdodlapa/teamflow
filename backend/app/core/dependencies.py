"""
Authentication dependencies for FastAPI endpoints.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.schemas.user import UserRead

# HTTP Bearer token security that returns 401 instead of 403
class HTTPBearerAuth(HTTPBearer):
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        try:
            return await super().__call__(request)
        except HTTPException as e:
            if e.status_code == 403:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            raise

security = HTTPBearerAuth()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Get current authenticated user from JWT token."""
    from app.services.auth_service import get_user_by_email_sync
    from sqlalchemy import select

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify token
    user_email = verify_token(credentials.credentials)
    if user_email is None:
        raise credentials_exception

    # Get user from database using direct SQLite access (much faster)
    user_dict = get_user_by_email_sync(email=user_email)
    if not user_dict:
        raise credentials_exception
        
    # If needed elsewhere in the app, get the full User object
    result = await db.execute(select(User).where(User.id == user_dict["id"]))
    user = result.scalar_one_or_none()
    if not user:
        raise credentials_exception

    return UserRead.model_validate(user)


async def get_current_active_user(
    current_user: UserRead = Depends(get_current_user),
) -> UserRead:
    """Get current active user (not suspended)."""
    from app.models.user import UserStatus

    if current_user.status == UserStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Suspended user"
        )

    return current_user


async def get_current_admin_user(
    current_user: UserRead = Depends(get_current_active_user),
) -> UserRead:
    """Get current user if they have admin privileges."""
    from app.models.user import UserRole

    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return current_user


# Optional authentication (user may or may not be authenticated)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db),
) -> Optional[UserRead]:
    """Get current user if authenticated, None otherwise."""

    if not credentials:
        return None

    try:
        user_email = verify_token(credentials.credentials)
        if user_email is None:
            return None

        user = await User.get_by_email(db, email=user_email)
        if user is None:
            return None

        return UserRead.model_validate(user)
    except Exception:
        return None
