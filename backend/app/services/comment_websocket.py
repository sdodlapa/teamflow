"""
Real-time WebSocket handler for enhanced comment system.

Provides live updates for:
- New comment notifications
- @mention alerts in real-time
- Comment editing and deletion updates
- User typing indicators
- Online presence for active commenters
"""

import asyncio
import json
from typing import Dict, Set, List, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.models.task import Task
from app.models.enhanced_comments import TaskCommentEnhanced, CommentMention
from app.schemas.user import UserRead
from app.core.dependencies import get_current_active_user

class CommentWebSocketManager:
    """
    Manages WebSocket connections for real-time comment features.
    
    Features:
    - Room-based connections (per task)
    - User presence tracking
    - Broadcast comment updates
    - Mention notifications
    - Typing indicators
    """
    
    def __init__(self):
        # Active connections by task_id
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        
        # User presence by task_id
        self.user_presence: Dict[int, Dict[UUID, Dict[str, Any]]] = {}
        
        # WebSocket to user mapping
        self.websocket_users: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Typing indicators
        self.typing_users: Dict[int, Dict[UUID, datetime]] = {}
    
    async def connect(self, websocket: WebSocket, task_id: int, user: UserRead):
        """Connect a user to a task's comment room."""
        await websocket.accept()
        
        # Add to connections
        if task_id not in self.active_connections:
            self.active_connections[task_id] = set()
        self.active_connections[task_id].add(websocket)
        
        # Add to user mapping
        self.websocket_users[websocket] = {
            "user_id": user.id,
            "user_name": user.first_name + " " + user.last_name,
            "user_email": user.email,
            "task_id": task_id,
            "connected_at": datetime.utcnow()
        }
        
        # Update presence
        if task_id not in self.user_presence:
            self.user_presence[task_id] = {}
        
        self.user_presence[task_id][user.id] = {
            "user_id": user.id,
            "user_name": user.first_name + " " + user.last_name,
            "status": "online",
            "last_seen": datetime.utcnow(),
            "is_typing": False
        }
        
        # Notify others of user joining
        await self.broadcast_presence_update(task_id, user.id, "joined")
        
        # Send current online users to newly connected user
        await self.send_current_presence(websocket, task_id)
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a user from the comment room."""
        if websocket in self.websocket_users:
            user_info = self.websocket_users[websocket]
            task_id = user_info["task_id"]
            user_id = user_info["user_id"]
            
            # Remove from connections
            if task_id in self.active_connections:
                self.active_connections[task_id].discard(websocket)
                if not self.active_connections[task_id]:
                    del self.active_connections[task_id]
            
            # Update presence
            if task_id in self.user_presence and user_id in self.user_presence[task_id]:
                self.user_presence[task_id][user_id]["status"] = "offline"
                self.user_presence[task_id][user_id]["last_seen"] = datetime.utcnow()
            
            # Remove from typing indicators
            if task_id in self.typing_users and user_id in self.typing_users[task_id]:
                del self.typing_users[task_id][user_id]
            
            # Clean up user mapping
            del self.websocket_users[websocket]
            
            # Notify others of user leaving (async task)
            asyncio.create_task(self.broadcast_presence_update(task_id, user_id, "left"))
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps({
                **message,
                "timestamp": datetime.utcnow().isoformat()
            }))
        except:
            # Connection might be closed
            self.disconnect(websocket)
    
    async def broadcast_to_task(self, message: Dict[str, Any], task_id: int, exclude_user_id: Optional[UUID] = None):
        """Broadcast a message to all users in a task's comment room."""
        if task_id not in self.active_connections:
            return
        
        message_data = {
            **message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        disconnected_websockets = set()
        
        for websocket in self.active_connections[task_id].copy():
            try:
                # Skip if excluding this user
                if exclude_user_id and websocket in self.websocket_users:
                    if self.websocket_users[websocket]["user_id"] == exclude_user_id:
                        continue
                
                await websocket.send_text(json.dumps(message_data))
            except:
                # Connection closed, mark for removal
                disconnected_websockets.add(websocket)
        
        # Clean up disconnected websockets
        for websocket in disconnected_websockets:
            self.disconnect(websocket)
    
    async def broadcast_comment_created(self, comment_data: Dict[str, Any], task_id: int, user_id: UUID):
        """Broadcast new comment to task participants."""
        await self.broadcast_to_task({
            "type": "comment_created",
            "data": comment_data,
            "task_id": task_id
        }, task_id, exclude_user_id=user_id)
    
    async def broadcast_comment_updated(self, comment_data: Dict[str, Any], task_id: int, user_id: UUID):
        """Broadcast comment edit to task participants."""
        await self.broadcast_to_task({
            "type": "comment_updated", 
            "data": comment_data,
            "task_id": task_id
        }, task_id, exclude_user_id=user_id)
    
    async def broadcast_comment_deleted(self, comment_id: int, task_id: int, user_id: UUID):
        """Broadcast comment deletion to task participants."""
        await self.broadcast_to_task({
            "type": "comment_deleted",
            "data": {"comment_id": comment_id},
            "task_id": task_id
        }, task_id, exclude_user_id=user_id)
    
    async def broadcast_mention_notification(self, mention_data: Dict[str, Any], mentioned_user_id: UUID):
        """Send mention notification to specific user across all their active connections."""
        for task_id, connections in self.active_connections.items():
            for websocket in connections.copy():
                if websocket in self.websocket_users:
                    if self.websocket_users[websocket]["user_id"] == mentioned_user_id:
                        await self.send_personal_message({
                            "type": "mention_received",
                            "data": mention_data
                        }, websocket)
    
    async def broadcast_typing_indicator(self, task_id: int, user_id: UUID, is_typing: bool):
        """Broadcast typing indicator status."""
        if task_id not in self.typing_users:
            self.typing_users[task_id] = {}
        
        if is_typing:
            self.typing_users[task_id][user_id] = datetime.utcnow()
        else:
            if user_id in self.typing_users[task_id]:
                del self.typing_users[task_id][user_id]
        
        # Update presence
        if task_id in self.user_presence and user_id in self.user_presence[task_id]:
            self.user_presence[task_id][user_id]["is_typing"] = is_typing
        
        await self.broadcast_to_task({
            "type": "user_typing",
            "data": {
                "user_id": str(user_id),
                "is_typing": is_typing,
                "typing_users": [str(uid) for uid in self.typing_users[task_id].keys()]
            }
        }, task_id, exclude_user_id=user_id)
    
    async def broadcast_presence_update(self, task_id: int, user_id: UUID, action: str):
        """Broadcast user presence changes (joined/left)."""
        presence_data = {}
        if task_id in self.user_presence:
            presence_data = {
                str(uid): {
                    "user_id": str(data["user_id"]),
                    "user_name": data["user_name"],
                    "status": data["status"],
                    "is_typing": data.get("is_typing", False),
                    "last_seen": data["last_seen"].isoformat() if data["last_seen"] else None
                }
                for uid, data in self.user_presence[task_id].items()
            }
        
        await self.broadcast_to_task({
            "type": "presence_update",
            "data": {
                "action": action,
                "user_id": str(user_id),
                "online_users": presence_data
            }
        }, task_id)
    
    async def send_current_presence(self, websocket: WebSocket, task_id: int):
        """Send current online users to a newly connected user."""
        presence_data = {}
        if task_id in self.user_presence:
            presence_data = {
                str(uid): {
                    "user_id": str(data["user_id"]),
                    "user_name": data["user_name"],
                    "status": data["status"],
                    "is_typing": data.get("is_typing", False),
                    "last_seen": data["last_seen"].isoformat() if data["last_seen"] else None
                }
                for uid, data in self.user_presence[task_id].items()
                if data["status"] == "online"
            }
        
        await self.send_personal_message({
            "type": "current_presence",
            "data": {
                "online_users": presence_data,
                "total_online": len(presence_data)
            }
        }, websocket)
    
    async def cleanup_expired_typing(self):
        """Clean up expired typing indicators (background task)."""
        current_time = datetime.utcnow()
        
        for task_id, typing_users in list(self.typing_users.items()):
            expired_users = []
            
            for user_id, last_typing in list(typing_users.items()):
                # Remove typing indicator after 10 seconds of inactivity
                if (current_time - last_typing).total_seconds() > 10:
                    expired_users.append(user_id)
            
            for user_id in expired_users:
                del self.typing_users[task_id][user_id]
                
                # Update presence
                if task_id in self.user_presence and user_id in self.user_presence[task_id]:
                    self.user_presence[task_id][user_id]["is_typing"] = False
                
                # Broadcast update
                await self.broadcast_typing_indicator(task_id, user_id, False)
    
    def get_task_stats(self, task_id: int) -> Dict[str, Any]:
        """Get real-time statistics for a task."""
        online_count = len(self.active_connections.get(task_id, set()))
        typing_count = len(self.typing_users.get(task_id, {}))
        
        return {
            "task_id": task_id,
            "online_users": online_count,
            "typing_users": typing_count,
            "last_activity": datetime.utcnow().isoformat()
        }


# Global WebSocket manager instance
comment_ws_manager = CommentWebSocketManager()


# Background task to clean up expired typing indicators
async def cleanup_typing_indicators():
    """Background task to clean up expired typing indicators."""
    while True:
        await comment_ws_manager.cleanup_expired_typing()
        await asyncio.sleep(5)  # Run every 5 seconds


# Function to start cleanup task (called from main app)
def start_websocket_background_tasks():
    """Start background tasks for WebSocket management."""
    try:
        asyncio.create_task(cleanup_typing_indicators())
    except RuntimeError:
        # No event loop running, background task will be started later
        pass