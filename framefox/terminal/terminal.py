import os
import sys
from typing import List

from framefox.terminal.command_registry import CommandRegistry
from framefox.terminal.typer_config.app_configurator import AppConfigurator
from framefox.terminal.ui.display_manager import DisplayManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class Terminal:
    """
    Main application console - Simplified and focused
    """

    def __init__(self):
        self.registry = CommandRegistry()
        self.display_manager = DisplayManager()

        # Discover commands
        self.registry.discover_commands()

        # Configure the Typer app
        configurator = AppConfigurator(self.registry, self.display_manager)
        self.app = configurator.configure()

    def run(self, args: List[str] = None):
        """Run the console application with the given arguments"""
        if args is None:
            args = sys.argv[1:]

        # Special case for 'init' without project
        if self._is_init_only_context(args):
            return self._run_init_command()

        # Use Typer for everything else
        try:
            return self.app(args)
        except SystemExit as e:
            return e.code
        except Exception as e:
            self.display_manager.print_error(f"Unexpected error: {e}")
            return 1

    def _is_init_only_context(self, args: List[str]) -> bool:
        """Check if this is an init-only context"""
        return len(args) == 1 and args[0] == "init" and not os.path.exists("src")

    def _run_init_command(self) -> int:
        """Run the init command directly"""
        command_class = self.registry.get_command("init")
        if not command_class:
            self.display_manager.print_error("Init command not found")
            return 1

        try:
            instance = command_class()
            if instance:
                return instance.execute()
        except Exception as e:
            self.display_manager.print_error(f"Error executing command init: {e}")
            return 1

        return 1
