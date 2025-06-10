from typing import List

from rich.console import Console

from framefox.terminal.ui.table_builder import TableBuilder
from framefox.terminal.ui.themes import FramefoxTheme

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class ErrorHandler:
    """Handles CLI errors and provides suggestions"""

    def __init__(self, console: Console, display_manager=None):
        self.console = console
        self.display_manager = display_manager

    def handle_unknown_command(self, command: str, available_commands: List[str]) -> bool:
        """Handle unknown command and suggest alternatives"""
        from framefox.terminal.utils.text_utils import suggest_similar_commands

        suggestions = suggest_similar_commands(command, available_commands, threshold=3)

        if suggestions:
            # Main error message
            self._print_error_header(f"Unknown command: '{command}'")

            # Display only the best suggestion
            self._display_single_suggestion(suggestions[0])

            return True

        return False

    def handle_unknown_subcommand(self, group: str, subcommand: str, available_subcommands: List[str]) -> bool:
        """Handle unknown subcommand within a group"""
        from framefox.terminal.utils.text_utils import suggest_similar_commands

        suggestions = suggest_similar_commands(subcommand, available_subcommands, threshold=3)

        if suggestions:
            # Main error message
            self._print_error_header(f"Unknown command: '{group} {subcommand}'")

            # Display only the best suggestion with group prefix
            self._display_single_suggestion(f"{group} {suggestions[0]}")

            return True

        return False

    def _print_error_header(self, error_message: str):
        """Print styled error header"""
        self.console.print("")
        self.console.print(f"[{FramefoxTheme.ERROR}]❌ {error_message}[/{FramefoxTheme.ERROR}]")
        self.console.print("")

    def _display_single_suggestion(self, suggestion: str):
        """Display a single suggestion without table"""
        msg = (
            f"[{FramefoxTheme.HEADER_STYLE}]💡 Did you mean:[/{FramefoxTheme.HEADER_STYLE}] "
            f"[{FramefoxTheme.TEXT}]framefox {suggestion}[/{FramefoxTheme.TEXT}]"
        )
        self.console.print(msg)
        self.console.print("")

    def handle_general_error(self, args: List[str]):
        """Handle general errors with styled display"""
        self._print_error_header(f"Invalid command: {' '.join(args)}")

        # Table with basic commands
        self.console.print(f"[{FramefoxTheme.HEADER_STYLE}]🚀 GETTING STARTED[/{FramefoxTheme.HEADER_STYLE}]")
        self.console.print("")

        getting_started_table = TableBuilder.create_commands_table()
        starter_commands = [
            ("framefox --help", "Show all available command groups"),
            ("framefox list", "List all commands with descriptions"),
            ("framefox server start", "Start development server"),
            ("framefox create controller", "Create a new controller"),
        ]

        TableBuilder.populate_commands_table(getting_started_table, starter_commands)
        self.console.print(getting_started_table)
        self.console.print("")
