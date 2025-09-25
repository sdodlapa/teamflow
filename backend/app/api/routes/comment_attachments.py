"""
Comment attachment API endpoints.

Handles file uploads, attachments to comments, and media management
for the enhanced comment system.
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime
import os
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.enhanced_comments import TaskCommentEnhanced, CommentAttachment
from app.models.file_management import FileUpload, FileType, FileVisibility
from app.schemas.user import UserRead
# TODO LATER: Switch back to full file_management service after libmagic is configured
# from app.services.file_management import FileManagementService
from app.services.file_management_stub import FileManagementService
from app.core.config import settings

router = APIRouter()


@router.post("/comments/{comment_id}/attachments")
async def add_comment_attachment(
    comment_id: int,
    files: List[UploadFile] = FastAPIFile(...),
    display_names: Optional[List[str]] = Form(None),
    is_inline: bool = Form(False),
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Add file attachments to a comment."""
    
    # Verify comment exists and user can attach files
    comment = await db.get(TaskCommentEnhanced, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user can attach (comment author or task participant)
    if comment.user_id != current_user.id:
        # Could add additional permission checks here
        pass
    
    # Validate file limits
    if len(files) > 10:  # Max 10 files per comment
        raise HTTPException(status_code=400, detail="Maximum 10 files per comment")
    
    file_service = FileManagementService(db)
    attachment_objects = []
    uploaded_files = []
    
    try:
        for i, file in enumerate(files):
            # Validate file
            if file.size > 50 * 1024 * 1024:  # 50MB limit
                raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds 50MB limit")
            
            # Determine display name
            display_name = None
            if display_names and i < len(display_names):
                display_name = display_names[i]
            
            # Upload file using file service
            file_upload = await file_service.create_file_upload(
                file=file,
                user_id=current_user.id,
                category=FileType.DOCUMENT,
                access_level=FileVisibility.PRIVATE,
                description=f"Attachment for comment {comment_id}",
                metadata={
                    "comment_id": comment_id,
                    "task_id": comment.task_id,
                    "is_inline": is_inline
                }
            )
            uploaded_files.append(file_upload)
            
            # Create comment attachment record
            attachment = CommentAttachment(
                comment_id=comment_id,
                file_id=file_upload.id,
                display_name=display_name or file.filename,
                uploaded_by=current_user.id,
                attachment_type="file",
                is_inline=is_inline,
                file_size=file.size,
                mime_type=file.content_type or "application/octet-stream",
                attachment_metadata={
                    "original_filename": file.filename,
                    "upload_timestamp": datetime.utcnow().isoformat()
                }
            )
            attachment_objects.append(attachment)
        
        # Add all attachments to database
        db.add_all(attachment_objects)
        
        # Update comment attachment count
        comment.attachment_count = (comment.attachment_count or 0) + len(attachment_objects)
        
        await db.commit()
        
        # Load attachments with relationships
        result = await db.execute(
            select(CommentAttachment)
            .options(selectinload(CommentAttachment.file))
            .where(CommentAttachment.comment_id == comment_id)
        )
        all_attachments = result.scalars().all()
        
        return {
            "message": f"Successfully attached {len(files)} files to comment",
            "attachment_count": len(attachment_objects),
            "attachments": [
                {
                    "id": attachment.id,
                    "display_name": attachment.display_name,
                    "file_size": attachment.file_size,
                    "mime_type": attachment.mime_type,
                    "is_inline": attachment.is_inline,
                    "is_image": attachment.is_image(),
                    "thumbnail_url": attachment.get_thumbnail_url(),
                    "download_url": f"/api/v1/files/{attachment.file.id}/download",
                    "preview_url": attachment.get_preview_url()
                }
                for attachment in attachment_objects
            ]
        }
        
    except Exception as e:
        # Clean up uploaded files if database operation fails
        for file_upload in uploaded_files:
            await file_service.delete_file(file_upload.id, current_user.id)
        
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to attach files: {str(e)}")


@router.get("/comments/{comment_id}/attachments")
async def get_comment_attachments(
    comment_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get all attachments for a comment."""
    
    comment = await db.get(TaskCommentEnhanced, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    result = await db.execute(
        select(CommentAttachment)
        .options(selectinload(CommentAttachment.file))
        .where(CommentAttachment.comment_id == comment_id)
        .order_by(CommentAttachment.created_at)
    )
    attachments = result.scalars().all()
    
    attachment_data = []
    for attachment in attachments:
        attachment_data.append({
            "id": attachment.id,
            "display_name": attachment.display_name,
            "file_id": attachment.file_id,
            "file_size": attachment.file_size,
            "mime_type": attachment.mime_type,
            "is_inline": attachment.is_inline,
            "is_image": attachment.is_image(),
            "attachment_type": attachment.attachment_type,
            "thumbnail_url": attachment.get_thumbnail_url(),
            "preview_url": attachment.get_preview_url(),
            "download_url": f"/api/v1/files/{attachment.file.id}/download",
            "metadata": attachment.attachment_metadata,
            "uploaded_at": attachment.created_at,
            "uploaded_by": {
                "id": current_user.id,
                "name": current_user.first_name + " " + current_user.last_name
            }
        })
    
    return {
        "attachments": attachment_data,
        "total_attachments": len(attachments),
        "total_size": sum(a.file_size for a in attachments if a.file_size),
        "has_images": any(a.is_image() for a in attachments)
    }


@router.delete("/attachments/{attachment_id}")
async def remove_comment_attachment(
    attachment_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Remove an attachment from a comment."""
    
    attachment = await db.get(CommentAttachment, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    # Load comment to check permissions
    comment = await db.get(TaskCommentEnhanced, attachment.comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Parent comment not found")
    
    # Check permissions (comment author or file uploader)
    if comment.user_id != current_user.id and attachment.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot remove this attachment")
    
    # Delete the file through file service
    file_service = FileManagementService(db)
    await file_service.delete_file(attachment.file_id, current_user.id)
    
    # Remove attachment record
    await db.delete(attachment)
    
    # Update comment attachment count
    comment.attachment_count = max(0, (comment.attachment_count or 1) - 1)
    
    await db.commit()
    
    return {"message": "Attachment removed successfully", "attachment_id": attachment_id}


@router.post("/comments/{comment_id}/attachments/inline-image")
async def upload_inline_image(
    comment_id: int,
    image: UploadFile = FastAPIFile(...),
    alt_text: Optional[str] = Form(None),
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Upload an inline image for rich text editor integration."""
    
    comment = await db.get(TaskCommentEnhanced, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Validate image file
    if not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    if image.size > 10 * 1024 * 1024:  # 10MB limit for images
        raise HTTPException(status_code=400, detail="Image exceeds 10MB limit")
    
    # Upload image
    file_service = FileManagementService(db)
    file_upload = await file_service.create_file_upload(
        file=image,
        user_id=current_user.id,
        category=FileType.IMAGE,
        access_level=FileVisibility.PRIVATE,
        description=f"Inline image for comment {comment_id}",
        metadata={
            "comment_id": comment_id,
            "task_id": comment.task_id,
            "is_inline_image": True,
            "alt_text": alt_text
        }
    )
    
    # Create inline attachment
    attachment = CommentAttachment(
        comment_id=comment_id,
        file_id=file_upload.id,
        display_name=alt_text or image.filename,
        uploaded_by=current_user.id,
        attachment_type="inline_image",
        is_inline=True,
        file_size=image.size,
        mime_type=image.content_type,
        attachment_metadata={
            "alt_text": alt_text,
            "is_inline_image": True
        }
    )
    
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)
    
    # Generate thumbnail if needed
    thumbnail_url = attachment.get_thumbnail_url()
    preview_url = attachment.get_preview_url()
    
    return {
        "attachment_id": attachment.id,
        "file_id": file_upload.id,
        "inline_url": f"/api/v1/files/{file_upload.id}/view",
        "thumbnail_url": thumbnail_url,
        "preview_url": preview_url,
        "alt_text": alt_text,
        "file_size": image.size,
        "dimensions": file_upload.metadata.get("dimensions") if file_upload.metadata else None,
        "markdown_embed": f"![{alt_text or 'Image'}]({preview_url})"
    }


@router.get("/attachments/{attachment_id}/preview")
async def get_attachment_preview(
    attachment_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get preview information for an attachment."""
    
    result = await db.execute(
        select(CommentAttachment)
        .options(selectinload(CommentAttachment.file))
        .where(CommentAttachment.id == attachment_id)
    )
    attachment = result.scalar_one_or_none()
    
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    # Generate preview based on file type
    preview_data = {
        "id": attachment.id,
        "display_name": attachment.display_name,
        "mime_type": attachment.mime_type,
        "file_size": attachment.file_size,
        "is_image": attachment.is_image(),
        "is_video": attachment.mime_type.startswith('video/') if attachment.mime_type else False,
        "is_document": attachment.mime_type in [
            'application/pdf', 'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ] if attachment.mime_type else False,
        "thumbnail_url": attachment.get_thumbnail_url(),
        "preview_url": attachment.get_preview_url(),
        "download_url": f"/api/v1/files/{attachment.file.id}/download"
    }
    
    # Add type-specific preview data
    if attachment.is_image():
        if attachment.file and attachment.file.metadata:
            preview_data["dimensions"] = attachment.file.metadata.get("dimensions")
            preview_data["color_palette"] = attachment.file.metadata.get("color_palette")
    
    return preview_data


@router.post("/comments/{comment_id}/attachments/bulk-upload")
async def bulk_upload_attachments(
    comment_id: int,
    files: List[UploadFile] = FastAPIFile(...),
    folder_structure: Optional[str] = Form(None),
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Handle bulk file upload (drag & drop folders, multiple files)."""
    
    comment = await db.get(TaskCommentEnhanced, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Validate bulk upload limits
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 files per bulk upload")
    
    total_size = sum(file.size for file in files)
    if total_size > 500 * 1024 * 1024:  # 500MB total limit
        raise HTTPException(status_code=400, detail="Total upload size exceeds 500MB limit")
    
    file_service = FileManagementService(db)
    successful_uploads = []
    failed_uploads = []
    
    for file in files:
        try:
            # Upload each file
            file_upload = await file_service.create_file_upload(
                file=file,
                user_id=current_user.id,
                category=FileType.DOCUMENT,
                access_level=FileVisibility.PRIVATE,
                description=f"Bulk upload attachment for comment {comment_id}",
                metadata={
                    "comment_id": comment_id,
                    "task_id": comment.task_id,
                    "bulk_upload": True,
                    "folder_structure": folder_structure
                }
            )
            
            # Create attachment
            attachment = CommentAttachment(
                comment_id=comment_id,
                file_id=file_upload.id,
                display_name=file.filename,
                uploaded_by=current_user.id,
                attachment_type="file",
                is_inline=False,
                file_size=file.size,
                mime_type=file.content_type or "application/octet-stream",
                attachment_metadata={
                    "bulk_upload": True,
                    "folder_structure": folder_structure
                }
            )
            
            db.add(attachment)
            successful_uploads.append({
                "filename": file.filename,
                "attachment_id": None,  # Will be set after commit
                "file_size": file.size
            })
            
        except Exception as e:
            failed_uploads.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    try:
        await db.commit()
        
        # Update comment attachment count
        comment.attachment_count = (comment.attachment_count or 0) + len(successful_uploads)
        await db.commit()
        
        return {
            "message": f"Bulk upload completed: {len(successful_uploads)} successful, {len(failed_uploads)} failed",
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
            "total_files": len(files),
            "success_count": len(successful_uploads),
            "failure_count": len(failed_uploads)
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk upload failed: {str(e)}")