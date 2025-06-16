from typing import Any, Dict, List

from framefox.core.form.form_field import FormField

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FormViewField:
    """View for rendering a form field."""

    def __init__(self, field: FormField):
        self.field = field

    def render(self, options: Dict[str, Any] = None) -> str:
        options = options or {}
        field_attrs = self.field.options.get("attr", {}).copy()
        render_attrs = options.get("attr", {})
        field_attrs.update(render_attrs)
        render_options = options.copy()
        render_options["attr"] = field_attrs

        if hasattr(self.field.type, "render"):
            return self.field.type.render(render_options)
        else:
            attrs = field_attrs.copy()
            attrs.setdefault("name", self.get_name())
            attrs.setdefault("id", self.get_id())

            if self.has_errors():
                attrs.setdefault("class", "")
                attrs["class"] += " is-invalid"

            input_type = "text"

            if hasattr(self.field.type, "get_attr"):
                type_attrs = self.field.type.get_attr()
                if "type" in type_attrs:
                    input_type = type_attrs["type"]

            field_type_name = self.field.type.__class__.__name__
            if field_type_name == "DateTimeType":
                input_type = "datetime-local"
            elif field_type_name == "CheckboxType":
                input_type = "checkbox"
            elif field_type_name == "NumberType":
                input_type = "number"
            elif field_type_name == "EmailType":
                input_type = "email"
            elif field_type_name == "PasswordType":
                input_type = "password"

            attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
            value = self.get_value() or ""
            html = f'<input type="{input_type}" value="{value}" {attr_str}>'

            if self.has_errors():
                errors = self.get_errors()
                error_html = '<div class="invalid-feedback">'
                for error in errors:
                    error_html += f"<div>{error}</div>"
                error_html += "</div>"
                html += error_html

            return html

    def get_name(self) -> str:
        """Gets the field name."""
        return self.field.name

    def get_value(self) -> Any:
        """Gets the field value."""
        return self.field.value

    def get_label(self) -> str:
        """Gets the field label."""
        return self.field.options.get("label", self.field.name)

    def get_id(self) -> str:
        """Gets the field ID."""
        return self.field.options.get("id", self.field.name)

    def get_type(self) -> str:
        """Gets the field type for rendering."""
        return self.field.type.get_block_prefix()

    def get_attr(self, name: str, default: Any = None) -> Any:
        """Gets a field attribute."""
        attrs = self.field.options.get("attr", {})
        return attrs.get(name, default)

    def get_attrs(self) -> Dict[str, Any]:
        """Gets all field attributes."""
        return self.field.options.get("attr", {})

    def get_errors(self) -> List[str]:
        """Gets the field errors."""
        return self.field.errors

    def has_errors(self) -> bool:
        """Checks if the field has errors."""
        return len(self.field.errors) > 0

    def is_required(self) -> bool:
        """Checks if the field is required."""
        return self.field.options.get("required", False)

    def get_choices(self) -> List[Dict[str, Any]]:
        """Gets the choices for a select field."""
        if hasattr(self.field.type, "get_choices"):
            return self.field.type.get_choices()
        return []
