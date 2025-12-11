"""Test script to verify WebSocket notifications work."""

import asyncio
import websockets
import json


async def test_websocket_connection():
    """Test WebSocket connection to the notifications endpoint."""
    uri = "ws://localhost:8001/ws/notifications/test_user_123"

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server")

            # Keep listening for messages
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    print(f"Received notification: {data}")
                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket connection closed")
                    break
    except Exception as e:
        print(f"Error connecting to WebSocket: {str(e)}")


if __name__ == "__main__":
    print("Testing WebSocket connection...")
    asyncio.run(test_websocket_connection())