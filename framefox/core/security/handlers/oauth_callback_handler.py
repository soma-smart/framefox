import logging
from typing import Dict

from fastapi import Request
from fastapi.responses import Response

from framefox.core.request.session.session_interface import SessionInterface
from framefox.core.security.authenticator.authenticator_interface import AuthenticatorInterface
from framefox.core.security.handlers.firewall_utils import FirewallUtils
from framefox.core.security.handlers.security_context_handler import SecurityContextHandler
from framefox.core.security.protector.time_attack_protector import TimingAttackProtector
from framefox.core.security.token_manager import TokenManager
from framefox.core.security.token_storage import TokenStorage

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class OAuthCallbackHandler:
    """
    Specialized handler for OAuth callbacks.
    Processes OAuth callback logic after provider redirection.
    
    This handler manages the complete OAuth callback flow including:
    - State validation for security
    - Authentication processing using existing authenticator logic
    - Token creation and storage
    - Session management
    - Success and failure response handling
    """

    def __init__(
        self,
        token_manager: TokenManager,
        token_storage: TokenStorage,
        session: SessionInterface,
        security_context_handler: SecurityContextHandler,
        timing_protector: TimingAttackProtector,
        utils: FirewallUtils,
    ):
        self.token_manager = token_manager
        self.token_storage = token_storage
        self.session = session
        self.security_context_handler = security_context_handler
        self.timing_protector = timing_protector
        self.utils = utils
        self.logger = logging.getLogger("FIREWALL")

    async def handle_oauth_callback(
        self,
        request: Request,
        authenticator: AuthenticatorInterface,
        firewall_config: Dict,
        firewall_name: str,
    ) -> Response:
        self.logger.debug(f"Processing OAuth callback for firewall '{firewall_name}'")
        
        if not self.utils.validate_oauth_state(request):
            return authenticator.on_auth_failure(request, "Invalid OAuth state")
        
        try:
            passport = await self.timing_protector.protected_authentication(
                authenticator.authenticate_request, 
                request, 
                firewall_name
            )

            if passport:
                return self._handle_oauth_success(
                    passport, firewall_name, authenticator
                )
            else:
                return self._handle_oauth_failure(
                    request, authenticator, firewall_name, 
                    "OAuth authentication failed. Please try again."
                )
                
        except Exception as e:
            error_message = f"OAuth callback error: {str(e)}"
            self.logger.error(error_message)
            return self._handle_oauth_failure(
                request, authenticator, firewall_name,
                "An error occurred during authentication. Please try again."
            )

    def _handle_oauth_success(
        self, 
        passport, 
        firewall_name: str,
        authenticator: AuthenticatorInterface
    ) -> Response:
        user_identifier = passport.user_badge.user_identifier if passport.user_badge else 'unknown'
        self.utils.log_oauth_event("auth_success", firewall_name, user_identifier)
        
        token = self.token_manager.create_token(
            user=passport.user,
            firewallname=firewall_name,
            roles=(passport.user.roles if passport.user and hasattr(passport.user, "roles") and passport.user.roles else []),
        )
        self.token_storage.set_token(token)

        self.session.set("user_id", passport.user.id)
        self.session.save()

        response = authenticator.on_auth_success(token)
        
        self.utils.log_oauth_event("session_created", firewall_name)
        return response

    def _handle_oauth_failure(
        self, 
        request: Request,
        authenticator: AuthenticatorInterface,
        firewall_name: str,
        error_message: str
    ) -> Response:
        self.utils.log_oauth_event("auth_failure", firewall_name, error_message)
        
        if hasattr(request.state, "session_id"):
            self.security_context_handler.set_authentication_error(error_message)
        
        self.logger.warning(f"OAuth callback failed for firewall '{firewall_name}': {error_message}")
        
        return authenticator.on_auth_failure(request, error_message)