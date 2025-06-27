from typing import List, Tuple

from rich.table import Table

from framefox.terminal.ui.themes import FramefoxTheme

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class TableBuilder:
    """Builder for creating styled tables"""

    @staticmethod
    def create_basic_table(title: str = None) -> Table:
        """Create a basic table with Framefox styling"""
        table = Table(show_header=True, header_style=FramefoxTheme.TABLE_HEADER_STYLE)
        if title:
            table.title = title
        return table

    @staticmethod
    def create_commands_table() -> Table:
        """Create a table for displaying commands"""
        table = TableBuilder.create_basic_table()
        table.add_column("Command", style=FramefoxTheme.COMMAND_STYLE, no_wrap=True)
        table.add_column("Description", style=FramefoxTheme.DESCRIPTION_STYLE)
        return table

    @staticmethod
    def create_options_table() -> Table:
        """Create a table for displaying options"""
        table = TableBuilder.create_basic_table()
        table.add_column("Options", style=FramefoxTheme.COMMAND_STYLE, no_wrap=True)
        table.add_column("Description", style=FramefoxTheme.DESCRIPTION_STYLE)
        return table

    @staticmethod
    def create_groups_table() -> Table:
        """Create a table for displaying command groups"""
        table = TableBuilder.create_basic_table()
        table.add_column("Command Group", style=FramefoxTheme.COMMAND_STYLE, no_wrap=True)
        table.add_column("Description", style=FramefoxTheme.DESCRIPTION_STYLE)
        return table

    @staticmethod
    def populate_commands_table(table: Table, commands: List[Tuple[str, str]]):
        """Populate a commands table with data"""
        for command, description in commands:
            table.add_row(command, description)

    @staticmethod
    def populate_options_table(table: Table, options: List[Tuple[str, str]]):
        """Populate an options table with data"""
        for option, description in options:
            table.add_row(option, description)
