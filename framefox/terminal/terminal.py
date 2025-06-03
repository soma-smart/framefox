import os
import sys
from typing import List

import typer

from framefox.terminal.command_registry import CommandRegistry
from framefox.terminal.typer_config.app_configurator import AppConfigurator
from framefox.terminal.ui.display_manager import DisplayManager
from framefox.terminal.ui.error_handler import ErrorHandler

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
        self.error_handler = ErrorHandler(self.display_manager.console)

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

        # Use Typer for everything else with error handling
        try:
            return self.app(args)
        except typer.Exit as e:
            # Typer exit (normal behavior)
            return e.exit_code
        except SystemExit as e:
            # Handle unknown commands
            if e.code == 2 and args:  # Exit code 2 = command not found
                return self._handle_unknown_command(args)
            return e.code
        except Exception as e:
            self.display_manager.print_error(f"Unexpected error: {e}")
            return 1

    def _handle_unknown_command(self, args: List[str]) -> int:
        """Handle unknown command and suggest alternatives"""
        if not args:
            return 2

        command_groups = self.registry.get_command_groups()

        # Case 1: Unknown main command (e.g., "framefox srever")
        if len(args) == 1:
            available_groups = [
                group for group in command_groups.keys() if group != "main"
            ]
            available_groups.extend(["init", "list"])  # Add built-in commands

            if self.error_handler.handle_unknown_command(args[0], available_groups):
                return 1

        # Case 2: Unknown subcommand (e.g., "framefox server stort")
        elif len(args) == 2:
            group_name, subcommand = args[0], args[1]

            # Check if group exists
            if group_name in command_groups:
                available_subcommands = list(command_groups[group_name].keys())
                if self.error_handler.handle_unknown_subcommand(
                    group_name, subcommand, available_subcommands
                ):
                    return 1
            else:
                # Group doesn't exist, suggest group
                available_groups = [
                    group for group in command_groups.keys() if group != "main"
                ]
                available_groups.extend(["init", "list"])

                if self.error_handler.handle_unknown_command(
                    group_name, available_groups
                ):
                    return 1

        # Fallback: show general help
        self.display_manager.print_error(f"Unknown command: {' '.join(args)}")
        self.display_manager.console.print(
            "Run 'framefox --help' for available commands", style="dim white"
        )
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
