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
        # self.handler = FirewallHandler(
        #     logger=self.logger)

    @DispatchEvent(event_before="auth.auth_attempt", event_after="auth.auth_result")
    async def dispatch(self, request: Request, call_next):
        """
        Main middleware to handle authentication and authorization.
        """
        if self.settings.access_control:
            auth_response = await self.handler.handle_authentication(request, call_next)
            if auth_response:
                return auth_response
            return await self.handler.handle_authorization(request, call_next)
        else:
            self.logger.info("No access control rules defined.")

        return await call_next(request)
