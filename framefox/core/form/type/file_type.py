import os
from typing import Any, Dict

from fastapi import UploadFile

from framefox.core.file.file_manager import FileManager
from framefox.core.form.type.abstract_form_type import AbstractFormType

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FileType(AbstractFormType):
    """Field type for file uploads."""

    def __init__(self, options: Dict[str, Any] = None):
        super().__init__(options or {})

        self.options.setdefault("attr", {})
        self.options.setdefault("multiple", False)
        self.options.setdefault("accept", "")
        self.options.setdefault("storage_path", "public/uploads")
        self.options.setdefault("max_file_size", 5 * 1024 * 1024)
        self.options.setdefault("allowed_extensions", [])
        self.options.setdefault("rename", True)

        if "class" not in self.options["attr"]:
            self.options["attr"]["class"] = "form-control"
        else:
            self.options["attr"]["class"] += " form-control"

    async def handle_upload(self, upload_file: UploadFile) -> str:
        """Handles an uploaded file and returns the storage path."""
        if not upload_file:
            return None

        await upload_file.seek(0)
        content = await upload_file.read()
        file_size = len(content)
        await upload_file.seek(0)

        if file_size > self.options.get("max_file_size"):
            raise ValueError(f"The file is too large. Maximum: {self.options.get('max_file_size') / 1024 / 1024}MB")

        original_filename = upload_file.filename
        extension = os.path.splitext(original_filename)[1].lower()
        allowed_extensions = self.options.get("allowed_extensions")

        if allowed_extensions and extension not in allowed_extensions:
            raise ValueError(f"File type not allowed. Allowed extensions: {', '.join(allowed_extensions)}")

        file_manager = FileManager()

        storage_path = self.options.get("storage_path")

        os.makedirs(storage_path, exist_ok=True)

        try:
            file_path = await file_manager.save(
                file=upload_file,
                subdirectory=storage_path,
                rename=self.options.get("rename", True),
                allowed_extensions=allowed_extensions,
            )

            return file_path
        except Exception as e:

            raise e

    def transform_to_model(self, value: Any) -> Any:
        """For files, the transformation is done asynchronously in Form.handle_request with handle_upload."""
        return value

    def transform_to_view(self, value: Any) -> Any:
        """Transforms the model value to a view value."""
        return value

    def get_block_prefix(self) -> str:
        """Returns the block prefix for rendering."""
        return "file"

    def render(self, options: Dict[str, Any] = None) -> str:
        """HTML rendering of the file field."""
        options = options or {}
        attrs = self.options.get("attr", {}).copy()
        attrs.update(
            {
                "name": self.name,
                "id": self.get_id(),
                "type": "file",
            }
        )

        if self.options.get("multiple"):
            attrs["multiple"] = "multiple"
            if not attrs["name"].endswith("[]"):
                attrs["name"] += "[]"

        if self.options.get("accept"):
            attrs["accept"] = self.options.get("accept")

        if self.options.get("required"):
            attrs["required"] = "required"

        if self.has_errors():
            if "class" in attrs:
                attrs["class"] += " is-invalid"
            else:
                attrs["class"] = "is-invalid"

        attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())

        html = f"<input {attr_str}>"

        current_value = self.get_value()
        if current_value:
            html += f'<div class="mt-1"><small class="text-muted">Current file: {os.path.basename(current_value)}</small></div>'

        if self.has_errors():
            errors = self.get_errors()
            error_html = '<div class="invalid-feedback">'
            error_html += '<ul class="list-unstyled mb-0">'
            for error in errors:
                error_html += f"<li>{error}</li>"
            error_html += "</ul></div>"
            html += error_html

        help_text = self.options.get("help")
        if help_text:
            html += f'<small class="form-text text-muted">{help_text}</small>'

        return html
