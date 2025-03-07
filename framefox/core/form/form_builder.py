from typing import Any, Dict, Optional, Type

from framefox.core.form.form import Form
from framefox.core.form.form_field import FormField
from framefox.core.form.type.abstract_form_type import AbstractFormType


class FormBuilder:
    """Construit un formulaire en ajoutant des champs."""

    def __init__(self, data: Any = None, options: Dict[str, Any] = None):
        self.fields: Dict[str, FormField] = {}
        self.data = data
        self.options = options or {}

    def add(
        self,
        name: str,
        type_class: Type[AbstractFormType],
        options: Dict[str, Any] = None,
    ) -> "FormBuilder":
        """Ajoute un champ au formulaire."""
        if options is None:
            options = {}

        # Créer le type de formulaire
        form_type = type_class(options)

        # Créer le champ avec sa valeur initiale
        field = FormField(name=name, type=form_type, options=options)

        # Si des données sont fournies, initialiser avec la valeur existante
        if self.data and hasattr(self.data, name):
            value = getattr(self.data, name)
            field.value = value

        self.fields[name] = field
        return self

    def get_form(self) -> Form:
        """Crée et retourne le formulaire avec les champs définis."""
        return Form(fields=self.fields, data=self.data, options=self.options)
