import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, get_type_hints

from framefox.core.di.service_config import ServiceConfig

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ServiceDefinition:

    def __init__(
        self,
        service_class: Type[Any],
        public: bool = False,
        tags: List[str] = None,
        autowire: bool = True,
    ):
        self.service_class = service_class
        self.public = public
        self.tags = tags or []
        self.autowire = autowire
        self.factory = None
        self.arguments = []
        self.calls = []
        self.abstract = inspect.isabstract(service_class)
        self.synthetic = False  # Service created manually rather than discovered

    def set_factory(self, factory: Callable) -> "ServiceDefinition":
        self.factory = factory
        return self

    def set_arguments(self, arguments: List[Any]) -> "ServiceDefinition":
        self.arguments = arguments
        return self

    def add_tag(self, tag: str) -> "ServiceDefinition":
        if tag not in self.tags:
            self.tags.append(tag)
        return self

    def add_method_call(
        self, method: str, arguments: List[Any] = None
    ) -> "ServiceDefinition":
        """Adds a method call to be made after instantiation"""
        self.calls.append((method, arguments or []))
        return self


class ServiceContainer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceContainer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        # Ensure the project directory is in the PYTHONPATH
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        sys.path.insert(0, str(project_root))

        # Initialize data structures
        self._definitions: Dict[Type[Any], ServiceDefinition] = {}
        self._instances: Dict[Type[Any], Any] = {}  # Created instances
        self._tags: Dict[str, List[Type[Any]]] = {}  # Tagged services
        # Service aliases
        self._aliases: Dict[str, Type[Any]] = {}
        # Service factories
        self._service_factories: List[Any] = []
        self._config = ServiceConfig()
        self._instance_counter = 1
        self._initialized = True

        # Load services
        self._load_services()

    # Add the missing method _find_or_create_definition

    def _find_or_create_definition(
        self, service_class: Type
    ) -> Optional[ServiceDefinition]:
        """
        Finds an existing service definition or creates a new one if possible.
        """
        # First, look for an existing definition
        definition = self._find_definition(service_class)
        if definition:
            return definition

        # If it's not a class, we can't create a definition
        if not inspect.isclass(service_class):
            return None

        # Check if the class can be a service
        if self._can_be_service(service_class):
            # Create a default definition
            definition = ServiceDefinition(service_class)

            # Add a default tag based on the module
            default_tag = self._get_default_tag(service_class)
            if default_tag:
                definition.add_tag(default_tag)

            # Register the definition
            self._add_service_definition(service_class, definition)
            return definition

        return None

    # Also add a method to register service factories

    def add_service_factory(self, factory) -> None:
        """
        Adds a service factory to the container.

        Factories must implement:
        - supports(service_class): bool
        - create(service_class, container): Any
        """
        self._service_factories.append(factory)

    def _load_services(self):

        src_paths = []

        project_root = Path(__file__).resolve().parent.parent.parent.parent
        src_path_dev = project_root / "src"
        if src_path_dev.exists():
            src_paths.append(src_path_dev)

        cwd_path = Path.cwd() / "src"
        if cwd_path.exists() and cwd_path not in src_paths:
            src_paths.append(cwd_path)
        parent = Path.cwd().parent
        for _ in range(3):
            if (parent / "src").exists() and (parent / "src") not in src_paths:
                src_paths.append(parent / "src")
            parent = parent.parent

        src_path = src_paths[0] if src_paths else None
        self._create_module_aliases()

        self._register_essential_services()

        core_path = Path(__file__).resolve().parent.parent

        excluded_directories = list(self._config.excluded_dirs) + [
            "entity",
            "entities",
            "Entity",
        ]
        excluded_modules = list(self._config.excluded_modules) + [
            "src.entity",
            "src.entities",
            "framefox.core.entity",
        ]

        self._scan_for_service_definitions(
            core_path, "framefox.core", excluded_directories, excluded_modules
        )

        # Load definitions from src if it exists
        if src_path and src_path.exists():
            self._scan_for_service_definitions(
                src_path, "src", excluded_directories, excluded_modules
            )
        else:
            print(f"Source path does not exist: {src_path}")

        # Register aliases for services
        self._register_aliases()
        # print("Service aliases registered")
        # print(f"Total service definitions: {len(self._definitions)}")

    def _create_module_aliases(self):
        """
        Creates module aliases so that framefox.X points to framefox.core.X
        """
        # List of submodules to alias
        core_modules = [
            "controller",
            "routing",
            "logging",
            "di",
            "events",
            "config",
            "debug",
            "request",
            "orm",
            "templates",
            "security",
            "middleware",
            "kernel",
        ]

        for module_name in core_modules:
            core_module = f"framefox.core.{module_name}"
            alias_name = f"framefox.{module_name}"

            # Do not overwrite existing modules
            if alias_name not in sys.modules:
                try:
                    # Import the core module
                    module = importlib.import_module(core_module)
                    # Create the alias
                    sys.modules[alias_name] = module
                except ModuleNotFoundError:
                    pass

    def set_instance(self, interface_type, instance):
        """Forces a specific instance for a given type in the container."""
        # In the container, keys are directly the classes
        # Do not use _get_service_id which does not exist
        self._instances[interface_type] = instance
        return self

    def _register_essential_services(self):
        """
        Registers essential services that must be available early in the lifecycle.
        """
        essential_services = [
            "framefox.core.config.settings.Settings",
            "framefox.core.logging.logger.Logger",
            "framefox.core.orm.entity_manager_registry.EntityManagerRegistry",
        ]

        for service_path in essential_services:
            try:
                parts = service_path.split(".")
                module_path = ".".join(parts[:-1])
                class_name = parts[-1]

                module = importlib.import_module(module_path)
                service_cls = getattr(module, class_name)

                # Create a definition and mark as public
                definition = ServiceDefinition(service_cls, public=True)
                definition.synthetic = True
                self._add_service_definition(service_cls, definition)

                # Immediately instantiate these essential services
                self.get(service_cls)
            except Exception as e:
                print(f"Error registering essential service {service_path}: {e}")

    def _scan_for_service_definitions(
        self,
        base_path: Path,
        base_package: str,
        excluded_dirs: list,
        excluded_modules: list,
    ):
        """
        Scans the directory to find service classes and creates their definitions.
        Does not instantiate services.
        """
        for root, _, files in os.walk(base_path):
            root_path = Path(root)

            # Check if this directory should be excluded
            if any(
                excluded_dir.lower() in part.lower()
                for part in root_path.parts
                for excluded_dir in excluded_dirs
            ):
                continue

            for file in files:
                if file.endswith(".py") and file not in [
                    "service_container.py",
                    "__init__.py",
                ]:
                    file_path = root_path / file

                    try:
                        # Build the module name
                        rel_path = (
                            file_path.relative_to(base_path)
                            .with_suffix("")
                            .as_posix()
                            .replace("/", ".")
                        )
                        if rel_path:
                            module_name = f"{base_package}.{rel_path}"
                        else:
                            module_name = base_package

                        # Check if this module should be excluded
                        if any(
                            module_name.startswith(excluded)
                            for excluded in excluded_modules
                        ):
                            continue

                        # Try to import the module without executing it
                        try:
                            module = importlib.import_module(module_name)

                            # Examine the module's attributes without executing them
                            for attr_name in dir(module):
                                try:
                                    attr = getattr(module, attr_name)

                                    # Check if the attribute is a class that can be a service
                                    if inspect.isclass(attr) and self._can_be_service(
                                        attr
                                    ):
                                        # Create a service definition
                                        is_public = self._config.is_public(attr)
                                        autowire = self._config.autowire_enabled
                                        tags = self._config.get_service_tags(attr)

                                        # Add a default tag based on the module
                                        default_tag = self._get_default_tag(attr)
                                        if default_tag and default_tag not in tags:
                                            tags.append(default_tag)

                                        # Create and register the definition
                                        definition = ServiceDefinition(
                                            attr,
                                            public=is_public,
                                            tags=tags,
                                            autowire=autowire,
                                        )
                                        self._add_service_definition(attr, definition)

                                except Exception as e:
                                    if not "access" in str(e).lower():
                                        print(
                                            f"Error inspecting attribute {attr_name} in {module_name}: {e}"
                                        )

                        except ModuleNotFoundError as e:
                            # Do not show error for typical debug modules
                            debug_modules = [
                                "icecream",
                                "devtools",
                                "pytest",
                                "IPython",
                            ]
                            if not any(
                                debug_module in str(e) for debug_module in debug_modules
                            ):
                                pass
                        except ImportError as e:
                            print(f"Import error for module {module_name}: {e}")

                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")

    def _register_aliases(self):
        """
        Registers aliases for services based on their class names.
        """
        for service_class in self._definitions:
            # Create an alias with the full class name
            full_name = f"{service_class.__module__}.{service_class.__name__}"
            self._aliases[full_name] = service_class

            # Create an alias with just the class name
            self._aliases[service_class.__name__] = service_class

    def _add_service_definition(
        self, service_class: Type[Any], definition: ServiceDefinition
    ):
        """
        Adds a service definition and registers its tags.
        """
        self._definitions[service_class] = definition

        # Register the tags
        for tag in definition.tags:
            if tag not in self._tags:
                self._tags[tag] = []
            if service_class not in self._tags[tag]:
                self._tags[tag].append(service_class)

    def _can_be_service(self, cls: Type) -> bool:
        """
        Determines if a class can be a service.
        """
        if not inspect.isclass(cls):
            return False

        # Ignore exceptions
        if issubclass(cls, Exception):
            return False

        # Ignore SQLModel/Pydantic classes
        if hasattr(cls, "__pydantic_self__") or hasattr(cls, "__pydantic_model__"):
            return False

        # Ignore interfaces (classes starting with 'I' and having abstract methods)
        if cls.__name__.startswith("I") and hasattr(cls, "__abstractmethods__"):
            return False

        # Ignore private classes (starting with _)
        if cls.__name__.startswith("_"):
            return False

        # Check if the class is explicitly marked as non-service
        if hasattr(cls, "__service__") and not cls.__service__:
            return False

        # Check configured exclusions
        config = self._config
        if config.is_excluded_class(cls.__name__):
            return False

        if config.is_excluded_module(cls.__module__):
            return False

        if config.is_in_excluded_directory(cls.__module__):
            return False

        # Ignore common Python types and classes from the typing module
        builtin_modules = ["builtins", "typing", "abc", "sqlmodel", "pydantic"]
        if cls.__module__ in builtin_modules or cls.__module__.startswith(
            tuple(builtin_modules)
        ):
            return False

        return True

    def get(self, service_class: Type) -> Any:
        """
        Retrieves or creates an instance of the requested service.
        """
        # Simple cases (existing instance, non-class, etc.)
        if service_class in self._instances:
            return self._instances[service_class]

        # Handle the case of simple values (non-classes)
        if not inspect.isclass(service_class):
            return service_class

        # Handle the case of primitive classes
        if service_class in (str, int, float, bool, list, dict, set, tuple):
            instance = service_class()
            self._instances[service_class] = instance
            return instance

        # Find or create the definition
        definition = self._find_or_create_definition(service_class)
        if not definition:
            # List of known external classes to silently ignore
            silent_classes = {"FastAPI", "Depends", "Request", "Response"}

            if service_class.__name__ not in silent_classes:
                print(f"No service definition found for {service_class.__name__}")
            return None

        # Do not instantiate abstract classes
        if definition.abstract:
            print(f"Cannot instantiate abstract class {service_class.__name__}")
            return None

        # Use a factory if available
        if definition.factory:
            try:
                instance = definition.factory()
                self._instances[service_class] = instance
                return instance
            except Exception as e:
                print(f"Error using factory for {service_class.__name__}: {e}")
                return None

        # Try registered service factories
        for factory in self._service_factories:
            if factory.supports(service_class):
                try:
                    instance = factory.create(service_class, self)
                    self._instances[service_class] = instance
                    return instance
                except Exception as e:
                    print(
                        f"Factory {factory.__class__.__name__} failed for {service_class.__name__}: {e}"
                    )
                    continue

        # If arguments are explicitly defined, use them
        if definition.arguments:
            try:
                instance = service_class(*definition.arguments)
                self._instances[service_class] = instance
                return instance
            except Exception as e:
                print(f"Error creating {service_class.__name__} with arguments: {e}")
                # Do not return here, try autowiring as fallback

        # Standard autowiring as a last resort
        try:
            dependencies = self._resolve_dependencies(service_class)
            instance = service_class(*dependencies)
            self._instances[service_class] = instance

            # Apply configured method calls
            for method_name, args in definition.calls:
                try:
                    method = getattr(instance, method_name)
                    method(*args)
                except Exception as e:
                    print(
                        f"Error calling {method_name} on {service_class.__name__}: {e}"
                    )

            return instance
        except Exception as e:
            print(f"Error creating instance of {service_class.__name__}: {e}")
            return None

    def _find_definition(self, service_class: Type) -> Optional[ServiceDefinition]:
        """
        Searches for the definition of a service.
        """
        # Direct search by class
        if service_class in self._definitions:
            return self._definitions[service_class]

        # Search by alias
        if isinstance(service_class, str) and service_class in self._aliases:
            return self._definitions.get(self._aliases[service_class])

        return None

    def _resolve_dependencies(self, service_class: Type) -> List[Any]:
        """
        Resolves the dependencies of a service class for autowiring.
        """
        dependencies = []

        try:
            constructor = inspect.signature(service_class.__init__)
            params = constructor.parameters

            # Attempt to get type annotations
            try:
                module = sys.modules[service_class.__module__]
                type_hints = get_type_hints(
                    service_class.__init__,
                    localns=vars(service_class),
                    globalns=module.__dict__,
                )

                for name, param in params.items():
                    if name == "self":
                        continue

                    dependency_cls = type_hints.get(name)

                    if dependency_cls:
                        # Get the dependency from the container
                        dependency = self.get(dependency_cls)
                        dependencies.append(dependency)
                    elif param.default != inspect.Parameter.empty:
                        # Use the default value if available
                        dependencies.append(param.default)
                    else:
                        # If no type annotation and no default value, add None
                        dependencies.append(None)
                        print(
                            f"Warning: Parameter {name} of {service_class.__name__} has no type hint and no default value"
                        )
            except Exception as e:
                print(f"Error getting type hints for {service_class.__name__}: {e}")
        except Exception as e:
            print(f"Error analyzing constructor of {service_class.__name__}: {e}")

        return dependencies

    def get_by_name(self, class_name: str) -> Optional[Any]:
        """
        Retrieves a service by its class name.
        """
        # Search in aliases
        if class_name in self._aliases:
            return self.get(self._aliases[class_name])

        # Search in definitions
        for cls in self._definitions:
            if cls.__name__ == class_name:
                return self.get(cls)

        print(f"Service with name '{class_name}' not found.")
        return None

    def get_by_tag(self, tag: str) -> Any:
        """
        Returns the first service associated with a tag.
        Raises an exception if there are multiple services.
        """
        service_classes = self._tags.get(tag, [])

        if not service_classes:
            return None

        if len(service_classes) > 1:
            service_names = [cls.__name__ for cls in service_classes]
            print(
                f"Warning: Multiple services found for tag '{tag}': {', '.join(service_names)}. Returning first."
            )

        return self.get(service_classes[0])

    def get_all_by_tag(self, tag: str) -> List[Any]:
        """
        Returns all services associated with a tag.
        """
        service_classes = self._tags.get(tag, [])
        return [self.get(cls) for cls in service_classes if cls in self._definitions]

    def _get_default_tag(self, service_class: Type) -> str:
        """
        Converts the module name to a tag.
        Ex: framefox.core.request.session.session -> core.request.session
        """
        module_name = service_class.__module__
        parts = module_name.split(".")
        if parts[0] in ["framefox", "src"]:
            parts = parts[1:]
        if len(parts) > 1 and parts[-1] == parts[-2]:
            parts = parts[:-1]

        return ".".join(parts)

    def print_container_stats(self):
        """
        Prints statistics about the service container.
        """
        print("\nServiceContainer Statistics:")
        print(f"Container instance: #{self._instance_counter}")
        print(f"Total service definitions: {len(self._definitions)}")
        print(f"Instantiated services: {len(self._instances)}")
        print(f"Tags: {len(self._tags)}")

        print("\nRegistered services:")
        for service_class in self._definitions:
            definition = self._definitions[service_class]
            status = (
                "instantiated"
                if service_class in self._instances
                else "not instantiated"
            )
            visibility = "public" if definition.public else "private"
            print(f"- {service_class.__name__} ({visibility}, {status})")

            if service_class in self._instances:
                instance = self._instances[service_class]
                print(f"  id: {id(instance)}")

            if definition.tags:
                print(f"  tags: {', '.join(definition.tags)}")
