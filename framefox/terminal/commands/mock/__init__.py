from typer import Typer

from .mock_create_command import MockCreateCommand
from .mock_load_command import MockLoadCommand


def add_mock_commands(app: Typer) -> None:
    mock_commands = Typer(
        no_args_is_help=True,
        rich_markup_mode="rich",
        pretty_exceptions_enable=False,
    )

    @mock_commands.command()
    def create(*args, **kwargs):
        MockCreateCommand().execute(*args, **kwargs)

    @mock_commands.command()
    def load(*args, **kwargs):
        MockLoadCommand().execute(*args, **kwargs)

    app.add_typer(
        mock_commands,
        name="mock",
        help="Mock management commands",
    )