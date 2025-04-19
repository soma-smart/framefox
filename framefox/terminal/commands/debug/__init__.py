from typer import Typer

from .debug_router_command import DebugRouterCommand
from .debug_service_command import DebugServiceCommand


def add_debug_commands(app: Typer) -> None:
    debug_commands = Typer(
        no_args_is_help=True,
        rich_markup_mode="rich",
        pretty_exceptions_enable=False,
    )

    @debug_commands.command()
    def router():
        DebugRouterCommand().execute()

    @debug_commands.command()
    def service():
        DebugServiceCommand().execute()

    app.add_typer(
        debug_commands,
        name="debug",
        help="Debug management commands",
    )