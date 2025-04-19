import os
from typing import Optional

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.commands.create.entity.import_manager import \
    ImportManager
from framefox.terminal.commands.create.entity.property_manager import \
    PropertyManager
from framefox.terminal.commands.create.entity.relation_manager import \
    RelationManager
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.model_checker import ModelChecker
from framefox.terminal.common.printer import Printer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen & LEUROND Raphael
Github: https://github.com/RayenBou
Github: https://github.com/Vasulvius
"""


class CreateEntityCommand(AbstractCommand):
    def __init__(self):
        super().__init__()
        self.property_manager = PropertyManager(InputManager(), Printer())
        self.relation_manager = RelationManager(
            InputManager(), Printer(), FileCreator(), ImportManager(Printer())
        )
        self.import_manager = ImportManager(Printer())
        self.file_creator = FileCreator()

    def execute(self, name: Optional[str] = None):
        self.printer.print_msg(
            "What is the name of the Entity ?(snake_case)",
            theme="bold_normal",
            linebefore=True,
        )
        entity_name = self._validate_and_get_entity_name(name)
        if not entity_name:
            return

        if not self._ensure_entity_exists(entity_name):
            return

        self._process_entity_properties(entity_name)

    def _validate_and_get_entity_name(self, name: Optional[str]) -> Optional[str]:
        if not name:
            name = InputManager().wait_input("Entity name")

        if not name or not ClassNameManager.is_snake_case(name):
            self.printer.print_msg(
                "Invalid name. Must be in snake_case.", theme="error"
            )
            return None
        return name

    def _ensure_entity_exists(self, entity_name: str) -> bool:
        exists = ModelChecker().check_entity_and_repository(entity_name)

        if exists:
            self.printer.print_full_text(
                f"The entity '[bold orange1]{
                    entity_name}[/bold orange1]' already exists. You are updating it !",
                newline=True,
            )
        else:
            self.printer.print_full_text(
                f"Creating the entity '[bold orange1]{
                    entity_name}[/bold orange1]'",
                newline=True,
            )
            self.create_entity_and_repository(entity_name)

        return True

    def _process_entity_properties(self, entity_name: str):
        while True:
            property_details = self.property_manager.request_property(entity_name)
            if property_details is None:
                continue
            if property_details is False:
                break
            if property_details.type == "relation":
                self.relation_manager.create_relation(
                    entity_name, property_details.name, property_details.optional
                )
            else:
                self.property_manager.add_property(entity_name, property_details)

    def create_entity_and_repository(self, entity_name: str):
        """Crée l'entité et le dépôt associé"""
        entity_class = ClassNameManager.snake_to_pascal(entity_name)
        repository_class = f"{entity_class}Repository"
        entity_file_path = os.path.join("src/entity", f"{entity_name}.py")
        repository_file_path = os.path.join(
            "src/repository", f"{entity_name}_repository.py"
        )

        self.file_creator.create_file(
            template="entity_template.jinja2",
            path="src/entity",
            name=entity_name,
            data={"class_name": entity_class, "properties": []},
        )

        self.file_creator.create_file(
            template="repository_template.jinja2",
            path="src/repository",
            name=f"{entity_name}_repository",
            data={
                "snake_case_name": entity_name,
                "entity_class_name": entity_class,
                "repository_class_name": repository_class,
            },
        )

        self.printer.print_msg(
            f"Entity '{entity_name}' and repository created successfully.",
            theme="success",
        )
