from typer import Typer

from .debug_router_command import DebugRouterCommand
from .debug_service_command import DebugServiceCommand


def add_debug_commands(app: Typer) -> None:
    debug_commands = Typer(
        no_args_is_help=True,
        rich_markup_mode="rich",
    )

    @debug_commands.command()
    def router():
        """
        Display the list of routes
        """
        DebugRouterCommand().execute()

    @debug_commands.command()
    def service():
        """
        Display the list of registered services
        """
        DebugServiceCommand().execute()

    app.add_typer(
        debug_commands,
        name="debug",
        help="Debug operations like checking routes or testing security.",
        rich_help_panel="tools",
    )