import inspect
import re
from typing import Any, Dict, List, Type

from sqlmodel import SQLModel


class SQLModelInspector:
    """
    Un inspecteur spécialisé pour les entités SQLModel qui:
    1. Évite d'initialiser le mapper SQLAlchemy complet
    2. Analyse directement le code source pour détecter les relations
    """

    @staticmethod
    def get_entity_properties(entity_class: Type[SQLModel]) -> List[Dict[str, Any]]:
        """
        Extrait les propriétés d'une classe SQLModel sans initialiser complètement le mapper.
        """
        properties = []
        foreign_keys = []
        relations = {}

        # 1. D'abord, identifier toutes les relations et clés étrangères
        for name, prop_type in entity_class.__annotations__.items():
            if name.endswith("_id") and "id" != name:
                foreign_keys.append(name)
                continue

            # Vérifier si c'est une relation
            try:
                class_source = inspect.getsource(entity_class)
                pattern = rf"{name}\s*:\s*.*=\s*Relationship\("
                if re.search(pattern, class_source, re.MULTILINE):
                    # Trouver la clé étrangère correspondante (name + '_id')
                    related_fk = name + "_id"
                    relations[related_fk] = name
            except Exception:
                pass

        # 2. Maintenant, traiter les propriétés en excluant les clés étrangères qui ont une relation
        for name, prop_type in entity_class.__annotations__.items():
            # Ignorer les spéciaux/id
            if name.startswith("_") or name == "id":
                continue

            # Ignorer les clés étrangères qui ont une relation associée
            if name in foreign_keys and name in relations:
                continue

            # Valeurs par défaut
            type_str = str(prop_type)
            html_type = "text"
            widget_type = "input"
            is_relation = False
            relation_type = None
            target_entity = None
            field_options = {}
            required = False
            python_type = type_str  # Conserver le type Python original

            # 2. Vérifier si c'est une relation
            try:
                # Analyser le code source de la classe pour détecter les relations
                class_source = inspect.getsource(entity_class)

                # Chercher des lignes contenant le nom de l'attribut et "Relationship"
                pattern = rf"{name}\s*:\s*.*=\s*Relationship\("
                if re.search(pattern, class_source, re.MULTILINE):
                    is_relation = True

                    # Déterminer si c'est une relation many
                    is_many = "list[" in type_str.lower() or "List[" in type_str
                    relation_type = "many" if is_many else "one"

                    # Extraire l'entité cible - Méthodes multiples pour plus de robustesse

                    # 1. Chercher dans l'annotation de type pour les guillemets
                    if "'" in type_str:
                        match = re.search(r"'([^']+)'", type_str)
                        if match:
                            target_entity = match.group(1).split(".")[-1]
                    elif '"' in type_str:
                        match = re.search(r'"([^"]+)"', type_str)
                        if match:
                            target_entity = match.group(1).split(".")[-1]

                    # 2. Chercher dans le code source pour la classe référencée
                    if not target_entity or target_entity == "None":
                        rel_match = re.search(
                            rf"{name}\s*:\s*(.*?)\s*=\s*Relationship", class_source
                        )
                        if rel_match:
                            type_annotation = rel_match.group(1).strip()

                            # Pour les listes, extraire le type générique entre crochets
                            if "list[" in type_annotation.lower():
                                list_match = re.search(
                                    r"list\[(.*?)\]", type_annotation, re.IGNORECASE
                                )
                                if list_match:
                                    inner_type = list_match.group(1).strip()

                                    # Gérer les types union dans la liste
                                    if "|" in inner_type:
                                        parts = inner_type.split("|")
                                        # Prendre le premier type non-None
                                        for part in parts:
                                            part = part.strip()
                                            if (
                                                part != "None"
                                                and part != "'None'"
                                                and part != '"None"'
                                            ):
                                                inner_type = part
                                                break

                                    # Extraire le nom simple de la classe
                                    inner_type = inner_type.strip("'\"")
                                    target_entity = inner_type.split(".")[-1]

                            # Pour les types union (avec |)
                            elif "|" in type_annotation:
                                parts = type_annotation.split("|")
                                # Prendre le premier type non-None
                                for part in parts:
                                    part = part.strip()
                                    if (
                                        part != "None"
                                        and part != "'None'"
                                        and part != '"None"'
                                    ):
                                        target_entity = part.split(".")[-1]
                                        break

                            # Pour les types simples
                            elif type_annotation != "None":
                                target_entity = type_annotation.split(".")[-1]

                    # 3. Si toujours pas de cible valide, essayer avec les génériques de liste
                    if not target_entity or target_entity == "None":
                        if is_many:
                            list_match = re.search(
                                r"list\[(.*?)\]", type_str, re.IGNORECASE
                            )
                            if list_match:
                                entity_type = list_match.group(1).strip("'\" ")
                                if entity_type and entity_type != "None":
                                    target_entity = entity_type.split(".")[-1]

                    # 4. En dernier recours, déduire du nom de la relation
                    if not target_entity or target_entity == "None":
                        # Convertir le nom de propriété en PascalCase pour obtenir le nom de la classe probable
                        target_entity = "".join(
                            word.capitalize() for word in name.split("_")
                        )

                    # Enlever les quotes et nettoyer
                    if target_entity:
                        target_entity = target_entity.strip("'\" ")

                    # Widget adapté à la relation
                    html_type = "select"
                    widget_type = "select_multiple" if is_many else "select"

            except Exception:
                # En cas d'erreur, continuer avec les valeurs par défaut
                pass

            # 3. Si ce n'est pas une relation, déterminer le type approprié
            if not is_relation:
                # Détection spécifique des types datetime
                if "datetime.datetime" in type_str:
                    html_type = "datetime-local"
                    widget_type = "datetime"  # Important: définir le widget_type
                    python_type = "datetime.datetime"
                # Vérifie aussi le module datetime importé directement
                elif "datetime" in type_str and "<class 'datetime." in type_str:
                    html_type = "datetime-local"
                    widget_type = "datetime"
                    python_type = "datetime.datetime"
                elif "date" in type_str and not "datetime" in type_str:
                    html_type = "date"
                    widget_type = "datetime"
                    python_type = "datetime.date"
                # Autres types standards
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

                # Types spéciaux basés sur le nom
                if "email" in name.lower():
                    html_type = "email"
                elif "password" in name.lower():
                    html_type = "password"
                elif "url" in name.lower():
                    html_type = "url"

            # 4. Déterminer si le champ est requis
            # Vérifier si le champ a un attribut Field/Column avec nullable=False
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
