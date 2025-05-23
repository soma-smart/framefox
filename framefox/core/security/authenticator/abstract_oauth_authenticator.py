import logging
from abc import abstractmethod
from typing import Any, Dict, Optional

from fastapi import Request
from fastapi.responses import Response

from framefox.core.di.service_container import ServiceContainer
from framefox.core.security.authenticator.abstract_authenticator import (
    AbstractAuthenticator,
)
from framefox.core.security.authenticator.oauth_authenticator_interface import (
    OAuthAuthenticatorInterface,
)

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class AbstractOAuthAuthenticator(AbstractAuthenticator, OAuthAuthenticatorInterface):
    """
    Minimal abstract class for OAuth authenticators.
    Contains only the essential methods used by the OAuth handler.
    """

    oauth_provider_name = "generic"

    client_id = None
    client_secret = None
    redirect_uri = None
    scopes = []

    authorization_endpoint = None
    token_endpoint = None
    userinfo_endpoint = None

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(f"OAUTH_{self.oauth_provider_name.upper()}")
        self.service_container = ServiceContainer()

    async def authenticate(self, request: Request, firewall_name: str = None) -> Optional[Response]:
        self.logger.debug("Default authenticate method called in AbstractOAuthAuthenticator")
        return None

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_oauth_user_data(self, access_token: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def map_oauth_data_to_user(self, oauth_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def on_auth_success(self, token: str) -> Response:
        pass

    @abstractmethod
    def on_auth_failure(self, request: Request, reason: str = None) -> Response:
        pass

    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        pass

    def _get_oauth_config(self, firewall_name: str) -> Dict[str, str]:
        firewall_config = self.settings.get_firewall_config(firewall_name)
        oauth_config = firewall_config.get("oauth", {})

        if not oauth_config:
            base_path = firewall_config.get("login_path", f"/{self.oauth_provider_name}-login")
            oauth_config = {
                "init_path": base_path,
                "callback_path": f"/{self.oauth_provider_name}-callback",
            }

        return oauth_config
