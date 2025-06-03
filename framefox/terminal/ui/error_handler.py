from typing import List

from rich.console import Console

from framefox.terminal.ui.themes import FramefoxTheme
from framefox.terminal.utils.text_utils import suggest_similar_commands

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class ErrorHandler:
    """Handles CLI errors and provides suggestions"""

    def __init__(self, console: Console):
        self.console = console

    def handle_unknown_command(
        self, command: str, available_commands: List[str]
    ) -> bool:
        """Handle unknown command and suggest alternatives"""
        suggestions = suggest_similar_commands(command, available_commands, threshold=3)

        if suggestions:
            self.console.print(
                f"[{FramefoxTheme.ERROR}]Unknown command: '{command}'[/{FramefoxTheme.ERROR}]"
            )
            self.console.print("")

            if len(suggestions) == 1:
                self.console.print(
                    f"Did you mean: [bold {FramefoxTheme.SECONDARY}]{suggestions[0]}[/bold {FramefoxTheme.SECONDARY}]?"
                )
            else:
                self.console.print("Did you mean one of these?")
                for suggestion in suggestions[:3]:  # Limit to top 3
                    self.console.print(
                        f"  • [bold {FramefoxTheme.SECONDARY}]{suggestion}[/bold {FramefoxTheme.SECONDARY}]"
                    )

            self.console.print("")
            self.console.print(
                "Run 'framefox --help' to see all available commands",
                style=FramefoxTheme.DIM_STYLE,
            )
            return True

        return False

    def handle_unknown_subcommand(
        self, group: str, subcommand: str, available_subcommands: List[str]
    ) -> bool:
        """Handle unknown subcommand within a group"""
        suggestions = suggest_similar_commands(
            subcommand, available_subcommands, threshold=3
        )

        if suggestions:
            self.console.print(
                f"[{FramefoxTheme.ERROR}]Unknown command: '{group} {subcommand}'[/{FramefoxTheme.ERROR}]"
            )
            self.console.print("")

            if len(suggestions) == 1:
                self.console.print(
                    f"Did you mean: [bold {FramefoxTheme.SECONDARY}]{group} {suggestions[0]}[/bold {FramefoxTheme.SECONDARY}]?"
                )
            else:
                self.console.print("Did you mean one of these?")
                for suggestion in suggestions[:3]:
                    self.console.print(
                        f"  • [bold {FramefoxTheme.SECONDARY}]{group} {suggestion}[/bold {FramefoxTheme.SECONDARY}]"
                    )

            self.console.print("")
            self.console.print(
                f"Run 'framefox {group} --help' to see available commands",
                style=FramefoxTheme.DIM_STYLE,
            )
            return True

        return False
