from typing import Any, Dict, List, Union

from framefox.core.form.type.abstract_form_type import AbstractFormType
from framefox.core.form.type.select_type import SelectType

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ChoiceType(AbstractFormType):
    """Type for fields selecting from predefined choices."""

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options or {})
        self.options.setdefault("choices", {})
        self.options.setdefault("multiple", False)
        self.options.setdefault("expanded", False)
        self.options.setdefault("attr", {})

    def transform_to_model(self, value: Any) -> Union[str, List[str]]:
        """Transforms the form value to a model value."""
        if not value:
            return [] if self.options.get("multiple") else None

        if self.options.get("multiple"):
            if isinstance(value, list):
                return value
            return [value]

        return value

    def transform_to_view(self, value: Any) -> Any:
        """Transforms the model value to a view value."""
        if self.options.get("multiple"):
            if value is None:
                return []
            if not isinstance(value, list):
                return [value] if value else []
            return value

        return value

    def get_block_prefix(self) -> str:
        """Returns the block prefix for rendering."""
        if self.options.get("expanded"):
            return "choice_expanded"
        return "choice"

    def render(self, options: Dict[str, Any] = None) -> str:
        """HTML rendering of the selection field."""
        select_options = self.options.copy()

        select_type = SelectType(select_options)
        select_type.name = self.name
        select_type.value = self.value
        select_type.parent = self.parent
        select_type.errors = self.errors

        return select_type.render(options)
