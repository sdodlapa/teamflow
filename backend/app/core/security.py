"""
Security utilities for authentication and authorization.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Union

from fastapi import Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """Create a JWT access token."""
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "iat": now, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    if not password:
        raise ValueError("Password cannot be empty")
    return pwd_context.hash(password)


def verify_token(token: str) -> Union[str, None]:
    """Verify JWT token and return subject if valid."""
    if not token:
        return None

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload.get("sub")
    except jwt.JWTError:
        return None


# Import dependencies functions for easier access
def get_current_user():
    """Import get_current_user from dependencies."""
    from app.core.dependencies import get_current_user as _get_current_user
    return _get_current_user


def require_admin():
    """Import admin requirement from dependencies.""" 
    from app.core.dependencies import get_current_admin_user
    return get_current_admin_user
