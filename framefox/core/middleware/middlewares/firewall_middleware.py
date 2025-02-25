import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer
from framefox.core.events.decorator.dispatch_event import DispatchEvent
from framefox.core.security.handlers.firewall_handler import FirewallHandler

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
---------------------------- 
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


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
            return await self.handler.handle_request(request, call_next)
        self.logger.info("No access control rules defined.")
        return await call_next(request)
