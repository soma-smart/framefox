from framefox.core.debug.exception.base_exception import FramefoxException

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class AuthException(FramefoxException):
    """Base authentication exception"""

    pass


class AuthenticationError(AuthException):
    """Raised when authentication fails"""

    def __init__(self, message="Authentication failed", original_error=None):
        super().__init__(message, original_error, "AUTH_FAILED")


class AuthorizationError(AuthException):
    """Raised when user doesn't have permission"""

    def __init__(self, resource: str = None, action: str = None, original_error=None):
        if resource and action:
            message = f"Access denied: cannot {action} {resource}"
        else:
            message = "Access denied: insufficient permissions"
        self.resource = resource
        self.action = action
        super().__init__(message, original_error, "AUTH_PERMISSION_DENIED")


class TokenExpiredError(AuthException):
    """Raised when authentication token has expired"""

    def __init__(self, token_type: str = "token", original_error=None):
        message = f"Authentication {token_type} has expired"
        self.token_type = token_type
        super().__init__(message, original_error, "AUTH_TOKEN_EXPIRED")


class InvalidTokenError(AuthException):
    """Raised when authentication token is invalid"""

    def __init__(self, token_type: str = "token", original_error=None):
        message = f"Invalid authentication {token_type}"
        self.token_type = token_type
        super().__init__(message, original_error, "AUTH_TOKEN_INVALID")


class UserNotFoundError(AuthException):
    """Raised when user is not found"""

    def __init__(self, identifier: str = None, original_error=None):
        message = f"User not found: {identifier}" if identifier else "User not found"
        self.identifier = identifier
        super().__init__(message, original_error, "AUTH_USER_NOT_FOUND")


class AccountDisabledError(AuthException):
    """Raised when user account is disabled"""

    def __init__(self, username: str = None, original_error=None):
        message = f"Account disabled: {username}" if username else "Account is disabled"
        self.username = username
        super().__init__(message, original_error, "AUTH_ACCOUNT_DISABLED")
