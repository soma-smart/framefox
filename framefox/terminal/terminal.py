import typer
import os

from .commands import add_init_commands
from .commands.cache import add_cache_commands
from .commands.create import add_create_commands
from .commands.database import add_database_commands
from .commands.debug import add_debug_commands
from .commands.mock import add_mock_commands
from .commands.server import add_server_commands

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class Terminal:
    """
    Main application console
    """

    def __init__(self):
        self.app = typer.Typer(
            help="🦊 Framefox - Swift, smart, and a bit foxy",
            no_args_is_help=True,
            rich_markup_mode="rich",
            pretty_exceptions_enable=False,
        )

        if self.is_project_exists():
            add_cache_commands(self.app)
            add_create_commands(self.app)
            add_database_commands(self.app)
            add_debug_commands(self.app)
            add_mock_commands(self.app)
            add_server_commands(self.app)
        else:
            add_init_commands(self.app)

    def run(self):
        """
        Run the application
        """
        self.app()

    def is_project_exists(self):
        return os.path.exists("src")