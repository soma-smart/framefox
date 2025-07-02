import os
from dataclasses import dataclass
from typing import Optional, Tuple

from framefox.terminal.common.class_name_manager import ClassNameManager

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


@dataclass
class RelationConfig:
    type: str
    cascade_delete: bool
    optional: bool
    inverse_relation: bool
    inverse_property: Optional[str] = None


class RelationManager:
    def __init__(self, input_manager, printer, file_creator, import_manager):
        self.input_manager = input_manager
        self.printer = printer
        self.file_creator = file_creator
        self.import_manager = import_manager
        self.entity_folder = "src/entity"

    def create_relation(self, source_entity: str, property_name: str, optional: bool) -> bool:
        target_entity = self._request_target_entity()
        if not target_entity:
            return False

        config = self._get_relation_config(source_entity, target_entity, property_name)
        if config.type == "ManyToMany":
            return self._create_many_to_many_relation(source_entity, target_entity, property_name, config)
        return self._create_standard_relation(source_entity, target_entity, property_name, config)

    def _get_relation_config(self, source_entity: str, target_entity: str, property_name: str) -> RelationConfig:
        relation_type = self._request_relation_type(source_entity, target_entity)

        if relation_type in ["ManyToOne", "OneToOne"]:
            optional = self._request_optional()
        else:
            optional = False

        if relation_type == "OneToMany":
            inverse_relation, inverse_property = self._request_inverse_relation(
                source_entity,
                property_name,
                auto_inverse=True,
                relation_type=relation_type,
            )
            optional = self._request_optional()
        else:
            inverse_relation, inverse_property = self._request_inverse_relation(source_entity, property_name, relation_type=relation_type)

        if not optional and inverse_relation:
            cascade_delete = self._request_delete_behavior()
        else:
            cascade_delete = False

        return RelationConfig(relation_type, cascade_delete, optional, inverse_relation, inverse_property)

    def _request_relation_type(self, source_entity: str, target_entity: str) -> str:
        source_class = ClassNameManager.snake_to_pascal(source_entity)
        target_class = ClassNameManager.snake_to_pascal(target_entity)

        relation_types = {
            "1": "OneToOne",
            "2": "OneToMany",
            "3": "ManyToOne",
            "4": "ManyToMany",
        }

        help_messages = {
            "1": f"One {source_class} is linked to One {target_class}",
            "2": f"One {source_class} is linked to Many {target_class}",
            "3": f"Many {source_class} are linked to One {target_class}",
            "4": f"Many {source_class} are linked to Many {target_class}",
        }

        display_relation_types = {
            "1": "[bold orange1]OneToOne[/bold orange1]",
            "2": "[bold orange1]OneToMany[/bold orange1]",
            "3": "[bold orange1]ManyToOne[/bold orange1]",
            "4": "[bold orange1]ManyToMany[/bold orange1]",
        }

        while True:
            print()
            self.printer.print_msg("[bold orange1]Select the type of relation:[/bold orange1]")

            for key, value in display_relation_types.items():
                self.printer.print_msg(f'{key}. {value}  - "{help_messages[key]}"')

            choice = self.input_manager.wait_input(
                "Enter the number corresponding to the type of relation",
                choices=["1", "2", "3", "4"],
            ).strip()

            if choice in relation_types:
                return relation_types[choice]
            else:
                self.printer.print_msg("Invalid choice. Please try again.", theme="error")

    def _request_delete_behavior(self) -> bool:
        """Ask for delete behavior (cascade or set null)"""
        delete_choice = (
            self.input_manager.wait_input(
                "What delete behavior do you want? (cascade/set null)",
                choices=["cascade", "set null"],
                default="cascade",
            )
            .strip()
            .lower()
        )
        return delete_choice == "cascade"

    def _request_inverse_relation(
        self,
        source_entity: str,
        property_name: str,
        auto_inverse=False,
        relation_type=None,
    ) -> Tuple[bool, Optional[str]]:
        if auto_inverse:
            has_inverse = True
            self.printer.print_msg("An inverse property will be added automatically.")
        else:
            has_inverse = (
                self.input_manager.wait_input(
                    "Do you want to add an inverse relation?",
                    choices=["yes", "no"],
                    default="yes",
                )
                .strip()
                .lower()
                == "yes"
            )

        inverse_property = None
        if has_inverse:

            if relation_type == "OneToMany":
                default_inverse = source_entity
            elif relation_type == "ManyToOne":
                default_inverse = self._pluralize(source_entity)
            else:
                default_inverse = self._pluralize(source_entity)

            user_input = self.input_manager.wait_input(
                f"Enter the name of the inverse property in the target entity [{
                    default_inverse}]",
                default=default_inverse,
            ).strip()
            inverse_property = user_input if user_input else default_inverse

            if not inverse_property.isidentifier():
                self.printer.print_msg(
                    "Invalid inverse property name. Using the default name.",
                    theme="warning",
                )
                inverse_property = default_inverse

        return has_inverse, inverse_property

    def _pluralize(self, word: str) -> str:
        """Simple pluralization function"""
        if word.endswith("y") and word[-2] not in "aeiou":
            return word[:-1] + "ies"
        elif word.endswith(("s", "sh", "ch", "x", "z")):
            return word + "es"
        else:
            return word + "s"

    def _request_optional(self) -> bool:
        """Ask if the relation can be optional"""
        return self.input_manager.wait_input("Can the relation be nullable?", choices=["yes", "no"], default="yes").strip().lower() == "yes"

    def _request_target_entity(self) -> Optional[str]:
        """Request the name of the target entity and check its existence"""
        while True:
            target_entity = self.input_manager.wait_input("Enter the name of the target entity (snake_case) ").strip().lower()
            target_file = os.path.join(self.entity_folder, f"{target_entity}.py")
            if os.path.exists(target_file):
                return target_entity
            else:
                self.printer.print_msg(
                    f"The entity '{target_entity}' does not exist. Please try again.",
                    theme="error",
                )

    def _generate_relation_code(
        self,
        source_entity: str,
        target_entity: str,
        property_name: str,
        source_class: str,
        target_class: str,
        config: RelationConfig,
    ) -> Tuple[str, Optional[str]]:

        # nullable_option = ", nullable=True" if config.optional else ""

        intermediate_class = ClassNameManager.snake_to_pascal(f"{source_entity}_{target_entity}")

        if config.type == "ManyToMany":
            if not property_name.endswith("s"):
                property_name = self._pluralize(property_name)
            inverse_prop = config.inverse_property if config.inverse_property else self._pluralize(source_entity)
        elif config.type == "OneToMany":
            inverse_prop = config.inverse_property if config.inverse_property else source_entity
        elif config.type == "ManyToOne":
            inverse_prop = config.inverse_property if config.inverse_property else self._pluralize(source_entity)
        else:
            inverse_prop = config.inverse_property if config.inverse_property else source_entity

        if config.cascade_delete:
            if config.type == "OneToMany":

                source_cascade = ', sa_relationship_kwargs={"cascade": "all, delete-orphan"}'
                target_cascade = ""
            elif config.type == "ManyToOne":
                source_cascade = ""
                target_cascade = ', sa_relationship_kwargs={"cascade": "all, delete-orphan"}'
            elif config.type == "OneToOne":

                source_cascade = ', sa_relationship_kwargs={"cascade": "all, delete-orphan"}'
                target_cascade = ""
            else:
                source_cascade = ""
                target_cascade = ""
        else:
            source_cascade = ""
            target_cascade = ""

        relation_template = {
            "OneToOne": (
                f"{property_name}: {target_class} | None = Relationship(back_populates='{inverse_prop}', uselist=False{source_cascade})",
                f"{inverse_prop}: {source_class} | None = Relationship(back_populates='{property_name}', uselist=False{target_cascade})",
            ),
            "OneToMany": (
                f"{property_name}: list['{target_class}'] = Relationship(back_populates='{inverse_prop}'{source_cascade})",
                f"{inverse_prop}: {source_class} | None = Relationship(back_populates='{property_name}'{target_cascade})",
            ),
            "ManyToOne": (
                f"{property_name}: {target_class} | None = Relationship(back_populates='{inverse_prop}'{source_cascade})",
                f"{inverse_prop}: list['{source_class}'] = Relationship(back_populates='{property_name}'{target_cascade})",
            ),
            "ManyToMany": (
                f"{property_name}: list['{target_class}'] = Relationship(back_populates='{inverse_prop}', link_model={intermediate_class}{source_cascade})",
                f"{inverse_prop}: list['{source_class}'] = Relationship(back_populates='{property_name}', link_model={intermediate_class}{target_cascade})",
            ),
        }

        source_relation = relation_template[config.type][0]
        target_relation = relation_template[config.type][1] if config.inverse_relation else None

        return source_relation, target_relation

    def _create_standard_relation(
        self,
        source_entity: str,
        target_entity: str,
        property_name: str,
        config: RelationConfig,
    ):
        source_class = ClassNameManager.snake_to_pascal(source_entity)
        target_class = ClassNameManager.snake_to_pascal(target_entity)
        source_file = os.path.join(self.entity_folder, f"{source_entity}.py")
        target_file = os.path.join(self.entity_folder, f"{target_entity}.py")

        source_relation, target_relation = self._generate_relation_code(
            source_entity,
            target_entity,
            property_name,
            source_class,
            target_class,
            config,
        )

        self._add_relation_to_file(source_file, source_relation)
        if target_relation:
            self._add_relation_to_file(target_file, target_relation)

        if config.type in ["OneToOne", "ManyToOne"]:
            self._add_class_import(source_file, target_entity, target_class)
        if config.type in ["OneToOne", "OneToMany"]:
            self._add_class_import(target_file, source_entity, source_class)

        if config.inverse_relation:
            if config.type == "OneToMany":

                foreign_key_code = (
                    f"    {source_entity}_id: int | None = Field(\n"
                    f"        foreign_key='{
                        source_entity}.id', ondelete='CASCADE', nullable=False\n"
                    f"    )\n"
                )
                self._add_field_to_file(target_file, foreign_key_code)
            elif config.type == "ManyToOne":

                foreign_key_code = (
                    f"    {target_entity}_id: int | None = Field(\n"
                    f"        foreign_key='{
                        target_entity}.id', ondelete='CASCADE', nullable=False\n"
                    f"    )\n"
                )
                self._add_field_to_file(source_file, foreign_key_code)
            elif config.type == "ManyToMany":

                pass

        self.printer.print_msg(
            f"Relation '{config.type}' created between '{source_entity}' and '{target_entity}'.",
            theme="success",
        )

        return True

    def _create_many_to_many_relation(
        self,
        source_entity: str,
        target_entity: str,
        property_name: str,
        config: RelationConfig,
    ) -> bool:
        intermediate_entity = f"{source_entity}_{target_entity}"
        self._create_intermediate_entity(intermediate_entity, source_entity, target_entity)
        self._add_many_to_many_relations(source_entity, target_entity, property_name, intermediate_entity, config)

        intermediate_class = ClassNameManager.snake_to_pascal(intermediate_entity)

        source_file = os.path.join(self.entity_folder, f"{source_entity}.py")
        target_file = os.path.join(self.entity_folder, f"{target_entity}.py")

        self._add_class_import(source_file, intermediate_entity, intermediate_class)
        self._add_class_import(target_file, intermediate_entity, intermediate_class)

        self.printer.print_msg(
            f"ManyToMany relation file '{intermediate_entity}' created between '{source_entity}' and '{target_entity}'.",
            theme="success",
        )

        return True

    def _create_intermediate_entity(self, intermediate_entity: str, source_entity: str, target_entity: str):
        intermediate_class = ClassNameManager.snake_to_pascal(intermediate_entity)
        source_class = ClassNameManager.snake_to_pascal(source_entity)
        target_class = ClassNameManager.snake_to_pascal(target_entity)
        file_path = os.path.join(
            self.entity_folder,
            f"{intermediate_entity}.py",
        )

        if not os.path.exists(file_path):
            # Correction : s'assurer que le chemin finit par un slash
            path = self.entity_folder
            if not path.endswith("/"):
                path += "/"
            self.file_creator.create_file(
                template="intermediate_entity_template.jinja2",
                path=path,
                name=intermediate_entity,
                data={
                    "intermediate_class": intermediate_class,
                    "source_entity": source_entity,
                    "target_entity": target_entity,
                    "source_class": source_class,
                    "target_class": target_class,
                },
            )

    def _add_many_to_many_relations(
        self,
        source_entity: str,
        target_entity: str,
        property_name: str,
        intermediate_entity: str,
        config: RelationConfig,
    ):
        source_class = ClassNameManager.snake_to_pascal(source_entity)
        target_class = ClassNameManager.snake_to_pascal(target_entity)
        # intermediate_class = ClassNameManager.snake_to_pascal(intermediate_entity)

        source_file = os.path.join(self.entity_folder, f"{source_entity}.py")
        target_file = os.path.join(self.entity_folder, f"{target_entity}.py")

        source_relation, target_relation = self._generate_relation_code(
            source_entity,
            target_entity,
            property_name,
            source_class,
            target_class,
            config,
        )

        self._add_relation_to_file(source_file, source_relation)
        if target_relation:
            self._add_relation_to_file(target_file, target_relation)

    def _add_relation_to_file(self, file_path: str, relation_code: str):
        with open(file_path, "a") as file:
            file.write(f"\n    {relation_code}\n")

    def _add_field_to_file(self, file_path: str, field_code: str):
        with open(file_path, "r") as file:
            lines = file.readlines()

        insertion_index = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("class "):
                insertion_index = i + 1
            elif line.strip() == "" and insertion_index > 0:
                insertion_index = i
                break

        lines.insert(insertion_index, field_code + "\n")

        with open(file_path, "w") as file:
            file.writelines(lines)

    def _add_class_import(self, file_path: str, entity_snake: str, entity_class: str):

        with open(file_path, "r") as file:
            lines = file.readlines()

        import_line = f"from src.entity.{entity_snake} import {entity_class}\n"

        if import_line not in lines:

            insertion_index = 0
            for i, line in enumerate(lines):
                if not line.startswith("from") and not line.startswith("import"):
                    insertion_index = i
                    break

            lines.insert(insertion_index, import_line)

            with open(file_path, "w") as file:
                file.writelines(lines)
