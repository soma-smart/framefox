from abc import ABC, abstractmethod
from typing import Any, Dict

from framefox.core.form.form_builder import FormBuilder


class FormTypeInterface(ABC):
    """Interface pour définir des types de formulaire."""

    @abstractmethod
    def build_form(self, builder: FormBuilder) -> None:
        """
        Configure le formulaire avec le builder.

        Cette méthode est appelée pour définir les champs du formulaire.
        """
        pass

    def get_options(self) -> Dict[str, Any]:
        """
        Retourne les options par défaut pour le formulaire.
        """
        return {}
