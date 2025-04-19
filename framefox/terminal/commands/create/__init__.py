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
        """
        Create a new authenticator
        """
        CreateAuthCommand().execute()

    @create_commands.command()
    def controller(name: str | None = None):
        """
        Create a simple controller and view.

        Args:
            name (str): The name of the controller;
        """
        CreateControllerCommand().execute(name)

    @create_commands.command()
    def crud(entity_name: str | None = None):
        """
        Create a CRUD controller for the given entity name.

        Args:
            entity_name (str): The name of the entity in snake_case.
        """
        CreateCrudCommand().execute(entity_name)

    @create_commands.command()
    def entity(name: str | None = None):
        """
        Create a new entity

        Args:
            entity_name (str, optional): The name of the entity in snake_case
        """
        CreateEntityCommand().execute(name)

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
    def user(name: str | None = None):
        """
        Create a user entity for the authentication.

        Args:
            name (str, optional): The name of the entity in snake_case. Defaults to None.
        """
        CreateUserCommand().execute(name)

    app.add_typer(
        create_commands,
        name="create",
        help="Create management commands",
    )