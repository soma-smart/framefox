from datetime import datetime

from framefox.core.orm.migration.alembic_manager import AlembicManager
from framefox.terminal.commands.database.abstract_database_command import (
    AbstractDatabaseCommand,
)


class CreateMigrationCommand(AbstractDatabaseCommand):
    def __init__(self):
        super().__init__("migration")
        self.alembic_manager = AlembicManager()

    def execute(self):
        """
        Create a new migration file with Alembic.\n
        This command checks if the database exists, then creates a new migration file\n
        with a timestamp in the filename. If the database does not exist, it prompts the user\n
        to create it first. If no changes are detected, it deletes the migration file and informs the user.\n
        """
        try:

            if not self.driver.database_exists(self.connection_manager.config.database):
                self.printer.print_msg(
                    "The database does not exist. Please run 'framefox database create' first.",
                    theme="warning",
                )

            if self.driver.database_exists(self.connection_manager.config.database):
                db_url = self.alembic_manager.get_database_url_string()
                self.alembic_manager.create_alembic_version_table(db_url)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            migration_message = f"{timestamp}_migration"

            created_file = self.alembic_manager.create_migration(migration_message, autogenerate=True)

            if not created_file:
                self.printer.print_msg("No migration generated.", theme="warning")
                return

            content = self.alembic_manager.get_migration_content(created_file)

            if not self.alembic_manager.has_changes(content):
                self.alembic_manager.delete_migration(created_file)
                self.printer.print_msg(
                    "No changes detected since the last migration.",
                    theme="warning",
                )
            else:
                self.printer.print_msg(
                    f"Migration file '{created_file}' created successfully.",
                    theme="success",
                )
                self.printer.print_msg(
                    "You can now run the 'framefox database upgrade' command to apply the updates.",
                    theme="info",
                )

        except Exception as e:
            self.printer.print_msg(f"Error creating migration: {str(e)}", theme="error")
            self.printer.print_msg(
                "Please check your migration or entity files",
                theme="error",
            )
