from typing import Any, Dict, List, Optional, Type

from framefox.core.form.type.abstract_form_type import AbstractFormType


class CollectionType(AbstractFormType):
    """Type pour les collections (listes) de valeurs."""

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options)
        self.entry_type = options.get("entry_type")
        self.allow_add = options.get("allow_add", True)
        self.allow_delete = options.get("allow_delete", True)

        # Créer une instance du type d'entrée
        if self.entry_type:
            self.entry_type_instance = self.entry_type(options.get("entry_options", {}))

    def transform_to_model(self, value: Any) -> List[Any]:
        """Transforme les valeurs brutes en liste d'éléments."""
        if not value:
            return []

        # Si la valeur est une chaîne unique, la scinder (pour les JSON arrays, CSV, etc.)
        if isinstance(value, str):
            if value.startswith("[") and value.endswith("]"):  # JSON array
                import json

                try:
                    values = json.loads(value)
                except json.JSONDecodeError:
                    values = [v.strip() for v in value.strip("[]").split(",")]
            else:
                # Considérer comme CSV
                values = [v.strip() for v in value.split(",")]
        elif not isinstance(value, list):
            values = [value]
        else:
            values = value

        # Transformer chaque élément avec le type d'entrée
        if self.entry_type:
            return [self.entry_type_instance.transform_to_model(v) for v in values]
        return values

    def transform_to_view(self, value: Any) -> List[Any]:
        """Transforme la liste d'éléments pour l'affichage."""
        if not value:
            return []

        if not isinstance(value, list):
            value = [value]

        # Transformer chaque élément pour l'affichage
        if self.entry_type:
            return [self.entry_type_instance.transform_to_view(v) for v in value]
        return value

    def get_block_prefix(self) -> str:
        """Retourne le préfixe du bloc pour le rendu."""
        return "collection"
