import json
import logging
import time
from datetime import datetime
from typing import List

import pika

from framefox.core.orm.entity_manager_interface import EntityManagerInterface
from framefox.core.task.entity.task import Task, TaskStatus
from framefox.core.task.transport.transport_interface import TransportInterface

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class RabbitMQTransport(TransportInterface):
    """Transport using RabbitMQ for task communication"""

    def __init__(self, entity_manager: EntityManagerInterface, task_transport_url: str):
        self.entity_manager = entity_manager
        self.task_transport_url = task_transport_url
        self.logger = logging.getLogger("RABBITMQ_TRANSPORT")

        self._configure_pika_logging()

        self.connection = None
        self.channel = None
        self.consumer_tag = None
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._last_connection_error_time = 0
        self._min_error_log_interval = 10

        self._setup_connection()

    def _configure_pika_logging(self):
        for logger_name in [
            "pika",
            "pika.adapters",
            "pika.adapters.utils",
            "pika.adapters.select_connection",
            "pika.adapters.blocking_connection",
            "pika.adapters.utils.io_services_utils",
            "pika.adapters.utils.connection_workflow",
            "pika.adapters.utils.selector_ioloop_adapter",
        ]:
            logging.getLogger(logger_name).setLevel(logging.WARNING)

    def _setup_connection(self):
        try:
            parameters = pika.URLParameters(self.task_transport_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.logger.info(f"Connected to RabbitMQ at {self.task_transport_url}")
            self._reconnect_attempts = 0
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {str(e)}")

        def _ensure_connection(self):
            try:
                if self.connection is None or not self.connection.is_open:
                    return self._reconnect_with_backoff()
                elif self.channel is None or not self.channel.is_open:
                    self.channel = self.connection.channel()
                return True
            except Exception as e:
                current_time = time.time()
                if (
                    current_time - self._last_connection_error_time
                ) > self._min_error_log_interval:
                    self.logger.error(f"Failed to ensure connection: {str(e)}")
                    self._last_connection_error_time = current_time
                return self._reconnect_with_backoff()

    def _setup_exchange_and_queue(self, queue: str):
        try:
            self.channel.exchange_declare(
                exchange="tasks", exchange_type="direct", durable=True
            )

            self.channel.queue_declare(
                queue=queue,
                durable=True,
                arguments={
                    "x-dead-letter-exchange": "tasks.dead",
                    "x-dead-letter-routing-key": f"{queue}.dead",
                },
            )

            self.channel.queue_bind(exchange="tasks", queue=queue, routing_key=queue)

            self.channel.exchange_declare(
                exchange="tasks.dead", exchange_type="direct", durable=True
            )

            self.channel.queue_declare(queue=f"{queue}.dead", durable=True)

            self.channel.queue_bind(
                exchange="tasks.dead",
                queue=f"{queue}.dead",
                routing_key=f"{queue}.dead",
            )

        except Exception as e:
            self.logger.error(f"Failed to setup exchange and queue: {e}")
            raise

    def _reconnect_with_backoff(self):
        self._reconnect_attempts += 1

        if self._reconnect_attempts > self._max_reconnect_attempts:
            current_time = time.time()
            if (current_time - self._last_connection_error_time) > 60:
                self.logger.warning(
                    f"Reconnection attempt limit reached ({self._max_reconnect_attempts}). "
                    "Will continue trying periodically, but some operations might fail."
                )
                self._last_connection_error_time = current_time
            return False

        backoff_seconds = min(30, 2 ** (self._reconnect_attempts - 1))

        if self._reconnect_attempts == 1:
            self.logger.info(
                f"RabbitMQ connection lost, trying to reconnect in {backoff_seconds}s..."
            )

        time.sleep(backoff_seconds)

        try:
            self._setup_connection()
            if self.connection is not None and self.connection.is_open:
                self.logger.info("Successfully reconnected to RabbitMQ")
                return True
        except Exception:
            pass

        return False

    def publish(self, task: Task) -> None:
        if not self._ensure_connection():
            self.logger.error("Cannot publish task: no connection")
            return

        try:
            self._setup_exchange_and_queue(task.queue)

            message = {
                "task_id": task.id,
                "name": task.name,
                "payload": task.get_payload(),
            }

            properties = pika.BasicProperties(
                delivery_mode=2,
                priority=task.priority,
                headers={
                    "x-delay": (
                        int(
                            (task.scheduled_for - datetime.now()).total_seconds() * 1000
                        )
                        if task.scheduled_for
                        else None
                    )
                },
                content_type="application/json",
            )

            self.channel.basic_publish(
                exchange="tasks",
                routing_key=task.queue,
                body=json.dumps(message),
                properties=properties,
            )

            self.logger.info(
                f"Task {task.id} ({task.name}) published to queue '{task.queue}'"
            )

        except Exception as e:
            self.logger.error(f"Failed to publish task {task.id}: {e}")
            try:
                self._setup_connection()
            except:
                pass

    def consume(self, queue: str, batch_size: int) -> List[Task]:
        tasks = []
        if not self._ensure_connection():
            return tasks

        try:
            self._setup_exchange_and_queue(queue)

            for _ in range(batch_size):
                method_frame, properties, body = self.channel.basic_get(
                    queue=queue, auto_ack=False
                )

                if method_frame is None:
                    break

                message = json.loads(body)
                task_id = message.get("task_id")

                task = self.entity_manager.find(Task, task_id)

                if task and task.status == TaskStatus.PENDING:
                    task._delivery_tag = method_frame.delivery_tag
                    task.status = TaskStatus.RUNNING
                    task.started_at = datetime.now()
                    self.entity_manager.persist(task)
                    tasks.append(task)
                else:
                    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)

            if tasks:
                self.entity_manager.commit()

            return tasks

        except Exception as e:
            self.logger.error(f"Error consuming tasks: {e}")
            try:
                self._setup_connection()
            except:
                pass
            return []

    def acknowledge(self, task: Task) -> None:
        if not self._ensure_connection():
            self.logger.error(f"Cannot acknowledge task {task.id}: no connection")
            return

        try:
            if hasattr(task, "_delivery_tag"):
                self.channel.basic_ack(delivery_tag=task._delivery_tag)
                self.logger.info(f"Task {task.id} acknowledged")
        except Exception as e:
            self.logger.error(f"Failed to acknowledge task {task.id}: {e}")
            try:
                self._setup_connection()
            except:
                pass

    def reject(self, task: Task, requeue: bool = False) -> None:
        if not self._ensure_connection():
            self.logger.error(f"Cannot reject task {task.id}: no connection")
            return

        try:
            if hasattr(task, "_delivery_tag"):
                self.channel.basic_reject(
                    delivery_tag=task._delivery_tag, requeue=requeue
                )
                self.logger.info(f"Task {task.id} rejected (requeue={requeue})")
        except Exception as e:
            self.logger.error(f"Failed to reject task {task.id}: {e}")
            try:
                self._setup_connection()
            except:
                pass

    def setup(self, queues: List[str]) -> None:
        if not self._ensure_connection():
            self.logger.error("Cannot setup transport: no connection")
            return

        try:
            for queue in queues:
                self._setup_exchange_and_queue(queue)
            self.logger.info(
                f"RabbitMQ transport setup complete for queues: {', '.join(queues)}"
            )
        except Exception as e:
            self.logger.error(f"Failed to setup RabbitMQ transport: {e}")

    def shutdown(self) -> None:
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
            if self.connection and self.connection.is_open:
                self.connection.close()
            self.logger.info("RabbitMQ transport shutdown")
        except Exception as e:
            self.logger.error(f"Error during RabbitMQ transport shutdown: {e}")
