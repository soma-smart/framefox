import os

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ImportManager:
    def __init__(self, printer):
        self.printer = printer
        self.standard_imports = {
            "from sqlmodel import Field, ForeignKey, Relationship",
            "from typing import Optional, list",
            "from framefox.core.orm.abstract_entity import AbstractEntity",
        }

    def ensure_import(self, file_path: str, import_line: str) -> bool:
        """Ensures that a specific import line is present in the file"""
        with open(file_path, "r") as f:
            content = f.readlines()

        if not any(line.strip() == import_line for line in content):

            insert_pos = 0
            for idx, line in enumerate(content):
                if line.startswith("from ") or line.startswith("import "):
                    insert_pos = idx + 1

            content.insert(insert_pos, f"{import_line}\n")

            with open(file_path, "w") as f:
                f.writelines(content)

            self.printer.print_msg(f"Import added to {file_path}: {import_line}", theme="success")
            return True
        return False

    def add_import_to_entity(self, entity_name: str, import_line: str) -> bool:
        """Ajoute une ligne d'import à une entité spécifique"""
        file_path = os.path.join("src/entity", f"{entity_name}.py")
        return self.ensure_import(file_path, import_line)
