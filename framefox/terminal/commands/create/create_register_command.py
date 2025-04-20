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
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""

REGISTER_CONTROLLER_TEMPLATE = r"security/register_controller_template.jinja2"
REGISTER_VIEW_TEMPLATE = r"security/register_view_template.jinja2"

CONTROLLER_PATH = r"src/controllers"
VIEW_PATH = r"templates/security"


class CreateRegisterCommand(AbstractCommand):
    def __init__(self):
        super().__init__()
        os.makedirs(VIEW_PATH, exist_ok=True)

    def execute(self):
        self.printer.print_msg(
            "What is the name of the entity that will be used as the provider?",
            theme="bold_normal",
            linebefore=True,
        )
        provider_name = InputManager().wait_input("Provider name")

        self._create_register_files(provider_name)

    def _create_register_files(self, provider_name: str):
        controller_path = os.path.join(CONTROLLER_PATH, "register_controller.py")
        view_path = os.path.join(VIEW_PATH, "register.html")

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

        FileCreator.create_file(
            REGISTER_CONTROLLER_TEMPLATE,
            controller_path,
            data={
                "entity_file_name": provider_name,
                "entity_class_name": ClassNameManager.snake_to_pascal(provider_name),
            },
        )
        self.printer.print_full_text(
            f"[bold orange1]Register controller created successfully:[/bold orange1] {
                controller_path}",
            linebefore=True,
        )

        FileCreator.create_file(
            REGISTER_VIEW_TEMPLATE,
            view_path,
        )
        self.printer.print_full_text(
            f"[bold orange1]Register view created successfully:[/bold orange1] {
                view_path}",
        )
