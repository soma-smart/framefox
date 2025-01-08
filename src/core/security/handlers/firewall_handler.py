import logging

from typing import Dict, Optional, Type, Annotated
from fastapi import Request
from fastapi.responses import Response, HTMLResponse, JSONResponse, RedirectResponse
from src.core.security.token_manager import TokenManager
from src.core.request.csrf_token_manager import CsrfTokenManager
from src.core.security.access_manager import AccessManager
from src.core.templates.template_renderer import TemplateRenderer
from injectable import Autowired, autowired
from src.core.config.settings import Settings
from src.core.request.cookie_manager import CookieManager
from src.core.security.authenticator.authenticator_interface import AuthenticatorInterface
import importlib


class FirewallHandler:
    @autowired
    def __init__(
        self,
        logger: logging.Logger,
        settings: Settings,
        template_renderer: Annotated[TemplateRenderer, Autowired],
    ):
        self.logger = logger
        self.settings = settings
        self.template_renderer = template_renderer
        self.token_manager = TokenManager()
        self.cookie_manager = CookieManager()
        self.csrf_manager = CsrfTokenManager(prefix="csrf_")
        self.access_manager = AccessManager(settings, logger)
        self.authenticators = self.load_authenticators()

    def load_authenticators(self) -> Dict[str, AuthenticatorInterface]:
        authenticators = {}
        firewalls = self.settings.firewalls
        for firewall_name, config in firewalls.items():
            for auth_type, auth_config in config.items():
                if isinstance(auth_config, dict) and 'authenticator' in auth_config:
                    authenticator_path = auth_config['authenticator']
                    try:
                        module_path, class_name = authenticator_path.rsplit(
                            ".", 1)
                        module = importlib.import_module(module_path)
                        AuthenticatorClass: Type[AuthenticatorInterface] = getattr(
                            module, class_name)
                        authenticator_instance = AuthenticatorClass()
                        authenticators[firewall_name] = authenticator_instance
                        self.logger.debug(f"Authenticator {class_name} loaded for firewall '{
                                          firewall_name}'.")
                    except (ImportError, AttributeError) as e:
                        self.logger.error(f"Error loading authenticator '{
                                          authenticator_path}' for firewall '{firewall_name}': {e}")
        return authenticators

    async def handle_authentication(self, request: Request, call_next) -> Optional[Response]:
        """
        Determines the firewall to use based on the request path and HTTP method.
        """
        for firewall_name, authenticator in self.authenticators.items():
            firewall_config = self.settings.get_firewall_config(firewall_name)
            login_path = firewall_config.get("login_path")
            logout_path = firewall_config.get("logout_path")

            # Gestion de la déconnexion
            if logout_path and request.url.path.startswith(logout_path):
                return await self.handle_logout(request, firewall_config, call_next)

            if request.url.path.startswith(login_path):
                if request.method == "GET":
                    return await self.handle_get_request(authenticator, firewall_config)
                elif request.method == "POST":
                    return await self.handle_post_request(request, authenticator, firewall_config)

        return None

    async def handle_get_request(self, authenticator: AuthenticatorInterface, firewall_config: Dict) -> Optional[Response]:
        """
        Handles GET requests for login.
        """
        self.logger.debug(f"Handling a GET request for {
                          type(authenticator).__name__}.")
        csrf_token_value = self.csrf_manager.generate_token()
        content = self.template_renderer.render(
            "login.html", {"csrf_token": csrf_token_value})
        response = HTMLResponse(content=content, status_code=200)
        self.cookie_manager.set_cookie(
            response=response, key="csrf_token", value=csrf_token_value)
        self.logger.debug("CSRF token set in the cookie.")
        return response

    async def handle_post_request(self, request: Request, authenticator: AuthenticatorInterface, firewall_config: Dict) -> Optional[Response]:
        """
        Handles POST requests for login.
        """
        self.logger.debug(f"Handling a POST request for {
                          type(authenticator).__name__}.")

        if not self.csrf_manager.validate_token(request):
            self.logger.error("CSRF validation failed.")
            return Response(content="Invalid CSRF token", status_code=400)

        passport = await authenticator.authenticate_request(request)
        if passport:
            token = self.token_manager.create_token(
                user=passport.user,
                firewallname=firewall_config.get(
                    "name", firewall_config.get("login_path", "main_firewall")),
                roles=(passport.user.roles if passport.user.roles else []),
            )
            response = authenticator.on_auth_success(token)
            self.cookie_manager.set_cookie(
                response=response, key="access_token", value=token)
            self.logger.info(
                "Authentication successful and token added to the cookie.")
            return response
        return Response(content="Authentication failed", status_code=400)

    async def handle_authorization(self, request: Request, call_next):
        """
        Handles authorization using the AccessManager class.
        """
        required_roles = self.access_manager.get_required_roles(
            request.url.path)
        if not required_roles:
            return await call_next(request)

        token = request.cookies.get("access_token")
        if token:
            payload = self.token_manager.decode_token(token)
            if payload:
                user_roles = payload.get("roles", [])
                if self.access_manager.is_allowed(user_roles, required_roles):
                    return await call_next(request)
                else:
                    self.logger.warning(
                        "User does not have the required roles.")
            else:
                self.logger.warning("Invalid token payload.")

        self.logger.warning(f"Access forbidden for path: {request.url.path}")
        return Response(content="Forbidden", status_code=403)

    async def handle_logout(self, request: Request, firewall_config: Dict, call_next) -> Response:
        """
        Handles user logout by deleting the access_token cookie.
        """

        response = await call_next(request)
        response.delete_cookie(
            key="access_token", httponly=True, secure=True, samesite="Lax")
        self.logger.info("User logged out.")
        return response
