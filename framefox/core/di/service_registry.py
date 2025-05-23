import logging
from typing import Any, Dict, List, Optional, Type, Set

from .service_definition import ServiceDefinition
from .exceptions import ServiceNotFoundError, InvalidServiceDefinitionError

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ServiceRegistry:
    """
    Registry for service definitions and aliases.
    Thread-safe and optimized for fast lookups.
    """

    def __init__(self):
        self._logger = logging.getLogger("SERVICE_REGISTRY")
        
        # Core storage
        self._definitions: Dict[Type[Any], ServiceDefinition] = {}
        self._aliases: Dict[str, Type[Any]] = {}
        self._tags: Dict[str, Set[Type[Any]]] = {}
        
        # Cache for performance
        self._name_cache: Dict[str, Type[Any]] = {}
        self._tag_cache: Dict[str, List[Type[Any]]] = {}
        
        # Tracking
        self._frozen = False

    def register_definition(self, definition: ServiceDefinition) -> None:
        """Register a service definition."""
        if self._frozen:
            raise RuntimeError("Registry is frozen")
        
        if not isinstance(definition, ServiceDefinition):
            raise InvalidServiceDefinitionError("Expected ServiceDefinition instance")
        
        service_class = definition.service_class
        
        # Store definition
        self._definitions[service_class] = definition.freeze()
        
        # Register aliases
        self._register_aliases(service_class)
        
        # Register tags
        for tag in definition.tags:
            if tag not in self._tags:
                self._tags[tag] = set()
            self._tags[tag].add(service_class)
        
        # Clear caches
        self._clear_caches()
        


    def _register_aliases(self, service_class: Type[Any]) -> None:
        """Register aliases for a service class."""
        # Full module path alias
        full_name = f"{service_class.__module__}.{service_class.__name__}"
        self._aliases[full_name] = service_class
        
        # Simple class name alias
        self._aliases[service_class.__name__] = service_class

    def get_definition(self, service_class: Type[Any]) -> Optional[ServiceDefinition]:
        """Get service definition by class."""
        return self._definitions.get(service_class)

    def get_definition_by_name(self, name: str) -> Optional[ServiceDefinition]:
        """Get service definition by name (with caching)."""
        # Check cache first
        if name in self._name_cache:
            service_class = self._name_cache[name]
            return self._definitions.get(service_class)
        
        # Look in aliases
        if name in self._aliases:
            service_class = self._aliases[name]
            self._name_cache[name] = service_class
            return self._definitions.get(service_class)
        
        # Search by class name
        for service_class in self._definitions:
            if service_class.__name__ == name:
                self._name_cache[name] = service_class
                return self._definitions[service_class]
        
        return None

    def get_definitions_by_tag(self, tag: str) -> List[ServiceDefinition]:
        """Get all service definitions with a specific tag (with caching)."""
        # Check cache first
        if tag in self._tag_cache:
            return [self._definitions[cls] for cls in self._tag_cache[tag] if cls in self._definitions]
        
        # Build and cache result
        service_classes = list(self._tags.get(tag, set()))
        self._tag_cache[tag] = service_classes
        
        return [self._definitions[cls] for cls in service_classes if cls in self._definitions]

    def has_definition(self, service_class: Type[Any]) -> bool:
        """Check if a service definition exists."""
        return service_class in self._definitions

    def has_definition_by_name(self, name: str) -> bool:
        """Check if a service definition exists by name."""
        return self.get_definition_by_name(name) is not None

    def get_all_definitions(self) -> Dict[Type[Any], ServiceDefinition]:
        """Get all service definitions."""
        return self._definitions.copy()

    def get_all_tags(self) -> Dict[str, List[Type[Any]]]:
        """Get all tags and their associated service classes."""
        return {tag: list(classes) for tag, classes in self._tags.items()}

    def freeze(self) -> None:
        """Freeze the registry to prevent further modifications."""
        self._frozen = True


    def _clear_caches(self) -> None:
        """Clear internal caches."""
        self._name_cache.clear()
        self._tag_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_definitions": len(self._definitions),
            "total_aliases": len(self._aliases),
            "total_tags": len(self._tags),
            "frozen": self._frozen,
        }

    def __len__(self) -> int:
        return len(self._definitions)

    def __contains__(self, service_class: Type[Any]) -> bool:
        return service_class in self._definitions