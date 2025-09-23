"""
WebSocket endpoints for real-time collaboration.
Handles live updates, notifications, and team presence.
"""
import json
import uuid
import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.websocket import connection_manager, MessageType
from app.models.user import User
from app.models.project import Project
from app.models.task import Task

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
    db: AsyncSession = Depends(get_db)
):
    """Main WebSocket endpoint for real-time collaboration."""
    
    connection_id = str(uuid.uuid4())
    user = None
    
    try:
        # Accept connection
        await connection_manager.connect(websocket, connection_id)
        
        # Authenticate user
        user = await connection_manager.authenticate_connection(
            websocket, connection_id, token, db
        )
        
        if not user:
            await websocket.close(code=4001, reason="Authentication failed")
            return
        
        # Send initial presence data
        await connection_manager.send_message(
            websocket,
            MessageType.NOTIFICATION,
            {
                "message": "Connected to TeamFlow real-time collaboration",
                "user_id": user.id,
                "connection_id": connection_id
            }
        )
        
        # Main message handling loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                message_type = message.get("type")
                message_data = message.get("data", {})
                
                # Handle different message types
                await handle_websocket_message(
                    user, connection_id, message_type, message_data, db
                )
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await connection_manager.send_message(
                    websocket,
                    MessageType.ERROR,
                    {"error": "Invalid JSON message format"}
                )
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await connection_manager.send_message(
                    websocket,
                    MessageType.ERROR,
                    {"error": "Internal server error"}
                )
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        # Clean up connection
        await connection_manager.disconnect(connection_id, user.id if user else None)


async def handle_websocket_message(
    user: User,
    connection_id: str,
    message_type: str,
    data: Dict[str, Any],
    db: AsyncSession
) -> None:
    """Handle incoming WebSocket messages based on type."""
    
    try:
        if message_type == "subscribe_project":
            await handle_subscribe_project(user, connection_id, data, db)
        
        elif message_type == "subscribe_task":
            await handle_subscribe_task(user, connection_id, data, db)
        
        elif message_type == "unsubscribe_project":
            await handle_unsubscribe_project(user, connection_id, data)
        
        elif message_type == "unsubscribe_task":
            await handle_unsubscribe_task(user, connection_id, data)
        
        elif message_type == "typing_start":
            await handle_typing_indicator(user, connection_id, data, True)
        
        elif message_type == "typing_stop":
            await handle_typing_indicator(user, connection_id, data, False)
        
        elif message_type == "get_presence":
            await handle_get_presence(user, connection_id, data)
        
        elif message_type == "heartbeat":
            await handle_heartbeat(user, connection_id)
        
        else:
            await connection_manager.send_to_user(
                user.id,
                MessageType.ERROR,
                {"error": f"Unknown message type: {message_type}"}
            )
    
    except Exception as e:
        logger.error(f"Error handling message type {message_type}: {e}")
        await connection_manager.send_to_user(
            user.id,
            MessageType.ERROR,
            {"error": f"Error processing {message_type}"}
        )


async def handle_subscribe_project(
    user: User,
    connection_id: str,
    data: Dict[str, Any],
    db: AsyncSession
) -> None:
    """Handle project subscription."""
    
    project_id = data.get("project_id")
    if not project_id:
        await connection_manager.send_to_user(
            user.id,
            MessageType.ERROR,
            {"error": "project_id is required"}
        )
        return
    
    # Verify user has access to project
    # This would integrate with existing project access logic
    project = await db.get(Project, project_id)
    if not project:
        await connection_manager.send_to_user(
            user.id,
            MessageType.ERROR,
            {"error": "Project not found"}
        )
        return
    
    # Subscribe to project
    await connection_manager.subscribe_to_project(user.id, project_id, connection_id)
    
    # Send current presence
    presence = await connection_manager.get_project_presence(project_id)
    await connection_manager.send_to_user(
        user.id,
        MessageType.NOTIFICATION,
        {
            "message": f"Subscribed to project {project.name}",
            "project_id": project_id,
            "presence": presence
        }
    )


async def handle_subscribe_task(
    user: User,
    connection_id: str,
    data: Dict[str, Any],
    db: AsyncSession
) -> None:
    """Handle task subscription."""
    
    task_id = data.get("task_id")
    if not task_id:
        await connection_manager.send_to_user(
            user.id,
            MessageType.ERROR,
            {"error": "task_id is required"}
        )
        return
    
    # Verify user has access to task
    task = await db.get(Task, task_id)
    if not task:
        await connection_manager.send_to_user(
            user.id,
            MessageType.ERROR,
            {"error": "Task not found"}
        )
        return
    
    # Subscribe to task
    await connection_manager.subscribe_to_task(user.id, task_id, connection_id)
    
    await connection_manager.send_to_user(
        user.id,
        MessageType.NOTIFICATION,
        {
            "message": f"Subscribed to task {task.title}",
            "task_id": task_id
        }
    )


