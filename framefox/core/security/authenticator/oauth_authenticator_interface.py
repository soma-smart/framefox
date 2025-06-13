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
    """
    Interface for OAuth authenticators.
    
    This interface extends the base AuthenticatorInterface to provide
    OAuth-specific functionality for user authentication via external providers.
    """

    is_oauth_authenticator = True

    @abstractmethod
    async def get_user_data_from_provider(self, access_token: str) -> Dict[str, Any]:
        """Retrieves and formats user data from the OAuth provider"""
        pass

    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        """Builds the authorization URL with the necessary parameters"""
        pass