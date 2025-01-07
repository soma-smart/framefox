import logging
import importlib
from typing import List, Optional
from fastapi import Request
from fastapi.responses import Response
from src.core.security.token_manager import TokenManager

from src.core.security.access_manager import AccessManager


class FirewallHandler:

    def __init__(self, logger: logging.Logger, settings):
        self.token_manager = TokenManager()
        self.logger = logger
        self.settings = settings

        self.access_manager = AccessManager(settings, logger)
        module_path, class_name = settings.authenticator.rsplit(".", 1)
        module = importlib.import_module(module_path)
        AuthenticatorClass = getattr(module, class_name)
        self.authenticator = AuthenticatorClass()

    async def handle_authentication(self, request: Request) -> Optional[Response]:
        """
        Détermine la méthode d'authentification à utiliser en fonction de la méthode HTTP.
        """

        if request.method == "GET" and request.url.path == self.settings.login_path:
            return await self.authenticator.handle_login_get()
        elif request.method == "POST" and request.url.path == self.settings.login_path:
            return await self.authenticator.handle_login_post(
                request, self.token_manager
            )
        return None

    async def handle_authorization(self, request: Request, call_next):
        """
        Gère l'autorisation en utilisant la classe access_manager.
        """
        required_roles = self.access_manager.get_required_roles(request.url.path)
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
                        "L'utilisateur ne possède pas les rôles requis."
                    )
            else:
                self.logger.warning("Payload du token invalide.")

        self.logger.warning(
            f"Accès interdit pour le chemin: {
                            request.url.path}"
        )
        return Response(content="Forbidden", status_code=403)
