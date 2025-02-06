import os
import shutil
from framefox.terminal.commands.abstract_command import AbstractCommand
from rich.table import Table
from rich.console import Console


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
            ".coverage"
        ]

    def execute(self):
        """
        Clear all cache files and directories
        """
        console = Console()
        print("")

        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Location", style="bold orange3")
        table.add_column("Status", style="white")
        table.add_column("Details", style="white")

        total_cleared = 0

        # Parcourir récursivement pour trouver tous les dossiers cache
        for root, dirs, files in os.walk("."):
            for dir_name in dirs:
                if dir_name in self.cache_dirs:
                    path = os.path.join(root, dir_name)
                    try:
                        shutil.rmtree(path)
                        table.add_row(
                            path,
                            "[green]Cleared[/green]",
                            "Directory removed"
                        )
                        total_cleared += 1
                    except Exception as e:
                        table.add_row(
                            path,
                            "[red]Error[/red]",
                            str(e)
                        )

            # Nettoyer les fichiers .pyc
            for file in files:
                if file.endswith(".pyc"):
                    path = os.path.join(root, file)
                    try:
                        os.remove(path)
                        table.add_row(
                            path,
                            "[green]Cleared[/green]",
                            "File removed"
                        )
                        total_cleared += 1
                    except Exception as e:
                        table.add_row(
                            path,
                            "[red]Error[/red]",
                            str(e)
                        )

        console.print(table)
        print("")

        self.printer.print_full_text(
            f"[bold green]✓ Cache cleared: {
                total_cleared} items removed[/bold green]",
            linebefore=True
        )
