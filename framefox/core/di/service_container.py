import inspect
import importlib
import os
import sys

from pathlib import Path
from typing import Type, Any, Dict, get_type_hints, List, Optional


class ServiceContainer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceContainer, cls).__new__(cls)
            cls._instance.services: Dict[Type[Any], Any] = {}
            cls._instance._tags: Dict[str, List[Any]] = {}
            cls._instance.scan_and_register_services()
            cls._instance._instance_counter = 1
        return cls._instance

    def print_container_stats(self):
        print("\nServiceContainer Statistics:")
        print(f"Container instance: #{self._instance_counter}")
        print(f"Total registered services: {len(self.services)}")
        print("\nRegistered services:")
        for service_class in self.services:
            print(
                f"- {service_class.__name__} (id: {id(self.services[service_class])})")

    def scan_and_register_services(self):
        core_path = Path(__file__).resolve().parent.parent
        src_path = Path(__file__).resolve().parent.parent.parent.parent / "src"

        paths_to_scan = [core_path, src_path]
        for base_path in paths_to_scan:
            for root, _, files in os.walk(core_path):
                for file in files:
                    if file.endswith(".py") and file not in ["service_container.py", "__init__.py"]:
                        module_path = Path(root) / file
                        module_name = self._module_name_from_path(
                            module_path, core_path)
                        try:
                            module = importlib.import_module(module_name)
                            for attr_name in dir(module):
                                attr = getattr(module, attr_name)
                                if inspect.isclass(attr) and not inspect.isabstract(attr):
                                    if self._is_service_class(attr):
                                        self.register(attr)
                        except NameError as e:
                            if "Scope" in str(e):
                                print(f"Ignoring module {
                                      module_name} (Scope error).")
                                continue
                            else:
                                raise e
                        except Exception as e:
                            print(f"Error importing module {module_name}: {e}")

    def _module_name_from_path(self, module_path: Path, core_path: Path) -> str:
        relative_path = module_path.relative_to(core_path).with_suffix("")
        return ".".join(['framefox.core'] + list(relative_path.parts))

    def _is_service_class(self, cls: Type[Any]) -> bool:

        if cls.__module__ == 'builtins' or cls in (str, int, float, bool, list, dict, set, tuple):
            print(f"Excluding primitive type {cls.__name__}")
            return False

        excluded_modules = {
            'typing',
            'builtins',
            'sqlmodel',
            'fastapi',
            'datetime',
            'pathlib',
            'starlette',
            'console',
            'jinja2',
            'sqlalchemy',
            'pydantic',
            'passlib'
        }

        if hasattr(cls, '__module__'):
            module_parts = cls.__module__.split('.')
            if any(part in excluded_modules for part in module_parts):
                return False

        non_instantiable = {
            "FastAPI", "datetime", "SQLModel", "Optional", "Union",
            "Type", "Dict", "List", "Console", "FileSystemLoader",
            "MiddlewareManager", "CustomCORSMiddleware", "FirewallMiddleware",
            "SessionMiddleware", "RequestMiddleware", "DebugHandler", "ContextVar", "SQLModelFormatter",
            "RenderableType", "HighlighterType", "FastAPI"
        }

        if (cls.__name__ in non_instantiable or
            cls.__name__.endswith('Model') or
            cls.__name__.endswith('Middleware') or
            'Interface' in cls.__name__ or
            'Abstract' in cls.__name__ or
                inspect.isabstract(cls)):
            return False

        return True

    def register(self, service_cls: Type[Any], tags: Optional[List[str]] = None, stack: Optional[List[Type[Any]]] = None) -> Any:

        if (hasattr(service_cls, '__module__') and service_cls.__module__ == 'typing') or hasattr(service_cls, '_special'):
            return None
        if service_cls in self.services:
            return self.services[service_cls]
        problematic_classes = {
            "FastAPI",
            "Panel", "Pretty", "Table"
        }
        if service_cls.__name__ in problematic_classes:
            return None

        if stack is None:
            stack = []
        if service_cls in stack:
            raise Exception(f"Circular dependency detected: {
                            ' -> '.join([c.__name__ for c in stack + [service_cls]])}")
        stack.append(service_cls)

        try:
            constructor = inspect.signature(service_cls.__init__)
            params = constructor.parameters
            dependencies = []
            module = sys.modules[service_cls.__module__]
            type_hints = get_type_hints(service_cls.__init__, localns=vars(
                service_cls), globalns=module.__dict__)

            for name, param in params.items():
                if name == "self":
                    continue
                dependency_cls = type_hints.get(name)
                if not dependency_cls:
                    # Handle untyped or optional parameter
                    if param.default != inspect.Parameter.empty:
                        dependencies.append(param.default)
                    continue
                dependencies.append(self.get(dependency_cls))

            instance = service_cls(*dependencies)
            stack.pop()
            self.services[service_cls] = instance

            if tags:
                for tag in tags:
                    if tag not in self._tags:
                        self._tags[tag] = []
                    self._tags[tag].append(instance)

            return instance
        except NameError as e:
            print(f"NameError while registering {service_cls.__name__}: {e}")
            stack.pop()
            return None
        except Exception as e:
            print(f"Error while registering service {
                  service_cls.__name__}: {e}")
            stack.pop()
            return None

    def get(self, service_cls: Type) -> Any:
        if service_cls not in self.services:
            self.register(service_cls)
        return self.services.get(service_cls)

    def get_by_name(self, class_name: str) -> Optional[Any]:
        for cls, instance in self.services.items():
            if cls.__name__ == class_name:
                return instance
        print(f"Service with name '{class_name}' not found.")
        return None

    def print_services(self) -> None:
        if not self.services:
            print("No services registered.")
            return
        print("Registered services:")
        for cls in self.services:
            print(f"- {cls.__name__}")

    def get_by_tag(self, tag: str) -> list:
        return self._tags.get(tag, [])

    @property
    def tags(self) -> Dict[str, list]:
        return self._tags
