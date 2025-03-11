from typing import Any, Dict, List

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class AbstractFormType:
    """Abstract base class for form field types."""

    def __init__(self, options: Dict[str, Any] = None):
        self.options = options or {}
        self.name = None
        self.errors = []
        self.value = None

    def set_name(self, name: str) -> None:
        """Sets the name of the field associated with this type."""
        self.name = name

    def get_name(self) -> str:
        """Returns the name of the field."""
        return self.name

    def get_id(self) -> str:
        """Returns the identifier of the field."""
        return self.name

    def has_errors(self) -> bool:
        """Checks if the field has errors."""
        return len(self.errors) > 0

    def get_errors(self) -> List[str]:
        """Returns the errors of the field."""
        return self.errors

    def set_value(self, value: Any) -> None:
        """Sets the value of the field."""
        self.value = value

    def get_value(self) -> Any:
        """Returns the value of the field."""
        return self.value

    def transform_to_model(self, value: Any) -> Any:
        """Transforms the form value to a model value."""
        raise NotImplementedError(
            "This method must be implemented by subclasses"
        )

    def transform_to_view(self, value: Any) -> Any:
        """Transforms the model value to a view value."""
        raise NotImplementedError(
            "This method must be implemented by subclasses"
        )

    def get_block_prefix(self) -> str:
        """Returns the block prefix for rendering."""
        raise NotImplementedError(
            "This method must be implemented by subclasses"
        )
