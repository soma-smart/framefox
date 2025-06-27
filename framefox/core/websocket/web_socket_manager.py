import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Set

from fastapi import WebSocket

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class WebSocketManager:
    """
    WebSocket connection manager implementing the Singleton pattern.
    This class manages WebSocket connections, user sessions, and room-based messaging
    for real-time communication. It provides functionality for connecting/disconnecting
    clients, organizing them into rooms, and broadcasting messages.
    Attributes:
        connections (Dict[str, WebSocket]): Active WebSocket connections indexed by connection ID
        rooms (Dict[str, Set[str]]): Room memberships with connection IDs
        users (Dict[str, Set[str]]): User sessions mapping user IDs to connection IDs
        connection_metadata (Dict[str, Dict[str, Any]]): Additional connection information
        logger (logging.Logger): Logger instance for WebSocket operations
    Features:
        - Singleton pattern ensures single manager instance
        - Connection lifecycle management (connect/disconnect)
        - Room-based messaging and user grouping
        - Broadcast capabilities to rooms and individual users
        - Connection statistics and monitoring
        - Automatic cleanup on disconnection
        - Error handling and logging
    Usage:
        manager = WebSocketManager()
        await manager.connect(websocket, "conn_1", user_id="user_1", room="chat")
        await manager.broadcast_to_room("chat", {"message": "Hello"})
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, Set[str]] = {}
        self.users: Dict[str, Set[str]] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger("WEBSOCKET_MANAGER")
        WebSocketManager._initialized = True

    async def connect(self, websocket: WebSocket, connection_id: str, user_id: Optional[str] = None, room: Optional[str] = None) -> bool:
        try:
            await websocket.accept()

            self.connections[connection_id] = websocket
            self.connection_metadata[connection_id] = {
                "user_id": user_id,
                "rooms": set([room] if room else []),
                "connected_at": datetime.now(),
            }

            if user_id:
                if user_id not in self.users:
                    self.users[user_id] = set()
                self.users[user_id].add(connection_id)

            if room:
                await self.join_room(connection_id, room)

            return True

        except Exception as e:
            self.logger.error(f"WebSocket connection error: {e}")
            return False

    async def disconnect(self, connection_id: str):
        if connection_id not in self.connections:
            return

        metadata = self.connection_metadata.get(connection_id, {})
        user_id = metadata.get("user_id")
        rooms = metadata.get("rooms", set())

        for room in list(rooms):
            await self.leave_room(connection_id, room)

        if user_id and user_id in self.users:
            self.users[user_id].discard(connection_id)
            if not self.users[user_id]:
                del self.users[user_id]

        del self.connections[connection_id]
        del self.connection_metadata[connection_id]

    async def send_to_connection(self, connection_id: str, message: dict) -> bool:
        if connection_id not in self.connections:
            return False

        try:
            await self.connections[connection_id].send_text(json.dumps(message))
            return True
        except Exception as e:
            self.logger.error(f"Error sending message to {connection_id}: {e}")
            await self.disconnect(connection_id)
            return False

    async def broadcast_to_room(self, room: str, message: dict, exclude: Optional[str] = None) -> int:
        if room not in self.rooms:
            return 0

        sent_count = 0
        for connection_id in list(self.rooms[room]):
            if connection_id != exclude:
                if await self.send_to_connection(connection_id, message):
                    sent_count += 1

        return sent_count

    async def send_to_user(self, user_id: str, message: dict) -> int:
        if user_id not in self.users:
            return 0

        sent_count = 0
        for connection_id in list(self.users[user_id]):
            if await self.send_to_connection(connection_id, message):
                sent_count += 1

        return sent_count

    async def join_room(self, connection_id: str, room: str) -> bool:
        if connection_id not in self.connections:
            return False

        if room not in self.rooms:
            self.rooms[room] = set()

        self.rooms[room].add(connection_id)
        if connection_id in self.connection_metadata:
            self.connection_metadata[connection_id]["rooms"].add(room)

        return True

    async def leave_room(self, connection_id: str, room: str) -> bool:
        if room in self.rooms:
            self.rooms[room].discard(connection_id)
            if not self.rooms[room]:
                del self.rooms[room]

        if connection_id in self.connection_metadata:
            self.connection_metadata[connection_id]["rooms"].discard(room)

        return True

    def get_stats(self) -> dict:
        return {
            "total_connections": len(self.connections),
            "total_users": len(self.users),
            "total_rooms": len(self.rooms),
            "rooms": {room: len(connections) for room, connections in self.rooms.items()},
        }
