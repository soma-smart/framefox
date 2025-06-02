from abc import ABC, abstractmethod
from typing import Any, Dict

from framefox.core.security.authenticator.authenticator_interface import (
    AuthenticatorInterface,
)

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class OAuthAuthenticatorInterface(AuthenticatorInterface, ABC):
    """Interface for OAuth authenticators"""

    is_oauth_authenticator = True

    @abstractmethod
    async def get_oauth_user_data(self, access_token: str) -> Dict[str, Any]:
        """Retrieves user data from the provider's API"""
        pass

    @abstractmethod
    def map_oauth_data_to_user(self, oauth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Maps OAuth data to the application's user fields"""
        pass

    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        """Builds the authorization URL with the necessary parameters"""
        pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchanges the authorization code for an access token"""
        pass
