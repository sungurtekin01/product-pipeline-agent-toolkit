"""WebSocket connection manager for real-time pipeline updates"""

from typing import Dict, List
from fastapi import WebSocket
import json


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        # Map of task_id to list of connected websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        self.active_connections[task_id].append(websocket)

    def disconnect(self, websocket: WebSocket, task_id: str):
        """Remove a WebSocket connection"""
        if task_id in self.active_connections:
            self.active_connections[task_id].remove(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

    async def send_message(self, task_id: str, message: dict):
        """Send a message to all connections for a specific task"""
        if task_id in self.active_connections:
            for connection in self.active_connections[task_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending message to websocket: {e}")

    async def broadcast(self, message: dict):
        """Broadcast a message to all active connections"""
        for connections in self.active_connections.values():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error broadcasting message: {e}")


# Global connection manager instance
manager = ConnectionManager()
