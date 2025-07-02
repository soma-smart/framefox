import hashlib
import importlib
import inspect
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Type

from framefox.terminal.commands.abstract_command import AbstractCommand

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class CommandRegistry:
    """Registry for managing and discovering CLI commands with caching support"""

    def __init__(self):
        self.commands: Dict[str, Type[AbstractCommand]] = {}
        self.command_groups: Dict[str, List[str]] = {}
        self.initialized = False
        self._cache_file = Path("var/cache/command_registry.json")
        self._cache_file.parent.mkdir(parents=True, exist_ok=True)

        # Setup logger
        self.logger = logging.getLogger(__name__)

    def discover_commands(self):
        """Discover all available commands using cache when possible"""
        if self.initialized:
            return

        project_exists = os.path.exists("src")

        if not project_exists:
            self._load_init_only()
            return

        if self._try_load_from_cache():
            self.initialized = True
            return

        self._full_discovery(project_exists)
        self._save_cache()
        self.initialized = True

    def _load_init_only(self):
        """Load only the init command for non-project contexts"""
        try:
            from framefox.terminal.commands.init_command import InitCommand

            self.add_command(InitCommand, "main")
            self.initialized = True
        except ImportError as e:
            self.logger.error(f"Failed to load InitCommand: {e}")

    def _try_load_from_cache(self) -> bool:
        """Attempt to load commands from cache if valid"""
        if not self._cache_file.exists():
            return False

        try:
            with open(self._cache_file, "r") as f:
                cache_data = json.load(f)

            if not self._is_cache_valid(cache_data.get("file_hashes", {})):
                return False

            self.command_groups = cache_data.get("command_groups", {})
            self._restore_command_classes(cache_data.get("command_modules", {}))
            return True

        except Exception as e:
            self.logger.debug(f"Cache invalid or corrupted: {e}")
            return False

    def _is_cache_valid(self, cached_hashes: Dict[str, str]) -> bool:
        """Check if cached file hashes match current files"""
        commands_path = Path(__file__).parent / "commands"

        if not commands_path.exists():
            return False

        try:
            for file_path in commands_path.rglob("*_command.py"):
                if file_path.name == "__init__.py":
                    continue

                file_key = str(file_path.relative_to(commands_path))
                stat = file_path.stat()
                current_hash = hashlib.md5(f"{stat.st_mtime}{stat.st_size}".encode()).hexdigest()

                if cached_hashes.get(file_key) != current_hash:
                    return False

            return True
        except Exception:
            return False

    def _save_cache(self):
        """Save current command registry state to cache"""
        try:
            commands_path = Path(__file__).parent / "commands"
            file_hashes = {}

            if commands_path.exists():
                for file_path in commands_path.rglob("*_command.py"):
                    if file_path.name == "__init__.py":
                        continue
                    file_key = str(file_path.relative_to(commands_path))
                    stat = file_path.stat()
                    file_hashes[file_key] = hashlib.md5(f"{stat.st_mtime}{stat.st_size}".encode()).hexdigest()

            command_modules = {}
            for cmd_id, cmd_class in self.commands.items():
                if hasattr(cmd_class, "__module__") and hasattr(cmd_class, "__name__"):
                    command_modules[cmd_id] = {
                        "module": cmd_class.__module__,
                        "class_name": cmd_class.__name__,
                    }

            cache_data = {
                "command_groups": self.command_groups,
                "command_modules": command_modules,
                "file_hashes": file_hashes,
                "version": "1.0",
                "timestamp": time.time(),
            }

            with open(self._cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save cache: {e}")

    def _restore_command_classes(self, command_modules: Dict):
        """Restore command classes from cached module information"""
        for cmd_id, module_info in command_modules.items():
            try:
                lazy_class = self._create_lazy_class(module_info["module"], module_info["class_name"])
                self.commands[cmd_id] = lazy_class
            except Exception as e:
                self.logger.debug(f"Failed to restore command {cmd_id}: {e}")

    def _create_lazy_class(self, module_name: str, class_name: str):
        """Create a lazy-loading proxy class for commands"""

        class LazyCommandClass:
            _real_class = None
            _module_name = module_name
            _class_name = class_name

            def __new__(cls):
                if cls._real_class is None:
                    try:
                        module = importlib.import_module(cls._module_name)
                        cls._real_class = getattr(module, cls._class_name)
                    except Exception as e:
                        logging.getLogger(__name__).debug(f"Lazy import failed for {cls._class_name}: {e}")
                        return None
                return cls._real_class()

            @classmethod
            def get_name(cls):
                if cls._real_class is None:
                    try:
                        module = importlib.import_module(cls._module_name)
                        cls._real_class = getattr(module, cls._class_name)
                    except Exception:
                        return cls._class_name.replace("Command", "").lower()
                return cls._real_class().get_name()

        LazyCommandClass.__name__ = class_name
        LazyCommandClass.__module__ = module_name
        return LazyCommandClass

    def _full_discovery(self, project_exists: bool):
        """Perform full command discovery by scanning command directories"""
        commands_path = Path(__file__).parent / "commands"
        excluded_commands = ["InitCommand"] if project_exists else []

        self._discover_in_path(
            commands_path,
            "framefox.terminal.commands",
            excluded_commands=excluded_commands,
        )
        self._load_run_command()

    def _discover_in_path(self, path: Path, module_prefix: str, excluded_commands: List[str] = None):
        """Recursively discover commands in the given path"""
        if excluded_commands is None:
            excluded_commands = []

        if not path.exists():
            return

        try:
            # Load commands from current directory
            for file_path in path.glob("*_command.py"):
                if file_path.name == "__init__.py":
                    continue
                module_name = f"{module_prefix}.{file_path.stem}"
                self._load_commands_from_module(module_name, "main", excluded_commands)

            # Load commands from subdirectories (namespaces)
            for subdir in path.iterdir():
                if subdir.is_dir() and not subdir.name.startswith("__"):
                    namespace = subdir.name
                    sub_module_prefix = f"{module_prefix}.{namespace}"
                    for file_path in subdir.glob("*_command.py"):
                        if file_path.name == "__init__.py":
                            continue
                        module_name = f"{sub_module_prefix}.{file_path.stem}"
                        self._load_commands_from_module(module_name, namespace, excluded_commands)

        except Exception as e:
            self.logger.error(f"Failed to discover commands in {path}: {e}")

    def _load_commands_from_module(self, module_name: str, namespace: str, excluded_commands: List[str]):
        """Load command classes from a specific module"""
        try:
            module = importlib.import_module(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    hasattr(attr, "__module__")
                    and attr.__module__ == module_name
                    and inspect.isclass(attr)
                    and issubclass(attr, AbstractCommand)
                    and attr is not AbstractCommand
                    and attr_name not in excluded_commands
                    and not attr_name.startswith("Abstract")
                    and not getattr(attr, "__abstractmethods__", None)
                ):
                    self.add_command(attr, namespace)
        except Exception as e:
            self.logger.debug(f"Failed to load module {module_name}: {e}")

    def _load_run_command(self):
        """Load the special run and star-us commands"""
        try:
            from framefox.terminal.commands.run_command import RunCommand

            self.add_command(RunCommand, "main")
        except ImportError as e:
            self.logger.debug(f"Failed to load RunCommand: {e}")

        try:
            from framefox.terminal.commands.star_us_command import StarUsCommand

            self.add_command(StarUsCommand, "main")
        except ImportError as e:
            self.logger.debug(f"Failed to load StarUsCommand: {e}")

    def add_command(self, command_class: Type[AbstractCommand], namespace: str = "main"):
        """Add a command class to the registry"""
        try:
            # Determine command name
            base_name = command_class.__name__.replace("Command", "").lower()
            if namespace == "main":
                command_name = base_name
            else:
                if base_name.startswith(namespace):
                    command_name = base_name[len(namespace) :]
                else:
                    prefixes_to_remove = [
                        "create",
                        "debug",
                        "mock",
                        "cache",
                        "database",
                        "server",
                    ]
                    for prefix in prefixes_to_remove:
                        if base_name.startswith(prefix):
                            command_name = base_name[len(prefix) :]
                            break
                    else:
                        command_name = base_name

                # Si le nom de commande est vide, utiliser le nom de base
                if not command_name:
                    command_name = base_name

            # Try to instantiate to get the actual name
            command_instance = None
            try:
                command_instance = command_class(command_name)
            except TypeError:
                try:
                    command_instance = command_class()
                    if hasattr(command_instance, "name"):
                        command_instance.name = command_name
                except Exception:
                    self.logger.debug(f"Skipping command {command_class.__name__}: incompatible constructor")
                    return

            # Get final name from instance if possible
            if hasattr(command_instance, "get_name"):
                final_name = command_instance.get_name()
            else:
                final_name = command_name

            # Register the command
            self.commands[final_name] = command_class
            if namespace not in self.command_groups:
                self.command_groups[namespace] = []
            if final_name not in self.command_groups[namespace]:
                self.command_groups[namespace].append(final_name)

        except Exception as e:
            self.logger.debug(f"Failed to add command {command_class.__name__}: {e}")

    def get_command(self, name: str) -> Optional[Type[AbstractCommand]]:
        """Retrieve a command class by name"""
        if not self.initialized:
            self.discover_commands()

        command_class = self.commands.get(name)
        if not command_class:
            return None

        # Resolve lazy class if needed
        if hasattr(command_class, "_real_class"):
            if command_class._real_class is None:
                try:
                    module = importlib.import_module(command_class._module_name)
                    command_class._real_class = getattr(module, command_class._class_name)
                except Exception as e:
                    self.logger.error(f"Failed to resolve lazy command {command_class._class_name}: {e}")
                    return None
            return command_class._real_class

        return command_class

    def get_all_commands(self) -> Dict[str, Type[AbstractCommand]]:
        """Get a copy of all registered commands"""
        if not self.initialized:
            self.discover_commands()
        return self.commands.copy()

    def get_commands_by_group(self, group: str) -> List[str]:
        """Get command names for a specific group"""
        if not self.initialized:
            self.discover_commands()
        return self.command_groups.get(group, [])

    def get_command_groups(self) -> Dict[str, Dict[str, Type[AbstractCommand]]]:
        """Get all command groups with resolved classes"""
        if not self.initialized:
            self.discover_commands()

        groups_with_classes = {}
        for namespace, command_names in self.command_groups.items():
            groups_with_classes[namespace] = {}
            for command_name in command_names:
                real_class = self.get_command(command_name)
                if real_class:
                    groups_with_classes[namespace][command_name] = real_class
                else:
                    self.logger.warning(f"Could not resolve command '{command_name}'")

        return groups_with_classes

    def list_all_commands(self) -> Dict[str, List[str]]:
        """Get a copy of all command groups (names only)"""
        if not self.initialized:
            self.discover_commands()
        return self.command_groups.copy()

    def clear_cache(self):
        """Clear the command registry cache"""
        try:
            if self._cache_file.exists():
                self._cache_file.unlink()
            self.logger.info("Command cache cleared successfully")
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")

    def rebuild_cache(self):
        """Rebuild the command registry cache from scratch"""
        self.clear_cache()
        self.initialized = False
        self.commands.clear()
        self.command_groups.clear()
        self.discover_commands()
        self.logger.info("Command cache rebuilt successfully")
