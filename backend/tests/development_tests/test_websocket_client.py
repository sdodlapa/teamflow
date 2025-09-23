"""
Simple WebSocket client test for TeamFlow real-time collaboration.
This demonstrates how to connect to the WebSocket endpoint and receive real-time updates.
"""
import asyncio
import json
import websockets
from datetime import datetime

# Configuration
WEBSOCKET_URL = "ws://127.0.0.1:8001/api/v1/realtime/ws"
# You'll need a valid JWT token for authentication
TEST_TOKEN = "your_jwt_token_here"


async def websocket_client_demo():
    """Demonstrate WebSocket connection and real-time collaboration features."""
    
    try:
        print("🚀 Connecting to TeamFlow WebSocket...")
        
        # Connect with authentication token
        uri = f"{WEBSOCKET_URL}?token={TEST_TOKEN}"
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to TeamFlow WebSocket!")
            
            # Send subscription messages
            await send_message(websocket, "subscribe_project", {"project_id": 1})
            await send_message(websocket, "subscribe_task", {"task_id": 1})
            
            print("📡 Subscribed to project and task updates")
            print("🎧 Listening for real-time updates...\n")
            
            # Listen for messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await handle_message(data)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON received: {message}")
                except KeyboardInterrupt:
                    print("\n👋 Disconnecting...")
                    break
    
    except ConnectionRefusedError:
        print("❌ Failed to connect. Make sure the server is running on http://127.0.0.1:8001")
    except websockets.exceptions.InvalidStatusCode as e:
        if e.status_code == 401:
            print("❌ Authentication failed. Please provide a valid JWT token.")
        else:
            print(f"❌ Connection failed with status {e.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")


async def send_message(websocket, message_type: str, data: dict):
    """Send a message to the WebSocket server."""
    message = {
        "type": message_type,
        "data": data
    }
    await websocket.send(json.dumps(message))


async def handle_message(data: dict):
    """Handle incoming WebSocket messages and display them."""
    
    message_type = data.get("type", "unknown")
    message_data = data.get("data", {})
    timestamp = data.get("timestamp", datetime.now().isoformat())
    
    # Format timestamp for display
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        time_str = dt.strftime("%H:%M:%S")
    except:
        time_str = timestamp[:8] if len(timestamp) > 8 else timestamp
    
    print(f"[{time_str}] ", end="")
    
    if message_type == "auth_success":
        print(f"🔐 Authenticated as user {message_data.get('user_name')} (ID: {message_data.get('user_id')})")
    
    elif message_type == "task_created":
        print(f"📝 New task created: '{message_data.get('task_title')}' in project {message_data.get('project_id')}")
    
    elif message_type == "task_updated":
        changes = message_data.get('changes', {})
        task_title = message_data.get('task_title', 'Unknown')
        print(f"✏️  Task updated: '{task_title}' - {len(changes)} changes")
        for field, change in changes.items():
            print(f"    • {field}: {change.get('old')} → {change.get('new')}")
    
    elif message_type == "task_status_changed":
        task_title = message_data.get('task_title', 'Unknown')
        old_status = message_data.get('old_status')
        new_status = message_data.get('new_status')
        print(f"🔄 Task status changed: '{task_title}' ({old_status} → {new_status})")
    
    elif message_type == "task_assigned":
        task_title = message_data.get('task_title', 'Unknown')
        action = message_data.get('action', 'assigned')
        print(f"👤 Task {action}: '{task_title}'")
    
    elif message_type == "comment_added":
        task_title = message_data.get('task_title', 'Unknown')
        user_name = message_data.get('user_name', 'Someone')
        content = message_data.get('content', '')[:50] + "..." if len(message_data.get('content', '')) > 50 else message_data.get('content', '')
        print(f"💬 New comment on '{task_title}' by {user_name}: {content}")
    
    elif message_type == "mention_created":
        task_title = message_data.get('task_title', 'Unknown')
        mentioned_by_name = message_data.get('mentioned_by_name', 'Someone')
        print(f"🔔 You were mentioned in '{task_title}' by {mentioned_by_name}")
    
    elif message_type == "time_tracking_started":
        task_title = message_data.get('task_title', 'Unknown')
        user_name = message_data.get('user_name', 'Someone')
        print(f"⏱️  {user_name} started tracking time on '{task_title}'")
    
    elif message_type == "time_tracking_stopped":
        task_title = message_data.get('task_title', 'Unknown')
        user_name = message_data.get('user_name', 'Someone')
        duration = message_data.get('duration_minutes', 0)
        print(f"⏹️  {user_name} stopped tracking time on '{task_title}' ({duration} minutes)")
    
    elif message_type == "user_joined":
        user_id = message_data.get('user_id')
        project_id = message_data.get('project_id')
        print(f"👋 User {user_id} joined project {project_id}")
    
    elif message_type == "user_left":
        user_id = message_data.get('user_id')
        project_id = message_data.get('project_id')
        print(f"👋 User {user_id} left project {project_id}")
    
    elif message_type == "user_typing":
        user_id = message_data.get('user_id')
        task_id = message_data.get('task_id')
        print(f"✍️  User {user_id} is typing in task {task_id}")
    
    elif message_type == "user_stopped_typing":
        user_id = message_data.get('user_id')
        task_id = message_data.get('task_id')
        print(f"✍️  User {user_id} stopped typing in task {task_id}")
    
    elif message_type == "notification":
        message_text = message_data.get('message', 'No message')
        print(f"🔔 {message_text}")
    
    elif message_type == "error":
        error = message_data.get('error', 'Unknown error')
        print(f"❌ Error: {error}")
    
    elif message_type == "heartbeat":
        print("💓 Heartbeat")
    
    else:
        print(f"📨 {message_type}: {json.dumps(message_data, indent=2)}")


async def send_test_messages(websocket):
    """Send some test messages to demonstrate WebSocket functionality."""
    
    await asyncio.sleep(2)
    
    # Test typing indicators
    print("\n🧪 Sending test typing indicator...")
    await send_message(websocket, "typing_start", {"task_id": 1})
    await asyncio.sleep(3)
    await send_message(websocket, "typing_stop", {"task_id": 1})
    
    # Test presence request
    print("🧪 Requesting presence information...")
    await send_message(websocket, "get_presence", {"project_id": 1})
    
    # Send heartbeat
    await asyncio.sleep(2)
    print("🧪 Sending heartbeat...")
    await send_message(websocket, "heartbeat", {})


def main():
    """Main function to run the WebSocket client demo."""
    
    print("=" * 60)
    print("🔗 TeamFlow WebSocket Client Demo")
    print("=" * 60)
    print("\n📋 Instructions:")
    print("1. Make sure the TeamFlow server is running on http://127.0.0.1:8001")
    print("2. Update TEST_TOKEN with a valid JWT token")
    print("3. Watch for real-time updates as you interact with the API")
    print("\n" + "=" * 60 + "\n")
    
    if TEST_TOKEN == "your_jwt_token_here":
        print("⚠️  Warning: Please set a valid JWT token in TEST_TOKEN variable")
        print("   You can get a token by logging in through the API at:")
        print("   POST http://127.0.0.1:8001/api/v1/auth/login")
        print("\n   For testing, you can temporarily modify the WebSocket endpoint")
        print("   to skip authentication or use a test token.\n")
    
    try:
        asyncio.run(websocket_client_demo())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()