import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from framefox.terminal.command_handler import CommandHandler

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


class Terminal:
    _typers = None

    @staticmethod
    def create_typer_app():
        app = typer.Typer(
            help="Framefox CLI",
            no_args_is_help=False,
            rich_markup_mode="rich",
            pretty_exceptions_enable=False,
        )
        create_app = typer.Typer(
            help="Create various resources like entities or CRUD operations."
        )
        database_app = typer.Typer(
            help="Database operations like creating or migrating databases."
        )
        server_app = typer.Typer(
            help="Server operations like starting or stopping the server."
        )
        debug_app = typer.Typer(
            help="Debug operations like checking routes or testing security."
        )
        cache_app = typer.Typer(
            help="Cache operations like clearing cache files and directories."
        )
        mock_app = typer.Typer(
            help="mock operations like generating or loading mock.")

        typers = {
            "main": app,
            "create": create_app,
            "database": database_app,
            "debug": debug_app,
            "server": server_app,
            "cache": cache_app,
            "mock": mock_app,
        }

        app.add_typer(create_app, name="create")
        app.add_typer(database_app, name="database")
        app.add_typer(server_app, name="server")
        app.add_typer(debug_app, name="debug")
        app.add_typer(cache_app, name="cache")
        app.add_typer(mock_app, name="mock")
        Terminal._typers = typers
        command_handler = CommandHandler()
        command_handler.load_commands(typers)

        # TODO : framefox --help = framefox = tableau réduit
        # TODO : framefox --all = toutes les commandes
        # TODO : framefox create = afficher toutes les commandes de create

        @app.callback(invoke_without_command=True)
        def main(
            ctx: typer.Context,
            help: bool = typer.Option(
                None,
                "--help",
                "-h",
                is_eager=True,
                help="Show this message and exit.",
            ),
            all: bool = typer.Option(
                False,
                "--all",
                '-a',
                help="Display all available commands in detailed view",
            ),
        ):
            """Framefox CLI - Swift, smart, and a bit foxy"""
            if ctx.invoked_subcommand is None:
                if all:
                    Terminal._display_all_commands_table(Terminal._typers)
                elif help:
                    Terminal._display_simplified_view()
                else:
                    Terminal._display_simplified_view()
            # if help is not None or ctx.invoked_subcommand is None:
            #     Terminal._display_all_commands_table(Terminal._typers)
            #     raise typer.Exit()

        return app

    @staticmethod
    def run():
        """Point d'entrée principal de l'application CLI"""
        app = Terminal.create_typer_app()
        return app

    @staticmethod
    def _display_all_commands_table(typers):
        console = Terminal._create_standard_console()

        # Créer un tableau pour les commandes
        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Commands", style="bold orange3", no_wrap=True)
        table.add_column("Description", style="white")

        for category, typer_app in typers.items():

            command_list = typer_app.registered_commands if hasattr(
                typer_app, "registered_commands") else typer_app.commands.values()

            if category != "main" and category != "create" and len(command_list) > 0:
                # TODO : mettre des jolis titre
                # table.add_row("=============================", "")
                # table.add_row(category.upper(), "")
                table.add_row("", "")

            for command in command_list:
                command_name = (
                    f"{category} {command.name}" if category != "main" else command.name
                )
                command_help = command.callback.__doc__ or ""
                first_line = command_help.strip().split(
                    "\n")[0] if command_help else ""
                table.add_row(command_name, first_line)

        console.print(table)
        print("")

    @staticmethod
    def _display_simplified_view():
        console = Terminal._create_standard_console(False)

        # Panel des options
        options_table = Table(show_header=True, header_style="bold orange1")
        options_table.add_column("Options", style="bold orange3", no_wrap=True)
        options_table.add_column("Description", style="white")
        options_table.add_row(
            "--all", "Display all available commands in detailed view")
        options_table.add_row("--install-completion",
                              "Install completion for the current shell.")
        options_table.add_row(
            "--show-completion", "Show completion for the current shell, to copy it or customize the installation.")
        options_table.add_row("--help", "Show this message and exit.")

        console.print(options_table)
        console.print("")

        # Panel des commandes
        commands_table = Table(show_header=True, header_style="bold orange1")
        commands_table.add_column(
            "Commands", style="bold orange3", no_wrap=True)
        commands_table.add_column("Description", style="white")

        # Liste des commandes principales
        groups = {
            "create": "Create various resources like entities or CRUD operations.",
            "database": "Database management commands",
            "debug": "Debug and development tools",
            "server": "Server management commands",
            "cache": "Cache management",
            "mock": "Mock data management"
        }

        for group, description in groups.items():
            commands_table.add_row(group, description)

        console.print(commands_table)

    @staticmethod
    def _create_standard_console(help=True):
        console = Console()
        print("")
        console.print(
            ":fox_face: Framefox - Swift, smart, and a bit foxy",
            style="bold orange1",
        )
        print("")
        console.print(
            "Usage: framefox [COMMAND] [OPTIONS]", style="bold white")
        if help:
            console.print("Try 'framefox --help' for more information",
                          style="bold white")
        print("")
        return console
