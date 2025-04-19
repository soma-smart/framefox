from typer import Typer

from .init_command import InitCommand


def add_init_commands(app: Typer) -> None:
    @app.command()
    def init():
        """
        Initializes a new Framefox project
        """
        InitCommand().execute()

