from typing import List

from framefox.core.debug.exception.base_exception import FramefoxException

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class HttpException(FramefoxException):
    """Base HTTP exception"""

    def __init__(self, message: str, status_code: int = 500, original_error=None):
        self.status_code = status_code
        super().__init__(message, original_error, f"HTTP_{status_code}")


class BadRequestError(HttpException):
    """Raised for 400 Bad Request errors"""

    def __init__(self, message="Bad request", original_error=None):
        super().__init__(message, 400, original_error)


class UnauthorizedError(HttpException):
    """Raised for 401 Unauthorized errors"""

    def __init__(self, message="Unauthorized", original_error=None):
        super().__init__(message, 401, original_error)


class ForbiddenError(HttpException):
    """Raised for 403 Forbidden errors"""

    def __init__(self, message="Forbidden", original_error=None):
        super().__init__(message, 403, original_error)


class NotFoundError(HttpException):
    """Raised for 404 Not Found errors"""

    def __init__(self, resource: str = None, original_error=None):
        message = f"Resource not found: {resource}" if resource else "Resource not found"
        self.resource = resource
        super().__init__(message, 404, original_error)


class MethodNotAllowedError(HttpException):
    """Raised for 405 Method Not Allowed errors"""

    def __init__(self, method: str, allowed_methods: List[str] = None, original_error=None):
        self.method = method
        self.allowed_methods = allowed_methods or []
        if allowed_methods:
            message = f"Method {method} not allowed. Allowed methods: {', '.join(allowed_methods)}"
        else:
            message = f"Method {method} not allowed"
        super().__init__(message, 405, original_error)


class ConflictError(HttpException):
    """Raised for 409 Conflict errors"""

    def __init__(self, message="Conflict", original_error=None):
        super().__init__(message, 409, original_error)


class UnprocessableEntityError(HttpException):
    """Raised for 422 Unprocessable Entity errors"""

    def __init__(self, message="Unprocessable entity", original_error=None):
        super().__init__(message, 422, original_error)


class TooManyRequestsError(HttpException):
    """Raised for 429 Too Many Requests errors"""

    def __init__(self, retry_after: int = None, original_error=None):
        self.retry_after = retry_after
        message = f"Too many requests. Retry after {retry_after} seconds" if retry_after else "Too many requests"
        super().__init__(message, 429, original_error)
