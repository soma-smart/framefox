from typing import Any, Dict, Optional

from framefox.core.form.type.abstract_form_type import AbstractFormType


class TextType(AbstractFormType):
    """Type pour les champs de texte."""

    def transform_to_model(self, value: Any) -> str:
        """Transforme la valeur brute en chaîne de caractères."""
        if value is None:
            return ""
        return str(value)

    def transform_to_view(self, value: Any) -> str:
        """Transforme la valeur du modèle en chaîne pour l'affichage."""
        if value is None:
            return ""
        return str(value)

    def get_block_prefix(self) -> str:
        """Retourne le préfixe du bloc pour le rendu."""
        return "text"
