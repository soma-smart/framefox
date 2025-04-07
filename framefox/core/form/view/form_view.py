from typing import Any, Dict, Optional

from framefox.core.form.form import Form
from framefox.core.form.view.form_view_field import FormViewField

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FormView:
    """View for rendering a form."""

    def __init__(self, form: Form):
        self.form = form
        self.fields = {}

        for name, field in form.fields.items():
            self.fields[name] = FormViewField(field)

    def get_field(self, name: str) -> Optional[FormViewField]:
        """Retrieve the view of a field by its name."""
        return self.fields.get(name)

    def get_fields(self) -> Dict[str, FormViewField]:
        """Retrieve all field views."""
        return self.fields

    def get_errors(self) -> Dict[str, Any]:
        """Retrieve form errors."""
        return self.form.errors

    def has_errors(self) -> bool:
        """Check if the form has errors."""
        return len(self.form.errors) > 0

    def is_submitted(self) -> bool:
        """Check if the form has been submitted."""
        return self.form.submitted

    def is_valid(self) -> bool:
        """Check if the form is valid."""
        return self.form.valid
