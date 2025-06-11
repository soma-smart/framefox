import os
import platform
import secrets
import shutil
import sys
from importlib.metadata import version

from rich.console import Console
from rich.table import Table

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.input_manager import InputManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen & LEUROND Raphael
Github: https://github.com/RayenBou
Github: https://github.com/Vasulvius
"""


MIN_PYTHON_VERSION = (3, 12)
MIN_DISK_SPACE = 100 * 1024 * 1024

# Project structure to create
PROJECT_DIRECTORIES = [
    "src",
    "src/controller",
    "src/tests",
    "src/entity",
    "src/repository",
    "src/security",
    "templates",
    "public",
    "config",
    "var",
    "var/log",
    "var/session",
    "migrations",
    "migrations/versions",
    "migrations/versions/__pycache__",
]

PROJECT_FILES = [
    "main.py",
    ".env",
    "templates/base.html",
    "config/application.yaml",
    "config/orm.yaml",
    "config/security.yaml",
    "config/mail.yaml",
    "config/debug.yaml",
    "config/parameter.yaml",
    "config/services.yaml",
    "config/tasks.yaml",
    "migrations/env.py",
    "migrations/script.py.mako",
    "migrations/versions/__pycache__/.gitkeep",
    ".gitignore",
    "requirements.txt",
]


class InitCommand(AbstractCommand):
    """Command to initialize a new Framefox project"""
    def __init__(self):
        super().__init__("init")

    def execute(self):
        """Initialize a new Framefox project"""
        if not self._check_system_requirements():
            return

        existing_items = self._check_existing_project_structure()

        if existing_items and not self._handle_existing_files(existing_items):
            return

        self._create_project()
        self._display_success_message()

    def _check_existing_project_structure(self):
        """Check which project files and directories already exist"""
        existing_items = []

        # Check directories
        for directory in PROJECT_DIRECTORIES:
            if os.path.exists(directory):
                existing_items.append(f"{directory}/ (directory)")

        # Check files
        for file in PROJECT_FILES:
            if os.path.exists(file):
                existing_items.append(f"{file} (file)")

        return existing_items

    def _handle_existing_files(self, existing_items):
        """Handle conflicts with existing files"""
        self._display_existing_files_warning(existing_items)

        choice = InputManager().wait_input("Your choice", choices=["1", "2"], default="1")

        if choice == "1":
            self.printer.print_msg(
                "Initialization cancelled.",
                theme="info",
                linebefore=True,
                newline=True,
            )
            return False

        self.printer.print_msg(
            "Overwriting existing files...",
            theme="warning",
            linebefore=True,
        )
        return True

    def _display_existing_files_warning(self, existing_items):
        """Display warning for existing files"""
        self.printer.print_msg(
            "The following files/directories already exist:",
            theme="warning",
            linebefore=True,
        )

        for item in existing_items:
            self.printer.print_msg(f"• {item}", theme="warning")

        print("")
        self.printer.print_msg("What do you want to do?", theme="bold_normal")
        self.printer.print_msg("1. Cancel initialization", theme="normal")
        self.printer.print_msg("2. Overwrite existing files/directories", theme="normal")

    def _create_project(self):
        """Create the complete project structure"""
        self._create_directories()
        self._create_files()

    def _create_directories(self):
        """Create all project directories"""
        for directory in PROJECT_DIRECTORIES:
            os.makedirs(directory, exist_ok=True)

    def _create_files(self):
        """Create all project files"""
        files_config = self._get_files_configuration()

        for file_config in files_config:
            FileCreator().create_file(**file_config)

    def _get_files_configuration(self):
        """Return the configuration of all files to create"""
        return [
            # Main file
            {
                "template": "init_files/main.jinja2",
                "path": ".",
                "name": "main",
                "data": {},
            },
            # Environment file
            {
                "template": "init_files/env.jinja2",
                "path": ".",
                "name": ".env",
                "data": {"session_secret_key": self._generate_secret_key()},
                "format": "env",
            },
            # Base HTML template
            {
                "template": "init_files/base.jinja2",
                "path": "./templates",
                "name": "base.html",
                "data": {},
                "format": "html",
            },
            # YAML configuration files
            *self._get_yaml_config_files(),
            # Migration files
            *self._get_migration_files(),
            # Miscellaneous files
            *self._get_misc_files(),
        ]

    def _get_yaml_config_files(self):
        """Return the configuration for YAML files"""
        yaml_files = ["application", "orm", "security", "mail", "debug", "parameter", "services", "tasks"]

        return [
            {
                "template": f"init_files/{name}.jinja2",
                "path": "./config",
                "name": f"{name}.yaml",
                "data": {},
                "format": "yaml",
            }
            for name in yaml_files
        ]

    def _get_migration_files(self):
        """Return the configuration for migration files"""
        return [
            {
                "template": "init_files/env.py.jinja2",
                "path": "./migrations",
                "name": "env",
                "data": {},
                "format": "py",
            },
            {
                "template": "init_files/script.py.mako",
                "path": "./migrations",
                "name": "script.py.mako",
                "data": {},
                "format": "py.mako",
            },
            {
                "template": "init_files/blank.jinja2",
                "path": "./migrations/versions/__pycache__",
                "name": ".gitkeep",
                "data": {},
                "format": "gitkeep",
            },
        ]

    def _get_misc_files(self):
        """Return the configuration for miscellaneous files"""
        return [
            {
                "template": "init_files/gitignore.jinja2",
                "path": ".",
                "name": ".gitignore",
                "data": {},
                "format": "gitignore",
            },
            {
                "template": "init_files/requirements.jinja2",
                "path": ".",
                "name": "requirements.txt",
                "data": {"framefox_version": version("framefox")},
                "format": "txt",
            },
        ]

    def _display_success_message(self):
        """Display success message"""
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
    def _generate_secret_key():
        """Generate a random secret key of 32 bytes encoded in base64"""
        return secrets.token_urlsafe(32)

    def _check_system_requirements(self):
        """Check if the system meets the requirements to run Framefox"""
        console = Console()
        print("")

        table = self._build_requirements_table()
        console.print(table)
        print("")

        requirements_met = self._evaluate_requirements()
        self._display_requirements_result(requirements_met)

        return requirements_met

    def _build_requirements_table(self):
        """Build the system requirements table"""
        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Component", style="bold orange3")
        table.add_column("Status", style="white")
        table.add_column("Required", style="white")
        table.add_column("Current", style="white")

        # Python version check
        python_version = sys.version_info
        python_ok = python_version >= MIN_PYTHON_VERSION
        table.add_row(
            "Python Version",
            "[green]OK[/green]" if python_ok else "[red]Error[/red]",
            f"Python {'.'.join(map(str, MIN_PYTHON_VERSION))}+",
            f"Python {'.'.join(map(str, python_version[:3]))}",
        )

        # Operating system check
        os_name = platform.system()
        os_ok = os_name in ["Linux", "Darwin", "Windows", "MacOS"]
        table.add_row(
            "Operating System",
            "[green]OK[/green]" if os_ok else "[red]Not Supported[/red]",
            "Win/Linux/MacOS",
            os_name,
        )

        # Permissions check
        home = os.path.expanduser("~")
        can_write = os.access(home, os.W_OK)
        table.add_row(
            "User Permissions",
            "[green]OK[/green]" if can_write else "[red]Error[/red]",
            "Write in home",
            "OK" if can_write else "Denied",
        )

        # Disk space check
        _, _, free = shutil.disk_usage(home)
        space_ok = free > MIN_DISK_SPACE
        table.add_row(
            "Disk Space",
            "[green]OK[/green]" if space_ok else "[red]Insufficient[/red]",
            "100 MB minimum",
            f"{free // (1024 * 1024)} MB available",
        )

        return table

    def _evaluate_requirements(self):
        """Evaluate if all requirements are satisfied"""
        python_version = sys.version_info
        python_ok = python_version >= MIN_PYTHON_VERSION

        os_name = platform.system()
        os_ok = os_name in ["Linux", "Darwin", "Windows", "MacOS"]

        home = os.path.expanduser("~")
        can_write = os.access(home, os.W_OK)

        _, _, free = shutil.disk_usage(home)
        space_ok = free > MIN_DISK_SPACE

        return python_ok and os_ok and can_write and space_ok

    def _display_requirements_result(self, requirements_met):
        """Display the result of requirements check"""
        if requirements_met:
            self.printer.print_full_text(
                "[bold orange1]✓ Your system is compatible with Framefox[/bold orange1]",
                linebefore=True,
            )
        else:
            self.printer.print_full_text(
                "[bold red]✗ Your system does not meet all the required conditions[/bold red]",
                linebefore=True,
            )

    # Static method kept for compatibility (if used elsewhere)
    @staticmethod
    def create_empty_project():
        """Static method kept for compatibility - delegates to an instance"""
        command = InitCommand()
        command._create_project()

    @staticmethod
    def generate_secret_key():
        """Static method kept for compatibility"""
        return InitCommand._generate_secret_key()
