import json
from abc import ABC, abstractmethod

from framefox.core.websocket.web_socket_manager import WebSocketManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class WebSocketEventHandler(ABC):

    @abstractmethod
    async def on_connect(self, connection_id: str, user_id: str = None, room: str = None):
        pass

    @abstractmethod
    async def on_disconnect(self, connection_id: str):
        pass

    @abstractmethod
    async def on_message(self, connection_id: str, raw_message: str):
        pass


class EchoHandler(WebSocketEventHandler):
    """
    WebSocket event handler that echoes back received messages to the sender.
    This handler implements a simple echo functionality where any message received
    from a WebSocket connection is parsed and sent back to the same connection
    with additional metadata including the original message and echo type information.
    The handler processes JSON messages and creates an echo response containing:
    - type: Set to "echo" to identify the message type
    - data: The original data from the received message
    - message: Copy of the original data
    - original_message: The complete original message for reference
    If message parsing fails, the handler silently ignores the error without
    sending any response back to the client.
    """

    async def on_connect(self, connection_id: str, user_id: str = None, room: str = None):
        pass

    async def on_disconnect(self, connection_id: str):
        pass

    async def on_message(self, connection_id: str, raw_message: str):

        manager = WebSocketManager()

        try:
            message = json.loads(raw_message)
            echo_message = {
                "type": "echo",
                "data": message.get("data"),
                "message": message.get("data"),
                "original_message": message,
            }

            await manager.send_to_connection(connection_id, echo_message)
        except Exception:
            pass


class BroadcastHandler(WebSocketEventHandler):
    """
    WebSocket event handler for broadcasting messages to rooms.
    This handler manages WebSocket connections and broadcasts messages between users
    in different rooms. It handles user join notifications, message broadcasting,
    and connection lifecycle events.
    Attributes:
        Inherits from WebSocketEventHandler to provide WebSocket event handling capabilities.
    Methods:
        on_connect: Handles new WebSocket connections and broadcasts join notifications.
        on_disconnect: Handles WebSocket disconnections.
        on_message: Processes incoming messages and broadcasts them to appropriate rooms.
    """

    async def on_connect(self, connection_id: str, user_id: str = None, room: str = None):
        if room:

            manager = WebSocketManager()

            join_message = {
                "type": "user_joined",
                "data": {"user_id": user_id, "room": room},
                "message": f"Utilisateur {connection_id[:8]} a rejoint {room}",
            }

            await manager.broadcast_to_room(room, join_message, connection_id)

    async def on_disconnect(self, connection_id: str):
        pass

    async def on_message(self, connection_id: str, raw_message: str):
        manager = WebSocketManager()

        try:
            message = json.loads(raw_message)

            metadata = manager.connection_metadata.get(connection_id, {})
            rooms = metadata.get("rooms", set())

            broadcast_message = {
                "type": "message",
                "data": message.get("data"),
                "user": message.get("username", f"User-{connection_id[:8]}"),
                "message": message.get("data"),
            }

            for room in rooms:
                await manager.broadcast_to_room(room, broadcast_message, exclude=connection_id)

        except Exception as e:
            print(f"Broadcast error: {e}")
