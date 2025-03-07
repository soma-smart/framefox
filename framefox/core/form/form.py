from typing import Any, Dict, List, Optional, Type

from fastapi import Request

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: YourName
"""


class Form:
    """Classe principale représentant un formulaire."""

    def __init__(
        self,
        fields: Dict[str, "FormField"],
        data: Optional[Any] = None,
        options: Dict[str, Any] = None,
    ):
        self.fields = fields
        self.data = data
        self.options = options or {}
        self.errors = {}
        self.submitted = False
        self.valid = False

    # Ajouter ceci à la méthode handle_request de la classe Form
    async def handle_request(self, request: Request) -> bool:
        """Traite la soumission du formulaire depuis une requête HTTP."""
        if request.method != "POST":
            return False

        self.submitted = True
        form_data = await request.form()

        # Convertir MultiDict en dict standard
        data_dict = {}
        file_dict = {}

        # Traiter séparément les fichiers et les données de formulaire
        for key, value in form_data.items():
            # Gérer les champs multiples standard
            if key.endswith("[]"):
                base_key = key[:-2]
                data_dict[base_key] = form_data.getlist(key)
            else:
                # Vérifier si c'est un fichier
                if hasattr(value, "filename") and hasattr(value, "file"):
                    file_dict[key] = value
                else:
                    # Pour les champs avec valeurs multiples
                    values = form_data.getlist(key)
                    if len(values) > 1:
                        data_dict[key] = values
                    else:
                        data_dict[key] = value

        # Assigner les valeurs aux champs (sauf fichiers)
        self.assign_data(data_dict)

        # Traiter les fichiers uploadés
        await self._handle_file_uploads(file_dict)

        # Vérifier les champs requis
        for name, field in self.fields.items():
            if field.options.get("required", False):
                # Si c'est un champ de type fichier, vérifier s'il est requis quand vide
                is_file_field = (
                    hasattr(field.type, "get_block_prefix")
                    and field.type.get_block_prefix() == "file"
                )
                file_already_exists = is_file_field and field.get_value() is not None

                # Si ce n'est pas un fichier ou si c'est un fichier requis sans valeur existante
                if not is_file_field or (is_file_field and not file_already_exists):
                    if name not in data_dict and name not in file_dict:
                        field.errors.append(
                            f"Le champ {field.options.get('label', name)} est obligatoire"
                        )

        # Valider le formulaire
        self.valid = self.validate()

        # Si le formulaire est valide, assigner les données au modèle
        if self.valid and self.data:
            self._apply_data_to_model()

        return self.valid

    async def _handle_file_uploads(self, file_dict: Dict[str, Any]) -> None:
        """Traite les fichiers uploadés."""
        for field_name, upload_file in file_dict.items():
            if field_name in self.fields:
                field = self.fields[field_name]
                if hasattr(field.type, "handle_upload"):
                    try:
                        # Si c'est un champ multiple, traiter chaque fichier
                        if field.options.get("multiple", False) and isinstance(
                            upload_file, list
                        ):
                            file_paths = []
                            for file in upload_file:
                                file_path = await field.type.handle_upload(file)
                                file_paths.append(file_path)
                            field.value = file_paths
                            field.submitted = True  # Marquer comme soumis
                        else:
                            # Traiter un seul fichier
                            file_path = await field.type.handle_upload(upload_file)
                            field.value = file_path
                            field.submitted = True  # Marquer comme soumis

                        # Debug pour vérifier l'assignation
                        print(
                            f">>> DEBUG: Champ {field_name} soumis avec valeur: {field.value}"
                        )
                    except Exception as e:
                        field.errors.append(str(e))

    def _apply_data_to_model(self):
        """Applique les données du formulaire au modèle"""
        for name, field in self.fields.items():
            if hasattr(self.data, name) and field.is_submitted():
                value = field.get_value()
                # Vérifier que la valeur n'est pas None pour les champs requis
                if field.options.get("required", False) and value is None:
                    self.valid = False
                    return
                setattr(self.data, name, value)

    def assign_data(self, data: Dict[str, Any]) -> None:
        """Assigne les données aux champs du formulaire."""
        for name, field in self.fields.items():
            if name in data:
                field.set_value(data[name])

    def validate(self) -> bool:
        """Valide tous les champs du formulaire."""
        valid = True
        self.errors = {}

        for name, field in self.fields.items():
            if not field.validate():
                self.errors[name] = field.errors
                valid = False

        return valid

    def get_data(self) -> Any:
        """Retourne l'objet avec les données du formulaire."""
        if hasattr(self.data, "__dict__"):
            # Si c'est une entité ou un objet
            for name, field in self.fields.items():
                if hasattr(self.data, name) and field.is_submitted():
                    value = field.get_value()
                    setattr(self.data, name, value)
            return self.data
        else:
            # Si c'est un dictionnaire ou None
            result = {}
            for name, field in self.fields.items():
                if field.is_submitted():
                    result[name] = field.get_value()
            return result

    def create_view(self) -> "FormView":
        """Crée une vue pour le rendu du formulaire."""
        from framefox.core.form.view.form_view import FormView

        return FormView(self)

    def is_valid(self) -> bool:
        """Indique si le formulaire est valide."""
        return self.valid and self.submitted

    def is_submitted(self) -> bool:
        """Indique si le formulaire a été soumis."""
        return self.submitted
