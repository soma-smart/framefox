import gc
import importlib
import inspect
import logging
import os
import sys
import threading
import time

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, get_type_hints

from framefox.core.di.exceptions import (
    CircularDependencyError,
    ServiceInstantiationError,
    ServiceNotFoundError,
)
from framefox.core.di.service_cache_manager import ServiceCacheManager
from framefox.core.di.service_config import ServiceConfig
from framefox.core.di.service_definition import ServiceDefinition
from framefox.core.di.service_factory_manager import ServiceFactoryManager
from framefox.core.di.service_registry import ServiceRegistry

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ServiceContainer:
    """
    Advanced dependency injection container for the Framefox framework.

    The ServiceContainer implements a comprehensive dependency injection system with features including:
    - Automatic service discovery and registration
    - Lazy loading with background scanning capabilities
    - Circular dependency detection
    - Service caching and performance optimization
    - Memory management and cleanup
    - Factory pattern support
    - Tag-based service retrieval

    This container follows a singleton pattern and provides both eager and lazy initialization
    strategies for optimal performance.

    Key Features:
    - Autowiring: Automatic dependency resolution based on type hints
    - Service Discovery: Automatic scanning of modules for service classes
    - Caching: Intelligent caching of service definitions and instances
    - Background Scanning: Non-blocking service discovery for large projects
    - Memory Management: Cleanup capabilities to manage memory usage
    - Essential Services: Priority loading for critical framework components

    Usage:
        container = ServiceContainer()
        service = container.get(MyService)
        services = container.get_all_by_tag('controller')

    Thread Safety:
        The container is thread-safe for service retrieval but not for registration.
        Service registration should be completed during initialization.
    """

    _instance: Optional["ServiceContainer"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceContainer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._logger = logging.getLogger("SERVICE_CONTAINER")
        self._ensure_python_path()

        # Core components
        self._registry = ServiceRegistry()
        self._factory_manager = ServiceFactoryManager()
        self._config = ServiceConfig()
        self._cache_manager = ServiceCacheManager()
        self._factory_manager = ServiceFactoryManager()

        self._register_core_factories()

        # Instance storage and tracking
        self._instances: Dict[Type[Any], Any] = {}
        self._resolution_cache: Dict[Type[Any], Any] = {}
        self._circular_detection: Set[Type[Any]] = set()

        # Lazy loading state
        self._scanned_modules: Set[str] = set()
        self._module_scan_cache: Dict[str, List[Type]] = {}
        self._src_scanned: bool = False
        self._src_scan_in_progress: bool = False
        self._src_paths: List[Path] = []
        self._excluded_directories: List[str] = []
        self._excluded_modules: List[str] = []

        # Background scanning
        self._background_scan_enabled: bool = True

        # Initialization
        self._instance_counter = 1
        self._initialized = True
        self._initialize_container()

    def _register_core_factories(self):
        """Register core factories before registry freeze."""
        try:
            from framefox.core.di.factory.entity_manager_factory import (
                EntityManagerFactory,
            )

            self._factory_manager.register_factory(EntityManagerFactory())
            from framefox.core.di.factory.pydantic_model_factory import (
                PydanticModelFactory,
            )

            self._factory_manager.register_factory(PydanticModelFactory())
            self._logger.debug("Core factories registered successfully")

        except ImportError as e:
            self._logger.warning(f"Could not register some core factories: {e}")

    def _ensure_python_path(self) -> None:
        """Ensure project directory is in PYTHONPATH."""
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        project_root_str = str(project_root)
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)

        current_dir = str(Path.cwd())
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        src_paths = self._find_source_paths()
        for src_path in src_paths:
            parent_path = str(src_path.parent)
            if parent_path not in sys.path:
                sys.path.insert(0, parent_path)

    def _initialize_container(self) -> None:
        """Initialize the container with all services."""
        try:
            self._cache_manager.settings = getattr(self, "settings", None)

            self._create_module_aliases()
            self._register_essential_services()
            self._discover_and_register_services()
            self._logger.debug("Service container initialized successfully")

        except Exception as e:
            self._logger.error(f"Failed to initialize service container: {e}")
            raise RuntimeError(f"Service container initialization failed: {e}") from e

    def _create_module_aliases(self) -> None:
        """Create module aliases for easier imports (framefox.X -> framefox.core.X)."""
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

            if alias_name not in sys.modules:
                try:
                    module = importlib.import_module(core_module)
                    sys.modules[alias_name] = module
                except ModuleNotFoundError:
                    pass

    def _register_essential_services(self) -> None:
        """Register essential services that must be available early."""
        essential_services = [
            "framefox.core.request.session.session.Session",
            "framefox.core.config.settings.Settings",
            "framefox.core.logging.logger.Logger",
            "framefox.core.security.user.entity_user_provider.EntityUserProvider",
            "framefox.core.orm.entity_manager_registry.EntityManagerRegistry",
            "framefox.core.bundle.bundle_manager.BundleManager",
            "framefox.core.security.token_storage.TokenStorage",
            "framefox.core.security.user.user_provider.UserProvider",
            "framefox.core.security.handlers.security_context_handler.SecurityContextHandler",
            "framefox.core.orm.entity_manager_interface.EntityManagerInterface",
            "framefox.core.security.handlers.firewall_handler.FirewallHandler",
        ]

        for service_path in essential_services:
            try:
                service_class = self._import_service_class(service_path)
                definition = ServiceDefinition(service_class, public=True, autowire=True, tags=["essential"])
                self._registry.register_definition(definition)

                self.get(service_class)

            except Exception as e:
                self._logger.debug(f"Could not register essential service {service_path}: {e}")

    def _create_cache_snapshot(self) -> Dict[str, Any]:
        """Create a cache snapshot via the ServiceCacheManager."""
        return self._cache_manager.create_cache_snapshot(self._registry)

    def _save_service_cache(self, cache_data: Dict[str, Any]) -> None:
        """Save cache via the ServiceCacheManager."""
        self._cache_manager.save_cache(cache_data)

    def _discover_and_register_services(self) -> None:
        """Discover services with cache support and lazy loading."""

        cache_data = self._cache_manager.load_cache()
        if cache_data and self._cache_manager.load_services_from_cache(cache_data, self._registry, self._scanned_modules):
            self._logger.debug("Services loaded from cache")
            self._src_scanned = True
            return

        core_path = Path(__file__).resolve().parent.parent
        self._setup_exclusions()
        self._scan_for_service_definitions(core_path, "framefox.core", self._excluded_directories, self._excluded_modules)

        self._src_paths = self._find_source_paths()
        for src_path in self._src_paths:
            controller_path = src_path / "controller"
            if controller_path.exists():
                self._scan_for_service_definitions(controller_path, "src.controller", [], [])

        self._save_initial_cache()

        if self._should_use_background_scan():
            self._start_background_src_scan()
        else:
            self._src_scanned = True

    def _setup_exclusions(self) -> None:
        """Configure exclusions for scanning."""
        self._excluded_directories = list(self._config.excluded_dirs) + [
            "entity",
            "entities",
            "Entity",
            "migration",
            "migrations",
            "Migrations",
            "test",
            "tests",
            "Test",
            "Tests",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            "node_modules",
            "venv",
            "env",
            ".env",
            "docs",
            "documentation",
        ]

        self._excluded_modules = list(self._config.excluded_modules) + [
            "src.entity",
            "src.entities",
            "framefox.core.entity",
            "src.migration",
            "src.migrations",
            "src.test",
            "src.tests",
            "framefox.tests",
            "framefox.test",
        ]

    def _save_initial_cache(self) -> None:
        """Save initial cache via the cache manager."""
        try:
            cache_data = self._cache_manager.create_cache_snapshot(self._registry)
            self._cache_manager.save_cache(cache_data)
        except Exception as e:
            self._logger.warning(f"Could not save initial cache: {e}")

    def _find_source_paths(self) -> List[Path]:
        """Find potential source paths for service discovery."""
        src_paths = []

        # Development path
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        dev_src_path = project_root / "src"
        if dev_src_path.exists():
            src_paths.append(dev_src_path)

        # Current working directory
        cwd_src_path = Path.cwd() / "src"
        if cwd_src_path.exists() and cwd_src_path not in src_paths:
            src_paths.append(cwd_src_path)

        # Search parent directories
        parent = Path.cwd().parent
        for _ in range(3):
            parent_src_path = parent / "src"
            if parent_src_path.exists() and parent_src_path not in src_paths:
                src_paths.append(parent_src_path)
            parent = parent.parent

        return src_paths

    def _scan_for_service_definitions(
        self,
        base_path: Path,
        base_package: str,
        excluded_dirs: List[str],
        excluded_modules: List[str],
    ) -> None:
        """Scan directory for service classes and create their definitions."""

        for root, dirs, files in os.walk(base_path):
            root_path = Path(root)

            if self._should_exclude_directory(root_path, excluded_dirs):
                dirs.clear()
                continue

            for filename in files:
                if not self._should_process_file(filename):
                    continue

                file_path = root_path / filename
                module_name = self._build_module_name(file_path, base_path, base_package)

                if not self._should_exclude_module(module_name, excluded_modules):
                    self._process_module(module_name)

    def _should_exclude_directory(self, path: Path, excluded_dirs: List[str]) -> bool:
        """Check if a directory should be excluded from scanning."""
        dir_name = path.name.lower()

        always_exclude = {"__pycache__", ".pytest_cache", ".mypy_cache", "node_modules", "venv", "env", ".env"}

        if dir_name in always_exclude:
            return True

        for excluded_dir in excluded_dirs:
            if dir_name == excluded_dir.lower():
                return True

        return False

    def _should_process_file(self, filename: str) -> bool:
        """Check if a file should be processed for service discovery."""
        if not filename.endswith(".py"):
            return False

        ignored_files = [
            "__init__.py",
            "service_container.py",
            "conftest.py",
            "test_*.py",
            "*_test.py",
            "migrations.py",
            "migration.py",
            "settings.py",
            "config.py",
        ]

        for pattern in ignored_files:
            if pattern.startswith("*"):
                if filename.endswith(pattern[1:]):
                    return False
            elif pattern.endswith("*"):
                if filename.startswith(pattern[:-1]):
                    return False
            elif filename == pattern:
                return False

        return True

    def _build_module_name(self, file_path: Path, base_path: Path, base_package: str) -> str:
        """Build module name from file path."""
        rel_path = file_path.relative_to(base_path).with_suffix("").as_posix().replace("/", ".")

        if rel_path:
            return f"{base_package}.{rel_path}"
        else:
            return base_package

    def _should_exclude_module(self, module_name: str, excluded_modules: List[str]) -> bool:
        """Check if a module should be excluded."""
        return any(module_name.startswith(excluded) for excluded in excluded_modules)

    def _process_module(self, module_name: str) -> None:
        """Process a module with optimized caching."""
        if module_name in self._scanned_modules:
            return

        if module_name in self._module_scan_cache:
            for service_class in self._module_scan_cache[module_name]:
                if not self._registry.has_definition(service_class):
                    self._create_and_register_definition(service_class)
            self._scanned_modules.add(module_name)
            return

        if self._should_skip_module(module_name):
            self._scanned_modules.add(module_name)
            self._module_scan_cache[module_name] = []
            return

        try:
            module = importlib.import_module(module_name)
            discovered_services = []

            for attr_name in dir(module):
                if not attr_name[0].isupper():
                    continue

                try:
                    attr = getattr(module, attr_name)
                    if inspect.isclass(attr) and attr.__module__ == module_name and self._can_be_service(attr):

                        discovered_services.append(attr)
                        self._create_and_register_definition(attr)
                except Exception:
                    pass

            self._module_scan_cache[module_name] = discovered_services
            self._scanned_modules.add(module_name)

        except (ModuleNotFoundError, ImportError):
            self._scanned_modules.add(module_name)
            self._module_scan_cache[module_name] = []

    def _should_skip_module(self, module_name: str) -> bool:
        """Early filter to avoid unnecessary imports."""
        skip_patterns = [
            "entity",
            "entities",
            "migration",
            "migrations",
            "test",
            "tests",
            "static",
            "templates",
            "assets",
            "docs",
            "documentation",
            "utils",
            "helpers",
        ]

        for pattern in skip_patterns:
            if pattern in module_name.lower():
                return True

        return False

    def _create_and_register_definition(self, service_class: Type[Any]) -> None:
        """Create and register a service definition."""
        is_public = self._config.is_public(service_class)
        autowire = self._config.autowire_enabled
        tags = self._config.get_service_tags(service_class)

        default_tag = self._get_default_tag(service_class)
        if default_tag and default_tag not in tags:
            tags.append(default_tag)

        definition = ServiceDefinition(
            service_class,
            public=is_public,
            tags=tags,
            autowire=autowire,
        )

        self._registry.register_definition(definition)

    def _can_be_service(self, cls: Type) -> bool:
        """Determine if a class can be a service."""
        if not inspect.isclass(cls):
            return False

        if issubclass(cls, Exception):
            return False

        module_name = cls.__module__

        if not (module_name.startswith("framefox.") or module_name.startswith("src.")):
            return False

        if self._config.is_excluded_class(cls.__name__):
            return False

        if self._config.is_excluded_module(cls.__module__):
            return False

        if self._config.is_in_excluded_directory(cls.__module__):
            return False

        return True

    def _get_default_tag(self, service_class: Type) -> str:
        """Convert the module name to a tag."""
        module_name = service_class.__module__
        parts = module_name.split(".")
        if parts[0] in ["framefox", "src"]:
            parts = parts[1:]
        if len(parts) > 1 and parts[-1] == parts[-2]:
            parts = parts[:-1]

        return ".".join(parts)

    def _import_service_class(self, service_path: str) -> Type[Any]:
        """Import a service class from its full path."""
        parts = service_path.split(".")
        module_path = ".".join(parts[:-1])
        class_name = parts[-1]

        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    def get(self, service_class: Type[Any]) -> Any:
        """Get a service instance with dependency injection."""
        if service_class in self._resolution_cache:
            return self._resolution_cache[service_class]

        if service_class in self._instances:
            cached_instance = self._instances[service_class]
            self._resolution_cache[service_class] = cached_instance
            return cached_instance

        if not inspect.isclass(service_class):
            return service_class

        instance = self._factory_manager.create_service(service_class, self)
        if instance is not None:
            self._instances[service_class] = instance
            self._resolution_cache[service_class] = instance
            return instance

        definition = self._registry.get_definition(service_class)

        if not definition and self._can_be_service(service_class):
            definition = ServiceDefinition(service_class, autowire=True)

            if self._registry.is_frozen():
                self._registry._frozen = False
                self._registry.register_definition(definition)
                self._registry._frozen = True
                self._logger.debug(f"Force-registered {service_class.__name__} in frozen registry")
            else:
                self._registry.register_definition(definition)

        if service_class in self._circular_detection:
            chain = list(self._circular_detection)
            raise CircularDependencyError(service_class, chain)

        if not definition:
            raise ServiceNotFoundError(f"Service {service_class.__name__} not found and cannot be auto-registered")

        self._circular_detection.add(service_class)

        try:
            instance = self._create_service_instance(definition)
            self._instances[service_class] = instance
            self._resolution_cache[service_class] = instance
            return instance

        except Exception as e:
            self._logger.error(f"Failed to create service {service_class.__name__}: {e}")
            raise ServiceInstantiationError(f"Cannot create service {service_class.__name__}: {e}") from e
        finally:
            self._circular_detection.discard(service_class)

    def _create_service_instance(self, definition: ServiceDefinition) -> Any:
        """Create a service instance using various strategies."""
        service_class = definition.service_class

        if definition.factory:
            try:
                if callable(definition.factory):
                    return definition.factory()
                else:
                    return definition.factory
            except Exception as e:
                self._logger.error(f"Factory failed for {service_class.__name__}: {e}")
                raise

        instance = self._factory_manager.create_service(service_class, self)
        if instance is not None:
            return instance

        if definition.arguments:
            return service_class(*definition.arguments)

        if definition.autowire:
            dependencies = self._resolve_dependencies(service_class)
            instance = service_class(*dependencies)
        else:
            instance = service_class()
        if definition.method_calls:
            self._apply_method_calls(instance, definition)

        return instance

    def _find_or_create_definition(self, service_class: Type) -> Optional[ServiceDefinition]:
        """Find an existing service definition or create a new one if possible."""
        definition = self._registry.get_definition(service_class)
        if definition:
            return definition

        if not inspect.isclass(service_class):
            return None

        if self._can_be_service(service_class):
            tags = []
            default_tag = self._get_default_tag(service_class)
            if default_tag:
                tags.append(default_tag)

            definition = ServiceDefinition(service_class, tags=tags)
            self._registry.register_definition(definition)
            return definition

        return None

    # def _create_service_instance(self, definition: ServiceDefinition) -> Any:
    #     """Create a service instance using various strategies."""
    #     service_class = definition.service_class

    #     if definition.factory:
    #         return definition.factory()

    #     instance = self._factory_manager.create_service(service_class, self)
    #     if instance is not None:
    #         return instance

    #     if definition.arguments:
    #         return service_class(*definition.arguments)

    #     if definition.autowire:
    #         dependencies = self._resolve_dependencies(service_class)
    #         return service_class(*dependencies)
    #     else:
    #         return service_class()

    def _resolve_dependencies(self, service_class: Type[Any]) -> List[Any]:
        """Resolve the dependencies of a service class for autowiring."""
        dependencies = []

        try:
            signature = inspect.signature(service_class.__init__)

            # ✅ FIX : Import safe pour get_type_hints
            try:
                type_hints = get_type_hints(service_class.__init__)
            except NameError as e:
                self._logger.warning(f"Error getting type hints for {service_class.__name__}: {e}")
                type_hints = {}

            for param_name, param in signature.parameters.items():
                if param_name == "self":
                    continue

                param_type = type_hints.get(param_name)

                if param_type:
                    try:
                        dependency = self.get(param_type)
                        dependencies.append(dependency)
                    except Exception as dep_e:
                        if param.default != inspect.Parameter.empty:
                            dependencies.append(param.default)
                        else:
                            self._logger.warning(
                                f"Could not resolve dependency {param_name} of type {param_type} for {service_class.__name__}: {dep_e}"
                            )
                elif param.default != inspect.Parameter.empty:
                    dependencies.append(param.default)
                else:
                    self._logger.warning(f"Parameter {param_name} of {service_class.__name__} has no type hint and no default value")

        except Exception as e:
            self._logger.error(f"Failed to resolve dependencies for {service_class.__name__}: {e}")
            return []

        return dependencies

    def _apply_method_calls(self, instance: Any, definition: ServiceDefinition) -> None:
        """Apply configured method calls to an instance."""
        for method_name, args in definition.method_calls:
            try:
                method = getattr(instance, method_name)
                method(*args)
            except Exception as e:
                self._logger.error(f"Error calling {method_name} on {definition.service_class.__name__}: {e}")

    def _should_use_background_scan(self) -> bool:
        """Disable automatic scan for large projects."""
        return False

    def _start_background_src_scan(self) -> None:
        """Start background src scan with cache."""
        if self._src_scan_in_progress or self._src_scanned:
            return

        self._src_scan_in_progress = True

        def background_scan():
            try:
                threading.Event().wait(0.1)

                self._logger.debug("Starting background src scan...")
                start_time = time.time()

                for src_path in self._src_paths:
                    if src_path.exists():
                        self._scan_for_service_definitions(src_path, "src", self._excluded_directories, self._excluded_modules)

                self._src_scanned = True
                self._src_scan_in_progress = False

                cache_data = self._cache_manager.create_cache_snapshot(self._registry)
                self._cache_manager.save_cache(cache_data)

                elapsed = time.time() - start_time
                total_services = len(self._registry.get_all_definitions())
                self._logger.debug(f"Background src scan completed in {elapsed:.2f}s. Total services: {total_services}")

            except Exception as e:
                self._logger.error(f"Background scan failed: {e}")
                self._src_scan_in_progress = False

        scan_thread = threading.Thread(target=background_scan, daemon=True)
        scan_thread.start()

    def _ensure_src_scanned_sync(self) -> None:
        """Force src scan synchronously if needed."""
        if self._src_scanned:
            return

        if self._src_scan_in_progress:
            max_wait = 5.0
            wait_interval = 0.1
            waited = 0.0

            while self._src_scan_in_progress and waited < max_wait:
                threading.Event().wait(wait_interval)
                waited += wait_interval

            if self._src_scanned:
                return

        self._logger.debug("Forcing synchronous src scan...")
        start_time = time.time()

        for src_path in self._src_paths:
            if src_path.exists():
                self._scan_for_service_definitions(src_path, "src", self._excluded_directories, self._excluded_modules)

        self._src_scanned = True
        self._src_scan_in_progress = False

        elapsed = time.time() - start_time
        self._logger.debug(f"Synchronous src scan completed in {elapsed:.2f}s")

    def cleanup_memory(self) -> None:
        """Clean up container memory."""
        self._resolution_cache.clear()

        essential_modules = {mod for mod in self._module_scan_cache.keys() if mod.startswith("framefox.core") or "controller" in mod}

        modules_to_remove = set(self._module_scan_cache.keys()) - essential_modules
        for module_name in modules_to_remove:
            del self._module_scan_cache[module_name]

        collected = gc.collect()

        self._logger.debug(f"Memory cleanup: removed {len(modules_to_remove)} cached modules, collected {collected} objects")

    def clear_cache(self) -> None:
        """Clear all caches."""
        self._resolution_cache.clear()
        self._cache_manager.clear_cache()
        self._logger.debug("All caches cleared")

    def rebuild_cache(self) -> None:
        """Force cache rebuild."""
        self._cache_manager.clear_cache()
        self._scanned_modules.clear()
        self._module_scan_cache.clear()
        self._src_scanned = False
        self._discover_and_register_services()

    def get_by_name(self, class_name: str) -> Optional[Any]:
        """Retrieve a service by its class name."""
        definition = self._registry.get_definition_by_name(class_name)
        if definition:
            return self.get(definition.service_class)

        self._logger.warning(f"Service with name '{class_name}' not found")
        return None

    def get_by_tag(self, tag: str) -> Optional[Any]:
        """Return the first service associated with a tag."""
        definitions = self._registry.get_definitions_by_tag(tag)

        if not definitions:
            return None

        if len(definitions) > 1:
            service_names = [def_.service_class.__name__ for def_ in definitions]
            self._logger.warning(f"Multiple services found for tag '{tag}': {', '.join(service_names)}. Returning first.")

        return self.get(definitions[0].service_class)

    def get_all_by_tag(self, tag: str) -> List[Any]:
        """Return all services associated with a tag."""
        definitions = self._registry.get_definitions_by_tag(tag)
        return [self.get(def_.service_class) for def_ in definitions]

    def has(self, service_class: Type[Any]) -> bool:
        """Check if a service is registered."""
        return self._registry.has_definition(service_class)

    def has_by_name(self, class_name: str) -> bool:
        """Check if a service is registered by name."""
        return self._registry.has_definition_by_name(class_name)

    def set_instance(self, service_class: Type[Any], instance: Any) -> None:
        """Manually set a service instance."""
        self._instances[service_class] = instance
        self._resolution_cache[service_class] = instance

    def register_factory(self, factory) -> None:
        """Register a service factory."""
        self._factory_manager.register_factory(factory)

    def freeze_registry(self) -> None:
        """Freeze the registry when initialization is complete."""
        if not self._registry._frozen:
            self._registry.freeze()
            self._logger.debug("Service registry frozen")

    def force_complete_scan(self) -> None:
        """Force complete scan immediately."""
        self._logger.debug("Forcing complete scan...")
        self._ensure_src_scanned_sync()

    def get_scan_status(self) -> Dict[str, Any]:
        """Get scan status for debugging."""
        return {
            "src_scanned": self._src_scanned,
            "src_scan_in_progress": self._src_scan_in_progress,
            "scanned_modules_count": len(self._scanned_modules),
            "cached_modules_count": len(self._module_scan_cache),
            "src_paths_count": len(self._src_paths),
            "background_scan_enabled": self._background_scan_enabled,
        }

    def disable_background_scan(self) -> None:
        """Disable background scanning."""
        self._background_scan_enabled = False

    def get_stats(self) -> Dict[str, Any]:
        """Get container statistics."""
        registry_stats = self._registry.get_stats()

        return {
            "container_instance": self._instance_counter,
            "instantiated_services": len(self._instances),
            "cached_resolutions": len(self._resolution_cache),
            "registered_factories": len(self._factory_manager.get_factories()),
            **registry_stats,
        }

