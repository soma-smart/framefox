from dataclasses import dataclass
from typing import Optional, Tuple, List
import os


@dataclass
class PropertyDetails:
    name: str
    type: str
    constraints: Optional[Tuple]
    optional: bool


class PropertyManager():
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
                return True
        return False

    def add_property(self, entity_name: str, property_details: PropertyDetails) -> bool:
        if self._property_exists(entity_name, property_details.name):
            self.printer.print_msg(
                f"La propriété '{property_details.name}' existe déjà dans l'entité '{
                    entity_name}'.",
                theme="error"
            )
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

        if property_constraint or optional:
            property_core = " = Field("
            params = []
            if property_constraint:
                params.append(f"{property_constraint[0]}={
                              property_constraint[1]}")
            if optional:
                params.append("nullable=True")
            property_parameters = ", ".join(params)

        final_property = (
            property_header + property_core + property_parameters + ")" + "\n"
            if property_core else property_header + "\n"
        )
        return final_property

    def _insert_property(self, entity_name: str, property_prompt: str) -> str:
        file_path = os.path.join(self.entity_folder, f"{entity_name}.py")

        with open(file_path, "r") as file:
            content = file.readlines()

        class_found = False
        last_line = 0
        for i, line in enumerate(content):
            if line.strip().startswith("class ") and line.strip().endswith(
                "(AbstractEntity, table=True):"
            ):
                class_found = True
            if "Field" in line:
                last_line = i

        if class_found:
            content.insert(last_line + 1, property_prompt)

        with open(file_path, "w") as file:
            file.writelines(content)
        return file_path

    def request_property(self, entity_name: str) -> Optional[PropertyDetails]:
        name = self._request_property_name()
        if not name:
            return None

        # Vérifier si la propriété existe déjà
        if self._property_exists(entity_name, name):
            self.printer.print_msg(
                f"La propriété '{name}' existe déjà dans l'entité '{
                    entity_name}'.",
                theme="error"
            )
            return None

        type_ = self._request_property_type()
        constraints = self._manage_property_constraint(type_)
        optional = self._request_optional()
        return PropertyDetails(name, type_, constraints, optional)

    def _request_property_name(self) -> str:
        return self.input_manager.wait_input("Property name")

    def _request_property_type(self) -> str:
        return self.input_manager.wait_input(
            "Property type [?]",
            choices=self.property_types,
            default="str"
        ).strip().lower() or "str"

    def _manage_property_constraint(self, property_type: str) -> Optional[Tuple]:
        if property_type == "str":
            length = self.input_manager.wait_input(
                "String max length", default=256)
            return ("max_length", length)
        return None

    def _request_optional(self) -> bool:
        return self.input_manager.wait_input(
            "Optional [?]",
            choices=["yes", "no"],
            default="no"
        ) == "yes"
