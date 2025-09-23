"""
File management notification functions for real-time updates.
Extends the realtime notification service with file-specific events.
"""
from typing import Optional
from app.core.websocket import get_connection_manager

# Get the connection manager instance
connection_manager = get_connection_manager()


async def notify_file_upload(file_id: int, user_id: int, context_id: Optional[int] = None):
    """
    Notify subscribers about a new file upload.
    
    Args:
        file_id: ID of the uploaded file
        user_id: ID of the user who uploaded the file
        context_id: Project or task ID for context-based notifications
    """
    try:
        # Prepare notification message
        message = {
            "type": "file_uploaded",
            "data": {
                "file_id": file_id,
                "uploaded_by": user_id,
                "context_id": context_id,
                "timestamp": connection_manager._get_timestamp()
            }
        }
        
        # Send to project/task subscribers if context provided
        if context_id:
            await connection_manager.broadcast_to_project(context_id, message)
        
        # Send to organization-wide subscribers
        await connection_manager.broadcast_to_organization(message)
        
    except Exception as e:
        print(f"Error sending file upload notification: {e}")


async def notify_file_delete(file_id: int, user_id: int, context_id: Optional[int] = None):
    """
    Notify subscribers about a file deletion.
    
    Args:
        file_id: ID of the deleted file
        user_id: ID of the user who deleted the file
        context_id: Project or task ID for context-based notifications
    """
    try:
        # Prepare notification message
        message = {
            "type": "file_deleted",
            "data": {
                "file_id": file_id,
                "deleted_by": user_id,
                "context_id": context_id,
                "timestamp": connection_manager._get_timestamp()
            }
        }
        
        # Send to project/task subscribers if context provided
        if context_id:
            await connection_manager.broadcast_to_project(context_id, message)
        
        # Send to organization-wide subscribers
        await connection_manager.broadcast_to_organization(message)
        
    except Exception as e:
        print(f"Error sending file delete notification: {e}")


async def notify_file_shared(file_id: int, user_id: int, share_token: str, context_id: Optional[int] = None):
    """
    Notify subscribers about a file being shared.
    
    Args:
        file_id: ID of the shared file
        user_id: ID of the user who created the share
        share_token: The share token for the file
        context_id: Project or task ID for context-based notifications
    """
    try:
        # Prepare notification message
        message = {
            "type": "file_shared",
            "data": {
                "file_id": file_id,
                "shared_by": user_id,
                "share_token": share_token,
                "context_id": context_id,
                "timestamp": connection_manager._get_timestamp()
            }
        }
        
        # Send to project/task subscribers if context provided
        if context_id:
            await connection_manager.broadcast_to_project(context_id, message)
        
        # Send to organization-wide subscribers
        await connection_manager.broadcast_to_organization(message)
        
    except Exception as e:
        print(f"Error sending file share notification: {e}")


async def notify_file_processing_complete(file_id: int, processing_type: str, success: bool, context_id: Optional[int] = None):
    """
    Notify subscribers about file processing completion (thumbnails, scanning, etc.).
    
    Args:
        file_id: ID of the processed file
        processing_type: Type of processing ('thumbnail', 'scan', 'metadata')
        success: Whether processing was successful
        context_id: Project or task ID for context-based notifications
    """
    try:
        # Prepare notification message
        message = {
            "type": "file_processing_complete",
            "data": {
                "file_id": file_id,
                "processing_type": processing_type,
                "success": success,
                "context_id": context_id,
                "timestamp": connection_manager._get_timestamp()
            }
        }
        
        # Send to project/task subscribers if context provided
        if context_id:
            await connection_manager.broadcast_to_project(context_id, message)
        
        # Send to organization-wide subscribers
        await connection_manager.broadcast_to_organization(message)
        
    except Exception as e:
        print(f"Error sending file processing notification: {e}")


