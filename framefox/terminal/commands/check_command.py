import os
import sys
import shutil
import platform
from framefox.terminal.commands.abstract_command import AbstractCommand
from rich.table import Table
from rich.console import Console


class CheckCommand(AbstractCommand):
    def __init__(self):
        super().__init__("check")
        self.MIN_PYTHON_VERSION = (3, 11)
        self.MIN_DISK_SPACE = 100 * 1024 * 1024

    def execute(self):
        """
        Check if the system meets the requirements to run Framefox
        """
        console = Console()
        print("")

        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Component", style="bold orange3")
        table.add_column("Status", style="white")
        table.add_column("Required", style="white")
        table.add_column("Current", style="white")

        python_version = sys.version_info
        python_ok = python_version >= self.MIN_PYTHON_VERSION
        table.add_row(
            "Python Version",
            "[green]OK[/green]" if python_ok else "[red]Error[/red]",
            f"Python {'.'.join(map(str, self.MIN_PYTHON_VERSION))}+",
            f"Python {'.'.join(map(str, python_version[:3]))}",
        )

        os_name = platform.system()
        os_ok = os_name in ["Linux", "Darwin", "Windows", "MacOS"]
        table.add_row(
            "Operating System",
            "[green]OK[/green]" if os_ok else "[red]Not Supported[/red]",
            "Win/Linux/MacOS",
            os_name,
        )
        home = os.path.expanduser("~")
        can_write = os.access(home, os.W_OK)
        table.add_row(
            "User Permissions",
            "[green]OK[/green]" if can_write else "[red]Error[/red]",
            "Write in home",
            "OK" if can_write else "Denied",
        )

        _, _, free = shutil.disk_usage(home)
        space_ok = free > self.MIN_DISK_SPACE
        table.add_row(
            "Disk Space",
            "[green]OK[/green]" if space_ok else "[red]Insufficient[/red]",
            "100 MB minimum",
            f"{free // (1024*1024)} MB available",
        )

        console.print(table)
        print("")

        all_ok = python_ok and os_ok and can_write and space_ok
        if all_ok:
            self.printer.print_full_text(
                "[bold orange1]✓ Your system is compatible with Framefox[/bold orange1]",
                linebefore=True,
            )
        else:
            self.printer.print_full_text(
                "[bold red]✗ Your system does not meet all the required conditions[/bold red]",
                linebefore=True,
            )
