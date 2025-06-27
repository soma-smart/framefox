from framefox.core.debug.exception.base_exception import FramefoxException

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TemplateException(FramefoxException):
    """Base template exception"""

    pass


class TemplateNotFoundError(TemplateException):
    """Raised when template file is not found"""

    def __init__(self, template_name: str, original_error=None):
        self.template_name = template_name
        message = f"Template not found: {template_name}"
        super().__init__(message, original_error, "TEMPLATE_NOT_FOUND")


class TemplateRenderError(TemplateException):
    """Raised when template rendering fails"""

    def __init__(self, template_name: str, error_details: str = None, original_error=None):
        self.template_name = template_name
        self.error_details = error_details
        if error_details:
            message = f"Template rendering failed for '{template_name}': {error_details}"
        else:
            message = f"Template rendering failed for '{template_name}'"
        super().__init__(message, original_error, "TEMPLATE_RENDER_ERROR")


class TemplateSyntaxError(TemplateException):
    """Raised when template has syntax errors"""

    def __init__(self, template_name: str, line_number: int = None, original_error=None):
        self.template_name = template_name
        self.line_number = line_number
        if line_number:
            message = f"Template syntax error in '{template_name}' at line {line_number}"
        else:
            message = f"Template syntax error in '{template_name}'"
        super().__init__(message, original_error, "TEMPLATE_SYNTAX_ERROR")
