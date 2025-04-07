import typer

from framefox.core.orm.migration.alembic_manager import AlembicManager
from framefox.terminal.commands.database.abstract_database_command import \
    AbstractDatabaseCommand


class DowngradeCommand(AbstractDatabaseCommand):
    def __init__(self):
        super().__init__("downgrade")
        self.alembic_manager = AlembicManager()

    def execute(self, steps: int = 1):
        """Reverts the last migration(s) applied to the database."""
        try:
            if not self.driver.database_exists(self.connection_manager.config.database):
                self.printer.print_msg(
                    "The database does not exist. Please create it first.",
                    theme="error",
                )
                return

            revision = f"-{steps}" if steps > 0 else "base"

            self.printer.print_msg(
                f"Reverting {steps} migration{'s' if steps > 1 else ''}...",
                theme="info",
            )

            if self.alembic_manager.downgrade(revision):
                self.printer.print_msg(
                    f"Successfully reverted {steps} migration{'s' if steps > 1 else ''}.",
                    theme="success",
                )
            else:
                self.printer.print_msg("Failed to revert migrations.", theme="error")

        except Exception as e:
            self.printer.print_msg(
                f"Error while reverting migrations: {str(e)}", theme="error"
            )
