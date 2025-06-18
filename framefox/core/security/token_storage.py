import logging
from typing import Any, Dict, Optional

from framefox.core.di.service_container import ServiceContainer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class TokenStorage:
    """
    Stores and retrieves the authentication token.
    This class centralizes the management of security tokens.
    """

    def __init__(self):
        self.container = ServiceContainer()
        self.session = self.container.get_by_name("Session")
        self.logger = logging.getLogger("TOKEN_STORAGE")

    def get_token(self) -> Optional[str]:
        """Retrieves the current authentication token."""
        return self.session.get("access_token")

    def set_token(self, token: str) -> None:
        """Sets the current authentication token."""
        self.session.set("access_token", token)
        self.session.save()
        self.logger.debug("Authentication token set in session")

    def clear_token(self) -> None:
        """Removes the authentication token."""
        if self.session.has("access_token"):
            self.session.remove("access_token")
            self.session.save()
            self.logger.debug("Authentication token removed from session")

    def get_payload(self) -> Optional[Dict[str, Any]]:
        """Retrieves the decoded data from the token."""
        token = self.get_token()
        if not token:
            return None
        token_manager = self.container.get_by_name("TokenManager")
        return token_manager.decode_token(token)
