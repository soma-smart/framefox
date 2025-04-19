import asyncio
import logging

from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer
from framefox.core.logging.filter.worker_polling_filter import \
    WorkerPollingFilter
from framefox.core.logging.worker_logger_configurator import \
    WorkerLoggerConfigurator
from framefox.core.task.worker_manager import WorkerManager
from framefox.core.task.worker_service_provider import WorkerServiceProvider
from framefox.terminal.commands.abstract_command import AbstractCommand

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class WorkerCommand(AbstractCommand):
    def __init__(self):
        self.service_container = ServiceContainer()
        WorkerLoggerConfigurator.configure()
        sql_logger = logging.getLogger("SQLMODEL")
        sql_logger.addFilter(WorkerPollingFilter())
        WorkerServiceProvider.register()
        self.settings = self.service_container.get(Settings)

    def execute(self) -> None:
        """Start the worker process to consume tasks from the queue."""

        queues = self.settings.task_default_queues
        concurrency = self.settings.task_worker_concurrency
        interval = self.settings.task_polling_interval

        self.printer.print_msg(
            f"Starting workers (queues: {', '.join(queues)})", "info"
        )
        self.printer.print_msg(
            f"Concurrency: {concurrency}, interval: {interval}s", "info"
        )

        worker_manager = self.service_container.get(WorkerManager)
        worker_manager.set_queues(queues)
        worker_manager.set_concurrent_tasks(concurrency)
        worker_manager.set_polling_interval(interval)

        cleanup_hours = self.settings.task_cleanup_interval
        retention_days = self.settings.task_retention_days
        worker_manager.set_cleanup_config(cleanup_hours, retention_days)

        try:

            asyncio.run(worker_manager.start())
        except KeyboardInterrupt:
            self.printer.print_msg("Stopping workers...", "warning")
