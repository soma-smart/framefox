from jinja2 import Environment

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FormExtension:

    def __init__(self, env: Environment):
        self.env = env
        self.register_functions()

    def register_functions(self):

        self.env.globals.update(
            {
                "form_start": self.form_start,
                "form_end": self.form_end,
                "form_row": self.form_row,
                "form_label": self.form_label,
                "form_widget": self.form_widget,
                "form_errors": self.form_errors,
            }
        )

    def form_start(self, form_view, options=None):
        """Render the start of the form."""
        options = options or {}
        action = options.get("action", "")
        method = options.get("method", "POST")
        form_attrs = {}
        if hasattr(form_view.form, "options") and "attr" in form_view.form.options:
            form_attrs = form_view.form.options["attr"].copy()

        attr = options.get("attr", {})
        form_attrs.update(attr)

        has_file_field = False
        for field in form_view.form.fields.values():
            if hasattr(field.type, "get_block_prefix") and field.type.get_block_prefix() == "file":
                has_file_field = True
                break

        if has_file_field and "enctype" not in form_attrs:
            form_attrs["enctype"] = "multipart/form-data"

        attr_str = " ".join(f'{k}="{v}"' for k, v in form_attrs.items())

        return f'<form method="{method}" action="{action}" {attr_str}>'

    def form_end(self, form_view, options=None):
        """Render the end of the form."""
        return "</form>"

    def form_row(self, form_view, field_name, options=None):
        """Render a complete form row (label + widget + errors)."""
        options = options or {}
        field_view = form_view.get_field(field_name)

        if not field_view:
            return f"<!-- Field {field_name} not found -->"

        label = self.form_label(form_view, field_name)
        widget = self.form_widget(form_view, field_name)
        errors = self.form_errors(form_view, field_name)

        # Détecter si c'est un choix étendu
        is_expanded_choice = False
        if hasattr(field_view, "type"):
            is_expanded_choice = (
                hasattr(field_view.type, "options")
                and field_view.type.options.get("expanded", False)
                and "choices" in field_view.type.options
            )

        # Adapter le HTML selon le type de champ
        if is_expanded_choice:
            return f"""
            <div class="mb-3">
                {label}
                <div class="choice-group mt-2">
                    {widget}
                </div>
                {errors}
            </div>
            """
        else:
            return f"""
            <div class="mb-3">
                {label}
                {widget}
                {errors}
            </div>
            """

    def form_label(self, form_view, field_name, options=None):
        """Render the label of a field."""
        options = options or {}
        field_view = form_view.get_field(field_name)

        if not field_view:
            return f"<!-- Field {field_name} not found -->"

        label_text = options.get("label", field_view.get_label())
        label_attr = options.get("label_attr", {})
        label_attr.setdefault("class", "form-label")
        label_attr.setdefault("for", field_view.get_id())

        attr_str = " ".join(f'{k}="{v}"' for k, v in label_attr.items())

        return f"<label {attr_str}>{label_text}</label>"

    def form_widget(self, form_view, field_name, options=None):
        """Render the widget of a field."""
        options = options or {}
        field_view = form_view.get_field(field_name)

        if not field_view:
            return f"<!-- Field {field_name} not found -->"

        return field_view.render(options)

    def form_errors(self, form_view, field_name, options=None):
        """Render the errors of a field."""
        options = options or {}
        field_view = form_view.get_field(field_name)

        if not field_view or not field_view.has_errors():
            return ""

        errors = field_view.get_errors()
        error_html = "".join([f'<div class="invalid-feedback">{error}</div>' for error in errors])

        return error_html


def form_widget(self, form_view, field_name, options=None):
    field_view = form_view.get_field(field_name)
    return field_view.render(options)
