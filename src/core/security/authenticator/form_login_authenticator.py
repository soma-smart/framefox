from typing import Optional
from fastapi import Request
from fastapi.responses import RedirectResponse
from src.core.security.passport.passport import Passport
from src.core.security.passport.user_badge import UserBadge
from src.core.security.passport.password_credentials import PasswordCredentials
from src.core.security.passport.csrf_token_badge import CsrfTokenBadge
from src.core.security.authenticator.abstract_authenticator import AbstractAuthenticator
from src.core.security.authenticator.authenticator_interface import AuthenticatorInterface


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
        return RedirectResponse(
            self.settings.login_redirect_route, status_code=303
        )
