import asyncio
import concurrent.futures
import importlib
import logging
import signal
import sys
import traceback
from datetime import datetime
from typing import Callable, Dict, List, Optional, Tuple

from framefox.core.di.service_container import ServiceContainer
from framefox.core.events.event_dispatcher import dispatcher
from framefox.core.task.broker.broker_interface import BrokerInterface
from framefox.core.task.entity.task import Task
from framefox.core.task.transport.transport_interface import TransportInterface

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class WorkerManager:
    _task_handlers: Dict[str, Tuple[Callable, bool]] = {}

    def __init__(self, broker: BrokerInterface):
        self.broker = broker
        self.logger = logging.getLogger("WORKER_MANAGER")
        self.running = False
        self.queues = ["default"]
        self.polling_interval = 5
        self.concurrent_tasks = 5
        self.cleanup_interval = 3600
        self.retain_tasks_days = 7
        self.last_cleanup_time = 0

    @classmethod
    def register_task_handler(cls, task_name: str, handler_func: Callable, is_coroutine: bool = None) -> None:
        if is_coroutine is None:
            is_coroutine = asyncio.iscoroutinefunction(handler_func)
        cls._task_handlers[task_name] = (handler_func, is_coroutine)

    def set_queues(self, queues: List[str]) -> None:
        self.queues = queues

    def set_polling_interval(self, seconds: int) -> None:
        self.polling_interval = seconds

    def set_concurrent_tasks(self, count: int) -> None:
        self.concurrent_tasks = count

    def set_cleanup_config(self, interval_hours: int = 1, retain_days: int = 7) -> None:
        self.cleanup_interval = interval_hours * 3600
        self.retain_tasks_days = retain_days
        self.logger.info(f"Automatic cleanup configured: every {interval_hours}h, retain {retain_days} days")

    async def start(self) -> None:
        self.running = True
        self.logger.info(f"Starting worker manager (queues: {', '.join(self.queues)})")
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
        await self._process_loop()

    async def stop(self) -> None:
        self.logger.info("Stopping worker manager...")
        self.running = False

    async def _process_loop(self) -> None:
        while self.running:
            try:
                tasks = []
                for queue in self.queues:
                    tasks.append(self._process_queue(queue))
                await asyncio.gather(*tasks)
                current_time = datetime.now().timestamp()
                if current_time - self.last_cleanup_time > self.cleanup_interval:
                    await self._cleanup_tasks()
                    self.last_cleanup_time = current_time
                await asyncio.sleep(self.polling_interval)
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                traceback.print_exc()
                await asyncio.sleep(1)

    async def _cleanup_tasks(self) -> None:
        try:
            loop = asyncio.get_event_loop()
            count = await loop.run_in_executor(None, self.broker.purge_failed_tasks, 2)
            if count > 0:
                self.logger.info(f"Scheduled cleanup: {count} failed tasks removed")
        except Exception as e:
            self.logger.error(f"Error during task cleanup: {e}")

    async def _process_queue(self, queue: str) -> None:
        try:
            tasks = self.broker.dequeue(queue, self.concurrent_tasks)
            if not tasks:
                return
            self.logger.info(f"Processing {len(tasks)} tasks from queue '{queue}'")
            worker_tasks = [self._execute_task(task) for task in tasks]
            await asyncio.gather(*worker_tasks)
        except Exception as e:
            self.logger.error(f"Error while processing queue '{queue}': {e}")

    async def _execute_task(self, task: Task) -> None:
        try:
            handler_info = self._get_task_handler(task.name)
            if handler_info is None:
                self.logger.error(f"No handler found for task {task.name}")
                self.broker.fail_task(task, f"No handler found for task {task.name}")
                return
            handler_func, is_coroutine = handler_info
            handler_func = self._bind_handler_to_instance(handler_func, task.name)
            dispatcher.dispatch("worker.task.before_execution", {"task": task})
            payload = task.get_payload()
            args = payload.get("args", [])
            kwargs = payload.get("kwargs", {})
            self.logger.info(f"Executing task {task.id} ({task.name}), coroutine: {is_coroutine}")
            result = None
            try:
                if is_coroutine:
                    result = await handler_func(*args, **kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        concurrent.futures.ThreadPoolExecutor(),
                        lambda: handler_func(*args, **kwargs),
                    )
                self.broker.complete_task(task)
                dispatcher.dispatch(
                    "worker.task.after_execution",
                    {"task": task, "success": True, "result": result},
                )
            except Exception as e:
                error_msg = f"{str(e)}\n{traceback.format_exc()}"
                self.logger.error(f"Error while executing task {task.id} ({task.name}): {error_msg}")
                self.broker.fail_task(task, error_msg)
                dispatcher.dispatch(
                    "worker.task.execution_error",
                    {"task": task, "error": e, "traceback": traceback.format_exc()},
                )
        except Exception as outer_e:
            self.logger.error(f"External error while processing task {task.id}: {outer_e}")
            self.broker.fail_task(task, str(outer_e))

    def _get_task_handler(self, task_name: str) -> Optional[Tuple[Callable, bool]]:
        if task_name in self._task_handlers:
            return self._task_handlers[task_name]
        parts = task_name.split(".")
        if len(parts) >= 3:
            try:
                module_name = ".".join(parts[:-2])
                class_name = parts[-2]
                method_name = parts[-1]
                module = importlib.import_module(module_name)
                if hasattr(module, class_name):
                    class_obj = getattr(module, class_name)
                    container = ServiceContainer()
                    instance = container.get(class_obj)
                    if instance and hasattr(instance, method_name):
                        bound_method = getattr(instance, method_name)
                        is_coroutine = asyncio.iscoroutinefunction(bound_method)
                        handler_info = (bound_method, is_coroutine)
                        self._task_handlers[task_name] = handler_info
                        return handler_info
            except Exception as e:
                self.logger.error(f"Unable to load handler for {task_name}: {e}")
        return None

    def _bind_handler_to_instance(self, handler: Callable, task_name: str) -> Callable:
        if hasattr(handler, "__self__") and handler.__self__ is not None:
            return handler
        if not hasattr(handler, "__qualname__") or "." not in handler.__qualname__:
            return handler
        try:
            class_name = handler.__qualname__.split(".")[0]
            module = sys.modules[handler.__module__]
            if hasattr(module, class_name):
                class_obj = getattr(module, class_name)
                container = ServiceContainer()
                instance = container.get(class_obj)
                if instance and hasattr(instance, handler.__name__):
                    bound_method = getattr(instance, handler.__name__)
                    self.logger.debug(f"Method {handler.__name__} bound to an instance of {class_name}")
                    return bound_method
        except Exception as e:
            self.logger.error(f"Error while binding handler {task_name}: {e}")
        return handler

    async def _process_loop(self) -> None:
        from framefox.core.task.transport.rabbitmq_transport import RabbitMQTransport

        transport = ServiceContainer().get(TransportInterface)

        is_push_mode = isinstance(transport, RabbitMQTransport)

        if is_push_mode:
            self.logger.info("Starting in push mode (waiting for messages)")

            transport.setup(self.queues)

        consecutive_errors = 0
        max_consecutive_errors = 5

        while self.running:
            try:
                tasks = []
                for queue in self.queues:
                    queue_tasks = await asyncio.to_thread(self.broker.dequeue, queue, self.concurrent_tasks)
                    tasks.extend([self._execute_task(task) for task in queue_tasks])

                if tasks:
                    await asyncio.gather(*tasks)

                current_time = datetime.now().timestamp()
                if current_time - self.last_cleanup_time > self.cleanup_interval:
                    await self._cleanup_tasks()
                    self.last_cleanup_time = current_time

                consecutive_errors = 0

                if not is_push_mode:
                    await asyncio.sleep(self.polling_interval)
                else:

                    await asyncio.sleep(0.1)

            except Exception as e:
                consecutive_errors += 1
                error_msg = f"Error in processing loop: {e}"

                if consecutive_errors > max_consecutive_errors:

                    if consecutive_errors % 60 == 0:
                        self.logger.error(f"{error_msg} (errors continue)")
                else:
                    self.logger.error(error_msg)
                    traceback.print_exc()

                backoff_seconds = min(30, 1 * (2 ** min(5, consecutive_errors - 1)))
                await asyncio.sleep(backoff_seconds)
