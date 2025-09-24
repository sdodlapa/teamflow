"""
WebSocket endpoints for real-time enhanced comment features.

Provides WebSocket connections for:
- Live comment updates and notifications
- Real-time @mention alerts
- User presence and typing indicators
- Comment activity streams
"""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any, Optional
import asyncio

from app.core.database import get_db
from app.models.user import User
from app.models.task import Task
from app.services.comment_websocket import comment_ws_manager
from app.core.dependencies import get_current_active_user
from app.schemas.user import UserRead

router = APIRouter()


async def get_websocket_user(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Authenticate WebSocket connection using query parameter token.
    This is a simplified version - in production, use proper JWT validation.
    """
    try:
        # For now, use a simple approach - in production, validate JWT token
        # This would typically involve JWT decoding and user lookup
        result = await db.execute(
            select(User).where(User.email == token)  # Simplified for demo
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.status == "active":
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")


@router.websocket("/tasks/{task_id}/comments/ws")
async def websocket_comment_endpoint(
    websocket: WebSocket,
    task_id: int,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time comment features on a specific task.
    
    Message types handled:
    - typing_start: User started typing
    - typing_stop: User stopped typing  
    - comment_preview: Live comment preview while typing
    - presence_ping: Keep connection alive
    """
    
    user = None
    
    try:
        # Authenticate user
        result = await db.execute(
            select(User).where(User.email == token)
        )
        user = result.scalar_one_or_none()
        
        if not user or user.status != "active":
            await websocket.close(code=4001, reason="Authentication failed")
            return
        
        # Verify task access (basic check)
        task = await db.get(Task, task_id)
        if not task:
            await websocket.close(code=4004, reason="Task not found")
            return
        
        # Convert to UserRead for compatibility
        user_read = UserRead(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            status=user.status
        )
        
        # Connect to WebSocket manager
        await comment_ws_manager.connect(websocket, task_id, user_read)
        
        # Send welcome message
        await comment_ws_manager.send_personal_message({
            "type": "connected",
            "data": {
                "message": f"Connected to task {task_id} comment stream",
                "user_id": str(user.id),
                "task_id": task_id
            }
        }, websocket)
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            message_data = message.get("data", {})
            
            if message_type == "typing_start":
                await comment_ws_manager.broadcast_typing_indicator(
                    task_id, user.id, True
                )
                
            elif message_type == "typing_stop":
                await comment_ws_manager.broadcast_typing_indicator(
                    task_id, user.id, False
                )
                
            elif message_type == "comment_preview":
                # Broadcast live comment preview (optional feature)
                preview_content = message_data.get("content", "")
                if len(preview_content) > 10:  # Only broadcast substantial previews
                    await comment_ws_manager.broadcast_to_task({
                        "type": "comment_preview",
                        "data": {
                            "user_id": str(user.id),
                            "user_name": user.first_name + " " + user.last_name,
                            "preview_content": preview_content[:200],  # Limit preview length
                            "is_preview": True
                        }
                    }, task_id, exclude_user_id=user.id)
                    
            elif message_type == "presence_ping":
                # Keep connection alive and update last seen
                await comment_ws_manager.send_personal_message({
                    "type": "presence_pong",
                    "data": {"status": "alive"}
                }, websocket)
                
            elif message_type == "get_task_stats":
                # Send real-time task statistics
                stats = comment_ws_manager.get_task_stats(task_id)
                await comment_ws_manager.send_personal_message({
                    "type": "task_stats",
                    "data": stats
                }, websocket)
                
            else:
                # Unknown message type
                await comment_ws_manager.send_personal_message({
                    "type": "error",
                    "data": {
                        "message": f"Unknown message type: {message_type}",
                        "received_type": message_type
                    }
                }, websocket)
                
    except WebSocketDisconnect:
        if user:
            comment_ws_manager.disconnect(websocket)
            
    except json.JSONDecodeError:
        await comment_ws_manager.send_personal_message({
            "type": "error",
            "data": {"message": "Invalid JSON format"}
        }, websocket)
        
    except Exception as e:
        await comment_ws_manager.send_personal_message({
            "type": "error", 
            "data": {"message": f"Server error: {str(e)}"}
        }, websocket)
        
        if user:
            comment_ws_manager.disconnect(websocket)


@router.websocket("/mentions/ws")
async def websocket_mentions_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for global mention notifications.
    Connects user to receive mention alerts across all tasks.
    """
    
    user = None
    
    try:
        # Authenticate user
        result = await db.execute(
            select(User).where(User.email == token)
        )
        user = result.scalar_one_or_none()
        
        if not user or user.status != "active":
            await websocket.close(code=4001, reason="Authentication failed")
            return
        
        await websocket.accept()
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "mentions_connected",
            "data": {
                "message": "Connected to global mentions stream",
                "user_id": str(user.id)
            },
            "timestamp": "2025-09-24T10:00:00Z"
        }))
        
        # Keep connection alive and listen for client messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "data": {"status": "alive"},
                        "timestamp": "2025-09-24T10:00:00Z"
                    }))
                    
            except WebSocketDisconnect:
                break
            except:
                # Continue listening even if there are message parsing errors
                continue
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        if websocket.client_state.name == "CONNECTED":
            await websocket.send_text(json.dumps({
                "type": "error",
                "data": {"message": f"Connection error: {str(e)}"},
                "timestamp": "2025-09-24T10:00:00Z"
            }))


# WebSocket utility functions for integration with comment APIs

async def notify_comment_created(comment_data: Dict[str, Any], task_id: int, user_id: str):
    """Utility function to notify WebSocket clients of new comments."""
    await comment_ws_manager.broadcast_comment_created(comment_data, task_id, user_id)


async def notify_comment_updated(comment_data: Dict[str, Any], task_id: int, user_id: str):
    """Utility function to notify WebSocket clients of comment updates."""
    await comment_ws_manager.broadcast_comment_updated(comment_data, task_id, user_id)


async def notify_comment_deleted(comment_id: int, task_id: int, user_id: str):
    """Utility function to notify WebSocket clients of comment deletions."""
    await comment_ws_manager.broadcast_comment_deleted(comment_id, task_id, user_id)


async def notify_mention_created(mention_data: Dict[str, Any], mentioned_user_id: str):
    """Utility function to notify specific user of new mentions."""
    await comment_ws_manager.broadcast_mention_notification(mention_data, mentioned_user_id)


# Background task for WebSocket health monitoring
async def websocket_health_monitor():
    """
    Background task to monitor WebSocket connection health.
    Runs periodic cleanup and health checks.
    """
    while True:
        try:
            # Clean up expired typing indicators
            await comment_ws_manager.cleanup_expired_typing()
            
            # Add other health monitoring tasks here
            # - Connection timeout cleanup
            # - Memory usage monitoring
            # - Performance metrics collection
            
            await asyncio.sleep(30)  # Run every 30 seconds
            
        except Exception as e:
            print(f"WebSocket health monitor error: {e}")
            await asyncio.sleep(60)  # Wait longer if there's an error


# Start the health monitor when an event loop is available
def start_websocket_background_tasks():
    """Start WebSocket background tasks."""
    try:
        asyncio.create_task(websocket_health_monitor())
    except RuntimeError:
        # No event loop running, will be started when app starts
        pass