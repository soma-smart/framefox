from typer import Typer, Option

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
    )

    @database_commands.command()
    def clear():
        """
        Cleans SQLAlchemy metadata and Python cache to resolve mapper issues
        """
        ClearMetadataCommand().execute()

    @database_commands.command()
    def copy():
        """
        Copy database tables from the entity directory to the database without using migrations.
        """
        CopyCommand().execute()

    @database_commands.command()
    def create():
        """
        Create the database if it doesn't exist.
        """
        CreateCommand().execute()

    @database_commands.command()
    def migration():
        """
        Create a new migration file with Alembic
        """
        CreateMigrationCommand().execute()

    @database_commands.command()
    def downgrade(steps: int = Option(None, help="The number of migrations to revert. If not provided, reverts the last migration")):
        """
        Reverts the last migration(s) applied to the database.
        """
        DowngradeCommand().execute(steps)

    @database_commands.command()
    def drop():
        """
        Deletes the configured database
        """
        DropCommand().execute()

    @database_commands.command()
    def status():
        """
        Check the status of the database and migrations.
        """
        StatusCommand().execute()

    @database_commands.command()
    def upgrade():
        """
        Apply all migrations to the database
        """
        UpgradeCommand().execute()

    app.add_typer(
        database_commands,
        name="database",
        help="Database operations like creating or migrating databases.",
    )