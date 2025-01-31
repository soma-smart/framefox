from dataclasses import dataclass
from typing import Optional, Tuple, List
import os
from framefox.terminal.common.class_name_manager import ClassNameManager


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
        self.property_types = ["str", "int", "float", "bool",
                               "list", "tuple", "dict", "date", "relation"]

    def _property_exists(self, entity_name: str, property_name: str) -> bool:
        file_path = os.path.join(self.entity_folder, f"{entity_name}.py")

        with open(file_path, "r") as file:
            content = file.readlines()

        for line in content:
            if line.strip().startswith(f"{property_name}:"):
                self.printer.print_msg(
                    f"The property '{property_name}' already exists in '{entity_name}'.", theme="warning")
                return True
        return False

    def add_property(self, entity_name: str, property_details: PropertyDetails) -> bool:
        if self._property_exists(entity_name, property_details.name):
            return False

        property_prompt = self._build_property(
            property_details.name,
            property_details.type,
            property_details.constraints,
            property_details.optional
        )
        file_path = self._insert_property(entity_name, property_prompt)
        self.printer.print_full_text(
            f"[bold green]Propriété '{
                property_details.name}' ajoutée à[/bold green] {file_path}",
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
        property_header = f"    {property_name}: {property_type}"
        property_core = ""
        property_parameters = ""

        if property_constraint or not optional:
            property_core += "("
            params = []
            if property_constraint:
                params.extend(property_constraint)
            if not optional:
                params.append("default=None")
            property_parameters = ", ".join(params)
            property_header += property_core + property_parameters + ")"

        final_property = (
            property_header + "\n"
        )
        return final_property

    def _insert_property(self, entity_name: str, property_prompt: str) -> str:
        file_path = os.path.join(self.entity_folder, f"{entity_name}.py")

        with open(file_path, "r") as file:
            content = file.readlines()

        class_found = False
        insertion_index = None
        indentation = "    "

        for i, line in enumerate(content):
            # Detect the class definition line
            if line.strip().startswith(f"class {ClassNameManager.snake_to_pascal(entity_name)}(") or \
                    line.strip().startswith(f"class {ClassNameManager.snake_to_pascal(entity_name)}:"):
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

            self.printer.print_error(f"Class '{ClassNameManager.snake_to_pascal(
                entity_name)}' not found in '{file_path}'.")
            raise ValueError(f"Class '{ClassNameManager.snake_to_pascal(
                entity_name)}' not found in '{file_path}'.")

        return file_path

    def request_property(self, entity_name: str) -> Optional[PropertyDetails]:
        name = self._request_property_name()
        if not name:
            return None

        if self._property_exists(entity_name, name):
            return None

        type_ = self._request_property_type()
        constraints = self._manage_property_constraint(type_)
        optional = True

        if type_ != "relation":
            optional = self._request_optional()

        return PropertyDetails(name, type_, constraints, optional)

    def _request_property_name(self) -> str:
        return self.input_manager.wait_input("Property name").strip()

    def _request_property_type(self) -> str:
        return self.input_manager.wait_input(
            "Property type [?]",
            choices=self.property_types,
            default="str"
        ).strip().lower() or "str"

    def _manage_property_constraint(self, property_type: str) -> Optional[Tuple]:
        if property_type == "str":
            max_length = self.input_manager.wait_input(
                "Maximum length ",
                default=256).strip()
            if max_length.isdigit():
                return ("max_length=" + max_length,)
        return None

    def _request_optional(self) -> bool:
        return self.input_manager.wait_input(
            "Optional [?]",
            choices=["yes", "no"],
            default="no"
        ).strip().lower() == "yes"
