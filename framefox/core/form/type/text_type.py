from typing import Any

from framefox.core.form.type.abstract_form_type import AbstractFormType

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TextType(AbstractFormType):
    """Type for text fields."""

    def transform_to_model(self, value: Any) -> str:
        """Transforms the raw value into a string."""
        if value is None:
            return ""
        return str(value)

    def transform_to_view(self, value: Any) -> str:
        """Transforms the model value into a string for display."""
        if value is None:
            return ""
        return str(value)

    def get_block_prefix(self) -> str:
        """Returns the block prefix for rendering."""
        return "text"
