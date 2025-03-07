from datetime import datetime
from typing import Any, Dict, Optional

from framefox.core.form.type.abstract_form_type import AbstractFormType


class DateTimeType(AbstractFormType):
    """Type de formulaire pour les champs datetime."""

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options or {})
        # Par défaut, utiliser le widget HTML5 natif
        self.use_native_widget = self.options.get("use_native_widget", True)
        self.widget_type = "datetime-local" if self.use_native_widget else "text"

    def get_attr(self) -> Dict[str, Any]:
        """Retourne les attributs HTML pour le champ."""
        attr = self.options.get("attr", {}).copy()

        # Ajouter le type HTML approprié
        if self.use_native_widget:
            attr["type"] = self.widget_type

        # Ajouter une classe si elle n'existe pas déjà
        if "class" not in attr:
            attr["class"] = "form-control"

        return attr

    def transform_to_model(self, value: Any) -> Optional[datetime]:
        """Transforme la valeur du formulaire (chaîne) en objet datetime."""
        if not value:
            return None

        if isinstance(value, datetime):
            return value

        try:
            # Format ISO depuis un input HTML datetime-local: "YYYY-MM-DDThh:mm"
            return datetime.fromisoformat(value.replace("T", " "))
        except ValueError:
            try:
                # Essayer plusieurs formats courants
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                raise ValueError(f"Format de date/heure non reconnu: {value}")
            except Exception as e:
                raise ValueError(
                    f"Impossible de convertir en datetime: {value}. Erreur: {str(e)}"
                )

    def transform_to_view(self, value: Any) -> str:
        """Transforme un objet datetime en chaîne pour l'affichage."""
        if not value:
            return ""

        if isinstance(value, str):
            return value

        try:
            # Format ISO pour un input HTML datetime-local
            return value.strftime("%Y-%m-%dT%H:%M")
        except Exception:
            return str(value)

    def get_block_prefix(self) -> str:
        """Retourne le préfixe du bloc pour le rendu."""
        return "datetime"
