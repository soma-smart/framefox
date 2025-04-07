import logging
from datetime import datetime
from typing import List

from sqlmodel import and_, select

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


class DatabaseTransport(TransportInterface):
    """Transport using the database as a broker"""

    def __init__(self, entity_manager: EntityManagerInterface):
        self.entity_manager = entity_manager
        self.logger = logging.getLogger("DATABASE_TRANSPORT")

    def publish(self, task: Task) -> None:
        pass

    def consume(self, queue: str, batch_size: int) -> List[Task]:
        now = datetime.now()

        statement = (
            select(Task)
            .where(
                and_(
                    Task.queue == queue,
                    Task.status == TaskStatus.PENDING,
                    (Task.scheduled_for == None) | (Task.scheduled_for <= now),
                )
            )
            .order_by(Task.priority.desc(), Task.created_at)
            .limit(batch_size)
        )

        tasks = self.entity_manager.exec_statement(statement)

        for task in tasks:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            self.entity_manager.persist(task)

        if tasks:
            self.entity_manager.commit()

        return tasks

    def acknowledge(self, task: Task) -> None:
        self.entity_manager.delete(task)
        self.entity_manager.commit()

    def reject(self, task: Task, requeue: bool = False) -> None:
        if requeue and task.retry_count < task.max_retries:
            task.status = TaskStatus.PENDING
            task.retry_count += 1
            task.scheduled_for = datetime.now()
            self.entity_manager.persist(task)
        else:
            task.status = TaskStatus.FAILED
            self.entity_manager.persist(task)

        self.entity_manager.commit()

    def setup(self, queues: List[str]) -> None:
        pass

    def shutdown(self) -> None:
        pass
