from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from rich.console import Console
from rich.table import Table
from sqlalchemy import create_engine

from framefox.core.orm.migration.alembic_manager import AlembicManager
from framefox.terminal.commands.database.abstract_database_command import (
    AbstractDatabaseCommand,
)


class StatusCommand(AbstractDatabaseCommand):
    def __init__(self):
        super().__init__()
        self.alembic_manager = AlembicManager()

    def execute(self):
        """
        Check the status of the database and migrations.\n
        This method performs the following steps:\n
        1. Check if the database exists and is accessible.\n
        2. Display the database connection status.\n
        3. List all migrations with their current status.\n
        """
        try:
            console = Console()
            console.print("")
            console.print("[bold orange1]Database Status[/bold orange1]")
            console.print("")

            db_table = Table(show_header=True, header_style="bold orange1")
            db_table.add_column("Component", style="bold orange3")
            db_table.add_column("Status", style="white")
            db_table.add_column("Details", style="white")

            db_name = self.connection_manager.config.database
            db_exists = self.driver.database_exists(db_name)

            db_table.add_row(
                "Database",
                "[green]Exists[/green]" if db_exists else "[red]Does not exist[/red]",
                db_name,
            )

            connection_ok = False
            error_message = ""

            if db_exists:
                try:
                    engine = create_engine(self.alembic_manager.get_database_url_string())
                    with engine.connect() as connection:
                        connection_ok = True
                except Exception as e:
                    error_message = str(e)

            db_table.add_row(
                "Connection",
                "[green]Established[/green]" if connection_ok else "[red]Failed[/red]",
                (error_message if error_message else ("OK" if connection_ok else "Not connected")),
            )

            if db_exists and connection_ok:
                driver_name = self.connection_manager.config.driver
                host = self.connection_manager.config.host
                port = self.connection_manager.config.port

                db_table.add_row("Type", f"[cyan]{driver_name.upper()}[/cyan]", f"{host}:{port}")

            console.print(db_table)
            console.print("")

            if not db_exists:
                self.printer.print_msg(
                    "The database does not exist. Please run 'framefox database:create' first.",
                    theme="error",
                )
                return

            if not connection_ok:
                self.printer.print_msg(
                    f"Unable to connect to the database: {error_message}",
                    theme="error",
                )
                return

            alembic_cfg = self.alembic_manager.create_config()
            script = ScriptDirectory.from_config(alembic_cfg)

            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()

                heads = script.get_revisions("heads")
                head_rev = heads[0].revision if heads else None

                table = Table(show_header=True, header_style="bold orange1")
                table.add_column("Version", style="cyan")
                table.add_column("Description", style="white")
                table.add_column("Status", style="green")

                rows = []
                for rev in script.walk_revisions():
                    if current_rev is None:
                        status = "PENDING"
                    else:
                        status = (
                            "CURRENT"
                            if rev.revision == current_rev
                            else (
                                "PENDING"
                                if rev.revision in [r.revision for r in script.iterate_revisions(current_rev, "head")]
                                else "APPLIED"
                            )
                        )
                    rows.append((rev.revision, rev.doc or "", status))

                console.print("[bold orange1]Migration Status[/bold orange1]")
                console.print("")

                for row in rows:
                    table.add_row(*row)

                console.print(table)
                console.print("")

                if current_rev != head_rev:
                    if current_rev is None:
                        self.printer.print_msg("No migrations applied", theme="warning")
                    else:
                        pending = list(script.iterate_revisions(current_rev, "head"))
                        self.printer.print_msg(f"{len(pending)} pending migration(s)", theme="warning")
                else:
                    self.printer.print_msg("The database is up to date", theme="success")

                self.alembic_manager.cleanup_temp_files()

        except Exception as e:
            self.printer.print_msg(
                f"Error while checking migrations: {str(e)}",
                theme="error",
            )
            self.alembic_manager.cleanup_temp_files()
