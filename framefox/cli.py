# from rich.text import Text
# from rich.panel import Panel
# from rich.table import Table
# from rich.console import Console
# import typer

# from framefox.terminal.command_handler import CommandHandler


# app = typer.Typer()

# create_app = typer.Typer(
#     help="Create various resources like entities or CRUD operations.")
# orm_app = typer.Typer(
#     help="ORM operations like creating or migrating databases.")

# typers = {
#     "main": app,
#     "create": create_app,
#     "orm": orm_app,
# }

# app.add_typer(create_app, name="create")
# app.add_typer(orm_app, name="orm")


# command_handler = CommandHandler()
# command_handler.load_commands(typers)

# # TODO : ajouter affichage de toutes les commandes disponibles sur un input de framefox


# # @app.callback(invoke_without_command=True)
# # def main(ctx: typer.Context):
# #     if ctx.invoked_subcommand is None:
# #         typer.echo("Available commands:")
# #         for typer_app in typers.values():
# #             for command in typer_app.registered_commands:
# #                 typer.echo(f"- {command.name}: \t {command.callback.__doc__}")


# @app.callback(invoke_without_command=True)
# def main(ctx: typer.Context):
#     if ctx.invoked_subcommand is None:
#         # Initialiser la console Rich
#         console = Console()

#         # Créer un tableau pour les commandes
#         table = Table(show_header=True, header_style="bold blue")
#         table.add_column("Commande", style="blue", no_wrap=True)
#         table.add_column("Description", style="white")

#         # Parcourir les typers et ajouter les commandes au tableau
#         for category, typer_app in typers.items():
#             for command in typer_app.registered_commands if hasattr(typer_app, 'registered_commands') else typer_app.commands.values():
#                 command_name = f"{category} {
#                     command.name}" if category != "main" else command.name
#                 command_help = command.callback.__doc__ or ""
#                 first_line = command_help.strip().split(
#                     "\n")[0] if command_help else ""
#                 table.add_row(command_name, first_line)

#         # # Créer un panel autour du tableau avec des bordures arrondies
#         # panel = Panel(table, title="Commandes Disponibles", border_style="blue", padding=(
#         #     1, 2), title_align="left", box="ROUND")

#         # # Afficher le panel
#         # console.print(panel)
#         console.print(table)

#         raise typer.Exit()


# if __name__ == "__main__":
#     app()


from framefox.terminal.terminal import Terminal

app = Terminal.run()

if __name__ == "__main__":
    app()
