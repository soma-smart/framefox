import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from sqlmodel import Field

from framefox.core.orm.abstract_entity import AbstractEntity


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class Task(AbstractEntity, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    queue: str = "default"
    payload: str = ""  # JSON serialized data
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    max_retries: int = 3
    retry_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    scheduled_for: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def set_payload(self, data: Dict[str, Any]) -> None:
        self.payload = json.dumps(data)

    def get_payload(self) -> Dict[str, Any]:
        return json.loads(self.payload) if self.payload else {}
