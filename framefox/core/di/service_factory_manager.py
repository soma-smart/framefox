import logging
from typing import Any, List, Protocol, Type

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ServiceFactory(Protocol):
    """Protocol for service factories."""

    def supports(self, service_class: Type[Any]) -> bool:
        """Check if this factory can create the given service."""
        ...

    def create(self, service_class: Type[Any], container: "ServiceContainer") -> Any:
        """Create an instance of the service."""
        ...


class ServiceFactoryManager:
    """
    Manages service factories for custom service creation.
    """

    def __init__(self):
        self._logger = logging.getLogger("SERVICE_FACTORY_MANAGER")
        self._factories: List[ServiceFactory] = []

    def register_factory(self, factory: ServiceFactory) -> None:
        """Register a service factory."""
        if not hasattr(factory, "supports") or not hasattr(factory, "create"):
            raise ValueError("Factory must implement 'supports' and 'create' methods")

        self._factories.append(factory)
        self._logger.debug(f"Registered service factory: {factory.__class__.__name__}")

    def create_service(self, service_class: Type[Any], container: "ServiceContainer") -> Any:
        """Try to create a service using registered factories."""
        for factory in self._factories:
            try:
                if factory.supports(service_class):
                    self._logger.debug(f"Using factory {factory.__class__.__name__} for {service_class.__name__}")
                    return factory.create(service_class, container)
            except Exception as e:
                self._logger.warning(f"Factory {factory.__class__.__name__} failed for {service_class.__name__}: {e}")
                continue

        return None

    def has_factory_for(self, service_class: Type[Any]) -> bool:
        """Check if any factory can handle the given service class."""
        return any(factory.supports(service_class) for factory in self._factories)

    def get_factories(self) -> List[ServiceFactory]:
        """Get all registered factories."""
        return self._factories.copy()
