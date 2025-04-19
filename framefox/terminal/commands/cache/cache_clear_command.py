import os
import shutil

from rich.console import Console
from rich.table import Table

from framefox.terminal.commands.abstract_command import AbstractCommand

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


CACHE_DIRS = [
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "var/cache",
    "var/log/*.log",
    "var/session/*",
]
EXCLUDED_DIRS = [
    "migrations/versions/__pycache__",
]


class CacheClearCommand(AbstractCommand):
    def __init__(self):
        super().__init__()

    def execute(self):
        console = Console()
        print("")

        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Location", style="bold orange3")
        table.add_column("Status", style="white")

        for cache_dir in CACHE_DIRS:
            if cache_dir in EXCLUDED_DIRS:
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
