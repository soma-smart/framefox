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
    def start(port: int | None = None, with_worker: bool = False):
        """
        Start the uvicorn server.

        Args:
            port (int, optional): The port to run the server on.
        """
        ServerStartCommand().execute(port, with_worker)

    @server_commands.command()
    def worker():
        """
        Start the worker process to consume tasks from the queue."""
        WorkerCommand().execute()

    app.add_typer(
        server_commands,
        name="server",
        help="Server operations like starting or stopping the server.",
    )