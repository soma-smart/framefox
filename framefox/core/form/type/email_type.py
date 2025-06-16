import re
from typing import Any

from framefox.core.form.type.text_type import TextType

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class EmailType(TextType):
    """Type for email fields."""

    def transform_to_model(self, value: Any) -> str:
        """Transforms and validates the email."""
        email = super().transform_to_model(value)
        if email and not self._validate_email(email):
            raise ValueError("Invalid email format")
        return email

    def get_block_prefix(self) -> str:
        """Returns the block prefix for rendering."""
        return "email"

    def _validate_email(self, email: str) -> bool:
        """Validates the email format."""
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email) is not None
