"""
OptimizedAuthService - Direct SQLite implementation for critical authentication operations.
"""

import os
import time
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

from app.services.db_performance import time_query

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.database import get_db
from app.models.user import User, UserStatus, UserRole
from app.schemas.user import UserRead

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("optimized_auth")


class OptimizedAuthService:
    """
    Optimized authentication service that uses direct SQLite access
    for performance-critical operations.
    """
    
    def __init__(self):
        """Initialize the optimized auth service."""
        # Extract DB path from SQLAlchemy URL
        self.db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
        
        # Ensure DB path exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get an optimized SQLite connection."""
        conn = sqlite3.connect(
            self.db_path, 
            timeout=5,
            check_same_thread=False
        )
        
        # Enable dictionary rows
        conn.row_factory = sqlite3.Row
        
        # Set pragmas for better performance
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = 10000")
        conn.execute("PRAGMA temp_store = MEMORY")
        
        return conn
    
    def close_connection(self, conn: sqlite3.Connection) -> None:
        """Close database connection safely."""
        if conn:
            conn.close()
    
    def check_user_exists(self, email: str) -> bool:
        """Check if a user exists by email."""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM users WHERE email = ? LIMIT 1", 
                (email,)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking user existence: {e}")
            return False
        finally:
            self.close_connection(conn)
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user data by email."""
        conn = None
        start_time = time.time()
        
        try:
            # Use performance tracking context manager
            with time_query("user_lookup_by_email", {"email": email}):
                conn = self.get_connection()
                cursor = conn.cursor()
                
                # Selective query with only needed fields
                cursor.execute(
                    """
                    SELECT id, email, hashed_password, is_verified, 
                           first_name, last_name, role, status,
                           created_at, updated_at, last_login_at
                    FROM users 
                    WHERE email = ?
                    """, 
                    (email,)
                )
                
                user = cursor.fetchone()
                if not user:
                    return None
                
                # Convert to dict
                return dict(user)
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
        finally:
            self.close_connection(conn)
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data by id."""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Selective query with only needed fields
            cursor.execute(
                """
                SELECT id, email, hashed_password, is_verified, 
                       first_name, last_name, role, status,
                       created_at, updated_at, last_login_at
                FROM users 
                WHERE id = ?
                """, 
                (user_id,)
            )
            
            user = cursor.fetchone()
            if not user:
                return None
            
            # Convert to dict
            return dict(user)
        except Exception as e:
            logger.error(f"Error getting user by id: {e}")
            return None
        finally:
            self.close_connection(conn)
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[int]:
        """Create a new user."""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            
            # Hash password
            hashed_password = get_password_hash(user_data["password"])
            
            # Insert user
            cursor.execute(
                """
                INSERT INTO users (
                    email, hashed_password, is_verified, first_name, last_name,
                    role, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_data["email"],
                    hashed_password,
                    False,  # is_verified
                    user_data["first_name"],
                    user_data["last_name"],
                    UserRole.USER,  # role
                    UserStatus.PENDING,  # status
                    now,
                    now
                )
            )
            
            # Get user ID
            user_id = cursor.lastrowid
            
            # Commit transaction
            conn.commit()
            
            return user_id
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            self.close_connection(conn)
    
    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            
            cursor.execute(
                "UPDATE users SET last_login_at = ? WHERE id = ?",
                (now, user_id)
            )
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            self.close_connection(conn)

    async def register_user(
        self, 
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        db: AsyncSession
    ) -> User:
        """Register a new user with optimized DB access."""
        # Check if user exists
        if self.check_user_exists(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user data
        user_data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name
        }
        
        # Create user
        user_id = self.create_user(user_data)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Get the created user through SQLAlchemy for consistent response
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def authenticate_user(
        self, 
        email: str,
        password: str
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Authenticate user and return auth result.
        
        Returns:
            Tuple[success, user_dict, error_message]
        """
        # Use performance tracking context manager for the entire authentication process
        with time_query("user_authentication", {"endpoint": "/optimized-auth/login"}):
            # Get user by email
            user = self.get_user_by_email(email)
            
            # Check if user exists
            if not user:
                return False, None, "Incorrect email or password"
            
            # Check password
            if not verify_password(password, user["hashed_password"]):
                return False, None, "Incorrect email or password"
            
            # Check if account is active
            if user["status"] in [UserStatus.SUSPENDED, UserStatus.INACTIVE]:
                return False, None, "Account is suspended or inactive"
            
            # Update last login time
            self.update_last_login(user["id"])
            
            return True, user, None
    
    def verify_jwt_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return subject if valid."""
        from app.core.security import verify_token
        return verify_token(token)
    
    async def get_user_from_token(
        self, 
        token: str,
        db: AsyncSession
    ) -> Optional[User]:
        """Get user from token."""
        # Verify token
        email = self.verify_jwt_token(token)
        if not email:
            return None
        
        # Get user by email
        user_dict = self.get_user_by_email(email)
        if not user_dict:
            return None
        
        # Get full user object through SQLAlchemy
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.id == user_dict["id"]))
        return result.scalar_one_or_none()


# Global instance
optimized_auth = OptimizedAuthService()


# Dependency for optimized auth service
def get_optimized_auth() -> OptimizedAuthService:
    """Get optimized auth service instance."""
    return optimized_auth