"""User Pydantic schemas for API serialization."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    timezone: str = Field(default="UTC", max_length=50)
    language: str = Field(default="en", max_length=10)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = Field(default=UserRole.MEMBER)


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    avatar_url: Optional[str] = Field(None, max_length=255)


class UserRead(UserBase):
    """Schema for reading user data (public view)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    full_name: Optional[str]
    avatar_url: Optional[str]
    role: UserRole
    status: UserStatus
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    
    @property
    def display_name(self) -> str:
        """Get the user's display name."""
        if self.full_name:
            return self.full_name
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(UserRead):
    """Extended user schema for profile view (private view)."""
    # Add any private fields here if needed
    pass


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserRegister(UserCreate):
    """Schema for user registration."""
    confirm_password: str
    
    def validate_passwords_match(self) -> None:
        """Validate that password and confirm_password match."""
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")


class Token(BaseModel):
    """Schema for authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Schema for token data."""
    user_id: Optional[int] = None
    email: Optional[str] = None


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str
    
    def validate_passwords_match(self) -> None:
        """Validate that password and confirm_password match."""
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")


class ChangePassword(BaseModel):
    """Schema for changing password."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str
    
    def validate_passwords_match(self) -> None:
        """Validate that password and confirm_password match."""
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")