import logging
from typing import Any, Dict, List, Optional, Set, Type

from framefox.core.di.exceptions import InvalidServiceDefinitionError
from framefox.core.di.service_definition import ServiceDefinition

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ServiceRegistry:
    """
    ServiceRegistry is responsible for managing service definitions, aliases, and tags.
    It provides fast lookups, supports caching, and can be frozen to prevent further modifications.
    """

    def __init__(self):
        self._logger = logging.getLogger("SERVICE_REGISTRY")
        self._definitions: Dict[Type[Any], ServiceDefinition] = {}
        self._aliases: Dict[str, Type[Any]] = {}
        self._tags: Dict[str, Set[Type[Any]]] = {}
        self._name_cache: Dict[str, Type[Any]] = {}
        self._tag_cache: Dict[str, List[Type[Any]]] = {}
        self._frozen = False

    def register_definition(self, definition: ServiceDefinition) -> None:
        if self._frozen:
            raise RuntimeError("Registry is frozen")
        if not isinstance(definition, ServiceDefinition):
            raise InvalidServiceDefinitionError("Expected ServiceDefinition instance")
        service_class = definition.service_class
        self._definitions[service_class] = definition.freeze()
        self._register_aliases(service_class)
        for tag in definition.tags:
            if tag not in self._tags:
                self._tags[tag] = set()
            self._tags[tag].add(service_class)
        self._clear_caches()

    def _register_aliases(self, service_class: Type[Any]) -> None:
        full_name = f"{service_class.__module__}.{service_class.__name__}"
        self._aliases[full_name] = service_class
        self._aliases[service_class.__name__] = service_class

    def get_definition(self, service_class: Type[Any]) -> Optional[ServiceDefinition]:
        return self._definitions.get(service_class)

    def get_definition_by_name(self, name: str) -> Optional[ServiceDefinition]:
        if name in self._name_cache:
            service_class = self._name_cache[name]
            return self._definitions.get(service_class)
        if name in self._aliases:
            service_class = self._aliases[name]
            self._name_cache[name] = service_class
            return self._definitions.get(service_class)
        for service_class in self._definitions:
            if service_class.__name__ == name:
                self._name_cache[name] = service_class
                return self._definitions[service_class]
        return None

    def get_definitions_by_tag(self, tag: str) -> List[ServiceDefinition]:
        if tag in self._tag_cache:
            return [
                self._definitions[cls]
                for cls in self._tag_cache[tag]
                if cls in self._definitions
            ]
        service_classes = list(self._tags.get(tag, set()))
        self._tag_cache[tag] = service_classes
        return [
            self._definitions[cls]
            for cls in service_classes
            if cls in self._definitions
        ]

    def has_definition(self, service_class: Type[Any]) -> bool:
        return service_class in self._definitions

    def has_definition_by_name(self, name: str) -> bool:
        return self.get_definition_by_name(name) is not None

    def get_all_definitions(self) -> Dict[Type[Any], ServiceDefinition]:
        return self._definitions.copy()

    def get_all_tags(self) -> Dict[str, List[Type[Any]]]:
        return {tag: list(classes) for tag, classes in self._tags.items()}

    def freeze(self) -> None:
        self._frozen = True

    def _clear_caches(self) -> None:
        self._name_cache.clear()
        self._tag_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
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
