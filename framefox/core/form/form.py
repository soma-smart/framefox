from typing import Any, Dict, Optional

from fastapi import Request

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class Form:
    """Main class representing a form."""

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

    async def handle_request(self, request: Request) -> bool:
        """Handles form submission from an HTTP request."""
        if request.method != "POST":
            return False

        self.submitted = True
        form_data = await request.form()

        data_dict = {}
        file_dict = {}

        for key, value in form_data.items():
            if key.endswith("[]"):
                base_key = key[:-2]
                data_dict[base_key] = form_data.getlist(key)
            else:
                if hasattr(value, "filename") and hasattr(value, "file"):
                    file_dict[key] = value
                else:
                    values = form_data.getlist(key)
                    if len(values) > 1:
                        data_dict[key] = values
                    else:
                        data_dict[key] = value

        self.assign_data(data_dict)
        await self._handle_file_uploads(file_dict)

        for name, field in self.fields.items():
            if field.options.get("required", False):
                is_file_field = hasattr(field.type, "get_block_prefix") and field.type.get_block_prefix() == "file"
                file_already_exists = is_file_field and field.get_value() is not None

                if not is_file_field or (is_file_field and not file_already_exists):
                    if name not in data_dict and name not in file_dict:
                        field.errors.append(f"The field {field.options.get('label', name)} is required")

        self.valid = self.validate()

        if self.valid and self.data:
            self._apply_data_to_model()

        return self.valid

    async def _handle_file_uploads(self, file_dict: Dict[str, Any]) -> None:
        """Handles uploaded files."""
        for field_name, upload_file in file_dict.items():
            if field_name in self.fields:
                field = self.fields[field_name]
                if hasattr(field.type, "handle_upload"):
                    try:
                        if field.options.get("multiple", False) and isinstance(upload_file, list):
                            file_paths = []
                            for file in upload_file:
                                file_path = await field.type.handle_upload(file)
                                file_paths.append(file_path)
                            field.value = file_paths
                            field.submitted = True
                        else:
                            file_path = await field.type.handle_upload(upload_file)
                            field.value = file_path
                            field.submitted = True

                    except Exception as e:
                        field.errors.append(str(e))

    def _apply_data_to_model(self):
        """Applies form data to the model."""
        for name, field in self.fields.items():
            if hasattr(self.data, name) and field.is_submitted():
                value = field.get_value()
                if field.options.get("required", False) and value is None:
                    self.valid = False
                    return
                setattr(self.data, name, value)

    def assign_data(self, data: Dict[str, Any]) -> None:
        """Assigns data to form fields."""
        for name, field in self.fields.items():
            if name in data:
                field.set_value(data[name])

    def validate(self) -> bool:
        """Validates all form fields."""
        valid = True
        self.errors = {}

        for name, field in self.fields.items():
            if field.options.get("required", False):
                value = field.get_value()
                if value is None or (isinstance(value, str) and value.strip() == ""):
                    field.errors.append(f"The field {field.options.get('label', name)} is required")
                    valid = False
                    self.errors[name] = field.errors
                    continue

            if not field.validate():
                self.errors[name] = field.errors
                valid = False

        return valid

    def get_data(self) -> Any:
        """Returns the object with form data."""
        if hasattr(self.data, "__dict__"):
            for name, field in self.fields.items():
                if hasattr(self.data, name) and field.is_submitted():
                    value = field.get_value()
                    setattr(self.data, name, value)
            return self.data
        else:
            result = {}
            for name, field in self.fields.items():
                if field.is_submitted():
                    result[name] = field.get_value()
            return result

    def create_view(self) -> "FormView":
        """Creates a view for rendering the form."""
        from framefox.core.form.view.form_view import FormView

        return FormView(self)

    def is_valid(self) -> bool:
        """Indicates if the form is valid."""
        return self.valid

    def is_submitted(self) -> bool:
        """Indicates if the form has been submitted."""
        return self.submitted
