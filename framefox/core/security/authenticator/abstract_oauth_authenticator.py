import base64
import hashlib
import secrets
from abc import abstractmethod
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import Request

from framefox.core.request.session.session import Session
from framefox.core.security.authenticator.abstract_authenticator import (
    AbstractAuthenticator,
)
from framefox.core.security.authenticator.oauth_authenticator_interface import (
    OAuthAuthenticatorInterface,
)
from framefox.core.security.passport.passport import Passport
from framefox.core.security.passport.user_badge import UserBadge

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class AbstractOAuthAuthenticator(AbstractAuthenticator, OAuthAuthenticatorInterface):
    """
    Abstract OAuth authenticator helper class.

    This class provides OAuth authentication flow helpers but does NOT define
    the authenticate, on_auth_success, or on_auth_failure methods.
    Users must implement these methods in their generated authenticator.

    Attributes:
        oauth_provider_name (str): Name of the OAuth provider
        authorization_endpoint (str): OAuth authorization URL
        token_endpoint (str): OAuth token exchange URL
        userinfo_endpoint (str): User information retrieval URL
        scopes (list): List of OAuth scopes to request
        client_id (str): OAuth client ID
        client_secret (str): OAuth client secret
        redirect_uri (str): OAuth redirect URI
        tenant_id (str): Tenant ID for multi-tenant providers (e.g., Microsoft)
        default_roles (list): Default roles assigned to OAuth users
    """

    oauth_provider_name = "generic"
    authorization_endpoint = None
    token_endpoint = None
    userinfo_endpoint = None
    scopes = ["email"]

    def __init__(self, session: Session):
        super().__init__()
        self.session = session
        self.is_oauth_authenticator = True
        self._load_oauth_config()

    def _load_oauth_config(self):
        """Load OAuth configuration from security.yaml"""
        firewalls = self.settings.firewalls
        oauth_config = {}

        for firewall_name, firewall_data in firewalls.items():
            if firewall_data.get("oauth"):
                oauth_config = firewall_data.get("oauth", {})
                break

        self.client_id = oauth_config.get("client_id")
        self.client_secret = oauth_config.get("client_secret")
        self.redirect_uri = oauth_config.get("redirect_uri")
        self.tenant_id = oauth_config.get("tenant_id")
        self.default_roles = oauth_config.get("default_roles", ["ROLE_USER"])

    def _build_endpoint_url(self, base_url: str) -> str:
        """
        Build endpoint URL by replacing {tenant} with tenant_id if provided
        """
        if self.tenant_id and "{tenant}" in base_url:
            return base_url.replace("{tenant}", self.tenant_id)
        elif "{tenant}" in base_url:
            return base_url.replace("{tenant}", "common")
        return base_url

    async def handle_oauth_callback(self, request: Request) -> Optional[Passport]:
        """Handle OAuth callback with scope and nonce validation"""
        code = request.query_params.get("code")
        scope_param = request.query_params.get("scope", "")

        if not self._validate_granted_scopes(scope_param):
            self.logger.warning(f"Insufficient scopes granted: {scope_param}")
            return None

        try:
            token_data = await self._exchange_code_for_token(code)

            if "id_token" in token_data:
                if not self._validate_id_token_nonce(token_data["id_token"]):
                    self.logger.warning("ID token nonce validation failed")
                    return None

            user_data = await self.get_user_data_from_provider(token_data["access_token"])

            passport = Passport(
                user_badge=UserBadge(user_data["email"]),
                password_credentials=None,
                csrf_token_badge=None,
                provider_info=None,
            )

            passport._oauth_authenticator = self
            passport._oauth_user_data = user_data

            return passport
        except Exception as e:
            self.logger.error(f"OAuth callback error: {e}")
            return None

    async def _exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token with PKCE"""
        token_url = self._build_endpoint_url(self.token_endpoint)

        code_verifier = self.session.get("oauth_code_verifier")

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }

        if code_verifier:
            data["code_verifier"] = code_verifier
            self.session.remove("oauth_code_verifier")
            self.session.save()

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            return response.json()

    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL with PKCE and nonce"""
        auth_url = self._build_endpoint_url(self.authorization_endpoint)

        code_verifier, code_challenge = self.generate_pkce_challenge()

        nonce = secrets.token_urlsafe(32)

        self.session.set("oauth_code_verifier", code_verifier)
        self.session.set("oauth_nonce", nonce)
        self.session.save()

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "scope": " ".join(self.scopes),
            "response_type": "code",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "nonce": nonce,
        }
        return f"{auth_url}?{urlencode(params)}"

    def generate_pkce_challenge(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge"""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")
        code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode("utf-8")).digest()).decode("utf-8").rstrip("=")
        return code_verifier, code_challenge

    def _validate_granted_scopes(self, granted_scopes_str: str) -> bool:
        """
        Validate that granted scopes by provider are sufficient

        Args:
            granted_scopes_str: Granted scopes as space-separated string

        Returns:
            bool: True if scopes are sufficient
        """
        if not granted_scopes_str:
            self.logger.debug("No scope parameter in callback - assuming scopes are granted")
            return True

        granted_scopes = set(granted_scopes_str.split())
        required_scopes = set(self.scopes)

        missing_scopes = required_scopes - granted_scopes
        if missing_scopes:
            self.logger.warning(f"Missing required scopes: {missing_scopes}")
            self.logger.warning(f"Required: {required_scopes}, Granted: {granted_scopes}")
            return False

        self.logger.debug(f"Scope validation successful - Required: {required_scopes}, Granted: {granted_scopes}")
        return True

    def _validate_id_token_nonce(self, id_token: str) -> bool:
        """
        Validate nonce in JWT ID token (for OpenID Connect)
        """
        try:
            stored_nonce = self.session.get("oauth_nonce")

            if not stored_nonce:
                self.logger.warning("No stored nonce found for ID token validation")
                return False

            decoded_token = jwt.decode(id_token, options={"verify_signature": False, "verify_exp": True})

            token_nonce = decoded_token.get("nonce")
            if not token_nonce:
                self.logger.warning("No nonce found in ID token")
                return False

            import hmac

            if not hmac.compare_digest(token_nonce, stored_nonce):
                self.logger.warning("ID token nonce mismatch - potential replay attack")
                return False

            self.session.remove("oauth_nonce")
            self.session.save()

            self.logger.debug("ID token nonce validation successful")
            return True

        except Exception as e:
            self.logger.error(f"ID token nonce validation error: {e}")
            return False

    async def create_oauth_user(self, user_data: Dict[str, Any], repository) -> Optional[Any]:
        """
        Optional method to create an OAuth user.
        By default, does nothing (virtual user).
        Developers can override this method to implement their logic.

        Args:
            user_data: User data retrieved from OAuth provider
            repository: Repository to create the user

        Returns:
            Created user or None if no creation
        """
        return None

    @abstractmethod
    async def get_user_data_from_provider(self, access_token: str) -> Dict[str, Any]:
        """Retrieve and format user data from OAuth provider"""
        pass
