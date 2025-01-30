from typing import Optional
from framefox.terminal.commands.create.entity.property_manager import PropertyManager
from framefox.terminal.commands.create.entity.relation_manager import RelationManager
from framefox.terminal.commands.create.entity.import_manager import ImportManager
from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.printer import Printer
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.model_checker import ModelChecker
from framefox.terminal.common.class_name_manager import ClassNameManager


class CreateEntityCommand(AbstractCommand):
    def __init__(self):
        super().__init__("entity")
        self.property_manager = PropertyManager(InputManager(), Printer())
        self.relation_manager = RelationManager(
            InputManager(), Printer(), FileCreator(), ImportManager(Printer()))
        self.import_manager = ImportManager(Printer())

    def execute(self, name: Optional[str] = None):
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
                "Nom invalide. Doit être en snake_case.", theme="error")
            return None

        return name

    def _ensure_entity_exists(self, entity_name: str) -> bool:
        exists = ModelChecker().check_entity_and_repository(entity_name)

        if exists:
            self.printer.print_full_text(
                f"L'entité '[bold green]{
                    entity_name}[/bold green]' existe déjà. Modification en cours...",
                newline=True
            )
        else:
            self.printer.print_full_text(
                f"Création de l'entité '[bold green]{
                    entity_name}[/bold green]'...",
                newline=True
            )
            self._create_entity_and_repository(entity_name)

        return True

    def _process_entity_properties(self, entity_name: str):
        while True:
            # Passer entity_name au property_manager
            property_details = self.property_manager.request_property(
                entity_name)

            # Si None, la propriété existe déjà ou est invalide, continuer la boucle
            if property_details is None:
                continue

            # Si False, l'utilisateur veut sortir
            if property_details is False:
                break

            if property_details.type == "relation":
                self.relation_manager.create_relation(
                    entity_name,
                    property_details.name,
                    property_details.optional
                )
            else:
                self.property_manager.add_property(
                    entity_name, property_details)
