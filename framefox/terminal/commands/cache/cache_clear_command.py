import os
import shutil

from rich.console import Console
from rich.table import Table

from framefox.terminal.commands.abstract_command import AbstractCommand


class CacheClearCommand(AbstractCommand):
    def __init__(self):
        super().__init__("clear")
        self.cache_dirs = [
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            "var/cache",
            "var/log/*.log",
            "var/session/*",

        ]
        self.excluded_dirs = ["migrations/versions/__pycache__"]

    def execute(self):
        """
        Clear all cache files and directories
        """
        console = Console()
        print("")

        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Location", style="bold orange3")
        table.add_column("Status", style="white")

        for cache_dir in self.cache_dirs:
            if cache_dir in self.excluded_dirs:
                table.add_row(cache_dir, "[yellow]Excluded[/yellow]")
                continue

            if os.path.exists(cache_dir):
                try:
                    if os.path.isdir(cache_dir):
                        shutil.rmtree(cache_dir)
                    else:
                        os.remove(cache_dir)
                    table.add_row(cache_dir, "[green]Cleared[/green]")
                except Exception as e:
                    table.add_row(cache_dir, f"[red]Error: {str(e)}[/red]")
            else:
                table.add_row(cache_dir, "[yellow]Not found[/yellow]")

        console.print(table)
        print("")
        self.printer.print_msg(
            "✓ Cache clearing completed.",
            theme="success",
            linebefore=True,
        )
