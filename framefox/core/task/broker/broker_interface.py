from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from framefox.core.task.entity.task import Task, TaskStatus

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class BrokerInterface(ABC):
    """
    Common interface for all task brokers.
    """

    @abstractmethod
    def enqueue(
        self,
        name: str,
        payload: Dict[str, Any],
        queue: str = "default",
        priority: int = 0,
        scheduled_for: Optional[datetime] = None,
        max_retries: int = 3,
    ) -> Task:
        """Adds a task to the queue."""
        pass

    @abstractmethod
    def dequeue(self, queue: str = "default", batch_size: int = 1) -> List[Task]:
        """Retrieves tasks from the queue for processing."""
        pass

    @abstractmethod
    def complete_task(self, task: Task) -> None:
        """Marks a task as successfully completed."""
        pass

    @abstractmethod
    def fail_task(self, task: Task, error: str) -> None:
        """Marks a task as failed."""
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieves a task by its identifier."""
        pass

    @abstractmethod
    def get_tasks_by_status(
        self, status: TaskStatus, queue: str = None, limit: int = 100
    ) -> List[Task]:
        """Retrieves tasks by status."""
        pass

    @abstractmethod
    def purge_failed_tasks(self, older_than_days: int = 30) -> int:
        """Cleans up failed tasks older than X days."""
        pass
