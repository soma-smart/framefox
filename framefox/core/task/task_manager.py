import logging
from datetime import datetime, timedelta
from typing import Callable, Optional, Union

from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer
from framefox.core.task.broker.broker_interface import BrokerInterface
from framefox.core.task.worker_service_provider import WorkerServiceProvider

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class TaskManager:
    """
    Centralized manager for asynchronous tasks.
    Allows creating and sending tasks to queues in a generic way.
    """

    def __init__(self, broker: BrokerInterface):
        self.broker = broker
        self.logger = logging.getLogger("TASK_MANAGER")
        settings = ServiceContainer().get(Settings)
        self.defaults = settings.task_defaults

    def queue_task(
        self,
        task: Union[str, Callable],
        queue: str = "default",
        priority: int = 0,
        max_retries: int = 3,
        delay: Optional[Union[int, timedelta]] = None,
        schedule_at: Optional[datetime] = None,
        **kwargs,
    ) -> str:
        """
        Adds a task to the queue for asynchronous execution.

        Args:
            task: Reference to the function or full name of the task (module.Class.method)
            queue: Name of the queue
            priority: Task priority (higher = more priority)
            max_retries: Maximum number of retries in case of failure
            delay: Delay before execution (in seconds or timedelta)
            schedule_at: Schedule at a specific date/time
            **kwargs: Arguments to pass to the task

        Returns:
            ID of the created task
        """
        if self.broker is None:
            container = ServiceContainer()
            self.broker = container.get(BrokerInterface)
            if self.broker is None:
                WorkerServiceProvider.register()
                self.broker = container.get(BrokerInterface)
            if self.broker is None:
                raise RuntimeError("Unable to initialize the task broker")

        queue = queue if queue is not None else self.defaults.get("queue")
        priority = priority if priority is not None else self.defaults.get("priority")
        max_retries = (
            max_retries if max_retries is not None else self.defaults.get("max_retries")
        )
        scheduled_for = self._calculate_schedule_time(delay, schedule_at)
        task_name = self._get_task_name(task)
        payload = {"kwargs": kwargs}

        task_entity = self.broker.enqueue(
            name=task_name,
            payload=payload,
            queue=queue,
            priority=priority,
            scheduled_for=scheduled_for,
            max_retries=max_retries,
        )

        self.logger.info(f"Task {task_entity.id} ({task_name}) queued")
        return task_entity.id

    def _get_task_name(self, task: Union[str, Callable]) -> str:
        """Determines the full name of the task from different types of arguments"""
        if isinstance(task, str):
            return task

        if callable(task):
            if hasattr(task, "__qualname__") and "." in task.__qualname__:
                class_name = task.__qualname__.split(".")[0]
                return f"{task.__module__}.{class_name}.{task.__name__}"
            return f"{task.__module__}.{task.__name__}"

        raise ValueError(f"The task type {type(task)} is not supported")

    def _calculate_schedule_time(
        self, delay: Optional[Union[int, timedelta]], schedule_at: Optional[datetime]
    ) -> Optional[datetime]:
        """Calculates the scheduled execution date"""
        if schedule_at:
            return schedule_at
        elif delay:
            if isinstance(delay, int):
                return datetime.now() + timedelta(seconds=delay)
            else:
                return datetime.now() + delay
        return None
