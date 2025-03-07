from jinja2 import Environment


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
        """Rendu du début du formulaire."""
        options = options or {}
        action = options.get("action", "")
        method = options.get("method", "POST")

        # Récupérer les attributs définis dans FormType via get_options()
        form_attrs = {}
        if hasattr(form_view.form, "options") and "attr" in form_view.form.options:
            form_attrs = form_view.form.options["attr"].copy()

        # Ajouter ou remplacer par les attributs définis dans le template
        attr = options.get("attr", {})
        form_attrs.update(attr)

        # Toujours ajouter enctype pour les formulaires avec uploads
        has_file_field = False
        for field in form_view.form.fields.values():
            if (
                hasattr(field.type, "get_block_prefix")
                and field.type.get_block_prefix() == "file"
            ):
                has_file_field = True
                break

        if has_file_field and "enctype" not in form_attrs:
            form_attrs["enctype"] = "multipart/form-data"

        attr_str = " ".join(f'{k}="{v}"' for k, v in form_attrs.items())

        return f'<form method="{method}" action="{action}" {attr_str}>'

    def form_end(self, form_view, options=None):
        """Rendu de la fin du formulaire."""
        return "</form>"

    def form_row(self, form_view, field_name, options=None):
        """Rendu d'une ligne complète de formulaire (label + widget + erreurs)."""
        options = options or {}
        field_view = form_view.get_field(field_name)

        if not field_view:
            return f"<!-- Champ {field_name} non trouvé -->"

        label = self.form_label(form_view, field_name)
        widget = self.form_widget(form_view, field_name)
        errors = self.form_errors(form_view, field_name)

        return f"""
        <div class="mb-3">
            {label}
            {widget}
            {errors}
        </div>
        """

    def form_label(self, form_view, field_name, options=None):
        """Rendu du label d'un champ."""
        options = options or {}
        field_view = form_view.get_field(field_name)

        if not field_view:
            return f"<!-- Champ {field_name} non trouvé -->"

        label_text = options.get("label", field_view.get_label())
        label_attr = options.get("label_attr", {})
        label_attr.setdefault("class", "form-label")
        label_attr.setdefault("for", field_view.get_id())

        attr_str = " ".join(f'{k}="{v}"' for k, v in label_attr.items())

        return f"<label {attr_str}>{label_text}</label>"

    def form_widget(self, form_view, field_name, options=None):
        """Rendu du widget d'un champ."""
        options = options or {}
        field_view = form_view.get_field(field_name)

        if not field_view:
            return f"<!-- Champ {field_name} non trouvé -->"

        # Déléguer le rendu au widget du champ
        return field_view.render(options)

    def form_errors(self, form_view, field_name, options=None):
        """Rendu des erreurs d'un champ."""
        options = options or {}
        field_view = form_view.get_field(field_name)

        if not field_view or not field_view.has_errors():
            return ""

        errors = field_view.get_errors()
        error_html = "".join(
            [f'<div class="invalid-feedback">{error}</div>' for error in errors]
        )

        return error_html


def form_widget(self, form_view, field_name, options=None):
    field_view = form_view.get_field(field_name)
    return field_view.render(options)  # FormViewField.render()
