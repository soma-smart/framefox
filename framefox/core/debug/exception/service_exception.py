from framefox.core.debug.exception.base_exception import FramefoxException

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ServiceException(FramefoxException):
    """Base service exception"""

    pass


class ServiceUnavailableError(ServiceException):
    """Raised when a service is unavailable"""

    def __init__(self, service_name: str, original_error=None):
        self.service_name = service_name
        message = f"Service unavailable: {service_name}"
        super().__init__(message, original_error, "SERVICE_UNAVAILABLE")


class ExternalServiceError(ServiceException):
    """Raised when external service fails"""

    def __init__(self, service_name: str, operation: str = None, original_error=None):
        self.service_name = service_name
        self.operation = operation
        if operation:
            message = f"External service error: {service_name} - {operation}"
        else:
            message = f"External service error: {service_name}"
        super().__init__(message, original_error, "EXTERNAL_SERVICE_ERROR")


class TimeoutError(ServiceException):
    """Raised when operation times out"""

    def __init__(self, operation: str = None, timeout_seconds: int = None, original_error=None):
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        if operation and timeout_seconds:
            message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        elif operation:
            message = f"Operation '{operation}' timed out"
        else:
            message = "Operation timed out"
        super().__init__(message, original_error, "TIMEOUT_ERROR")


class RateLimitExceededError(ServiceException):
    """Raised when rate limit is exceeded"""

    def __init__(self, limit: int = None, window: str = None, original_error=None):
        self.limit = limit
        self.window = window
        if limit and window:
            message = f"Rate limit exceeded: {limit} requests per {window}"
        else:
            message = "Rate limit exceeded"
        super().__init__(message, original_error, "RATE_LIMIT_EXCEEDED")
