from typing import Any, Dict, Optional, Type

from framefox.core.form.form import Form
from framefox.core.form.form_builder import FormBuilder
from framefox.core.form.type.form_type_interface import FormTypeInterface

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FormFactory:
    """Factory to create forms."""

    @classmethod
    def create_builder(
        cls, data: Optional[Any] = None, options: Dict[str, Any] = None
    ) -> FormBuilder:
        """Create a form builder."""
        return FormBuilder(data, options)

    @classmethod
    def create_form(
        cls,
        form_type: Type[FormTypeInterface],
        data: Optional[Any] = None,
        options: Dict[str, Any] = None,
    ) -> Form:
        """Create a form from a form type."""
        builder = cls.create_builder(data, options)
        form_instance = form_type()
        form_instance.build_form(builder)
        return builder.get_form()
