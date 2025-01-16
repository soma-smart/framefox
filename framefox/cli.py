import typer
import difflib
import click
import sys

from framefox.terminal.command_handler import CommandHandler


# app = typer.Typer()
# CommandHandler().load_commands(app)


# app = typer.Typer()
# command_handler = CommandHandler()
# command_handler.load_commands(app)


# # Ajouter les commandes disponibles
# @app.command("hello:with:greeting")
# def greeting():
#     """Afficher un message de salutation avec un greeting."""
#     # typer.echo("Bonjour avec salutation !")
#     print("Bonjour avec salutation !")


# @app.command("hello:with:pleasure")
# def pleasure():
#     """Afficher un message de salutation avec plaisir."""
#     # typer.echo("Bonjour avec plaisir !")
#     print("Bonjour avec plaisir !")


# @app.command("test")
# def test():
#     """Afficher un message de salutation avec plaisir."""
#     # typer.echo("test")
#     print("test")

# Callback pour les suggestions

# def get_command_mapping(app: typer.Typer) -> dict:
#     """
#     Récupère un dictionnaire des commandes définies dans une instance Typer.
#     Clé : Nom de la commande
#     Valeur : Callable associé à la commande
#     """
#     command_mapping = {}
#     for command in app.registered_commands:
#         command_mapping[command.name] = command.callback
#     return command_mapping


# @app.callback(invoke_without_command=True)
# def main(ctx: typer.Context, command: str = typer.Argument(None, help="Commande partielle à rechercher")):
#     """
#     Gestion des suggestions pour les commandes partielles.
#     """
#     available_commands = get_command_mapping(app)
#     # print(command)
#     # breakpoint()

#     # Si une commande exacte a été invoquée, on laisse typer l'exécuter
#     if command in available_commands.keys():
#         ctx.invoke(available_commands[command])
#         # app(args=[command, *ctx.args])
#         raise typer.Exit()

#     # Si aucune commande n'est donnée
#     if command is None:
#         typer.echo("Erreur : Aucune commande fournie.")
#         typer.echo("Voici les commandes disponibles :")
#         for cmd in available_commands:
#             typer.echo(f"  - {cmd}")
#         raise typer.Exit()

#     # Proposer des suggestions basées sur l'entrée partielle
#     suggestions = [
#         cmd for cmd in available_commands if cmd.startswith(command)]
#     if suggestions:
#         typer.echo(f"Suggestions pour '{command}':")
#         for suggestion in suggestions:
#             typer.echo(f"  - {suggestion}")
#     else:
#         typer.echo(f"Aucune commande ne correspond à '{command}'.")
#         typer.echo("Essayez l'une des commandes suivantes :")
#         for cmd in available_commands:
#             typer.echo(f"  - {cmd}")
#     raise typer.Exit()


app = typer.Typer()

create_app = typer.Typer(
    help="Create various resources like entities or CRUD operations.")
app.add_typer(create_app, name="create")


@create_app.command("entity")
def create_entity():
    """Create an entity"""
    typer.echo("Creating an entity...")


@create_app.command("crud")
def create_crud():
    """Create CRUD"""
    typer.echo("Creating CRUD...")


@app.command()
def test():
    """Run tests"""
    typer.echo("Running tests...")


@app.command()
def test():
    """Run tests"""
    typer.echo("Running tests...")

# TODO : ajouter affichage de toutes les commandes disponibles sur un input de framefox


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    print(ctx.invoked_subcommand)


if __name__ == "__main__":
    app()
