from typing import Any, Dict, List, Type

from framefox.core.di.service_container import ServiceContainer
from framefox.core.form.type.abstract_form_type import AbstractFormType
from framefox.core.form.type.select_type import SelectType


class EntityType(AbstractFormType):
    """Type pour les champs qui représentent des relations d'entité."""

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options or {})
        self.options.setdefault("class", None)
        self.options.setdefault("multiple", False)
        self.options.setdefault("choice_label", "id")

        # Initialiser le repository
        self._repository = None

    def get_repository(self):
        """Obtient le repository pour l'entité cible."""
        if self._repository is None:
            entity_class = self.options.get("class")
            if entity_class:
                # Trouver le repository correspondant à l'entité
                from framefox.core.di.service_container import ServiceContainer

                container = ServiceContainer()
                # Utiliser la convention de nommage pour trouver le repository
                entity_name = entity_class.lower()
                repo_class = f"{entity_name}_repository"
                try:
                    import importlib

                    module = importlib.import_module(f"src.repository.{repo_class}")
                    repo_class_name = f"{entity_class}Repository"
                    repository_class = getattr(module, repo_class_name)
                    self._repository = repository_class()
                except (ImportError, AttributeError) as e:
                    print(f"Error loading repository for {entity_class}: {str(e)}")
        return self._repository

    def get_choices(self) -> Dict[str, str]:
        """Récupère les choix disponibles pour cette entité."""
        repository = self.get_repository()
        choices = {}

        if repository:
            items = repository.find_all()
            choice_label = self.options.get("choice_label")
            show_id = self.options.get("show_id", True)

            for item in items:
                # La valeur est toujours l'ID
                value = getattr(item, "id", None)

                # L'étiquette peut être configurée
                if hasattr(item, choice_label):
                    label = getattr(item, choice_label)
                elif hasattr(item, "name"):
                    label = getattr(item, "name")
                elif hasattr(item, "title"):
                    label = getattr(item, "title")
                else:
                    label = f"ID: {value}"

                # Format conditionnel selon l'option show_id_in_label
                if show_id:
                    choices[value] = f"{value} - {label}"
                else:
                    choices[value] = f"{label}"

        return choices

    def transform_to_model(self, value: Any) -> Any:
        """Transforme la valeur du formulaire en entité ou liste d'entités."""
        if not value:
            return [] if self.options.get("multiple") else None

        repository = self.get_repository()
        if not repository:
            return value

        if self.options.get("multiple"):
            # Pour les relations multiple, value est une liste d'IDs
            if isinstance(value, list):
                entities = []
                for id in value:
                    if id:  # Ignorer les valeurs vides
                        entity = repository.find({"id": int(id)})
                        if entity:
                            entities.append(entity)
                return entities
            # Si c'est une seule valeur mais devrait être multiple
            entity = repository.find({"id": int(value)}) if value else None
            return [entity] if entity else []
        else:
            # Pour les relations simples, value est un ID unique
            return repository.find({"id": int(value)}) if value else None

    def transform_to_view(self, value: Any) -> Any:
        """Transforme l'entité ou liste d'entités en valeur(s) pour le formulaire."""
        if not value:
            return [] if self.options.get("multiple") else None

        if self.options.get("multiple"):
            # Pour les relations multiple, retourner une liste d'IDs
            if not isinstance(value, list):
                value = [value] if value else []
            return [getattr(item, "id") for item in value if item is not None]
        else:
            # Pour les relations simples, retourner l'ID
            return getattr(value, "id", None)

    def get_block_prefix(self) -> str:
        """Retourne le préfixe du bloc pour le rendu."""
        return "entity"

    def render(self, options: Dict[str, Any] = None) -> str:
        """Rendu HTML du champ entité (délégation à SelectType)."""
        options = options or {}

        # Créer un SelectType pour faire le rendu
        select_options = self.options.copy()
        select_options["choices"] = self.get_choices()

        # S'assurer que l'option multiple est bien transmise
        if self.options.get("multiple", False):
            select_options["multiple"] = True

        # Créer une instance de SelectType
        from framefox.core.form.type.select_type import SelectType

        select_type = SelectType(select_options)
        select_type.name = self.name  # Important: transférer le nom

        # Déléguer le rendu
        return select_type.render(options)
