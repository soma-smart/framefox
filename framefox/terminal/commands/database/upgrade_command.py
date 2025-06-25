from framefox.core.orm.migration.alembic_manager import AlembicManager
from framefox.terminal.commands.database.abstract_database_command import (
    AbstractDatabaseCommand,
)

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class UpgradeCommand(AbstractDatabaseCommand):
    def __init__(self):
        super().__init__("upgrade")
        self.alembic_manager = AlembicManager()

    def execute(self):
        """
        Apply all migrations to the database.\n
        This command checks if the database exists, then applies all pending migrations.\n
        If the database does not exist, it prompts the user to create it first.\n
        If the database is already up to date, it informs the user.\n
        If an error occurs during the migration process, it displays an error message.\n
        """
        try:
            # Vérifier si la base de données existe
            if not self.driver.database_exists(self.connection_manager.config.database):
                self.printer.print_msg(
                    "The database does not exist. Please create it first.",
                    theme="error",
                )
                return

            self.printer.print_msg("Applying migrations...", theme="info")

            # Utiliser le gestionnaire pour appliquer les migrations
            success, migrations_applied = self.alembic_manager.upgrade("head")

            if success:
                if migrations_applied:
                    self.printer.print_msg(
                        "Migrations applied successfully.", theme="success"
                    )
                else:
                    self.printer.print_msg(
                        "The database is already up to date, no migrations to apply.",
                        theme="info",
                    )

                self.printer.print_full_text(
                    "You can use [bold orange1]framefox database downgrade[/bold orange1] to undo the migrations if necessary.",
                    linebefore=True,
                )
            else:
                self.printer.print_msg("Failed to apply migrations.", theme="error")

        except Exception as e:
            self.printer.print_msg(
                f"An error occurred while applying migrations: {str(e)}",
                theme="error",
            )
