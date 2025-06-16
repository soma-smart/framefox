import logging
import re,hmac
from typing import Dict, List, Optional

from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse, Response

from framefox.core.config.settings import Settings
from framefox.core.security.access_manager import AccessManager
from framefox.core.security.authenticator.authenticator_interface import AuthenticatorInterface
from framefox.core.security.protector.input_validation_protector import InputValidationProtector

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FirewallUtils:
    """
    Utility class for FirewallHandler.
    Groups auxiliary methods for validation, verification and response generation.
    """

    def __init__(
        self,
        access_manager: AccessManager,
        input_validator: InputValidationProtector,
    ):
        self.settings = Settings()
        self.access_manager = access_manager
        self.input_validator = input_validator
        self.logger = logging.getLogger("FIREWALL")

    def get_auth_routes(self) -> List[str]:
        auth_routes = []
        for firewall in self.settings.firewalls.values():
            if "login_path" in firewall:
                auth_routes.append(firewall["login_path"])
            if "logout_path" in firewall:
                auth_routes.append(firewall["logout_path"])
            oauth_config = firewall.get("oauth", {})
            if oauth_config and oauth_config.get("callback_path"):
                auth_routes.append(oauth_config["callback_path"])
        return auth_routes

    def matches_firewall_pattern(self, path: str, firewall_name: str) -> bool:
        firewall_config = self.settings.get_firewall_config(firewall_name)
        pattern = firewall_config.get("pattern")
        
        if pattern:
            try:
                match = re.match(pattern, path)
                if match:
                    self.logger.debug(f"Path {path} matches firewall '{firewall_name}' pattern: {pattern}")
                    return True
                else:
                    self.logger.debug(f"Path {path} does NOT match firewall '{firewall_name}' pattern: {pattern}")
                    return False
            except re.error:
                self.logger.warning(f"Invalid regex pattern for firewall '{firewall_name}': {pattern}")
                return False
        return False

    def should_validate_input(self, request: Request) -> bool:
        content_type = request.headers.get("content-type", "")
        return "application/json" in content_type or "application/x-www-form-urlencoded" in content_type

    async def validate_request_input(self, request: Request) -> bool:
        try:
            content_type = request.headers.get("content-type", "")

            if "application/json" in content_type:
                body = await request.body()
                if body:
                    body_str = body.decode("utf-8")
                    if self.input_validator.is_malicious_payload(body_str):
                        self.logger.warning(f"Malicious payload detected from {getattr(request.client, 'host', 'unknown')}")
                        return False
            return True
        except Exception as e:
            self.logger.error(f"Input validation error: {e}")
            return False

    def get_denied_redirect_url(self) -> str:
        main_firewall = self.settings.get_firewall_config("main")
        if main_firewall and main_firewall.get("denied_redirect"):
            return main_firewall["denied_redirect"]
        return "/"

    def is_jwt_authenticator(self, authenticator: AuthenticatorInterface) -> bool:
        return hasattr(authenticator, '__class__') and 'jwt' in authenticator.__class__.__name__.lower()

    def is_oauth_authenticator(self, authenticator: AuthenticatorInterface) -> bool:
        return getattr(authenticator, "is_oauth_authenticator", False)

    def is_public_route(self, path: str) -> bool:
        required_roles = self.access_manager.get_required_roles(path)
        return not required_roles or "IS_AUTHENTICATED_ANONYMOUSLY" in required_roles

    def is_oauth_callback(self, request: Request, callback_path: str) -> bool:
        return (
            callback_path
            and request.url.path == callback_path
            and "code" in request.query_params
        )

    def generate_access_denied_response(self, request: Request) -> Response:
        self.logger.warning(f"Access forbidden for path: {request.url.path}")

        accept_header = request.headers.get("accept", "")
        
        if "text/html" in accept_header:
            redirect_url = self.get_denied_redirect_url()
            return RedirectResponse(url=redirect_url, status_code=302)
        else:
            return JSONResponse(content={"error": "Access denied"}, status_code=403)

    def check_user_authorization(self, request: Request, required_roles: List[str], token_storage) -> bool:
        current_user = getattr(request.state, 'current_user', None)
        if current_user:
            user_roles = current_user.roles if hasattr(current_user, 'roles') else []
            if self.access_manager.is_allowed(user_roles, required_roles):
                self.logger.debug(f"JWT user authorized with roles: {user_roles}")
                return True
            else:
                self.logger.warning(f"JWT user does not have required roles. Has: {user_roles}, Required: {required_roles}")
                return False

        payload = token_storage.get_payload()
        if payload:
            user_roles = payload.get("roles", [])
            if self.access_manager.is_allowed(user_roles, required_roles):
                self.logger.debug(f"Session user authorized with roles: {user_roles}")
                return True
            else:
                self.logger.warning(f"Session user does not have required roles. Has: {user_roles}, Required: {required_roles}")
                return False
        
        self.logger.debug("No authenticated user found")
        return False

    def identify_jwt_firewall(self, request: Request, authenticators: Dict[str, AuthenticatorInterface]) -> Optional[Dict]:
        for firewall_name, authenticator in authenticators.items():
            if self.is_jwt_authenticator(authenticator):
                if self.matches_firewall_pattern(request.url.path, firewall_name):
                    self.logger.debug(f"JWT firewall '{firewall_name}' matched for path: {request.url.path}")
                    return {
                        "firewall_name": firewall_name,
                        "authenticator": authenticator
                    }

        self.logger.debug(f"No JWT firewall pattern matched for path: {request.url.path}")
        return None

    def extract_username_from_request(self, request: Request) -> str:
        try:
            if hasattr(request, '_form_data'):
                form_data = request._form_data
            else:
                return "unknown"
            
            return form_data.get("_username") or form_data.get("email", "unknown")
        except:
            return "unknown"

    def should_apply_oauth_logic(
        self, 
        request: Request, 
        authenticator: AuthenticatorInterface, 
        firewall_config: Dict
    ) -> bool:
        is_oauth_auth = self.is_oauth_authenticator(authenticator)
        oauth_config = firewall_config.get("oauth", {})
        
        return is_oauth_auth and oauth_config

    def get_oauth_callback_path(self, firewall_config: Dict) -> Optional[str]:
        oauth_config = firewall_config.get("oauth", {})
        return oauth_config.get("callback_path") if oauth_config else None

    def validate_oauth_callback(self, request: Request) -> bool:
        """
        Complete OAuth callback validation
        
        Args:
            request: Request containing callback parameters
            
        Returns:
            bool: True if callback is valid
        """
        if not self.validate_oauth_state(request):
            return False
        
        code = request.query_params.get("code")
        if not code:
            self.logger.warning("OAuth callback without authorization code")
            return False
        
        error = request.query_params.get("error")
        if error:
            error_description = request.query_params.get("error_description", "")
            self.logger.warning(f"OAuth provider returned error: {error} - {error_description}")
            return False
        
        self.logger.debug("OAuth callback validation successful")
        return True

    def validate_oauth_state(self, request: Request) -> bool:
        """OAuth state validation with enhanced logging"""
        received_state = request.query_params.get("state")
        if not received_state:
            self.logger.warning("OAuth callback without state parameter - potential CSRF attack")
            return False
            
        from framefox.core.request.session.session import Session
        session = Session()
        
        stored_state = session.get("oauth_state")
        
        if not stored_state:
            self.logger.warning("No stored OAuth state found - session may have expired")
            return False
            
        if not hmac.compare_digest(received_state, stored_state):
            self.logger.warning("OAuth state mismatch - potential CSRF attack")
            self.logger.debug(f"Expected state: {stored_state[:8]}..., Received: {received_state[:8]}...")
            return False
            
        session.remove("oauth_state")
        session.save()
        
        self.logger.debug("OAuth state validation successful")
        return True

    def log_oauth_event(self, event_type: str, firewall_name: str, additional_info: str = ""):
        if event_type == "login_initiated":
            self.logger.debug(f"OAuth login initiated for firewall '{firewall_name}' - redirecting to provider")
        elif event_type == "callback_detected":
            self.logger.debug(f"OAuth callback detected for firewall '{firewall_name}' - processing authentication")
        elif event_type == "auth_success":
            self.logger.info(f"OAuth authentication successful")
        elif event_type == "auth_failure":
            self.logger.warning(f"OAuth authentication failed: {additional_info}")
        elif event_type == "session_created":
            self.logger.debug("OAuth authentication and session creation successful")