async def handle_unsubscribe_project(
    user: User,
    connection_id: str,
    data: Dict[str, Any]
) -> None:
    """Handle project unsubscription."""
    
    project_id = data.get("project_id")
    if not project_id:
        return
    
    # Remove from project subscriptions
    if project_id in connection_manager.project_subscriptions:
        if user.id in connection_manager.project_subscriptions[project_id]:
            connection_manager.project_subscriptions[project_id][user.id].discard(connection_id)
            if not connection_manager.project_subscriptions[project_id][user.id]:
                del connection_manager.project_subscriptions[project_id][user.id]
    
    await connection_manager.send_to_user(
        user.id,
        MessageType.NOTIFICATION,
        {
            "message": f"Unsubscribed from project {project_id}",
            "project_id": project_id
        }
    )


async def handle_unsubscribe_task(
    user: User,
    connection_id: str,
    data: Dict[str, Any]
) -> None:
    """Handle task unsubscription."""
    
    task_id = data.get("task_id")
    if not task_id:
        return
    
    # Remove from task subscriptions
    if task_id in connection_manager.task_subscriptions:
        if user.id in connection_manager.task_subscriptions[task_id]:
            connection_manager.task_subscriptions[task_id][user.id].discard(connection_id)
            if not connection_manager.task_subscriptions[task_id][user.id]:
                del connection_manager.task_subscriptions[task_id][user.id]
    
    await connection_manager.send_to_user(
        user.id,
        MessageType.NOTIFICATION,
        {
            "message": f"Unsubscribed from task {task_id}",
            "task_id": task_id
        }
    )


async def handle_typing_indicator(
    user: User,
    connection_id: str,
    data: Dict[str, Any],
    is_typing: bool
) -> None:
    """Handle typing indicators."""
    
    task_id = data.get("task_id")
    if not task_id:
        await connection_manager.send_to_user(
            user.id,
            MessageType.ERROR,
            {"error": "task_id is required for typing indicators"}
        )
        return
    
    await connection_manager.handle_typing_indicator(
        user.id, task_id, connection_id, is_typing
    )


async def handle_get_presence(
    user: User,
    connection_id: str,
    data: Dict[str, Any]
) -> None:
    """Handle presence request."""
    
    project_id = data.get("project_id")
    if not project_id:
        await connection_manager.send_to_user(
            user.id,
            MessageType.ERROR,
            {"error": "project_id is required"}
        )
        return
    
    presence = await connection_manager.get_project_presence(project_id)
    await connection_manager.send_to_user(
        user.id,
        MessageType.NOTIFICATION,
        {
            "type": "presence_update",
            "project_id": project_id,
            "presence": presence
        }
    )


async def handle_heartbeat(user: User, connection_id: str) -> None:
    """Handle heartbeat to keep connection alive."""
    
    await connection_manager.send_to_user(
        user.id,
        MessageType.HEARTBEAT,
        {
            "timestamp": connection_manager._get_current_timestamp(),
            "connection_id": connection_id
        }
    )


# Utility functions for triggering real-time updates from other parts of the application

async def notify_task_created(task: Task, created_by_user_id: int) -> None:
    """Notify users about a new task creation."""
    
    await connection_manager.broadcast_to_project(
        task.project_id,
        MessageType.TASK_CREATED,
        {
            "task_id": task.id,
            "task_title": task.title,
            "project_id": task.project_id,
            "created_by": created_by_user_id,
            "assignee_id": task.assignee_id,
            "status": task.status,
            "priority": task.priority,
            "timestamp": task.created_at.isoformat() if task.created_at else None
        },
        exclude_user=created_by_user_id
    )


async def notify_task_updated(task: Task, updated_by_user_id: int, changes: Dict[str, Any]) -> None:
    """Notify users about task updates."""
    
    # Broadcast to project subscribers
    await connection_manager.broadcast_to_project(
        task.project_id,
        MessageType.TASK_UPDATED,
        {
            "task_id": task.id,
            "task_title": task.title,
            "project_id": task.project_id,
            "updated_by": updated_by_user_id,
            "changes": changes,
            "timestamp": task.updated_at.isoformat() if task.updated_at else None
        },
        exclude_user=updated_by_user_id
    )
    
    # Broadcast to task subscribers
    await connection_manager.broadcast_to_task(
        task.id,
        MessageType.TASK_UPDATED,
        {
            "task_id": task.id,
            "changes": changes,
            "updated_by": updated_by_user_id,
            "timestamp": task.updated_at.isoformat() if task.updated_at else None
        },
        exclude_user=updated_by_user_id
    )


