from typing import Any, Dict, List

from framefox.core.debug.exception.base_exception import FramefoxException

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ValidationException(FramefoxException):
    """Base validation exception"""

    pass


class ValidationError(ValidationException):
    """Raised when input validation fails"""

    def __init__(self, field: str, message: str, value: Any = None, original_error=None):
        self.field = field
        self.value = value
        self.validation_message = message
        full_message = f"Validation failed for field '{field}': {message}"
        super().__init__(full_message, original_error, "VALIDATION_ERROR")


class MultipleValidationErrors(ValidationException):
    """Raised when multiple validation errors occur"""

    def __init__(self, errors: Dict[str, List[str]], original_error=None):
        self.errors = errors
        error_count = sum(len(field_errors) for field_errors in errors.values())
        message = f"Multiple validation errors ({error_count} errors)"
        super().__init__(message, original_error, "VALIDATION_MULTIPLE_ERRORS")


class RequiredFieldError(ValidationException):
    """Raised when a required field is missing"""

    def __init__(self, field: str, original_error=None):
        self.field = field
        message = f"Required field missing: {field}"
        super().__init__(message, original_error, "VALIDATION_REQUIRED_FIELD")


class InvalidFormatError(ValidationException):
    """Raised when data format is invalid"""

    def __init__(self, field: str, expected_format: str, original_error=None):
        self.field = field
        self.expected_format = expected_format
        message = f"Invalid format for field '{field}': expected {expected_format}"
        super().__init__(message, original_error, "VALIDATION_INVALID_FORMAT")


class ValueRangeError(ValidationException):
    """Raised when value is outside allowed range"""

    def __init__(self, field: str, value: Any, min_val: Any = None, max_val: Any = None, original_error=None):
        self.field = field
        self.value = value
        self.min_val = min_val
        self.max_val = max_val

        if min_val is not None and max_val is not None:
            message = f"Value '{value}' for field '{field}' must be between {min_val} and {max_val}"
        elif min_val is not None:
            message = f"Value '{value}' for field '{field}' must be at least {min_val}"
        elif max_val is not None:
            message = f"Value '{value}' for field '{field}' must be at most {max_val}"
        else:
            message = f"Value '{value}' for field '{field}' is out of range"

        super().__init__(message, original_error, "VALIDATION_VALUE_RANGE")
