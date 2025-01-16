from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.model_checker import ModelChecker
from framefox.terminal.common.input_manager import InputManager


class CreateCrudCommand(AbstractCommand):
    def __init__(self):
        super().__init__('crud')
        self.api_controller_template = r"api_crud_controller_template.jinja2"
        self.templated_controller_template = r"api_crud_controller_template.jinja2"
        self.controllers_path = r'src/controllers'
        self.input_choices = ['api', 'templated']

    def execute(self, entity_name: str):
        """
        Make a CRUD controller for the given entity name.

        Args:
            entity_name (str): The name of the entity in snake_case.
        """
        if not ClassNameManager.is_snake_case(entity_name):
            print("\033[91mInvalid name. Must be in snake_case.\033[0m")
            return
        if not ModelChecker().check_entity_and_repository(entity_name):
            print("\033[91mFailed to create controller.\033[0m")
            return
        print("What type of controller do you want to create?")
        user_input = InputManager.wait_input(
            input_type='controller type',
            choices=self.input_choices
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
        if user_input == 'api':
            FileCreator().create_file(
                self.api_controller_template,
                self.controllers_path,
                f"{entity_name}_controller",
                data
            )
        else:
            FileCreator().create_file(
                self.templated_controller_template,
                self.controllers_path,
                f"{entity_name}_controller",
                data
            )
        print("\033[92m" + f"Controller '{class_name}' created." + "\033[0m")
