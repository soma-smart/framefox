import re
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from src.core.events.decorator.dispatch_event import DispatchEvent
from src.core.security.handlers.firewall_handler import FirewallHandler
from fastapi import Request
from src.core.request.cookie_manager import CookieManager


class FirewallMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, settings):
        super().__init__(app)
        self.settings = settings
        self.logger = logging.getLogger("FIREWALL")
        self.cookie_manager = CookieManager()

        self.handler = FirewallHandler(
            cookie_manager=self.cookie_manager, logger=self.logger, settings=settings
        )

        self.role_hierarchy = self.define_role_hierarchy()

    def define_role_hierarchy(self):
        return {
            "ROLE_ADMIN": ["ROLE_USER"],
        }

    def build_role_hierarchy(self):
        hierarchy = {}
        for role, inherits in self.role_hierarchy.items():
            hierarchy[role] = set(inherits + [role])
        return hierarchy

    def get_required_roles(self, path):
        self.logger.debug(f"Evaluating required roles for path: {path}")
        for rule in self.settings.access_control:
            pattern = rule.get("path")
            roles = rule.get("roles", "")
            if isinstance(roles, str):
                roles = [roles]
            elif isinstance(roles, list):
                pass
            else:
                roles = []

            if re.match(pattern, path):
                self.logger.debug(
                    f"Path {path} matches pattern {pattern} with roles {roles}"
                )
                return roles
        self.logger.debug(f"No access control rules match the path: {path}")
        return None

    @DispatchEvent(event_before="auth.auth_attempt", event_after="auth.auth_result")
    async def dispatch(self, request: Request, call_next):
        """
        Main middleware to handle authentication and authorization.
        """
        path = request.url.path
        method = request.method

        if self.settings.access_control:
            if method == "GET" and path == self.settings.login_path:
                return await self.handler.handle_login_get(request, call_next)
            if method == "POST" and path == self.settings.login_path:
                return await self.handler.handle_login_post(request)

            required_roles = self.get_required_roles(path)
            if required_roles:
                return await self.handler.handle_authorization(
                    request, required_roles, call_next
                )
        else:
            self.logger.info("No access control rules are defined.")

        return await call_next(request)
