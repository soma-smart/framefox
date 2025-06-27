from datetime import datetime
from typing import Any, Dict, Optional

from framefox.core.form.type.abstract_form_type import AbstractFormType

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class DateTimeType(AbstractFormType):
    """Form type for datetime fields."""

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options or {})
        self.use_native_widget = self.options.get("use_native_widget", True)
        self.widget_type = "datetime-local" if self.use_native_widget else "text"

    def get_attr(self) -> Dict[str, Any]:
        """Returns the HTML attributes for the field."""
        attr = self.options.get("attr", {}).copy()
        if self.use_native_widget:
            attr["type"] = self.widget_type

        if "class" not in attr:
            attr["class"] = "form-control"

        return attr

    def transform_to_model(self, value: Any) -> Optional[datetime]:
        """Transforms the form value (string) into a datetime object."""
        if not value:
            return None

        if isinstance(value, datetime):
            return value

        try:
            return datetime.fromisoformat(value.replace("T", " "))
        except ValueError:
            try:

                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                raise ValueError(f"Unrecognized date/time format: {value}")
            except Exception as e:
                raise ValueError(f"Unable to convert to datetime: {value}. Error: {str(e)}")

    def transform_to_view(self, value: Any) -> str:
        """Transforms a datetime object into a string for display."""
        if not value:
            return ""

        if isinstance(value, str):
            return value

        try:
            return value.strftime("%Y-%m-%dT%H:%M")
        except Exception:
            return str(value)

    def get_block_prefix(self) -> str:
        """Returns the block prefix for rendering."""
        return "datetime"
