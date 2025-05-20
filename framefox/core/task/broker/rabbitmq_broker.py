import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from framefox.core.orm.entity_manager_interface import EntityManagerInterface
from framefox.core.task.broker.broker_interface import BrokerInterface
from framefox.core.task.entity.task import Task, TaskStatus
from framefox.core.task.transport.rabbitmq_transport import RabbitMQTransport

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class RabbitMQBroker(BrokerInterface):
    """RabbitMQ implementation of the broker interface for task queue management.
    This class provides methods to interact with RabbitMQ for task queue operations including
    enqueueing, dequeueing, completing and failing tasks. It uses an entity manager for 
    persistence and a RabbitMQ transport for message broker operations.
    """

    def __init__(
        self, entity_manager: EntityManagerInterface, transport: RabbitMQTransport
    ):
        self.entity_manager = entity_manager
        self.transport = transport
        self.logger = logging.getLogger("RABBITMQ_BROKER")

    def enqueue(
        self,
        name: str,
        payload: Dict[str, Any],
        queue: str = "default",
        priority: int = 0,
        scheduled_for: Optional[datetime] = None,
        max_retries: int = 3,
    ) -> Task:
        task = Task(
            name=name,
            queue=queue,
            priority=priority,
            scheduled_for=scheduled_for,
            max_retries=max_retries,
        )
        task.set_payload(payload)

        self.entity_manager.persist(task)
        self.entity_manager.commit()

        self.transport.publish(task)

        self.logger.info(
            f"Task {task.id} ({task.name}) added to queue '{queue}' and published to RabbitMQ"
        )
        return task

    def dequeue(self, queue: str = "default", batch_size: int = 1) -> List[Task]:
        return self.transport.consume(queue, batch_size)

    def complete_task(self, task: Task) -> None:
        self.transport.acknowledge(task)
        self.entity_manager.delete(task)
        self.entity_manager.commit()
        self.logger.info(f"Task {task.id} ({task.name}) successfully completed")

    def fail_task(self, task: Task, error: str) -> None:
        if task.retry_count < task.max_retries:
            task.status = TaskStatus.RETRYING
            task.retry_count += 1
            task.error_message = error
            task.updated_at = datetime.now()
            self.entity_manager.persist(task)
            self.entity_manager.commit()

            self.transport.reject(task, requeue=True)
            self.logger.warning(
                f"Task {task.id} ({task.name}) failed, retrying {task.retry_count}/{task.max_retries}"
            )
        else:
            task.status = TaskStatus.FAILED
            task.error_message = error
            task.updated_at = datetime.now()
            self.entity_manager.persist(task)
            self.entity_manager.commit()

            self.transport.reject(task, requeue=False)
            self.logger.error(
                f"Task {task.id} ({task.name}) permanently failed: {error}"
            )

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.entity_manager.find(Task, task_id)

    def get_tasks_by_status(
        self, status: TaskStatus, queue: str = None, limit: int = 100
    ) -> List[Task]:
        from sqlmodel import select

        statement = select(Task).where(Task.status == status)
        if queue:
            statement = statement.where(Task.queue == queue)
        statement = statement.limit(limit)
        return self.entity_manager.exec_statement(statement)

    def purge_failed_tasks(self, older_than_days: int = 30) -> int:
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        from sqlmodel import and_, select

        statement = select(Task).where(
            and_(Task.status == TaskStatus.FAILED, Task.updated_at <= cutoff_date)
        )
        tasks = self.entity_manager.exec_statement(statement)
        count = 0
        for task in tasks:
            self.entity_manager.delete(task)
            count += 1
        if count > 0:
            self.entity_manager.commit()
            self.logger.info(
                f"Cleaned up {count} failed tasks older than {older_than_days} days"
            )
        return count
