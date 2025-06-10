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


class CreateControllerCommand(AbstractCommand):
    def __init__(self):
        super().__init__("controller")
        self.controller_path = r"src/controller"
        self.view_path = r"templates"
        self.controller_template = r"controller_template.jinja2"
        self.view_template = r"view_template.jinja2"

    def execute(self, name: str = None):
        """
        Create a simple controller and view.

        Args:
            name (str): The name of the controller.
        """
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
        file_creator = FileCreator()
        if file_creator.check_if_exists(self.controller_path, f"{name}_controller"):
            self.printer.print_msg(
                f"Controller {name} already exists!",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return

        # Vérifier si le template existe
        if os.path.exists(os.path.join(self.view_path, name)):
            self.printer.print_msg(
                f"View folder {name} already exists!",
                theme="error",
                linebefore=True,
                newline=True,
            )
        controller_path = FileCreator().create_file(
            template=self.controller_template,
            path=self.controller_path,
            name=f"{name}_controller",
            data=data_controller,
        )
        os.makedirs(os.path.join(self.view_path, name))
        view_path = FileCreator().create_file(
            template=self.view_template,
            path=os.path.join(self.view_path, name),
            name="index.html",
            data=data_view,
            format="html",
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
