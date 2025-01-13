import typer
# from injectable import load_injection_container

from framefox.terminal.command_handler import CommandHandler

app = typer.Typer()


# @app.command()
# def say_hello(name: str, divers: int = 2):
#     """
#     Greet theuser with a welcome message.

#     Args:
#         name (str): The name of the person to greet.
#     """
#     print(f"Welcome {name}")


# @app.command()
# def init():
#     """
#     Print projet initialisé.
#     """
#     print("Project initialized")


# load_injection_container()
# Load commands from the commands directory
CommandHandler().load_commands(app)

if __name__ == "__main__":
    # load_commands(app, commands_path="framefox/terminal/commands")
    app()
