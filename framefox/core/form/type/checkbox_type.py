from typing import Any

from framefox.core.form.type.abstract_form_type import AbstractFormType


class CheckboxType(AbstractFormType):
    """Type pour les champs à cocher."""

    def transform_to_model(self, value: Any) -> bool:
        """Transforme la valeur brute en booléen."""
        if value is None:
            return False
        return value.lower() in ("true", "on", "yes", "1", "y")

    def transform_to_view(self, value: Any) -> bool:
        """Transforme la valeur du modèle en booléen pour l'affichage."""
        if value is None:
            return False
        return bool(value)

    def get_block_prefix(self) -> str:
        """Retourne le préfixe du bloc pour le rendu."""
        return "checkbox"
