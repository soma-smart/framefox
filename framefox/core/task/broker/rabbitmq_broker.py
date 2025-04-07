import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from framefox.core.orm.entity_manager_interface import EntityManagerInterface
from framefox.core.task.broker.broker_interface import BrokerInterface
from framefox.core.task.entity.task import Task, TaskStatus
from framefox.core.task.transport.rabbitmq_transport import RabbitMQTransport


class RabbitMQBroker(BrokerInterface):
    """Broker utilisant RabbitMQ pour la communication des tâches."""

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
        """Ajoute une tâche à la file d'attente RabbitMQ."""
        # 1. Créer la tâche en base de données (pour la traçabilité)
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

        # 2. Publier dans RabbitMQ - c'est ce qui manque dans votre implémentation actuelle
        self.transport.publish(task)

        self.logger.info(
            f"Task {task.id} ({task.name}) added to queue '{queue}' and published to RabbitMQ"
        )
        return task

    def dequeue(self, queue: str = "default", batch_size: int = 1) -> List[Task]:
        """Récupère des tâches depuis RabbitMQ pour traitement."""
        return self.transport.consume(queue, batch_size)

    def complete_task(self, task: Task) -> None:
        """Marque une tâche comme terminée et la confirme dans RabbitMQ."""
        self.transport.acknowledge(task)
        self.entity_manager.delete(task)
        self.entity_manager.commit()
        self.logger.info(f"Task {task.id} ({task.name}) successfully completed")

    def fail_task(self, task: Task, error: str) -> None:
        """Marque une tâche comme échouée et la rejette dans RabbitMQ."""
        if task.retry_count < task.max_retries:
            task.status = TaskStatus.RETRYING
            task.retry_count += 1
            task.error_message = error
            task.updated_at = datetime.now()
            self.entity_manager.persist(task)
            self.entity_manager.commit()

            # Requeue dans RabbitMQ
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

            # Rejeter définitivement
            self.transport.reject(task, requeue=False)
            self.logger.error(
                f"Task {task.id} ({task.name}) permanently failed: {error}"
            )

    # Autres méthodes de l'interface...
    def get_task(self, task_id: str) -> Optional[Task]:
        return self.entity_manager.find(Task, task_id)

    def get_tasks_by_status(
        self, status: TaskStatus, queue: str = None, limit: int = 100
    ) -> List[Task]:
        # Cette méthode ne change pas, car elle utilise la BD pour les tâches historiques
        from sqlmodel import select

        statement = select(Task).where(Task.status == status)
        if queue:
            statement = statement.where(Task.queue == queue)
        statement = statement.limit(limit)
        return self.entity_manager.exec_statement(statement)

    def purge_failed_tasks(self, older_than_days: int = 30) -> int:
        # Cette méthode ne change pas
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
