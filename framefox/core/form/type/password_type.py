from framefox.core.form.type.text_type import TextType

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class PasswordType(TextType):
    """Type for password fields."""

    def get_block_prefix(self) -> str:
        """Returns the block prefix for rendering."""
        return "password"
