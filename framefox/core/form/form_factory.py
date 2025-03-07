from typing import Any, Dict, Optional, Type

from framefox.core.form.form import Form
from framefox.core.form.form_builder import FormBuilder
from framefox.core.form.type.form_type_interface import FormTypeInterface


class FormFactory:
    """Usine pour créer des formulaires."""

    @classmethod
    def create_builder(
        cls, data: Optional[Any] = None, options: Dict[str, Any] = None
    ) -> FormBuilder:
        """Crée un constructeur de formulaire."""
        return FormBuilder(data, options)

    @classmethod
    def create_form(
        cls,
        form_type: Type[FormTypeInterface],
        data: Optional[Any] = None,
        options: Dict[str, Any] = None,
    ) -> Form:
        """Crée un formulaire à partir d'un type de formulaire."""
        builder = cls.create_builder(data, options)

        # Demander au type de formulaire de construire le formulaire
        form_instance = form_type()
        form_instance.build_form(builder)

        # Récupérer le formulaire construit
        return builder.get_form()
