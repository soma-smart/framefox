import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import UploadFile


class FileManager:
    """Service de gestion des fichiers uploadés."""

    def __init__(self):
        """
        Initialise le gestionnaire de fichiers avec un répertoire de base.

        """
        # Chemin absolu vers public/uploads dans le dossier du projet
        project_root = os.getcwd()
        self.base_upload_path = Path(project_root)

        # Créer le dossier s'il n'existe pas
        os.makedirs(self.base_upload_path, exist_ok=True)

        self.logger = logging.getLogger("FILE_MANAGER")
        self.logger.info(
            f"FileManager initialisé avec le chemin absolu: {self.base_upload_path}"
        )

    async def save(
        self,
        file: UploadFile,
        subdirectory: str = None,
        rename: bool = True,
        allowed_extensions: List[str] = None,
    ) -> str:
        """
        Sauvegarde un fichier uploadé et retourne son chemin relatif.
        """
        if not file:
            self.logger.warning("Tentative d'upload avec un fichier None")
            return None

        # Log du début d'upload
        self.logger.info(f"Début d'upload du fichier: {file.filename}")

        # Vérifier l'extension si nécessaire
        original_filename = file.filename
        extension = os.path.splitext(original_filename)[1].lower()
        self.logger.info(f"Extension détectée: {extension}")

        if allowed_extensions and extension not in allowed_extensions:
            self.logger.error(
                f"Extension non autorisée: {extension}. Autorisées: {allowed_extensions}"
            )
            raise ValueError(
                f"Type de fichier non autorisé. Extensions autorisées: {', '.join(allowed_extensions)}"
            )

        dest_dir = self.base_upload_path
        if subdirectory:
            subdirectory = subdirectory.strip("/")
            print(f">>> DEBUG: Base path avant ajout de sous-dossier: {dest_dir}")
            dest_dir = dest_dir / subdirectory
            print(f">>> DEBUG: Destination finale avec sous-dossier: {dest_dir}")

        # S'assurer que le répertoire de destination existe
        os.makedirs(dest_dir, exist_ok=True)
        print(
            f">>> DEBUG: Répertoire destination (absolu): {os.path.abspath(dest_dir)}"
        )

        # Générer le nom de fichier
        if rename:
            filename = f"{uuid.uuid4()}{extension}"
            self.logger.info(f"Fichier renommé: {filename}")
        else:
            filename = original_filename
            self.logger.info(f"Utilisation du nom original: {filename}")

        # Chemin complet de destination
        file_path = dest_dir / filename
        abs_file_path = os.path.abspath(file_path)
        self.logger.info(f"Chemin complet du fichier: {abs_file_path}")

        try:
            # Lire et sauvegarder le contenu du fichier
            content = await file.read()
            self.logger.info(f"Contenu du fichier lu: {len(content)} octets")

            with open(file_path, "wb") as f:
                f.write(content)

            self.logger.info(f"Fichier écrit sur le disque: {file_path}")

            # Vérifier si le fichier a bien été créé
            if os.path.exists(file_path):
                self.logger.info(
                    f"✓ Vérification réussie: le fichier existe à {file_path}"
                )
                self.logger.info(
                    f"✓ Taille du fichier: {os.path.getsize(file_path)} octets"
                )
            else:
                self.logger.error(
                    f"✗ Échec de vérification: le fichier n'existe pas à {file_path}"
                )

            # Correction: gérer les chemins relatifs sûrement
            try:
                rel_path = str(file_path.relative_to(os.getcwd()))
            except ValueError:

                if os.path.isabs(file_path):
                    base_path = Path(os.getcwd())
                    rel_path = str(file_path).replace(str(base_path) + "/", "")
                else:
                    # Pour un chemin déjà relatif
                    rel_path = str(file_path)

            self.logger.info(f"Chemin relatif retourné: {rel_path}")
            return rel_path

        except Exception as e:
            self.logger.error(
                f"Erreur lors de la sauvegarde du fichier: {str(e)}", exc_info=True
            )
            raise e

    def delete(self, file_path: str) -> bool:
        """
        Supprime un fichier.

        Args:
            file_path: Chemin du fichier à supprimer

        Returns:
            True si le fichier a été supprimé, False sinon
        """
        if not file_path:
            return False

        # Convertir en chemin absolu si nécessaire
        path = Path(file_path)
        if not path.is_absolute():
            path = Path(os.getcwd()) / path

        # Vérifier si le fichier existe et est dans le dossier d'upload
        if path.exists() and str(path).startswith(
            str(Path(os.getcwd()) / self.base_upload_path)
        ):
            os.remove(path)
            return True
        return False

    def get_file_url(self, file_path: str) -> str:
        """
        Convertit un chemin de fichier en URL accessible.

        Args:
            file_path: Chemin relatif du fichier

        Returns:
            L'URL pour accéder au fichier
        """
        if not file_path:
            return None

        # Convertir le chemin en URL relative
        path = Path(file_path)
        # Supposons que tous les fichiers dans public/ sont accessibles via /
        if "public/" in file_path:
            return "/" + str(path).split("public/", 1)[1]
        return "/" + str(path)
