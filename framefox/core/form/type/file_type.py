import os
from typing import Any, Dict, List

from fastapi import UploadFile

from framefox.core.file.file_manager import FileManager
from framefox.core.form.type.abstract_form_type import AbstractFormType


class FileType(AbstractFormType):
    """Type de champ pour les uploads de fichiers."""

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options or {})

        # Options par défaut
        self.options.setdefault("attr", {})
        self.options.setdefault("multiple", False)
        self.options.setdefault("accept", "")  # Types MIME acceptés
        self.options.setdefault("storage_path", "public/uploads")
        self.options.setdefault("max_file_size", 5 * 1024 * 1024)  # 5MB par défaut
        # Vide = toutes extensions
        self.options.setdefault("allowed_extensions", [])
        self.options.setdefault("rename", True)  # Renommer avec UUID

        # Ajouter la classe form-control par défaut
        if "class" not in self.options["attr"]:
            self.options["attr"]["class"] = "form-control"
        else:
            self.options["attr"]["class"] += " form-control"

    async def handle_upload(self, upload_file: UploadFile) -> str:
        """Traite un fichier uploadé et retourne le chemin de stockage."""
        if not upload_file:
            return None

        # Ajoutons un log visible dans la console pour déboguer
        print(f">>> DEBUG: Traitement du fichier {upload_file.filename}")

        # Vérifier la taille du fichier
        await upload_file.seek(0)
        content = await upload_file.read()
        file_size = len(content)
        await upload_file.seek(0)  # Revenir au début

        print(f">>> DEBUG: Taille du fichier: {file_size} octets")

        if file_size > self.options.get("max_file_size"):
            raise ValueError(
                f"Le fichier est trop volumineux. Maximum: {self.options.get('max_file_size') / 1024 / 1024}MB"
            )

        # Vérifier l'extension
        original_filename = upload_file.filename
        extension = os.path.splitext(original_filename)[1].lower()
        allowed_extensions = self.options.get("allowed_extensions")

        print(f">>> DEBUG: Extension détectée: {extension}")

        if allowed_extensions and extension not in allowed_extensions:
            raise ValueError(
                f"Type de fichier non autorisé. Extensions autorisées: {', '.join(allowed_extensions)}"
            )

        # Utiliser FileManager pour sauvegarder le fichier
        from framefox.core.di.service_container import ServiceContainer

        container = ServiceContainer()

        try:
            file_manager = container.get(FileManager)
            print(f">>> DEBUG: FileManager récupéré depuis le conteneur")
        except Exception as e:
            print(f">>> ERREUR: Impossible de récupérer FileManager: {str(e)}")
            # Fallback - créer une instance directement
            file_manager = FileManager()
            print(f">>> DEBUG: FileManager créé directement")

        storage_path = self.options.get("storage_path")

        os.makedirs(storage_path, exist_ok=True)

        try:

            file_path = await file_manager.save(
                file=upload_file,
                subdirectory=storage_path,
                rename=self.options.get("rename", True),
                allowed_extensions=allowed_extensions,
            )
            print(f">>> DEBUG: Fichier enregistré à: {file_path}")
            return file_path
        except Exception as e:
            print(f">>> ERREUR FileManager.save: {str(e)}")
            raise e

    def transform_to_model(self, value: Any) -> Any:
        """Pour les fichiers, la transformation se fait de façon asynchrone
        dans Form.handle_request avec handle_upload."""
        # Le fichier est déjà traité et value contient le chemin
        return value

    def transform_to_view(self, value: Any) -> Any:
        """Transforme la valeur du modèle en valeur pour l'affichage."""
        # Dans le cas d'un fichier, on retourne simplement le chemin
        return value

    def get_block_prefix(self) -> str:
        """Retourne le préfixe du bloc pour le rendu."""
        return "file"

    def render(self, options: Dict[str, Any] = None) -> str:
        """Rendu HTML du champ file."""
        options = options or {}
        attrs = self.options.get("attr", {}).copy()

        # Attributs HTML
        attrs.update(
            {
                "name": self.name,
                "id": self.get_id(),
                "type": "file",
            }
        )

        # Option multiple
        if self.options.get("multiple"):
            attrs["multiple"] = "multiple"
            # Pour les champs multiples, ajouter des crochets au nom
            if not attrs["name"].endswith("[]"):
                attrs["name"] += "[]"

        # Type MIME accepté
        if self.options.get("accept"):
            attrs["accept"] = self.options.get("accept")

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

        # Générer le HTML du champ
        html = f"<input {attr_str}>"

        # Si un fichier est déjà présent, afficher son nom
        current_value = self.get_value()
        if current_value:
            html += f'<div class="mt-1"><small class="text-muted">Fichier actuel: {os.path.basename(current_value)}</small></div>'

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
        help_text = self.options.get("help")
        if help_text:
            html += f'<small class="form-text text-muted">{help_text}</small>'

        return html
