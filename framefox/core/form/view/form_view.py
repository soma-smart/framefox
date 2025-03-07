from typing import Any, Dict, Optional

from framefox.core.form.form import Form
from framefox.core.form.view.form_view_field import FormViewField


class FormView:
    """Vue pour le rendu d'un formulaire."""

    def __init__(self, form: Form):
        self.form = form
        self.fields = {}

        # Créer les vues des champs
        for name, field in form.fields.items():
            self.fields[name] = FormViewField(field)

    def get_field(self, name: str) -> Optional[FormViewField]:
        """Récupère la vue d'un champ par son nom."""
        return self.fields.get(name)

    def get_fields(self) -> Dict[str, FormViewField]:
        """Récupère toutes les vues des champs."""
        return self.fields

    def get_errors(self) -> Dict[str, Any]:
        """Récupère les erreurs du formulaire."""
        return self.form.errors

    def has_errors(self) -> bool:
        """Vérifie si le formulaire a des erreurs."""
        return len(self.form.errors) > 0

    def is_submitted(self) -> bool:
        """Vérifie si le formulaire a été soumis."""
        return self.form.submitted

    def is_valid(self) -> bool:
        """Vérifie si le formulaire est valide."""
        return self.form.valid
