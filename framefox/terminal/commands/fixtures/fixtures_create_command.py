import os
from typing import Optional

import typer

from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.model_checker import ModelChecker


class FixturesCreateCommand(AbstractCommand):
    def __init__(self):
        super().__init__("create")
        self.file_creator = FileCreator()
        self.model_checker = ModelChecker()

    def execute(self, name: Optional[str] = None):
        """Create fixture file for an entity"""
        self.printer.print_msg(
            "On which entity you want to create this fixture?(snake_case)",
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
        loop_input = InputManager().wait_input("Number of fixtures (default=3)")
        try:
            loop_count = int(loop_input) if loop_input else 3
        except ValueError:
            loop_count = 3

        if not self.model_checker.check_entity_class(entity_name, verbose=True):
            return

        self._create_fixture_file(entity_name, loop_count)

    def _validate_and_get_entity_name(self, name: Optional[str]):
        if not name:
            name = InputManager().wait_input("Entity name (snake_case)")
        if not name or not ClassNameManager.is_snake_case(name):
            self.printer.print_msg(
                "Invalid name. Must be in snake_case.", theme="error"
            )
            return None
        return name

    def _create_fixture_file(self, entity_name: str, loop_count: int):
        fixtures_dir = "src/fixtures"
        if not os.path.exists(fixtures_dir):
            os.makedirs(fixtures_dir)

        entity_class = ClassNameManager.snake_to_pascal(entity_name)
        fixture_class = f"{entity_class}Fixture"

        properties_list = self.model_checker.get_entity_properties(
            entity_name, verbose=True
        )

        properties_list = [prop for prop in properties_list if prop["name"] != "id"]

        self.file_creator.create_file(
            template="fixture_create_template.jinja2",
            path=fixtures_dir,
            name=f"{entity_name}_fixture",
            data={
                "entity_name": entity_name,
                "entity_class_name": entity_class,
                "fixture_class_name": fixture_class,
                "properties": properties_list,
                "loop_count": loop_count,
            },
        )

        self.printer.print_msg(
            f"Fixture file created: {fixtures_dir}/{entity_name}_fixture.py",
            theme="success",
        )
