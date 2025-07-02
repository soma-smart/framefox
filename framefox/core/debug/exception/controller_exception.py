from framefox.core.debug.exception.base_exception import FramefoxException

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ControllerException(FramefoxException):
    """Base controller exception"""

    pass


class ControllerNotFoundError(ControllerException):
    """Raised when a controller cannot be found"""

    def __init__(self, controller_name: str, searched_paths: list = None, original_error=None):
        self.controller_name = controller_name
        self.searched_paths = searched_paths or []

        if searched_paths:
            paths_str = ", ".join(str(path) for path in searched_paths)
            message = f"Controller '{controller_name}' not found. Searched in: {paths_str}"
        else:
            message = f"Controller '{controller_name}' not found"

        super().__init__(message, original_error, "CONTROLLER_NOT_FOUND")


class ControllerInstantiationError(ControllerException):
    """Raised when a controller cannot be instantiated"""

    def __init__(self, controller_class: str, reason: str = None, original_error=None):
        self.controller_class = controller_class
        self.reason = reason

        if reason:
            message = f"Failed to instantiate controller '{controller_class}': {reason}"
        else:
            message = f"Failed to instantiate controller '{controller_class}'"

        super().__init__(message, original_error, "CONTROLLER_INSTANTIATION_ERROR")


class ControllerDependencyError(ControllerException):
    """Raised when controller dependencies cannot be resolved"""

    def __init__(self, controller_class: str, dependency_name: str, original_error=None):
        self.controller_class = controller_class
        self.dependency_name = dependency_name
        message = f"Failed to resolve dependency '{dependency_name}' for controller '{controller_class}'"
        super().__init__(message, original_error, "CONTROLLER_DEPENDENCY_ERROR")


class InvalidControllerError(ControllerException):
    """Raised when a controller class is invalid"""

    def __init__(self, controller_class: str, reason: str = None, original_error=None):
        self.controller_class = controller_class
        self.reason = reason

        if reason:
            message = f"Invalid controller '{controller_class}': {reason}"
        else:
            message = f"Invalid controller '{controller_class}'"

        super().__init__(message, original_error, "INVALID_CONTROLLER")


class ControllerModuleError(ControllerException):
    """Raised when controller module cannot be loaded"""

    def __init__(self, module_path: str, original_error=None):
        self.module_path = module_path
        message = f"Failed to load controller module: {module_path}"
        super().__init__(message, original_error, "CONTROLLER_MODULE_ERROR")


class DuplicateControllerError(ControllerException):
    """Raised when multiple controllers with the same name are found"""

    def __init__(self, controller_name: str, file_paths: list, original_error=None):
        self.controller_name = controller_name
        self.file_paths = file_paths
        paths_str = ", ".join(str(path) for path in file_paths)
        message = f"Duplicate controller '{controller_name}' found in multiple files: {paths_str}"
        super().__init__(message, original_error, "DUPLICATE_CONTROLLER")


class ControllerRegistrationError(ControllerException):
    """Raised when controller registration fails"""

    def __init__(self, controller_name: str, reason: str = None, original_error=None):
        self.controller_name = controller_name
        self.reason = reason

        if reason:
            message = f"Failed to register controller '{controller_name}': {reason}"
        else:
            message = f"Failed to register controller '{controller_name}'"

        super().__init__(message, original_error, "CONTROLLER_REGISTRATION_ERROR")
