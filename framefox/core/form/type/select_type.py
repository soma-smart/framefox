from typing import Any, Dict, List

from framefox.core.form.type.abstract_form_type import AbstractFormType


class SelectType(AbstractFormType):
    """Type de champ pour une liste déroulante."""

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options or {})

        # Options par défaut
        self.options.setdefault("choices", {})
        self.options.setdefault("multiple", False)
        self.options.setdefault("empty_label", "Sélectionner...")
        self.options.setdefault("attr", {})

        # Ajouter la classe form-select par défaut
        if "class" not in self.options["attr"]:
            self.options["attr"]["class"] = "form-select"
        else:
            self.options["attr"]["class"] += " form-select"

    def transform_to_model(self, value: Any) -> Any:
        """Transforme la valeur du formulaire en valeur pour le modèle."""
        if not value:
            return [] if self.options.get("multiple") else None

        # Pour les sélections multiples
        if self.options.get("multiple"):
            # Si on a déjà une liste
            if isinstance(value, list):
                return value
            # Si on a une seule valeur mais qu'on attend une liste
            return [value]

        # Pour les sélections simples
        return value

    def transform_to_view(self, value: Any) -> Any:
        """Transforme la valeur du modèle en valeur pour l'affichage."""
        if self.options.get("multiple"):
            # Pour les listes, s'assurer qu'on a bien une liste
            if value is None:
                return []
            if not isinstance(value, list):
                return [value] if value else []
            return value

        # Pour les valeurs simples
        return value

    def get_block_prefix(self) -> str:
        """Retourne le préfixe du bloc pour le rendu."""
        return "select"

    def render(self, options: Dict[str, Any] = None) -> str:
        """Rendu HTML du champ select."""
        options = options or {}
        attrs = self.options.get("attr", {}).copy()

        # Attributs HTML
        attrs.update(
            {
                "name": self.name,
                "id": self.get_id(),
            }
        )

        # Option multiple
        if self.options.get("multiple"):
            attrs["multiple"] = "multiple"
            # Pour les sélections multiples, ajouter des crochets au nom
            if not attrs["name"].endswith("[]"):
                attrs["name"] += "[]"

        # Attribut required
        if self.options.get("required"):
            attrs["required"] = "required"

        # Ajouter la classe d'erreur si nécessaire
        if self.has_errors():
            if "class" in attrs:
                attrs["class"] += " is-invalid"
            else:
                attrs["class"] = "is-invalid"

        # Générer les attributs en chaîne
        attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())

        # Récupérer les options du select
        choices = self.options.get("choices", {})
        selected_values = []

        # Convertir la valeur actuelle en liste de valeurs sélectionnées
        current_value = self.get_value()
        if current_value is not None:
            if isinstance(current_value, list):
                selected_values = [str(v) for v in current_value]
            else:
                selected_values = [str(current_value)]

        # Générer les options HTML
        options_html = ""

        # Option vide au début si elle est définie et que ce n'est pas un select multiple
        empty_label = self.options.get("empty_label")
        if empty_label and not self.options.get("multiple"):
            options_html += f'<option value="">{empty_label}</option>'

        # Générer les options à partir des choix
        for value, label in choices.items():
            selected = "selected" if str(value) in selected_values else ""
            options_html += f'<option value="{value}" {selected}>{label}</option>'

        # Générer le HTML complet du select
        html = f"<select {attr_str}>{options_html}</select>"

        # Ajouter le message d'erreur si nécessaire
        if self.has_errors():
            errors = self.get_errors()
            error_html = '<div class="invalid-feedback">'
            error_html += '<ul class="list-unstyled mb-0">'
            for error in errors:
                error_html += f"<li>{error}</li>"
            error_html += "</ul></div>"
            html += error_html

        # Ajouter le texte d'aide si nécessaire
        help = self.options.get("help")
        if help:
            html += f'<small class="form-text text-muted">{help}</small>'

        return html
