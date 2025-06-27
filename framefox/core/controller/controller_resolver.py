import importlib
import inspect
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Type

from framefox.core.di.service_container import ServiceContainer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ControllerResolver:
    def __init__(self):
        self._container = ServiceContainer()
        self._logger = logging.getLogger("CONTROLLER")
        self._controller_cache: Dict[str, Type] = {}
        self._controller_paths = self._discover_controller_paths()

    def _discover_controller_paths(self) -> Dict[str, Path]:
        paths = {}
        controller_dir = Path("src/controller")
        if controller_dir.exists():
            for file in controller_dir.rglob("*.py"):
                if file.name != "__init__.py":
                    controller_name = file.stem
                    if controller_name.endswith("_controller"):
                        controller_name = controller_name[:-11]
                    paths[controller_name] = file
        return paths

    def resolve_controller(self, controller_name: str) -> Any:
        if controller_name in self._controller_cache:
            controller_class = self._controller_cache[controller_name]
            return self._create_controller_instance(controller_class)

        controller_class = self._load_controller_class(controller_name)
        if controller_class:
            self._controller_cache[controller_name] = controller_class
            return self._create_controller_instance(controller_class)

        raise Exception(f"Controller {controller_name} not found")

    def _load_controller_class(self, controller_name: str) -> Optional[Type]:
        if controller_name not in self._controller_paths:
            return None

        try:
            file_path = self._controller_paths[controller_name]
            rel_path = file_path.relative_to(Path("src")).with_suffix("")
            module_name = f"src.{rel_path.as_posix().replace('/', '.')}"
            module = importlib.import_module(module_name)

            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and name.endswith("Controller") and obj.__module__ == module_name:
                    return obj
        except Exception as e:
            self._logger.warning(f"Failed to load controller {controller_name}: {e}")

        return None

    def _create_controller_instance(self, controller_class: Type) -> Any:
        try:
            dependencies = self._resolve_controller_dependencies(controller_class)
            return controller_class(*dependencies)
        except Exception as e:
            self._logger.warning(f"Failed to resolve dependencies for {controller_class.__name__}: {e}")
            return controller_class()

    def _resolve_controller_dependencies(self, controller_class: Type) -> list:
        dependencies = []
        try:
            signature = inspect.signature(controller_class.__init__)
            for param_name, param in signature.parameters.items():
                if param_name == "self":
                    continue

                if param.annotation and param.annotation != inspect.Parameter.empty:
                    try:
                        dependency = self._container.get(param.annotation)
                        dependencies.append(dependency)
                    except:
                        if param.default != inspect.Parameter.empty:
                            dependencies.append(param.default)
                elif param.default != inspect.Parameter.empty:
                    dependencies.append(param.default)
        except Exception:
            pass

        return dependencies
