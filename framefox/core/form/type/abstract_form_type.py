from typing import Any, Dict, List


class AbstractFormType:
    """Classe de base abstraite pour les types de champs de formulaire."""

    def __init__(self, options: Dict[str, Any] = None):
        self.options = options or {}
        self.name = None
        self.errors = []
        self.value = None

    def set_name(self, name: str) -> None:
        """Définit le nom du champ associé à ce type."""
        self.name = name

    def get_name(self) -> str:
        """Retourne le nom du champ."""
        return self.name

    def get_id(self) -> str:
        """Retourne l'identifiant du champ."""
        return self.name

    def has_errors(self) -> bool:
        """Vérifie si le champ a des erreurs."""
        return len(self.errors) > 0

    def get_errors(self) -> List[str]:
        """Retourne les erreurs du champ."""
        return self.errors

    def set_value(self, value: Any) -> None:
        """Définit la valeur du champ."""
        self.value = value

    def get_value(self) -> Any:
        """Retourne la valeur du champ."""
        return self.value

    def transform_to_model(self, value: Any) -> Any:
        """Transforme la valeur du formulaire en valeur pour le modèle."""
        raise NotImplementedError(
            "Cette méthode doit être implémentée par les sous-classes"
        )

    def transform_to_view(self, value: Any) -> Any:
        """Transforme la valeur du modèle en valeur pour l'affichage."""
        raise NotImplementedError(
            "Cette méthode doit être implémentée par les sous-classes"
        )

    def get_block_prefix(self) -> str:
        """Retourne le préfixe du bloc pour le rendu."""
        raise NotImplementedError(
            "Cette méthode doit être implémentée par les sous-classes"
        )
