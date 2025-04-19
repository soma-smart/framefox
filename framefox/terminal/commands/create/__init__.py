from typer import Typer

from .create_auth_command import CreateAuthCommand
from .create_controller_command import CreateControllerCommand
from .create_crud_command import CreateCrudCommand
from .create_entity_command import CreateEntityCommand
from .create_hash_command import CreateHashCommand
from .create_register_command import CreateRegisterCommand
from .create_user_command import CreateUserCommand


def add_create_commands(app: Typer) -> None:
    create_commands = Typer(
        no_args_is_help=True,
        rich_markup_mode="rich",
        pretty_exceptions_enable=False,
    )

    @create_commands.command()
    def auth():
        CreateAuthCommand().execute()

    @create_commands.command()
    def controller(name: str | None):
        CreateControllerCommand().execute(name)

    @create_commands.command()
    def crud(entity_name: str | None):
        CreateCrudCommand().execute(entity_name)

    @create_commands.command()
    def entity(name: str | None):
        CreateEntityCommand().execute(name)

    @create_commands.command()
    def hash():
        CreateHashCommand().execute()

    @create_commands.command()
    def register():
        CreateRegisterCommand().execute()

    @create_commands.command()
    def user(name: str | None):
        CreateUserCommand().execute()

    app.add_typer(
        create_commands,
        name="create",
        help="Create management commands",
    )