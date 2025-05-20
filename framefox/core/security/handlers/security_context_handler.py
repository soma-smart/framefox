from typing import Optional
import logging
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
    
    it reads from and writes to the request state and session.
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
    
    def get_last_authentication_error(self, clear_error: bool = True) -> Optional[str]:
        """
        Get the last authentication error from request attributes or session.
        
        Args:
            clear_error: Whether to clear the error after retrieval
            
        Returns:
            The error message or None if no error was found
        """
        try:
            request = self.get_request()
            error = None
            
            if hasattr(request.state, AUTHENTICATION_ERROR):
                error = getattr(request.state, AUTHENTICATION_ERROR)
                if clear_error:
                    delattr(request.state, AUTHENTICATION_ERROR)
            if not error and hasattr(request.state, "session_data"):
                session_data = request.state.session_data
                error = session_data.get(AUTHENTICATION_ERROR)
                if error and clear_error:
                    session_data.pop(AUTHENTICATION_ERROR, None)
            
            return error
        except ValueError:
            return None
    
    def set_authentication_error(self, error: str) -> None:
        """
        Set authentication error in both request state and session.
        
        Args:
            error: The error message to store
        """
        try:
            request = self.get_request()
            
            # Store in request state
            setattr(request.state, AUTHENTICATION_ERROR, error)
            
            # Also store in session for persistence across redirects
            if hasattr(request.state, "session_data"):
                request.state.session_data[AUTHENTICATION_ERROR] = error
                
        except ValueError:
            self.logger.error("Failed to store authentication error: no request in context")
    
    def get_last_username(self) -> str:
        """
        Get the last username used for authentication.
        
        Returns:
            The last username or empty string if not found
        """
        try:
            request = self.get_request()
            
            if hasattr(request.state, LAST_USERNAME):
                return getattr(request.state, LAST_USERNAME) or ""
            if hasattr(request.state, "session_data"):
                return request.state.session_data.get(LAST_USERNAME, "")
                
            return ""
        except ValueError:
            return ""
    
    def set_last_username(self, username: str) -> None:
        """
        Store the username used for authentication.
        
        Args:
            username: The username to store
        """
        try:
            request = self.get_request()
            setattr(request.state, LAST_USERNAME, username)
            
            if hasattr(request.state, "session_data"):
                request.state.session_data[LAST_USERNAME] = username
                
        except ValueError:
            self.logger.error("Failed to store last username: no request in context")