from typing import Any, Dict, List, Optional

from framefox.core.form.form_field import FormField


class FormViewField:
    """Vue pour le rendu d'un champ de formulaire."""

    def __init__(self, field: FormField):
        self.field = field

    def render(self, options: Dict[str, Any] = None) -> str:
        """Délègue le rendu au type de champ sous-jacent."""
        options = options or {}

        # Fusionner les attributs du champ avec ceux fournis
        field_attrs = self.field.options.get("attr", {}).copy()
        render_attrs = options.get("attr", {})
        field_attrs.update(render_attrs)

        # Mettre à jour les options avec les attributs fusionnés
        render_options = options.copy()
        render_options["attr"] = field_attrs

        # Déléguer au type de champ
        if hasattr(self.field.type, "render"):
            return self.field.type.render(render_options)
        else:
            # Rendu par défaut
            attrs = field_attrs.copy()
            attrs.setdefault("name", self.get_name())
            attrs.setdefault("id", self.get_id())

            # Gestion des classes CSS
            if self.has_errors():
                attrs.setdefault("class", "")
                attrs["class"] += " is-invalid"

            # Déterminer le type d'input en fonction du type de champ
            input_type = "text"  # Type par défaut

            # Récupérer les attributs depuis le type de formulaire si disponible
            if hasattr(self.field.type, "get_attr"):
                type_attrs = self.field.type.get_attr()
                if "type" in type_attrs:
                    input_type = type_attrs["type"]

            # Cas spécifiques basés sur le nom de la classe
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

            # Générer la chaîne d'attributs HTML
            attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())

            # Générer l'input avec le bon type
            value = self.get_value() or ""
            html = f'<input type="{input_type}" value="{value}" {attr_str}>'

            # Ajouter les erreurs si nécessaire
            if self.has_errors():
                errors = self.get_errors()
                error_html = '<div class="invalid-feedback">'
                for error in errors:
                    error_html += f"<div>{error}</div>"
                error_html += "</div>"
                html += error_html

            return html

    def get_name(self) -> str:
        """Récupère le nom du champ."""
        return self.field.name

    def get_value(self) -> Any:
        """Récupère la valeur du champ."""
        return self.field.value

    def get_label(self) -> str:
        """Récupère le label du champ."""
        return self.field.options.get("label", self.field.name)

    def get_id(self) -> str:
        """Récupère l'identifiant du champ."""
        return self.field.options.get("id", self.field.name)

    def get_type(self) -> str:
        """Récupère le type du champ pour le rendu."""
        return self.field.type.get_block_prefix()

    def get_attr(self, name: str, default: Any = None) -> Any:
        """Récupère un attribut du champ."""
        attrs = self.field.options.get("attr", {})
        return attrs.get(name, default)

    def get_attrs(self) -> Dict[str, Any]:
        """Récupère tous les attributs du champ."""
        return self.field.options.get("attr", {})

    def get_errors(self) -> List[str]:
        """Récupère les erreurs du champ."""
        return self.field.errors

    def has_errors(self) -> bool:
        """Vérifie si le champ a des erreurs."""
        return len(self.field.errors) > 0

    def is_required(self) -> bool:
        """Vérifie si le champ est requis."""
        return self.field.options.get("required", False)

    def get_choices(self) -> List[Dict[str, Any]]:
        """Récupère les choix d'un champ select."""
        if hasattr(self.field.type, "get_choices"):
            return self.field.type.get_choices()
        return []
