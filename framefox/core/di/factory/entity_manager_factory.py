from framefox.core.di.service_factory_manager import ServiceFactory

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class EntityManagerFactory(ServiceFactory):
    """Factory for EntityManager with request context support."""

    def supports(self, service_class) -> bool:
        """Check if this factory can create the EntityManager."""
        from framefox.core.orm.entity_manager import EntityManager

        return service_class == EntityManager or service_class.__name__ == "EntityManager"

    def create(self, service_class, container):
        """Create EntityManager using the registry."""
        try:
            from framefox.core.orm.entity_manager_registry import EntityManagerRegistry

            entity_manager = EntityManagerRegistry.get_entity_manager_for_request()

            if entity_manager is None:
                from framefox.core.di.service_container import ServiceContainer
                from framefox.core.orm.entity_manager import EntityManager

                container_instance = ServiceContainer()
                settings = container_instance.get_by_name("Settings")

                if settings:
                    entity_manager = EntityManager()

            return entity_manager

        except Exception as e:
            import logging

            logger = logging.getLogger("ENTITY_MANAGER_FACTORY")
            logger.error(f"Failed to create EntityManager: {e}")

            try:
                from framefox.core.orm.entity_manager import EntityManager

                return EntityManager()
            except Exception as fallback_error:
                logger.error(f"Fallback EntityManager creation failed: {fallback_error}")
                return None

    def get_priority(self) -> int:
        """High priority for EntityManager."""
        return 100
