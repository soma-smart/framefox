import os
from dataclasses import dataclass
from typing import Optional, Tuple

from framefox.terminal.commands.create.entity.import_manager import \
    ImportManager
from framefox.terminal.common.class_name_manager import ClassNameManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


@dataclass
class PropertyDetails:
    name: str
    type: str
    constraints: Optional[Tuple]
    optional: bool


class PropertyManager:
    def __init__(self, input_manager, printer):
        self.input_manager = input_manager
        self.printer = printer
        self.entity_folder = "src/entity"
        self.import_manager = ImportManager(printer)
        self.property_types = [
            "str",
            "int",
            "float",
            "bool",
            "list",
            "tuple",
            "dict",
            "date",
            "relation",
        ]

    def _property_exists(self, entity_name: str, property_name: str) -> bool:
        file_path = os.path.join(self.entity_folder, f"{entity_name}.py")

        with open(file_path, "r") as file:
            content = file.readlines()

        for line in content:
            if line.strip().startswith(f"{property_name}:"):
                self.printer.print_msg(
                    f"The property '{property_name}' already exists in '{entity_name}'.",
                    theme="error",
                )
                return True
        return False

    def add_property(self, entity_name: str, property_details: PropertyDetails) -> bool:
        if self._property_exists(entity_name, property_details.name):
            return False

        # Ajouter les imports nécessaires selon le type
        if property_details.type == "date":
            self.import_manager.add_import_to_entity(entity_name, "import datetime")
            # Modifier le type pour utiliser datetime.datetime au lieu de simplement date
            property_type = "datetime.datetime"
        else:
            property_type = property_details.type

        property_prompt = self._build_property(
            property_details.name,
            property_type,  # Utiliser le type modifié
            property_details.constraints,
            property_details.optional,
        )
        file_path = self._insert_property(entity_name, property_prompt)
        self.printer.print_full_text(
            f"[bold orange1]Property '{property_details.name}' added to[/bold orange1] {file_path}",
            linebefore=True,
            newline=True,
        )
        return True

    def _build_property(
        self,
        property_name: str,
        property_type: str,
        property_constraint: Optional[Tuple],
        optional: bool,
    ) -> str:
        # Détection des types avec un point (comme datetime.datetime)
        if "." in property_type:
            field_type = property_type
        else:
            field_type = property_type

        # Utilisez field_type ici au lieu de property_type
        property_header = f"    {property_name}: {field_type}"
        property_core = " = Field("
        property_parameters = []

        if property_constraint:
            property_parameters.extend(property_constraint)
        if not optional:
            property_parameters.append("nullable=False")
        else:
            property_parameters.append("nullable=True")

        property_parameters_str = ", ".join(property_parameters)
        final_property = f"{property_header}{property_core}{property_parameters_str})\n"
        return final_property

    def _insert_property(self, entity_name: str, property_prompt: str) -> str:
        file_path = os.path.join(self.entity_folder, f"{entity_name}.py")

        with open(file_path, "r") as file:
            content = file.readlines()

        class_found = False
        insertion_index = None
        indentation = "    "

        for i, line in enumerate(content):
            if line.strip().startswith(
                f"class {ClassNameManager.snake_to_pascal(entity_name)}("
            ) or line.strip().startswith(
                f"class {ClassNameManager.snake_to_pascal(entity_name)}:"
            ):
                class_found = True
                continue

            if class_found:
                if not line.startswith(indentation) and line.strip():
                    insertion_index = i
                    break

                if line.startswith(indentation):
                    insertion_index = i + 1

        if class_found and insertion_index is not None:
            if not property_prompt.startswith(indentation):
                property_prompt = indentation + property_prompt.lstrip()

            content.insert(insertion_index, property_prompt)
            with open(file_path, "w") as file:
                file.writelines(content)
        else:
            self.printer.print_error(
                f"Class '{ClassNameManager.snake_to_pascal(
                    entity_name)}' not found in '{file_path}'."
            )
            raise ValueError(
                f"Class '{ClassNameManager.snake_to_pascal(
                    entity_name)}' not found in '{file_path}'."
            )

        return file_path

    def request_property(self, entity_name: str) -> Optional[PropertyDetails]:
        name = self._request_property_name()
        if not name:
            self.printer.print_msg(
                "No property entered. Closing terminal.", theme="success"
            )
            exit(0)

        if self._property_exists(entity_name, name):
            return None

        type_ = self._request_property_type()
        constraints = self._manage_property_constraint(type_)
        optional = True

        if type_ != "relation":
            optional = self._request_optional()

        return PropertyDetails(name, type_, constraints, optional)

    def _request_property_name(self) -> str:
        self.printer.print_msg(
            "Do you want to add a new property to the entity ?(press enter to quit the terminal)",
            theme="bold_normal",
            linebefore=True,
        )
        return self.input_manager.wait_input("Property name").strip()

    def _request_property_type(self) -> str:
        return (
            self.input_manager.wait_input(
                "Property type [?]", choices=self.property_types, default="str"
            )
            .strip()
            .lower()
            or "str"
        )

    def _manage_property_constraint(self, property_type: str) -> Optional[Tuple]:
        if property_type == "str":
            max_length = self.input_manager.wait_input(
                "Maximum length", default=256
            ).strip()
            if max_length.isdigit():
                return ("max_length=" + max_length,)
        return None

    def _request_optional(self) -> bool:
        return (
            self.input_manager.wait_input(
                "Optional [?]", choices=["yes", "no"], default="no"
            )
            .strip()
            .lower()
            == "yes"
        )
