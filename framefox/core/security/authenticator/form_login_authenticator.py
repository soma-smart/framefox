from typing import Optional
from fastapi import Request
from fastapi.responses import RedirectResponse

from framefox.core.security.passport.passport import Passport
from framefox.core.security.passport.user_badge import UserBadge
from framefox.core.security.passport.password_credentials import PasswordCredentials
from framefox.core.security.passport.csrf_token_badge import CsrfTokenBadge
from framefox.core.security.authenticator.abstract_authenticator import (
    AbstractAuthenticator,
)
from framefox.core.security.authenticator.authenticator_interface import (
    AuthenticatorInterface,
)


class FormLoginAuthenticator(AbstractAuthenticator, AuthenticatorInterface):
    async def authenticate(self, request: Request) -> Optional[Passport]:
        form = await request.form()
        email = form.get("email")
        passport = Passport(
            user_badge=UserBadge(email),
            password_credentials=PasswordCredentials(form.get("password")),
            csrf_token_badge=CsrfTokenBadge(form.get("csrf_token")),
        )
        return passport

    def on_auth_success(self, token: str) -> RedirectResponse:
        """
        Handles the logic after a successful authentication.
        """
        return RedirectResponse(url="/", status_code=303)
