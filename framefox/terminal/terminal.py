import contextlib
import os
import sys
from io import StringIO
from typing import List

import typer

from framefox.terminal.command_registry import CommandRegistry
from framefox.terminal.typer_config.app_configurator import AppConfigurator
from framefox.terminal.ui.display_manager import DisplayManager
from framefox.terminal.ui.error_handler import ErrorHandler
from framefox.terminal.utils.terminal.command_suggestion_service import (
    CommandSuggestionService,
)

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class Terminal:
    """
    Terminal is the main entry point for the command-line interface (CLI) application.

    This class is responsible for initializing the command registry, display manager, error handler,
    and command suggestion service. It manages the application's lifecycle, including parsing arguments,
    handling errors, suggesting commands, and executing the appropriate command logic.
    """

    def __init__(self):
        self.registry = CommandRegistry()
        self.display_manager = DisplayManager()
        self.error_handler = ErrorHandler(self.display_manager.console, self.display_manager)
        self.suggestion_service = CommandSuggestionService(self.registry)
        self.registry.discover_commands()
        configurator = AppConfigurator(self.registry, self.display_manager)
        self.app = configurator.configure()

    def run(self, args: List[str] = None):
        if args is None:
            args = sys.argv[1:]
        if self._is_init_only_context(args):
            return self._run_init_command()
        return self._run_with_error_handling(args)

    def _run_with_error_handling(self, args: List[str]) -> int:
        stderr_capture = StringIO()
        try:
            with contextlib.redirect_stderr(stderr_capture):
                return self.app(args)
        except typer.Exit as e:
            return e.exit_code
        except SystemExit as e:
            captured_error = stderr_capture.getvalue()
            if e.code == 2 and args and self._is_command_not_found_error(captured_error):
                return self._handle_unknown_command(args)
            return e.code
        except Exception as e:
            self.display_manager.print_error(f"An unexpected error occurred: {e}")
            return 1

    def _is_command_not_found_error(self, error_output: str) -> bool:
        error_indicators = [
            "No such command",
            "Try '",
            "Usage:",
            "Error",
        ]
        return any(indicator in error_output for indicator in error_indicators)

    def _handle_unknown_command(self, args: List[str]) -> int:
        if not args:
            return 2
        command_groups = self.registry.get_command_groups()
        if len(args) >= 2:
            suggestion_result = self.suggestion_service.suggest_command_with_subcommand(args)
            if suggestion_result:
                return self._handle_suggestion_result(suggestion_result)
        if len(args) == 1:
            available_groups = [group for group in command_groups.keys() if group != "main"]
            available_groups.extend(["init", "list"])
            if self.error_handler.handle_unknown_command(args[0], available_groups):
                return 1
        elif len(args) == 2:
            group_name, subcommand = args[0], args[1]
            if group_name in command_groups:
                available_subcommands = list(command_groups[group_name].keys())
                if self.error_handler.handle_unknown_subcommand(group_name, subcommand, available_subcommands):
                    return 1
        self.error_handler.handle_general_error(args)
        return 1

    def _handle_suggestion_result(self, result) -> int:
        if len(result) == 2:
            error_msg, suggestion = result
            self.error_handler._print_error_header(error_msg)
            self.error_handler._display_single_suggestion(suggestion)
        elif len(result) == 3:
            error_msg, group_info, subcommands = result
            if group_info.startswith("group:"):
                group_name = group_info.replace("group:", "")
                self.error_handler._print_error_header(error_msg)
                self.error_handler.display_group_with_available_subcommands(group_name, subcommands)
        return 1

    def _is_init_only_context(self, args: List[str]) -> bool:
        return len(args) == 1 and args[0] == "init" and not os.path.exists("src")

    def _run_init_command(self) -> int:
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
