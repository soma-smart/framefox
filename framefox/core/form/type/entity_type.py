from typing import Any, Dict

from framefox.core.form.type.abstract_form_type import AbstractFormType


"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class EntityType(AbstractFormType):
    """Type for fields that represent entity relationships."""

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options or {})
        self.options.setdefault("class", None)
        self.options.setdefault("multiple", False)
        self.options.setdefault("choice_label", "id")

        self._repository = None

    def get_repository(self):
        """Gets the repository for the target entity."""
        if self._repository is None:
            entity_class = self.options.get("class")
            if entity_class:
                from framefox.core.di.service_container import ServiceContainer

                container = ServiceContainer()
                entity_name = entity_class.lower()
                repo_class = f"{entity_name}_repository"
                try:
                    import importlib

                    module = importlib.import_module(
                        f"src.repository.{repo_class}")
                    repo_class_name = f"{entity_class}Repository"
                    repository_class = getattr(module, repo_class_name)
                    self._repository = repository_class()
                except (ImportError, AttributeError) as e:
                    print(
                        f"Error loading repository for {entity_class}: {str(e)}")
        return self._repository

    def get_choices(self) -> Dict[str, str]:
        """Retrieves the available choices for this entity."""
        repository = self.get_repository()
        choices = {}

        if repository:
            items = repository.find_all()
            choice_label = self.options.get("choice_label")
            show_id = self.options.get("show_id", True)

            for item in items:

                value = getattr(item, "id", None)
                if hasattr(item, choice_label):
                    label = getattr(item, choice_label)
                elif hasattr(item, "name"):
                    label = getattr(item, "name")
                elif hasattr(item, "title"):
                    label = getattr(item, "title")
                else:
                    label = f"ID: {value}"

                if show_id:
                    choices[value] = f"{value} - {label}"
                else:
                    choices[value] = f"{label}"

        return choices

    def transform_to_model(self, value: Any) -> Any:
        """Transforms the form value into an entity or list of entities."""
        if not value:
            return [] if self.options.get("multiple") else None

        repository = self.get_repository()
        if not repository:
            return value

        if self.options.get("multiple"):
            if isinstance(value, list):
                entities = []
                for id in value:
                    if id:
                        entity = repository.find({"id": int(id)})
                        if entity:
                            entities.append(entity)
                return entities
            entity = repository.find({"id": int(value)}) if value else None
            return [entity] if entity else []
        else:
            return repository.find({"id": int(value)}) if value else None

    def transform_to_view(self, value: Any) -> Any:
        """Transforms the entity or list of entities into form value(s)."""
        if not value:
            return [] if self.options.get("multiple") else None

        if self.options.get("multiple"):
            if not isinstance(value, list):
                value = [value] if value else []
            return [getattr(item, "id") for item in value if item is not None]
        else:
            return getattr(value, "id", None)

    def get_block_prefix(self) -> str:
        """Returns the block prefix for rendering."""
        return "entity"

    def render(self, options: Dict[str, Any] = None) -> str:
        """HTML rendering of the entity field (delegation to SelectType)."""
        options = options or {}

        select_options = self.options.copy()
        select_options["choices"] = self.get_choices()

        if self.options.get("multiple", False):
            select_options["multiple"] = True

        from framefox.core.form.type.select_type import SelectType

        select_type = SelectType(select_options)
        select_type.name = self.name

        return select_type.render(options)
