"""
Real-time Collaboration Service
Handles WebSocket connections, user presence, and live updates
"""

from typing import Dict, Set, Optional, Any, List
import asyncio
import json
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
import redis.asyncio as redis

from app.core.database import get_db
from app.models.user import User
from app.models.task import Task
from app.models.project import Project
from app.core.config import settings


class ConnectionManager:
    """Manages WebSocket connections and real-time communication"""
    
    def __init__(self):
        # Active connections: {user_id: {websocket, workspace_id, last_seen}}
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        # Workspace subscriptions: {workspace_id: set(user_ids)}
        self.workspace_subscriptions: Dict[str, Set[str]] = {}
        # Redis for multi-instance coordination
        self.redis = None
        
    async def connect(
        self, 
        websocket: WebSocket, 
        user_id: str, 
        workspace_id: str
    ):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Store connection info
        self.active_connections[user_id] = {
            "websocket": websocket,
            "workspace_id": workspace_id,
            "last_seen": datetime.utcnow(),
            "status": "online"
        }
        
        # Subscribe to workspace
        if workspace_id not in self.workspace_subscriptions:
            self.workspace_subscriptions[workspace_id] = set()
        self.workspace_subscriptions[workspace_id].add(user_id)
        
        # Broadcast user joined
        await self.broadcast_to_workspace(workspace_id, {
            "type": "user_presence",
            "action": "joined",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        print(f"User {user_id} connected to workspace {workspace_id}")
        
    async def disconnect(self, user_id: str):
        """Handle WebSocket disconnection"""
        if user_id in self.active_connections:
            connection_info = self.active_connections[user_id]
            workspace_id = connection_info["workspace_id"]
            
            # Remove from active connections
            del self.active_connections[user_id]
            
            # Remove from workspace subscription
            if workspace_id in self.workspace_subscriptions:
                self.workspace_subscriptions[workspace_id].discard(user_id)
                if not self.workspace_subscriptions[workspace_id]:
                    del self.workspace_subscriptions[workspace_id]
            
            # Broadcast user left
            await self.broadcast_to_workspace(workspace_id, {
                "type": "user_presence", 
                "action": "left",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            print(f"User {user_id} disconnected from workspace {workspace_id}")
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to specific user"""
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]["websocket"]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error sending message to user {user_id}: {e}")
                await self.disconnect(user_id)
    
    async def broadcast_to_workspace(self, workspace_id: str, message: dict):
        """Broadcast message to all users in workspace"""
        if workspace_id in self.workspace_subscriptions:
            disconnected_users = []
            
            for user_id in self.workspace_subscriptions[workspace_id]:
                if user_id in self.active_connections:
                    websocket = self.active_connections[user_id]["websocket"]
                    try:
                        await websocket.send_text(json.dumps(message))
                    except Exception as e:
                        print(f"Error broadcasting to user {user_id}: {e}")
                        disconnected_users.append(user_id)
            
            # Clean up disconnected users
            for user_id in disconnected_users:
                await self.disconnect(user_id)
    
    async def broadcast_task_update(self, task_id: str, update_data: dict):
        """Broadcast task updates to relevant workspaces"""
        # Get task's project to determine workspace
        # This would be enhanced with proper database lookup
        message = {
            "type": "task_update",
            "task_id": task_id,
            "data": update_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # For now, broadcast to all workspaces (would be optimized)
        for workspace_id in self.workspace_subscriptions:
            await self.broadcast_to_workspace(workspace_id, message)
    
    async def broadcast_project_update(self, project_id: str, update_data: dict):
        """Broadcast project updates to relevant workspaces"""
        message = {
            "type": "project_update",
            "project_id": project_id,
            "data": update_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # For now, broadcast to all workspaces (would be optimized)
        for workspace_id in self.workspace_subscriptions:
            await self.broadcast_to_workspace(workspace_id, message)
    
    def get_workspace_users(self, workspace_id: str) -> List[str]:
        """Get list of active users in workspace"""
        return list(self.workspace_subscriptions.get(workspace_id, set()))
    
    def get_user_status(self, user_id: str) -> Optional[str]:
        """Get user's current status"""
        if user_id in self.active_connections:
            return self.active_connections[user_id]["status"]
        return "offline"
    
    async def update_user_activity(self, user_id: str, activity: dict):
        """Update user's current activity"""
        if user_id in self.active_connections:
            connection_info = self.active_connections[user_id]
            connection_info["last_seen"] = datetime.utcnow()
            connection_info["current_activity"] = activity
            
            # Broadcast activity update
            workspace_id = connection_info["workspace_id"]
            await self.broadcast_to_workspace(workspace_id, {
                "type": "user_activity",
                "user_id": user_id,
                "activity": activity,
                "timestamp": datetime.utcnow().isoformat()
            })


# Global connection manager instance
connection_manager = ConnectionManager()


class CollaborationService:
    """Service for collaboration features"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def handle_real_time_comment(
        self, 
        user_id: str, 
        entity_type: str, 
        entity_id: str, 
        comment_data: dict
    ):
        """Handle real-time comment creation"""
        # Create comment in database (using existing comment service)
        # This would integrate with existing comment endpoints
        
        # Broadcast to relevant users
        message = {
            "type": "new_comment",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "comment": comment_data,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to all relevant workspaces
        for workspace_id in connection_manager.workspace_subscriptions:
            await connection_manager.broadcast_to_workspace(workspace_id, message)
    
    async def handle_typing_indicator(
        self, 
        user_id: str, 
        entity_type: str, 
        entity_id: str, 
        is_typing: bool
    ):
        """Handle typing indicators for comments"""
        if user_id in connection_manager.active_connections:
            connection_info = connection_manager.active_connections[user_id]
            workspace_id = connection_info["workspace_id"]
            
            message = {
                "type": "typing_indicator",
                "entity_type": entity_type,
                "entity_id": entity_id,
                "user_id": user_id,
                "is_typing": is_typing,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await connection_manager.broadcast_to_workspace(workspace_id, message)
    
    async def get_active_collaborators(self, workspace_id: str) -> List[dict]:
        """Get list of active collaborators in workspace"""
        active_users = []
        user_ids = connection_manager.get_workspace_users(workspace_id)
        
        for user_id in user_ids:
            if user_id in connection_manager.active_connections:
                conn_info = connection_manager.active_connections[user_id]
                active_users.append({
                    "user_id": user_id,
                    "status": conn_info["status"],
                    "last_seen": conn_info["last_seen"].isoformat(),
                    "current_activity": conn_info.get("current_activity", {})
                })
        
        return active_users


# Utility functions for integration with existing endpoints
async def notify_task_update(task_id: str, update_data: dict):
    """Utility to notify task updates from existing endpoints"""
    await connection_manager.broadcast_task_update(task_id, update_data)

async def notify_project_update(project_id: str, update_data: dict):
    """Utility to notify project updates from existing endpoints"""
    await connection_manager.broadcast_project_update(project_id, update_data)