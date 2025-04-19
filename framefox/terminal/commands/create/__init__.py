from typer import Typer

from .create_auth_command import CreateAuthCommand
from .create_controller_command import CreateControllerCommand
from .create_crud_command import CreateCrudCommand
from .create_entity_command import CreateEntityCommand
from .create_hash_command import CreateHashCommand
from .create_register_command import CreateRegisterCommand
from .create_user_command import CreateUserCommand


def add_create_commands(app: Typer) -> None:
    create_commands = Typer()

    @create_commands.command()
    def auth(*args, **kwargs):
        CreateAuthCommand().execute(*args, **kwargs)

    @create_commands.command()
    def controller(*args, **kwargs):
        CreateControllerCommand().execute(*args, **kwargs)

    @create_commands.command()
    def crud(*args, **kwargs):
        CreateCrudCommand().execute(*args, **kwargs)

    @create_commands.command()
    def entity(*args, **kwargs):
        CreateEntityCommand().execute(*args, **kwargs)

    @create_commands.command()
    def hash(*args, **kwargs):
        CreateHashCommand().execute(*args, **kwargs)

    @create_commands.command()
    def register(*args, **kwargs):
        CreateRegisterCommand().execute(*args, **kwargs)

    @create_commands.command()
    def user(*args, **kwargs):
        CreateUserCommand().execute(*args, **kwargs)

    app.add_typer(
        create_commands,
        name="create",
        help="Create management commands",
    )