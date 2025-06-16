from abc import ABC, abstractmethod
from typing import List

from framefox.core.task.entity.task import Task

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class TransportInterface(ABC):
    """Interface for task message transport"""

    @abstractmethod
    def publish(self, task: Task) -> None:
        """Publishes a task to the transport"""
        pass

    @abstractmethod
    def consume(self, queue: str, batch_size: int) -> List[Task]:
        """Consumes tasks from the transport"""
        pass

    @abstractmethod
    def acknowledge(self, task: Task) -> None:
        """Confirms that a task has been processed"""
        pass

    @abstractmethod
    def reject(self, task: Task, requeue: bool = False) -> None:
        """Rejects a task"""
        pass

    @abstractmethod
    def setup(self, queues: List[str]) -> None:
        """Configures the transport"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Gracefully shuts down the transport"""
        pass
