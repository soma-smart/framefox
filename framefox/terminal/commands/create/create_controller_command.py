from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.input_manager import InputManager


class CreateControllerCommand(AbstractCommand):
    def __init__(self):
        super().__init__("controller")
        self.controller_path = r"src/controllers"
        self.view_path = r"templates"
        self.controller_template = r"controller_template.jinja2"
        self.view_template = r"view_template.jinja2"

    def execute(self, name: str = None):
        """
        Create a simple controller with a exemple route and view.

        Args:
            name (str): The name of the controller.
        """
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
        view_name = f"{name}.html"

        data_controller = {
            "controller_class_name": class_name,
            "controller_file_name": name,
            "view_name": view_name,
            "name": name,
        }
        data_view = {
            "pascal_case_name": ClassNameManager.snake_to_pascal(name),
            "controller_class_name": class_name,
        }

        controller_path = FileCreator().create_file(
            template=self.controller_template,
            path=self.controller_path,
            name=f"{name}_controller",
            data=data_controller,
        )
        view_path = FileCreator().create_file(
            template=self.view_template,
            path=self.view_path,
            name=view_name,
            data=data_view,
            format="html",
        )

        self.printer.print_full_text(
            f"[bold green]Controller created successfuly:[/bold green] {
                controller_path}",
            linebefore=True,
        )
        self.printer.print_full_text(
            f"[bold green]View created successfully:[/bold green] {
                view_path}",
            newline=True,
        )
