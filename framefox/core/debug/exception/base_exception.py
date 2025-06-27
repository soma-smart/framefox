"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FramefoxException(Exception):
    """Base exception for all Framefox-specific errors"""

    def __init__(self, message: str, original_error=None, error_code: str = None):
        self.message = message
        self.original_error = original_error
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)


class ConfigurationException(FramefoxException):
    """Raised when there's a configuration error"""

    pass


class DevelopmentException(FramefoxException):
    """Raised during development for debugging purposes"""

    pass
