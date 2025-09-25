"""
Authentication schemas for the TeamFlow API.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """
    JWT token schema.
    """
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    """
    JWT token payload schema.
    """
    sub: Optional[str] = None
    exp: Optional[int] = None


class RefreshToken(BaseModel):
    """
    Refresh token schema for token refresh operations.
    """
    refresh_token: str