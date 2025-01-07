from src.terminal.commands.abstract_command import AbstractCommand
from src.terminal.common.class_name_manager import ClassNameManager
from src.terminal.common.file_creator import FileCreator


class CreateEntityCommand(AbstractCommand):
    def __init__(self):
        super().__init__('create_entity')
        self.entity_template = r"entity_template.jinja2"
        self.repository_template = r"repository_template.jinja2"
        self.entity_path = r"src/entity"
        self.repository_path = r"src/repository"

    def execute(self, name: str):
        if not ClassNameManager.is_snake_case(name):
            print("Invalid class name. Must be in snake_case.")
            return
        self.create_entity(name)
        self.create_repository(name)

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
        }
        FileCreator().create_file(
            self.repository_template,
            self.repository_path,
            f"{name}_repository",
            data
        )

    @staticmethod
    def create_repository_class_name(name: str) -> str:
        return f"{ClassNameManager.snake_to_pascal(name)}Repository"

    @staticmethod
    def create_entity_class_name(name: str) -> str:
        return ClassNameManager.snake_to_pascal(name)
