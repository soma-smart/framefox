import os

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.input_manager import InputManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphaël
Github: https://github.com/Vasulvius
"""


CONTROLLER_TEMPLATE = r"controller_template.jinja2"
VIEW_TEMPLATE = r"view_template.jinja2"

CONTROLLER_PATH = r"src/controllers"
VIEW_PATH = r"templates"


class CreateControllerCommand(AbstractCommand):
    def __init__(self):
        super().__init__()

    def execute(self, name: str = None):
        self.printer.print_msg(
            "What is the name of the controller ?(snake_case)",
            theme="bold_normal",
            linebefore=True,
        )
        if name is None:
            name = InputManager().wait_input("Controller name")
            if name == "":
                return

        if not ClassNameManager.is_snake_case(name):
            self.printer.print_msg(
                "Invalid name. Must be in snake_case.",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return

        class_name = f"{ClassNameManager.snake_to_pascal(name)}Controller"

        data_controller = {
            "controller_class_name": class_name,
            "controller_file_name": name,
            "view_name": f"{name}/index.html",
            "name": name,
        }
        data_view = {
            "pascal_case_name": ClassNameManager.snake_to_pascal(name),
            "controller_class_name": class_name,
        }
        controller_path = os.path.join(CONTROLLER_PATH, f"{name}_controller.py")
        if FileCreator.check_if_exists(controller_path):
            self.printer.print_msg(
                f"Controller {name} already exists!",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return

        # Vérifier si le template existe
        if os.path.exists(os.path.join(VIEW_PATH, name)):
            self.printer.print_msg(
                f"View folder {name} already exists!",
                theme="error",
                linebefore=True,
                newline=True,
            )
        FileCreator.create_file(
            CONTROLLER_TEMPLATE,
            controller_path,
            data=data_controller,
        )
        os.makedirs(os.path.join(VIEW_PATH, name))
        view_path = os.path.join(VIEW_PATH, name, "index.html")
        FileCreator.create_file(
            VIEW_TEMPLATE,
            view_path,
            data=data_view,
        )

        self.printer.print_full_text(
            f"[bold orange1]Controller created successfully:[/bold orange1] {
                controller_path}",
            linebefore=True,
        )
        self.printer.print_full_text(
            f"[bold orange1]View created successfully:[/bold orange1] {
                view_path}",
            newline=True,
        )
