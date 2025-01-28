from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.model_checker import ModelChecker
from framefox.terminal.common.input_manager import InputManager


class CreateCrudCommand(AbstractCommand):
    def __init__(self):
        super().__init__("crud")
        self.api_controller_template = r"api_crud_controller_template.jinja2"
        self.templated_controller_template = r"api_crud_controller_template.jinja2"
        self.controllers_path = r"src/controllers"
        self.input_choices = ["api", "templated"]

    def execute(self, entity_name: str = None):
        """
        Make a CRUD controller for the given entity name.

        Args:
            entity_name (str): The name of the entity in snake_case.
        """
        if entity_name is None:
            entity_name = InputManager().wait_input("Entity name")
            if entity_name == "":
                return

        if not ClassNameManager.is_snake_case(entity_name):
            self.printer.print_msg(
                "Invalid name. Must be in snake_case.",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return

        if not ModelChecker().check_entity_and_repository(entity_name):
            self.printer.print_msg(
                "Failed to create controller. Entity or repository does not exist.",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return

        self.printer.print_msg(
            "What type of controller do you want to create?",
            theme="bold_normal",
            linebefore=True,
        )
        user_input = InputManager.wait_input(
            prompt="Controller type [?]", choices=self.input_choices
        )
        entity_class_name = ClassNameManager.snake_to_pascal(entity_name)
        class_name = f"{entity_class_name}Controller"
        data = {
            "controller_class_name": class_name,
            "repository_file_name": f"{entity_name}_repository",
            "repository_class_name": f"{entity_class_name}Repository",
            "entity_file_name": entity_name,
            "entity_class_name": entity_class_name,
            "entity_name": entity_name,
        }
        if user_input == "api":
            file_path = FileCreator().create_file(
                self.api_controller_template,
                self.controllers_path,
                f"{entity_name}_controller",
                data,
            )
        else:
            file_path = FileCreator().create_file(
                self.templated_controller_template,
                self.controllers_path,
                f"{entity_name}_controller",
                data,
            )

        self.printer.print_full_text(
            f"[bold green]Controller '{
                class_name}' created:[/bold green] {file_path}",
            linebefore=True,
            newline=True,
        )
