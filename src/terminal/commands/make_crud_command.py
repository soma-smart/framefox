from src.terminal.commands.abstract_command import AbstractCommand
from src.terminal.common.file_creator import FileCreator
from src.terminal.common.class_name_manager import ClassNameManager


class MakeCrudCommand(AbstractCommand):
    def __init__(self):
        super().__init__('make_crud')
        self.controler_template = r"controller_template.jinja2"
        self.controllers_path = r'src/controllers'

    def execute(self, entity_name: str):
        """
        Make a CRUD controller for the given entity name.

        Args:
            entity_name (str): The name of the entity in snake_case.
        """
        if not ClassNameManager.is_snake_case(entity_name):
            print("Invalid name. Must be in snake_case.")
            return
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
        # print(data)
        FileCreator().create_file(
            self.controler_template,
            self.controllers_path,
            f"{entity_name}_controller",
            data
        )
