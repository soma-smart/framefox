from typing import Any, Dict

import typer

from framefox.core.di.service_container import ServiceContainer
from framefox.terminal.command_registry import CommandRegistry
from framefox.terminal.ui.display_manager import DisplayManager
from framefox.terminal.ui.themes import FramefoxMessages

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class CommandBuilder:
    """Builds Typer commands and subapps"""

    def __init__(self, registry: CommandRegistry, display_manager: DisplayManager):
        self.registry = registry
        self.display_manager = display_manager

    def create_subapp(self, namespace: str, commands: Dict[str, Any]) -> typer.Typer:
        """Create a Typer subapp for a command namespace"""
        description = self._get_namespace_description(namespace)

        subapp = typer.Typer(
            name=namespace,
            help=description,
            no_args_is_help=False,
        )

        # Setup callback for subapp help
        @subapp.callback(invoke_without_command=True)
        def subgroup_main(ctx: typer.Context):
            if ctx.invoked_subcommand is None:
                self.display_manager.print_header()
                self.display_manager.display_subgroup_help(namespace, commands, description)
                raise typer.Exit()

        # Add commands to subapp
        for command_name, command_class in commands.items():
            self._add_command_to_subapp(subapp, command_name, command_class)

        return subapp

    def _add_command_to_subapp(self, subapp: typer.Typer, command_name: str, command_class):
        """Add a single command to a subapp"""

        # Create an instance of the command
        instance = self.instantiate_command(command_class)
        if not instance:
            return

        # Use the execute method directly with its Typer annotations
        subapp.command(name=command_name)(instance.execute)

    def instantiate_command(self, command_class):
        """Instantiate a command using dependency injection if needed"""
        try:
            return command_class()
        except TypeError:
            try:
                container = ServiceContainer()
                return container.get(command_class)
            except Exception as e:
                self.display_manager.print_error(f"Error instantiating command: {e}")
                return None

    def _get_namespace_description(self, namespace: str) -> str:
        """Get description for a namespace"""
        return FramefoxMessages.NAMESPACE_DESCRIPTIONS.get(namespace, f"{namespace.title()} operations")
