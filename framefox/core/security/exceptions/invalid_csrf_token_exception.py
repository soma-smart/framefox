"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class InvalidCsrfTokenException(Exception):
    """
    Exception raised for invalid CSRF tokens.

    Attributes:
        message (str): Explanation of the error.
    """

    def __init__(self, message: str = "Invalid CSRF token"):
        self.message = message
        super().__init__(self.message)
