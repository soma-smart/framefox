from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.model_checker import ModelChecker
from framefox.terminal.common.entity_property_manager import EntityPropertyManager
from framefox.terminal.common.input_manager import InputManager


class CreateEntityCommand(AbstractCommand):
    def __init__(self):
        super().__init__('create_entity')
        self.entity_template = r"entity_template.jinja2"
        self.repository_template = r"repository_template.jinja2"
        self.entity_path = r"src/entity"
        self.repository_path = r"src/repository"
        self.entity_property_manager = EntityPropertyManager()

    def execute(self, name: str = None):
        """
        Create the entity and the associated repository and ask for properties to add to the entity.

        Args:
            name (str, optional): The name of the entity in snake_case. Defaults to None.
        """
        if name is None:
            name = InputManager().wait_input("Entity name")
            if name == '':
                return
        if not ClassNameManager.is_snake_case(name):
            self.printer.print_msg(
                "Invalid name. Must be in snake_case.",
                theme="error",
                linebefore=True,
                newline=True
            )
            return

        does_entity_exist = ModelChecker().check_entity_and_repository(name)
        if not does_entity_exist:
            entity_path = self.create_entity(name)
            repository_path = self.create_repository(name)
            self.printer.print_msg(
                f"Entity created successfully: {entity_path}",
                theme="success",
                linebefore=True,
            )
            self.printer.print_msg(
                f"Repository created successfully: {repository_path}",
                theme="success",
                newline=True,
            )
        else:
            self.printer.print_msg(
                "Entity already exists. You can add properties to the entity.",
                theme="warning",
                linebefore=True,
                newline=True,
            )
        self.request_n_add_property_to_entity(name)

    def create_entity(self, name: str):
        data = {
            "class_name": CreateEntityCommand.create_entity_class_name(name),
        }
        file_path = FileCreator().create_file(
            self.entity_template,
            self.entity_path,
            name,
            data
        )
        return file_path

    def create_repository(self, name: str):
        data = {
            "entity_class_name": CreateEntityCommand.create_entity_class_name(name),
            "repository_class_name": CreateEntityCommand.create_repository_class_name(name),
            "snake_case_name": name,
        }
        file_path = FileCreator().create_file(
            self.repository_template,
            self.repository_path,
            f"{name}_repository",
            data
        )
        return file_path

    def request_n_add_property_to_entity(self, name: str):
        while True:
            self.printer.print_msg(
                "Enter the properties you want to add to the entity. Leave empty now to stop.",
                theme="bold_normal",
            )
            request = self.entity_property_manager.request_and_add_property(
                name)
            if not request:
                break

    @staticmethod
    def create_repository_class_name(name: str) -> str:
        return f"{ClassNameManager.snake_to_pascal(name)}Repository"

    @staticmethod
    def create_entity_class_name(name: str) -> str:
        return ClassNameManager.snake_to_pascal(name)
