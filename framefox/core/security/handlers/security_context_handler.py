import logging
from typing import Optional

from fastapi import Request

from framefox.core.request.request_stack import RequestStack

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""

AUTHENTICATION_ERROR = "auth_error"
LAST_USERNAME = "last_username"


class SecurityContextHandler:
    """
    Utility class to extract and manage authentication data from requests.

    It reads from and writes to the request state and session.
    """

    def __init__(self):
        """Initialize the context handler."""
        self.logger = logging.getLogger("SECURITY_CONTEXT")

    def get_request(self) -> Request:
        """Get the current request from RequestStack."""
        try:
            request = RequestStack.get_request()
            if request is None:
                raise ValueError("No request found in context")
            return request
        except Exception as e:
            self.logger.error(f"Error getting request: {str(e)}")
            raise ValueError("Cannot access current request") from e

    def _store_value(self, key: str, value: str) -> None:
        """
        Store a value in both request state and session for persistence.

        Args:
            key: The key to store the value under
            value: The value to store
        """
        try:
            request = self.get_request()

            # Store in request state for immediate access
            setattr(request.state, key, value)

            # Store in session for persistence across redirects
            if hasattr(request.state, "session_data"):
                request.state.session_data[key] = value

        except ValueError:
            self.logger.error(f"Failed to store {key}: no request in context")

    def _get_value(self, key: str, clear_value: bool = False) -> Optional[str]:
        """
        Get a value from request state or session.

        Args:
            key: The key to retrieve
            clear_value: Whether to clear the value after retrieval

        Returns:
            The value or None if not found
        """
        try:
            request = self.get_request()
            value = None

            # Try to get from request state first
            if hasattr(request.state, key):
                value = getattr(request.state, key)
                if clear_value:
                    delattr(request.state, key)

            # Fall back to session if not found in request state
            if not value and hasattr(request.state, "session_data"):
                session_data = request.state.session_data
                value = session_data.get(key)
                if value and clear_value:
                    session_data.pop(key, None)

            return value
        except ValueError:
            return None

    def _clear_value(self, key: str) -> None:
        """
        Clear a value from both request state and session.

        Args:
            key: The key to clear
        """
        try:
            request = self.get_request()

            # Clear from request state
            if hasattr(request.state, key):
                delattr(request.state, key)

            # Clear from session
            if hasattr(request.state, "session_data"):
                request.state.session_data.pop(key, None)

        except ValueError:
            self.logger.error(f"Failed to clear {key}: no request in context")

    # Authentication Error Methods
    def get_last_authentication_error(self, clear_error: bool = True) -> Optional[str]:
        """
        Get the last authentication error from request attributes or session.

        Args:
            clear_error: Whether to clear the error after retrieval

        Returns:
            The error message or None if no error was found
        """
        return self._get_value(AUTHENTICATION_ERROR, clear_error)

    def set_authentication_error(self, error: str) -> None:
        """
        Set authentication error in both request state and session.

        Args:
            error: The error message to store
        """
        self._store_value(AUTHENTICATION_ERROR, error)

    def clear_authentication_error(self) -> None:
        """Clear authentication error from both request state and session."""
        self._clear_value(AUTHENTICATION_ERROR)

    # Last Username Methods
    def get_last_username(self) -> str:
        """
        Get the last username used for authentication.

        Returns:
            The last username or empty string if not found
        """
        return self._get_value(LAST_USERNAME) or ""

    def set_last_username(self, username: str) -> None:
        """
        Store the username used for authentication.

        Args:
            username: The username to store
        """
        self._store_value(LAST_USERNAME, username)

    def clear_last_username(self) -> None:
        """Clear the last username from both request state and session."""
        self._clear_value(LAST_USERNAME)

    # Utility Methods
    def clear_all_authentication_data(self) -> None:
        """Clear all authentication-related data from request state and session."""
        self.clear_authentication_error()
        self.clear_last_username()

    def has_authentication_error(self) -> bool:
        """
        Check if there's an authentication error without clearing it.

        Returns:
            True if there's an authentication error, False otherwise
        """
        return self._get_value(AUTHENTICATION_ERROR, clear_value=False) is not None

    def get_authentication_context(self) -> dict:
        """
        Get all authentication context data without clearing it.

        Returns:
            Dictionary containing authentication context
        """
        return {
            "error": self._get_value(AUTHENTICATION_ERROR, clear_value=False),
            "last_username": self._get_value(LAST_USERNAME, clear_value=False),
            "has_error": self.has_authentication_error(),
        }
