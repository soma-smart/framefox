from contextlib import closing

from alembic import command
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from rich.console import Console
from rich.table import Table

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.commands.orm.database.orm_copy_db_command import OrmCopyDbCommand
from framefox.terminal.common.alembic_file_manager import AlembicFileManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class OrmStatusDbCommand(AbstractCommand):
    def __init__(self):
        super().__init__("status")
        self.alembic_manager = AlembicFileManager()

    def execute(self):
        """Check the status of migrations"""
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
            script = ScriptDirectory.from_config(alembic_cfg)

            with closing(self.alembic_manager.get_engine_connection()) as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()

                heads = script.get_revisions("heads")
                head_rev = heads[0].revision if heads else None

                table = Table(show_header=True, header_style="bold orange1")
                table.add_column("Version", style="cyan")
                table.add_column("Description", style="white")
                table.add_column("Status", style="green")

                for rev in script.walk_revisions():

                    if current_rev is None:
                        status = "PENDING"
                    else:
                        status = (
                            "CURRENT"
                            if rev.revision == current_rev
                            else (
                                "PENDING"
                                if rev.revision
                                in [
                                    r.revision
                                    for r in script.iterate_revisions(
                                        current_rev, "head"
                                    )
                                ]
                                else "APPLIED"
                            )
                        )

                    table.add_row(rev.revision, rev.doc or "", status)
                    console = Console()
                    console.print("")
                    console.print(
                        "[bold orange1]Migration Status[/bold orange1]")
                    console.print("")
                    console.print(table)
                    console.print("")

                if current_rev != head_rev:
                    if current_rev is None:
                        self.printer.print_msg(
                            "No migrations applied", theme="warning")
                    else:
                        pending = list(
                            script.iterate_revisions(current_rev, "head"))
                        self.printer.print_msg(
                            f"{len(pending)} pending migration(s)", theme="warning"
                        )
                else:
                    self.printer.print_msg(
                        "The database is up to date", theme="success"
                    )

        except Exception as e:
            self.printer.print_msg(
                f"Error while checking migrations: {str(e)}", theme="error"
            )
