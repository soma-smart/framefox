import logging
from typing import Dict, Optional

from fastapi import Request
from fastapi.responses import JSONResponse, Response

from framefox.core.security.authenticator.authenticator_interface import AuthenticatorInterface
from framefox.core.security.handlers.firewall_utils import FirewallUtils
from framefox.core.security.protector.time_attack_protector import TimingAttackProtector

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class JWTAuthenticationHandler:
    """
    Specialized handler for JWT authentication.
    Handles JWT stateless authentication logic for APIs only.

    This class manages the complete JWT authentication flow including token validation,
    user context injection, and error handling with timing attack protection.
    """

    def __init__(
        self,
        timing_protector: TimingAttackProtector,
        utils: FirewallUtils,
    ):
        self.timing_protector = timing_protector
        self.utils = utils
        self.logger = logging.getLogger("FIREWALL")

    async def handle_jwt_authentication(self, request: Request, authenticators: Dict[str, AuthenticatorInterface]) -> Optional[Response]:
        jwt_context = self.utils.identify_jwt_firewall(request, authenticators)
        if not jwt_context:
            return None

        if self.utils.is_public_route(request.url.path):
            self.logger.debug(f"Route {request.url.path} is public but matches JWT pattern - skipping JWT auth")
            return None

        firewall_name = jwt_context["firewall_name"]
        self.logger.debug(f"JWT authentication attempt for {request.url.path} using firewall '{firewall_name}'")

        return await self._authenticate_jwt_request(request, jwt_context)

    async def _authenticate_jwt_request(self, request: Request, jwt_context: Dict) -> Optional[Response]:
        firewall_name = jwt_context["firewall_name"]
        authenticator = jwt_context["authenticator"]

        try:
            passport = await self.timing_protector.protected_authentication(authenticator.authenticate_request, request, firewall_name)

            if passport:
                return self._handle_jwt_success(request, passport, firewall_name)
            else:
                return self._handle_jwt_failure(request, authenticator, "Invalid or missing JWT token")

        except Exception as e:
            self.logger.error(f"JWT authentication error for {request.url.path}: {e}")
            return self._handle_jwt_exception(request, str(e))

    def _handle_jwt_success(self, request: Request, passport, firewall_name: str) -> None:
        request.state.current_user = passport.user
        request.state.firewall_name = firewall_name

        # user_identifier = passport.user.email if hasattr(passport.user, "email") else passport.user.id
        self.logger.info("JWT authentication successful")
        self.logger.debug(f"User roles: {getattr(passport.user, 'roles', [])} - Firewall: {firewall_name}")

        return None

    def _handle_jwt_failure(self, request: Request, authenticator: AuthenticatorInterface, error_message: str) -> Response:
        client_ip = getattr(request.client, "host", "unknown")
        self.logger.warning(f"JWT authentication failed for {request.url.path} from {client_ip}: {error_message}")

        return authenticator.on_auth_failure(request, error_message)

    def _handle_jwt_exception(self, request: Request, error_details: str) -> Response:
        client_ip = getattr(request.client, "host", "unknown")
        self.logger.error(f"JWT authentication exception for {request.url.path} from {client_ip}: {error_details}")
        return JSONResponse({"error": "Authentication error"}, status_code=500)

    def is_jwt_route(self, request: Request, authenticators: Dict[str, AuthenticatorInterface]) -> bool:
        jwt_context = self.utils.identify_jwt_firewall(request, authenticators)
        return jwt_context is not None

    def get_jwt_context(self, request: Request, authenticators: Dict[str, AuthenticatorInterface]) -> Optional[Dict]:
        return self.utils.identify_jwt_firewall(request, authenticators)
