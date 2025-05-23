import inspect
from typing import Any, Callable, List, Optional, Type

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ServiceDefinition:
    """
    Represents a service definition with all its configuration.
    Immutable after creation for thread safety.
    """

    def __init__(
        self,
        service_class: Type[Any],
        public: bool = False,
        tags: List[str] = None,
        autowire: bool = True,
        factory: Optional[Callable] = None,
        arguments: List[Any] = None,
        method_calls: List[tuple] = None,
        synthetic: bool = False,
        lazy: bool = False,
    ):
        self._service_class = service_class
        self._public = public
        self._tags = list(tags or [])
        self._autowire = autowire
        self._factory = factory
        self._arguments = list(arguments or [])
        self._method_calls = list(method_calls or [])
        self._synthetic = synthetic
        self._lazy = lazy
        self._abstract = inspect.isabstract(service_class)
        self._frozen = False

    @property
    def service_class(self) -> Type[Any]:
        return self._service_class

    @property
    def public(self) -> bool:
        return self._public

    @property
    def tags(self) -> List[str]:
        return self._tags.copy()

    @property
    def autowire(self) -> bool:
        return self._autowire

    @property
    def factory(self) -> Optional[Callable]:
        return self._factory

    @property
    def arguments(self) -> List[Any]:
        return self._arguments.copy()

    @property
    def method_calls(self) -> List[tuple]:
        return self._method_calls.copy()

    @property
    def synthetic(self) -> bool:
        return self._synthetic

    @property
    def lazy(self) -> bool:
        return self._lazy

    @property
    def abstract(self) -> bool:
        return self._abstract

    @property
    def frozen(self) -> bool:
        return self._frozen

    def freeze(self) -> "ServiceDefinition":
        """Mark the definition as frozen (immutable)."""
        self._frozen = True
        return self

    def with_tag(self, tag: str) -> "ServiceDefinition":
        """Create a new definition with an additional tag."""
        if self._frozen:
            raise RuntimeError("Cannot modify frozen service definition")

        new_tags = self._tags.copy()
        if tag not in new_tags:
            new_tags.append(tag)

        return ServiceDefinition(
            self._service_class,
            self._public,
            new_tags,
            self._autowire,
            self._factory,
            self._arguments,
            self._method_calls,
            self._synthetic,
            self._lazy,
        )

    def with_factory(self, factory: Callable) -> "ServiceDefinition":
        """Create a new definition with a factory."""
        if self._frozen:
            raise RuntimeError("Cannot modify frozen service definition")

        return ServiceDefinition(
            self._service_class,
            self._public,
            self._tags,
            self._autowire,
            factory,
            self._arguments,
            self._method_calls,
            self._synthetic,
            self._lazy,
        )

    def with_arguments(self, arguments: List[Any]) -> "ServiceDefinition":
        """Create a new definition with explicit arguments."""
        if self._frozen:
            raise RuntimeError("Cannot modify frozen service definition")

        return ServiceDefinition(
            self._service_class,
            self._public,
            self._tags,
            self._autowire,
            self._factory,
            arguments,
            self._method_calls,
            self._synthetic,
            self._lazy,
        )

    def with_method_call(self, method: str, arguments: List[Any] = None) -> "ServiceDefinition":
        """Create a new definition with an additional method call."""
        if self._frozen:
            raise RuntimeError("Cannot modify frozen service definition")

        new_calls = self._method_calls.copy()
        new_calls.append((method, arguments or []))

        return ServiceDefinition(
            self._service_class,
            self._public,
            self._tags,
            self._autowire,
            self._factory,
            self._arguments,
            new_calls,
            self._synthetic,
            self._lazy,
        )

    def __repr__(self) -> str:
        return f"ServiceDefinition({self._service_class.__name__}, public={self._public}, tags={self._tags})"
