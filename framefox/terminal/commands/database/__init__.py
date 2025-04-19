from typer import Typer

from .clear_metadata_command import ClearMetadataCommand
from .copy_command import CopyCommand
from .create_command import CreateCommand
from .create_migration_command import CreateMigrationCommand
from .downgrade_command import DowngradeCommand
from .drop_command import DropCommand
from .status_command import StatusCommand
from .upgrade_command import UpgradeCommand


def add_database_commands(app: Typer) -> None:
    database_commands = Typer(
        no_args_is_help=True,
        rich_markup_mode="rich",
        pretty_exceptions_enable=False,
    )

    @database_commands.command()
    def clear():
        ClearMetadataCommand().execute()

    @database_commands.command()
    def copy():
        CopyCommand().execute()

    @database_commands.command()
    def create():
        CreateCommand().execute()

    @database_commands.command()
    def migration():
        CreateMigrationCommand().execute()

    @database_commands.command()
    def downgrade(steps: int | None = None):
        DowngradeCommand().execute(steps)

    @database_commands.command()
    def drop():
        DropCommand().execute()

    @database_commands.command()
    def status():
        StatusCommand().execute()

    @database_commands.command()
    def upgrade():
        UpgradeCommand().execute()

    app.add_typer(
        database_commands,
        name="database",
        help="Database management commands",
    )