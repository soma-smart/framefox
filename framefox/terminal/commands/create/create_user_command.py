from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.commands.create.create_entity_command import \
    CreateEntityCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.entity_property_manager import \
    EntityPropertyManager
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.model_checker import ModelChecker

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen & LEUROND Raphael
Github: https://github.com/RayenBou
Github: https://github.com/Vasulvius
"""


class CreateUserCommand(AbstractCommand):
    def __init__(self):
        super().__init__()
        self.create_entity_command = CreateEntityCommand()
        self.entity_property_manager = EntityPropertyManager()

    def execute(self, name: str = None):
        self.printer.print_msg(
            "What is the name of the user entity ?(snake_case)",
            theme="bold_normal",
            linebefore=True,
        )
        if name is None:
            name = InputManager().wait_input("Entity name", default="user")
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
        if ModelChecker().check_entity_and_repository(name):
            self.printer.print_msg(
                "Entity already exists. You cannot replace it by a provider.",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return
        entity_path = self.create_entity_command.create_entity_and_repository(name)

        self.entity_property_manager.insert_property(
            name, "    password: str= Field(nullable=False)\n"
        )
        self.entity_property_manager.insert_property(
            name, "    email: str= Field(nullable=False)\n"
        )
        self.entity_property_manager.insert_property(
            name,
            "    roles: list[str] = Field(default_factory=lambda: ['ROLE_USER'], sa_column=Column(JSON))\n",
        )
