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
from framefox.core.security.authenticator.authenticator_interface import AuthenticatorInterface
from framefox.core.security.handlers.security_context_handler import SecurityContextHandler
from framefox.core.security.token_manager import TokenManager
from framefox.core.security.token_storage import TokenStorage
from framefox.core.templates.template_renderer import TemplateRenderer

from framefox.core.security.protector.time_attack_protector import TimingAttackProtector
from framefox.core.security.protector.rate_limiting_protector import RateLimitingProtector
from framefox.core.security.protector.security_headers_protector import SecurityHeadersProtector
from framefox.core.security.protector.input_validation_protector import InputValidationProtector
from framefox.core.security.protector.brute_force_protector import BruteForceProtector

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FirewallHandler:

    def __init__(
        self,
        settings: Settings,
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
        self.settings = settings
        self.template_renderer = template_renderer
        self.cookie_manager = cookie_manager
        self.session_manager = session_manager
        self.token_manager = token_manager
        self.csrf_manager = csrf_manager
        self.session = session
        self.token_storage = token_storage
        self.access_manager = access_manager
        self.security_context_handler = security_context_handler

        # Security protectors
        self.timing_protector = time_attack_protector
        self.rate_limiter = rate_limiting_protector
        self.headers_protector = security_headers_protector
        self.input_validator = input_validation_protector
        self.brute_force_protector = brute_force_protector

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
                    authenticator_instance = AuthenticatorClass()
                    authenticators[firewall_name] = authenticator_instance
                except (ImportError, AttributeError) as e:
                    self.logger.error(f"Error loading authenticator '{authenticator_path}' for firewall '{firewall_name}': {e}")
        return authenticators

    async def handle_request(self, request: Request, call_next):
        if not self.settings.firewalls:
            return await call_next(request)

        client_ip = getattr(request.client, "host", "unknown")
        user_agent = request.headers.get("user-agent", "")

        # Rate limiting protection
        allowed, reason = self.rate_limiter.is_allowed(client_ip, request.url.path)
        if not allowed:
            self.logger.warning(f"Rate limited: {client_ip} - {reason}")
            return JSONResponse({"error": "Too many requests"}, status_code=429)

        # Input validation for POST/PUT/PATCH requests
        if request.method in ["POST", "PUT", "PATCH"] and self._should_validate_input(request):
            if not await self._validate_request_input(request):
                return JSONResponse({"error": "Invalid input detected"}, status_code=400)

        # Process firewall logic
        auth_routes = self._get_auth_routes()

        # Handle logout
        for firewall_name, firewall in self.settings.firewalls.items():
            if "logout_path" in firewall and request.url.path.startswith(firewall["logout_path"]):
                response = await self.handle_logout(request, firewall, firewall_name, call_next)
                self.headers_protector.apply_headers(response, request)
                return response

        # Handle authentication
        is_auth_route = any(request.url.path.startswith(route) for route in auth_routes)
        if is_auth_route:
            auth_response = await self.handle_authentication(request, call_next)
            if auth_response:
                self.headers_protector.apply_headers(auth_response, request)
                return auth_response

        # Handle authorization
        auth_result = await self.handle_authorization(request, call_next)
        if hasattr(auth_result, "headers"):
            self.headers_protector.apply_headers(auth_result, request)

        return auth_result

    def _get_auth_routes(self) -> list:
        """Extract authentication routes from firewall configs."""
        auth_routes = []
        for firewall in self.settings.firewalls.values():
            if "login_path" in firewall:
                auth_routes.append(firewall["login_path"])
            if "logout_path" in firewall:
                auth_routes.append(firewall["logout_path"])
        return auth_routes

    def _should_validate_input(self, request: Request) -> bool:
        """Check if request should be validated for malicious input."""
        content_type = request.headers.get("content-type", "")
        return "application/json" in content_type or "application/x-www-form-urlencoded" in content_type

    async def _validate_request_input(self, request: Request) -> bool:
        """Validate request input with context awareness."""
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

    async def handle_authentication(self, request: Request, call_next) -> Optional[Response]:
        for firewall_name, authenticator in self.authenticators.items():
            firewall_config = self.settings.get_firewall_config(firewall_name)
            login_path = firewall_config.get("login_path")
            logout_path = firewall_config.get("logout_path")
            oauth_config = firewall_config.get("oauth", {})

            if logout_path and request.url.path.startswith(logout_path):
                return await self.handle_logout(request, firewall_config, firewall_name, call_next)

            # OAuth handling
            is_oauth_authenticator = getattr(authenticator, "is_oauth_authenticator", False)
            if is_oauth_authenticator and oauth_config:
                init_path = oauth_config.get("init_path", login_path)
                if request.url.path.endswith(init_path):
                    return authenticator.on_auth_failure(request)

                callback_path = oauth_config.get("callback_path")
                is_callback = (
                    callback_path
                    and request.url.path.endswith(callback_path)
                    and "code" in request.query_params
                    and "state" in request.query_params
                )

                if is_callback:
                    return await call_next(request)

            # Standard login handling
            elif request.url.path.startswith(login_path):
                if request.method == "GET":
                    return await call_next(request)
                elif request.method == "POST":
                    # CSRF validation with timing protection
                    csrf_valid = await self.timing_protector.protected_csrf_validation(self.csrf_manager.validate_token, request)

                    if not csrf_valid:
                        self.logger.error("CSRF validation failed")
                        if hasattr(request.state, "session_id"):
                            self.security_context_handler.set_authentication_error("A security error occurred. Please try again.")
                        return RedirectResponse(url=login_path, status_code=303)

                    return await self.handle_post_request(request, authenticator, firewall_config, firewall_name)

        return await call_next(request)

    async def handle_post_request(
        self,
        request: Request,
        authenticator: AuthenticatorInterface,
        firewall_config: Dict,
        firewall_name: str,
    ) -> Optional[Response]:

        client_ip = getattr(request.client, "host", "unknown")

        # Extract username for brute force protection
        try:
            form_data = await request.form()
            username = form_data.get("_username") or form_data.get("email", "")
        except:
            username = "unknown"

        # Brute force protection check
        allowed, reason, delay = self.brute_force_protector.check_login_attempt(client_ip, username)
        if not allowed:
            self.logger.warning(f"Brute force protection triggered: {reason}")
            if delay > 0:
                await asyncio.sleep(min(delay, 5))  # Max 5 seconds delay
            return authenticator.on_auth_failure(request, "Too many failed attempts")

        # Apply progressive delay if needed
        if delay > 0:
            await asyncio.sleep(min(delay, 5))

        # Authentication with timing attack protection
        passport = await self.timing_protector.protected_authentication(authenticator.authenticate_request, request, firewall_name)

        if passport:
            # Success: Reset brute force counters
            self.brute_force_protector.check_login_attempt(client_ip, username, success=True)

            # Create and store token
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
        else:
            # Failure: Record failed attempt
            self.brute_force_protector.check_login_attempt(client_ip, username, success=False)

            error_message = "Invalid credentials. Please try again."
            if hasattr(request.state, "session_id"):
                self.security_context_handler.set_authentication_error(error_message)

            return authenticator.on_auth_failure(request, error_message)

    async def handle_authorization(self, request: Request, call_next):
        required_roles = self.access_manager.get_required_roles(request.url.path)
        if not required_roles:
            return await call_next(request)

        payload = self.token_storage.get_payload()

        if payload:
            user_roles = payload.get("roles", [])
            if self.access_manager.is_allowed(user_roles, required_roles):
                return await call_next(request)
            else:
                self.logger.warning("User does not have the required roles")

        self.logger.warning(f"Access forbidden for path: {request.url.path}")

        accept_header = request.headers.get("accept", "")
        if "text/html" in accept_header:
            redirect_url = self._get_denied_redirect_url(request)
            return RedirectResponse(url=redirect_url, status_code=302)
        else:
            return JSONResponse(content={"error": "Access denied"}, status_code=403)

    async def handle_logout(self, request: Request, firewall_config: Dict, firewall_name: str, call_next) -> Response:
        # Clear tokens and sessions
        self.token_storage.clear_token()

        session_id = request.cookies.get("session_id")
        if session_id:
            self.session_manager.delete_session(session_id)

        self.session.clear()
        request.state.session_data = {}

        # Generate response
        if firewall_name == "main":
            response = await call_next(request)
        else:
            accept_header = request.headers.get("accept", "")
            if "application/json" in accept_header:
                response = JSONResponse(content={"message": "Successfully logged out"}, status_code=200)
            else:
                response = RedirectResponse(url="/login", status_code=302)

        # Clean up cookies
        self.cookie_manager.delete_cookie(response, "session_id")
        self.cookie_manager.delete_cookie(response, "csrf_token")
        self.cookie_manager.delete_cookie(response, "access_token")

        self.logger.info("User logged out successfully")
        return response

    def _get_denied_redirect_url(self, request: Request) -> str:
        """Get the denied redirect URL from firewall configuration."""

        main_firewall = self.settings.get_firewall_config("main")
        if main_firewall and main_firewall.get("denied_redirect"):
            return main_firewall["denied_redirect"]

        return "/"
