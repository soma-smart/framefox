import os
import platform
import secrets
import shutil
import sys

from rich.console import Console
from rich.table import Table

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.file_creator import FileCreator

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen & LEUROND Raphael
Github: https://github.com/RayenBou
Github: https://github.com/Vasulvius
"""


class InitCommand(AbstractCommand):
    def __init__(self):
        super().__init__("init")
        self.MIN_PYTHON_VERSION = (3, 11)
        self.MIN_DISK_SPACE = 100 * 1024 * 1024

    def execute(self):
        """
        Initializes a new Framefox project
        """

        if not self.check_requirements():
            return

        if os.path.exists("src"):
            self.printer.print_msg(
                "If you want to create a new project, delete the existing project first",
                theme="warning",
                linebefore=True,
                newline=True,
            )
            return
        else:
            InitCommand.create_empty_project()
            self.printer.print_msg(
                "✓ Project created successfully",
                theme="success",
                linebefore=True,
                newline=True,
            )
            self.printer.print_full_text(
                "Next, try [bold orange1]framefox[/bold orange1] to see the available commands",
                newline=True,
            )

    @staticmethod
    def generate_secret_key():
        """Generates a random secret key of 32 bytes encoded in base64"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_empty_project():
        # Create src directories
        project_path = "src"
        os.makedirs(os.path.join(project_path, "controllers"))
        os.makedirs(os.path.join(project_path, "tests"))
        os.makedirs(os.path.join(project_path, "entity"))
        os.makedirs(os.path.join(project_path, "repository"))
        os.makedirs(os.path.join(project_path, "security"))
        # Create templates directory
        os.makedirs(os.path.join(".", "templates"))
        # Create public directory
        os.makedirs(os.path.join(".", "public"))

        # Create config directory
        os.makedirs(os.path.join(".", "config"))
        # Create var directory
        os.makedirs(os.path.join(".", "var"))
        os.makedirs(os.path.join("./var", "log"))
        os.makedirs(os.path.join("./var", "session"))
        # Create migrations directory
        os.makedirs(os.path.join(".", "migrations"))
        os.makedirs(os.path.join("./migrations", "versions"))
        os.makedirs(os.path.join("./migrations", "versions", "__pycache__"))
        # Create usefull files
        # main.py
        FileCreator().create_file(
            template="init_files/main.jinja2",
            path=".",
            name="main",
            data={},
        )
        # .env
        FileCreator().create_file(
            template="init_files/env.jinja2",
            path=".",
            name=".env",
            data={"session_secret_key": InitCommand.generate_secret_key()},
            format="env",
        )
        # base.html
        FileCreator().create_file(
            template="init_files/base.jinja2",
            path="./templates",
            name="base.html",
            data={},
            format="html",
        )
        # yaml files
        FileCreator().create_file(
            template="init_files/application.jinja2",
            path="./config",
            name="application.yaml",
            data={},
            format="yaml",
        )
        FileCreator().create_file(
            template="init_files/orm.jinja2",
            path="./config",
            name="orm.yaml",
            data={},
            format="yaml",
        )
        FileCreator().create_file(
            template="init_files/security.jinja2",
            path="./config",
            name="security.yaml",
            data={},
            format="yaml",
        )
        FileCreator().create_file(
            template="init_files/parameter.jinja2",
            path="./config",
            name="parameter.yaml",
            data={},
            format="yaml",
        )
        FileCreator().create_file(
            template="init_files/services.jinja2",
            path="./config",
            name="services.yaml",
            data={},
            format="yaml",
        )
        # env.py in migrations
        FileCreator().create_file(
            template="init_files/env.py.jinja2",
            path="./migrations",
            name="env",
            data={},
            format="py",
        )
        # env.py in migrations
        FileCreator().create_file(
            template="init_files/blank.jinja2",
            path="./migrations/versions/__pycache__",
            name=".gitkeep",
            data={},
            format="gitkeep",
        )
        # gitignore
        FileCreator().create_file(
            template="init_files/gitignore.jinja2",
            path=".",
            name=".gitignore",
            data={},
            format="gitignore",
        )

    def check_requirements(self):
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
            return True
        else:
            self.printer.print_full_text(
                "[bold red]✗ Your system does not meet all the required conditions[/bold red]",
                linebefore=True,
            )
            return False
