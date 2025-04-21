from typer import Typer, Option

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
    )

    @create_commands.command()
    def auth():
        """
        Create a new authenticator
        """
        CreateAuthCommand().execute()

    @create_commands.command()
    def controller(name: str = Option(None, help="The name of the controller")):
        """
        Create a simple controller and view.
        """
        if name:
            CreateControllerCommand().execute(name)
        else:
            CreateControllerCommand().execute()

    @create_commands.command()
    def crud(entity_name: str = Option(None, help="The name of the entity in snake_case")):
        """
        Create a CRUD controller for the given entity name.
        """
        if entity_name:
            CreateCrudCommand().execute(entity_name)
        else:
            CreateCrudCommand().execute()

    @create_commands.command()
    def entity(name: str = Option(None, help="The name of the entity in snake_case")):
        """
        Create a new entity
        """
        if name:
            CreateEntityCommand().execute(name)
        else:
            CreateEntityCommand().execute()

    @create_commands.command()
    def hash():
        """
        Create a hashed password and display the result
        """
        CreateHashCommand().execute()

    @create_commands.command()
    def register():
        """
        Create the register controller and view
        """
        CreateRegisterCommand().execute()

    @create_commands.command()
    def user(name: str = Option(None, help="The name of the entity in snake_case")):
        """
        Create a user entity for the authentication.
        """
        if name:
            CreateUserCommand().execute(name)
        else:
            CreateUserCommand().execute()

    app.add_typer(
        create_commands,
        name="create",
        help="Create various resources like entities or CRUD operations.",
    )