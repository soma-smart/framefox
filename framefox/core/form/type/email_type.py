import re
from typing import Any

from framefox.core.form.type.text_type import TextType


class EmailType(TextType):
    """Type pour les champs d'email."""

    def transform_to_model(self, value: Any) -> str:
        """Transforme et valide l'email."""
        email = super().transform_to_model(value)
        if email and not self._validate_email(email):
            raise ValueError("Format d'email invalide")
        return email

    def get_block_prefix(self) -> str:
        """Retourne le préfixe du bloc pour le rendu."""
        return "email"

    def _validate_email(self, email: str) -> bool:
        """Valide le format de l'email."""
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email) is not None
