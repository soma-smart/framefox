from typing import Any, Dict, Optional, Type

from framefox.core.form.form import Form
from framefox.core.form.form_field import FormField
from framefox.core.form.type.abstract_form_type import AbstractFormType

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FormBuilder:
    """Builds a form by adding fields."""

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
        if options is None:
            options = {}

        form_type = type_class(options)
        field = FormField(name=name, type=form_type, options=options)

        if self.data and hasattr(self.data, name):
            value = getattr(self.data, name)
            field.value = value

        self.fields[name] = field
        return self

    def get_form(self) -> Form:
        """Creates and returns the form with the defined fields."""
        return Form(fields=self.fields, data=self.data, options=self.options)

    def get_initial_data(self) -> Dict[str, Any]:
        """
        Returns the initial data of the form.
        """
        if isinstance(self.data, dict):
            return self.data
        elif hasattr(self.data, '__dict__'):
            return self.data.__dict__
        return {}
