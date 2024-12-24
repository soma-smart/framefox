import logging
import jwt
from typing import Annotated
from datetime import datetime, timedelta

from fastapi import Request
from fastapi.responses import RedirectResponse
from injectable import Autowired, autowired

from src.core.config.settings import Settings
from src.core.security.passport.passport import Passport
from src.core.security.passport.user_badge import UserBadge
from src.core.security.passport.password_credentials import PasswordCredentials
from src.core.security.passport.csrf_token_badge import CsrfTokenBadge

from src.entity.user import User


@autowired
class FormLoginAuthenticator:
    """
    FormLoginAuthenticator class handles the authentication process using form-based login.

    Attributes:
        logger (logging.Logger): Logger instance for authentication logging.
        settings (Settings): Application settings.

    Methods:
        __init__(settings: Annotated[Settings, Autowired]):
            Initializes the FormLoginAuthenticator with the provided settings.

        authenticate(request: Request) -> bool:
            Authenticates the user based on the form data in the request.
            Args:
                request (Request): The incoming request containing form data.
            Returns:
                bool: Returns a Passport object containing user credentials and CSRF token.

        on_auth_success() -> RedirectResponse:
            Handles actions to be taken upon successful authentication.
            Returns:
                RedirectResponse: A response redirecting to the home page.

        create_token(user: User, firewallname: str, roles: list) -> str:
            Creates a JWT token for the authenticated user.
            Args:
                user (User): The authenticated user.
                firewallname (str): The name of the firewall.
                roles (list): List of roles assigned to the user.
            Returns:
                str: The generated JWT token.

        decode_token(token: str) -> dict:
            Decodes the provided JWT token.
            Args:
                token (str): The JWT token to decode.
            Returns:
                dict: The decoded token payload if valid, otherwise None.
    """

    def __init__(
        self,
        settings: Annotated[Settings, Autowired],
    ):
        self.logger = logging.getLogger("AUTH")
        self.settings = settings

    async def authenticate(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("email")
        # ------ email in session -----#

        # request.session.set("email", email)

        passport = Passport(
            user_badge=UserBadge(email),
            password_credentials=PasswordCredentials(form.get("password")),
            csrf_token_badge=CsrfTokenBadge(form.get("csrf_token")),
        )

        return passport

    def on_auth_success(self, login_redirect_route: str) -> RedirectResponse:

        return RedirectResponse(login_redirect_route, status_code=303)

    def create_token(self, user: User, firewallname: str, roles: list) -> str:

        payload = {
            "email": user.email,
            "firewallname": firewallname,
            "roles": roles,
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        token = jwt.encode(payload, self.settings.cookie_secret_key, algorithm="HS256")
        return token

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token, self.settings.cookie_secret_key, algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired.")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid token.")
            return None
