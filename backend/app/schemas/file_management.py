"""
File management schemas for TeamFlow API.
Defines request/response models for file upload, management, and sharing operations.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, HttpUrl
from enum import Enum

from app.models.file_management import FileType, FileVisibility


class FileUploadRequest(BaseModel):
    """Request model for file upload metadata."""
    
    description: Optional[str] = Field(None, max_length=1000, description="File description")
    visibility: FileVisibility = Field(FileVisibility.PUBLIC, description="File visibility level")
    project_id: Optional[int] = Field(None, description="Associated project ID")
    task_id: Optional[int] = Field(None, description="Associated task ID")
    
    class Config:
        use_enum_values = True


class FileMetadata(BaseModel):
    """File metadata extracted from uploaded file."""
    
    filename: str
    original_filename: str
    file_size: int
    file_type: str
    mime_type: str
    file_hash: Optional[str] = None
    
    # Image/media specific
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    duration_seconds: Optional[int] = None


class FileUploadResponse(BaseModel):
    """Response model for successful file upload."""
    
    id: int
    filename: str
    original_filename: str
    file_size: int
    human_readable_size: str
    file_type: str
    mime_type: str
    visibility: str
    description: Optional[str]
    
    # Context
    project_id: Optional[int]
    task_id: Optional[int]
    organization_id: int
    
    # Upload info
    uploaded_by: int
    uploaded_at: datetime
    
    # File properties
    is_image: bool
    is_document: bool
    image_width: Optional[int]
    image_height: Optional[int]
    
    # Status
    is_processed: bool
    processing_status: Optional[str]
    scan_status: str
    
    class Config:
        from_attributes = True


class FileThumbnailResponse(BaseModel):
    """Response model for file thumbnail."""
    
    id: int
    thumbnail_type: str
    width: int
    height: int
    file_size: int
    generated_at: datetime
    
    class Config:
        from_attributes = True


class FileVersionResponse(BaseModel):
    """Response model for file version."""
    
    id: int
    version_number: int
    filename: str
    file_size: int
    human_readable_size: str
    uploaded_by: int
    uploaded_at: datetime
    changes_description: Optional[str]
    is_current: bool
    
    class Config:
        from_attributes = True


class FileDetailsResponse(FileUploadResponse):
    """Detailed file response with additional metadata."""
    
    # Relationships
    thumbnails: List[FileThumbnailResponse] = []
    versions: List[FileVersionResponse] = []
    
    # Access tracking
    download_count: int = 0
    last_downloaded: Optional[datetime]
    
    # Sharing info
    is_shared: bool = False
    share_count: int = 0


class FileListResponse(BaseModel):
    """Response model for file listing."""
    
    files: List[FileUploadResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        from_attributes = True


class FileSearchRequest(BaseModel):
    """Request model for file search and filtering."""
    
    # Basic filters
    filename: Optional[str] = Field(None, description="Search in filename")
    file_type: Optional[List[FileType]] = Field(None, description="Filter by file types")
    
    # Context filters
    project_id: Optional[int] = Field(None, description="Filter by project")
    task_id: Optional[int] = Field(None, description="Filter by task")
    uploaded_by: Optional[int] = Field(None, description="Filter by uploader")
    
    # Date filters
    uploaded_after: Optional[datetime] = Field(None, description="Files uploaded after this date")
    uploaded_before: Optional[datetime] = Field(None, description="Files uploaded before this date")
    
    # Size filters
    min_size: Optional[int] = Field(None, description="Minimum file size in bytes")
    max_size: Optional[int] = Field(None, description="Maximum file size in bytes")
    
    # Visibility
    visibility: Optional[List[FileVisibility]] = Field(None, description="Filter by visibility")
    
    # Status filters
    scan_status: Optional[List[str]] = Field(None, description="Filter by scan status")
    is_processed: Optional[bool] = Field(None, description="Filter by processing status")
    
    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    
    # Sorting
    sort_by: str = Field("uploaded_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")
    
    class Config:
        use_enum_values = True


class FileShareRequest(BaseModel):
    """Request model for creating file share links."""
    
    password: Optional[str] = Field(None, min_length=4, max_length=50, description="Optional password protection")
    expires_in_hours: Optional[int] = Field(None, ge=1, le=8760, description="Expiration time in hours (max 1 year)")
    max_downloads: Optional[int] = Field(None, ge=1, le=1000, description="Maximum number of downloads")
    
    allow_preview: bool = Field(True, description="Allow file preview")
    allow_download: bool = Field(True, description="Allow file download")
    require_login: bool = Field(False, description="Require user login to access")


class FileShareResponse(BaseModel):
    """Response model for file share links."""
    
    id: int
    share_token: str
    share_url: str
    
    # Access control
    has_password: bool
    max_downloads: Optional[int]
    current_downloads: int
    
    # Settings
    allow_preview: bool
    allow_download: bool
    require_login: bool
    
    # Metadata
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    last_accessed: Optional[datetime]
    
    # File info
    file_id: int
    filename: str
    file_size: int
    
    class Config:
        from_attributes = True


class FileAccessRequest(BaseModel):
    """Request model for granting file access permissions."""
    
    user_id: int
    permission_type: str = Field(..., pattern="^(view|download|edit|delete)$", description="Permission type")
    expires_in_hours: Optional[int] = Field(None, ge=1, le=8760, description="Permission expiration in hours")


class FileAccessResponse(BaseModel):
    """Response model for file access permissions."""
    
    id: int
    user_id: int
    permission_type: str
    granted_by: int
    granted_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class FileVersionRequest(BaseModel):
    """Request model for uploading new file version."""
    
    changes_description: Optional[str] = Field(None, max_length=500, description="Description of changes")


class FileStatsResponse(BaseModel):
    """Response model for file statistics."""
    
    total_files: int
    total_size_bytes: int
    total_size_readable: str
    
    # By type
    files_by_type: Dict[str, int]
    size_by_type: Dict[str, int]
    
    # By project
    files_by_project: Dict[str, int]
    
    # Recent activity
    recent_uploads: int  # Last 7 days
    recent_downloads: int  # Last 7 days
    
    # Storage usage
    storage_quota_bytes: Optional[int] = None
    storage_used_percentage: Optional[float] = None


class BulkFileActionRequest(BaseModel):
    """Request model for bulk file operations."""
    
    file_ids: List[int] = Field(..., min_items=1, max_items=100, description="List of file IDs")
    action: str = Field(..., pattern="^(delete|archive|change_visibility|move_project)$", description="Action to perform")
    
    # Action-specific parameters
    new_visibility: Optional[FileVisibility] = Field(None, description="New visibility for change_visibility action")
    target_project_id: Optional[int] = Field(None, description="Target project for move_project action")
    
    class Config:
        use_enum_values = True


class BulkFileActionResponse(BaseModel):
    """Response model for bulk file operations."""
    
    total_processed: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]] = []


class FileUploadProgress(BaseModel):
    """Model for tracking file upload progress."""
    
    upload_id: str
    filename: str
    total_size: int
    uploaded_size: int
    progress_percentage: float
    status: str  # "uploading", "processing", "complete", "error"
    error_message: Optional[str] = None
    estimated_time_remaining: Optional[int] = None  # seconds


class FileProcessingStatus(BaseModel):
    """Model for file processing status updates."""
    
    file_id: int
    processing_type: str  # "thumbnail", "scan", "metadata"
    status: str  # "pending", "processing", "complete", "error"
    progress_percentage: Optional[float] = None
    message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None