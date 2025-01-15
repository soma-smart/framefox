from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.commands.add_property_command import AddPropertyCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.model_checker import ModelChecker

import inspect


class CreateEntityCommand(AbstractCommand):
    def __init__(self):
        super().__init__('create_entity')
        self.entity_template = r"entity_template.jinja2"
        self.repository_template = r"repository_template.jinja2"
        self.entity_path = r"src/entity"
        self.repository_path = r"src/repository"
        self.add_property_command = AddPropertyCommand()

    def execute(self, name: str):
        """
        Create the entity and the associated repository and ask for properties to add to the entity.

        Args:
            name (str): The name of the entity to be created in snake case.
        """
        if not ClassNameManager.is_snake_case(name):
            self.printer.print_msg(
                "Invalid name. Must be in snake_case.", theme="error")
            return

        does_entity_exist = ModelChecker().check_entity_and_repository(name)
        if not does_entity_exist:
            self.create_entity(name)
            self.create_repository(name)
            self.printer.print_msg(
                "Entity and repository created successfully.", theme="success"
            )
        else:
            self.printer.print_msg("Entity already exists.", theme="warning")
        signature = inspect.signature(self.add_property_command.execute)
        param_list = [param.name for param in signature.parameters.values()]
        self.request_n_add_property_to_entity(name, param_list)

    def create_entity(self, name: str):
        data = {
            "class_name": CreateEntityCommand.create_entity_class_name(name),
        }
        FileCreator().create_file(
            self.entity_template,
            self.entity_path,
            name,
            data
        )

    def create_repository(self, name: str):
        data = {
            "entity_class_name": CreateEntityCommand.create_entity_class_name(name),
            "repository_class_name": CreateEntityCommand.create_repository_class_name(name),
            "snake_case_name": name,
        }
        FileCreator().create_file(
            self.repository_template,
            self.repository_path,
            f"{name}_repository",
            data
        )

    def request_n_add_property_to_entity(self, name: str, param_list: list):
        while True:
            self.printer.print_msg(
                "Do you want to add a property to the entity? If yes, enter its name. Otherwise, press enter.",
                theme="normal",
            )
            property_name = InputManager.wait_input("property_name")
            if property_name == '':
                break
            param_dict = {
                'name': name,
                'property_name': property_name}
            for param in param_list:
                if param == 'name' or param == 'property_name':
                    continue
                choices = self.add_property_command.get_choices(param)
                default = self.add_property_command.get_default(param)
                input_value = InputManager.wait_input(
                    input_type=param,
                    choices=choices,
                    default=default
                )
                param_dict[param] = input_value
            self.add_property_command.execute(**param_dict)
            print("\n")

    @staticmethod
    def create_repository_class_name(name: str) -> str:
        return f"{ClassNameManager.snake_to_pascal(name)}Repository"

    @staticmethod
    def create_entity_class_name(name: str) -> str:
        return ClassNameManager.snake_to_pascal(name)
