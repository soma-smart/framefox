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
    """
    Represents a form field type for selecting from predefined choices.
    Supports single or multiple selections, and can render as select, radio, or checkbox inputs.
    """

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options or {})
        self.options.setdefault("choices", {})
        self.options.setdefault("multiple", False)
        self.options.setdefault("expanded", False)
        self.options.setdefault("attr", {})

    def transform_to_model(self, value: Any) -> Union[str, List[str]]:
        if not value:
            return [] if self.options.get("multiple") else None
        if self.options.get("multiple"):
            if isinstance(value, list):
                return value
            return [value]
        return value

    def transform_to_view(self, value: Any) -> Any:
        if self.options.get("multiple"):
            if value is None:
                return []
            if not isinstance(value, list):
                return [value] if value else []
            return value
        return value

    def get_block_prefix(self) -> str:
        if self.options.get("expanded"):
            return "choice_expanded"
        return "choice"

    def render(self, options: Dict[str, Any] = None) -> str:
        options = options or {}
        if not self.options.get("expanded", False):
            select_options = self.options.copy()
            select_type = SelectType(select_options)
            select_type.name = self.name if hasattr(self, "name") else ""
            select_type.value = self.value if hasattr(self, "value") else None
            if hasattr(self, "parent"):
                select_type.parent = self.parent
            else:
                select_type.parent = None
            select_type.errors = self.errors if hasattr(self, "errors") else []
            return select_type.render(options)
        choices = self.options.get("choices", {})
        is_multiple = self.options.get("multiple", False)
        input_type = "checkbox" if is_multiple else "radio"
        field_id = f"{self.name}" if hasattr(self, "name") else ""
        current_values = []
        if hasattr(self, "value") and self.value is not None:
            if isinstance(self.value, list):
                current_values = [str(val) for val in self.value]
            else:
                current_values = [str(self.value)]
        default_attr = self.options.get("attr", {}).copy()
        default_attr.setdefault("class", "form-check-input")
        wrapper_attr = self.options.get("row_attr", {}).copy()
        wrapper_attr.setdefault("class", "")
        wrapper_class = wrapper_attr.pop("class", "")
        wrapper_attr_str = " ".join(f'{k}="{v}"' for k, v in wrapper_attr.items())
        html = f'<div class="{wrapper_class}" {wrapper_attr_str}>'
        for value, label in choices.items():
            item_id = f"{field_id}_{value}"
            checked = "checked" if str(value) in current_values else ""
            item_attr = default_attr.copy()
            if callable(self.options.get("choice_attr")):
                choice_attr = self.options.get("choice_attr")(value)
                if choice_attr:
                    item_attr.update(choice_attr)
            attr_str = " ".join(f'{k}="{v}"' for k, v in item_attr.items())
            html += f"""
            <div class="form-check">
                <input type="{input_type}" id="{item_id}" name="{self.name}{"[]" if is_multiple else ""}"
                    value="{value}" {checked} {attr_str}>
                <label class="form-check-label" for="{item_id}">
                    {label}
                </label>
            </div>
            """
        html += "</div>"
        return html
