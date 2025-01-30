from dataclasses import dataclass
from typing import Optional, Tuple, List
import os
from framefox.terminal.common.class_name_manager import ClassNameManager


@dataclass
class RelationConfig:
    type: str
    cascade_delete: bool
    optional: bool
    inverse_relation: bool


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
            return False  # Interrompre si l'entité cible n'existe pas

        config = self._get_relation_config(
            optional, source_entity, target_entity)
        if config.type == "ManyToMany":
            return self._create_many_to_many_relation(source_entity, target_entity, property_name, config)
        return self._create_standard_relation(source_entity, target_entity, property_name, config)

    def _get_relation_config(self, optional: bool, source_entity: str, target_entity: str) -> RelationConfig:
        relation_type = self._request_relation_type(
            source_entity, target_entity)
        cascade_delete = self._request_delete_behavior()
        inverse_relation = self._request_inverse_relation()
        return RelationConfig(relation_type, cascade_delete, optional, inverse_relation)

    def _request_relation_type(self, source_entity: str, target_entity: str) -> str:
        source_class = ClassNameManager.snake_to_pascal(source_entity)
        target_class = ClassNameManager.snake_to_pascal(target_entity)

        relation_types = {
            "1": "OneToOne",
            "2": "OneToMany",
            "3": "ManyToOne",
            "4": "ManyToMany"
        }

        help_messages = {
            "1": f"One {source_class} est lié à One {target_class}",
            "2": f"One {source_class} est lié à Many {target_class}",
            "3": f"Many {source_class} sont liés à One {target_class}",
            "4": f"Many {source_class} sont liés à Many {target_class}"
        }

        self.printer.print_msg("Sélectionnez le type de relation :")
        for key, value in relation_types.items():
            self.printer.print_msg(
                f"{key}. {value}  - \"{help_messages[key]}\""
            )

        choice = self.input_manager.wait_input(
            "Entrez le numéro correspondant au type de relation :: "
        ).strip()

        if choice not in relation_types:
            self.printer.print_msg(
                "Choix invalide. Utilisation de ManyToOne par défaut.",
                theme="warning"
            )
            return "ManyToOne"

        return relation_types[choice]

    def _request_delete_behavior(self) -> bool:
        """Demande le comportement de suppression (cascade ou set null)"""
        delete_choice = self.input_manager.wait_input(
            "Quel comportement de suppression souhaitez-vous ? (cascade/set null) :"
        ).strip().lower()
        return delete_choice == "cascade"

    def _request_inverse_relation(self) -> bool:
        """Demande si une relation inverse doit être créée"""
        return self.input_manager.wait_input(
            "Voulez-vous ajouter une relation inverse ? (oui/non) :",
            choices=["oui", "non"],
            default="oui"
        ).strip().lower() == "oui"

    def _request_target_entity(self) -> Optional[str]:
        """Demande le nom de l'entité cible et vérifie son existence"""
        while True:
            target_entity = self.input_manager.wait_input(
                "Entrez le nom de l'entité cible (snake_case) :: ").strip()
            if not target_entity:
                self.printer.print_msg(
                    "Nom de l'entité cible invalide.", theme="error"
                )
                continue  # Reposer la question

            target_file = os.path.join(
                self.entity_folder, f"{target_entity}.py")
            if not os.path.isfile(target_file):
                self.printer.print_msg(
                    f"L'entité cible '{target_entity}' n'existe pas.", theme="error"
                )

                continue
            return target_entity

    def _create_standard_relation(
        self,
        source_entity: str,
        target_entity: str,
        property_name: str,
        config: RelationConfig
    ) -> bool:
        source_class = ClassNameManager.snake_to_pascal(source_entity)
        target_class = ClassNameManager.snake_to_pascal(target_entity)

        # Création des chemins de fichiers
        source_file = os.path.join(self.entity_folder, f"{source_entity}.py")
        target_file = os.path.join(self.entity_folder, f"{target_entity}.py")

        # Génération des relations
        source_relation, target_relation = self._generate_relation_code(
            source_entity, target_entity, property_name, source_class, target_class, config
        )

        # Ajout des clés étrangères
        foreign_key = self._generate_foreign_key(
            source_entity, target_entity, config
        )

        # Ajout des imports nécessaires
        self._add_necessary_imports(
            source_file, target_file, source_class, target_class, config
        )

        # Ajout des relations aux fichiers
        self._add_relation_to_file(source_file, source_relation)
        if config.inverse_relation and target_relation:
            self._add_relation_to_file(target_file, target_relation)

        # Ajout de la clé étrangère
        if config.type in ["ManyToOne", "OneToOne"]:
            self._add_relation_to_file(source_file, foreign_key)
        elif config.type == "OneToMany":
            self._add_relation_to_file(target_file, foreign_key)

        self.printer.print_msg(
            f"Relation {config.type} entre '{source_entity}' et '{
                target_entity}' ajoutée avec succès.",
            theme="success"
        )
        return True

    def _generate_relation_code(
        self,
        source_entity: str,
        target_entity: str,
        property_name: str,
        source_class: str,
        target_class: str,
        config: RelationConfig
    ) -> Tuple[str, Optional[str]]:
        cascade_option = ", cascade_delete=True" if config.cascade_delete else ""

        intermediate_class = ClassNameManager.snake_to_pascal(
            f"{source_entity}_{target_entity}")

        relation_template = {
            "OneToOne": (
                f"{property_name}: Optional['{target_class}'] = Relationship(back_populates='{
                    source_entity}', uselist=False{cascade_option})",
                f"{source_entity}: Optional['{source_class}'] = Relationship(back_populates='{
                    property_name}', uselist=False)"
            ),
            "OneToMany": (
                f"{property_name}s: List['{target_class}'] = Relationship(back_populates='{
                    source_entity}'{cascade_option})",
                f"{source_entity}: Optional['{source_class}'] = Relationship(back_populates='{
                    property_name}s')"
            ),
            "ManyToOne": (
                f"{property_name}: Optional['{target_class}'] = Relationship(back_populates='{
                    source_entity}s'{cascade_option})",
                f"{source_entity}s: List['{source_class}'] = Relationship(back_populates='{
                    property_name}')"
            ),
            "ManyToMany": (
                f"{property_name}s: List['{target_class}'] = Relationship(back_populates='{
                    source_entity}s', link_model={intermediate_class})",
                f"{source_entity}s: List['{source_class}'] = Relationship(back_populates='{
                    property_name}s', link_model={intermediate_class})"
            )
        }

        if config.type == "ManyToMany":
            source_relation = relation_template["ManyToMany"][0]
            target_relation = relation_template["ManyToMany"][1] if config.inverse_relation else None
        else:
            source_relation = relation_template[config.type][0]
            target_relation = relation_template[config.type][1] if config.inverse_relation else None

        return source_relation, target_relation

    def _generate_foreign_key(
        self,
        source_entity: str,
        target_entity: str,
        config: RelationConfig
    ) -> str:
        ondelete = "CASCADE" if config.cascade_delete else "SET NULL"
        if config.type == "ManyToOne":
            return f"    {target_entity}_id: int = Field(foreign_key='{target_entity}.id', ondelete='{ondelete}')"
        elif config.type == "OneToMany":
            return f"    {source_entity}_id: int = Field(foreign_key='{source_entity}.id', ondelete='{ondelete}')"
        else:
            return f"    {target_entity}_id: int = Field(foreign_key='{target_entity}.id', ondelete='{ondelete}')"

    def _add_necessary_imports(
        self,
        source_file: str,
        target_file: str,
        source_class: str,
        target_class: str,
        config: RelationConfig
    ):
        standard_imports = [
            "from sqlmodel import Field, ForeignKey, Relationship",
            "from typing import Optional, List"
        ]

        # Importer la classe cible si non optionnelle
        if not config.optional:
            self.import_manager.ensure_import(
                source_file,
                f"from src.entity.{target_class.lower()} import {target_class}"
            )

        # Importer la classe intermédiaire (link_model) si ManyToMany
        if config.type == "ManyToMany":
            intermediate_class = ClassNameManager.snake_to_pascal(f"{source_file.split(
                '/')[-1].split('.')[0]}_{target_file.split('/')[-1].split('.')[0]}")
            self.import_manager.ensure_import(
                source_file,
                f"from src.entity.{intermediate_class.lower()} import {
                    intermediate_class}"
            )
            self.import_manager.ensure_import(
                target_file,
                f"from src.entity.{intermediate_class.lower()} import {
                    intermediate_class}"
            )

        # Ajouter les imports standard
        for import_line in standard_imports:
            self.import_manager.ensure_import(source_file, import_line)
            if config.inverse_relation:
                self.import_manager.ensure_import(target_file, import_line)

    def _add_relation_to_file(self, file_path: str, relation_code: str):
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Trouver la position d'insertion (après la dernière propriété)
        insert_pos = next(
            (i for i in reversed(range(len(lines)))
             if lines[i].strip().startswith("#") or "Field" in lines[i] or "Relationship" in lines[i]),
            len(lines)
        ) + 1

        lines.insert(insert_pos, f"    {relation_code}\n")

        with open(file_path, 'w') as f:
            f.writelines(lines)

    def _create_many_to_many_relation(
        self,
        source_entity: str,
        target_entity: str,
        property_name: str,
        config: RelationConfig
    ) -> bool:
        intermediate_entity = f"{source_entity}_{target_entity}"
        self._create_intermediate_entity(
            intermediate_entity, source_entity, target_entity)
        self._add_many_to_many_relations(
            source_entity, target_entity, property_name, intermediate_entity, config)
        return True

    def _create_intermediate_entity(
        self,
        intermediate_entity: str,
        source_entity: str,
        target_entity: str
    ):
        intermediate_class = ClassNameManager.snake_to_pascal(
            intermediate_entity)
        properties = [
            f"{source_entity}_id: int = Field(foreign_key='{
                source_entity}.id')",
            f"{target_entity}_id: int = Field(foreign_key='{
                target_entity}.id')"
        ]
        data = {
            'class_name': intermediate_class,
            'properties': properties
        }
        self.file_creator.create_file(
            template="entity_template.jinja2",
            path=self.entity_folder,
            name=intermediate_entity,
            data=data
        )
        self.printer.print_msg(
            f"Entité intermédiaire '{intermediate_entity}' créée.",
            theme="success"
        )

    def _add_many_to_many_relations(
        self,
        source_entity: str,
        target_entity: str,
        property_name: str,
        intermediate_entity: str,
        config: RelationConfig
    ):
        source_class = ClassNameManager.snake_to_pascal(source_entity)
        target_class = ClassNameManager.snake_to_pascal(target_entity)
        intermediate_class = ClassNameManager.snake_to_pascal(
            intermediate_entity)

        source_relation = f"{property_name}s: List['{target_class}'] = Relationship(back_populates='{
            source_entity}s', link_model={intermediate_class})"
        target_relation = f"{source_entity}s: List['{source_class}'] = Relationship(back_populates='{
            property_name}s', link_model={intermediate_class})"

        source_file = os.path.join(self.entity_folder, f"{source_entity}.py")
        target_file = os.path.join(self.entity_folder, f"{target_entity}.py")

        self._add_relation_to_file(source_file, source_relation)
        self._add_relation_to_file(target_file, target_relation)

        self.printer.print_msg(
            f"Relations ManyToMany entre '{
                source_entity}' et '{target_entity}' ajoutées.",
            theme="success"
        )
