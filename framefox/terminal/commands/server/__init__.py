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
    def start(port: int | None, with_worker: bool = False):
        ServerStartCommand().execute(port, with_worker=with_worker)

    @server_commands.command()
    def worker():
        WorkerCommand().execute()

    app.add_typer(
        server_commands,
        name="server",
        help="Server management commands",
    )