from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer
from framefox.core.orm.entity_manager_interface import EntityManagerInterface
from framefox.core.orm.entity_manager_registry import EntityManagerRegistry

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class WorkerServiceProvider:
    @staticmethod
    def register():
        container = ServiceContainer()
        settings = Settings()

        entity_manager = EntityManagerRegistry.get_instance().get_entity_manager_for_worker()
        entity_manager_interface = EntityManagerInterface(entity_manager=entity_manager)
        container.set_instance(EntityManagerInterface, entity_manager_interface)
        from framefox.core.task.broker.broker_interface import BrokerInterface
        from framefox.core.task.broker.database_broker import DatabaseBroker
        from framefox.core.task.task_manager import TaskManager
        from framefox.core.task.transport.database_transport import DatabaseTransport
        from framefox.core.task.transport.transport_interface import TransportInterface
        from framefox.core.task.worker_manager import WorkerManager

        broker_type = settings.task_broker_type
        broker = None

        if broker_type == "rabbitmq":

            from framefox.core.task.broker.rabbitmq_broker import RabbitMQBroker
            from framefox.core.task.transport.rabbitmq_transport import (
                RabbitMQTransport,
            )

            task_transport = settings.task_transport_url
            transport = RabbitMQTransport(entity_manager_interface, task_transport)
            container.set_instance(TransportInterface, transport)
            container.set_instance(RabbitMQTransport, transport)

            broker = RabbitMQBroker(entity_manager_interface, transport)
            container.set_instance(RabbitMQBroker, broker)
            container.set_instance(BrokerInterface, broker)

        elif broker_type == "database":
            transport = DatabaseTransport(entity_manager_interface)
            container.set_instance(TransportInterface, transport)

            broker = DatabaseBroker(entity_manager_interface)
            container.set_instance(DatabaseBroker, broker)

            container.set_instance(BrokerInterface, broker)

        worker_manager = WorkerManager(broker)
        container.set_instance(WorkerManager, worker_manager)

        task_manager = TaskManager(broker)
        container.set_instance(TaskManager, task_manager)
