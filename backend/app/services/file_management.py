"""
File management service for TeamFlow.
Handles file uploads, processing, storage, and security operations.
"""
import os
import hashlib
import uuid
import mimetypes
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO, Tuple
from datetime import datetime, timedelta

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from PIL import Image, ImageOps
import magic

from app.core.config import settings
from app.core.database import get_db
from app.models.file_management import (
    FileUpload, FileType, FileVisibility, FileThumbnail,
    FileVersion, FileAccessPermission, FileDownload, FileShare
)
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.schemas.file_management import (
    FileUploadRequest, FileMetadata, FileSearchRequest,
    FileShareRequest, FileAccessRequest
)


class FileStorageService:
    """Service for handling file storage operations."""
    
    def __init__(self):
        self.storage_path = Path(settings.FILE_UPLOAD_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.uploads_path = self.storage_path / "uploads"
        self.thumbnails_path = self.storage_path / "thumbnails"
        self.temp_path = self.storage_path / "temp"
        
        for path in [self.uploads_path, self.thumbnails_path, self.temp_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def get_file_path(self, file_id: int, filename: str, subfolder: str = "uploads") -> Path:
        """Generate file path for storage."""
        # Organize files by date and ID for better organization
        date_folder = datetime.now().strftime("%Y/%m")
        folder_path = self.storage_path / subfolder / date_folder / str(file_id)
        folder_path.mkdir(parents=True, exist_ok=True)
        
        return folder_path / filename
    
    async def save_upload_file(self, upload_file: UploadFile, file_id: int) -> Tuple[str, int]:
        """Save uploaded file to storage and return path and size."""
        file_path = self.get_file_path(file_id, upload_file.filename)
        
        file_size = 0
        with open(file_path, "wb") as buffer:
            while chunk := await upload_file.read(8192):  # Read in 8KB chunks
                buffer.write(chunk)
                file_size += len(chunk)
        
        return str(file_path), file_size
    
    def save_file_content(self, content: bytes, file_id: int, filename: str, subfolder: str = "uploads") -> str:
        """Save file content to storage."""
        file_path = self.get_file_path(file_id, filename, subfolder)
        
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        return str(file_path)
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from storage."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False
    
    def get_file_content(self, file_path: str) -> Optional[bytes]:
        """Get file content from storage."""
        try:
            with open(file_path, "rb") as file:
                return file.read()
        except Exception:
            return None


class FileSecurityService:
    """Service for file security and scanning operations."""
    
    ALLOWED_MIME_TYPES = {
        # Documents
        "application/pdf": FileType.PDF,
        "application/msword": FileType.DOC,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileType.DOCX,
        "text/plain": FileType.TXT,
        "application/rtf": FileType.RTF,
        
        # Images
        "image/jpeg": FileType.JPEG,
        "image/jpg": FileType.JPG,
        "image/png": FileType.PNG,
        "image/gif": FileType.GIF,
        "image/svg+xml": FileType.SVG,
        "image/webp": FileType.WEBP,
        
        # Spreadsheets
        "application/vnd.ms-excel": FileType.XLS,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": FileType.XLSX,
        "text/csv": FileType.CSV,
        
        # Presentations
        "application/vnd.ms-powerpoint": FileType.PPT,
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": FileType.PPTX,
        
        # Archives
        "application/zip": FileType.ZIP,
        "application/x-rar-compressed": FileType.RAR,
        "application/x-tar": FileType.TAR,
        "application/gzip": FileType.GZ,
        
        # Media
        "video/mp4": FileType.MP4,
        "video/x-msvideo": FileType.AVI,
        "video/quicktime": FileType.MOV,
        "audio/mpeg": FileType.MP3,
        "audio/wav": FileType.WAV,
    }
    
    MAX_FILE_SIZES = {
        # Images: 10MB
        FileType.JPEG: 10 * 1024 * 1024,
        FileType.JPG: 10 * 1024 * 1024,
        FileType.PNG: 10 * 1024 * 1024,
        FileType.GIF: 10 * 1024 * 1024,
        FileType.SVG: 5 * 1024 * 1024,
        FileType.WEBP: 10 * 1024 * 1024,
        
        # Documents: 50MB
        FileType.PDF: 50 * 1024 * 1024,
        FileType.DOC: 50 * 1024 * 1024,
        FileType.DOCX: 50 * 1024 * 1024,
        FileType.TXT: 10 * 1024 * 1024,
        FileType.RTF: 20 * 1024 * 1024,
        
        # Spreadsheets: 100MB
        FileType.XLS: 100 * 1024 * 1024,
        FileType.XLSX: 100 * 1024 * 1024,
        FileType.CSV: 50 * 1024 * 1024,
        
        # Presentations: 100MB
        FileType.PPT: 100 * 1024 * 1024,
        FileType.PPTX: 100 * 1024 * 1024,
        
        # Archives: 500MB
        FileType.ZIP: 500 * 1024 * 1024,
        FileType.RAR: 500 * 1024 * 1024,
        FileType.TAR: 500 * 1024 * 1024,
        FileType.GZ: 500 * 1024 * 1024,
        
        # Media: 1GB
        FileType.MP4: 1024 * 1024 * 1024,
        FileType.AVI: 1024 * 1024 * 1024,
        FileType.MOV: 1024 * 1024 * 1024,
        FileType.MP3: 100 * 1024 * 1024,
        FileType.WAV: 500 * 1024 * 1024,
    }
    
    def validate_file(self, upload_file: UploadFile, file_content: bytes) -> FileMetadata:
        """Validate uploaded file and extract metadata."""
        # Detect MIME type using python-magic for better accuracy
        mime_type = magic.from_buffer(file_content, mime=True)
        
        # Validate MIME type
        if mime_type not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{mime_type}' is not allowed"
            )
        
        file_type = self.ALLOWED_MIME_TYPES[mime_type]
        
        # Validate file size
        file_size = len(file_content)
        max_size = self.MAX_FILE_SIZES.get(file_type, 50 * 1024 * 1024)  # Default 50MB
        
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size ({file_size / (1024 * 1024):.1f}MB) exceeds maximum allowed size ({max_size_mb:.1f}MB)"
            )
        
        # Generate file hash for deduplication
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Generate safe filename
        safe_filename = self._generate_safe_filename(upload_file.filename)
        
        metadata = FileMetadata(
            filename=safe_filename,
            original_filename=upload_file.filename,
            file_size=file_size,
            file_type=file_type.value,
            mime_type=mime_type,
            file_hash=file_hash
        )
        
        # Extract image metadata if it's an image
        if file_type in [FileType.JPEG, FileType.JPG, FileType.PNG, FileType.GIF, FileType.WEBP]:
            try:
                image = Image.open(upload_file.file)
                metadata.image_width = image.width
                metadata.image_height = image.height
                upload_file.file.seek(0)  # Reset file pointer
            except Exception:
                pass
        
        return metadata
    
    def _generate_safe_filename(self, original_filename: str) -> str:
        """Generate a safe filename for storage."""
        # Get file extension
        name, ext = os.path.splitext(original_filename)
        
        # Generate UUID for unique filename
        unique_id = str(uuid.uuid4())
        
        return f"{unique_id}{ext.lower()}"
    
    async def scan_file(self, file_path: str) -> Dict[str, Any]:
        """Perform virus scanning on uploaded file."""
        # This is a placeholder for actual virus scanning
        # In production, integrate with ClamAV, VirusTotal API, or similar
        
        try:
            # Basic file validation
            if not os.path.exists(file_path):
                return {"status": "error", "message": "File not found"}
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return {"status": "error", "message": "Empty file"}
            
            # Placeholder scan result
            return {"status": "clean", "message": "File is safe"}
            
        except Exception as e:
            return {"status": "error", "message": f"Scan failed: {str(e)}"}


