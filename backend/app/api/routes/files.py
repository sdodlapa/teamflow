"""
File management API routes for TeamFlow.
Handles file upload, download, management, and sharing operations.
"""
import os
import mimetypes
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

from fastapi import (
    APIRouter, Depends, HTTPException, status, UploadFile, File,
    Form, Query, Response, BackgroundTasks
)
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.user import UserRead
from app.models.file_management import FileUpload, FileDownload, FileShare
from app.schemas.file_management import (
    FileUploadRequest, FileUploadResponse, FileDetailsResponse,
    FileListResponse, FileSearchRequest, FileShareRequest,
    FileShareResponse, FileStatsResponse, BulkFileActionRequest,
    BulkFileActionResponse, FileProcessingStatus
)
from app.services.file_management import FileManagementService
from app.services.file_notifications import (
    notify_file_upload, notify_file_delete, notify_file_shared,
    notify_file_download, notify_bulk_file_action
)


router = APIRouter(prefix="/files", tags=["File Management"])
file_service = FileManagementService()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    visibility: str = Form("public"),
    project_id: Optional[int] = Form(None),
    task_id: Optional[int] = Form(None),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a new file to the system.
    
    Supports multiple file types including:
    - Documents: PDF, DOC, DOCX, TXT, RTF
    - Images: JPEG, PNG, GIF, SVG, WEBP
    - Spreadsheets: XLS, XLSX, CSV
    - Presentations: PPT, PPTX
    - Archives: ZIP, RAR, TAR, GZ
    - Media: MP4, AVI, MOV, MP3, WAV
    """
    
    # Create upload request
    upload_request = FileUploadRequest(
        description=description,
        visibility=visibility,
        project_id=project_id,
        task_id=task_id
    )
    
    # Upload and process file
    file_upload = await file_service.upload_file(file, upload_request, current_user, db)
    
    # Send real-time notification
    background_tasks.add_task(
        notify_file_upload,
        file_upload.id,
        current_user.id,
        project_id or task_id
    )
    
    return FileUploadResponse.from_orm(file_upload)


@router.get("/", response_model=FileListResponse)
def list_files(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    filename: Optional[str] = Query(None, description="Search in filename"),
    file_type: Optional[List[str]] = Query(None, description="Filter by file types"),
    project_id: Optional[int] = Query(None, description="Filter by project"),
    task_id: Optional[int] = Query(None, description="Filter by task"),
    uploaded_by: Optional[int] = Query(None, description="Filter by uploader"),
    sort_by: str = Query("uploaded_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List files with filtering, sorting, and pagination.
    
    Supports filtering by:
    - Filename (partial match)
    - File type
    - Project/Task association
    - Upload date range
    - File size range
    - Uploader
    """
    
    # Validate sort_order
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort_order. Must be 'asc' or 'desc'"
        )
    
    # Create search request
    search_request = FileSearchRequest(
        filename=filename,
        file_type=file_type,
        project_id=project_id,
        task_id=task_id,
        uploaded_by=uploaded_by,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Search files
    files, total_count = file_service.search_files(search_request, current_user, db)
    
    # Calculate pagination info
    total_pages = (total_count + page_size - 1) // page_size
    
    return FileListResponse(
        files=[FileUploadResponse.from_orm(f) for f in files],
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{file_id}", response_model=FileDetailsResponse)
def get_file_details(
    file_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific file."""
    
    file_upload = file_service.get_file(file_id, current_user, db)
    if not file_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Get download statistics
    download_count = db.query(FileDownload).filter(
        FileDownload.file_id == file_id
    ).count()
    
    last_download = db.query(FileDownload).filter(
        FileDownload.file_id == file_id
    ).order_by(FileDownload.downloaded_at.desc()).first()
    
    # Get sharing information
    share_count = db.query(FileShare).filter(
        FileShare.file_id == file_id,
        FileShare.is_active == True
    ).count()
    
    # Create detailed response
    response_data = FileUploadResponse.from_orm(file_upload).dict()
    response_data.update({
        "thumbnails": [t for t in file_upload.thumbnails],
        "versions": [v for v in file_upload.versions],
        "download_count": download_count,
        "last_downloaded": last_download.downloaded_at if last_download else None,
        "is_shared": share_count > 0,
        "share_count": share_count
    })
    
    return FileDetailsResponse(**response_data)


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a file."""
    
    file_upload = file_service.get_file(file_id, current_user, db)
    if not file_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if file exists on disk
    if not os.path.exists(file_upload.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    # Log download
    download_record = FileDownload(
        file_id=file_id,
        user_id=current_user.id,
        download_method="direct",
        file_size_at_download=file_upload.file_size
    )
    db.add(download_record)
    db.commit()
    
    # Send real-time notification
    await notify_file_download(
        file_id, current_user.id, "direct", 
        file_upload.project_id or file_upload.task_id
    )
    
    # Return file
    return FileResponse(
        path=file_upload.file_path,
        filename=file_upload.original_filename,
        media_type=file_upload.mime_type
    )


@router.get("/{file_id}/thumbnail/{size}")
async def get_file_thumbnail(
    file_id: int,
    size: str,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file thumbnail."""
    
    # Validate size parameter
    if size not in ["small", "medium", "large", "preview"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid thumbnail size. Must be one of: small, medium, large, preview"
        )
    
    file_upload = file_service.get_file(file_id, current_user, db)
    if not file_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if not file_upload.is_image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thumbnails are only available for image files"
        )
    
    # Find thumbnail
    thumbnail = next(
        (t for t in file_upload.thumbnails if t.thumbnail_type == size),
        None
    )
    
    if not thumbnail or not os.path.exists(thumbnail.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail not found"
        )
    
    return FileResponse(
        path=thumbnail.file_path,
        media_type=thumbnail.mime_type
    )


@router.post("/{file_id}/share", response_model=FileShareResponse)
async def create_file_share(
    file_id: int,
    share_request: FileShareRequest,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a shareable link for a file."""
    
    file_upload = file_service.get_file(file_id, current_user, db)
    if not file_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Calculate expiration date
    expires_at = None
    if share_request.expires_in_hours:
        expires_at = datetime.utcnow() + timedelta(hours=share_request.expires_in_hours)
    
    # Create share record
    file_share = FileShare(
        file_id=file_id,
        created_by=current_user.id,
        expires_at=expires_at,
        max_downloads=share_request.max_downloads,
        allow_preview=share_request.allow_preview,
        allow_download=share_request.allow_download,
        require_login=share_request.require_login
    )
    
    # Set password if provided
    if share_request.password:
        from app.core.security import get_password_hash
        file_share.password_hash = get_password_hash(share_request.password)
    
    db.add(file_share)
    db.commit()
    db.refresh(file_share)
    
    # Generate share URL
    file_share.share_url = f"/api/v1/files/shared/{file_share.share_token}"
    db.commit()
    
    # Send real-time notification
    await notify_file_shared(
        file_id, current_user.id, file_share.share_token,
        file_upload.project_id or file_upload.task_id
    )
    
    return FileShareResponse(
        id=file_share.id,
        share_token=file_share.share_token,
        share_url=file_share.share_url,
        has_password=bool(file_share.password_hash),
        max_downloads=file_share.max_downloads,
        current_downloads=file_share.current_downloads,
        allow_preview=file_share.allow_preview,
        allow_download=file_share.allow_download,
        require_login=file_share.require_login,
        created_at=file_share.created_at,
        expires_at=file_share.expires_at,
        is_active=file_share.is_active,
        last_accessed=file_share.last_accessed,
        file_id=file_share.file_id,
        filename=file_upload.original_filename,
        file_size=file_upload.file_size
    )


@router.get("/shared/{share_token}")
async def access_shared_file(
    share_token: str,
    password: Optional[str] = Query(None),
    action: str = Query("download"),
    db: Session = Depends(get_db)
):
    """Access a shared file via share token."""
    
    # Validate action parameter
    if action not in ["download", "preview"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be 'download' or 'preview'"
        )
    
    # Find share record
    file_share = db.query(FileShare).filter(
        FileShare.share_token == share_token,
        FileShare.is_active == True
    ).first()
    
    if not file_share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share link not found or expired"
        )
    
    # Check if share has expired
    if file_share.is_expired:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Share link has expired"
        )
    
    # Check download limit
    if action == "download" and file_share.is_download_limit_reached:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Download limit reached"
        )
    
    # Check password
    if file_share.password_hash:
        if not password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password required"
            )
        
        from app.core.security import verify_password
        if not verify_password(password, file_share.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
    
    # Check action permissions
    if action == "preview" and not file_share.allow_preview:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Preview not allowed"
        )
    
    if action == "download" and not file_share.allow_download:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Download not allowed"
        )
    
    # Get file
    file_upload = file_share.file
    if not os.path.exists(file_upload.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    # Update share statistics
    file_share.last_accessed = datetime.utcnow()
    if action == "download":
        file_share.current_downloads += 1
        
        # Send real-time notification for shared file download
        await notify_file_download(
            file_upload.id, None, "shared", 
            file_upload.project_id or file_upload.task_id
        )
    
    db.commit()
    
    # Return file
    return FileResponse(
        path=file_upload.file_path,
        filename=file_upload.original_filename,
        media_type=file_upload.mime_type
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    background_tasks: BackgroundTasks,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a file."""
    
    file_upload = file_service.get_file(file_id, current_user, db)
    if not file_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    success = await file_service.delete_file(file_id, current_user, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )
    
    # Send real-time notification
    background_tasks.add_task(
        notify_file_delete,
        file_id,
        current_user.id,
        file_upload.project_id or file_upload.task_id
    )
    
    return {"message": "File deleted successfully"}


@router.post("/bulk-action", response_model=BulkFileActionResponse)
async def bulk_file_action(
    action_request: BulkFileActionRequest,
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform bulk actions on multiple files."""
    
    successful = 0
    failed = 0
    errors = []
    
    for file_id in action_request.file_ids:
        try:
            if action_request.action == "delete":
                success = await file_service.delete_file(file_id, current_user, db)
                if success:
                    successful += 1
                else:
                    failed += 1
                    errors.append({"file_id": file_id, "error": "Delete failed"})
            
            # Add other bulk actions here (change_visibility, move_project, etc.)
            
        except Exception as e:
            failed += 1
            errors.append({"file_id": file_id, "error": str(e)})
    
    # Send bulk action notification
    await notify_bulk_file_action(
        action_request.action,
        action_request.file_ids,
        current_user.id,
        {"successful": successful, "failed": failed, "errors": errors}
    )
    
    return BulkFileActionResponse(
        total_processed=len(action_request.file_ids),
        successful=successful,
        failed=failed,
        errors=errors
    )


@router.get("/statistics", response_model=FileStatsResponse)
def get_file_statistics(
    project_id: Optional[int] = Query(None, description="Filter by project"),
    current_user: UserRead = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file usage statistics."""
    
    # Base query
    query = db.query(FileUpload).filter(
        FileUpload.organization_id == current_user.organization_id,
        FileUpload.is_active == True
    )
    
    if project_id:
        query = query.filter(FileUpload.project_id == project_id)
    
    files = query.all()
    
    # Calculate statistics
    total_files = len(files)
    total_size = sum(f.file_size for f in files)
    
    # Group by file type
    files_by_type = {}
    size_by_type = {}
    
    for file in files:
        file_type = file.file_type
        files_by_type[file_type] = files_by_type.get(file_type, 0) + 1
        size_by_type[file_type] = size_by_type.get(file_type, 0) + file.file_size
    
    # Group by project
    files_by_project = {}
    for file in files:
        if file.project_id:
            project_name = file.project.name if file.project else f"Project {file.project_id}"
            files_by_project[project_name] = files_by_project.get(project_name, 0) + 1
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_uploads = query.filter(FileUpload.uploaded_at >= week_ago).count()
    
    recent_downloads = db.query(FileDownload).filter(
        FileDownload.downloaded_at >= week_ago
    ).count()
    
    return FileStatsResponse(
        total_files=total_files,
        total_size_bytes=total_size,
        total_size_readable=f"{total_size / (1024*1024*1024):.2f} GB",
        files_by_type=files_by_type,
        size_by_type=size_by_type,
        files_by_project=files_by_project,
        recent_uploads=recent_uploads,
        recent_downloads=recent_downloads
    )