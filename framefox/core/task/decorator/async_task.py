import asyncio
import functools
from datetime import datetime, timedelta
from typing import Callable, Optional, Union

from framefox.core.di.service_container import ServiceContainer
from framefox.core.task.broker.broker_interface import BrokerInterface
from framefox.core.task.worker_manager import WorkerManager


class AsyncTask:
    def __init__(
        self,
        queue: str = "default",
        priority: int = 0,
        max_retries: int = 3,
        delay: Optional[Union[int, timedelta]] = None,
        schedule_at: Optional[datetime] = None,
    ):
        self.queue = queue
        self.priority = priority
        self.max_retries = max_retries
        self.delay = delay
        self.schedule_at = schedule_at

    def __call__(self, func: Callable):
        if hasattr(func, "__qualname__") and "." in func.__qualname__:
            class_name = func.__qualname__.split(".")[0]
            task_name = f"{func.__module__}.{class_name}.{func.__name__}"
        else:
            task_name = f"{func.__module__}.{func.__name__}"

        is_coroutine = asyncio.iscoroutinefunction(func)

        WorkerManager.register_task_handler(task_name, func, is_coroutine)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper = async_wrapper if is_coroutine else sync_wrapper

        wrapper.delay = self._create_delay_method(func, task_name)
        return wrapper

    def _create_delay_method(self, func: Callable, task_name: str) -> Callable:
        def delay_execution(*args, **kwargs) -> str:
            container = ServiceContainer()
            broker = container.get(BrokerInterface)

            scheduled_for = self._calculate_schedule_time()

            payload = {}
            if args:
                payload["args"] = args
            if kwargs:
                payload["kwargs"] = kwargs

            task = broker.enqueue(
                name=task_name,
                payload=payload,
                queue=self.queue,
                priority=self.priority,
                scheduled_for=scheduled_for,
                max_retries=self.max_retries,
            )

            return task.id

        return delay_execution

    def _calculate_schedule_time(self) -> Optional[datetime]:
        if self.schedule_at:
            return self.schedule_at
        elif self.delay:
            if isinstance(self.delay, int):
                return datetime.now() + timedelta(seconds=self.delay)
            else:
                return datetime.now() + self.delay
        return None
