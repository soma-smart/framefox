import secrets

from fastapi import Request

from framefox.core.security.exceptions.invalid_csrf_token_exception import \
    InvalidCsrfTokenException

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class CsrfTokenBadge:
    """
    This module provides the CsrfTokenBadge class for CSRF token validation.

    Classes:
        CsrfTokenBadge: A class to handle CSRF token validation.

    Exceptions:
        InvalidCsrfTokenException: Raised when the CSRF token is invalid.
    """

    def __init__(self, csrf_token: str):
        self.token = csrf_token

    def validate_csrf_token(self, request: Request):
        stored_token = request.cookies.get("csrf_token", "")
        if not secrets.compare_digest(self.token, stored_token):
            raise InvalidCsrfTokenException()
        return True
