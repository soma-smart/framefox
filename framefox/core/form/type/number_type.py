from typing import Any, Union

from framefox.core.form.type.abstract_form_type import AbstractFormType


class NumberType(AbstractFormType):
    """Type pour les champs numériques."""

    def transform_to_model(self, value: Any) -> Union[float, int]:
        """Transforme la valeur brute en nombre."""
        if not value and value != 0:
            return 0

        try:
            # Détermine si c'est un entier ou un float
            if self.options.get("integer", True):
                return int(value)
            else:
                return float(value)
        except ValueError:
            raise ValueError(f"Valeur numérique invalide: {value}")

    def transform_to_view(self, value: Any) -> str:
        """Transforme la valeur du modèle en chaîne pour l'affichage."""
        if value is None:
            return ""
        return str(value)

    def get_block_prefix(self) -> str:
        """Retourne le préfixe du bloc pour le rendu."""
        return "number"
