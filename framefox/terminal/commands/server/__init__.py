from typer import Typer, Option

from .server_start_command import ServerStartCommand
from .worker_command import WorkerCommand


def add_server_commands(app: Typer) -> None:
    server_commands = Typer(
        no_args_is_help=True,
        rich_markup_mode="rich",
    )

    @server_commands.command()
    def start(port: int = Option(None, help="The port to run the server on."), with_worker: bool = Option(False, help="Whete to start the process with workers.")):
        """
        Start the uvicorn server.
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