async def notify_task_status_changed(
    task: Task, 
    old_status: str, 
    new_status: str, 
    updated_by_user_id: int
) -> None:
    """Notify users about task status changes."""
    
    await connection_manager.broadcast_to_project(
        task.project_id,
        MessageType.TASK_STATUS_CHANGED,
        {
            "task_id": task.id,
            "task_title": task.title,
            "project_id": task.project_id,
            "old_status": old_status,
            "new_status": new_status,
            "updated_by": updated_by_user_id,
            "timestamp": task.updated_at.isoformat() if task.updated_at else None
        },
        exclude_user=updated_by_user_id
    )


async def notify_task_assigned(
    task: Task, 
    old_assignee_id: Optional[int], 
    new_assignee_id: Optional[int],
    updated_by_user_id: int
) -> None:
    """Notify users about task assignment changes."""
    
    # Notify old assignee
    if old_assignee_id:
        await connection_manager.send_to_user(
            old_assignee_id,
            MessageType.TASK_ASSIGNED,
            {
                "task_id": task.id,
                "task_title": task.title,
                "project_id": task.project_id,
                "action": "unassigned",
                "updated_by": updated_by_user_id,
                "timestamp": task.updated_at.isoformat() if task.updated_at else None
            }
        )
    
    # Notify new assignee
    if new_assignee_id:
        await connection_manager.send_to_user(
            new_assignee_id,
            MessageType.TASK_ASSIGNED,
            {
                "task_id": task.id,
                "task_title": task.title,
                "project_id": task.project_id,
                "action": "assigned",
                "updated_by": updated_by_user_id,
                "timestamp": task.updated_at.isoformat() if task.updated_at else None
            }
        )
    
    # Broadcast to project
    await connection_manager.broadcast_to_project(
        task.project_id,
        MessageType.TASK_ASSIGNED,
        {
            "task_id": task.id,
            "task_title": task.title,
            "old_assignee_id": old_assignee_id,
            "new_assignee_id": new_assignee_id,
            "updated_by": updated_by_user_id,
            "timestamp": task.updated_at.isoformat() if task.updated_at else None
        },
        exclude_user=updated_by_user_id
    )


async def notify_comment_added(comment_data: Dict[str, Any], task: Task) -> None:
    """Notify users about new comments."""
    
    await connection_manager.broadcast_to_task(
        task.id,
        MessageType.COMMENT_ADDED,
        {
            "comment_id": comment_data["id"],
            "task_id": task.id,
            "task_title": task.title,
            "project_id": task.project_id,
            "content": comment_data["content"],
            "user_id": comment_data["user_id"],
            "user_name": comment_data.get("user_name"),
            "timestamp": comment_data["created_at"]
        },
        exclude_user=comment_data["user_id"]
    )


async def notify_mention_created(mention_data: Dict[str, Any], task: Task) -> None:
    """Notify users about @mentions."""
    
    # Notify the mentioned user directly
    await connection_manager.send_to_user(
        mention_data["mentioned_user_id"],
        MessageType.MENTION_CREATED,
        {
            "mention_id": mention_data["id"],
            "task_id": task.id,
            "task_title": task.title,
            "project_id": task.project_id,
            "mentioned_by_user_id": mention_data["mentioned_by_user_id"],
            "mentioned_by_name": mention_data.get("mentioned_by_name"),
            "context": mention_data["context"],
            "context_type": mention_data["context_type"],
            "timestamp": mention_data["created_at"]
        }
    )


async def notify_time_tracking_started(time_log_data: Dict[str, Any], task: Task) -> None:
    """Notify users about time tracking start."""
    
    await connection_manager.broadcast_to_project(
        task.project_id,
        MessageType.TIME_TRACKING_STARTED,
        {
            "time_log_id": time_log_data["id"],
            "task_id": task.id,
            "task_title": task.title,
            "user_id": time_log_data["user_id"],
            "user_name": time_log_data.get("user_name"),
            "description": time_log_data.get("description"),
            "timestamp": time_log_data["start_time"]
        },
        exclude_user=time_log_data["user_id"]
    )


async def notify_time_tracking_stopped(time_log_data: Dict[str, Any], task: Task) -> None:
    """Notify users about time tracking stop."""
    
    await connection_manager.broadcast_to_project(
        task.project_id,
        MessageType.TIME_TRACKING_STOPPED,
        {
            "time_log_id": time_log_data["id"],
            "task_id": task.id,
            "task_title": task.title,
            "user_id": time_log_data["user_id"],
            "user_name": time_log_data.get("user_name"),
            "duration_minutes": time_log_data["duration_minutes"],
            "is_billable": time_log_data.get("is_billable"),
            "timestamp": time_log_data["end_time"]
        },
        exclude_user=time_log_data["user_id"]
    )