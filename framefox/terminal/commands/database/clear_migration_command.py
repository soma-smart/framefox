from framefox.core.orm.migration.alembic_manager import AlembicManager
from framefox.terminal.commands.database.abstract_database_command import (
    AbstractDatabaseCommand,
)

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class ClearMigrationCommand(AbstractDatabaseCommand):
    def __init__(self):
        super().__init__("clear-migration")
        self.alembic_manager = AlembicManager()

    def execute(self):
        """Clear all migration files and reset migration table in database"""
        try:
            self.printer.print_msg("Clearing migration files and database references...", theme="info")

            # Check if database exists
            if not self.driver.database_exists(self.connection_manager.config.database):
                self.printer.print_msg(
                    "Database does not exist. Only clearing migration files.",
                    theme="warning",
                )
                # Only clear files, not database table
                self.alembic_manager.cleanup_migrations()
                self.alembic_manager.setup_directories()
                self.printer.print_msg("Migration files cleared", theme="success")
                return

            # Clear migration table in database using AlembicManager
            table_cleared = self.alembic_manager.clear_alembic_version_table()
            if table_cleared:
                self.printer.print_msg("Migration table cleared", theme="success")
            else:
                self.printer.print_msg("Migration table does not exist", theme="info")

            # Clear migration files using AlembicManager
            self.alembic_manager.cleanup_migrations()
            self.alembic_manager.setup_directories()
            self.printer.print_msg("Migration files cleared", theme="success")

            self.printer.print_msg("Migration files and database references cleared successfully", theme="success")
            self.printer.print_msg("You can now create new migrations with 'framefox database create-migration'", theme="info")

        except Exception as e:
            self.printer.print_msg(
                f"Error while clearing migrations: {str(e)}",
                theme="error",
            )
