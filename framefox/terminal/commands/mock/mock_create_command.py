import os
from typing import Optional

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.model_checker import ModelChecker

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class MockCreateCommand(AbstractCommand):
    def __init__(self):
        super().__init__("create")
        self.file_creator = FileCreator()
        self.model_checker = ModelChecker()

    def execute(self, name: Optional[str] = None):
        """
        Create mock file for an entity.
        Args:
            name (str, optional): The name of the entity in snake_case. Defaults to None.
        """
        self.printer.print_msg(
            "On which entity you want to create this mock?(snake_case)",
            theme="bold_normal",
            linebefore=True,
        )
        entity_name = self._validate_and_get_entity_name(name)
        if not entity_name:
            return

        self.printer.print_msg(
            "How many items do you want to generate?",
            theme="bold_normal",
            linebefore=True,
        )
        loop_input = InputManager().wait_input("Number of Mock (default=3)")
        try:
            loop_count = int(loop_input) if loop_input else 3
        except ValueError:
            loop_count = 3

        if not self.model_checker.check_entity_class(entity_name, verbose=True):
            return

        self._create_mock_file(entity_name, loop_count)

    def _validate_and_get_entity_name(self, name: Optional[str]):
        if not name:
            name = InputManager().wait_input("Entity name (snake_case)")
        if not name or not ClassNameManager.is_snake_case(name):
            self.printer.print_msg(
                "Invalid name. Must be in snake_case.", theme="error"
            )
            return None
        return name

    def _create_mock_file(self, entity_name: str, loop_count: int):
        mocks_dir = "src/mocks"
        if not os.path.exists(mocks_dir):
            os.makedirs(mocks_dir)

        entity_class = ClassNameManager.snake_to_pascal(entity_name)
        mock_class = f"{entity_class}Mock"

        properties_list = self.model_checker.get_entity_properties(
            entity_name, verbose=True
        )

        properties_list = [prop for prop in properties_list if prop["name"] != "id"]

        self.file_creator.create_file(
            template="mock_create_template.jinja2",
            path=mocks_dir,
            name=f"{entity_name}_mock",
            data={
                "entity_name": entity_name,
                "entity_class_name": entity_class,
                "mock_class_name": mock_class,
                "properties": properties_list,
                "loop_count": loop_count,
            },
        )

        self.printer.print_msg(
            f"mock file created: {mocks_dir}/{entity_name}_mock.py",
            theme="success",
        )
