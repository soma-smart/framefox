from dataclasses import dataclass, field
from typing import Any, Dict, List

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


@dataclass
class FormField:
    """Represents a form field."""

    name: str
    type: "FormType"
    options: Dict[str, Any] = field(default_factory=dict)
    value: Any = None
    errors: List[str] = field(default_factory=list)
    submitted: bool = False

    def __post_init__(self):
        if hasattr(self.type, "set_name"):
            self.type.set_name(self.name)

    def set_value(self, value: Any) -> None:
        self.submitted = True
        try:
            if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
                import json

                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass

            self.value = self.type.transform_to_model(value)
        except Exception as e:
            self.errors.append(str(e))

    def get_value(self) -> Any:
        return self.value

    def validate(self) -> bool:
        self.errors = []

        if self.options.get("required", False) and not self.value and self.value is not False:
            self.errors.append(f"The field {self.name} is required")
            return False

        for validator in self.options.get("validators", []):
            if not validator.validate(self.value):
                self.errors.append(validator.message)
                return False

        return len(self.errors) == 0

    def is_submitted(self) -> bool:
        return self.submitted
