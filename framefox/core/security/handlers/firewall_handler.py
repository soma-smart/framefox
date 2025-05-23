import importlib
import logging
from typing import Dict, Optional, Type
from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer
from framefox.core.request.cookie_manager import CookieManager
from framefox.core.request.csrf_token_manager import CsrfTokenManager
from framefox.core.request.session.session_interface import SessionInterface
from framefox.core.request.session.session_manager import SessionManager
from framefox.core.security.access_manager import AccessManager
from framefox.core.security.authenticator.authenticator_interface import AuthenticatorInterface
from framefox.core.security.token_manager import TokenManager
from framefox.core.templates.template_renderer import TemplateRenderer
from framefox.core.security.handlers.security_context_handler import SecurityContextHandler


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
        security_context_handler: SecurityContextHandler
    ):
        self.logger = logging.getLogger("FIREWALL")
        self.settings = settings
        self.template_renderer = template_renderer
        self.cookie_manager = cookie_manager
        self.session_manager = session_manager
        self.token_manager = token_manager
        self.csrf_manager = csrf_manager
        self.session = session
        self.access_manager = access_manager
        self.security_context_handler = security_context_handler


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
                    AuthenticatorClass: Type[AuthenticatorInterface] = getattr(
                        module, class_name
                    )
                    
                    authenticator_instance = AuthenticatorClass()
                    authenticators[firewall_name] = authenticator_instance
                except (ImportError, AttributeError) as e:
                    self.logger.error(
                        f"Error loading authenticator '{authenticator_path}' for firewall '{firewall_name}': {e}"
                    )
        return authenticators

    async def handle_request(self, request: Request, call_next):
        if not self.settings.firewalls:
            return await call_next(request)

        auth_routes = []
        for firewall in self.settings.firewalls.values():
            if "login_path" in firewall:
                auth_routes.append(firewall["login_path"])
            if "logout_path" in firewall:
                auth_routes.append(firewall["logout_path"])

        for firewall_name, firewall in self.settings.firewalls.items():
            if "logout_path" in firewall and request.url.path.startswith(
                firewall["logout_path"]
            ):
                return await self.handle_logout(
                    request, firewall, firewall_name, call_next
                )

        is_auth_route = any(request.url.path.startswith(route) for route in auth_routes)
        if is_auth_route:
            auth_response = await self.handle_authentication(request, call_next)
            if auth_response:
                return auth_response
                
        auth_result = await self.handle_authorization(request, call_next)
        if auth_result.status_code == 403:
            self.logger.warning("Authorization failed - insufficient permissions")

        return auth_result

    async def handle_authentication(self, request: Request, call_next) -> Optional[Response]:
        self.logger.debug(f"Authentication check: path={request.url.path}, params={request.query_params}")
        
        for firewall_name, authenticator in self.authenticators.items():
            firewall_config = self.settings.get_firewall_config(firewall_name)
            login_path = firewall_config.get("login_path")
            logout_path = firewall_config.get("logout_path")
            oauth_config = firewall_config.get("oauth", {})
            
            if logout_path and request.url.path.startswith(logout_path):
                return await self.handle_logout(request, firewall_config, firewall_name, call_next)

            is_oauth_authenticator = getattr(authenticator, 'is_oauth_authenticator', False)

            if is_oauth_authenticator and oauth_config:
                init_path = oauth_config.get("init_path", login_path)
                if request.url.path.endswith(init_path):
                    self.logger.debug(f"Handling OAuth initiation for {firewall_name}")
                    return authenticator.on_auth_failure(request)

                callback_path = oauth_config.get("callback_path")
                is_callback = (callback_path and 
                            request.url.path.endswith(callback_path) and 
                            "code" in request.query_params and
                            "state" in request.query_params)

                self.logger.debug(f"OAuth check: path={request.url.path}, callback_path={callback_path}, is_callback={is_callback}, params={request.query_params}")
                if is_callback:
                    self.logger.debug(f"Handling OAuth callback for {firewall_name}")
                    return call_next(request)

            elif request.url.path.startswith(login_path):
                if request.method == "GET":
                    return await call_next(request)
                elif request.method == "POST":
                    if not await self.csrf_manager.validate_token(request):
                        self.logger.error("CSRF validation failed.")
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
        self.logger.debug(f"Handling a POST request for {type(authenticator).__name__}.")


  
        passport = await authenticator.authenticate_request(request, firewall_name)
        if passport:
            token = self.token_manager.create_token(
                user=passport.user,
                firewallname=firewall_name,
                roles=(passport.user.roles if passport.user and hasattr(passport.user, 'roles') and passport.user.roles else []),
            )
            token_storage = ServiceContainer().get_by_name("TokenStorage")
            token_storage.set_token(token)
            
            self.session.set("user_id", passport.user.id)
            self.session.save()

     

            response = authenticator.on_auth_success(token)
            self.cookie_manager.delete_cookie(response, "csrf_token")

            self.logger.info("Authentication successful and token stored securely.")
            return response
        else:
            error_message = "Invalid credentials. Please try again."
            detailed_error = getattr(request.state, "auth_error", "Unknown authentication error")
            self.logger.warning(f"Authentication failed: {detailed_error}")
            
            if hasattr(request.state, "session_id"):
                self.security_context_handler.set_authentication_error(error_message)
                
            return authenticator.on_auth_failure(request, error_message)

    async def handle_authorization(self, request: Request, call_next):
        required_roles = self.access_manager.get_required_roles(request.url.path)
        if not required_roles:
            response = await call_next(request)
            return response

        from framefox.core.security.token_storage import TokenStorage
        token_storage = ServiceContainer().get(TokenStorage)
        payload = token_storage.get_payload()

        if payload:
            user_roles = payload.get("roles", [])
            if self.access_manager.is_allowed(user_roles, required_roles):
                return await call_next(request)
            else:
                self.logger.warning("User does not have the required roles.")

        self.logger.warning(f"Access forbidden for path: {request.url.path}")

        accept_header = request.headers.get("accept", "")
        if "text/html" in accept_header:
            return RedirectResponse(url="/", status_code=302)
        else:
            return JSONResponse(
                content={"error": "Access denied"},
                status_code=403
            )

    async def handle_logout(
        self, request: Request, firewall_config: Dict, firewall_name: str, call_next
    ) -> Response:
        token_storage = ServiceContainer().get_by_name("TokenStorage")
        token_storage.clear_token()
        
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
                response = JSONResponse(
                    content={"message": "Successfully logged out"}, 
                    status_code=200
                )
            else:
                response = RedirectResponse(url="/login", status_code=302)
                
        self.cookie_manager.delete_cookie(response, "session_id")
        self.cookie_manager.delete_cookie(response, "csrf_token")
        self.cookie_manager.delete_cookie(response, "access_token")

        self.logger.info("User logged out and session deleted")
        return response
