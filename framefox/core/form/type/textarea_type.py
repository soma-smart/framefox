from typing import Any, Dict

from framefox.core.form.type.abstract_form_type import AbstractFormType

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TextareaType(AbstractFormType):
    """Type for textarea fields."""

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options or {})

        self.options.setdefault("attr", {})

        if "class" not in self.options["attr"]:
            self.options["attr"]["class"] = "form-control"
        else:
            self.options["attr"]["class"] += " form-control"

        if "rows" not in self.options["attr"]:
            self.options["attr"]["rows"] = 3

    def transform_to_model(self, value: Any) -> Any:
        """Transforms the textarea value to a model value."""
        if self.name == "roles" and isinstance(value, str):
            if value.strip().startswith("[") and value.strip().endswith("]"):
                try:
                    import json

                    return json.loads(value)
                except Exception:
                    pass

            if value.strip():
                return [item.strip() for item in value.split(",")]
            return []

        return value

    def transform_to_view(self, value: Any) -> Any:
        """Transforms the model value to a view value."""
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        return value if value is not None else ""

    def get_block_prefix(self) -> str:
        """Returns the block prefix for rendering."""
        return "textarea"
