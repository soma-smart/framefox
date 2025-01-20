import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from framefox.core.events.decorator.dispatch_event import DispatchEvent
from framefox.core.security.handlers.firewall_handler import FirewallHandler
from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer

from fastapi.responses import JSONResponse, Response


class FirewallMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings
        self.logger = logging.getLogger("FIREWALL")
        container = ServiceContainer()
        self.handler = container.get(FirewallHandler)

    @DispatchEvent(event_before="auth.auth_attempt", event_after="auth.auth_result")
    async def dispatch(self, request: Request, call_next):
        if self.settings.access_control:
            # Authentification
            auth_routes = []
            for firewall in self.settings.firewalls.values():
                if "login_path" in firewall:
                    auth_routes.append(firewall["login_path"])

            # Vérifier si c'est une route d'authentification
            is_auth_route = any(request.url.path.startswith(route)
                                for route in auth_routes)
            if is_auth_route:
                auth_response = await self.handler.handle_authentication(request, call_next)
                if auth_response:
                    return auth_response

            # Autorisation
            auth_result = await self.handler.handle_authorization(request, call_next)
            if auth_result.status_code == 403:
                self.logger.warning(
                    "Authorization failed - insufficient permissions")
                return auth_result

            return auth_result

        else:
            self.logger.info("No access control rules defined.")

        return await call_next(request)
