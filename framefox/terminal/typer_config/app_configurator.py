import typer

from framefox.terminal.command_registry import CommandRegistry
from framefox.terminal.typer_config.command_builder import CommandBuilder
from framefox.terminal.ui.display_manager import DisplayManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class AppConfigurator:
    """Configures the main Typer application"""

    def __init__(self, registry: CommandRegistry, display_manager: DisplayManager):
        self.registry = registry
        self.display_manager = display_manager
        self.command_builder = CommandBuilder(registry, display_manager)

        self.app = typer.Typer(
            name="Framefox",
            help="🦊 Framefox - Swift, smart, and a bit foxy",
            no_args_is_help=False,
            rich_markup_mode="rich",
            pretty_exceptions_enable=False,
            add_completion=True,
            pretty_exceptions_show_locals=False,
        )

    def configure(self) -> typer.Typer:
        """Configure the application with all commands and callbacks"""
        self._setup_main_callback()
        self._setup_builtin_commands()
        self._setup_command_groups()
        return self.app

    def _setup_main_callback(self):
        """Setup the main application callback"""

        @self.app.callback(invoke_without_command=True)
        def main(
            ctx: typer.Context,
            help: bool = typer.Option(None, "--help", "-h", is_eager=True),
            all: bool = typer.Option(False, "--all", "-a"),
        ):
            """Framefox CLI - Swift, smart, and a bit foxy"""
            if ctx.invoked_subcommand is None:
                self.display_manager.print_header()
                command_groups = self.registry.get_command_groups()

                if all:
                    self.display_manager.display_all_commands(command_groups)
                else:
                    self.display_manager.display_help(command_groups)

                raise typer.Exit()

    def _setup_builtin_commands(self):
        """Setup built-in commands (list, init)"""

        # List command
        @self.app.command("list")
        def list_commands():
            """List all available commands"""
            self.display_manager.print_header()
            command_groups = self.registry.get_command_groups()
            self.display_manager.display_all_commands(command_groups)

        # Init command (if available)
        init_command = self.registry.get_command("init")
        if init_command:

            @self.app.command("init")
            def init():
                """Initialize a new Framefox project"""
                instance = self.command_builder.instantiate_command(init_command)
                if instance:
                    return instance.execute()

    def _setup_command_groups(self):
        """Setup command groups as Typer subapps"""
        command_groups = self.registry.get_command_groups()

        for namespace, commands in command_groups.items():
            if namespace == "main":
                continue

            subapp = self.command_builder.create_subapp(namespace, commands)
            self.app.add_typer(subapp, name=namespace)
