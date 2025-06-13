import os
from typing import Any, Dict

from rich.console import Console as RichConsole

from framefox.terminal.ui.table_builder import TableBuilder
from framefox.terminal.ui.themes import FramefoxMessages, FramefoxTheme

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class DisplayManager:
    """Manages all CLI display operations"""

    def __init__(self):
        self.console = RichConsole()

    def print_header(self):
        """Print the application header"""
        self.console.print("")
        self.console.print(
            f"[{FramefoxTheme.HEADER_STYLE}]{FramefoxMessages.HEADER_TITLE}[/{FramefoxTheme.HEADER_STYLE}]",
            justify="left",
        )
        self.console.print(
            f"[{FramefoxTheme.DIM_STYLE}]{FramefoxMessages.HEADER_SUBTITLE}[/{FramefoxTheme.DIM_STYLE}]",
            justify="left",
        )
        self.console.print("")

    def display_help(self, command_groups: Dict[str, Dict[str, Any]]):
        """Display the main help screen"""
        project_exists = os.path.exists("src")

        if not project_exists:
            self._display_init_only_help(command_groups)
            return

        self._display_full_help(command_groups)

    def display_subgroup_help(self, namespace: str, commands: Dict[str, Any], description: str):
        """Display help for a specific command group"""
        self.console.print(f"[{FramefoxTheme.HEADER_STYLE}]{namespace.upper()} COMMANDS[/{FramefoxTheme.HEADER_STYLE}]")
        self.console.print("")
        self.console.print(description, style=FramefoxTheme.DIM_STYLE)
        self.console.print("")

        # Build commands table
        table = TableBuilder.create_commands_table()
        commands_data = []

        for command_name, command_class in sorted(commands.items()):
            doc = command_class.execute.__doc__ if hasattr(command_class, "execute") else ""
            first_line = doc.strip().split("\n")[0] if doc else ""
            commands_data.append((command_name, first_line))

        TableBuilder.populate_commands_table(table, commands_data)
        self.console.print(table)
        self.console.print("")
        self.console.print(
            f"Run 'framefox {namespace} COMMAND --help' for specific command details",
            style=FramefoxTheme.TEXT,
        )

    def display_all_commands(self, command_groups: Dict[str, Dict[str, Any]]):
        """Display all commands with their descriptions"""
        project_exists = os.path.exists("src")

        table = TableBuilder.create_commands_table()

        if not project_exists:
            # Only show init command
            init_commands = command_groups.get("main", {})
            if "init" in init_commands:
                doc = init_commands["init"].execute.__doc__ or ""
                first_line = doc.strip().split("\n")[0] if doc else ""
                table.add_row("init", first_line)
        else:
            # Show all commands grouped by namespace
            commands_data = []

            # First display commands from the "main" namespace (without group prefix)
            main_commands = command_groups.get("main", {})
            for command_name, command_class in sorted(main_commands.items()):
                if command_name != "init":
                    doc = command_class.execute.__doc__ if hasattr(command_class, "execute") else ""
                    first_line = doc.strip().split("\n")[0] if doc else ""
                    commands_data.append((command_name, first_line))

            # Then display the other namespaces with their prefixes
            for namespace, commands in sorted(command_groups.items()):
                if namespace != "main":
                    # Add section separator
                    commands_data.append(("", ""))

                    for command_name, command_class in sorted(commands.items()):
                        full_command = f"{namespace} {command_name}"
                        doc = command_class.execute.__doc__ if hasattr(command_class, "execute") else ""
                        first_line = doc.strip().split("\n")[0] if doc else ""
                        commands_data.append((full_command, first_line))

            TableBuilder.populate_commands_table(table, commands_data)

        self.console.print(table)
        self.console.print("")

    def _display_init_only_help(self, command_groups: Dict[str, Dict[str, Any]]):
        """Display help when only init command is available"""
        table = TableBuilder.create_commands_table()

        init_commands = command_groups.get("main", {})
        if "init" in init_commands:
            doc = init_commands["init"].execute.__doc__ or ""
            first_line = doc.strip().split("\n")[0] if doc else ""
            table.add_row("init", first_line)

        self.console.print(table)
        self.console.print("")
        self.console.print(FramefoxMessages.HELP_INIT_DETAILS, style=FramefoxTheme.TEXT)

    def _display_full_help(self, command_groups: Dict[str, Dict[str, Any]]):
        """Display full help when project exists"""
        # Options table
        options_table = TableBuilder.create_options_table()
        options_data = [
            ("--install-completion", "Install completion for the current shell"),
            ("--show-completion", "Show completion for the current shell"),
            ("-a, --all, list", "Show detailed list of all commands"),
            ("-h, -help", "Show command help message"),
        ]
        TableBuilder.populate_options_table(options_table, options_data)
        self.console.print(options_table)
        self.console.print("")

        # Command groups table
        groups_table = TableBuilder.create_groups_table()
        groups_data = []

        for namespace in sorted(command_groups.keys()):
            if namespace != "main":
                description = self._get_namespace_description(namespace)
                groups_data.append((namespace, description))

        TableBuilder.populate_options_table(groups_table, groups_data)
        self.console.print(groups_table)
        self.console.print("")

        # Help messages
        self.console.print(FramefoxMessages.HELP_COMMAND_DETAILS, style=FramefoxTheme.TEXT)
        self.console.print("")
        self.console.print(FramefoxMessages.HELP_EXAMPLE, style=FramefoxTheme.DIM_STYLE)

    def _get_namespace_description(self, namespace: str) -> str:
        """Get description for a namespace"""
        return FramefoxMessages.NAMESPACE_DESCRIPTIONS.get(namespace, f"{namespace.title()} operations")

    def print_error(self, message: str):
        """Print an error message"""
        self.console.print(message, style=FramefoxTheme.ERROR)

    def print_success(self, message: str):
        """Print a success message"""
        self.console.print(message, style=FramefoxTheme.SUCCESS)
