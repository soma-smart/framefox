import logging
import os
import uuid
from pathlib import Path
from typing import List

from fastapi import UploadFile

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FileManager:
    """Service for managing uploaded files."""

    def __init__(self):
        """
        Initializes the file manager with a base directory.
        """
        project_root = os.getcwd()
        self.base_upload_path = Path(project_root)

        os.makedirs(self.base_upload_path, exist_ok=True)

        self.logger = logging.getLogger("FILE_MANAGER")

    async def save(
        self,
        file: UploadFile,
        subdirectory: str = None,
        rename: bool = True,
        allowed_extensions: List[str] = None,
    ) -> str:
        """
        Saves an uploaded file and returns its relative path.
        """
        if not file:
            self.logger.warning("Attempt to upload with a None file")
            return None

        original_filename = file.filename
        extension = os.path.splitext(original_filename)[1].lower()

        if allowed_extensions and extension not in allowed_extensions:
            raise ValueError(f"Unauthorized file type. Allowed extensions: {', '.join(allowed_extensions)}")

        dest_dir = self.base_upload_path
        if subdirectory:
            subdirectory = subdirectory.strip("/")
            dest_dir = dest_dir / subdirectory

        os.makedirs(dest_dir, exist_ok=True)

        if rename:
            filename = f"{uuid.uuid4()}{extension}"
        else:
            filename = original_filename

        file_path = dest_dir / filename
        abs_file_path = os.path.abspath(file_path)

        try:
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)

            try:
                rel_path = str(file_path.relative_to(os.getcwd()))
            except ValueError:

                if os.path.isabs(file_path):
                    base_path = Path(os.getcwd())
                    rel_path = str(file_path).replace(str(base_path) + "/", "")
                else:
                    rel_path = str(file_path)
            return rel_path

        except Exception as e:
            self.logger.error(f"Error saving file: {str(e)}", exc_info=True)
            raise e

    def delete(self, file_path: str) -> bool:
        """
        Deletes a file.

        Args:
            file_path: Path of the file to delete

        Returns:
            True if the file was deleted, False otherwise
        """
        if not file_path:
            return False

        path = Path(file_path)
        if not path.is_absolute():
            path = Path(os.getcwd()) / path
        if path.exists() and str(path).startswith(str(Path(os.getcwd()) / self.base_upload_path)):
            os.remove(path)
            return True
        return False

    def get_file_url(self, file_path: str) -> str:
        """
        Converts a file path to an accessible URL.

        Args:
            file_path: Relative path of the file

        Returns:
            The URL to access the file
        """
        if not file_path:
            return None
        path = Path(file_path)
        if "public/" in file_path:
            return "/" + str(path).split("public/", 1)[1]
        return "/" + str(path)
