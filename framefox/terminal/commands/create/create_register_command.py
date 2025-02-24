import os

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.model_checker import ModelChecker

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class CreateRegisterCommand(AbstractCommand):
    def __init__(self):
        super().__init__("register")
        self.register_controller_template_name = (
            r"security/register_controller_template.jinja2"
        )
        self.register_view_template_name = r"security/register_view_template.jinja2"
        self.controller_path = r"src/controllers"
        self.view_path = r"templates/security"
        os.makedirs(self.view_path, exist_ok=True)

    def execute(self):
        """
        Create the register controller and view
        """
        self.printer.print_msg(
            "What is the name of the entity that will be used as the provider?",
            theme="bold_normal",
            linebefore=True,
        )
        provider_name = InputManager().wait_input("Provider name")

        self._create_register_files(provider_name)

    def _create_register_files(self, provider_name: str):

        controller_path = os.path.join("src/controllers", "register_controller.py")
        view_path = os.path.join("templates/security", "register.html")

        existing_files = []
        if os.path.exists(controller_path):
            existing_files.append("Register controller")
        if os.path.exists(view_path):
            existing_files.append("Register view")

        if existing_files:
            self.printer.print_full_text(
                f"[bold red]Cannot create register files. Following files already exist:[/bold red]",
                linebefore=True,
            )
            for file in existing_files:
                self.printer.print_msg(f"• {file}", theme="error")
            return None

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
            f"[bold orange1]Register controller created successfully:[/bold orange1] {
                file_path}",
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
            f"[bold orange1]Register view created successfully:[/bold orange1] {
                file_path}",
        )
