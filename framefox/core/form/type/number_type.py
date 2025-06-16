from typing import Any, Union

from framefox.core.form.type.abstract_form_type import AbstractFormType

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class NumberType(AbstractFormType):
    """Type for numeric fields."""

    def transform_to_model(self, value: Any) -> Union[float, int]:
        """Transforms the raw value into a number."""
        if not value and value != 0:
            return 0

        try:
            if self.options.get("integer", True):
                return int(value)
            else:
                return float(value)
        except ValueError:
            raise ValueError(f"Invalid numeric value: {value}")

    def transform_to_view(self, value: Any) -> str:
        """Transforms the model value into a string for display."""
        if value is None:
            return ""
        return str(value)

    def get_block_prefix(self) -> str:
        """Returns the block prefix for rendering."""
        return "number"
