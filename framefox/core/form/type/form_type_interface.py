from abc import ABC, abstractmethod
from typing import Any, Dict

from framefox.core.form.form_builder import FormBuilder


"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FormTypeInterface(ABC):
    """Interface to define form types."""

    @abstractmethod
    def build_form(self, builder: FormBuilder) -> None:
        """
        Configure the form with the builder.

        This method is called to define the fields of the form.
        """
        pass

    def get_options(self) -> Dict[str, Any]:
        """
        Returns the default options for the form.
        """
        return {}
