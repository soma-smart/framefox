from framefox.terminal.commands.abstract_command import AbstractCommand
from alembic import command
from framefox.terminal.common.alembic_file_manager import AlembicFileManager
from framefox.terminal.commands.orm.database.orm_copy_db_command import OrmCopyDbCommand
from contextlib import closing
import typer


class OrmRollbackDbCommand(AbstractCommand):
    def __init__(self):
        super().__init__("downgrade")
        self.alembic_manager = AlembicFileManager()

    def execute(self, steps: int = typer.Argument(1, help="Number of migrations to rollback")):
        """Rolls back migrations"""
        try:
            if not OrmCopyDbCommand.database_exists(
                self.alembic_manager.get_database_url()
            ):
                self.printer.print_msg(
                    "The database does not exist. Please create it first.",
                    theme="error",
                )
                return

            alembic_cfg = self.alembic_manager.get_config()

            with closing(self.alembic_manager.get_engine_connection()) as connection:
                alembic_cfg.attributes["connection"] = connection
                command.downgrade(alembic_cfg, f"-{steps}")

            self.printer.print_msg(
                f"Successfully rolled back {steps} migration{
                    's' if steps > 1 else ''}.",
                theme="success"
            )
        except Exception as e:
            self.printer.print_msg(
                f"Error rolling back migrations: {str(e)}",
                theme="error"
            )
