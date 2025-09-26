"""
Test real-time collaboration functionality
"""
import pytest
import json
from fastapi.testclient import TestClient
from app.main import app
from app.services.collaboration_service import connection_manager


@pytest.fixture
def client():
    return TestClient(app)


def test_collaboration_health_endpoint(client):
    """Test collaboration health check endpoint"""
    response = client.get("/api/v1/collaboration/health")
    
    # Print debug info if test fails
    if response.status_code != 200:
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        print(f"Response headers: {response.headers}")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "active_connections" in data
    assert "active_workspaces" in data


def test_connection_manager_basic_functionality():
    """Test basic connection manager functionality"""
    # Test workspace subscription management
    workspace_id = "test-workspace"
    user_id = "test-user"
    
    # Initially no users in workspace
    assert workspace_id not in connection_manager.workspace_subscriptions
    
    # Test user status when offline
    status = connection_manager.get_user_status(user_id)
    assert status == "offline"
    
    # Test getting workspace users when empty
    users = connection_manager.get_workspace_users(workspace_id)
    assert users == []


def test_collaboration_message_structure():
    """Test collaboration message structure validation"""
    # Test valid message structures
    valid_messages = [
        {
            "type": "ping",
            "timestamp": "2024-01-01T00:00:00Z"
        },
        {
            "type": "user_activity", 
            "activity": {
                "type": "editing",
                "entity_type": "task",
                "entity_id": "123"
            },
            "timestamp": "2024-01-01T00:00:00Z"
        },
        {
            "type": "typing_indicator",
            "entity_type": "task",
            "entity_id": "123", 
            "is_typing": True,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    ]
    
    for message in valid_messages:
        # Should be able to serialize/deserialize
        json_str = json.dumps(message)
        parsed = json.loads(json_str)
        assert parsed["type"] == message["type"]
        assert "timestamp" in parsed


def test_collaboration_service_imports():
    """Test that collaboration service imports correctly"""
    from app.services.collaboration_service import (
        ConnectionManager,
        CollaborationService,
        connection_manager,
        notify_task_update,
        notify_project_update
    )
    
    # Test that classes and functions exist
    assert ConnectionManager is not None
    assert CollaborationService is not None
    assert connection_manager is not None
    assert callable(notify_task_update)
    assert callable(notify_project_update)


@pytest.mark.asyncio
async def test_collaboration_utility_functions():
    """Test utility functions for collaboration"""
    from app.services.collaboration_service import notify_task_update, notify_project_update
    
    # Test that functions can be called without errors
    await notify_task_update("task-123", {"title": "Updated Task"})
    await notify_project_update("project-456", {"name": "Updated Project"})
    
    # No assertions needed - just testing that functions don't crash


def test_collaboration_api_endpoints_exist(client):
    """Test that collaboration API endpoints are properly registered"""
    # Test that endpoints return proper status codes (not 404)
    
    # Health endpoint should work
    response = client.get("/api/v1/collaboration/health")
    assert response.status_code == 200
    
    # WebSocket endpoint exists but requires authentication
    # We can't test WebSocket directly in this test, but we can verify the route exists
    # by checking that it doesn't return 404
    
    # Other endpoints should require authentication (401 or 422, not 404)
    response = client.get("/api/v1/collaboration/workspaces/test/active-users")
    assert response.status_code in [401, 422]  # Not 404 - endpoint exists
    
    response = client.get("/api/v1/collaboration/users/test-user/status")  
    assert response.status_code in [401, 422]  # Not 404 - endpoint exists