class ThumbnailService:
    """Service for generating file thumbnails and previews."""
    
    THUMBNAIL_SIZES = {
        "small": (150, 150),
        "medium": (300, 300),
        "large": (800, 600),
        "preview": (1200, 800)
    }
    
    def __init__(self, storage_service: FileStorageService):
        self.storage_service = storage_service
    
    async def generate_thumbnails(self, file_upload: FileUpload) -> List[FileThumbnail]:
        """Generate thumbnails for image files."""
        if not file_upload.is_image:
            return []
        
        thumbnails = []
        
        try:
            # Open original image
            with Image.open(file_upload.file_path) as image:
                # Convert to RGB if necessary
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")
                
                for size_name, (width, height) in self.THUMBNAIL_SIZES.items():
                    # Create thumbnail
                    thumbnail_image = ImageOps.fit(image, (width, height), Image.Resampling.LANCZOS)
                    
                    # Save thumbnail
                    thumbnail_filename = f"{file_upload.id}_{size_name}.jpg"
                    thumbnail_path = self.storage_service.get_file_path(
                        file_upload.id, thumbnail_filename, "thumbnails"
                    )
                    
                    thumbnail_image.save(thumbnail_path, "JPEG", quality=85, optimize=True)
                    
                    # Get thumbnail size
                    thumbnail_size = os.path.getsize(thumbnail_path)
                    
                    # Create thumbnail record
                    thumbnail = FileThumbnail(
                        file_id=file_upload.id,
                        thumbnail_type=size_name,
                        width=width,
                        height=height,
                        file_path=str(thumbnail_path),
                        file_size=thumbnail_size,
                        mime_type="image/jpeg"
                    )
                    
                    thumbnails.append(thumbnail)
        
        except Exception as e:
            # Log error but don't fail the upload
            print(f"Failed to generate thumbnails for file {file_upload.id}: {str(e)}")
        
        return thumbnails


