from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Set

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


@dataclass
class WebSocketMessage:
    """
    Standardized WebSocket message data structure.
    This dataclass represents a WebSocket message with metadata including type, data payload,
    timestamp, sender information, and routing details for room-based or targeted messaging.
    Attributes:
        type (str): The message type identifier
        data (Any): The message payload data
        timestamp (datetime): When the message was created, defaults to current time
        sender_id (Optional[str]): Identifier of the message sender
        room (Optional[str]): Room identifier for broadcast messages
        target (Optional[str]): Specific target identifier for direct messages
    Methods:
        to_dict() -> dict: Converts the message to a dictionary representation with
                        ISO format timestamp for JSON serialization
    """

    type: str
    data: Any
    timestamp: datetime = field(default_factory=datetime.now)
    sender_id: Optional[str] = None
    room: Optional[str] = None
    target: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "sender_id": self.sender_id,
            "room": self.room,
            "target": self.target,
        }


@dataclass
class WebSocketConnection:
    """Representation of a WebSocket connection"""

    connection_id: str
    user_id: Optional[str] = None
    rooms: Set[str] = field(default_factory=set)
    metadata: dict = field(default_factory=dict)
    connected_at: datetime = field(default_factory=datetime.now)
