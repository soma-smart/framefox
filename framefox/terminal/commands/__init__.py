from typer import Typer

from .init_command import InitCommand


def add_init_commands(app: Typer) -> None:
    init_commands = Typer(
        no_args_is_help=True,
        rich_markup_mode="rich",
        pretty_exceptions_enable=False,
    )

    @init_commands.command(help="Initializes a new Framefox project")
    def init(*args, **kwargs):
        InitCommand().execute(*args, **kwargs)

    app.add_typer(
        init_commands,
        name="Init",
        help="Initializes a new Framefox project",
    )