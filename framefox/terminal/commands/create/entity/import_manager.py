from typing import List, Set
import os


class ImportManager:
    def __init__(self, printer):
        self.printer = printer
        self.standard_imports = {
            "from sqlmodel import Field, ForeignKey, Relationship",
            "from typing import Optional, list",
            "from framefox.core.orm.abstract_entity import AbstractEntity"
        }

    def ensure_import(self, file_path: str, import_line: str) -> bool:
        """Assure qu'une ligne d'import spécifique est présente dans le fichier"""
        with open(file_path, 'r') as f:
            content = f.readlines()

        if not any(line.strip() == import_line for line in content):
            # Trouver la position d'insertion (après le dernier import)
            insert_pos = 0
            for idx, line in enumerate(content):
                if line.startswith("from ") or line.startswith("import "):
                    insert_pos = idx + 1

            content.insert(insert_pos, f"{import_line}\n")

            with open(file_path, 'w') as f:
                f.writelines(content)

            self.printer.print_msg(
                f"Import ajouté dans {file_path}: {import_line}",
                theme="success"
            )
            return True
        return False
