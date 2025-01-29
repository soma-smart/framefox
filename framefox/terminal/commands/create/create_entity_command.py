from typing import List, Optional
from sqlmodel import SQLModel
import os
from framefox.terminal.commands.abstract_command import AbstractCommand
from framefox.terminal.common.class_name_manager import ClassNameManager
from framefox.terminal.common.file_creator import FileCreator
from framefox.terminal.common.model_checker import ModelChecker
from framefox.terminal.common.entity_property_manager import EntityPropertyManager
from framefox.terminal.common.input_manager import InputManager


class CreateEntityCommand(AbstractCommand):
    def __init__(self):
        super().__init__("entity")
        self.entity_template = r"entity_template.jinja2"
        self.entity_intermediate_template = r"entity_intermediate_template.jinja2"
        self.repository_template = r"repository_template.jinja2"
        self.entity_path = r"src/entity"
        self.repository_path = r"src/repository"
        self.entity_property_manager = EntityPropertyManager()

    def execute(self, name: str = None):
        """
        Crée ou modifie l'entité et le repository associé, et demande les propriétés à ajouter à l'entité.

        Args:
            name (str, optional): Le nom de l'entité en snake_case. Defaults to None.
        """
        if name is None:
            name = InputManager().wait_input("Entity name")
            if name == "":
                return

        if not ClassNameManager.is_snake_case(name):
            self.printer.print_msg(
                "Nom invalide. Doit être en snake_case.",
                theme="error",
                linebefore=True,
                newline=True,
            )
            return

        does_entity_exist = ModelChecker().check_entity_and_repository(name)
        if not does_entity_exist:
            self.create_entity(name)
            self.create_repository(name)
        else:
            self.printer.print_msg(
                f"L'entité '{name}' existe déjà. Modification en cours...",
                theme="info"
            )

        self.request_n_add_property_to_entity(name)

        self.printer.print_full_text(
            "Ensuite, procédez avec [bold green]framefox orm database create_migration[/bold green]",
            newline=True,
        )

    def create_entity(self, name: str):
        class_name = ClassNameManager.snake_to_pascal(name)
        data = {
            "class_name": class_name,
        }
        file_path = FileCreator().create_file(
            self.entity_template, self.entity_path, name, data
        )
        self.printer.print_full_text(
            f"[bold green]Entité '{
                class_name}' créée avec succès:[/bold green] {file_path}",
            newline=True,
        )

    def create_repository(self, name: str):
        class_name = ClassNameManager.snake_to_pascal(name)
        repository_class_name = f"{class_name}Repository"
        data = {
            "entity_class_name": class_name,
            "repository_class_name": repository_class_name,
            "snake_case_name": name,
        }
        file_path = FileCreator().create_file(
            self.repository_template, self.repository_path, f"{
                name}_repository", data
        )
        self.printer.print_full_text(
            f"[bold green]Repository '{
                repository_class_name}' créée avec succès:[/bold green] {file_path}",
            newline=True,
        )

    def request_n_add_property_to_entity(self, name: str):
        while True:
            result = self.entity_property_manager.request_and_add_property(
                entity_name=name)
            if not result:
                break
            if isinstance(result, tuple) and result[0] == "relation":
                _, entity_name, property_name = result
                self.handle_relation(entity_name, property_name)

    def handle_relation(self, entity_name: str, property_name: str):
        target_entity = self.select_target_entity()

        if not ModelChecker().check_entity_and_repository(target_entity, verbose=True):
            self.printer.print_msg(
                f"L'entité cible '{
                    target_entity}' n'existe pas. Veuillez la créer d'abord.",
                theme="error"
            )
            return

        relation_type = self.select_relation_type()
        self.add_relation_to_entities(
            entity_name, target_entity, relation_type, property_name
        )

    def select_relation_type(self) -> str:
        relation_types = ["OneToOne", "OneToMany", "ManyToOne", "ManyToMany"]
        self.printer.print_msg(
            "Sélectionnez le type de relation :",
            theme="bold_normal"
        )
        for idx, r_type in enumerate(relation_types, start=1):
            self.printer.print_msg(f"{idx}. {r_type}", theme="info")
        while True:
            choice = InputManager().wait_input(
                "Entrez le numéro correspondant au type de relation :").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(relation_types):
                return relation_types[int(choice) - 1]
            else:
                self.printer.print_msg(
                    "Choix invalide. Veuillez réessayer.", theme="error"
                )

    def select_target_entity(self) -> str:
        target = InputManager().wait_input(
            "Entrez le nom de l'entité cible (snake_case) :").strip()
        return target

    def add_relation_to_entities(self, entity_name: str, target_entity: str, relation_type: str, property_name: str):
        # Convertir les noms en PascalCase
        entity_class = ClassNameManager.snake_to_pascal(entity_name)
        target_class = ClassNameManager.snake_to_pascal(target_entity)

        if relation_type == "ManyToMany":
            # Créer le nom de l'entité intermédiaire
            intermediate_entity_name = f"{entity_name}_{target_entity}"
            intermediate_class = ClassNameManager.snake_to_pascal(
                intermediate_entity_name)

            # Créer l'entité intermédiaire avec les clés étrangères
            self.create_intermediate_entity(
                intermediate_entity_name, entity_class, target_class, property_name)

            # Définir les relations entre les entités originales et l'entité intermédiaire
            entity_relation = f"{property_name}s: List['{target_class}'] = Relationship(back_populates='{
                entity_name}s', link_model={intermediate_class})"
            target_relation = f"{entity_name}s: List['{entity_class}'] = Relationship(back_populates='{
                target_entity}s', link_model={intermediate_class})"

            # Ajouter les relations aux fichiers des entités
            entity_file_path = os.path.join("src/entity", f"{entity_name}.py")
            target_file_path = os.path.join(
                "src/entity", f"{target_entity}.py")
            self.append_relation_to_file(entity_file_path, entity_relation)
            self.append_relation_to_file(target_file_path, target_relation)

            # Ajouter les imports nécessaires
            self.ensure_intermediate_import(
                entity_file_path, intermediate_entity_name)
            self.ensure_intermediate_import(
                target_file_path, intermediate_entity_name)

            self.printer.print_msg(
                f"Relation {relation_type} entre '{entity_name}' et '{
                    target_entity}' ajoutée avec succès via '{intermediate_entity_name}'.",
                theme="success"
            )
        else:
            # Gérer les autres types de relations
            if relation_type == "OneToOne":
                entity_relation = f"{property_name}: Optional['{
                    target_class}'] = Relationship(back_populates='{entity_name}', uselist=False)"
                target_relation = f"{entity_name}: Optional['{
                    entity_class}'] = Relationship(back_populates='{property_name}', uselist=False)"
            elif relation_type == "OneToMany":
                entity_relation = f"{property_name}s: List['{
                    target_class}'] = Relationship(back_populates='{entity_name}')"
                target_relation = f"{entity_name}: Optional['{
                    entity_class}'] = Relationship(back_populates='{property_name}s')"
            elif relation_type == "ManyToOne":
                entity_relation = f"{property_name}: Optional['{
                    target_class}'] = Relationship(back_populates='{entity_name}s')"
                target_relation = f"{entity_name}s: List['{
                    entity_class}'] = Relationship(back_populates='{property_name}')"

            # Assurer les imports nécessaires
            entity_file_path = os.path.join("src/entity", f"{entity_name}.py")
            target_file_path = os.path.join(
                "src/entity", f"{target_entity}.py")
            self.ensure_imports(entity_file_path)
            self.ensure_imports(target_file_path)

            # Ajouter les relations aux fichiers des entités
            self.append_relation_to_file(entity_file_path, entity_relation)
            self.append_relation_to_file(target_file_path, target_relation)

            self.printer.print_msg(
                f"Relation {relation_type} entre '{entity_name}' et '{
                    target_entity}' ajoutée avec succès.",
                theme="success"
            )

    def create_intermediate_entity(self, intermediate_name: str, entity_class: str, target_class: str, property_name: str):
        """
        Crée une entité intermédiaire avec les clés étrangères vers les deux entités liées.
        """
        class_name = ClassNameManager.snake_to_pascal(intermediate_name)
        data = {
            "class_name": class_name,
            "entity_class": entity_class,
            "target_class": target_class,
            "property_name": property_name
        }
        intermediate_path = os.path.join(
            "src/entity", f"{intermediate_name}.py")

        # Vérifiez si le fichier intermédiaire existe déjà
        if not os.path.exists(intermediate_path):
            FileCreator().create_file(
                self.entity_intermediate_template, self.entity_path, intermediate_name, data
            )
            self.printer.print_full_text(
                f"[bold green]Entité intermédiaire '{
                    intermediate_name}' créée avec succès dans {intermediate_path}[/bold green]",
                newline=True,
            )
        else:
            self.printer.print_msg(
                f"L'entité intermédiaire '{
                    intermediate_name}' existe déjà dans {intermediate_path}.",
                theme="info"
            )

    def append_relation_to_file(self, file_path: str, relation_line: str):
        with open(file_path, 'a') as f:
            f.write(f"\n    {relation_line}\n")

    def ensure_intermediate_import(self, file_path: str, intermediate_class_name: str):
        """
        Ajoute l'import de la classe intermédiaire dans le fichier spécifié si ce n'est pas déjà fait.
        """
        with open(file_path, 'r') as f:
            lines = f.readlines()
        intermediate_class = ClassNameManager.snake_to_pascal(
            intermediate_class_name)
        import_line = f"from src.entity.{intermediate_class_name} import {
            intermediate_class}\n"

        if import_line not in lines:
            # Trouver l'endroit où ajouter l'import (après les autres importations)
            insert_pos = 0
            for idx, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    insert_pos = idx + 1
            lines.insert(insert_pos, import_line)

            with open(file_path, 'w') as f:
                f.writelines(lines)

            self.printer.print_msg(
                f"Import de '{intermediate_class}' ajouté dans '{file_path}'.",
                theme="success"
            )
        else:
            self.printer.print_msg(
                f"L'import de '{intermediate_class}' existe déjà dans '{
                    file_path}'.",
                theme="info"
            )

    def add_standard_property(self, entity_name: str, property_name: str, property_type: str):
        property_line = f"    {property_name}: {
            self.map_type(property_type)} = Field(nullable=False)"
        entity_file = os.path.join("src/entity", f"{entity_name}.py")
        self.append_relation_to_file(entity_file, property_line)
        self.printer.print_msg(
            f"Propriété '{property_name}' de type '{
                property_type}' ajoutée à l'entité '{entity_name}'.",
            theme="success"
        )

    def map_type(self, property_type: str) -> str:
        type_mapping = {
            "string": "str",
            "integer": "int",
            "float": "float",
            "boolean": "bool",
            "list": "List",
            "tuple": "Tuple",
            "dict": "Dict",
            "date": "datetime",
        }
        return type_mapping.get(property_type.lower(), "str")

    @staticmethod
    def create_entity_class_name(name: str) -> str:
        return ClassNameManager.snake_to_pascal(name)

    @staticmethod
    def create_repository_class_name(name: str) -> str:
        return f"{ClassNameManager.snake_to_pascal(name)}Repository"
