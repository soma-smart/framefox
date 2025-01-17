from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
import typer

from framefox.terminal.command_handler import CommandHandler


class Terminal:

    @staticmethod
    def create_typer_app():
        app = typer.Typer()
        create_app = typer.Typer(
            help="Create various resources like entities or CRUD operations.")
        orm_app = typer.Typer(
            help="ORM operations like creating or migrating databases.")
        typers = {
            "main": app,
            "create": create_app,
            "orm": orm_app
        }

        app.add_typer(create_app, name="create")
        app.add_typer(orm_app, name="orm")

        command_handler = CommandHandler()
        command_handler.load_commands(typers)

        return app, typers

    @staticmethod
    def run():

        app, typers = Terminal.create_typer_app()

        @app.callback(invoke_without_command=True)
        def main(ctx: typer.Context):
            if ctx.invoked_subcommand is None:
                print(ctx.get_help())
                # Initialiser la console Rich
                console = Console()

                # Créer un tableau pour les commandes
                table = Table(show_header=True, header_style="bold blue")
                table.add_column("Commands", style="blue", no_wrap=True)
                table.add_column("Description", style="white")

                # Parcourir les typers et ajouter les commandes au tableau
                for category, typer_app in typers.items():
                    for command in typer_app.registered_commands if hasattr(typer_app, 'registered_commands') else typer_app.commands.values():
                        command_name = f"{category} {
                            command.name}" if category != "main" else command.name
                        command_help = command.callback.__doc__ or ""
                        first_line = command_help.strip().split(
                            "\n")[0] if command_help else ""
                        table.add_row(command_name, first_line)

                # # Créer un panel autour du tableau avec des bordures arrondies
                # panel = Panel(table, title="Commandes Disponibles", border_style="blue", padding=(
                #     1, 2), title_align="left", box="ROUND")

                # # Afficher le panel
                # console.print(panel)
                console.print(table)

                raise typer.Exit()
        return app
