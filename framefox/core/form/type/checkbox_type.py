from typing import Any

from framefox.core.form.type.abstract_form_type import AbstractFormType

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class CheckboxType(AbstractFormType):
    """Type for checkbox fields."""

    def transform_to_model(self, value: Any) -> bool:
        """Transforms the raw value into a boolean."""
        if value is None:
            return False
        return value.lower() in ("true", "on", "yes", "1", "y")

    def transform_to_view(self, value: Any) -> bool:
        """Transforms the model value into a boolean for display."""
        if value is None:
            return False
        return bool(value)

    def get_block_prefix(self) -> str:
        """Returns the block prefix for rendering."""
        return "checkbox"
