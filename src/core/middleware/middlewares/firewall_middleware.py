import re
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.security.token_manager import TokenManager
from src.core.events.decorator.dispatch_event import DispatchEvent


class FirewallMiddleware(BaseHTTPMiddleware):
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
        self.logger = logging.getLogger("AUTH")
        self.token_manager = TokenManager(settings)

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

    def get_required_roles(self, path):
        self.logger.debug(f"Évaluation des rôles requis pour le chemin: {path}")
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
                self.logger.debug(
                    f"Chemin {path} correspond au pattern {
                                  pattern} avec les rôles {roles}"
                )
                return roles
        self.logger.debug(
            f"Aucune règle de contrôle d'accès ne correspond au chemin: {path}"
        )
        return None

    def get_current_user(self, request: Request):
        token = request.cookies.get("access_token")
        if not token:
            return None

        payload = self.token_manager.decode_token(token)
        if not payload:
            return None

        roles = payload.get("roles", [])
        return {"roles": roles}

    def has_required_role(self, user_roles, required_roles):
        self.logger.debug(
            f"Vérification des rôles de l'utilisateur: {
                          user_roles} contre les rôles requis: {required_roles}"
        )
        expanded_roles = set()
        for role in user_roles:
            expanded_roles.update(self.flattened_roles.get(role, {role}))
        self.logger.debug(f"Rôles étendus de l'utilisateur: {expanded_roles}")
        has_role = bool(expanded_roles.intersection(required_roles))
        self.logger.debug(
            f"L'utilisateur {'a' if has_role else 'n\'a pas'} les rôles requis."
        )
        return has_role

    @DispatchEvent(event_before="auth.auth_attempt", event_after="auth.auth_result")
    async def dispatch(self, request: Request, call_next):
        """
        Middleware pour gérer l'authentification avec dispatching d'événements.
        """
        path = request.url.path

        if not self.access_control:
            self.logger.info("Access control is disabled.")
            return await call_next(request)

        required_roles = self.get_required_roles(path)

        if required_roles:
            token = request.cookies.get("access_token")
            if token:
                payload = self.token_manager.decode_token(token)
                if payload and self.has_required_role(
                    payload.get("roles", []), required_roles
                ):
                    response = await call_next(request)
                    return response

            self.logger.warning(f"Accès interdit pour le chemin: {path}")
            return Response(content="Forbidden", status_code=403)

        response = await call_next(request)
        return response
