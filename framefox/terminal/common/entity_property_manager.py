from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.input_manager import InputManager
from framefox.terminal.common.model_checker import ModelChecker
from framefox.terminal.common.printer import Printer
"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""

class EntityPropertyManager(object):
    """
    Manages entity properties for the framework.
    
    This class handles the creation, validation, and insertion of properties
    into entity files. It supports various property types including basic types
    and relations between entities.
    """
    
    def __init__(self):
        self.entity_folder = r"src/entity"
        self.printer = Printer()
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

    def request_and_add_property(self, entity_name=None):
        request = self.request_property(entity_name)
        if request is None:
            return None
        entity_name, property_name, property_type, property_constraint, optional = (
            request
        )

        if property_type == "relation":
            return self.handle_relation(entity_name, property_name, optional)
        else:
            property_prompt = self.build_property(
                property_name, property_type, property_constraint, optional
            )
            file_path = self.insert_property(entity_name, property_prompt)
            self.printer.print_full_text(
                f"[bold green]Property '{property_name}' added to[/bold green] {file_path}",
                linebefore=True,
                newline=True,
            )
            return True

    def handle_relation(self, entity_name, property_name):
        return ("relation", entity_name, property_name)

    def request_property(self, entity_name=None):
        if entity_name is None:
            entity_name = self.request_snake_case(
                "What is the name of the entity?(snake_case)"
            )
        if entity_name is None:
            return None
        property_name = self.request_property_name()
        if property_name == "":
            return None
        property_type = self.request_property_type()
        property_constraint = self.manage_property_constraint(property_type)
        optional = self.request_optionnal()
        return entity_name, property_name, property_type, property_constraint, optional

    def build_property(
        self,
        property_name: str,
        property_type: str,
        property_constraint: tuple,
        optional: str,
    ):
        property_header = f"    {property_name}: {property_type}"
        property_core = ""
        property_parameters = ""
        if property_constraint or optional == "yes":
            property_core = " = Field("
            params = []
            if property_constraint:
                params.append(
                    f"{property_constraint[0]}={property_constraint[1]}"
                )
            if optional == "yes":
                params.append("nullable=True")
            property_parameters = ", ".join(params)
        final_property = (
            property_header + property_core + property_parameters + ")" + "\n"
        )
        return final_property

    def insert_property(self, entity_name: str, property_prompt: str):
        file_path = self.entity_folder + "/" + entity_name + ".py"

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

    def request_snake_case(self, prompt, loop=False):
        name = InputManager.wait_input(prompt=prompt)
        if not ClassNameManager.is_snake_case(name):
            self.printer.print_msg(
                "Invalid name. Must be in snake_case.",
                theme="error",
                linebefore=True,
                newline=True,
            )
            if loop:
                return EntityPropertyManager.request_snake_case(prompt, loop)
            else:
                return None
        return name

    def request_property_name(self):
        prompt = "Property name"
        name = InputManager.wait_input(prompt=prompt)
        return name

    def request_property_type(self):
        property_type = (
            InputManager()
            .wait_input("Property type [?]", choices=self.property_types, default="str")
            .strip()
            .lower()
            or "str"
        )

        if property_type == "date":
            property_type = "datetime"

        return property_type

    def request_optionnal(self):
        optional = InputManager.wait_input(
            prompt="Optional [?]", choices=["yes", "no"], default="no"
        )
        return optional

    def manage_property_constraint(self, property_type):
        if property_type == "str":
            str_length = InputManager.wait_input(
                prompt="String max length", default=256
            )
            constraint = ("max_length", str_length)
        else:
            constraint = None
        return constraint
