import sys
from typing import List, Optional
import os
import typer
from rich.console import Console as RichConsole
from rich.table import Table

from framefox.core.di.service_container import ServiceContainer
from framefox.terminal.command_registry import CommandRegistry

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
        self.registry = CommandRegistry()
        self.rich_console = RichConsole()
        self.app = typer.Typer(
            help="🦊 Framefox - Swift, smart, and a bit foxy",
            no_args_is_help=True,
            rich_markup_mode="rich",
            pretty_exceptions_enable=False,
        )

        self.registry.discover_commands()

        self._configure_app()

    def _configure_app(self):
        """Configure the main application"""

        @self.app.callback(invoke_without_command=True)
        def main(
            ctx: typer.Context,
            help: bool = typer.Option(None, "--help", "-h", is_eager=True),
            all: bool = typer.Option(False, "--all", "-a"),
        ):
            """Framefox CLI - Swift, smart, and a bit foxy"""
            if ctx.invoked_subcommand is None:
                self._print_header()
                if all:
                    self._display_all_commands()
                else:
                    self._display_help()
                raise typer.Exit()

        # Add a manual "list" command to list all commands
        @self.app.command("list")
        def list_commands():
            """List all available commands"""
            self._print_header()
            self._display_all_commands()

    def run(self, args: List[str] = None):
        """Run the console application with the given arguments"""
        if args is None:
            args = sys.argv[1:]

        if not args:
            self._create_standard_console()
            self._display_help()
            return 0

        # Ajout pour gérer spécifiquement la commande 'init'
        if len(args) == 1 and args[0] == "init":
            command_class = self.registry.get_command("init")
            if command_class:
                try:
                    # Instantiate and execute the command
                    instance = self._instantiate_command(command_class)
                    if instance:
                        print(f"Executing command init")
                        return instance.execute()
                    else:
                        self.rich_console.print(
                            f"Error instantiating command init",
                            style="bold red",
                        )
                        return 1
                except Exception as e:
                    self.rich_console.print(
                        f"Error executing command init: {e}",
                        style="bold red",
                    )
                    return 1

        if len(args) == 1 and ":" not in args[0] and args[0] != "list":
            namespace = args[0]
            commands_by_namespace = self.registry.list_commands()

            if namespace in commands_by_namespace:
                self._create_standard_console()
                self._display_namespace_commands(namespace)
                return 0

        # Check if we have a command with the format namespace:name
        if len(args) > 0 and ":" in args[0]:
            command_id = args[0]
            command_class = self.registry.get_command(command_id)
            if command_class:
                try:
                    # Instantiate and execute the command
                    instance = self._instantiate_command(command_class)
                    if instance:
                        print(f"Executing command {command_id}")
                        return instance.execute(*args[1:])
                    else:
                        self.rich_console.print(
                            f"Error instantiating command {command_id}",
                            style="bold red",
                        )
                        return 1
                except Exception as e:
                    self.rich_console.print(
                        f"Error executing command {command_id}: {e}",
                        style="bold red",
                    )
                    return 1
            else:
                self.rich_console.print(f"Command not found", style="bold red")

                # Calculate Levenshtein distance for all commands
                command_similarities = []
                for cmd in self.registry.commands.keys():
                    # Calculate the distance between the requested command and each available command
                    distance = self.levenshtein_distance(command_id, cmd)

                    # If the namespace is the same, give a bonus (reduce the distance)
                    if ":" in cmd and ":" in command_id:
                        if cmd.split(":")[0] == command_id.split(":")[0]:
                            distance -= 2

                    # Store the distance and the command
                    command_similarities.append((distance, cmd))

                # Sort by distance (smaller distance = more similar)
                command_similarities.sort()

                # Only suggest the most similar command if it has a reasonable distance
                if command_similarities and command_similarities[0][0] < 5:
                    best_match = command_similarities[0][1]
                    self.rich_console.print(
                        f"Did you mean [bold yellow]{best_match}[/] ?", style="yellow"
                    )

                return 1

        # Otherwise, use Typer normally
        try:
            return self.app()
        except SystemExit as e:
            # Intercept Typer's exit to return the status code
            return e.code

    def _instantiate_command(self, command_class):
        """Instantiate a command using the service container if necessary"""
        try:
            # First try to instantiate simply
            return command_class()
        except TypeError:
            # If it fails, it's probably because it needs dependencies
            try:
                # Use the container to resolve dependencies
                container = ServiceContainer()
                return container.get(command_class)
            except Exception as e:
                self.rich_console.print(
                    f"Error instantiating with the container: {e}",
                    style="bold red",
                )
                return None

    def _print_header(self):
        """Print the application header"""
        print("")
        self.rich_console.print(
            "🦊 Framefox - Swift, smart, and a bit foxy", style="bold orange1"
        )
        print("")

    def _create_standard_console(self, help=True):
        """Create a console with the standard Framefox style"""
        print("")
        self.rich_console.print(
            "🦊 Framefox - Swift, smart, and a bit foxy",
            style="bold orange1",
        )
        print("")
        self.rich_console.print(
            "Usage: framefox [namespace:command] [OPTIONS]", style="bold white"
        )
        if help:
            self.rich_console.print(
                "Try 'framefox list' for available commands", style="bold white"
            )
        print("")
        return self.rich_console

    def _display_all_commands(self):
        """Display all commands with their description in an enhanced style"""
        # Vérifier si le projet est initialisé
        project_exists = os.path.exists("src")

        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Commands", style="bold orange3", no_wrap=True)
        table.add_column("Description", style="white")

        if not project_exists:
            # Afficher uniquement la commande init
            init_command = self.registry.get_command("init")
            if init_command:
                doc = init_command.execute.__doc__ or ""
                first_line = doc.strip().split("\n")[0] if doc else ""
                table.add_row("init", first_line)

            self.rich_console.print(table)
            return

        commands_by_namespace = self.registry.list_commands()

        # For each namespace
        for namespace, commands in sorted(commands_by_namespace.items()):
            if namespace != "main":
                # Add an empty row and a section header
                if namespace != next(iter(sorted(commands_by_namespace))):
                    table.add_row("", "")
                table.add_row(f"{namespace.upper()}", "")

                # Add the commands of this namespace
                for name in sorted(commands):
                    command_id = f"{namespace}:{name}"
                    command_class = self.registry.get_command(command_id)
                    doc = command_class.execute.__doc__ or ""
                    first_line = doc.strip().split("\n")[0] if doc else ""
                    table.add_row(command_id, first_line)

        # Display the commands of the main namespace at the end
        if "main" in commands_by_namespace:
            table.add_row("", "")
            table.add_row(f"MAIN", "")
            for name in sorted(commands_by_namespace["main"]):
                command_class = self.registry.get_command(name)
                doc = command_class.execute.__doc__ or ""
                first_line = doc.strip().split("\n")[0] if doc else ""
                table.add_row(name, first_line)

        self.rich_console.print(table)
        print("")

    def _display_help(self):
        """Display simplified help in an enhanced style"""
        project_exists = os.path.exists("src")

        if not project_exists:
            # Afficher uniquement la commande init
            init_table = Table(show_header=True, header_style="bold orange1")
            init_table.add_column(
                "Command", style="bold orange3", no_wrap=True)
            init_table.add_column("Description", style="white")

            init_command = self.registry.get_command("init")
            if init_command:
                doc = init_command.execute.__doc__ or ""
                first_line = doc.strip().split("\n")[0] if doc else ""
                init_table.add_row("init", first_line)

            self.rich_console.print(init_table)
            self.rich_console.print("")
            self.rich_console.print(
                "Run 'framefox init --help' for command details",
                style="bold white",
            )
            return
        options_table = Table(show_header=True, header_style="bold orange1")
        options_table.add_column("Options", style="bold orange3", no_wrap=True)
        options_table.add_column("Description", style="white")
        options_table.add_row(
            "--all", "Display all available commands in detailed view"
        )
        options_table.add_row("namespace:command",
                              "Execute a specific command")
        options_table.add_row("list", "Show detailed list of all commands")

        self.rich_console.print(options_table)
        self.rich_console.print("")

        # Command panel - display namespaces
        commands_table = Table(show_header=True, header_style="bold orange1")
        commands_table.add_column(
            "Namespace", style="bold orange3", no_wrap=True)
        commands_table.add_column("Description", style="white")

        namespace_descriptions = {
            "server": "Server operations like starting or stopping the server.",
            "create": "Create various resources like entities or CRUD operations.",
            "database": "Database operations like creating or migrating databases.",
            "debug": "Debug operations like checking routes or testing security.",
            "cache": "Cache operations like clearing cache files and directories.",
            "mock": "Mock operations like generating or loading mock data.",
        }

        commands_by_namespace = self.registry.list_commands()

        # Display only the namespaces that have commands
        for namespace in sorted(commands_by_namespace.keys()):
            if namespace != "main":
                description = namespace_descriptions.get(namespace, "")
                commands_table.add_row(namespace, description)

        self.rich_console.print(commands_table)
        self.rich_console.print("")
        self.rich_console.print(
            "Run 'framefox namespace:command --help' for specific command details",
            style="bold white",
        )

    def _display_namespace_commands(self, namespace: str):
        """Display the commands of a specific namespace"""
        # Title
        self.rich_console.print(
            f"[bold orange1]{namespace.upper()} COMMANDS[/]")
        self.rich_console.print("")

        # Table
        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Command", style="bold orange3", no_wrap=True)
        table.add_column("Description", style="white")

        commands_by_namespace = self.registry.list_commands()
        if namespace in commands_by_namespace:
            for name in sorted(commands_by_namespace[namespace]):
                command_id = f"{namespace}:{name}"
                command_class = self.registry.get_command(command_id)
                doc = command_class.execute.__doc__ or ""
                first_line = doc.strip().split("\n")[0] if doc else ""
                table.add_row(command_id, first_line)

        self.rich_console.print(table)

        # Final instructions
        self.rich_console.print("")
        self.rich_console.print(
            f"Run 'framefox {namespace}:COMMAND --help' for specific command details"
        )

    def levenshtein_distance(self, s1, s2):
        """
        Calculate the Levenshtein distance between two strings.
        This function determines the minimum number of operations (insertion, deletion, substitution)
        needed to transform one string into another.
        """
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]
