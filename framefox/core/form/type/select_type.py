from typing import Any, Dict

from framefox.core.form.type.abstract_form_type import AbstractFormType
"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class SelectType(AbstractFormType):
    """Field type for a dropdown list."""

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options or {})
        self.options.setdefault("choices", {})
        self.options.setdefault("multiple", False)
        self.options.setdefault("empty_label", "Select...")
        self.options.setdefault("attr", {})

        if "class" not in self.options["attr"]:
            self.options["attr"]["class"] = "form-select"
        else:
            self.options["attr"]["class"] += " form-select"

    def transform_to_model(self, value: Any) -> Any:
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
        return "select"

    def render(self, options: Dict[str, Any] = None) -> str:
        """HTML rendering of the select field."""
        options = options or {}
        attrs = self.options.get("attr", {}).copy()

        attrs.update(
            {
                "name": self.name,
                "id": self.get_id(),
            }
        )

        if self.options.get("multiple"):
            attrs["multiple"] = "multiple"
            if not attrs["name"].endswith("[]"):
                attrs["name"] += "[]"

        if self.options.get("required"):
            attrs["required"] = "required"

        if self.has_errors():
            if "class" in attrs:
                attrs["class"] += " is-invalid"
            else:
                attrs["class"] = "is-invalid"

        attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())

        choices = self.options.get("choices", {})
        selected_values = []

        current_value = self.get_value()
        if current_value is not None:
            if isinstance(current_value, list):
                selected_values = [str(v) for v in current_value]
            else:
                selected_values = [str(current_value)]

        options_html = ""

        empty_label = self.options.get("empty_label")
        if empty_label and not self.options.get("multiple"):
            options_html += f'<option value="">{empty_label}</option>'

        for value, label in choices.items():
            selected = "selected" if str(value) in selected_values else ""
            options_html += f'<option value="{value}" {selected}>{label}</option>'

        html = f"<select {attr_str}>{options_html}</select>"

        if self.has_errors():
            errors = self.get_errors()
            error_html = '<div class="invalid-feedback">'
            error_html += '<ul class="list-unstyled mb-0">'
            for error in errors:
                error_html += f"<li>{error}</li>"
            error_html += "</ul></div>"
            html += error_html

        help = self.options.get("help")
        if help:
            html += f'<small class="form-text text-muted">{help}</small>'

        return html
