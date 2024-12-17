import re
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling authentication and authorization.

    Attributes:
        access_control (list): List of access control rules.
        role_hierarchy (dict): Dictionary defining role inheritance.
        flattened_roles (dict): Dictionary with flattened role hierarchy for easy checking.
        logger (logging.Logger): Logger instance for logging.
    """

    def __init__(self, app, settings):
        super().__init__(app)

        self.access_control = settings.access_control
        self.role_hierarchy = self.define_role_hierarchy()
        self.flattened_roles = self.build_role_hierarchy()
        self.logger = logging.getLogger(__name__)

    def define_role_hierarchy(self):
        return {
            "ROLE_ADMIN": ["ROLE_USER"],
            # You can add other hierarchies here
        }

    def build_role_hierarchy(self):
        hierarchy = {}
        for role, inherits in self.role_hierarchy.items():
            hierarchy[role] = set(inherits + [role])
        return hierarchy

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        self.logger.debug(f"Request path: {path}")
        required_roles = self.get_required_roles(path)
        self.logger.debug(f"Required roles: {required_roles}")

        if required_roles:
            user = self.get_current_user(request)
            self.logger.debug(f"Current user roles: {user.get('roles', [])}")
            if not user or not self.has_required_role(user, required_roles):
                self.logger.warning(
                    f"Access forbidden for path: {
                        path} with roles: {user.get('roles', [])}"
                )
                return JSONResponse({"error": "Forbidden"}, status_code=403)

        response = await call_next(request)
        return response

    def get_required_roles(self, path):
        for rule in self.access_control:
            pattern = rule.get("path")
            roles = rule.get("roles", "")
            if isinstance(roles, str):
                roles = [roles]
            elif isinstance(roles, list):
                pass
            else:
                roles = []

            if re.match(pattern, path):
                return roles
        return None

    def get_current_user(self, request: Request):
        # Implement the logic to get the current user
        return {"roles": ["ROLE_USER"]}  # Static example

    def has_required_role(self, user, required_roles):
        user_roles = set(user.get("roles", []))
        expanded_roles = set()
        for role in user_roles:
            expanded_roles.update(self.flattened_roles.get(role, {role}))
        return bool(expanded_roles.intersection(required_roles))
