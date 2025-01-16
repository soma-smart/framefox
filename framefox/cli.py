import typer

from framefox.terminal.command_handler import CommandHandler


app = typer.Typer()

create_app = typer.Typer(
    help="Create various resources like entities or CRUD operations.")
orm_app = typer.Typer(
    help="ORM operations like creating or migrating databases.")

typers = {
    "main": app,
    "create": create_app,
    "orm": orm_app,
}

app.add_typer(create_app, name="create")
app.add_typer(orm_app, name="orm")


command_handler = CommandHandler()
command_handler.load_commands(typers)

# @create_app.command("entity")
# def create_entity():
#     """Create an entity"""
#     typer.echo("Creating an entity...")


# @create_app.command("crud")
# def create_crud():
#     """Create CRUD"""
#     typer.echo("Creating CRUD...")


# @app.command()
# def test():
#     """Run tests"""
#     typer.echo("Running tests...")


# @app.command()
# def test():
#     """Run tests"""
#     typer.echo("Running tests...")

# TODO : ajouter affichage de toutes les commandes disponibles sur un input de framefox


# @app.callback(invoke_without_command=True)
# def main(ctx: typer.Context):
#     print(ctx.invoked_subcommand)


if __name__ == "__main__":
    app()
