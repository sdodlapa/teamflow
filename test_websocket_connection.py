#!/usr/bin/env python3
"""
Quick test script to verify WebSocket connection to the TeamFlow backend.
"""

import asyncio
import websockets
import json
import sys
from typing import Optional

async def test_websocket_connection():
    """Test WebSocket connection to TeamFlow backend"""
    uri = "ws://localhost:8000/realtime/ws"
    
    try:
        print(f"🔌 Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")
            
            # Send a test message
            test_message = {
                "type": "ping",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 Sent test message")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received response: {response}")
                return True
                
            except asyncio.TimeoutError:
                print("⏰ No response received within 5 seconds")
                return False
                
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Invalid status code: {e}")
        if e.status_code == 401:
            print("🔐 This might be due to authentication requirements")
        return False
        
    except ConnectionRefusedError:
        print("❌ Connection refused - is the backend server running?")
        return False
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Testing TeamFlow WebSocket Connection\n")
    
    success = await test_websocket_connection()
    
    if success:
        print("\n✅ WebSocket test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ WebSocket test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())