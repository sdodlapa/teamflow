"""
WebSocket manager for real-time collaboration features.
Handles live updates, notifications, and team presence.
"""
import json
import logging
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.core.security import verify_token

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types for real-time collaboration."""
    
    # Authentication
    AUTH = "auth"
    AUTH_SUCCESS = "auth_success"
    AUTH_ERROR = "auth_error"
    
    # Task updates
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_STATUS_CHANGED = "task_status_changed"
    TASK_ASSIGNED = "task_assigned"
    
    # Comments and mentions
    COMMENT_ADDED = "comment_added"
    COMMENT_UPDATED = "comment_updated"
    COMMENT_DELETED = "comment_deleted"
    MENTION_CREATED = "mention_created"
    
    # Time tracking
    TIME_TRACKING_STARTED = "time_tracking_started"
    TIME_TRACKING_STOPPED = "time_tracking_stopped"
    
    # Presence and collaboration
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    USER_TYPING = "user_typing"
    USER_STOPPED_TYPING = "user_stopped_typing"
    
    # Project updates
    PROJECT_UPDATED = "project_updated"
    PROJECT_MEMBER_ADDED = "project_member_added"
    PROJECT_MEMBER_REMOVED = "project_member_removed"
    
    # System notifications
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


class ConnectionManager:
    """Manages WebSocket connections for real-time collaboration."""
    
    def __init__(self):
        # Active connections: {user_id: {connection_id: websocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        
        # Project subscriptions: {project_id: {user_id: connection_ids}}
        self.project_subscriptions: Dict[int, Dict[int, Set[str]]] = {}
        
        # Task subscriptions: {task_id: {user_id: connection_ids}}
        self.task_subscriptions: Dict[int, Dict[int, Set[str]]] = {}
        
        # User presence: {project_id: {user_id: {last_seen, status, current_task}}}
        self.user_presence: Dict[int, Dict[int, Dict[str, Any]]] = {}
        
        # Typing indicators: {task_id: {user_id: {started_at, connection_id}}}
        self.typing_indicators: Dict[int, Dict[int, Dict[str, Any]]] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        logger.info(f"WebSocket connection accepted: {connection_id}")
    
    async def disconnect(self, connection_id: str, user_id: Optional[int] = None) -> None:
        """Handle WebSocket disconnection."""
        if user_id:
            # Remove from active connections
            if user_id in self.active_connections:
                self.active_connections[user_id].pop(connection_id, None)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Remove from project subscriptions
            for project_id, users in self.project_subscriptions.items():
                if user_id in users:
                    users[user_id].discard(connection_id)
                    if not users[user_id]:
                        del users[user_id]
            
            # Remove from task subscriptions
            for task_id, users in self.task_subscriptions.items():
                if user_id in users:
                    users[user_id].discard(connection_id)
                    if not users[user_id]:
                        del users[user_id]
            
            # Update presence
            await self._update_user_presence(user_id, "offline")
            
            # Clear typing indicators
            await self._clear_typing_indicators(user_id, connection_id)
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def authenticate_connection(
        self, 
        websocket: WebSocket, 
        connection_id: str, 
        token: str,
        db: AsyncSession
    ) -> Optional[User]:
        """Authenticate WebSocket connection using JWT token."""
        try:
            # Verify JWT token
            user_email = verify_token(token)
            if not user_email:
                await self.send_message(
                    websocket, 
                    MessageType.AUTH_ERROR, 
                    {"error": "Invalid token"}
                )
                return None
            
            # Get user from database
            user = await User.get_by_email(db, email=user_email)
            if not user:
                await self.send_message(
                    websocket, 
                    MessageType.AUTH_ERROR, 
                    {"error": "User not found"}
                )
                return None
            
            # Store connection
            if user.id not in self.active_connections:
                self.active_connections[user.id] = {}
            self.active_connections[user.id][connection_id] = websocket
            
            # Update user presence
            await self._update_user_presence(user.id, "online")
            
            # Send authentication success
            await self.send_message(
                websocket,
                MessageType.AUTH_SUCCESS,
                {
                    "user_id": user.id,
                    "user_name": user.full_name,
                    "connection_id": connection_id
                }
            )
            
            logger.info(f"User {user.id} authenticated on connection {connection_id}")
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            await self.send_message(
                websocket,
                MessageType.AUTH_ERROR,
                {"error": "Authentication failed"}
            )
            return None
    
    async def subscribe_to_project(
        self, 
        user_id: int, 
        project_id: int, 
        connection_id: str
    ) -> None:
        """Subscribe user to project updates."""
        if project_id not in self.project_subscriptions:
            self.project_subscriptions[project_id] = {}
        
        if user_id not in self.project_subscriptions[project_id]:
            self.project_subscriptions[project_id][user_id] = set()
        
        self.project_subscriptions[project_id][user_id].add(connection_id)
        
        # Update presence for this project
        if project_id not in self.user_presence:
            self.user_presence[project_id] = {}
        
        self.user_presence[project_id][user_id] = {
            "last_seen": datetime.utcnow(),
            "status": "online",
            "current_task": None
        }
        
        # Notify other users
        await self.broadcast_to_project(
            project_id,
            MessageType.USER_JOINED,
            {
                "user_id": user_id,
                "project_id": project_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )
        
        logger.info(f"User {user_id} subscribed to project {project_id}")
    
    async def subscribe_to_task(
        self, 
        user_id: int, 
        task_id: int, 
        connection_id: str
    ) -> None:
        """Subscribe user to task updates."""
        if task_id not in self.task_subscriptions:
            self.task_subscriptions[task_id] = {}
        
        if user_id not in self.task_subscriptions[task_id]:
            self.task_subscriptions[task_id][user_id] = set()
        
        self.task_subscriptions[task_id][user_id].add(connection_id)
        logger.info(f"User {user_id} subscribed to task {task_id}")
    
    async def send_message(
        self, 
        websocket: WebSocket, 
        message_type: MessageType, 
        data: Dict[str, Any]
    ) -> None:
        """Send a message to a specific WebSocket connection."""
        try:
            message = {
                "type": message_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def send_to_user(
        self, 
        user_id: int, 
        message_type: MessageType, 
        data: Dict[str, Any]
    ) -> None:
        """Send a message to all connections of a specific user."""
        if user_id in self.active_connections:
            for connection_id, websocket in self.active_connections[user_id].items():
                try:
                    await self.send_message(websocket, message_type, data)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}, connection {connection_id}: {e}")
                    # Remove failed connection
                    await self.disconnect(connection_id, user_id)
    
    async def broadcast_to_project(
        self, 
        project_id: int, 
        message_type: MessageType, 
        data: Dict[str, Any],
        exclude_user: Optional[int] = None
    ) -> None:
        """Broadcast a message to all users subscribed to a project."""
        if project_id not in self.project_subscriptions:
            return
        
        for user_id, connection_ids in self.project_subscriptions[project_id].items():
            if exclude_user and user_id == exclude_user:
                continue
            
            if user_id in self.active_connections:
                for connection_id in connection_ids:
                    if connection_id in self.active_connections[user_id]:
                        websocket = self.active_connections[user_id][connection_id]
                        try:
                            await self.send_message(websocket, message_type, data)
                        except Exception as e:
                            logger.error(f"Error broadcasting to project {project_id}, user {user_id}: {e}")
    
    async def broadcast_to_task(
        self, 
        task_id: int, 
        message_type: MessageType, 
        data: Dict[str, Any],
        exclude_user: Optional[int] = None
    ) -> None:
        """Broadcast a message to all users subscribed to a task."""
        if task_id not in self.task_subscriptions:
            return
        
        for user_id, connection_ids in self.task_subscriptions[task_id].items():
            if exclude_user and user_id == exclude_user:
                continue
            
            if user_id in self.active_connections:
                for connection_id in connection_ids:
                    if connection_id in self.active_connections[user_id]:
                        websocket = self.active_connections[user_id][connection_id]
                        try:
                            await self.send_message(websocket, message_type, data)
                        except Exception as e:
                            logger.error(f"Error broadcasting to task {task_id}, user {user_id}: {e}")
    
    async def handle_typing_indicator(
        self, 
        user_id: int, 
        task_id: int, 
        connection_id: str,
        is_typing: bool
    ) -> None:
        """Handle typing indicators for real-time collaboration."""
        if is_typing:
            # Start typing
            if task_id not in self.typing_indicators:
                self.typing_indicators[task_id] = {}
            
            self.typing_indicators[task_id][user_id] = {
                "started_at": datetime.utcnow(),
                "connection_id": connection_id
            }
            
            await self.broadcast_to_task(
                task_id,
                MessageType.USER_TYPING,
                {
                    "user_id": user_id,
                    "task_id": task_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                exclude_user=user_id
            )
        else:
            # Stop typing
            if task_id in self.typing_indicators and user_id in self.typing_indicators[task_id]:
                del self.typing_indicators[task_id][user_id]
                
                await self.broadcast_to_task(
                    task_id,
                    MessageType.USER_STOPPED_TYPING,
                    {
                        "user_id": user_id,
                        "task_id": task_id,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    exclude_user=user_id
                )
    
    async def get_project_presence(self, project_id: int) -> Dict[str, Any]:
        """Get current user presence for a project."""
        if project_id not in self.user_presence:
            return {"online_users": [], "total_online": 0}
        
        online_users = []
        for user_id, presence in self.user_presence[project_id].items():
            if presence["status"] == "online":
                online_users.append({
                    "user_id": user_id,
                    "last_seen": presence["last_seen"].isoformat(),
                    "current_task": presence["current_task"]
                })
        
        return {
            "online_users": online_users,
            "total_online": len(online_users)
        }
    
    async def _update_user_presence(
        self, 
        user_id: int, 
        status: str,
        current_task: Optional[int] = None
    ) -> None:
        """Update user presence across all subscribed projects."""
        for project_id in self.user_presence:
            if user_id in self.user_presence[project_id]:
                self.user_presence[project_id][user_id].update({
                    "last_seen": datetime.utcnow(),
                    "status": status,
                    "current_task": current_task
                })
    
    async def _clear_typing_indicators(self, user_id: int, connection_id: str) -> None:
        """Clear typing indicators for a disconnected user."""
        tasks_to_clear = []
        for task_id, typing_users in self.typing_indicators.items():
            if user_id in typing_users and typing_users[user_id]["connection_id"] == connection_id:
                tasks_to_clear.append(task_id)
        
        for task_id in tasks_to_clear:
            if user_id in self.typing_indicators[task_id]:
                del self.typing_indicators[task_id][user_id]
                
                await self.broadcast_to_task(
                    task_id,
                    MessageType.USER_STOPPED_TYPING,
                    {
                        "user_id": user_id,
                        "task_id": task_id,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    exclude_user=user_id
                )
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        return datetime.utcnow().isoformat()


# Global connection manager instance
connection_manager = ConnectionManager()