import inspect
import re
from typing import Any, Dict, List, Type

from sqlmodel import SQLModel

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: LEUROND Raphael
Github: https://github.com/Vasulvius
"""


class SQLModelInspector:
    """
    A specialized inspector for SQLModel entities that:
    1. Avoids initializing the full SQLAlchemy mapper
    2. Directly analyzes source code to detect relationships
    """

    @staticmethod
    def get_entity_properties(entity_class: Type[SQLModel]) -> List[Dict[str, Any]]:
        """
        Extracts properties from a SQLModel class without fully initializing the mapper.
        """
        properties = []
        foreign_keys = []
        relations = {}

        for name, prop_type in entity_class.__annotations__.items():
            if name.endswith("_id") and "id" != name:
                foreign_keys.append(name)
                continue

            try:
                class_source = inspect.getsource(entity_class)
                pattern = rf"{name}\s*:\s*.*=\s*Relationship\("
                if re.search(pattern, class_source, re.MULTILINE):
                    related_fk = name + "_id"
                    relations[related_fk] = name
            except Exception:
                pass

        for name, prop_type in entity_class.__annotations__.items():
            if name.startswith("_") or name == "id":
                continue

            if name in foreign_keys and name in relations:
                continue

            type_str = str(prop_type)
            html_type = "text"
            widget_type = "input"
            is_relation = False
            relation_type = None
            target_entity = None
            field_options = {}
            required = False
            python_type = type_str

            try:
                class_source = inspect.getsource(entity_class)

                pattern = rf"{name}\s*:\s*.*=\s*Relationship\("
                if re.search(pattern, class_source, re.MULTILINE):
                    is_relation = True

                    is_many = "list[" in type_str.lower() or "List[" in type_str
                    relation_type = "many" if is_many else "one"

                    if "'" in type_str:
                        match = re.search(r"'([^']+)'", type_str)
                        if match:
                            target_entity = match.group(1).split(".")[-1]
                    elif '"' in type_str:
                        match = re.search(r'"([^"]+)"', type_str)
                        if match:
                            target_entity = match.group(1).split(".")[-1]

                    if not target_entity or target_entity == "None":
                        rel_match = re.search(rf"{name}\s*:\s*(.*?)\s*=\s*Relationship", class_source)
                        if rel_match:
                            type_annotation = rel_match.group(1).strip()

                            if "list[" in type_annotation.lower():
                                list_match = re.search(r"list\[(.*?)\]", type_annotation, re.IGNORECASE)
                                if list_match:
                                    inner_type = list_match.group(1).strip()

                                    if "|" in inner_type:
                                        parts = inner_type.split("|")
                                        for part in parts:
                                            part = part.strip()
                                            if part != "None" and part != "'None'" and part != '"None"':
                                                inner_type = part
                                                break

                                    inner_type = inner_type.strip("'\"")
                                    target_entity = inner_type.split(".")[-1]

                            elif "|" in type_annotation:
                                parts = type_annotation.split("|")
                                for part in parts:
                                    part = part.strip()
                                    if part != "None" and part != "'None'" and part != '"None"':
                                        target_entity = part.split(".")[-1]
                                        break

                            elif type_annotation != "None":
                                target_entity = type_annotation.split(".")[-1]

                    if not target_entity or target_entity == "None":
                        if is_many:
                            list_match = re.search(r"list\[(.*?)\]", type_str, re.IGNORECASE)
                            if list_match:
                                entity_type = list_match.group(1).strip("'\" ")
                                if entity_type and entity_type != "None":
                                    target_entity = entity_type.split(".")[-1]

                    if not target_entity or target_entity == "None":
                        target_entity = "".join(word.capitalize() for word in name.split("_"))

                    if target_entity:
                        target_entity = target_entity.strip("'\" ")

                    html_type = "select"
                    widget_type = "select_multiple" if is_many else "select"

            except Exception:
                pass

            if not is_relation:
                if "datetime.datetime" in type_str:
                    html_type = "datetime-local"
                    widget_type = "datetime"
                    python_type = "datetime.datetime"
                elif "datetime" in type_str and "<class 'datetime." in type_str:
                    html_type = "datetime-local"
                    widget_type = "datetime"
                    python_type = "datetime.datetime"
                elif "date" in type_str and not "datetime" in type_str:
                    html_type = "date"
                    widget_type = "datetime"
                    python_type = "datetime.date"
                elif "int" in type_str:
                    html_type = "number"
                    python_type = "int"
                elif "float" in type_str or "decimal" in type_str:
                    html_type = "number"
                    field_options["step"] = "0.01"
                    python_type = "float"
                elif "bool" in type_str:
                    html_type = "checkbox"
                    widget_type = "checkbox"
                    python_type = "bool"
                elif "list[str]" in type_str or "List[str]" in type_str:
                    widget_type = "textarea"
                    html_type = "textarea"
                    field_options["rows"] = 3
                    python_type = "list[str]"

                if "email" in name.lower():
                    html_type = "email"
                elif "password" in name.lower():
                    html_type = "password"
                elif "url" in name.lower():
                    html_type = "url"

            if hasattr(entity_class, name):
                attr_value = getattr(entity_class, name)
                attr_str = str(attr_value)
                required = "nullable=False" in attr_str

            properties.append(
                {
                    "name": name,
                    "type": type_str,
                    "html_type": html_type,
                    "widget_type": widget_type,
                    "is_relation": is_relation,
                    "relation_type": relation_type,
                    "target_entity": target_entity,
                    "field_options": field_options,
                    "required": required,
                    "python_type": python_type,
                }
            )

        return properties