class FileManagementService:
    """Main service for file management operations."""
    
    def __init__(self):
        self.storage_service = FileStorageService()
        self.security_service = FileSecurityService()
        self.thumbnail_service = ThumbnailService(self.storage_service)
    
    async def upload_file(
        self,
        upload_file: UploadFile,
        request: FileUploadRequest,
        user: User,
        db: Session
    ) -> FileUpload:
        """Upload and process a new file."""
        
        # Read file content
        file_content = await upload_file.read()
        await upload_file.seek(0)  # Reset file pointer
        
        # Validate file
        metadata = self.security_service.validate_file(upload_file, file_content)
        
        # Check for duplicate files
        existing_file = db.query(FileUpload).filter(
            FileUpload.file_hash == metadata.file_hash,
            FileUpload.organization_id == user.organization_id,
            FileUpload.is_active == True
        ).first()
        
        if existing_file:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="File already exists in the system"
            )
        
        # Validate project/task access
        if request.project_id:
            project = db.query(Project).filter(
                Project.id == request.project_id,
                Project.organization_id == user.organization_id
            ).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        
        if request.task_id:
            task = db.query(Task).filter(
                Task.id == request.task_id,
                Task.organization_id == user.organization_id
            ).first()
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )
        
        # Create file record
        file_upload = FileUpload(
            filename=metadata.filename,
            original_filename=metadata.original_filename,
            file_path="",  # Will be set after saving
            file_size=metadata.file_size,
            file_type=metadata.file_type,
            mime_type=metadata.mime_type,
            file_hash=metadata.file_hash,
            uploaded_by=user.id,
            organization_id=user.organization_id,
            project_id=request.project_id,
            task_id=request.task_id,
            visibility=request.visibility.value,
            description=request.description,
            image_width=metadata.image_width,
            image_height=metadata.image_height
        )
        
        # Save to database to get ID
        db.add(file_upload)
        db.flush()
        
        try:
            # Save file to storage
            file_path, _ = await self.storage_service.save_upload_file(upload_file, file_upload.id)
            file_upload.file_path = file_path
            
            # Perform security scan
            scan_result = await self.security_service.scan_file(file_path)
            file_upload.scan_status = scan_result["status"]
            file_upload.scan_result = scan_result.get("message")
            
            # Generate thumbnails for images
            if file_upload.is_image:
                thumbnails = await self.thumbnail_service.generate_thumbnails(file_upload)
                for thumbnail in thumbnails:
                    db.add(thumbnail)
                
                file_upload.is_processed = True
                file_upload.processing_status = "success"
            
            db.commit()
            db.refresh(file_upload)
            
            return file_upload
            
        except Exception as e:
            db.rollback()
            # Clean up file if it was saved
            if file_upload.file_path:
                self.storage_service.delete_file(file_upload.file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process file: {str(e)}"
            )
    
    def get_file(self, file_id: int, user: User, db: Session) -> Optional[FileUpload]:
        """Get file by ID with access control."""
        file_upload = db.query(FileUpload).filter(
            FileUpload.id == file_id,
            FileUpload.organization_id == user.organization_id,
            FileUpload.is_active == True
        ).first()
        
        if not file_upload:
            return None
        
        # Check access permissions
        if not self._check_file_access(file_upload, user, "view"):
            return None
        
        return file_upload
    
    def _check_file_access(self, file_upload: FileUpload, user: User, permission: str) -> bool:
        """Check if user has access to file."""
        # File owner always has access
        if file_upload.uploaded_by == user.id:
            return True
        
        # Check visibility rules
        if file_upload.visibility == FileVisibility.PUBLIC.value:
            return True
        elif file_upload.visibility == FileVisibility.PRIVATE.value:
            # Private files only accessible by owner and assignee (if task)
            if file_upload.task_id:
                task = file_upload.task
                if task and task.assigned_to == user.id:
                    return True
            return False
        
        # For restricted files, check explicit permissions
        # This would be implemented with FileAccessPermission model
        
        return False
    
    def search_files(
        self,
        request: FileSearchRequest,
        user: User,
        db: Session
    ) -> Tuple[List[FileUpload], int]:
        """Search files with filters and pagination."""
        query = db.query(FileUpload).filter(
            FileUpload.organization_id == user.organization_id,
            FileUpload.is_active == True
        )
        
        # Apply filters
        if request.filename:
            query = query.filter(
                FileUpload.original_filename.ilike(f"%{request.filename}%")
            )
        
        if request.file_type:
            file_types = [ft.value for ft in request.file_type]
            query = query.filter(FileUpload.file_type.in_(file_types))
        
        if request.project_id:
            query = query.filter(FileUpload.project_id == request.project_id)
        
        if request.task_id:
            query = query.filter(FileUpload.task_id == request.task_id)
        
        if request.uploaded_by:
            query = query.filter(FileUpload.uploaded_by == request.uploaded_by)
        
        if request.uploaded_after:
            query = query.filter(FileUpload.uploaded_at >= request.uploaded_after)
        
        if request.uploaded_before:
            query = query.filter(FileUpload.uploaded_at <= request.uploaded_before)
        
        if request.min_size:
            query = query.filter(FileUpload.file_size >= request.min_size)
        
        if request.max_size:
            query = query.filter(FileUpload.file_size <= request.max_size)
        
        if request.visibility:
            visibility_values = [v.value for v in request.visibility]
            query = query.filter(FileUpload.visibility.in_(visibility_values))
        
        if request.scan_status:
            query = query.filter(FileUpload.scan_status.in_(request.scan_status))
        
        if request.is_processed is not None:
            query = query.filter(FileUpload.is_processed == request.is_processed)
        
        # Get total count
        total_count = query.count()
        
        # Apply sorting
        if request.sort_by == "filename":
            sort_field = FileUpload.original_filename
        elif request.sort_by == "size":
            sort_field = FileUpload.file_size
        elif request.sort_by == "type":
            sort_field = FileUpload.file_type
        else:
            sort_field = FileUpload.uploaded_at
        
        if request.sort_order == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())
        
        # Apply pagination
        offset = (request.page - 1) * request.page_size
        files = query.offset(offset).limit(request.page_size).all()
        
        return files, total_count
    
    async def delete_file(self, file_id: int, user: User, db: Session) -> bool:
        """Delete file and associated resources."""
        file_upload = self.get_file(file_id, user, db)
        if not file_upload:
            return False
        
        # Check delete permissions
        if not self._check_file_access(file_upload, user, "delete"):
            return False
        
        try:
            # Delete physical file
            self.storage_service.delete_file(file_upload.file_path)
            
            # Delete thumbnails
            for thumbnail in file_upload.thumbnails:
                self.storage_service.delete_file(thumbnail.file_path)
            
            # Mark as deleted (soft delete)
            file_upload.is_active = False
            
            db.commit()
            return True
            
        except Exception:
            db.rollback()
            return False