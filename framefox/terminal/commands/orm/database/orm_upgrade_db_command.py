from contextlib import closing

from alembic import command

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.commands.orm.database.orm_copy_db_command import OrmCopyDbCommand
from framefox.terminal.common.alembic_file_manager import AlembicFileManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class OrmUpgradeDbCommand(AbstractCommand):
    def __init__(self):
        super().__init__("upgrade")
        self.alembic_manager = AlembicFileManager()

    def execute(self):
        """Apply all migrations to the database"""
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
                command.upgrade(alembic_cfg, "head")

            self.printer.print_msg(
                "All migrations have been successfully applied.", theme="success"
            )
            self.printer.print_full_text(
                "You can use [bold orange1]framefox orm database downgrade[/bold orange1] to roll back migrations, if you need to.",
                linebefore=True,
            )
        except Exception as e:
            self.printer.print_msg(
                f"An error occurred while applying the migrations: {e}", theme="error"
            )
