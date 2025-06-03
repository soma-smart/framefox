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

    def handle_unknown_command(
        self, command: str, available_commands: List[str]
    ) -> bool:
        """Handle unknown command and suggest alternatives"""
        from framefox.terminal.utils.text_utils import suggest_similar_commands

        suggestions = suggest_similar_commands(command, available_commands, threshold=3)

        if suggestions:
            # Afficher le header comme pour les autres commandes
            if self.display_manager:
                self.display_manager.print_header()

            # Message d'erreur principal
            self._print_error_header(f"Unknown command: '{command}'")

            # Créer un tableau de suggestions
            self._display_suggestions_table(suggestions, is_subcommand=False)

            return True

        return False

    def handle_unknown_subcommand(
        self, group: str, subcommand: str, available_subcommands: List[str]
    ) -> bool:
        """Handle unknown subcommand within a group"""
        from framefox.terminal.utils.text_utils import suggest_similar_commands

        suggestions = suggest_similar_commands(
            subcommand, available_subcommands, threshold=3
        )

        if suggestions:
            # Afficher le header comme pour les autres commandes
            if self.display_manager:
                self.display_manager.print_header()

            # Message d'erreur principal
            self._print_error_header(f"Unknown command: '{group} {subcommand}'")

            # Créer un tableau de suggestions avec le groupe
            formatted_suggestions = [f"{group} {cmd}" for cmd in suggestions]
            self._display_suggestions_table(
                formatted_suggestions, is_subcommand=True, group=group
            )
            return True

        return False

    def _print_error_header(self, error_message: str):
        """Print styled error header"""
        self.console.print("")
        self.console.print(
            f"[{FramefoxTheme.ERROR}]❌ {error_message}[/{FramefoxTheme.ERROR}]"
        )
        self.console.print("")

    def _display_suggestions_table(
        self, suggestions: List[str], is_subcommand: bool = False, group: str = None
    ):
        """Display suggestions in a styled table"""
        if len(suggestions) == 1:
            # Single suggestion - format spécial
            self.console.print(
                f"[{FramefoxTheme.HEADER_STYLE}]💡 DID YOU MEAN?[/{FramefoxTheme.HEADER_STYLE}]"
            )
            self.console.print("")

            table = TableBuilder.create_basic_table()
            table.add_column(
                "Suggested Command", style=FramefoxTheme.COMMAND_STYLE, no_wrap=True
            )
            table.add_column("Action", style=FramefoxTheme.DESCRIPTION_STYLE)

            suggestion = suggestions[0]
            action = "Run this command instead"
            table.add_row(f"framefox {suggestion}", action)

        else:
            # Multiple suggestions
            self.console.print(
                f"[{FramefoxTheme.HEADER_STYLE}]💡 SIMILAR COMMANDS[/{FramefoxTheme.HEADER_STYLE}]"
            )
            self.console.print("")

            table = TableBuilder.create_basic_table()
            table.add_column(
                "Suggested Commands", style=FramefoxTheme.COMMAND_STYLE, no_wrap=True
            )
            table.add_column("Type", style=FramefoxTheme.DESCRIPTION_STYLE)

            for suggestion in suggestions[:3]:  # Limit to top 3
                if is_subcommand and group:
                    command_type = f"{group.title()} command"
                else:
                    command_type = "Command group"
                table.add_row(f"framefox {suggestion}", command_type)

        self.console.print(table)
        self.console.print("")

    def handle_general_error(self, args: List[str]):
        """Handle general errors with styled display"""
        if self.display_manager:
            self.display_manager.print_header()

        self._print_error_header(f"Invalid command: {' '.join(args)}")

        # Table avec les commandes de base
        self.console.print(
            f"[{FramefoxTheme.HEADER_STYLE}]🚀 GETTING STARTED[/{FramefoxTheme.HEADER_STYLE}]"
        )
        self.console.print("")

        getting_started_table = TableBuilder.create_commands_table()
        starter_commands = [
            ("framefox --help", "Show all available command groups"),
            ("framefox list", "List all commands with descriptions"),
            ("framefox server start", "Start development server (example)"),
            ("framefox create controller", "Create a new controller (example)"),
        ]

        TableBuilder.populate_commands_table(getting_started_table, starter_commands)
        self.console.print(getting_started_table)
        self.console.print("")