async def notify_file_download(file_id: int, user_id: int, download_method: str, context_id: Optional[int] = None):
    """
    Notify subscribers about a file download.
    
    Args:
        file_id: ID of the downloaded file
        user_id: ID of the user who downloaded the file
        download_method: Method used ('direct', 'preview', 'thumbnail', 'shared')
        context_id: Project or task ID for context-based notifications
    """
    try:
        # Prepare notification message
        message = {
            "type": "file_downloaded",
            "data": {
                "file_id": file_id,
                "downloaded_by": user_id,
                "download_method": download_method,
                "context_id": context_id,
                "timestamp": connection_manager._get_timestamp()
            }
        }
        
        # Send to project/task subscribers if context provided
        if context_id:
            await connection_manager.broadcast_to_project(context_id, message)
        
        # Send to organization-wide subscribers (for audit purposes)
        await connection_manager.broadcast_to_organization(message)
        
    except Exception as e:
        print(f"Error sending file download notification: {e}")


async def notify_bulk_file_action(action: str, file_ids: list, user_id: int, results: dict):
    """
    Notify subscribers about bulk file operations.
    
    Args:
        action: The bulk action performed ('delete', 'move', 'change_visibility')
        file_ids: List of file IDs affected
        user_id: ID of the user who performed the action
        results: Results of the bulk operation
    """
    try:
        # Prepare notification message
        message = {
            "type": "bulk_file_action",
            "data": {
                "action": action,
                "file_ids": file_ids,
                "performed_by": user_id,
                "results": results,
                "timestamp": connection_manager._get_timestamp()
            }
        }
        
        # Send to organization-wide subscribers
        await connection_manager.broadcast_to_organization(message)
        
    except Exception as e:
        print(f"Error sending bulk file action notification: {e}")


async def notify_file_access_granted(file_id: int, granted_to_user_id: int, granted_by_user_id: int, permission_type: str):
    """
    Notify about file access permissions being granted.
    
    Args:
        file_id: ID of the file
        granted_to_user_id: ID of the user receiving access
        granted_by_user_id: ID of the user granting access
        permission_type: Type of permission granted
    """
    try:
        # Prepare notification message
        message = {
            "type": "file_access_granted",
            "data": {
                "file_id": file_id,
                "granted_to": granted_to_user_id,
                "granted_by": granted_by_user_id,
                "permission_type": permission_type,
                "timestamp": connection_manager._get_timestamp()
            }
        }
        
        # Send to the user receiving access
        await connection_manager.send_to_user(granted_to_user_id, message)
        
        # Send to the user granting access (confirmation)
        await connection_manager.send_to_user(granted_by_user_id, message)
        
    except Exception as e:
        print(f"Error sending file access notification: {e}")


async def notify_file_quota_warning(user_id: int, organization_id: int, usage_percentage: float):
    """
    Notify about file storage quota warnings.
    
    Args:
        user_id: ID of the user to notify
        organization_id: ID of the organization
        usage_percentage: Current storage usage percentage
    """
    try:
        # Prepare notification message
        message = {
            "type": "file_quota_warning",
            "data": {
                "organization_id": organization_id,
                "usage_percentage": usage_percentage,
                "timestamp": connection_manager._get_timestamp()
            }
        }
        
        # Send to specific user (admin)
        await connection_manager.send_to_user(user_id, message)
        
    except Exception as e:
        print(f"Error sending quota warning notification: {e}")


async def notify_file_scan_result(file_id: int, scan_status: str, user_id: int, context_id: Optional[int] = None):
    """
    Notify about file security scan results.
    
    Args:
        file_id: ID of the scanned file
        scan_status: Result of the scan ('clean', 'infected', 'error')
        user_id: ID of the file uploader
        context_id: Project or task ID for context
    """
    try:
        # Prepare notification message
        message = {
            "type": "file_scan_result",
            "data": {
                "file_id": file_id,
                "scan_status": scan_status,
                "uploader_id": user_id,
                "context_id": context_id,
                "timestamp": connection_manager._get_timestamp()
            }
        }
        
        # Send to file uploader
        await connection_manager.send_to_user(user_id, message)
        
        # If scan failed or file infected, notify project/task subscribers
        if scan_status in ["infected", "error"] and context_id:
            await connection_manager.broadcast_to_project(context_id, message)
        
    except Exception as e:
        print(f"Error sending file scan notification: {e}")