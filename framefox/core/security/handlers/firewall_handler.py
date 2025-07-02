import asyncio
import importlib
import logging
from typing import Dict, Optional, Type

from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse, Response

from framefox.core.config.settings import Settings
from framefox.core.request.cookie_manager import CookieManager
from framefox.core.request.csrf_token_manager import CsrfTokenManager
from framefox.core.request.session.session_interface import SessionInterface
from framefox.core.request.session.session_manager import SessionManager
from framefox.core.security.access_manager import AccessManager
from framefox.core.security.authenticator.authenticator_interface import (
    AuthenticatorInterface,
)
from framefox.core.security.handlers.firewall_utils import FirewallUtils
from framefox.core.security.handlers.jwt_authentication_handler import (
    JWTAuthenticationHandler,
)
from framefox.core.security.handlers.oauth_callback_handler import OAuthCallbackHandler
from framefox.core.security.handlers.security_context_handler import (
    SecurityContextHandler,
)
from framefox.core.security.protector.brute_force_protector import BruteForceProtector
from framefox.core.security.protector.input_validation_protector import (
    InputValidationProtector,
)
from framefox.core.security.protector.rate_limiting_protector import (
    RateLimitingProtector,
)
from framefox.core.security.protector.security_headers_protector import (
    SecurityHeadersProtector,
)
from framefox.core.security.protector.time_attack_protector import TimingAttackProtector
from framefox.core.security.token_manager import TokenManager
from framefox.core.security.token_storage import TokenStorage
from framefox.core.templates.template_renderer import TemplateRenderer

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FirewallHandler:
    """
    Main security firewall handler.
    Orchestrates JWT authentication, OAuth, form authentication and authorization.

    This class serves as the central security component that manages all incoming requests,
    applies security protections, handles various authentication methods, and enforces
    authorization policies.

    Features:
    - Multiple authentication methods (JWT, OAuth, form-based)
    - Rate limiting and brute force protection
    - CSRF protection for form submissions
    - Input validation and sanitization
    - Security headers enforcement
    - Session management
    - Role-based access control
    """

    def __init__(
        self,
        template_renderer: TemplateRenderer,
        cookie_manager: CookieManager,
        session_manager: SessionManager,
        token_manager: TokenManager,
        csrf_manager: CsrfTokenManager,
        access_manager: AccessManager,
        session: SessionInterface,
        security_context_handler: SecurityContextHandler,
        time_attack_protector: TimingAttackProtector,
        token_storage: TokenStorage,
        rate_limiting_protector: RateLimitingProtector,
        security_headers_protector: SecurityHeadersProtector,
        input_validation_protector: InputValidationProtector,
        brute_force_protector: BruteForceProtector,
    ):
        self.logger = logging.getLogger("FIREWALL")
        self.settings = Settings()
        self.template_renderer = template_renderer
        self.cookie_manager = cookie_manager
        self.session_manager = session_manager
        self.token_manager = token_manager
        self.csrf_manager = csrf_manager
        self.session = session
        self.token_storage = token_storage
        self.access_manager = access_manager
        self.security_context_handler = security_context_handler

        self.timing_protector = time_attack_protector
        self.rate_limiter = rate_limiting_protector
        self.headers_protector = security_headers_protector
        self.input_validator = input_validation_protector
        self.brute_force_protector = brute_force_protector

        self.utils = FirewallUtils(
            access_manager=access_manager,
            input_validator=input_validation_protector,
        )

        self.oauth_callback_handler = OAuthCallbackHandler(
            token_manager=token_manager,
            token_storage=token_storage,
            session=session,
            security_context_handler=security_context_handler,
            timing_protector=time_attack_protector,
            utils=self.utils,
        )

        self.jwt_authentication_handler = JWTAuthenticationHandler(
            timing_protector=time_attack_protector,
            utils=self.utils,
        )

        self.authenticators = self.load_authenticators()

    def load_authenticators(self) -> Dict[str, AuthenticatorInterface]:
        authenticators = {}
        firewalls = self.settings.firewalls
        if not firewalls:
            return authenticators

        for firewall_name, config in firewalls.items():
            authenticator_path = config.get("authenticator")
            if authenticator_path:
                try:
                    module_path, class_name = authenticator_path.rsplit(".", 1)
                    module = importlib.import_module(module_path)
                    AuthenticatorClass: Type[AuthenticatorInterface] = getattr(module, class_name)

                    from framefox.core.di.service_container import ServiceContainer

                    container = ServiceContainer()

                    try:
                        authenticator_instance = container.get(AuthenticatorClass)
                    except Exception as e:
                        self.logger.warning(f"Could not autowire {class_name}, falling back to manual instantiation: {e}")
                        authenticator_instance = AuthenticatorClass()

                    authenticators[firewall_name] = authenticator_instance
                except (ImportError, AttributeError) as e:
                    self.logger.error(f"Error loading authenticator '{authenticator_path}' for firewall '{firewall_name}': {e}")
        return authenticators

    async def handle_request(self, request: Request, call_next):
        if not self.settings.firewalls:
            return await call_next(request)

        if not await self._apply_basic_protections(request):
            return self._get_protection_failure_response()

        auth_response = await self._handle_authentication_routes(request, call_next)
        if auth_response:
            self.headers_protector.apply_headers(auth_response, request)
            return auth_response

        jwt_response = await self.jwt_authentication_handler.handle_jwt_authentication(request, self.authenticators)
        if jwt_response:
            self.headers_protector.apply_headers(jwt_response, request)
            return jwt_response

        required_roles = self.access_manager.get_required_roles(request.url.path)

        if not required_roles or "IS_AUTHENTICATED_ANONYMOUSLY" in required_roles:
            response = await call_next(request)
            self.headers_protector.apply_headers(response, request)
            return response

        auth_result = await self._handle_authorization(request, call_next)
        if hasattr(auth_result, "headers"):
            self.headers_protector.apply_headers(auth_result, request)

        return auth_result

    async def _apply_basic_protections(self, request: Request) -> bool:
        client_ip = getattr(request.client, "host", "unknown")

        allowed, reason = self.rate_limiter.is_allowed(client_ip, request.url.path)
        if not allowed:
            self.logger.warning(f"Rate limited: {client_ip} - {reason}")
            self._protection_failure_response = JSONResponse({"error": "Too many requests"}, status_code=429)
            return False

        if request.method in [
            "POST",
            "PUT",
            "PATCH",
        ] and self.utils.should_validate_input(request):
            if not await self.utils.validate_request_input(request):
                self._protection_failure_response = JSONResponse({"error": "Invalid input detected"}, status_code=400)
                return False

        return True

    def _get_protection_failure_response(self):
        return getattr(
            self,
            "_protection_failure_response",
            JSONResponse({"error": "Protection failed"}, status_code=400),
        )

    async def _handle_authentication_routes(self, request: Request, call_next) -> Optional[Response]:
        auth_routes = self.utils.get_auth_routes()

        for firewall_name, firewall in self.settings.firewalls.items():
            if "logout_path" in firewall and request.url.path.startswith(firewall["logout_path"]):
                return await self.handle_logout(request, firewall, firewall_name, call_next)

        is_auth_route = any(request.url.path.startswith(route) for route in auth_routes)
        if is_auth_route:
            return await self.handle_authentication(request, call_next)

        return None

    async def handle_authentication(self, request: Request, call_next) -> Optional[Response]:
        self.logger.debug(f"Handling authentication for path: {request.url.path}")

        for firewall_name, authenticator in self.authenticators.items():
            firewall_config = self.settings.get_firewall_config(firewall_name)
            login_path = firewall_config.get("login_path")
            logout_path = firewall_config.get("logout_path")

            self.logger.debug(f"Checking firewall '{firewall_name}': login_path={login_path}")

            if logout_path and request.url.path.startswith(logout_path):
                return await self.handle_logout(request, firewall_config, firewall_name, call_next)

            if self.utils.should_apply_oauth_logic(request, authenticator, firewall_config):
                oauth_response = await self._handle_oauth_authentication(request, firewall_name, authenticator, firewall_config)
                if oauth_response:
                    return oauth_response

            elif request.url.path.startswith(login_path):
                if request.method == "GET":
                    return await call_next(request)
                elif request.method == "POST":
                    return await self._handle_form_authentication(request, authenticator, firewall_config, firewall_name)

        self.logger.debug(f"No firewall matched for path: {request.url.path}")
        return None

    async def _handle_oauth_authentication(
        self,
        request: Request,
        firewall_name: str,
        authenticator: AuthenticatorInterface,
        firewall_config: Dict,
    ) -> Optional[Response]:
        login_path = firewall_config.get("login_path")

        self.logger.debug(f"OAuth authenticator detected for firewall '{firewall_name}'")

        if request.url.path.startswith(login_path):
            self.utils.log_oauth_event("login_initiated", firewall_name)
            return authenticator.on_auth_failure(request)

        callback_path = self.utils.get_oauth_callback_path(firewall_config)
        if self.utils.is_oauth_callback(request, callback_path):
            self.utils.log_oauth_event("callback_detected", firewall_name)
            return await self.oauth_callback_handler.handle_oauth_callback(request, authenticator, firewall_config, firewall_name)

        return None

    async def _handle_form_authentication(
        self,
        request: Request,
        authenticator: AuthenticatorInterface,
        firewall_config: Dict,
        firewall_name: str,
    ) -> Response:
        login_path = firewall_config.get("login_path")

        if not self.utils.is_jwt_authenticator(authenticator):
            csrf_valid = await self.timing_protector.protected_csrf_validation(self.csrf_manager.validate_token, request)

            if not csrf_valid:
                self.logger.error("CSRF validation failed")
                if hasattr(request.state, "session_id"):
                    self.security_context_handler.set_authentication_error("A security error occurred. Please try again.")
                return RedirectResponse(url=login_path, status_code=303)

        return await self.handle_post_request(request, authenticator, firewall_config, firewall_name)

    async def _handle_authorization(self, request: Request, call_next) -> Response:
        required_roles = self.access_manager.get_required_roles(request.url.path)

        if not required_roles:
            return await call_next(request)

        if "IS_AUTHENTICATED_ANONYMOUSLY" in required_roles:
            self.logger.debug(f"Route {request.url.path} accessible anonymously - access granted")
            return await call_next(request)

        if self.utils.check_user_authorization(request, required_roles, self.token_storage):
            return await call_next(request)
        else:
            return self.utils.generate_access_denied_response(request)

    async def handle_post_request(
        self,
        request: Request,
        authenticator: AuthenticatorInterface,
        firewall_config: Dict,
        firewall_name: str,
    ) -> Optional[Response]:
        client_ip = getattr(request.client, "host", "unknown")

        try:
            form_data = await request.form()
            request._form_data = form_data
            username = form_data.get("_username") or form_data.get("email", "")
        except Exception:
            username = "unknown"

        allowed, reason, delay = self.brute_force_protector.check_login_attempt(client_ip, username)
        if not allowed:
            self.logger.warning(f"Brute force protection triggered: {reason}")
            if delay > 0:
                await asyncio.sleep(min(delay, 5))
            return authenticator.on_auth_failure(request, "Too many failed attempts")

        if delay > 0:
            await asyncio.sleep(min(delay, 5))

        passport = await self.timing_protector.protected_authentication(authenticator.authenticate_request, request, firewall_name)

        if passport:
            return self._handle_authentication_success(passport, firewall_name, authenticator, client_ip, username)
        else:
            return self._handle_authentication_failure(request, authenticator, client_ip, username)

    def _handle_authentication_success(
        self,
        passport,
        firewall_name: str,
        authenticator: AuthenticatorInterface,
        client_ip: str,
        username: str,
    ) -> Response:
        self.brute_force_protector.check_login_attempt(client_ip, username, success=True)

        token = self.token_manager.create_token(
            user=passport.user,
            firewallname=firewall_name,
            roles=(passport.user.roles if passport.user and hasattr(passport.user, "roles") and passport.user.roles else []),
        )
        self.token_storage.set_token(token)

        self.session.set("user_id", passport.user.id)
        self.session.save()

        response = authenticator.on_auth_success(token)
        self.cookie_manager.delete_cookie(response, "csrf_token")

        self.logger.info("Authentication successful")
        return response

    def _handle_authentication_failure(
        self,
        request: Request,
        authenticator: AuthenticatorInterface,
        client_ip: str,
        username: str,
    ) -> Response:
        self.brute_force_protector.check_login_attempt(client_ip, username, success=False)

        error_message = "Invalid credentials. Please try again."
        if hasattr(request.state, "session_id"):
            self.security_context_handler.set_authentication_error(error_message)

        return authenticator.on_auth_failure(request, error_message)

    async def handle_logout(self, request: Request, firewall_config: Dict, firewall_name: str, call_next) -> Response:
        self.token_storage.clear_token()

        session_id = request.cookies.get("session_id")
        if session_id:
            self.session_manager.delete_session(session_id)

        self.session.clear()
        request.state.session_data = {}

        if firewall_name == "main":
            response = await call_next(request)
        else:
            accept_header = request.headers.get("accept", "")
            if "application/json" in accept_header:
                response = JSONResponse(content={"message": "Successfully logged out"}, status_code=200)
            else:
                response = RedirectResponse(url="/login", status_code=302)

        self.cookie_manager.delete_cookie(response, "session_id")
        self.cookie_manager.delete_cookie(response, "csrf_token")
        self.cookie_manager.delete_cookie(response, "access_token")

        self.logger.info("User logged out successfully")
        return response
