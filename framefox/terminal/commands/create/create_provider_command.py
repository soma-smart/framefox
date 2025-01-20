from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.model_checker import ModelChecker
from framefox.terminal.common.entity_property_manager import EntityPropertyManager
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.commands.create.create_entity_command import CreateEntityCommand


class CreateProviderCommand(AbstractCommand):
    def __init__(self):
        super().__init__('provider')
        self.create_entity_command = CreateEntityCommand()
        self.entity_property_manager = EntityPropertyManager()

    def execute(self, name: str = None):
        """
        Create a provider entity and the associated repository.

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

        if ModelChecker().check_entity_and_repository(name):
            self.printer.print_msg(
                "Entity already exists. You cannot replace it by a provider.",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return

        entity_path = self.create_entity_command.create_entity(name)
        repository_path = self.create_entity_command.create_repository(name)

        self.entity_property_manager.insert_property(
            name,
            "    password: str\n"
        )
        self.entity_property_manager.insert_property(
            name,
            "    email: str\n"
        )
        self.entity_property_manager.insert_property(
            name,
            "    roles: List[str] = Field(default_factory=lambda: ['ROLE_USER'], sa_column=Column(JSON))\n"
        )

        self.printer.print_full_text(
            f"[bold green]Provider entity created successfully:[/bold green] {
                entity_path}",
            linebefore=True,
        )
        self.printer.print_full_text(
            f"[bold green]Provider repository created successfully:[/bold green] {
                repository_path}",
            newline=True,
        )
