"""
Ultra-minimal auth route that bypasses all SQLAlchemy for critical routes.
This should fix the extreme slowness with SQLite.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, verify_token
from app.schemas.auth import Token, RefreshToken

# Direct SQL connection
import sqlite3

# Create router
router = APIRouter(prefix="/fast-auth", tags=["auth-fast"])

# Direct database access
def get_db_connection():
    """Get SQLite connection directly with performance optimizations."""
    db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    conn = sqlite3.connect(db_path, timeout=5, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    # Add optimizations
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA cache_size = 10000")
    conn.execute("PRAGMA temp_store = MEMORY")
    
    return conn

# Models for direct auth
class UserRegisterFast(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str

# OAuth2 token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/fast-auth/login")

# Register endpoint
@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegisterFast) -> Dict[str, Any]:
    """Register a new user account - ultra fast direct SQL implementation."""
    
    # Get connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT 1 FROM users WHERE email = ?", (user_data.email,))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user
        now = datetime.utcnow().isoformat()
        hashed_password = get_password_hash(user_data.password)
        
        cursor.execute(
            """
            INSERT INTO users (
                email, hashed_password, is_verified, first_name, last_name,
                role, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_data.email, 
                hashed_password, 
                False, 
                user_data.first_name,
                user_data.last_name,
                "user",  # role
                "pending",  # status
                now,
                now
            )
        )
        
        # Get created user ID
        user_id = cursor.lastrowid
        
        # Commit transaction
        conn.commit()
        
        # Return user data
        return {
            "id": user_id,
            "email": user_data.email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name
        }
    
    except Exception as e:
        # Rollback on error
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    finally:
        # Close connection
        conn.close()

# Login endpoint
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    """Login with username and password - ultra fast direct SQL implementation."""
    
    # Get connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        start_time = datetime.now()
        
        # Find user by email
        cursor.execute(
            """
            SELECT id, email, hashed_password, status
            FROM users
            WHERE email = ?
            """,
            (form_data.username,)
        )
        
        user = cursor.fetchone()
        
        # Check if user exists and password is valid
        if not user or not verify_password(form_data.password, user["hashed_password"]):
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if user["status"] in ["suspended", "inactive"]:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is suspended or inactive"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user["email"], 
            expires_delta=access_token_expires
        )
        
        # Create refresh token
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = create_refresh_token(
            subject=user["email"],
            expires_delta=refresh_token_expires
        )
        
        # Update last login timestamp
        now = datetime.utcnow().isoformat()
        cursor.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (now, user["id"])
        )
        
        # Commit transaction
        conn.commit()
        
        # Calculate time
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        print(f"Fast auth login completed in {elapsed_ms:.2f}ms")
        
        # Return token
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        # Handle other errors
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )
    
    finally:
        # Close connection
        conn.close()


@router.post("/refresh", response_model=Token)
def refresh(refresh_data: RefreshToken) -> Dict[str, str]:
    """Refresh access token using refresh token - ultra fast direct SQL implementation."""
    
    try:
        # Verify refresh token
        email = verify_token(refresh_data.refresh_token)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Get connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if user exists
            cursor.execute(
                "SELECT id, email, status FROM users WHERE email = ?", 
                (email,)
            )
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Check if user is active
            if user["status"] in ["suspended", "inactive"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is suspended or inactive",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Create new tokens
            access_token = create_access_token(subject=email)
            refresh_token = create_refresh_token(subject=email)
            
            # Return new tokens
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
            
        finally:
            # Close connection
            conn.close()
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh error: {str(e)}"
        )


# Current user model
class CurrentUserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    status: str
    is_verified: bool
    
    
def get_current_user_from_token(token: str) -> Dict[str, Any]:
    """Get current user from token using direct SQL."""
    # Verify token
    email = verify_token(token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get user by email
        cursor.execute(
            """
            SELECT id, email, first_name, last_name, role, status, is_verified
            FROM users
            WHERE email = ?
            """,
            (email,)
        )
        
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Convert to dict
        return dict(user)
        
    finally:
        # Close connection
        conn.close()


@router.get("/me", response_model=CurrentUserResponse)
def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get current user information - ultra fast direct SQL implementation."""
    return get_current_user_from_token(token)