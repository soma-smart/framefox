import os

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.model_checker import ModelChecker


class CreateRegisterCommand(AbstractCommand):
    def __init__(self):
        super().__init__("register")
        self.register_controller_template_name = r"security/register_controller_template.jinja2"
        self.register_view_template_name = r"security/register_view_template.jinja2"
        self.controller_path = self.get_settings().controller_dir
        self.view_path = r"templates/security"
        os.makedirs(self.view_path, exist_ok=True)

    def execute(self, provider_name: str = None):
        """
        Create the register controller and view.\n
        This command will create a register controller and view for the provider entity.\n
        It will ask the user for the provider name, validate it, and create the files if they do not already exist.\n
        The provider name must be in snake_case and must have 'password' and 'email' properties.\n
        If the provider entity already exists, it will not create the files and will raise an error.\n
        If the files already exist, it will not create them and will inform the user.\n
        If the provider name is not valid, it will raise an error.\n
        If the provider name is valid, it will create the register controller and view files.\n

        Args:
            provider_name (str, optional): The name of the provider entity in snake_case. Defaults to None.
        """
        self.printer.print_msg(
            "What is the name of the entity that will be used as the provider? (snake_case)",
            theme="bold_normal",
            linebefore=True,
        )

        if provider_name is None:
            provider_name = InputManager().wait_input("Provider name", default="user")
            if provider_name == "":
                raise Exception("Provider name cannot be empty.")

        if not ClassNameManager.is_snake_case(provider_name):
            self.printer.print_msg(
                "Invalid name. Must be in snake_case.",
                theme="error",
                linebefore=True,
                newline=True,
            )
            raise Exception("Invalid name. Must be in snake_case.")

        if not ModelChecker().check_entity_and_repository(provider_name):
            self.printer.print_msg(
                "Provider entity does not exist. Please use framefox create user",
                theme="error",
                linebefore=True,
                newline=True,
            )
            raise Exception("Provider entity does not exist.")

        if not ModelChecker().check_entity_properties(provider_name, ["password", "email"]):
            self.printer.print_msg(
                "Provider entity must have 'password' and 'email' properties.",
                theme="error",
                linebefore=True,
                newline=True,
            )
            raise Exception("Provider entity must have 'password' and 'email' properties.")

        self._create_register_files(provider_name)

    def _create_register_files(self, provider_name: str):
        controller_path = os.path.join(self.controller_path, "register_controller.py")
        view_path = os.path.join("templates/security", "register.html")

        existing_files = []
        if os.path.exists(controller_path):
            existing_files.append("Register controller")
        if os.path.exists(view_path):
            existing_files.append("Register view")

        if existing_files:
            self.printer.print_full_text(
                "[bold red]Cannot create register files. Following files already exist:[/bold red]",
                linebefore=True,
            )
            for file in existing_files:
                self.printer.print_msg(f"• {file}", theme="error")
            raise Exception("Register files already exist.")

        file_path = FileCreator().create_file(
            self.register_controller_template_name,
            self.controller_path,
            name=r"register_controller",
            data={
                "entity_file_name": provider_name,
                "entity_class_name": ClassNameManager.snake_to_pascal(provider_name),
            },
        )
        self.printer.print_full_text(
            f"[bold orange1]Register controller created successfully:[/bold orange1] {file_path}",
            linebefore=True,
        )

        file_path = FileCreator().create_file(
            self.register_view_template_name,
            self.view_path,
            name=r"register.html",
            data={},
            format="html",
        )
        self.printer.print_full_text(
            f"[bold orange1]Register view created successfully:[/bold orange1] {file_path}",
        )
