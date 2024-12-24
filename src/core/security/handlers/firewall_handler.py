import logging
from typing import Optional, List
import importlib

from fastapi import Request, Response, HTTPException
from src.core.security.passport.passport import Passport
from src.core.request.csrf_token_manager import CsrfTokenManager
from src.core.request.cookie_manager import CookieManager
from src.repository.user_repository import UserRepository
from src.core.security.exceptions.invalid_csrf_token_exception import (
    InvalidCsrfTokenException,
)


class FirewallHandler:
    def __init__(self, cookie_manager: CookieManager, logger: logging.Logger, settings):
        self.cookie_manager = cookie_manager
        self.logger = logger
        self.settings = settings
        self.csrf_manager = CsrfTokenManager(prefix="csrf_")

        authenticator_path = settings.authenticator
        module_path, class_name = authenticator_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        AuthenticatorClass = getattr(module, class_name)
        self.authenticator = AuthenticatorClass(settings)

    async def handle_login_get(self, request: Request, call_next):
        """
        Handles GET requests to the login page by generating a CSRF token.
        """
        self.logger.debug("Handling a GET request to the login page.")
        response = await call_next(request)

        csrf_token_value = self.csrf_manager.get_token()

        self.cookie_manager.set_response_cookie(
            response=response, key="csrf_token", token=csrf_token_value
        )
        self.logger.debug("CSRF token generated and added to the cookie.")
        return response

    async def handle_login_post(self, request: Request):
        """
        Handles POST requests to the login page by authenticating the user.
        """
        self.logger.debug("Handling a POST request to the login page.")
        try:
            passport: Optional[Passport] = await self.authenticator.authenticate(
                request
            )
            if passport:
                user_repository = UserRepository()

                authenticated = await passport.authenticate_user(user_repository)
                if not authenticated:
                    self.logger.warning("Invalid credentials.")
                    return Response(content="Invalid credentials", status_code=401)

                token = self.authenticator.create_token(
                    user=passport.user,
                    firewallname="main_firewall",
                    roles=(passport.user.roles if passport.user.roles else []),
                )
                response = self.authenticator.on_auth_success(
                    self.settings.login_redirect_route
                )

                self.cookie_manager.set_response_cookie(
                    response=response, key="access_token", token=token
                )
                self.logger.info(
                    "Authentication successful and token added to the cookie."
                )

            return response
        except HTTPException as e:
            self.logger.error(f"HTTP error during authentication: {e.detail}")
            return Response(content=e.detail, status_code=e.status_code)
        except InvalidCsrfTokenException:
            self.logger.error("CSRF validation failed.")
            return Response(content="Invalid CSRF token", status_code=400)

    async def handle_authorization(
        self, request: Request, required_roles: List[str], call_next
    ):
        """
        Handles authorization by checking the user's roles.
        """
        token = request.cookies.get("access_token")
        if token:
            payload = self.authenticator.decode_token(token)
            if payload and self.has_required_role(
                payload.get("roles", []), required_roles
            ):
                return await call_next(request)
            else:
                self.logger.warning("The user does not have the required roles.")
        else:
            self.logger.warning("No token found in cookies.")

        self.logger.warning(f"Access forbidden for path: {request.url.path}")
        return Response(content="Forbidden", status_code=403)

    def has_required_role(self, user_roles, required_roles):
        self.logger.debug(
            f"Checking user roles: {
                user_roles} against required roles: {required_roles}"
        )
        expanded_roles = set()
        for role in user_roles:
            expanded_roles.update(self.settings.flattened_roles.get(role, {role}))
        has_role = bool(expanded_roles.intersection(required_roles))
        self.logger.debug(
            f"The user {
                'has' if has_role else 'does not have'} the required roles."
        )
        return has_role
