import importlib
import inspect
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Type

from framefox.core.debug.exception.controller_exception import (
    ControllerDependencyError,
    ControllerInstantiationError,
    ControllerModuleError,
    ControllerNotFoundError,
    DuplicateControllerError,
)
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
        self._controller_name_to_class: Dict[str, Type] = {}

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

                    try:
                        rel_path = file.relative_to(Path("src")).with_suffix("")
                        module_name = f"src.{rel_path.as_posix().replace('/', '.')}"
                        module = importlib.import_module(module_name)

                        for name, obj in inspect.getmembers(module):
                            if inspect.isclass(obj) and name.endswith("Controller") and obj.__module__ == module_name:

                                generated_name = name.replace("Controller", "").lower()

                                if generated_name in self._controller_name_to_class:
                                    existing_class = self._controller_name_to_class[generated_name]
                                    if existing_class != obj:
                                        raise DuplicateControllerError(
                                            generated_name,
                                            [existing_class.__module__, obj.__module__],
                                        )

                                self._controller_name_to_class[generated_name] = obj
                    except ImportError as e:
                        raise ControllerModuleError(f"src.{rel_path.as_posix().replace('/', '.')}", e)
                    except Exception:
                        pass

        return paths

    def resolve_controller(self, controller_name: str) -> Any:
        # D'abord vérifier dans le cache des noms mappés
        if controller_name in self._controller_name_to_class:
            controller_class = self._controller_name_to_class[controller_name]
            if controller_class not in self._controller_cache.values():
                self._controller_cache[controller_name] = controller_class
            return self._create_controller_instance(controller_class)

        if controller_name in self._controller_cache:
            controller_class = self._controller_cache[controller_name]
            return self._create_controller_instance(controller_class)

        controller_class = self._load_controller_class(controller_name)
        if controller_class:
            self._controller_cache[controller_name] = controller_class
            return self._create_controller_instance(controller_class)

        searched_paths = [path for path in self._controller_paths.values()]
        raise ControllerNotFoundError(controller_name, searched_paths)

    def _load_controller_class(self, controller_name: str) -> Optional[Type]:

        if controller_name in self._controller_paths:
            return self._load_from_path(self._controller_paths[controller_name])

        controller_dir = Path("src/controller")
        if controller_dir.exists():
            for file in controller_dir.rglob("*.py"):
                if file.name == "__init__.py":
                    continue

                controller_class = self._load_from_path(file)
                if controller_class:

                    generated_name = controller_class.__name__.replace("Controller", "").lower()
                    if generated_name == controller_name:
                        return controller_class

        return None

    def _load_from_path(self, file_path: Path) -> Optional[Type]:
        try:
            rel_path = file_path.relative_to(Path("src")).with_suffix("")
            module_name = f"src.{rel_path.as_posix().replace('/', '.')}"
            module = importlib.import_module(module_name)

            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and name.endswith("Controller") and obj.__module__ == module_name:
                    return obj
        except ImportError as e:
            raise ControllerModuleError(module_name, e)
        except Exception as e:
            self._logger.warning(f"Failed to load controller from {file_path}: {e}")

        return None

    def _create_controller_instance(self, controller_class: Type) -> Any:
        try:
            dependencies = self._resolve_controller_dependencies(controller_class)
            return controller_class(*dependencies)
        except Exception as e:
            raise ControllerInstantiationError(controller_class.__name__, str(e), e)

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
                    except Exception as e:
                        if param.default != inspect.Parameter.empty:
                            dependencies.append(param.default)
                        else:
                            raise ControllerDependencyError(controller_class.__name__, param_name, e)
                elif param.default != inspect.Parameter.empty:
                    dependencies.append(param.default)
        except ControllerDependencyError:
            raise
        except Exception:
            pass

        return dependencies
