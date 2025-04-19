from typer import Typer

from .server_start_command import ServerStartCommand
from .worker_command import WorkerCommand


def add_server_commands(app: Typer) -> None:
    server_commands = Typer(
        no_args_is_help=True,
        rich_markup_mode="rich",
        pretty_exceptions_enable=False,
    )

    @server_commands.command()
    def start(*args, **kwargs):
        ServerStartCommand().execute(*args, **kwargs)

    @server_commands.command()
    def worker(*args, **kwargs):
        WorkerCommand().execute(*args, **kwargs)

    app.add_typer(
        server_commands,
        name="server",
        help="Server management commands",
    )