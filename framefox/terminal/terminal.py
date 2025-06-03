import os
import sys
from typing import List

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
            name="Framefox",
            help="🦊 Framefox - Swift, smart, and a bit foxy",
            no_args_is_help=False,
            rich_markup_mode="rich",
            pretty_exceptions_enable=False,
            add_completion=True,
        )

        self.registry.discover_commands()
        self._configure_app()

    def _configure_app(self):
        """Configure the main application with subcommands"""

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

        # Commande 'list' manuelle
        @self.app.command("list")
        def list_commands():
            """List all available commands"""
            self._print_header()
            self._display_all_commands()

        # Commande 'init' spéciale (pas dans un groupe)
        if self.registry.get_command("init"):

            @self.app.command("init")
            def init():
                """Initialize a new Framefox project"""
                command_class = self.registry.get_command("init")
                instance = self._instantiate_command(command_class)
                if instance:
                    return instance.execute()

        # Créer les groupes de sous-commandes
        self._create_command_groups()

    def _create_command_groups(self):
        """Create Typer subcommand groups"""
        command_groups = self.registry.get_command_groups()

        for namespace, commands in command_groups.items():
            if namespace == "main":
                continue  # Skip main namespace (already handled)

            # Créer un sous-groupe pour chaque namespace
            subapp = typer.Typer(
                name=namespace,
                help=self._get_namespace_description(namespace),
                no_args_is_help=False,
            )

            def create_subgroup_callback(ns=namespace):
                @subapp.callback(invoke_without_command=True)
                def subgroup_main(ctx: typer.Context):
                    if ctx.invoked_subcommand is None:
                        self._print_header()
                        self._display_subgroup_help(ns)
                        raise typer.Exit()

                return subgroup_main

            create_subgroup_callback()

            # Ajouter chaque commande au sous-groupe
            for command_name, command_class in commands.items():
                self._add_command_to_subapp(subapp, command_name, command_class)

            # Ajouter le sous-groupe à l'app principale
            self.app.add_typer(subapp, name=namespace)

    def _display_subgroup_help(self, namespace: str):
        """Display help for a specific command group"""
        self.rich_console.print(
            f"[bold orange1]{namespace.upper()} COMMANDS[/bold orange1]"
        )
        self.rich_console.print("")
        self.rich_console.print(
            self._get_namespace_description(namespace), style="dim white"
        )
        self.rich_console.print("")

        # Table des commandes du groupe
        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Command", style="bold orange3", no_wrap=True)
        table.add_column("Description", style="white")

        command_groups = self.registry.get_command_groups()
        if namespace in command_groups:
            for command_name, command_class in sorted(
                command_groups[namespace].items()
            ):
                doc = (
                    command_class.execute.__doc__
                    if hasattr(command_class, "execute")
                    else ""
                )
                first_line = doc.strip().split("\n")[0] if doc else ""
                table.add_row(command_name, first_line)

        self.rich_console.print(table)
        self.rich_console.print("")
        self.rich_console.print(
            f"Run 'framefox {namespace} COMMAND --help' for specific command details",
            style="bold white",
        )

    def _add_command_to_subapp(
        self, subapp: typer.Typer, command_name: str, command_class
    ):
        """Add a command to a Typer subapp"""

        def create_command_func(cmd_class):
            def command_func():
                instance = self._instantiate_command(cmd_class)
                if instance:
                    return instance.execute()
                return 1

            # Copier la docstring pour l'aide
            if hasattr(cmd_class, "execute") and cmd_class.execute.__doc__:
                command_func.__doc__ = cmd_class.execute.__doc__.strip()

            return command_func

        # Ajouter la commande au sous-app
        subapp.command(name=command_name)(create_command_func(command_class))

    def _get_namespace_description(self, namespace: str) -> str:
        """Get description for a namespace"""
        descriptions = {
            "server": "Server operations like starting or stopping the server.",
            "create": "Create various resources like entities or CRUD operations.",
            "database": "Database operations like creating or migrating databases.",
            "debug": "Debug operations like checking routes or testing security.",
            "cache": "Cache operations like clearing cache files and directories.",
            "mock": "Mock operations like generating or loading mock data.",
            "orm": "ORM operations for entity management.",
            "fixtures": "Fixture operations for test data management.",
        }
        return descriptions.get(namespace, f"{namespace.title()} operations")

    def run(self, args: List[str] = None):
        """Run the console application with the given arguments"""
        if args is None:
            args = sys.argv[1:]

        # Cas spécial pour 'init' sans projet
        if len(args) == 1 and args[0] == "init" and not os.path.exists("src"):
            command_class = self.registry.get_command("init")
            if command_class:
                try:
                    instance = self._instantiate_command(command_class)
                    if instance:
                        return instance.execute()
                except Exception as e:
                    self.rich_console.print(
                        f"Error executing command init: {e}", style="bold red"
                    )
                    return 1

        # Utiliser Typer pour le reste
        try:
            return self.app(args)
        except SystemExit as e:
            return e.code
        except Exception as e:
            self.rich_console.print(f"Unexpected error: {e}", style="bold red")
            return 1

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
        self.rich_console.print("")
        self.rich_console.print(
            "🦊 [bold orange1]Framefox Framework CLI[/bold orange1]", justify="left"
        )
        self.rich_console.print(
            "[dim]Swift, smart, and a bit foxy[/dim]", justify="left"
        )
        self.rich_console.print("")

    def _display_all_commands(self):
        """Display all commands with their descriptions"""
        project_exists = os.path.exists("src")

        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Commands", style="bold orange3", no_wrap=True)
        table.add_column("Description", style="white")

        if not project_exists:
            init_command = self.registry.get_command("init")
            if init_command:
                doc = init_command.execute.__doc__ or ""
                first_line = doc.strip().split("\n")[0] if doc else ""
                table.add_row("init", first_line)
            self.rich_console.print(table)
            return

        command_groups = self.registry.get_command_groups()

        for namespace, commands in sorted(command_groups.items()):
            if namespace != "main":
                # Section header
                table.add_row("", "")

                for command_name, command_class in sorted(commands.items()):
                    # ✅ CHANGEMENT : Utiliser des espaces au lieu de ':'
                    full_command = f"{namespace} {command_name}"
                    doc = (
                        command_class.execute.__doc__
                        if hasattr(command_class, "execute")
                        else ""
                    )
                    first_line = doc.strip().split("\n")[0] if doc else ""
                    table.add_row(full_command, first_line)

        self.rich_console.print(table)
        self.rich_console.print("")

    def _display_help(self):
        """Display simplified help"""
        project_exists = os.path.exists("src")

        if not project_exists:
            # Afficher uniquement la commande init
            init_table = Table(show_header=True, header_style="bold orange1")
            init_table.add_column("Command", style="bold orange3", no_wrap=True)
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

        # Afficher les options disponibles
        options_table = Table(show_header=True, header_style="bold orange1")
        options_table.add_column("Options", style="bold orange3", no_wrap=True)
        options_table.add_column("Description", style="white")
        options_table.add_row(
            "--install-completion", "Install completion for the current shell"
        )
        options_table.add_row(
            "--show-completion", "Show completion for the current shell"
        )
        options_table.add_row(
            "--all", "Display all available commands in detailed view"
        )
        options_table.add_row(
            "COMMAND --help", "Show help for a specific command group"
        )
        # options_table.add_row(
        #     "COMMAND SUBCOMMAND --help", "Show help for a specific command"
        # )
        options_table.add_row("list", "Show detailed list of all commands")

        self.rich_console.print(options_table)
        self.rich_console.print("")

        # Groupes de commandes
        commands_table = Table(show_header=True, header_style="bold orange1")
        commands_table.add_column("Command Group", style="bold orange3", no_wrap=True)
        commands_table.add_column("Description", style="white")

        command_groups = self.registry.get_command_groups()
        for namespace in sorted(command_groups.keys()):
            if namespace != "main":
                description = self._get_namespace_description(namespace)
                commands_table.add_row(namespace, description)

        self.rich_console.print(commands_table)
        self.rich_console.print("")
        # ✅ CHANGEMENT : Mettre à jour les instructions avec la nouvelle syntaxe
        self.rich_console.print(
            "Run 'framefox COMMAND --help' for specific command group details",
            style="bold white",
        )
        self.rich_console.print("")
        self.rich_console.print(
            "Example: 'framefox server start' or 'framefox create controller'",
            style="dim white",
        )

    def _display_namespace_commands(self, namespace: str):
        """Display the commands of a specific namespace"""
        # Title
        self.rich_console.print(f"[bold orange1]{namespace.upper()} COMMANDS[/]")
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
