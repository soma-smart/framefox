from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from framefox.core.config.settings import Settings
from framefox.core.di.service_container import ServiceContainer
from framefox.core.events.decorator.dispatch_event import DispatchEvent

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FirewallMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.settings = Settings()
        self.handler = ServiceContainer().get_by_tag("core.security.handlers.firewall_handler")

    @DispatchEvent(event_before="auth.auth_attempt", event_after="auth.auth_result")
    async def dispatch(self, request: Request, call_next):
        if self.settings.firewalls:
            return await self.handler.handle_request(request, call_next)
        return await call_next(request)
