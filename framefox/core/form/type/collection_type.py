from typing import Any, Dict, List, Optional, Type

from framefox.core.form.type.abstract_form_type import AbstractFormType

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class CollectionType(AbstractFormType):
    """Type for collections (lists) of values."""

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options)
        self.entry_type = options.get("entry_type")
        self.allow_add = options.get("allow_add", True)
        self.allow_delete = options.get("allow_delete", True)
        if self.entry_type:
            self.entry_type_instance = self.entry_type(
                options.get("entry_options", {}))

    def transform_to_model(self, value: Any) -> List[Any]:
        """Transforms raw values into a list of elements."""
        if not value:
            return []

        if isinstance(value, str):
            if value.startswith("[") and value.endswith("]"):  # JSON array
                import json

                try:
                    values = json.loads(value)
                except json.JSONDecodeError:
                    values = [v.strip() for v in value.strip("[]").split(",")]
            else:

                values = [v.strip() for v in value.split(",")]
        elif not isinstance(value, list):
            values = [value]
        else:
            values = value

        if self.entry_type:
            return [self.entry_type_instance.transform_to_model(v) for v in values]
        return values

    def transform_to_view(self, value: Any) -> List[Any]:
        """Transforms the list of elements for display."""
        if not value:
            return []

        if not isinstance(value, list):
            value = [value]

        if self.entry_type:
            return [self.entry_type_instance.transform_to_view(v) for v in value]
        return value

    def get_block_prefix(self) -> str:
        """Returns the block prefix for rendering."""
        return "collection"
