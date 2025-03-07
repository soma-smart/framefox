from typing import Any, Dict

from framefox.core.form.type.abstract_form_type import AbstractFormType


class TextareaType(AbstractFormType):
    """Type pour les champs textarea."""

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options or {})

        # Options par défaut
        self.options.setdefault("attr", {})

        # Ajouter la classe form-control par défaut
        if "class" not in self.options["attr"]:
            self.options["attr"]["class"] = "form-control"
        else:
            self.options["attr"]["class"] += " form-control"

        # Définir rows par défaut
        if "rows" not in self.options["attr"]:
            self.options["attr"]["rows"] = 3

    def transform_to_model(self, value: Any) -> Any:
        """Transforme la valeur du textarea en valeur pour le modèle."""
        # Cas spécial: conversion en liste pour un champ roles
        if self.name == "roles" and isinstance(value, str):
            # Si la valeur est une chaîne JSON (commence par [ et finit par ])
            if value.strip().startswith("[") and value.strip().endswith("]"):
                try:
                    import json

                    return json.loads(value)
                except:
                    # Si le parsing JSON échoue, traiter comme une liste de valeurs séparées par des virgules
                    pass

            # Traiter comme une liste de valeurs séparées par des virgules
            if value.strip():
                return [item.strip() for item in value.split(",")]
            return []

        return value

    def transform_to_view(self, value: Any) -> Any:
        """Transforme la valeur du modèle en valeur pour l'affichage."""
        # Pour les listes, les convertir en chaîne séparée par des virgules
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        return value if value is not None else ""

    def get_block_prefix(self) -> str:
        """Retourne le préfixe du bloc pour le rendu."""
        return "textarea"
