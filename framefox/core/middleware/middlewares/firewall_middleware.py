import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from framefox.core.events.decorator.dispatch_event import DispatchEvent
from framefox.core.security.handlers.firewall_handler import FirewallHandler
from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer


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
            # auth_response = await self.handler.handle_authentication(request, call_next)
            # print("auth_response")
            # print(auth_response)
            # print(auth_response.status_code)
            # if auth_response and auth_response.status_code != 200:
            #     return auth_response
            # auth_result = await self.handler.handle_authorization(request, call_next)
            # return auth_result

            # Récupérer la configuration des firewalls
            auth_routes = []
            for firewall in self.settings.firewalls.values():
                if "login_path" in firewall:
                    auth_routes.append(firewall["login_path"])

            # Vérifier si c'est une route d'authentification
            is_auth_route = any(request.url.path.startswith(route)
                                for route in auth_routes)

            # Gérer l'authentification
            auth_response = await self.handler.handle_authentication(request, call_next)

            if auth_response:
                if is_auth_route:
                    # Pour les routes d'auth, on veut le 200 pour injecter le CSRF
                    return auth_response
                elif auth_response.status_code != 200:
                    # Pour les autres routes, on bloque si != 200
                    self.logger.warning("Authentication failed")
                    return auth_response

            # Gérer l'autorisation (seulement pour les routes non-auth)
            if not is_auth_route:
                auth_result = await self.handler.handle_authorization(request, call_next)
                if auth_result.status_code != 200:
                    self.logger.warning("Authorization failed")
                    return auth_result
                return auth_result
            return auth_response or await call_next(request)
        else:
            self.logger.warning("Access control is disabled!")

        return await call_next(request)
