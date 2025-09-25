"""
Temporary stub for file management service.
Used for Railway deployment until libmagic system dependency is resolved.

TODO LATER: Replace this with full file_management.py implementation
Requirements:
- Configure nixpacks.toml with libmagic system package
- Re-enable python-magic in requirements.txt
- Switch imports back to full file_management service
"""
import os
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO, Tuple
from datetime import datetime

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User


class FileManagementService:
    """
    Stub implementation of FileManagementService for deployment.
    
    DEPLOYMENT NOTE: This is a temporary stub to enable deployment without
    python-magic dependency. File upload functionality is disabled.
    """
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR) if hasattr(settings, 'UPLOAD_DIR') else Path("uploads")
    
    async def upload_file(
        self, 
        file: UploadFile, 
        user: User, 
        db: Session,
        **kwargs
    ) -> Dict[str, Any]:
        """Stub method - raises not implemented error"""
        raise HTTPException(
            status_code=501,
            detail="File upload temporarily disabled during deployment. System dependency required."
        )
    
    async def delete_file(self, file_id: str, user: User, db: Session) -> bool:
        """Stub method - raises not implemented error"""
        raise HTTPException(
            status_code=501,
            detail="File management temporarily disabled during deployment."
        )
    
    async def get_file_info(self, file_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Stub method - returns None"""
        return None
    
    def get_file_mime_type(self, file_path: str) -> str:
        """Stub method - returns generic mime type without python-magic"""
        return "application/octet-stream"
    
    async def create_thumbnail(self, file_path: str, **kwargs) -> Optional[str]:
        """Stub method - returns None"""
        return None


# Create service instance
file_management_service = FileManagementService()