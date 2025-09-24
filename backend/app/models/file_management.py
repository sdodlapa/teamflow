"""
File upload and management models for TeamFlow.
Handles secure file storage, task attachments, and media management.
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class FileType(str, Enum):
    """Supported file types for uploads."""
    
    # Documents
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    TXT = "txt"
    RTF = "rtf"
    
    # Images
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    GIF = "gif"
    SVG = "svg"
    WEBP = "webp"
    
    # Spreadsheets
    XLS = "xls"
    XLSX = "xlsx"
    CSV = "csv"
    
    # Presentations
    PPT = "ppt"
    PPTX = "pptx"
    
    # Archives
    ZIP = "zip"
    RAR = "rar"
    TAR = "tar"
    GZ = "gz"
    
    # Media
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MP3 = "mp3"
    WAV = "wav"
    
    # Other
    OTHER = "other"


class FileVisibility(str, Enum):
    """File visibility levels."""
    
    PUBLIC = "public"           # Visible to all project members
    PRIVATE = "private"         # Visible only to uploader and assignee
    RESTRICTED = "restricted"   # Visible to specific users only


class FileUpload(Base):
    """Model for file uploads and attachments."""
    
    __tablename__ = "file_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # File identification
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Path in storage system
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    file_type = Column(String(50), nullable=False)  # FileType enum
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64), nullable=True)  # SHA256 hash for deduplication
    
    # Upload metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Organization and project context
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    
    # File properties
    visibility = Column(String(20), default=FileVisibility.PUBLIC.value, nullable=False)
    description = Column(Text, nullable=True)
    
    # Image/media specific metadata
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # For video/audio files
    
    # File status
    is_active = Column(Boolean, default=True, nullable=False)
    is_processed = Column(Boolean, default=False, nullable=False)  # For thumbnails/processing
    processing_status = Column(String(50), nullable=True)  # "pending", "success", "failed"
    
    # Virus scanning and security
    scan_status = Column(String(20), default="pending", nullable=False)  # "pending", "clean", "infected", "error"
    scan_result = Column(Text, nullable=True)
    
    # Expiration and cleanup
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    uploader = relationship("User", back_populates="uploaded_files")
    organization = relationship("Organization", back_populates="files")
    project = relationship("Project", back_populates="files")
    task = relationship("Task", back_populates="files")
    
    # Version control
    versions = relationship("FileVersion", back_populates="file", cascade="all, delete-orphan")
    
    # Analytics and tracking
    downloads = relationship("FileDownload", back_populates="file", cascade="all, delete-orphan")
    
    # Thumbnails and previews
    thumbnails = relationship("FileThumbnail", back_populates="file", cascade="all, delete-orphan")
    
    # Access permissions
    access_permissions = relationship("FileAccessPermission", back_populates="file", cascade="all, delete-orphan")
    
    # Enhanced comment attachments
    comment_attachments = relationship("CommentAttachment", back_populates="file", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FileUpload(id={self.id}, filename='{self.filename}', size={self.file_size})>"
    
    @property
    def file_extension(self) -> str:
        """Get file extension from filename."""
        return self.filename.split('.')[-1].lower() if '.' in self.filename else ''
    
    @property
    def human_readable_size(self) -> str:
        """Get human readable file size."""
        size = self.file_size
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    @property
    def is_image(self) -> bool:
        """Check if file is an image."""
        return self.file_type in [
            FileType.JPEG.value, FileType.JPG.value, FileType.PNG.value,
            FileType.GIF.value, FileType.SVG.value, FileType.WEBP.value
        ]
    
    @property
    def is_document(self) -> bool:
        """Check if file is a document."""
        return self.file_type in [
            FileType.PDF.value, FileType.DOC.value, FileType.DOCX.value,
            FileType.TXT.value, FileType.RTF.value, FileType.XLS.value,
            FileType.XLSX.value, FileType.CSV.value, FileType.PPT.value,
            FileType.PPTX.value
        ]


class FileVersion(Base):
    """Model for file versions (when files are updated)."""
    
    __tablename__ = "file_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file_uploads.id"), nullable=False)
    
    version_number = Column(Integer, nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_hash = Column(String(64), nullable=True)
    
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    changes_description = Column(Text, nullable=True)
    is_current = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    file = relationship("FileUpload", back_populates="versions")
    uploader = relationship("User")
    
    def __repr__(self):
        return f"<FileVersion(id={self.id}, file_id={self.file_id}, version={self.version_number})>"


class FileThumbnail(Base):
    """Model for file thumbnails and previews."""
    
    __tablename__ = "file_thumbnails"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file_uploads.id"), nullable=False)
    
    thumbnail_type = Column(String(20), nullable=False)  # "small", "medium", "large", "preview"
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    file = relationship("FileUpload", back_populates="thumbnails")
    
    def __repr__(self):
        return f"<FileThumbnail(id={self.id}, type='{self.thumbnail_type}', size={self.width}x{self.height})>"


class FileAccessPermission(Base):
    """Model for fine-grained file access permissions."""
    
    __tablename__ = "file_access_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file_uploads.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    permission_type = Column(String(20), nullable=False)  # "view", "download", "edit", "delete"
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    file = relationship("FileUpload", back_populates="access_permissions")
    user = relationship("User", foreign_keys=[user_id])
    granter = relationship("User", foreign_keys=[granted_by])
    
    def __repr__(self):
        return f"<FileAccessPermission(file_id={self.file_id}, user_id={self.user_id}, type='{self.permission_type}')>"


class FileDownload(Base):
    """Model for tracking file downloads and access logs."""
    
    __tablename__ = "file_downloads"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file_uploads.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    downloaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    
    # Download method
    download_method = Column(String(20), nullable=False)  # "direct", "preview", "thumbnail"
    
    # File info at time of download (for audit purposes)
    file_version = Column(Integer, nullable=True)
    file_size_at_download = Column(BigInteger, nullable=True)
    
    # Relationships
    file = relationship("FileUpload", back_populates="downloads")
    user = relationship("User")
    
    def __repr__(self):
        return f"<FileDownload(file_id={self.file_id}, user_id={self.user_id}, downloaded_at={self.downloaded_at})>"


class FileShare(Base):
    """Model for file sharing links and external access."""
    
    __tablename__ = "file_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file_uploads.id"), nullable=False)
    
    # Share link properties
    share_token = Column(String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    share_url = Column(String(500), nullable=True)  # Full URL for sharing
    
    # Access control
    password_hash = Column(String(128), nullable=True)  # Optional password protection
    max_downloads = Column(Integer, nullable=True)  # Limit number of downloads
    current_downloads = Column(Integer, default=0, nullable=False)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Settings
    allow_preview = Column(Boolean, default=True, nullable=False)
    allow_download = Column(Boolean, default=True, nullable=False)
    require_login = Column(Boolean, default=False, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_accessed = Column(DateTime, nullable=True)
    
    # Relationships
    file = relationship("FileUpload")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<FileShare(id={self.id}, token='{self.share_token[:8]}...', file_id={self.file_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if share link has expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    @property
    def is_download_limit_reached(self) -> bool:
        """Check if download limit has been reached."""
        if self.max_downloads:
            return self.current_downloads >= self.max_downloads
        return False