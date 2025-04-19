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
    def create(name: str | None = None):
        """
        Create mock file for an entity
        
        Args:
            name (str, optional): Name of the entity. Defaults to None.
        """
        MockCreateCommand().execute(name)

    @mock_commands.command()
    def load():
        """
        Load all mocks found in the mocks directory.
        """
        MockLoadCommand().execute()

    app.add_typer(
        mock_commands,
        name="mock",
        help="Mock management commands",
    )