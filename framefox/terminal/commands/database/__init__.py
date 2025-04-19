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
    def clear(*args, **kwargs):
        ClearMetadataCommand().execute(*args, **kwargs)

    @database_commands.command()
    def copy(*args, **kwargs):
        CopyCommand().execute(*args, **kwargs)

    @database_commands.command()
    def create(*args, **kwargs):
        CreateCommand().execute(*args, **kwargs)

    @database_commands.command()
    def migration(*args, **kwargs):
        CreateMigrationCommand().execute(*args, **kwargs)

    @database_commands.command()
    def downgrade(*args, **kwargs):
        DowngradeCommand().execute(*args, **kwargs)

    @database_commands.command()
    def drop(*args, **kwargs):
        DropCommand().execute(*args, **kwargs)

    @database_commands.command()
    def status(*args, **kwargs):
        StatusCommand().execute(*args, **kwargs)

    @database_commands.command()
    def upgrade(*args, **kwargs):
        UpgradeCommand().execute(*args, **kwargs)

    app.add_typer(
        database_commands,
        name="database",
        help="Database management commands",
    )