"""
WebSocket endpoints for real-time collaboration
"""

from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.responses import JSONResponse
import json

from app.services.collaboration_service import (
    connection_manager, 
    CollaborationService
)
from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/collaboration", tags=["collaboration"])


@router.websocket("/ws/{workspace_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    workspace_id: str,
    token: Optional[str] = Query(None)
):
    """WebSocket endpoint for real-time collaboration"""
    try:
        # Authenticate user via token
        if not token:
            await websocket.close(code=1008, reason="Authentication required")
            return
            
        # For now, extract user_id from token (would use proper JWT validation)
        # This is simplified - in production, use proper JWT validation
        user_id = token  # Temporary - replace with JWT decode
        
        # Connect user to collaboration system
        await connection_manager.connect(websocket, user_id, workspace_id)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                message_type = message.get("type")
                
                if message_type == "ping":
                    # Handle ping/pong for connection health
                    await connection_manager.send_to_user(user_id, {
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })
                
                elif message_type == "user_activity":
                    # Update user's current activity
                    activity = message.get("activity", {})
                    await connection_manager.update_user_activity(user_id, activity)
                
                elif message_type == "typing_indicator":
                    # Handle typing indicators
                    entity_type = message.get("entity_type")
                    entity_id = message.get("entity_id")
                    is_typing = message.get("is_typing", False)
                    
                    # Broadcast typing indicator to workspace
                    await connection_manager.broadcast_to_workspace(workspace_id, {
                        "type": "typing_indicator",
                        "user_id": user_id,
                        "entity_type": entity_type,
                        "entity_id": entity_id,
                        "is_typing": is_typing
                    })
                
                elif message_type == "comment":
                    # Handle real-time comments
                    entity_type = message.get("entity_type")
                    entity_id = message.get("entity_id")
                    comment_text = message.get("text")
                    
                    # Broadcast new comment to workspace
                    await connection_manager.broadcast_to_workspace(workspace_id, {
                        "type": "new_comment",
                        "user_id": user_id,
                        "entity_type": entity_type,
                        "entity_id": entity_id,
                        "text": comment_text,
                        "timestamp": message.get("timestamp")
                    })
                
                else:
                    print(f"Unknown message type: {message_type}")
                    
        except WebSocketDisconnect:
            await connection_manager.disconnect(user_id)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


@router.get("/workspaces/{workspace_id}/active-users")
async def get_active_users(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of active users in workspace"""
    collaboration_service = CollaborationService(db)
    active_users = await collaboration_service.get_active_collaborators(workspace_id)
    
    return {
        "workspace_id": workspace_id,
        "active_users": active_users,
        "total_active": len(active_users)
    }


@router.get("/users/{user_id}/status")
async def get_user_status(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific user's collaboration status"""
    status = connection_manager.get_user_status(user_id)
    
    return {
        "user_id": user_id,
        "status": status,
        "is_online": status != "offline"
    }


@router.post("/workspaces/{workspace_id}/broadcast")
async def broadcast_message(
    workspace_id: str,
    message_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Broadcast message to all users in workspace (admin function)"""
    message = {
        "type": "broadcast",
        "from_user": current_user.id,
        "data": message_data
    }
    
    await connection_manager.broadcast_to_workspace(workspace_id, message)
    
    return {"success": True, "message": "Broadcast sent"}


@router.get("/health")
async def collaboration_health():
    """Health check for collaboration service"""
    total_connections = len(connection_manager.active_connections)
    total_workspaces = len(connection_manager.workspace_subscriptions)
    
    return {
        "status": "healthy",
        "active_connections": total_connections,
        "active_workspaces": total_workspaces
    }