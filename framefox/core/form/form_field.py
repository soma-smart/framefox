from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type


@dataclass
class FormField:
    """Représente un champ de formulaire."""

    name: str
    type: "FormType"
    options: Dict[str, Any] = field(default_factory=dict)
    value: Any = None
    errors: List[str] = field(default_factory=list)
    submitted: bool = False

    def __post_init__(self):
        """Initialisation après création de l'instance."""
        # Transmettre le nom au type
        if hasattr(self.type, "set_name"):
            self.type.set_name(self.name)

    def set_value(self, value: Any) -> None:
        """Définit la valeur du champ à partir des données brutes du formulaire."""
        self.submitted = True
        try:
            # Traitement spécial pour les valeurs de type liste représentées comme chaînes
            if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
                import json

                try:
                    # Tenter de désérialiser la chaîne JSON
                    value = json.loads(value)
                except json.JSONDecodeError:
                    # Si ce n'est pas un JSON valide, garder la valeur telle quelle
                    pass

            self.value = self.type.transform_to_model(value)
        except Exception as e:
            self.errors.append(str(e))

    def get_value(self) -> Any:
        """Récupère la valeur transformée du champ."""
        return self.value

    def validate(self) -> bool:
        """Valide le champ selon ses contraintes."""
        self.errors = []

        # Vérifier si le champ est requis
        if (
            self.options.get("required", False)
            and not self.value
            and self.value is not False
        ):
            self.errors.append(f"Le champ {self.name} est obligatoire")
            return False

        # Exécuter les validateurs personnalisés
        for validator in self.options.get("validators", []):
            if not validator.validate(self.value):
                self.errors.append(validator.message)
                return False

        return len(self.errors) == 0

    def is_submitted(self) -> bool:
        """Indique si le champ a été soumis."""
        return self.submitted
