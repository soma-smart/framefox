import typer

from .commands.cache import add_cache_commands

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

        add_cache_commands(self.app)

    def run(self):
        """
        Run the application
        """
        self.app()