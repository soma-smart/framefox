import importlib
import inspect
import os
import pkgutil
from abc import ABC
from pathlib import Path
from typing import Dict, List

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class CommandRegistry:
    """
    Global registry of all available commands.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CommandRegistry, cls).__new__(cls)
            cls._instance.commands = {}
            cls._instance.initialized = False
        return cls._instance

    def get_command(self, name: str):
        """Retrieve a command by its full name (e.g., 'server:start')"""
        if not self.initialized:
            self.discover_commands()

        return self.commands.get(name)

    def add_command(self, command_class, namespace=None, name=None):
        """Add a command to the registry with an optional namespace"""
        if not name:
            class_name = command_class.__name__
            if class_name.endswith("Command"):
                class_name = class_name[:-7]

            if namespace and class_name.lower().startswith(namespace.lower()):
                class_name = class_name[len(namespace.title()) :]

            name = ""
            for i, c in enumerate(class_name):
                if c.isupper() and i > 0:
                    name += "-" + c.lower()
                else:
                    name += c.lower()

        if not namespace:
            module_parts = command_class.__module__.split(".")
            if len(module_parts) >= 3 and module_parts[-3] == "commands":
                namespace = module_parts[-2]
            else:
                namespace = "main"

        command_id = f"{namespace}:{name}" if namespace != "main" else name
        self.commands[command_id] = command_class
        return command_id

    def discover_commands(self):
        """Automatically discover all commands in the project"""
        if self.initialized:
            return

        project_exists = os.path.exists("src")

        if not project_exists:
            try:
                module = importlib.import_module(
                    "framefox.terminal.commands.init_command"
                )
                command_class = getattr(module, "InitCommand")
                self.add_command(command_class)
                self.initialized = True
                return
            except (ImportError, AttributeError) as e:
                print(f"Error loading initialization command: {e}")

        commands_path = Path(__file__).parent / "commands"
        self._discover_in_path(
            commands_path,
            "framefox.terminal.commands",
            excluded_commands=["InitCommand"] if project_exists else [],
        )

        src_commands = Path(__file__).parent.parent.parent / "src" / "commands"
        if src_commands.exists():
            self._discover_in_path(
                src_commands,
                "src.commands",
                excluded_commands=["InitCommand"] if project_exists else [],
            )

        self.initialized = True

    def _discover_in_path(
        self, path: Path, package_prefix: str, excluded_commands=None
    ):
        """
        Discover commands in a specific path

        Args:
            path: Path to explore
            package_prefix: Package prefix for import
            excluded_commands: List of command class names to exclude
        """
        if not path.exists():
            return

        excluded_commands = excluded_commands or []

        for item in path.iterdir():
            if item.is_dir() and not item.name.startswith("__"):
                namespace = item.name
                self._discover_in_package(
                    f"{package_prefix}.{namespace}", namespace, excluded_commands
                )

        self._discover_in_package(package_prefix, "main", excluded_commands)

    def _discover_in_package(
        self, package_name: str, namespace: str, excluded_commands=None
    ):
        """Discover commands in a Python package"""
        excluded_commands = excluded_commands or []

        try:
            package = importlib.import_module(package_name)
        except ImportError:
            print(f"Package {package_name} not found")
            return

        for _, name, is_pkg in pkgutil.iter_modules(
            package.__path__, package.__name__ + "."
        ):
            if not is_pkg and name.endswith("_command"):
                try:
                    module = importlib.import_module(name)
                    for item_name in dir(module):

                        if (
                            item_name.endswith("Command")
                            and not item_name.startswith("Abstract")
                            and item_name not in excluded_commands
                        ):
                            command_class = getattr(module, item_name)
                            if inspect.isclass(command_class):

                                if not self._is_abstract_class(command_class):
                                    self.add_command(command_class, namespace)
                except ImportError as e:
                    print(f"Error loading {name}: {e}")

    def _is_abstract_class(self, cls):
        """
        Detects if a class is abstract.
        """

        if cls.__name__.startswith("Abstract"):
            return True

        if hasattr(cls, "__abstractmethods__") and cls.__abstractmethods__:
            return True

        if cls is ABC:
            return True

        return False

    def list_commands(self) -> Dict[str, List[str]]:
        """Return commands organized by namespace"""
        if not self.initialized:
            self.discover_commands()

        result = {}
        for command_id in sorted(self.commands.keys()):
            if ":" in command_id:
                namespace, name = command_id.split(":", 1)
            else:
                namespace, name = "main", command_id

            if namespace not in result:
                result[namespace] = []
            result[namespace].append(name)

        return result
