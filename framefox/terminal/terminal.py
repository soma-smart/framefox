import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from framefox.terminal.command_handler import CommandHandler


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
        orm_app = typer.Typer(
            help="ORM operations like creating or migrating databases."
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
            help="mock operations like generating or loading mock."
        )

        typers = {
            "main": app,
            "create": create_app,
            "orm": orm_app,
            "debug": debug_app,
            "orm database": database_app,
            "server": server_app,
            "cache": cache_app,
            "mock": mock_app,
        }

        app.add_typer(create_app, name="create")
        app.add_typer(orm_app, name="orm")
        app.add_typer(server_app, name="server")
        orm_app.add_typer(database_app, name="database")
        app.add_typer(debug_app, name="debug")
        app.add_typer(cache_app, name="cache")
        app.add_typer(mock_app, name="mock")
        Terminal._typers = typers
        command_handler = CommandHandler()
        command_handler.load_commands(typers)

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
        ):
            """Framefox CLI - Swift, smart, and a bit foxy"""
            if help is not None or ctx.invoked_subcommand is None:
                Terminal.display_commands_table(Terminal._typers)
                raise typer.Exit()

        return app

    @staticmethod
    def run():
        """Point d'entrée principal de l'application CLI"""
        app = Terminal.create_typer_app()
        return app

    # @staticmethod
    # def run():
    #     app, typers = Terminal.create_typer_app()

    #     @app.callback(invoke_without_command=True)
    #     def main(
    #         ctx: typer.Context,
    #         help: bool = typer.Option(
    #             False, "--help", "-h",
    #             help="Show this message and exit.",
    #             is_eager=True,
    #             callback=lambda x: Terminal.display_commands_table(
    #                  typers) if x else None
    #         )
    #     ):
    #         """Framefox CLI - Swift, smart, and a bit foxy"""
    #         if ctx.invoked_subcommand is None:
    #             Terminal.display_commands_table(typers)
    #             raise typer.Exit()

    #     return app

    @staticmethod
    def display_commands_table(typers):
        console = Console()
        print("")
        console.print(
            ":fox_face: Framefox - Swift, smart, and a bit foxy",
            style="bold orange1",
        )
        print("")

        console.print(
            "Usage: framefox [COMMAND] [OPTIONS]", style="bold white")
        console.print("Try 'framefox --help' for more information",
                      style="bold white")
        print("")

        # Créer un tableau pour les commandes
        table = Table(show_header=True, header_style="bold orange1")
        table.add_column("Commands", style="bold orange3", no_wrap=True)
        table.add_column("Description", style="white")

        # Parcourir les typers et ajouter les commandes au tableau
        for category, typer_app in typers.items():
            for command in (
                typer_app.registered_commands
                if hasattr(typer_app, "registered_commands")
                else typer_app.commands.values()
            ):
                command_name = (
                    f"{category} {command.name}" if category != "main" else command.name
                )
                command_help = command.callback.__doc__ or ""
                first_line = command_help.strip().split(
                    "\n")[0] if command_help else ""
                table.add_row(command_name, first_line)

        console.print(table)
        print("")
