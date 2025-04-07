import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlmodel import and_, select

from framefox.core.orm.entity_manager_interface import EntityManagerInterface
from framefox.core.task.broker.broker_interface import BrokerInterface
from framefox.core.task.entity.task import Task, TaskStatus


class DatabaseBroker(BrokerInterface):
    """Broker utilisant la base de données pour la gestion des tâches asynchrones."""

    def __init__(self, entity_manager: EntityManagerInterface):
        self.entity_manager = entity_manager
        self.logger = logging.getLogger("DATABASE_BROKER")

    def enqueue(
        self,
        name: str,
        payload: Dict[str, Any],
        queue: str = "default",
        priority: int = 0,
        scheduled_for: Optional[datetime] = None,
        max_retries: int = 3,
    ) -> Task:
        """Ajoute une tâche à la file d'attente."""
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
        self.logger.info(f"Task {task.id} ({task.name}) added to queue '{queue}'")
        return task

    def dequeue(self, queue: str = "default", batch_size: int = 1) -> List[Task]:
        """Récupère des tâches depuis la file d'attente pour traitement."""
        now = datetime.now()

        # Créer une requête pour trouver les tâches en attente
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

        # Marquer les tâches comme étant en cours d'exécution
        if tasks:
            for task in tasks:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                self.entity_manager.persist(task)

            self.entity_manager.commit()

        return tasks

    def complete_task(self, task: Task) -> None:
        """Marque une tâche comme terminée avec succès et la supprime."""
        self.logger.info(
            f"Task {task.id} ({task.name}) successfully completed - deleting"
        )
        self.entity_manager.delete(task)
        self.entity_manager.commit()

    def fail_task(self, task: Task, error: str) -> None:
        """Marque une tâche comme échouée ou planifie une nouvelle tentative."""
        if task.retry_count < task.max_retries:
            task.status = TaskStatus.RETRYING
            task.retry_count += 1
            self.logger.warning(
                f"Task {task.id} ({task.name}) failed, retrying {task.retry_count}/{task.max_retries}"
            )
        else:
            task.status = TaskStatus.FAILED
            task.error_message = error
            self.logger.error(
                f"Task {task.id} ({task.name}) permanently failed: {error}"
            )

        task.updated_at = datetime.now()
        self.entity_manager.persist(task)
        self.entity_manager.commit()

    def get_task(self, task_id: str) -> Optional[Task]:
        """Récupère une tâche par son identifiant."""
        return self.entity_manager.find(Task, task_id)

    def get_tasks_by_status(
        self, status: TaskStatus, queue: str = None, limit: int = 100
    ) -> List[Task]:
        """Récupère des tâches par statut."""
        statement = select(Task).where(Task.status == status)

        if queue:
            statement = statement.where(Task.queue == queue)

        statement = statement.limit(limit)

        return self.entity_manager.exec_statement(statement)

    def purge_failed_tasks(self, older_than_days: int = 30) -> int:
        """Nettoie les tâches échouées plus anciennes que le nombre de jours spécifié."""
        cutoff_date = datetime.now() - timedelta(days=older_than_days)

        statement = select(Task).where(
            and_(Task.status == TaskStatus.FAILED, Task.updated_at <= cutoff_date)
        )

        tasks_to_delete = self.entity_manager.exec_statement(statement)
        count = 0

        for task in tasks_to_delete:
            self.entity_manager.delete(task)
            count += 1

        if count > 0:
            self.entity_manager.commit()
            self.logger.info(
                f"Cleanup: {count} failed tasks deleted (older than {older_than_days} days)"
            )

        return count
