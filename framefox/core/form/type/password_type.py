from typing import Any

from framefox.core.form.type.text_type import TextType


class PasswordType(TextType):
    """Type pour les champs de mot de passe."""

    def get_block_prefix(self) -> str:
        """Retourne le préfixe du bloc pour le rendu."""
        return "password"
